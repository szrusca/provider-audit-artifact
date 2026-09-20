# 方向 4 结果（一）：同一开源模型跨 provider 的配置指纹与行为分叉

日期：2026-09-10。设计见 01-design.md，指纹表见 02-fingerprints.md（自动生成），本文汇总阶段 1、阶段 2 并做归因。原始数据在 `runs/`。

## 一、覆盖

- 阶段 1 指纹：25 个栈拿到有效数据（8 个 provider：Groq、OVH 匿名层、Cloudflare、Ollama Cloud、OpenRouter、Zhipu、NVIDIA NIM、Kilo Code），646 次调用。
- 阶段 2 行为分叉：5 个模型家族，同一批 40 个 T1 账本步（种子 7000 起，深度 1/5/9/13），温度 0。加上 9 月 9 日已完成的 qwen3.8-27b 三栈（agent-reliability/results/11），共 6 个家族、20 个栈。
- 退出的家族与原因：glm-5.3 / glm-5.3-flash / deepseek-v4-flash / kimi-k2.6 在 Ollama Cloud 免费层 402、Cloudflare 403、NVIDIA 上 kimi 404，各只剩一个可用栈；gemma-4-26b、qwen3.5-397b 因 OpenRouter 日限 50 次和 OVH 限速在阶段 1 就没凑齐两个栈。

## 二、阶段 1 指纹：八条跨 provider 的差异

1. **思考默认值随 provider 变**。qwen3.8-27b 在 Groq 默认关思考（5 token 直接答），在 OVH、Cloudflare 默认开（1000 到 1500 token）。gemma-4-31b 在 Ollama 和 NVIDIA 都默认关。gpt-oss、nemotron、glm 在所有栈默认开。
2. **思考正文的暴露方式分三种**。Groq、OpenRouter、Zhipu 只给 `reasoning_tokens` 计数；OVH、Ollama、Cloudflare、NVIDIA 把完整思考放进 `message.reasoning`；Kilo 两者都给（计数加 `message.reasoning` 字段）；Groq 上的 qwen3.6-27b 把 `<think>` 段直接写进 `content`，客户端若不剥离就会把思考当答案。
3. **关思考的接口没有任何一种通用**。以 nemotron 五栈为例：NVIDIA 接受 `chat_template_kwargs` 和 `reasoning_effort` 两种；Ollama、Kilo、OpenRouter 只认 `reasoning_effort`；Cloudflare 只认 `chat_template_kwargs`；Groq 对两种都返回 400。`/no_think` 提示词开关在所有栈上无效，只有 Zhipu 的 glm-5.3 对它有反应。
4. **关掉思考后小模型和 nemotron 都答错**。三步算术题在 qwen3.8（OVH、Cloudflare）、nemotron（五栈）、gemma-4-31b（两栈默认就关）上，一旦思考关闭全部出错。这与方向 F 单栈受控实验（agent-reliability/results/13，关思考 67% 对开思考 100%）一致。
5. **provider 侧的硬约束改变了可比性**。Groq 免费层对 20K token 提示返回 413；对 qwen3.6-27b 限制每分钟 1000 输出 token，任何 max_tokens 大于 1000 的请求直接 429。OVH 匿名层每分钟 2 次。OpenRouter 免费池每天 50 次。
6. **温度 0 的确定性**。24 个栈有重复数据，21 个重复请求文本完全一致（其中 2 个只有两次重复）。例外：Cloudflare 的 gemma-4-26b（3 次 2 种）、Ollama 的 gpt-oss-20b（3 次 2 种）、Groq 的 qwen3.6-27b（3 次 3 种）。
7. **系统提示遵守**。qwen3.8-27b 在 Groq 遵守"只用一个法语单词"，在 OVH 和 Cloudflare 不遵守；两家默认开思考，思考后模型倾向于写完整句子。
8. **网关包裹上游错误**。Kilo Code 把 NVIDIA 上游的 502 包在 HTTP 200 里返回，正文是 `{"error": {...code: 502}}`，没有 `choices`。只看状态码的客户端会把它当成"模型输出为空"。阶段 2 第一次 nemotron 组因此在 Kilo 栈出现 8 个假空输出，运行时已修正为基础设施错误并重试。

## 三、阶段 2 行为分叉：按"配置是否一致"分层

下表把两两语义分叉率（基础设施失败已剔除）按指纹表判定的配置差异分层。详细表见文末自动生成部分。

