import glob
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(os.path.dirname(HERE), "runs", "stacks")
OLLAMA = "ollama:gemma4:31b"
NVIDIA = "nvidia:google/gemma-4-31b-it"
PERMUTATIONS = 200000
BOOTSTRAPS = 20000


def is_infra(o):
    return str(o.get("error", "")).startswith("infra")


def sem_eq(a, b):
    return a["ledger"] is not None and a["ledger"] == b["ledger"]


def load_passes():
    samples = {}
    for path in sorted(glob.glob(os.path.join(RUNS, "stacks_gemma431_n160_*.json"))):
        d = json.load(open(path))
        key = min(r["seed"] for r in d["results"]) // 100
        samples.setdefault(key, []).append((os.path.basename(path), d))
    steps = {}
    for key, runs in sorted(samples.items()):
        runs.sort(key=lambda x: x[0])
        for p, (name, d) in enumerate(runs):
            for r in d["results"]:
                steps.setdefault((r["seed"], r["t"]), {})[p] = r["outputs"]
    return samples, steps


def pair_row(results, a, b):
    both = [r["outputs"] for r in results if a in r["outputs"] and b in r["outputs"] and not is_infra(r["outputs"][a]) and not is_infra(r["outputs"][b])]
    n = len(both)
    sem = sum(sem_eq(o[a], o[b]) for o in both)
    text = sum(o[a]["text"] == o[b]["text"] for o in both)
    both_ok = sum(o[a]["kind"] == "ok" and o[b]["kind"] == "ok" for o in both)
    a_only = sum(o[a]["kind"] == "ok" and o[b]["kind"] != "ok" for o in both)
    b_only = sum(o[b]["kind"] == "ok" and o[a]["kind"] != "ok" for o in both)
    return n, sem, text, both_ok, a_only, b_only


def self_row(first, second, s):
    a = {(r["seed"], r["t"]): r["outputs"][s] for r in first["results"] if s in r["outputs"]}
    b = {(r["seed"], r["t"]): r["outputs"][s] for r in second["results"] if s in r["outputs"]}
    both = [(a[k], b[k]) for k in a if k in b and not is_infra(a[k]) and not is_infra(b[k])]
    n = len(both)
    return n, sum(sem_eq(x, y) for x, y in both), sum(x["text"] == y["text"] for x, y in both)


def pooled_rates(steps):
    cross = [0, 0]
    same = [0, 0]
    for ps in steps.values():
        for out in ps.values():
            if OLLAMA in out and NVIDIA in out and not is_infra(out[OLLAMA]) and not is_infra(out[NVIDIA]):
                cross[1] += 1
                cross[0] += not sem_eq(out[OLLAMA], out[NVIDIA])
        if 0 in ps and 1 in ps:
            for s in (OLLAMA, NVIDIA):
                a, b = ps[0].get(s), ps[1].get(s)
                if a and b and not is_infra(a) and not is_infra(b):
                    same[1] += 1
                    same[0] += not sem_eq(a, b)
    return cross, same


def complete_steps(steps):
    quads = []
    for (seed, t), ps in sorted(steps.items()):
        if 0 not in ps or 1 not in ps:
            continue
        outs = [ps[p].get(s) for p in (0, 1) for s in (OLLAMA, NVIDIA)]
        if any(o is None or is_infra(o) for o in outs):
            continue
        quads.append((seed, outs))
    return quads


def decompose(quads):
    cells = {}
    diffs = []
    seeds = []
    clean_direction = {"ollama_wrong": 0, "nvidia_wrong": 0, "both_wrong_differently": 0}
    for seed, (o1, n1, o2, n2) in quads:
        cross = [not sem_eq(o1, n1), not sem_eq(o2, n2)]
        same = [not sem_eq(o1, o2), not sem_eq(n1, n2)]
        cells[(sum(cross), sum(same))] = cells.get((sum(cross), sum(same)), 0) + 1
        diffs.append(statistics.mean(cross) - statistics.mean(same))
        seeds.append(seed)
        if sum(cross) == 2 and sum(same) == 0:
            for a, b in ((o1, n1), (o2, n2)):
                if a["kind"] == "ok" and b["kind"] != "ok":
                    clean_direction["nvidia_wrong"] += 1
                elif b["kind"] == "ok" and a["kind"] != "ok":
                    clean_direction["ollama_wrong"] += 1
                else:
                    clean_direction["both_wrong_differently"] += 1
    return cells, diffs, seeds, clean_direction


