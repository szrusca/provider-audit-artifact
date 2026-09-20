# 指纹表（自动生成）


## gpt-oss-120b

| 栈 | F1 思考默认 | F2a template | F2b effort=none | F2c /no_think | F3 系统提示 | F4 确定性 | F5 mt=40 | F6 JSON | F7 tools | F8 seed/logprobs/top_k | F9 stop | F10 20K ctx | F11 自述 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| groq `openai/gpt-oss-120b` | on, separate (375/385) | HTTP 400 | HTTP 400 | same 385->451 ok | yes | 1 distinct / 3 | length, text 0ch | yes | 1 calls | 200/HTTP 400/HTTP 400 | no | HTTP 413 |  |
| ovh `gpt-oss-120b` | on, field (1377ch/413) | HTTP 400 | HTTP 429 | HTTP 429 | HTTP 429 | 1 distinct / 3 | length, text 0ch | yes | HTTP 429 | 200/HTTP 400/HTTP 400 | no | no | I am ChatGPT, a large language model built on OpenAI’s GPT‑4 architecture, and my knowledg |
| ollama `gpt-oss:120b` | on, field (1141ch/357) | same 357->286 ok | same 357->368 ok | same 357->394 ok | yes | 1 distinct / 3 | length, text 0ch | yes | 1 calls | 200/200/200 lp:no | no | no | I am ChatGPT, a large language |
| cloudflare `@cf/openai/gpt-oss-120b` | on, field (904ch/299) | same 299->369 ok | HTTP 400 | same 299->523 ok | yes | 1 distinct / 3 | length, text 0ch | yes | 1 calls | 200/200/200 lp:yes | no | no |  |

## qwen3.8-27b

| 栈 | F1 思考默认 | F2a template | F2b effort=none | F2c /no_think | F3 系统提示 | F4 确定性 | F5 mt=40 | F6 JSON | F7 tools | F8 seed/logprobs/top_k | F9 stop | F10 20K ctx | F11 自述 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| groq `qwen/qwen3.8-27b` | off (5) | HTTP 400 | same 5->5 WRONG | same 5->5 WRONG | yes | 1 distinct / 3 | stop, text 4ch | yes | 1 calls | 200/HTTP 400/HTTP 400 | yes | HTTP 413 | I am Qwen, a large language model independently developed by Alibaba Group's Tongyi Lab, a |
| ovh `Qwen3.8-27B` | on, field (4087ch/1489) | HTTP 400 | cut 1489->5 WRONG | same 1489->1640 ok | no | 1 distinct / 3 | length, text 0ch | yes | 1 calls | 200/HTTP 400/HTTP 400 | yes | no |  |
| cloudflare `@cf/qwen/qwen3.8-27b` | on, field (2719ch/999) | cut 999->5 WRONG | HTTP 400 | same 999->893 ok | no | 1 distinct / 3 | length, text 0ch | yes | 1 calls | 200/200/200 lp:yes | yes | no | I am Qwen, a large language model developed by Alibaba |

## qwen3.6-27b

| 栈 | F1 思考默认 | F2a template | F2b effort=none | F2c /no_think | F3 系统提示 | F4 确定性 | F5 mt=40 | F6 JSON | F7 tools | F8 seed/logprobs/top_k | F9 stop | F10 20K ctx | F11 自述 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| groq `qwen/qwen3.6-27b` | on, inline tag (1000) | HTTP 400 | cut 1000->4 WRONG | same 1000->2048 ok | no | 3 distinct / 3 | length, text 121ch | HTTP 400 | 1 calls | 200/HTTP 400/HTTP 400 | no | HTTP 413 | <think>
Thinking Process:

1.  **Analyze the Request:**
    *   Constraint: "In one senten |
| ovh `Qwen3.6-27B` | on, field (5644ch/2048) | HTTP 400 | cut 2048->4 WRONG | HTTP 429 | no | 1 distinct / 2 | HTTP 429 | no | 0 calls | HTTP 429/HTTP 400/HTTP 400 | no | no | HTTP 429 |

## gpt-oss-20b