| 层 | 家族 | 栈对数 | 两两语义一致 | 分叉性质 |
|---|---|---|---|---|
| A. 指纹一致，思考默认开 | gpt-oss-120b（4 栈）、gpt-oss-20b（5 栈）、nemotron（4 栈，修正 Kilo 错误分类后重跑） | 6 + 10 + 6 | 95% 到 100%（nemotron 六对全部 100%） | 全部是单栈格式错误（坏 JSON、缺 JSON），没有"两边都给出合法但不同账本"的情况 |
| B. 指纹一致，思考默认关 | gemma-4-31b（Ollama、NVIDIA） | 1 | 91%（34 步可比，3 步分叉） | 两边都给出合法账本但内容不同，且都关思考，无法归到思考默认值 |
| C. 思考默认不一致 | qwen3.8-27b（Groq 关 vs OVH/Cloudflare 开） | 2 | 72% 到 73% | 单边：分叉步几乎全是关思考的 Groq 错 |
| D. provider 约束互斥 | qwen3.6-27b（Groq 每分钟 1000 输出 token vs OVH 强制开思考） | 1 | 0% | Groq 39/40 内联 `<think>` 截断成坏 JSON，OVH 31/39 思考写不完输出为空；两栈都几乎不可用 |

文本级一致率在所有层都只有 62% 到 98%，与语义一致率脱钩：A 层文本一致 75% 到 98%，语义 95% 到 100%。用逐 token 比对评估回放会把 A 层的空格、换行、键顺序差异全部报成分叉。

## 四、归因

- **思考默认值是最大的单一因素**。C 层 27% 的分叉全部可以用"一边开思考一边关"解释，而且方向单边；A 层在思考默认一致时把分叉压到只剩格式错误。这把 9 月 9 日的推断（agent-reliability/results/11 第 2 条）用 6 个家族、20 个栈坐实。
- **剩余的、配置无法解释的分叉约 9%，只在关思考的小模型上出现**（B 层 gemma）。开思考的模型在 T1 上太容易，看不到这类分叉；要确认它是量化/数值路径造成的，需要阶段 4 的 Kaggle 本地参考栈，或者更难的任务族。
- **provider 硬约束本身能让"同一模型"完全不可比**（D 层）。这是审计里最不直观的一条：两家都在正常服务 qwen3.6-27b，但一家限输出速率、一家强制思考，用户找不到对两家都公平的请求参数。
- **网关层的错误语义是独立于模型的第四类差异**。Kilo 的 200 包裹 502、OVH 的 429 被记成空输出，在没有错误分类的日志里都会被算成模型失败，直接污染 p 的估计。事件日志必须同时记状态码、错误体和 usage。

## 五、用户可消除 / 不可消除清单

| 差异 | 可消除？ | 方法或原因 |
|---|---|---|
| 思考默认值 | 部分 | NVIDIA、Cloudflare、Ollama、Kilo、OpenRouter 至少有一种开关可用；Groq 的 qwen3.8 和 OVH 的所有 qwen 都不可切换 |
| 思考正文位置 | 否 | 由 provider 的响应格式决定，客户端只能适配 |
| 输出速率上限（Groq qwen3.6） | 否 | 免费层配额 |
| 长上下文 413（Groq） | 否 | 免费层 TPM |
| 网关包裹错误（Kilo） | 客户端可适配 | 解析响应体里的 `error` 字段 |
| 温度 0 不确定性（3 个栈） | 否 | 服务端批处理与内核实现 |
| B 层数值分叉（gemma） | 否 | 需参考栈确认来源 |

## 六、对方向 F 论文的直接用处

- 事件日志中的模型标识必须是 (provider, model, 思考模式, 日期) 四元组，仅模型名不足以保证回放可信（RQ3.3 结论的扩展证据）。
- 升级目标可以在 A 层栈之间自由切换而不改变结果，实验二把升级调用分散到 NVIDIA、Kilo、Ollama、Cloudflare 是安全的。
- 实验一里 Groq qwen3.8 的低 p 有 provider 成分，论文中要注明。

## 七、局限与下一步

