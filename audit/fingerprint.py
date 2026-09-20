import argparse
import json
import os
import re
import time

from .providers import OPENAI_COMPATIBLE, _http, _rate_limit

STACKS = {
    "gpt-oss-120b": [("groq", "openai/gpt-oss-120b"), ("ovh", "gpt-oss-120b"), ("ollama", "gpt-oss:120b"), ("cloudflare", "@cf/openai/gpt-oss-120b")],
    "qwen3.8-27b": [("groq", "qwen/qwen3.8-27b"), ("ovh", "Qwen3.8-27B"), ("cloudflare", "@cf/qwen/qwen3.8-27b")],
    "qwen3.6-27b": [("groq", "qwen/qwen3.6-27b"), ("ovh", "Qwen3.6-27B")],
    "gpt-oss-20b": [("groq", "openai/gpt-oss-20b"), ("ovh", "gpt-oss-20b"), ("ollama", "gpt-oss:20b"), ("cloudflare", "@cf/openai/gpt-oss-20b"), ("nvidia", "openai/gpt-oss-20b")],
    "nemotron-3-super-120b": [("ollama", "nemotron-3-super"), ("openrouter", "nvidia/nemotron-3-super-120b-a12b:free"), ("cloudflare", "@cf/nvidia/nemotron-3-120b-a12b"), ("nvidia", "nvidia/nemotron-3-super-120b-a12b"), ("kilocode", "nvidia/nemotron-3-super-120b-a12b:free")],
    "gemma-4-31b": [("ollama", "gemma4:31b"), ("openrouter", "google/gemma-4-31b-it:free"), ("nvidia", "google/gemma-4-31b-it")],
    "gemma-4-26b-a4b": [("cloudflare", "@cf/google/gemma-4-26b-a4b-it"), ("openrouter", "google/gemma-4-26b-a4b-it:free")],
    "glm-5.3-flash": [("ollama", "glm-5.3-flash"), ("zhipu", "glm-5.3-flash"), ("cloudflare", "@cf/zai-org/glm-5.3-flash")],
    "glm-5.3": [("ollama", "glm-5.3"), ("zhipu", "glm-5.3"), ("cloudflare", "@cf/zai-org/glm-5.3")],
    "deepseek-v4-flash": [("ollama", "deepseek-v4-flash:0731"), ("cloudflare", "@cf/deepseek-ai/deepseek-v4-flash-0731"), ("nvidia", "deepseek-ai/deepseek-v4-flash-0731")],
    "kimi-k2.6": [("ollama", "kimi-k2.6"), ("cloudflare", "@cf/moonshotai/kimi-k2.6"), ("nvidia", "moonshotai/kimi-k2.6")],
    "qwen3.5-397b": [("ovh", "Qwen3.5-397B-A17B"), ("ollama", "qwen3.5:397b")],
}

RPM = {"groq": 10, "ovh": 1.5, "cloudflare": 6, "ollama": 3, "openrouter": 4, "zhipu": 6, "nvidia": 4, "kilocode": 3}
RETRYABLE = {0, 429, 500, 502, 503, 504}
MAX_TOKENS_CAP = {("groq", "qwen/qwen3.6-27b"): 1000}

MATH_Q = (
    "A warehouse starts with 1,284 boxes. On Monday it ships 37% of them. On Tuesday it receives "
    "3 pallets of 96 boxes each. On Wednesday it ships 415 boxes. How many boxes remain? "
    "Answer with the final integer only."
)
MATH_ANSWER = 1284 - round(1284 * 0.37) + 3 * 96 - 415
PASSCODE = "TANGERINE-4471"


def long_context_prompt(target_tokens=20000):
    filler = "The quarterly report lists routine maintenance entries for facility sector %d with no anomalies recorded. "
    parts = []
    i = 0
    while sum(len(p) for p in parts) < target_tokens * 3.6:
        parts.append(filler % i)
        i += 1
    mid = len(parts) // 2
    parts.insert(mid, f"IMPORTANT: the access passcode for the audit is {PASSCODE}. ")
    return "".join(parts) + "\n\nWhat is the access passcode for the audit? Reply with the passcode only."