| 栈 | F1 思考默认 | F2a template | F2b effort=none | F2c /no_think | F3 系统提示 | F4 确定性 | F5 mt=40 | F6 JSON | F7 tools | F8 seed/logprobs/top_k | F9 stop | F10 20K ctx | F11 自述 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| groq `openai/gpt-oss-20b` | on, separate (713/723) | HTTP 400 | HTTP 400 | same 723->433 ok | yes | 1 distinct / 3 | length, text 0ch | yes | 1 calls | 200/HTTP 400/HTTP 400 | no | HTTP 413 | I am ChatGPT |
| ovh `gpt-oss-20b` | on, field (1857ch/584) | HTTP 400 | HTTP 400 | same 584->1024 ok | HTTP 429 | 1 distinct / 3 | length, text 0ch | yes | 1 calls | 200/HTTP 429/HTTP 400 | no | no | HTTP 429 |
| ollama `gpt-oss:20b` | on, field (2329ch/726) | same 726->838 ok | same 726->1015 ok | same 726->585 ok | yes | 2 distinct / 3 | length, text 0ch | yes | 1 calls | 200/200/200 lp:no | no | no |  |
| cloudflare `@cf/openai/gpt-oss-20b` | on, field (1538ch/532) | same 532->1568 ok | HTTP 400 | same 532->644 ok | yes | 1 distinct / 3 | length, text 0ch | yes | 1 calls | 200/200/200 lp:yes | no | no |  |
| nvidia `openai/gpt-oss-20b` | on, field (1982ch/662) | same 662->1103 ok | HTTP 400 | same 662->1179 ok | yes | 1 distinct / 3 | length, text 0ch | yes | 1 calls | 200/200/200 lp:yes | no | no | I am ChatGPT, a large language model developed by OpenAI, with a knowledge cutoff in Septe |

## nemotron-3-super-120b

| 栈 | F1 思考默认 | F2a template | F2b effort=none | F2c /no_think | F3 系统提示 | F4 确定性 | F5 mt=40 | F6 JSON | F7 tools | F8 seed/logprobs/top_k | F9 stop | F10 20K ctx | F11 自述 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ollama `nemotron-3-super` | on, field (3143ch/1202) | same 1202->644 ok | cut 1202->4 WRONG | same 1202->2048 WRONG | yes | 1 distinct / 3 | length, text 0ch | yes | 1 calls | 200/200/200 lp:no | no | no | I am Nemotron 3 Super, a language model developed by NVIDIA, with a knowledge cutoff of Ju |
| openrouter `nvidia/nemotron-3-super-120b-a12b:free` | on, separate (389/633) | same 633->1012 ok | cut 633->4 WRONG | same 633->500 ok | yes | 1 distinct / 2 | HTTP 429 | HTTP 429 | HTTP 429 | HTTP 429/HTTP 429/HTTP 429 | HTTP 429 | HTTP 429 | HTTP 429 |
| cloudflare `@cf/nvidia/nemotron-3-120b-a12b` | on, field (1669ch/643) | cut 643->5 WRONG | HTTP 400 | same 643->823 ok | yes | 1 distinct / 3 | length, text 0ch | yes | 1 calls | 200/200/200 lp:yes | no | no | I am Nemotron 3 Super, a language model developed by NVIDIA, with |
| nvidia `nvidia/nemotron-3-super-120b-a12b` | on, field (4612ch/1711) | cut 1711->4 WRONG | cut 1711->4 WRONG | cut 1711->602 ok | yes | 1 distinct / 3 | length, text 86ch | yes | 1 calls | 200/200/200 lp:yes | no | no | I am Nemotron 3 Super, a large language model developed by NVIDIA, with a knowledge cutoff |
| kilocode `nvidia/nemotron-3-super-120b-a12b:free` | on, separate (397/614) | same 614->701 ok | cut 614->4 WRONG | same 614->859 ok | yes | 1 distinct / 3 | length, text 86ch | yes | 1 calls | 200/200/200 lp:- | no | no | User asks: "In one sentence: what model are you, who developed you, and what is your knowl |

## gemma-4-31b

| 栈 | F1 思考默认 | F2a template | F2b effort=none | F2c /no_think | F3 系统提示 | F4 确定性 | F5 mt=40 | F6 JSON | F7 tools | F8 seed/logprobs/top_k | F9 stop | F10 20K ctx | F11 自述 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ollama `gemma4:31b` | off (4) | same 4->4 WRONG | same 4->4 WRONG | same 4->4 WRONG | yes | 1 distinct / 3 | stop, text 3ch | yes | 1 calls | 200/200/200 lp:no | no | yes | I am a large language model, trained by Google, with a knowledge cutoff that varies by ver |
| openrouter `google/gemma-4-31b-it:free` | HTTP 429 | HTTP 429 | HTTP 429 | HTTP 429 | HTTP 429 | · | HTTP 429 | HTTP 429 | HTTP 429 | HTTP 429/HTTP 429/HTTP 429 | HTTP 429 | HTTP 429 | HTTP 429 |
| nvidia `google/gemma-4-31b-it` | off (4) | same 4->4 WRONG | same 4->4 WRONG | same 4->4 WRONG | yes | 1 distinct / 3 | stop, text 3ch | HTTP 0 | 1 calls | 200/200/200 lp:yes | yes | yes | I am a large language model, trained by Google, with a knowledge cutoff that varies by ver |

## gemma-4-26b-a4b