- T1 对开思考的大模型太容易，A 层全部接近 100% 正确，看不到"两边都合法但不同"的分叉；下一步在 T2 仓库任务上重复 A 层。
- gemma 只有两栈、34 个可比步，B 层结论样本小；OpenRouter 配额恢复后补第三栈。
- OVH 只能匿名层，429 剔除后有效样本 32 到 39 步。
- 阶段 4：Kaggle T4 上以 fp16 与 4-bit 各跑一遍 gemma-4-31b（或 gpt-oss-20b），作为 B 层分叉的裁决。


## 附：阶段 2 自动生成表

`stacks_nemotron_super_20260910-154900` 是修正 Kilo 包裹错误分类之前的第一次运行，Kilo 栈的 8 个空输出实为上游 502；`stacks_nemotron_super_v2_*` 是修正后的重跑，以后者为准。


## gemma431  (40 步, stacks_gemma431_20260910-161048.json)

| 栈 | n（有效） | 基础设施失败 | 正确 | 各类结果 | 中位延迟 s | 平均 token |
|---|---|---|---|---|---|---|
| ollama:gemma4:31b | 40 | 0 | 32 (80%) | ok=32, semantic=8 | 0.8 | 1437 |
| nvidia:google/gemma-4-31b-it | 34 | 6 | 28 (82%) | ok=28, semantic=6 | 38.1 | 1370 |

| 栈对 | n | 文本一致 | 语义一致 | 两边都对 | 仅前者对 | 仅后者对 |
|---|---|---|---|---|---|---|
| ollama vs nvidia | 34 | 31 (91%) | 31 (91%) | 27 | 1 | 1 |

## gptoss120b  (40 步, stacks_gptoss120b_20260910-190022.json)

| 栈 | n（有效） | 基础设施失败 | 正确 | 各类结果 | 中位延迟 s | 平均 token |
|---|---|---|---|---|---|---|
| groq:openai/gpt-oss-120b | 40 | 0 | 40 (100%) | ok=40 | 0.9 | 1765 |
| ovh:gpt-oss-120b | 32 | 8 | 32 (100%) | ok=32 | 3.7 | 1514 |
| ollama:gpt-oss:120b | 40 | 0 | 40 (100%) | ok=40 | 1.7 | 1516 |
| cloudflare:@cf/openai/gpt-oss-120b | 20 | 0 | 19 (95%) | format_nojson=1, ok=19 | 5.3 | 1681 |

| 栈对 | n | 文本一致 | 语义一致 | 两边都对 | 仅前者对 | 仅后者对 |
|---|---|---|---|---|---|---|
| groq vs ovh | 32 | 32 (100%) | 32 (100%) | 32 | 0 | 0 |
| groq vs ollama | 40 | 39 (98%) | 40 (100%) | 40 | 0 | 0 |
| groq vs cloudflare | 20 | 18 (90%) | 19 (95%) | 19 | 1 | 0 |
| ovh vs ollama | 32 | 31 (97%) | 32 (100%) | 32 | 0 | 0 |
| ovh vs cloudflare | 19 | 17 (89%) | 18 (95%) | 18 | 1 | 0 |
| ollama vs cloudflare | 20 | 17 (85%) | 19 (95%) | 19 | 1 | 0 |

## gptoss20b  (40 步, stacks_gptoss20b_20260910-181315.json)

| 栈 | n（有效） | 基础设施失败 | 正确 | 各类结果 | 中位延迟 s | 平均 token |
|---|---|---|---|---|---|---|
| groq:openai/gpt-oss-20b | 40 | 0 | 40 (100%) | ok=40 | 0.6 | 1752 |
| ovh:gpt-oss-20b | 39 | 1 | 39 (100%) | ok=39 | 4.1 | 1468 |
| ollama:gpt-oss:20b | 40 | 0 | 40 (100%) | ok=40 | 4.3 | 1507 |
| cloudflare:@cf/openai/gpt-oss-20b | 20 | 0 | 20 (100%) | ok=20 | 3.7 | 1508 |
| nvidia:openai/gpt-oss-20b | 40 | 0 | 39 (98%) | format_badjson=1, ok=39 | 13.9 | 1492 |

