# 方向 4 实验设计：同一开源模型跨 provider 的配置审计

日期：2026-09-09。本轮不使用 Kilo Code 与 NVIDIA 的 key。Cerebras 返回 402（未激活），HF router 无 token，均不纳入。

## 研究问题

- RQ4.1 同名同权重的开源模型在不同 provider 上，默认推理配置（思考开关、可否切换、系统提示遵守、JSON 模式、工具调用、采样参数容忍、停止序列、长上下文）有多大差异？
- RQ4.2 在长程账本任务上，跨 provider 的语义分叉率有多大？分叉能否用 RQ4.1 的配置指纹解释？
- RQ4.3 哪些差异是用户可消除的（可通过参数切换），哪些是不可消除的（provider 固定了默认值）？

## 阶段 0：目录发现（已完成）

`runs/models_discovery.json`。可用 provider：Groq、OVH（匿名层）、Cloudflare Workers AI、Ollama Cloud、OpenRouter（:free）、Zhipu。

| 模型 | 栈 | 数 |
|---|---|---|
| gpt-oss-120b | groq `openai/gpt-oss-120b`、ovh `gpt-oss-120b`、ollama `gpt-oss:120b`、cloudflare `@cf/openai/gpt-oss-120b` | 4 |
| qwen3.8-27b | groq `qwen/qwen3.8-27b`、ovh `Qwen3.8-27B`、cloudflare `@cf/qwen/qwen3.8-27b` | 3 |
| qwen3.6-27b | groq `qwen/qwen3.6-27b`、ovh `Qwen3.6-27B` | 2 |
| nemotron-3-super-120b | ollama `nemotron-3-super`、openrouter `nvidia/nemotron-3-super-120b-a12b:free`、cloudflare `@cf/nvidia/nemotron-3-120b-a12b` | 3 |
| gemma-4-31b | ollama `gemma4:31b`、openrouter `google/gemma-4-31b-it:free` | 2 |
| gemma-4-26b-a4b | cloudflare `@cf/google/gemma-4-26b-a4b-it`、openrouter `google/gemma-4-26b-a4b-it:free` | 2 |
| glm-5.3-flash | ollama `glm-5.3-flash`、zhipu `glm-5.3-flash`、cloudflare `@cf/zai-org/glm-5.3-flash` | 3 |
| glm-5.3 | ollama `glm-5.3`、zhipu `glm-5.3`、cloudflare `@cf/zai-org/glm-5.3` | 3 |
| deepseek-v4-flash | ollama `deepseek-v4-flash:0731`、cloudflare `@cf/deepseek-ai/deepseek-v4-flash-0731` | 2 |
| kimi-k2.6 | ollama `kimi-k2.6`、cloudflare `@cf/moonshotai/kimi-k2.6` | 2 |
| qwen3.5-397b | ovh `Qwen3.5-397B-A17B`、ollama `qwen3.5:397b` | 2 |

11 个模型，28 个栈。Zhipu 上 glm-5.3 是否在免费额度内由探针结果判定。

## 阶段 1：配置指纹（每栈约 16 次调用，温度 0）

| 探针 | 内容 | 记录 |
|---|---|---|
| F1 reasoning_default | 三步算术应用题，max_tokens 2048 | 输出 token、reasoning_tokens 字段、message 里是否有 reasoning/reasoning_content、正文是否含 `<think>`、是否以空行开头、答案是否正确 |
| F2 reasoning_switch | 同题，分别附加 `chat_template_kwargs.enable_thinking=false`、`reasoning_effort=none`、系统提示 `/no_think` | 状态码、输出 token 相对 F1 的变化 |
| F3 system_adherence | 系统提示要求只用一个法语单词回答 | 是否遵守 |
| F4 determinism | F1 同请求重复 3 次 | 文本完全一致的比例 |
| F5 max_tokens_semantics | F1 同题，max_tokens 40 | finish_reason、正文是否为空（思考是否吃掉预算） |
| F6 json_mode | `response_format={"type":"json_object"}` | 状态码、正文是否为合法 JSON |
| F7 tools | 一个 get_weather 工具定义 | 是否返回 tool_calls、状态码 |
| F8 params | 分别单独发送 `seed`、`logprobs`、`top_k` | 状态码（接受、忽略、400） |
| F9 stop | 数 1 到 10，stop=["6"] | 输出是否在 6 前停止 |
| F10 long_context | 约 20K token 填充文本中埋一个口令 | 状态码、是否找回口令 |
| F11 identity | 一句话自述模型名与开发方 | 原文 |

输出：`runs/fingerprint_<provider>_<ts>.jsonl`，每行一次调用的完整原始响应；汇总表 `results/02-fingerprints.md`。

## 阶段 2：行为分叉（复用 `audit/stacks.py`）

对每个有 2 个以上栈的模型，同一批 40 个 T1 账本步（种子 7000 起，深度 1/5/9/13），温度 0，max_tokens 4096。指标：单栈正确率、两两文本一致率、两两语义一致率、"恰一边对"的方向。Cloudflare 每天每模型上限 20 步，分两天完成。

已完成的部分可直接复用：qwen3.8-27b 三栈（agent-reliability/results/11）、nemotron 四栈（agent-reliability/results/12，其中 NVIDIA 与 Kilo 两栈本轮不再重跑）。

## 阶段 3：归因

把阶段 2 的两两语义分叉率与阶段 1 的指纹差异做交叉：
- 指纹完全相同的栈对 vs 思考默认不同的栈对 vs 其他差异的栈对。
- 预期（基于 11、12、13）：思考默认一致时语义分叉接近 0，思考默认不一致时分叉 20% 以上且单边。
- 对每个模型给出"用户可消除"与"用户不可消除"的差异清单。

## 阶段 4（可选，需 Kaggle）

在 Kaggle T4 x2 上以已知配置本地运行 gpt-oss-20b、qwen3.8-27b 4-bit，作为参考栈，把阶段 2 的分叉进一步归因到量化与模板。

## 配额约束

| provider | 约束 | 阶段 1 用量 | 阶段 2 用量 |
|---|---|---|---|
| Groq | 每模型每天 1000 次、20 万 token | 3 栈 × 16 | 3 × 40 |
| OVH 匿名 | 2 RPM | 4 栈 × 16，约 35 分钟 | 4 × 40，约 80 分钟 |
| Cloudflare | 每天 10,000 neurons | 8 栈 × 16 = 128 次，可能触顶，分两天 | 每天 ≤ 60 步 |
| Ollama Cloud | 未知，实测 | 9 栈 × 16 | 9 × 40 |
| OpenRouter | 每天 50 次 | 3 栈 × 16 = 48，刚好一天 | 每天 50 步 |
| Zhipu | 免费模型限速未知 | 2 栈 × 16 | 2 × 40 |
