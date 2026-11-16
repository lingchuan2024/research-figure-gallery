# 输入数据格式与真实日志映射

## 一份 CSV：observations.csv

UTF-8（可带 BOM），第一行为表头。**一行 = 一题 × 一方法 × 已选定的一次运行**。唯一键为 `(benchmark, question_id, method)`；题号用字符串。不同 benchmark 可以有相同题号。每个 benchmark 中，配置内所有方法必须具有完全相同的题目集合，不能自动按交集丢题。

```csv
benchmark,question_id,subset,method,score,status,wall_seconds,rerank_seconds,main_input_tokens,reranker_input_tokens,rerank_events,scored_passages
DemoQA,q001,Bridge,baseline,0,complete,44.2,0,10320,0,0,0
DemoQA,q001,Bridge,auto_rerank,1,complete,48.6,3.8,9400,6100,6,300
DemoQA,q001,Bridge,v14,1,complete,39.1,1.2,8100,2050,2,100
```

这三行仅解释格式，是虚构值；只有一题时不能对总体效果作可靠推断。完整可运行例子见 `data/demo/observations.csv`。

| 字段 | 是否必需 | 类型 / 单位 | 定义 |
| --- | --- | --- | --- |
| `benchmark` | 是 | 非空字符串 | 数据集与评测划分；同名下所有方法必须可比较 |
| `question_id` | 是 | 非空字符串 | 稳定题号，不依赖 CSV 行号 |
| `subset` | 是 | 非空字符串 | 互斥题型；同题各方法必须一致；无分层填 `unstratified`，`All` 保留给自动汇总 |
| `method` | 是 | 字符串 | 必须与 config.methods 中的 id 完全相同 |
| `score` | 是 | 有限数值 [0,1] | 每题质量；binary 时严格为 0/1，bounded 时可为 nDCG 等 [0,1] 值；不能提前乘 100 |
| `status` | 是 | 枚举 | `complete`、`timeout`、`no_final`、`error`，见下方说明 |
| `wall_seconds` | 成本图按需 | 非负秒数 | 整题端到端观测时间；并发实验中的每题 elapsed，不是吞吐量 |
| `rerank_seconds` | 成本图按需 | 非负秒数 | 整题累计 reranker **评分**时间；不自动包含准备、网络或排队时间 |
| `main_input_tokens` | 成本图按需 | 非负整数 | 整段轨迹累计主模型输入 token，包括被重复输入的上下文；应统一是否包含缓存输入 |
| `reranker_input_tokens` | 成本图按需 | 非负整数 | 整题累计独立 reranker 输入 token，单独统计 |
| `rerank_events` | 成本图按需 | 非负整数 | 整题实际重排事件，包括自动触发；不是主模型显式工具动作数 |
| `scored_passages` | 成本图按需 | 非负整数 | 整题累计被评分片段次数；同一片段被多次评分可多次计数 |

成本列可以缺列或留空，读取后为缺失值。默认绘图成本是 `wall_seconds`，需要该列有实际值；森林图只需要身份、score、status。填入了数值的成本列即使本次未使用，也会检查是否有限、非负及是否满足整数要求。`nan` / `inf` 不是缺失标记，会报错。

**状态定义：**`complete` 表示有可判分的终态回答，回答可能错误；`timeout` 表示超时且没有可判分的终态回答；`no_final` 表示结束但无终态回答；`error` 表示执行失败。对于 binary 最终答题指标，后三者 `score=0`；仍保留已观测耗时及资源。达到轮数上限但已有正常可判分回答的记录应是 `complete`，停止原因另写条件/日志，不能直接把 stop_reason 当作本字段。完全没运行的题不是零耗时失败，不得补造一行。

**零与缺失不同：**确认未调用 reranker 的 baseline，其重排秒数、事件数、输入 token 可以为 0；日志中没记录或资源文件缺失应留空。小数 token 或事件次数会报错；秒数允许小数。切勿把返回 100 个字符记成 100 tokens。

## JSON 配置

以 `config.measured.example.json` 为起点，填完所有 `REPLACE_...` 占位符。代码会保留整个配置到产物 provenance。

| 字段 | 含义 |
| --- | --- |
| `schema_version` | 当前为整数 1 |
| `data_kind` | `synthetic` 或 `measured`，决定图底声明；真实值必须显式改为 measured |
| `experiment` | 本次比较的名称与范围 |
| `methods` | 有序列表，每项含 `id`、图中 `label`、Matplotlib 支持的 `color`；不假设固定 3 方法 |
| `baseline` | 森林图的参照 method ID |
| `score.label` | 明确指标，例如 Answer accuracy、EM、nDCG@10；Recall 需说明定义和 k |
| `score.kind` | binary 或 bounded；所有 benchmark 必须使用相同指标定义 |
| `score.scale` | 仅用于展示的倍数：准确率百分比常用 100，nDCG 原分数常用 1 |
| `score.unit` | 点估计单位，例如 `%` 或 `score` |
| `score.delta_unit` | 差值单位，例如 `pp` 或 `score`；不是相对百分比增长 |
| `conditions.question_set` | 数据集版本、split、实际题集或题集文件摘要 |
| `conditions.generator_model` | 主模型版本与解码条件；离线纯 rerank 写明不使用生成模型 |
| `conditions.retrieval_policy` | 索引、检索器、候选池策略、M/K/limit、作用范围；记录固定或变化的条件 |
| `conditions.hardware` | 硬件与服务环境；不能把不同环境的秒数当成同条件成本 |
| `conditions.concurrency` | batch 与并发；同硬件不同负载仍可能不可比 |
| `conditions.stopping_rule` | 轮数/时间限制、超时与失败的计分规则 |
| `conditions.run_selection` | 各方法选定的 run/seed；明确未池化重复运行 |