| 栈 | F1 思考默认 | F2a template | F2b effort=none | F2c /no_think | F3 系统提示 | F4 确定性 | F5 mt=40 | F6 JSON | F7 tools | F8 seed/logprobs/top_k | F9 stop | F10 20K ctx | F11 自述 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cloudflare `@cf/google/gemma-4-26b-a4b-it` | on, field (4356ch/2048) | cut 2048->4 WRONG | same 2048->2048 WRONG | same 2048->2048 WRONG | yes | 2 distinct / 3 | length, text 0ch | yes | 1 calls | 200/200/200 lp:no | no | no |  |
| openrouter `google/gemma-4-26b-a4b-it:free` | HTTP 429 | HTTP 429 | HTTP 429 | HTTP 429 | HTTP 429 | · | HTTP 429 | HTTP 429 | HTTP 429 | HTTP 429/HTTP 429/HTTP 429 | HTTP 429 | HTTP 429 | HTTP 429 |

## glm-5.3-flash

| 栈 | F1 思考默认 | F2a template | F2b effort=none | F2c /no_think | F3 系统提示 | F4 确定性 | F5 mt=40 | F6 JSON | F7 tools | F8 seed/logprobs/top_k | F9 stop | F10 20K ctx | F11 自述 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ollama `glm-5.3-flash` | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 | · | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402/HTTP 402/HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 |
| zhipu `glm-5.3-flash` | on, separate (314/318) | same 318->366 ok | HTTP 400 | same 318->237 ok | yes | 1 distinct / 3 | length, text 0ch | yes | 1 calls | 200/200/200 lp:no | yes | no | I am a GLM |
| cloudflare `@cf/zai-org/glm-5.3-flash` | HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403 | · | HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403/HTTP 403/HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403 |

## glm-5.3

| 栈 | F1 思考默认 | F2a template | F2b effort=none | F2c /no_think | F3 系统提示 | F4 确定性 | F5 mt=40 | F6 JSON | F7 tools | F8 seed/logprobs/top_k | F9 stop | F10 20K ctx | F11 自述 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ollama `glm-5.3` | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 | · | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402/HTTP 402/HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 |
| zhipu `glm-5.3` | on, separate (826/832) | same 832->491 ok | HTTP 400 | cut 832->198 ok | yes | 1 distinct / 3 | length, text 0ch | yes | 1 calls | 200/200/200 lp:no | yes | no | I am GLM, a large language model developed by Z.ai, with knowledge extending to October 20 |
| cloudflare `@cf/zai-org/glm-5.3` | HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403 | · | HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403/HTTP 403/HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403 |

## deepseek-v4-flash

| 栈 | F1 思考默认 | F2a template | F2b effort=none | F2c /no_think | F3 系统提示 | F4 确定性 | F5 mt=40 | F6 JSON | F7 tools | F8 seed/logprobs/top_k | F9 stop | F10 20K ctx | F11 自述 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ollama `deepseek-v4-flash:0731` | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 | · | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402/HTTP 402/HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 |
| cloudflare `@cf/deepseek-ai/deepseek-v4-flash-0731` | HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403 | · | HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403/HTTP 403/HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403 |
| nvidia `deepseek-ai/deepseek-v4-flash-0731` | HTTP 400 | HTTP 400 | HTTP 400 | HTTP 400 | HTTP 400 | · | HTTP 400 | HTTP 400 | HTTP 400 | HTTP 400/HTTP 400/HTTP 0 | HTTP 400 | HTTP 400 | HTTP 400 |

## kimi-k2.6

| 栈 | F1 思考默认 | F2a template | F2b effort=none | F2c /no_think | F3 系统提示 | F4 确定性 | F5 mt=40 | F6 JSON | F7 tools | F8 seed/logprobs/top_k | F9 stop | F10 20K ctx | F11 自述 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ollama `kimi-k2.6` | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 | · | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402/HTTP 402/HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 |
| cloudflare `@cf/moonshotai/kimi-k2.6` | HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403 | · | HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403/HTTP 403/HTTP 403 | HTTP 403 | HTTP 403 | HTTP 403 |
| nvidia `moonshotai/kimi-k2.6` | HTTP 404 | HTTP 404 | HTTP 404 | HTTP 404 | HTTP 404 | · | HTTP 404 | HTTP 404 | HTTP 404 | HTTP 404/HTTP 404/HTTP 404 | HTTP 404 | HTTP 404 | HTTP 404 |

## qwen3.5-397b

| 栈 | F1 思考默认 | F2a template | F2b effort=none | F2c /no_think | F3 系统提示 | F4 确定性 | F5 mt=40 | F6 JSON | F7 tools | F8 seed/logprobs/top_k | F9 stop | F10 20K ctx | F11 自述 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ovh `Qwen3.5-397B-A17B` | HTTP 429 | HTTP 400 | same 0->4 WRONG | same 0->2048 WRONG | no | · | length, text 0ch | HTTP 429 | HTTP 429 | 200/HTTP 400/HTTP 429 | HTTP 429 | HTTP 429 |  |
| ollama `qwen3.5:397b` | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 | · | HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402/HTTP 402/HTTP 402 | HTTP 402 | HTTP 402 | HTTP 402 |