def probes():
    math_msgs = [{"role": "user", "content": MATH_Q}]
    return [
        ("F1_reasoning_default", {"messages": math_msgs, "max_tokens": 2048}),
        ("F2a_template_nothink", {"messages": math_msgs, "max_tokens": 2048, "chat_template_kwargs": {"enable_thinking": False}}),
        ("F2b_effort_none", {"messages": math_msgs, "max_tokens": 2048, "reasoning_effort": "none"}),
        ("F2c_prompt_nothink", {"messages": [{"role": "system", "content": "/no_think"}] + math_msgs, "max_tokens": 2048}),
        ("F3_system_adherence", {"messages": [{"role": "system", "content": "Always answer in French. Output exactly one word and nothing else."}, {"role": "user", "content": "What color is a clear daytime sky?"}], "max_tokens": 256}),
        ("F4a_repeat", {"messages": math_msgs, "max_tokens": 2048}),
        ("F4b_repeat", {"messages": math_msgs, "max_tokens": 2048}),
        ("F5_max_tokens_40", {"messages": math_msgs, "max_tokens": 40}),
        ("F6_json_mode", {"messages": [{"role": "user", "content": "Give the capital of France and its population as JSON with keys city and population."}], "max_tokens": 512, "response_format": {"type": "json_object"}}),
        ("F7_tools", {"messages": [{"role": "user", "content": "What is the weather in Paris right now?"}], "max_tokens": 512, "tools": [{"type": "function", "function": {"name": "get_weather", "description": "Get current weather for a city", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}}], "tool_choice": "auto"}),
        ("F8a_seed", {"messages": math_msgs, "max_tokens": 2048, "seed": 12345}),
        ("F8b_logprobs", {"messages": [{"role": "user", "content": "Reply with the single word: pong"}], "max_tokens": 8, "logprobs": True, "top_logprobs": 2}),
        ("F8c_top_k", {"messages": [{"role": "user", "content": "Reply with the single word: pong"}], "max_tokens": 8, "top_k": 1}),
        ("F9_stop", {"messages": [{"role": "user", "content": "Count from 1 to 10, one number per line, digits only, no other text."}], "max_tokens": 256, "stop": ["6"]}),
        ("F10_long_context", {"messages": [{"role": "user", "content": long_context_prompt()}], "max_tokens": 64}),
        ("F11_identity", {"messages": [{"role": "user", "content": "In one sentence: what model are you, who developed you, and what is your knowledge cutoff?"}], "max_tokens": 128}),
    ]


def raw_call(provider, model, body, timeout=240):
    url, key_var = OPENAI_COMPATIBLE[provider]
    url = url.format(account=os.environ.get("CLOUDFLARE_ACCOUNT_ID", ""))
    key = os.environ.get(key_var, "")
    payload = {"model": model, "temperature": 0}
    payload.update(body)
    cap = MAX_TOKENS_CAP.get((provider, model))
    if cap and payload.get("max_tokens", 0) > cap:
        payload["max_tokens"] = cap
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    status, resp_headers, raw, latency = _http(url, payload, headers, timeout)
    if provider == "ovh" and status == 401 and key:
        status, resp_headers, raw, latency = _http(url, payload, {}, timeout)
    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = {"_raw": raw.decode(errors="replace")[:2000]}
    return status, parsed, latency, _rate_limit(resp_headers)


