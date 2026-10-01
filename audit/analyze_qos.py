import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(os.path.dirname(HERE), "runs", "stacks")

FIRST_RUNS = [
    ("gpt-oss-120b", "stacks_gptoss120b_20260910-190022.events.jsonl"),
    ("gpt-oss-20b", "stacks_gptoss20b_20260910-181315.events.jsonl"),
    ("nemotron", "stacks_nemotron_super_v2_20260910-202513.events.jsonl"),
    ("gemma-4-31b", "stacks_gemma431_20260910-161048.events.jsonl"),
    ("qwen3.6-27b", "stacks_qwen36_20260910-193707.events.jsonl"),
]
PROVIDER = {
    "cloudflare": "Cloudflare",
    "groq": "Groq",
    "ovh": "OVH",
    "ollama": "Ollama",
    "nvidia": "NVIDIA NIM",
    "kilocode": "Kilo Code",
}


def responses(path):
    for line in open(path):
        rec = json.loads(line)
        if rec.get("kind") == "ModelResponded":
            yield rec


def quantile(values, fraction):
    if not values:
        return float("nan")
    return values[min(len(values) - 1, int(fraction * len(values)))]


def rate_limit_headers():
    seen = collections.defaultdict(set)
    providers = set()
    for name in sorted(os.listdir(RUNS)):
        if not name.endswith(".events.jsonl"):
            continue
        for rec in responses(os.path.join(RUNS, name)):
            providers.add(rec["provider"])
            headers = rec.get("rate_limit")
            if isinstance(headers, dict):
                seen[rec["provider"]].update(headers)
    return seen, providers


def main():
    print("family & provider & ok/n & med & p95 & max & out & rl")
    for family, name in FIRST_RUNS:
        grouped = collections.defaultdict(list)
        for rec in responses(os.path.join(RUNS, name)):
            grouped[PROVIDER[rec["provider"]]].append(rec)
        for provider in sorted(grouped):
            all_ = grouped[provider]
            ok = [r for r in all_ if r.get("status") == 200 and not r.get("error_kind")]
            latency = sorted(r["latency_ms"] for r in ok if r.get("latency_ms"))
            out = [r["output_tokens"] for r in ok if r.get("output_tokens") is not None]
            print(
                f"{family} & {provider} & {len(ok)}/{len(all_)} & "
                f"{quantile(latency, 0.5) / 1000:.1f} & {quantile(latency, 0.95) / 1000:.1f} & "
                f"{max(latency) / 1000:.1f} & {sum(out) / len(out):.0f}"
            )

    seen, providers = rate_limit_headers()
    print()
    print("rate-limit headers returned, all Phase 2 runs")
    for provider in sorted(providers):
        headers = sorted(seen.get(provider, ()))
        print(f"  {PROVIDER.get(provider, provider):12s} {len(headers)} {headers}")

    total = 0.0
    n = 0
    for name in sorted(os.listdir(RUNS)):
        if not name.endswith(".events.jsonl"):
            continue
        for rec in responses(os.path.join(RUNS, name)):
            n += 1
            total += rec.get("usd") or 0.0
    print()
    print(f"phase 2 responses {n}, priced spend ${total:.4f}")


if __name__ == "__main__":
    main()