可以在配置中加自己的模型、数据版本、成本计费定义等元数据，都会保留。新增方法/预算配置要同步增加对应逐题行；方法数量不受写死的三组限制。

## 统计与对照约束

- 一份数据只用一种质量指标及方向（越大越好）。Accuracy、EM、nDCG、MRR、Hit/Recall 不能混填；不同截止 k 的 nDCG 也应分文件/配置。每个 benchmark 独立聚合，不生成跨 benchmark 的混合平均。
- 同题的多次 rerank 调用先按所选资源定义聚合为题级累计量，不能当成独立问题。`run_id` 或 `seed` 不是当前唯一键的一部分；重复运行需分文件作图，或先采用预先约定的题内聚合与层级统计方法。当前 bootstrap 只描述所选运行下的问题抽样不确定性。
- 森林图按题目配对重采样差值；不是把两组区间分别计算后相减。所有方法的配对集合必须完全一致，行顺序无影响。
- 成本缺失可选择 `--missing-cost complete-case`。按 `(benchmark, question_id)` 移除所有方法的对应行，Pareto 同时在共同样本上重新计算质量与成本；`*_provenance.json` 的 `missing_cost_audit` 保存排除名单与前后 n。
- 不自动丢弃超时、答错或未调用 rerank 的题。观测到超时上限时，耗时是受限观测；图展示的是已记录值，不能解释成没有超时限制时的完成时间分布。
- 同方法中单题或所有差值相同的组，经验 bootstrap 可能退化为零宽区间；这不证明总体没有不确定性。图始终标出 n，不能把小样本形式上的区间当成强证据。

## 日志字段映射示例

以下是人工导出时可采用的字段映射示例，不对应某个已执行实验。实际名称和嵌套层级由你的日志格式决定；模板只读取导出的 CSV，不会自动扫描运行日志或补齐缺失字段。

| 统一字段 | 日志字段示例 | 导出时要确认 |
| --- | --- | --- |
| `question_id` | qid、逐题表题号 | 保持各方法使用同一套稳定 ID |
| `method` | 配置中的 method_id | 对应明确的版本与运行条件；各方法必须覆盖相同题集 |
| `score` | correct、exact_match 等最终判分 | 将 True/False 转为逐题 1/0，不使用汇总准确率重复填每题 |
| `wall_seconds` | 终态记录 elapsed_seconds | 单位为秒；确认终态、时限与重复记录 |
| `main_input_tokens` | usage.input_tokens 或顶层 input_tokens | 核对累计总量和缓存统计方式，避免重复加缓存项 |
| `reranker_input_tokens` | reranker_summary.input_tokens | 独立模型的输入量，不与主模型 token 合并成统一成本 |
| `rerank_seconds` | reranker_summary.scoring_seconds | preparation_seconds 单独记录；scoring_seconds 若已包含在 elapsed 内，不能再加到墙钟时间 |
| `rerank_events` | reranker_summary.scoring_calls，结合实际事件日志核对 | 自动调用、显式工具动作、forward_calls 是不同计数；不能机械互换 |
| `scored_passages` | reranker_summary.scored_passages | 累计评分片段数，不是去重后的唯一片段数 |

若某题有最终判分但资源记录缺失，应保留其质量记录，未知资源留空。森林图可以使用完整质量题集；成本图需显式选择 `--missing-cost complete-case`，并在共同完整题集上重新计算质量与成本。只有汇总 token 总账时，不能将其均摊成雨云图需要的逐题分布。

候选池 M、保留名次 K、最终 limit，以及“gold 路径出现”“含答案材料进入前 k”“最终答对”都应分清。当前模板只画你提供的明确指标，不从这些不同含义的字段自动推导另一种效果。

## 可移植的输入溯源

每张图的 `*_provenance.json` 保留输入 CSV 和配置文件的 SHA256、完整配置、随机种子及样本筛选信息。`input_csv` 优先保存相对于配置文件所在目录的路径，`input_csv_base=config_directory`；若输入只位于模板目录内，则相对于 `common.py` 所在目录，标记为 `template_directory`。输入在两者之外时只保存文件名，标记为 `filename_only`，由 `input_sha256` 精确识别内容。`config_file` 保存配置文件名，`config_sha256` 标识配置内容；这些字段不会写入本机绝对目录。