def summarize(name, status, parsed):
    s = {"status": status}
    if status != 200 or "choices" not in parsed:
        s["error"] = json.dumps(parsed)[:300]
        return s
    choice = parsed["choices"][0]
    msg = choice.get("message") or {}
    text = msg.get("content") or ""
    usage = parsed.get("usage") or {}
    details = usage.get("completion_tokens_details") or {}
    s.update({
        "finish_reason": choice.get("finish_reason"),
        "output_tokens": usage.get("completion_tokens"),
        "input_tokens": usage.get("prompt_tokens"),
        "reasoning_tokens": details.get("reasoning_tokens"),
        "has_reasoning_field": bool(msg.get("reasoning") or msg.get("reasoning_content")),
        "reasoning_chars": len(msg.get("reasoning") or msg.get("reasoning_content") or ""),
        "think_tag_in_text": "<think>" in text or "</think>" in text,
        "leading_blank": text.startswith("\n"),
        "text_chars": len(text),
        "text_head": text.strip()[:160],
        "tool_calls": len(msg.get("tool_calls") or []),
        "has_logprobs": bool(choice.get("logprobs")),
    })
    digits = re.findall(r"-?\d[\d,]*", text.replace(",", ""))
    if name.startswith(("F1", "F2", "F4", "F8a")):
        s["math_correct"] = bool(digits) and int(digits[-1]) == MATH_ANSWER
    if name.startswith("F3"):
        s["french_one_word"] = len(text.strip().split()) == 1 and "bleu" in text.lower()
    if name.startswith("F6"):
        try:
            json.loads(text.strip().strip("`").removeprefix("json").strip())
            s["valid_json"] = True
        except Exception:
            s["valid_json"] = False
    if name.startswith("F9"):
        nums = [int(d) for d in re.findall(r"\d+", text)]
        s["stopped_before_6"] = bool(nums) and max(nums) <= 5
    if name.startswith("F10"):
        s["passcode_found"] = PASSCODE in text
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True)
    ap.add_argument("--models", default="", help="comma list of model families; default all with this provider")
    ap.add_argument("--probes", default="", help="comma list of probe name prefixes")
    ap.add_argument("--out", default="runs")
    ap.add_argument("--retry-missing", action="store_true", help="only run probes that have no non-retryable result yet")
    ap.add_argument("--max-attempts", type=int, default=3)
    args = ap.parse_args()
    done = set()
    if args.retry_missing:
        import glob
        for p in glob.glob(os.path.join(args.out, f"fingerprint_{args.provider}_*.jsonl")):
            for line in open(p):
                r = json.loads(line)
                if r["summary"]["status"] not in RETRYABLE:
                    done.add((r["model"], r["probe"]))
    os.makedirs(args.out, exist_ok=True)
    fams = [f for f in args.models.split(",") if f] or [f for f, st in STACKS.items() if any(p == args.provider for p, _ in st)]
    wanted = [p for p in args.probes.split(",") if p]
    path = os.path.join(args.out, f"fingerprint_{args.provider}_{time.strftime('%Y%m%d-%H%M%S')}.jsonl")
    gap = 60.0 / RPM.get(args.provider, 4)
    for fam in fams:
        models = [m for p, m in STACKS[fam] if p == args.provider]
        for model in models:
            for name, body in probes():
                if wanted and not any(name.startswith(w) for w in wanted):
                    continue
                if (model, name) in done:
                    continue
                t0 = time.time()
                status, parsed, latency, rl = raw_call(args.provider, model, body)
                attempt = 1
                while status in RETRYABLE and attempt < args.max_attempts:
                    time.sleep(max(gap, 20) * (2 ** attempt))
                    status, parsed, latency, rl = raw_call(args.provider, model, body)
                    attempt += 1
                summ = summarize(name, status, parsed)
                rec = {"ts": time.time(), "family": fam, "provider": args.provider, "model": model, "probe": name, "latency_ms": latency, "rate_limit": rl, "summary": summ, "request": {k: v for k, v in body.items() if k != "messages"}, "response": parsed}
                with open(path, "a") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                brief = {k: v for k, v in summ.items() if k in ("status", "output_tokens", "reasoning_tokens", "math_correct", "french_one_word", "valid_json", "tool_calls", "stopped_before_6", "passcode_found", "finish_reason")}
                print(f"{args.provider} {model} {name} {brief}", flush=True)
                time.sleep(max(0, gap - (time.time() - t0)))
    print("saved", path)


if __name__ == "__main__":
    main()