| 栈对 | n | 文本一致 | 语义一致 | 两边都对 | 仅前者对 | 仅后者对 |
|---|---|---|---|---|---|---|
| groq vs ovh | 39 | 36 (92%) | 39 (100%) | 39 | 0 | 0 |
| groq vs ollama | 40 | 36 (90%) | 40 (100%) | 40 | 0 | 0 |
| groq vs cloudflare | 20 | 18 (90%) | 20 (100%) | 20 | 0 | 0 |
| groq vs nvidia | 40 | 34 (85%) | 39 (98%) | 39 | 1 | 0 |
| ovh vs ollama | 39 | 36 (92%) | 39 (100%) | 39 | 0 | 0 |
| ovh vs cloudflare | 19 | 18 (95%) | 19 (100%) | 19 | 0 | 0 |
| ovh vs nvidia | 39 | 33 (85%) | 38 (97%) | 38 | 1 | 0 |
| ollama vs cloudflare | 20 | 17 (85%) | 20 (100%) | 20 | 0 | 0 |
| ollama vs nvidia | 40 | 32 (80%) | 39 (98%) | 39 | 1 | 0 |
| cloudflare vs nvidia | 20 | 17 (85%) | 20 (100%) | 20 | 0 | 0 |

## nemotron_super  (40 步, stacks_nemotron_super_20260910-154900.json)

| 栈 | n（有效） | 基础设施失败 | 正确 | 各类结果 | 中位延迟 s | 平均 token |
|---|---|---|---|---|---|---|
| ollama:nemotron-3-super | 40 | 0 | 40 (100%) | ok=40 | 9.0 | 1906 |
| cloudflare:@cf/nvidia/nemotron-3-120b-a12b | 18 | 1 | 18 (100%) | ok=18 | 5.0 | 1787 |
| nvidia:nvidia/nemotron-3-super-120b-a12b | 40 | 0 | 40 (100%) | ok=40 | 8.9 | 1898 |
| kilocode:nvidia/nemotron-3-super-120b-a12b:free | 40 | 0 | 31 (78%) | format_empty=8, ok=31, semantic=1 | 6.3 | 1616 |

| 栈对 | n | 文本一致 | 语义一致 | 两边都对 | 仅前者对 | 仅后者对 |
|---|---|---|---|---|---|---|
| ollama vs cloudflare | 18 | 16 (89%) | 18 (100%) | 18 | 0 | 0 |
| ollama vs nvidia | 40 | 30 (75%) | 40 (100%) | 40 | 0 | 0 |
| ollama vs kilocode | 40 | 25 (62%) | 31 (78%) | 31 | 9 | 0 |
| cloudflare vs nvidia | 18 | 15 (83%) | 18 (100%) | 18 | 0 | 0 |
| cloudflare vs kilocode | 18 | 13 (72%) | 13 (72%) | 13 | 5 | 0 |
| nvidia vs kilocode | 40 | 30 (75%) | 31 (78%) | 31 | 9 | 0 |

## nemotron_super_v2  (40 步, stacks_nemotron_super_v2_20260910-202513.json)

| 栈 | n（有效） | 基础设施失败 | 正确 | 各类结果 | 中位延迟 s | 平均 token |
|---|---|---|---|---|---|---|
| ollama:nemotron-3-super | 40 | 0 | 40 (100%) | ok=40 | 7.0 | 1907 |
| cloudflare:@cf/nvidia/nemotron-3-120b-a12b | 15 | 5 | 15 (100%) | ok=15 | 7.8 | 1868 |
| nvidia:nvidia/nemotron-3-super-120b-a12b | 40 | 0 | 40 (100%) | ok=40 | 5.2 | 1879 |
| kilocode:nvidia/nemotron-3-super-120b-a12b:free | 39 | 1 | 39 (100%) | ok=39 | 4.7 | 2110 |

| 栈对 | n | 文本一致 | 语义一致 | 两边都对 | 仅前者对 | 仅后者对 |
|---|---|---|---|---|---|---|
| ollama vs cloudflare | 15 | 11 (73%) | 15 (100%) | 15 | 0 | 0 |
| ollama vs nvidia | 40 | 33 (82%) | 40 (100%) | 40 | 0 | 0 |
| ollama vs kilocode | 39 | 34 (87%) | 39 (100%) | 39 | 0 | 0 |
| cloudflare vs nvidia | 15 | 12 (80%) | 15 (100%) | 15 | 0 | 0 |
| cloudflare vs kilocode | 15 | 11 (73%) | 15 (100%) | 15 | 0 | 0 |
| nvidia vs kilocode | 39 | 36 (92%) | 39 (100%) | 39 | 0 | 0 |

## qwen36  (40 步, stacks_qwen36_20260910-193707.json)

