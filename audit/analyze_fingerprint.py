import glob
import json
import sys
from collections import defaultdict

from .fingerprint import STACKS


def load(paths):
    rows = defaultdict(dict)
    for path in paths:
        for line in open(path):
            r = json.loads(line)
            rows[(r["family"], r["provider"], r["model"])][r["probe"]] = r
    return rows


def cell(rec, key, fmt=None):
    if rec is None:
        return "·"
    s = rec["summary"]
    if s["status"] != 200:
        return f"HTTP {s['status']}"
    v = s.get(key)
    if fmt:
        return fmt(v)
    return {True: "yes", False: "no", None: "-"}.get(v, str(v))


def yes_no(v):
    return {True: "yes", False: "no"}.get(v, "-")


def reasoning_mode(rec):
    if rec is None:
        return "·"
    s = rec["summary"]
    if s["status"] != 200:
        return f"HTTP {s['status']}"
    out = s.get("output_tokens") or 0
    rt = s.get("reasoning_tokens")
    if rt:
        return f"on, separate ({rt}/{out})"
    if s.get("has_reasoning_field"):
        return f"on, field ({s['reasoning_chars']}ch/{out})"
    if s.get("think_tag_in_text"):
        return f"on, inline tag ({out})"
    if out > 120:
        return f"on?, hidden ({out})"
    return f"off ({out})"


def switch_effect(base, rec):
    if rec is None or base is None:
        return "·"
    s = rec["summary"]
    if s["status"] != 200:
        return f"HTTP {s['status']}"
    b = base["summary"].get("output_tokens") or 0
    o = s.get("output_tokens") or 0
    ok = "ok" if s.get("math_correct") else "WRONG"
    if b and o < 0.4 * b:
        return f"cut {b}->{o} {ok}"
    return f"same {b}->{o} {ok}"


def determinism(rows):
    texts = []
    for p in ("F1_reasoning_default", "F4a_repeat", "F4b_repeat"):
        r = rows.get(p)
        if r and r["summary"]["status"] == 200:
            texts.append(json.dumps(r["response"]["choices"][0]["message"].get("content")))
    if len(texts) < 2:
        return "·"
    return f"{len(set(texts))} distinct / {len(texts)}"


def main():
    paths = sys.argv[1:] or sorted(glob.glob("runs/fingerprint_*.jsonl"))
    rows = load(paths)
    print("# 指纹表（自动生成）\n")
    cols = ["栈", "F1 思考默认", "F2a template", "F2b effort=none", "F2c /no_think", "F3 系统提示", "F4 确定性", "F5 mt=40", "F6 JSON", "F7 tools", "F8 seed/logprobs/top_k", "F9 stop", "F10 20K ctx", "F11 自述"]
    for fam, stacks in STACKS.items():
        present = [(p, m) for p, m in stacks if (fam, p, m) in rows]
        if not present:
            continue
        print(f"\n## {fam}\n")
        print("| " + " | ".join(cols) + " |")
        print("|" + "---|" * len(cols))
        for p, m in present:
            r = rows[(fam, p, m)]
            g = r.get
            f5 = g("F5_max_tokens_40")
            f5c = "·" if f5 is None else (f"HTTP {f5['summary']['status']}" if f5["summary"]["status"] != 200 else f"{f5['summary'].get('finish_reason')}, text {f5['summary'].get('text_chars')}ch")
            f8 = "/".join(cell(g(k), "status", lambda v: str(v)) for k in ("F8a_seed", "F8b_logprobs", "F8c_top_k"))
            lp = g("F8b_logprobs")
            if lp and lp["summary"]["status"] == 200:
                f8 += " lp:" + yes_no(lp["summary"].get("has_logprobs"))
            f11 = g("F11_identity")
            f11c = "·" if f11 is None else (f"HTTP {f11['summary']['status']}" if f11["summary"]["status"] != 200 else f11["summary"]["text_head"][:90].replace("|", "/"))
            vals = [
                f"{p} `{m}`",
                reasoning_mode(g("F1_reasoning_default")),
                switch_effect(g("F1_reasoning_default"), g("F2a_template_nothink")),
                switch_effect(g("F1_reasoning_default"), g("F2b_effort_none")),
                switch_effect(g("F1_reasoning_default"), g("F2c_prompt_nothink")),
                cell(g("F3_system_adherence"), "french_one_word"),
                determinism(r),
                f5c,
                cell(g("F6_json_mode"), "valid_json"),
                cell(g("F7_tools"), "tool_calls", lambda v: f"{v} calls"),
                f8,
                cell(g("F9_stop"), "stopped_before_6"),
                cell(g("F10_long_context"), "passcode_found"),
                f11c,
            ]
            print("| " + " | ".join(vals) + " |")


if __name__ == "__main__":
    main()
