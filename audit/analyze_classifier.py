import glob
import itertools
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(os.path.dirname(HERE), "runs")
INDICATORS = ("count", "field", "inline")


def load_latest():
    latest = {}
    for path in sorted(glob.glob(os.path.join(RUNS, "fingerprint_*.jsonl"))):
        for line in open(path):
            rec = json.loads(line)
            key = (rec["provider"], rec["model"], rec["probe"])
            if key not in latest or rec["ts"] > latest[key]["ts"]:
                latest[key] = rec
    return latest


def indicators(summary):
    return {
        "count": bool(summary.get("reasoning_tokens")),
        "field": bool(summary.get("has_reasoning_field")),
        "inline": bool(summary.get("think_tag_in_text")) or bool(summary.get("leading_blank")),
    }


def classify_off(summary, theta, used=INDICATORS):
    if summary.get("status") != 200:
        return None
    flags = indicators(summary)
    if any(flags[k] for k in used):
        return False
    n = summary.get("output_tokens")
    return None if n is None else n <= theta


def counts(latest, theta, used=INDICATORS):
    f1 = {k[:2]: v for k, v in latest.items() if k[2] == "F1_reasoning_default"}
    on_by_default = {k for k, v in f1.items() if classify_off(v["summary"], theta, used) is False}
    default_off = sum(1 for v in f1.values() if classify_off(v["summary"], theta, used))
    switch_off = sum(
        1
        for k, v in latest.items()
        if k[2].startswith("F2") and classify_off(v["summary"], theta, used) and k[:2] in on_by_default
    )
    return default_off, switch_off


def main():
    latest = load_latest()
    f1 = {k[:2]: v for k, v in latest.items() if k[2] == "F1_reasoning_default"}
    answered = [v["summary"] for v in f1.values() if v["summary"].get("status") == 200]
    without = sorted(s["output_tokens"] for s in answered if not any(indicators(s).values()))
    with_ = sorted(s["output_tokens"] for s in answered if any(indicators(s).values()))

    print(f"stacks answering F1: {len(answered)}")
    print(f"no reasoning indicator (n={len(without)}): output tokens {without}")
    print(f"with reasoning indicator (n={len(with_)}): min {with_[0]}, max {with_[-1]}")
    print()
    print("theta    default-off  switch-off")
    for theta in (2, 4, 5, 10, 20, 50, 100, 298, 299, 400):
        d, s = counts(latest, theta)
        print(f"{theta:<8} {d:<12} {s}")
    print()
    print("indicator ablation at theta=10")
    for r in (1, 2, 3):
        for used in itertools.combinations(INDICATORS, r):
            d, s = counts(latest, 10, used)
            print(f"  {str(used):36s} default-off={d}  switch-off={s}")
    d, s = counts(latest, 10, ())
    print(f"  {'() token count alone':36s} default-off={d}  switch-off={s}")


if __name__ == "__main__":
    main()
