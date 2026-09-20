import glob
import itertools
import json
import statistics
import sys


def load(path):
    d = json.load(open(path))
    return d["stacks"], d["results"]


def is_infra(o):
    return str(o.get("error", "")).startswith("infra")


def stack_summary(stacks, results):
    rows = []
    for s in stacks:
        all_outs = [r["outputs"][s] for r in results if s in r["outputs"]]
        infra = sum(is_infra(o) for o in all_outs)
        outs = [o for o in all_outs if not is_infra(o)]
        n = len(outs)
        ok = sum(o["kind"] == "ok" for o in outs)
        kinds = {}
        for o in outs:
            kinds[o["kind"]] = kinds.get(o["kind"], 0) + 1
        lat = statistics.median(o["latency_ms"] for o in outs) / 1000 if outs else 0
        tok = statistics.mean(o["tokens"] for o in outs) if outs else 0
        rows.append((s, n, ok, kinds, lat, tok, infra))
    return rows


def pairwise(stacks, results):
    rows = []
    for a, b in itertools.combinations(stacks, 2):
        both = [r for r in results if a in r["outputs"] and b in r["outputs"] and not is_infra(r["outputs"][a]) and not is_infra(r["outputs"][b])]
        n = len(both)
        text_eq = sum(r["outputs"][a]["text"] == r["outputs"][b]["text"] for r in both)
        sem_eq = sum(r["outputs"][a]["ledger"] == r["outputs"][b]["ledger"] and r["outputs"][a]["ledger"] is not None for r in both)
        both_ok = sum(r["outputs"][a]["kind"] == "ok" and r["outputs"][b]["kind"] == "ok" for r in both)
        a_only = sum(r["outputs"][a]["kind"] == "ok" and r["outputs"][b]["kind"] != "ok" for r in both)
        b_only = sum(r["outputs"][b]["kind"] == "ok" and r["outputs"][a]["kind"] != "ok" for r in both)
        rows.append((a, b, n, text_eq, sem_eq, both_ok, a_only, b_only))
    return rows


def pct(x, n):
    return f"{x} ({100 * x / n:.0f}%)" if n else "-"


def main():
    paths = sys.argv[1:] or sorted(glob.glob("runs/stacks/stacks_*.json"))
    print("# 阶段 2 跨栈分叉表（自动生成）\n\n基础设施失败（429、5xx、超时、网关包裹的上游错误）已从 n 与两两比较中剔除，单独计数。")
    for path in paths:
        stacks, results = load(path)
        label = path.split("stacks_")[-1].rsplit("_", 1)[0]
        print(f"\n## {label}  ({len(results)} 步, {path.split('/')[-1]})\n")
        print("| 栈 | n（有效） | 基础设施失败 | 正确 | 各类结果 | 中位延迟 s | 平均 token |")
        print("|---|---|---|---|---|---|---|")
        for s, n, ok, kinds, lat, tok, infra in stack_summary(stacks, results):
            print(f"| {s} | {n} | {infra} | {pct(ok, n)} | {', '.join(f'{k}={v}' for k, v in sorted(kinds.items()))} | {lat:.1f} | {tok:.0f} |")
        print("\n| 栈对 | n | 文本一致 | 语义一致 | 两边都对 | 仅前者对 | 仅后者对 |")
        print("|---|---|---|---|---|---|---|")
        for a, b, n, te, se, bo, ao, bo2 in pairwise(stacks, results):
            print(f"| {a.split(':')[0]} vs {b.split(':')[0]} | {n} | {pct(te, n)} | {pct(se, n)} | {bo} | {ao} | {bo2} |")


if __name__ == "__main__":
    main()
