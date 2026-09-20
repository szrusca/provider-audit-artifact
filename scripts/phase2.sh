#!/bin/bash
cd "$(dirname "$0")/.."
run() { python3 -m audit.stacks --label "$1" --n 40 --stacks "$2" --limit "${3:-}" --rpm "groq=10,ovh=1.5,cloudflare=6,openrouter=4,ollama=3,zhipu=6,nvidia=4,kilocode=3" --out runs/stacks; }
run nemotron_super "ollama|nemotron-3-super,cloudflare|@cf/nvidia/nemotron-3-120b-a12b,nvidia|nvidia/nemotron-3-super-120b-a12b,kilocode|nvidia/nemotron-3-super-120b-a12b:free" "cloudflare=20"
run gemma431 "ollama|gemma4:31b,nvidia|google/gemma-4-31b-it"
run gptoss20b "groq|openai/gpt-oss-20b,ovh|gpt-oss-20b,ollama|gpt-oss:20b,cloudflare|@cf/openai/gpt-oss-20b,nvidia|openai/gpt-oss-20b" "cloudflare=20"
run gptoss120b "groq|openai/gpt-oss-120b,ovh|gpt-oss-120b,ollama|gpt-oss:120b,cloudflare|@cf/openai/gpt-oss-120b" "cloudflare=20"
run() { python3 -m audit.stacks --label "$1" --n 40 --stacks "$2" --limit "${3:-}" --max-tokens 1000 --rpm "groq=10,ovh=1.5" --out runs/stacks; }
run qwen36 "groq|qwen/qwen3.6-27b,ovh|Qwen3.6-27B"
python3 -m audit.audit --provider groq --retry-missing > logs/fp3_groq.log 2>&1
echo PHASE2_DONE
