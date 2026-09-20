import json
import sys


def is_infra(o):
    return str(o.get("error", "")).startswith("infra")


def load(path):
    d = json.load(open(path))
    return d["stacks"], {r["idx"]: r for r in d["results"]}


def match_stack(name, stacks):
    base = name.split("#")[0]
    for s in stacks:
        if s.split("#")[0] == base:
            return s
    return None


def compare(first_path, second_path):
    stacks_a, res_a = load(first_path)
    stacks_b, res_b = load(second_path)
    rows = []
    for sa in stacks_a:
        sb = match_stack(sa, stacks_b)
        if sb is None:
            continue
        both = []
        for idx, ra in res_a.items():
            rb = res_b.get(idx)
            if rb is None or sa not in ra["outputs"] or sb not in rb["outputs"]:
                continue
            oa, ob = ra["outputs"][sa], rb["outputs"][sb]
            if is_infra(oa) or is_infra(ob):
                continue
            both.append((oa, ob))
        n = len(both)
        text_eq = sum(a["text"] == b["text"] for a, b in both)
        sem_eq = sum(a["ledger"] is not None and a["ledger"] == b["ledger"] for a, b in both)
        both_ok = sum(a["kind"] == "ok" and b["kind"] == "ok" for a, b in both)
        first_only = sum(a["kind"] == "ok" and b["kind"] != "ok" for a, b in both)
        second_only = sum(b["kind"] == "ok" and a["kind"] != "ok" for a, b in both)
        both_wrong_same = sum(a["kind"] != "ok" and b["kind"] != "ok" and a["ledger"] is not None and a["ledger"] == b["ledger"] for a, b in both)
        both_wrong_diff = sum(a["kind"] != "ok" and b["kind"] != "ok" and a["ledger"] != b["ledger"] for a, b in both)
        rows.append((sa, n, text_eq, sem_eq, both_ok, first_only, second_only, both_wrong_same, both_wrong_diff))
    return rows


def pct(x, n):
    return f"{x} ({100 * x / n:.0f}%)" if n else "-"


def main():
    first, second = sys.argv[1], sys.argv[2]
    print(f"same-stack repeat: {first.split('/')[-1]} vs {second.split('/')[-1]}\n")
    print("| 栈 | n | 文本一致 | 语义一致 | 两次都对 | 仅第一次对 | 仅第二次对 | 两次同错 | 两次异错 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for s, n, te, se, bo, fo, so, ws, wd in compare(first, second):
        print(f"| {s} | {n} | {pct(te, n)} | {pct(se, n)} | {bo} | {fo} | {so} | {ws} | {wd} |")


if __name__ == "__main__":
    main()
