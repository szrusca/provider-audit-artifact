# Same Name, Different Model: artifact

Probes, raw responses, run logs, and analysis scripts for the paper *Same Name, Different Model: A Configuration Audit of Open-Weight LLMs Across Inference Providers* (Zhouran Song, Independent Researcher, 2026; under review).

The audit has two phases. Phase 1 sends eleven configuration probes (F1 to F11) to every (provider, model identifier) pair, called a *stack*, and stores every raw response body. Phase 2 sends the same 40 steps of an integer-ledger state-tracking workload at temperature 0 to every stack of a model family and compares the returned ledgers pairwise, structurally and textually, after removing infrastructure failures. All prompts are synthetic. No company or personal data was sent to any provider.

## Author and contact

Zhouran Song, Independent Researcher, Santa Clara, California. ORCID [0009-0001-2985-0012](https://orcid.org/0009-0001-2985-0012). Contact: songzhouran@gmail.com. Issues and pull requests are welcome.

## Layout

```
audit/
  fingerprint.py            Phase 1: probes F1-F11; the STACKS table defines the model x provider matrix
  analyze_fingerprint.py    builds results/02-fingerprints.md from runs/fingerprint_*.jsonl
  stacks.py                 Phase 2: sends the same ledger steps to several stacks, writes event logs
  analyze_stacks.py         pairwise textual and semantic agreement, infrastructure failures excluded
  providers.py              one call() over the OpenAI-compatible endpoints; rate pacer; wrapped-error detection
  env.py events.py pricing.py tasks_t1.py   shared infrastructure (env loading, event schema, T1 ledger task)
results/
  01-design.md              experiment design, research questions, stack matrix, quotas (working notes, Chinese)
  02-fingerprints.md        fingerprint table, generated; source of Table III in the paper
  03-stacks.md              Phase 2 results and attribution; source of Table IV
runs/
  models_discovery.json     provider catalog snapshot, 2026-09-09
  fingerprint_<provider>_<timestamp>.jsonl   one record per probe call with the full raw response body
  stacks/<label>_<timestamp>.json            Phase 2 per-run summary
  stacks/<label>_<timestamp>.events.jsonl    Phase 2 event log, one record per request and response
companion/
  results/11-stacks-qwen.md                  qwen3.8-27b on Groq, OVH, Cloudflare (60 steps, 2026-09-09; Layer C)
  results/13-stacks-thinking-ctrl.md         nemotron-3-super-120b on NVIDIA NIM, reasoning off vs. on (Layer C control)
  runs/                                      the run summaries and event logs behind those two files
scripts/phase2.sh           the Phase 2 run chain as executed
logs/                       console logs of the probe passes
```

`companion/` holds the two measurements that the paper takes from a companion study of agent recovery, which used the same request format and the same T1 ledger task.

## Mapping from the paper

| Paper | File |
|---|---|
| Table I (families and stacks) | `runs/models_discovery.json`, `audit/fingerprint.py` (`STACKS`) |
| Table II (probe battery) | `audit/fingerprint.py` |
| Table III (fingerprints) | `results/02-fingerprints.md`, raw bodies in `runs/fingerprint_*.jsonl` |
| Table IV, Layers A, B, D, D' | `results/03-stacks.md`, `runs/stacks/` |
| Table IV, Layer C | `companion/results/11-stacks-qwen.md`, `companion/results/13-stacks-thinking-ctrl.md` |
| Section IV-B (gateway-wrapped errors) | `runs/stacks/stacks_nemotron_super_20260910-*.events.jsonl` (first run) vs. `stacks_nemotron_super_v2_*` (rerun) |

## Reproducing

Python 3.10 or later, standard library only. API keys are read from a `.env` file in the repository root or its parent (`GROQ_API_KEY`, `OVH_API_KEY`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `OLLAMA_API_KEY`, `OPENROUTER_API_KEY`, `ZHIPU_API_KEY`, `NVIDIA_API_KEY`, `KILOCODE_API_KEY`); no key is stored in this repository.

```
python3 -m audit.fingerprint --provider groq                  # all stacks of one provider
python3 -m audit.fingerprint --provider ovh --retry-missing   # retry only the retryable failures
python3 -m audit.analyze_fingerprint > results/02-fingerprints.md
python3 -m audit.stacks --label gptoss20b --n 40 \
  --stacks "groq|openai/gpt-oss-20b,ovh|gpt-oss-20b" --out runs/stacks
python3 -m audit.analyze_stacks
bash scripts/phase2.sh                                        # the full Phase 2 chain
```

Provider defaults, catalogs, and free-tier limits change without notice. Every number in the paper is dated 2026-09-09 to 2026-09-20, and one stack (Groq's qwen3.6-27b) was withdrawn from the catalog inside that window, so a rerun today will not reproduce the tables exactly. The raw responses in `runs/` are the record of what the providers returned on those dates.

## Citing

```bibtex
@misc{song2026samename,
  author = {Song, Zhouran},
  title  = {Same Name, Different Model: A Configuration Audit of Open-Weight {LLMs} Across Inference Providers},
  year   = {2026},
  note   = {Manuscript under review. Artifact: \url{https://github.com/szrusca/provider-audit-artifact}}
}
```

## License

Source code in `audit/` and `scripts/` is under the MIT License (`LICENSE`). Data in `runs/`, `results/`, `logs/`, and `companion/` is under CC BY 4.0 (`LICENSE-DATA.md`).