| 栈 | n（有效） | 基础设施失败 | 正确 | 各类结果 | 中位延迟 s | 平均 token |
|---|---|---|---|---|---|---|
| groq:qwen/qwen3.6-27b | 40 | 0 | 0 (0%) | format_badjson=39, semantic=1 | 2.3 | 2330 |
| ovh:Qwen3.6-27B | 39 | 1 | 6 (15%) | format_empty=31, format_nojson=2, ok=6 | 12.6 | 2348 |

| 栈对 | n | 文本一致 | 语义一致 | 两边都对 | 仅前者对 | 仅后者对 |
|---|---|---|---|---|---|---|
| groq vs ovh | 39 | 0 (0%) | 0 (0%) | 0 | 0 | 6 |

## 补充（2026-09-13）：qwen3.6-27b 双方强制关思考的对照

审稿指出 D 层"无公平请求"的说法与指纹表矛盾：两家都接受 `reasoning_effort=none`。补跑同 40 步、双方 `reasoning_effort=none`、max_tokens 1000（`runs/stacks/stacks_qwen36_off_*`）：

| 栈 | 有效 | 基础设施失败 | 正确 |
|---|---|---|---|
| Groq | 40 | 0 | 26（65%） |
| OVH | 37 | 3 | 27（73%） |

37 个可比步：语义一致 31（84%），其中 23 步两边都对、8 步两边给出相同的错账本；6 步分歧，1 步仅 Groq 对、4 步仅 OVH 对、1 步两边错得不同，全部格式合法。文本一致同为 84%。

结论：D 层改述为"默认设置下不可比"；在唯一共同的覆盖设置下，这一对的行为与 B 层（gemma 双关思考）同形：双向、格式合法、约 16% 的残余分叉，且有共享的确定性错答案。论文 Table IV 加 D′ 行。

## 补充（2026-09-20）：B 层与 D′ 层的同栈重复基线

审稿指出 B 层 9% 到 16% 的残余分叉没有同栈重复基线，无法与批处理非确定性区分。补跑同 40 步（seed 7000 起，深度 1/5/9/13），与首次运行逐步比对（`python3 -m audit.compare_repeat <first.json> <second.json>`）：

| 栈 | 首次 | 重跑 | 可比步 | 文本一致 | 语义一致 | 两次都对 | 仅一次对 | 两次同错 | 两次异错 |
|---|---|---|---|---|---|---|---|---|---|
| ollama:gemma4:31b（默认关思考） | 09-10 | 09-20 | 40 | 38（95%） | 38（95%） | 31 | 1 | 7 | 1 |
| ovh:Qwen3.6-27B（reasoning_effort=none，max_tokens 1000） | 09-13 | 09-20 | 30 | 26（87%） | 26（87%） | 21 | 2 | 5 | 2 |

文件：`runs/stacks/stacks_gemma431_rep_ollama_20260920-023752.json`、`runs/stacks/stacks_qwen36_off_rep_20260920-014340.json`。OVH 重跑 40 步中 7 步 429 剔除；首次 3 步 429，故可比 30 步。

未能完成的两个栈：

- Groq `qwen/qwen3.6-27b`：40 步全部 404 `model_not_found`，Groq 目录（2026-09-20 查询）已无此模型，D′ 的 Groq 侧无法重复。
- NVIDIA `google/gemma-4-31b-it`：与 Ollama 合跑 8 步（`stacks_gemma431_rep_partial_*`），应答的 4 步延迟 116 到 232 秒，另 4 步 240 秒超时；拆出的单独运行（`stacks_gemma431_rep_nvidia_*`）前 9 步全部 240 秒超时，已中止。NIM 侧同栈基线未获得。

结论：同栈相隔 7 到 10 天重跑的分叉为 5%（gemma Ollama）与 13%（qwen3.6 OVH），跨栈同日分叉为 9%（B 层）与 16%（D′ 层）。两个基线测的不是同一个量（同日跨栈 = 引擎差异 + 非确定性；跨日同栈 = 非确定性 + provider 一周内变化），不能相减，只能给上界：跨 provider 分叉不大于单栈自身一周内的变动，在 30 到 40 步样本下两者不可区分。要单独分离非确定性需同日重跑。第四节"剩余的、配置无法解释的分叉约 9%"应据此弱化为上界表述，不是引擎差异的证据。