def sign_flip_p(values, rng):
    obs = abs(sum(values))
    hits = 0
    for _ in range(PERMUTATIONS):
        if abs(sum(v if rng.random() < 0.5 else -v for v in values)) >= obs - 1e-12:
            hits += 1
    return (hits + 1) / (PERMUTATIONS + 1)


def cluster_bootstrap(by_seed, rng):
    keys = list(by_seed)
    means = []
    for _ in range(BOOTSTRAPS):
        vals = [d for k in (rng.choice(keys) for _ in keys) for d in by_seed[k]]
        means.append(statistics.mean(vals))
    means.sort()
    return means[int(0.025 * BOOTSTRAPS)], means[int(0.975 * BOOTSTRAPS)], sum(m <= 0 for m in means) / BOOTSTRAPS


def main():
    rng = random.Random(20260926)
    samples, steps = load_passes()
    cross, same = pooled_rates(steps)
    print(f"distinct steps {len(steps)}")
    print(f"pooled cross-stack disagreement {cross[0]}/{cross[1]} = {100 * cross[0] / cross[1]:.2f}%")
    print(f"pooled same-stack disagreement {same[0]}/{same[1]} = {100 * same[0] / same[1]:.2f}%")
    print()
    print("per-pass pair rows (n, sem, text, both_ok, ollama_only, nvidia_only)")
    for key, runs in sorted(samples.items()):
        for p, (name, d) in enumerate(sorted(runs, key=lambda x: x[0])):
            print(f"  sample {key} pass {p + 1} {name}: {pair_row(d['results'], OLLAMA, NVIDIA)}")
        first, second = [d for _, d in sorted(runs, key=lambda x: x[0])]
        for s in (OLLAMA, NVIDIA):
            print(f"  sample {key} {s.split(':')[0]} pass 1 vs pass 2 (n, sem, text): {self_row(first, second, s)}")
    quads = complete_steps(steps)
    cells, diffs, seeds, clean_direction = decompose(quads)
    print()
    print(f"steps with all four responses {len(quads)}")
    print("(cross-disagreeing passes, self-disagreeing stacks) -> steps")
    for k in sorted(cells):
        print(f"  {k}: {cells[k]}")
    persistent = sum(v for (c, s), v in cells.items() if c == 2)
    clean = cells.get((2, 0), 0)
    single = cells.get((1, 1), 0)
    print(f"cross disagreements on single-flip steps {single}, on persistent steps {2 * persistent} (clean {2 * clean})")
    print(f"expected persistent steps under independence at the pooled cross rate {len(quads) * (cross[0] / cross[1]) ** 2:.2f}")
    print(f"direction on the clean steps (per comparison) {clean_direction}")
    print(f"mean per-step (cross - same) {100 * statistics.mean(diffs):.2f} points")
    print(f"step-level sign-flip p {sign_flip_p(diffs, rng):.4f}")
    by_seed = {}
    for d, s in zip(diffs, seeds):
        by_seed.setdefault(s, []).append(d)
    print(f"trajectory-level sign-flip p ({len(by_seed)} trajectories) {sign_flip_p([sum(v) for v in by_seed.values()], rng):.4f}")
    lo, hi, p_le0 = cluster_bootstrap(by_seed, rng)
    print(f"trajectory bootstrap 95% interval for the excess {100 * lo:.2f} to {100 * hi:.2f} points, share <= 0: {p_le0:.4f}")


if __name__ == "__main__":
    main()
