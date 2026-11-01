# 演示数据与真实数据替换

这里的 9 张 CSV **全部是合成数据**，由 [`scripts/generate_demo_data.py`](../scripts/generate_demo_data.py) 生成，默认种子 `20261101`、100 个问题、4 种方法。数据用于展示图型和验证代码，不用于支持论文结论。`timeline.csv` 是手工定义的虚构案例；其他表由固定随机种子生成。

视觉筛选后，`actions.csv` 和 `context.csv` 的绘图模板已删除；这两张辅助表仍保留，用于检查显式调用数、动作轮数以及累计输入 token 是否一致。

四种方法的默认绘图顺序是 Baseline、Paging、Auto rerank、Agent rerank。替换或增加方法时修改 [`gallerylib/__init__.py`](../gallerylib/__init__.py) 的 `METHODS` 和配色。所有 CSV 是 UTF-8、有表头，整数 0/1 表示布尔值，空字符串表示缺失，不等于零。真实数据请放到新目录，并传入 `--data-dir`，避免覆盖演示数据。

| 文件 | 每行粒度 / 唯一键 | 字段和单位 |
| --- | --- | --- |
| `questions.csv` | 问题 × 方法，`question_id,method` | 问题级评测与资源总量，见下文 |
| `tool_calls.csv` | 问题 × 方法 × 工具 | `calls` 显式调用次数；`returned_chars` 返回给模型的字符总量 |
| `actions.csv` | 问题 × 方法 × 动作序号 | `turn` 整数动作序号；`tool` 为 search/bash/read/rerank |
| `context.csv` | 问题 × 方法 × 模型轮次 | `input_tokens` 本轮主模型输入长度，含复用上下文；本示例求和等于问题总输入 |
| `ranks.csv` | 重排候选快照，`snapshot_id` | `question_id,in_candidates,before_rank,after_rank`；排名 1 最好，全集上限 1000 |
| `query_pairs.csv` | 同题两种 query，`question_id` | `search_ndcg,rerank_ndcg`，范围 [0,1]；真实评测需另说明 nDCG@k 的 k 与标签 |
| `budget_runs.csv` | 问题 × 方法 × 预算 | `budget` 最大轮数；`correct` 对错；`cost_units` 合成成本单位，不是美元 |
| `ablations.csv` | 问题 × 消融版本 | `variant,correct`；Full system、Search query、Head snippet、BM25 order、Fixed scope、Fixed schedule |
| `timeline.csv` | 虚构案例 × 方法 × 事件 | `case_id,method,turn,tool,evidence`；tool 还可为 answer；evidence=1 表示观察到答案证据 |

## questions.csv 字段

| 字段 | 含义 |
| --- | --- |
| `question_id,method` | 同题配对的标识，不依赖行顺序 |
| `main_input_tokens` | 整段轨迹累计主模型输入 token 数 |
| `main_uncached_tokens,main_cached_tokens` | 非缓存、缓存输入；两者之和等于 `main_input_tokens` |
| `main_output_tokens` | 累计主模型输出 token 数 |
| `reranker_input_tokens` | 单独统计的 reranker 输入，不与主模型混用算力口径 |
| `rerank_events` | 后台实际重排事件数，含自动重排，并非显式工具调用数 |
| `scored_passages` | reranker 累计评分片段数 |
| `rerank_gpu_seconds` | 合成的后台评分 GPU 秒数，仅为扩展分析预留 |
| `turns` | 总模型轮数；示例设每轮恰有一次显式工具动作 |
| `wall_seconds` | 端到端观测耗时（秒），示例上限 3600 秒 |
| `correct` | 最终答案是否正确，0/1 |
| `outcome` | 互斥：Correct、Wrong answer、Abstain、No final |
| `stop_reason` | 互斥：Completed、Turn limit、Timeout；与答案分类独立 |
| `gold_in_pool` | 已标注证据是否进入候选集 |
| `gold_shown` | 该证据是否出现在返回给模型的内容中 |
| `gold_located` | 模型是否成功定位该证据；这三项需满足嵌套关系 |
| `first_visible_turn` | 证据首次被展示的轮次，未展示时为空；预留字段 |

## 统计口径

`ablations.csv` 的版本名是候选消融的标签：Search query 可表示复用原搜索 query；Head snippet 可表示用开头片段替代相关片段；BM25 order 可表示以 BM25 排序替代学习式 reranker；Fixed scope / Fixed schedule 可表示固定候选范围 / 固定调用时机。它们没有对应已执行的真实实验；实际使用时需写明每项改变的唯一变量、固定条件及运行配置。

- **统一返回长度**：合成示例中每次 search / 显式 rerank 都返回 100 字符。这不是 reranker 输入长度，也不能把 100 字符视为固定 token 数。真实工具可能返回不足上限，按实际长度累计。
- **调用比例**：使用所有调用池化后的比例。它不同于先算每题比例再对问题取平均；工具绝对次数另除以问题数。
- **隐式计算**：Auto rerank 没有显式 rerank 动作，但有后台重排事件和 token；比较成本时不能漏算。
- **配对**：08 的 query 图和 09/17 的方法差异必须按 `question_id` 对齐，重复或缺题会报错。bootstrap 按问题重采样，不能把一个题的多次重排当成独立问题。
- **区间**：比例图使用 95% Wilson 区间；配对差值使用固定种子的 3,000 次 bootstrap 百分位区间。它们描述问题抽样的不确定性，不覆盖模型随机种子、数据集偏差或多重比较。
- **排名迁移**：保留候选全集中的重排前后排名，包括跌出 Top-K 的证据；候选集外另计。替换候选集规模时同时调整脚本的校验范围与分箱。
- **轨迹**：辅助动作表记录单个有序动作序列。若真实日志允许并行调用，先定义事件顺序或改用并行动作统计，不直接套用序号。
- **上下文**：辅助上下文表模拟的是本轮输入长度，不是去重后的新增 token；用于检查其求和是否等于问题级输入总量。
- **预算**：14 使用预算配置下的单独评测记录，不能从完整轨迹截断就假设模型在较小预算下会给出相同答案。12 的成本单位没有实际价格含义。
- **失败**：未执行、缺失日志与零调用必须区分；本示例数据完整。耗时触顶的运行保留，并报告截断；多个种子、重复运行需扩展键并采用对应的统计方法。

所有脚本默认期待以上 schema。迁移到真实日志时先检查粒度、去重、缺失和时间截断，再调整图中标题、单位、脚注和显著性表述。
