# 补充索引与筛选理由

[返回仓库首页](README.md) · [全部 34 图与代码](docs/FIGURE_INDEX.md) · [精选图文](docs/GALLERY.md)

主图库按实验契合度、可读性和信息互补性，从 23 张中精选 15 张。以下 8 张适合后续专项实验或附录，当前不重复展示大图。全部图片、代码及数据保留，随时可复用。

| 图表 | 暂不进入主图库的原因 | 文件 |
| --- | --- | --- |
| 逐题结果与 Token 联动 | 上下两层对齐后的阅读负担较大，缩小后细柱难辨；逐题资源联动适合作为附录分析。 | [图片](assets/09_token_outcome_pairs.png) · [代码](examples/09_token_outcome_pairs/plot.py) · [数据](data/demo/questions.csv) |
| 预算—效果曲线 | 需要额外独立预算评测；当前主线优先验证固定返回预算下的 rerank 与 query。 | [图片](assets/14_budget_accuracy.png) · [代码](examples/14_budget_accuracy/plot.py) · [数据](data/demo/budget_runs.csv) |
| 工具轨迹时间线 | 虚构案例且留白较多；真实代表性轨迹整理完成后再重新设计。 | [图片](assets/16_trajectory_timeline.png) · [代码](examples/16_trajectory_timeline/plot.py) · [数据](data/demo/timeline.csv) |
| 引用支持率与有效证据量 | 偏长报告声明–URL核验，当前短答案任务未定义引用要求，需先建立答案–证据标注。 | [图片](paper_expansion/2026-11-01/figures/N04_citation_support.png) · [代码](paper_expansion/2026-11-01/code/N04_citation_support.py) · [数据](paper_expansion/2026-11-01/data/deepbench_fact.csv) |
| 评估费用与人类一致性 | 关注评估器配置及费用，离 reranker 效果主线较远，适合评估方法附录。 | [图片](paper_expansion/2026-11-01/figures/N08_evaluator_budget.png) · [代码](paper_expansion/2026-11-01/code/N08_evaluator_budget.py) · [数据](paper_expansion/2026-11-01/data/judge_batch.csv) |
| 检索暴露文本量 | 侧重检索接口暴露文本，和重排模型本身的效果关系较间接；转入检索工作空间专项。 | [图片](paper_expansion/2026-11-01/figures/N01_retrieved_context.png) · [代码](paper_expansion/2026-11-01/code/N01_retrieved_context.py) · [数据](paper_expansion/2026-11-01/data/arag_context.csv) |
| 调用投入与独立来源增长 | 侧重长报告的独立来源增长；本轮优先固定候选集合的重排与计算预算。 | [图片](paper_expansion/2026-11-01/figures/N07_source_growth.png) · [代码](paper_expansion/2026-11-01/code/N07_source_growth.py) · [数据](paper_expansion/2026-11-01/data/fs_scaling.csv) |
| 任务难度分层 | 原指标为长报告rubric遵循率，距离当前rerank实验较远；保留为后续任务分层参考。 | [图片](paper_expansion/2026-11-01/figures/N05_task_complexity.png) · [代码](paper_expansion/2026-11-01/code/N05_task_complexity.py) · [数据](paper_expansion/2026-11-01/data/rubric_complexity.csv) |

筛选针对图的表达与当前实验用途，没有按结果方向筛样本或改变数值。主图库的 15 张按统一用途组织，数据来源类型在每图旁注明；不同论文分数不能合并排名。
