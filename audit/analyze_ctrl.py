import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(os.path.dirname(HERE), "runs", "stacks")


def is_infra(o):
    return str(o.get("error", "")).startswith("infra")


def load(pattern):
    path = sorted(glob.glob(os.path.join(RUNS, pattern)))[-1]
    d = json.load(open(path))
    return os.path.basename(path), d["stacks"], {(r["seed"], r["t"]): r["outputs"] for r in d["results"]}


def pair(a_outs, b_outs):
    keys = [k for k in a_outs if k in b_outs and not is_infra(a_outs[k]) and not is_infra(b_outs[k])]
    n = len(keys)
    sem = sum(a_outs[k]["ledger"] is not None and a_outs[k]["ledger"] == b_outs[k]["ledger"] for k in keys)
    text = sum(a_outs[k]["text"] == b_outs[k]["text"] for k in keys)
    both = sum(a_outs[k]["kind"] == "ok" and b_outs[k]["kind"] == "ok" for k in keys)
    a_only = sum(a_outs[k]["kind"] == "ok" and b_outs[k]["kind"] != "ok" for k in keys)
    b_only = sum(b_outs[k]["kind"] == "ok" and a_outs[k]["kind"] != "ok" for k in keys)
    wrong_same = sum(a_outs[k]["kind"] != "ok" and b_outs[k]["kind"] != "ok" and a_outs[k]["ledger"] is not None and a_outs[k]["ledger"] == b_outs[k]["ledger"] for k in keys)
    return n, sem, text, both, a_only, b_only, wrong_same


def by_stack(stacks, results, stack):
    outs = {k: v[stack] for k, v in results.items() if stack in v}
    infra = sum(is_infra(o) for o in outs.values())
    answered = {k: o for k, o in outs.items() if not is_infra(o)}
    ok = sum(o["kind"] == "ok" for o in answered.values())
    return outs, infra, len(answered), ok


def main():
    ctrl_name, ctrl_stacks, ctrl = load("stacks_qwen38_ctrl_off_*.json")
    prev_name, prev_stacks, prev = load("stacks_qwen38_same40_*.json")
    print(f"control run: {ctrl_name}\nprevious 40-step run: {prev_name}\n")
    print("| stack | infra | answered | correct |")
    print("|---|---|---|---|")
    outs = {}
    for s in ctrl_stacks:
        o, infra, n, ok = by_stack(ctrl_stacks, ctrl, s)
        outs[s] = o
        print(f"| {s} | {infra} | {n} | {ok} ({100 * ok / n:.0f}%) |")
    for s in prev_stacks:
        o, infra, n, ok = by_stack(prev_stacks, prev, s)
        outs["prev:" + s] = o
        print(f"| 09-25 {s} | {infra} | {n} | {ok} ({100 * ok / n:.0f}%) |")
    print("\n| pair | n | sem | text | both ok | A only | B only | both wrong same |")
    print("|---|---|---|---|---|---|---|---|")
    names = list(ctrl_stacks)
    combos = [(names[i], names[j]) for i in range(len(names)) for j in range(i + 1, len(names))]
    cf_on = "prev:" + [s for s in prev_stacks if s.startswith("cloudflare")][0]
    groq_prev = "prev:" + [s for s in prev_stacks if s.startswith("groq")][0]
    cf_off = [s for s in names if s.startswith("cloudflare")][0]
    groq_now = [s for s in names if s.startswith("groq")][0]
    combos += [(cf_on, cf_off), (groq_prev, groq_now), (groq_now, cf_on)]
    for a, b in combos:
        n, sem, text, both, ao, bo, ws = pair(outs[a], outs[b])
        print(f"| {a} vs {b} | {n} | {sem} ({100 * sem / n:.0f}%) | {text} | {both} | {ao} | {bo} | {ws} |")


if __name__ == "__main__":
    main()
