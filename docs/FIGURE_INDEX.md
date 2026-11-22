# 图型、代码与来源索引

[返回一图多用途图库](../README.md)

按 **10 种图型**统一整理。每类在首页只显示一张代表图，下面的实现用于不同实验目的；不再按网站、论文或模板来源分组。

同类代码的指标、字段和统计方法可能不同。选择与实验目的相符的实现，不要仅改标题就套用原数值。执行状态与许可证逐项注明；所有示例均不属于我们的实测结果。

<a id="f01"></a>

## F01 · 结果表

[代表图与多用途说明](../README.md#f01)

<a id="variant-m03"></a>

### F01.1 · 主结果表 · 当前代表图

[主代码](../examples/19_results_table/plot.py) · [公共函数](../gallerylib/__init__.py)

输入：[questions.csv](../data/demo/questions.csv) · [tool_calls.csv](../data/demo/tool_calls.csv)。

适用用途：各方法在同一题集上的最终回答质量、主模型用量、工具调用与耗时分别是多少？。

执行状态：本地可运行。表中均值、中位数和准确率区间的统计对象不同，单方法 Wilson 区间不能直接当作方法间配对差值的置信区间。

图型参考：[SciencePlots](https://github.com/garrettj403/SciencePlots)。

<a id="variant-t04"></a>

### F01.2 · 实测主结果表模板

[主代码](../rerank_templates/2026-11-21/plot_results_table.py) · [公共函数](../rerank_templates/2026-11-21/common.py)

输入：[示例 CSV](../rerank_templates/2026-11-21/data/demo/observations.csv) · [配置](../rerank_templates/2026-11-21/config.json)。

适用用途：各方法在同一题集上的最终回答质量、主模型用量、工具调用与耗时分别是多少？。

执行状态：本地可运行。单方法 Wilson／bootstrap 区间不是方法间配对差值区间；默认演示数据为合成示例。

本库独立实现的实测数据契约模板（2026-11-21）；默认数据为合成示例，附带 `config.measured.example.json`。

<a id="f02"></a>

## F02 · 配对比较

[代表图与多用途说明](../README.md#f02)

<a id="variant-m01"></a>

### F02.1 · 推理时重排对最终回答的影响

[主代码](../rerank_expansion/2026-11-15/code/R01_rerank_qa.py) · [公共函数](../rerank_expansion/2026-11-15/plotlib.py)

输入：[rankrag_qa_ablation.csv](../rerank_expansion/2026-11-15/data/rankrag_qa_ablation.csv)。

适用用途：重排开关是否改变最终答案质量，提供金标准证据后还剩多少回答失误？。

执行状态：本地可运行。原表不构成同 token 预算证明，论文 EM 也不能与其他图中的 F1、召回或不同 benchmark 分数混合排名。

来源：[RankRAG](https://arxiv.org/pdf/2407.02485v1#page=8)，2407.02485v1，Table 3。

<a id="variant-m02"></a>

### F02.2 · 前 5 条中的含答案材料召回

[主代码](../rerank_expansion/2026-11-15/code/R02_answer_recall.py) · [公共函数](../rerank_expansion/2026-11-15/plotlib.py)

输入：[rankrag_answer_recall.csv](../rerank_expansion/2026-11-15/data/rankrag_answer_recall.csv)。

适用用途：重排或 query 改写能否把相关、含答案材料提前，哪些题目获得收益或出现损失？。

执行状态：本地可运行。这里的 Answer Recall 是含答案材料命中率，不是全部 gold 文档的召回率，k=5 也不是重排候选数量。

来源：[RankRAG](https://arxiv.org/pdf/2407.02485v1#page=21)，2407.02485v1，Table 8。

<a id="variant-m04"></a>

### F02.3 · 输入顺序鲁棒性

[主代码](../rerank_expansion/2026-11-15/code/R03_order_robustness.py) · [公共函数](../rerank_expansion/2026-11-15/plotlib.py)

输入：[rankzephyr_order_robustness.csv](../rerank_expansion/2026-11-15/data/rankzephyr_order_robustness.csv)。

适用用途：保持候选内容不变时，随机打乱输入顺序会使重排质量变化多少？。

执行状态：本地可运行。现图区间来自 RankZephyr 原文六次打乱，不是逐题差值区间，也不能证明所有可能排列都稳定。

来源：[RankZephyr](https://arxiv.org/pdf/2312.02724v1#page=11)，2312.02724v1，Table 7。

<a id="variant-m05"></a>

### F02.4 · Query 配对比较 · 当前代表图

[主代码](../examples/08_query_paired_comparison/plot.py) · [公共函数](../gallerylib/__init__.py)

输入：[query_pairs.csv](../data/demo/query_pairs.csv)。

适用用途：重排或 query 改写能否把相关、含答案材料提前，哪些题目获得收益或出现损失？。

执行状态：本地可运行。当前标签与数值均为合成示例，若两种 query 同时改变检索候选，就不能把差值解释为 query 对重排本身的独立作用。

图型参考：[The-Python-Graph-Gallery](https://github.com/holtzy/The-Python-Graph-Gallery)。

<a id="variant-m10"></a>

### F02.5 · 解码方式与重排时延

[主代码](../rerank_expansion/2026-11-15/code/R04_decoding_latency.py) · [公共函数](../rerank_expansion/2026-11-15/plotlib.py)

输入：[first_decoding_latency.csv](../rerank_expansion/2026-11-15/data/first_decoding_latency.csv)。

适用用途：替换解码实现或检索接口后，重排时延与返回文本量各减少多少？。

执行状态：本地可运行。原数据为 RTX4090、top-100、窗口20／步长10下的重排耗时，不能当作 agent 端到端加速或自动推断质量不变。

来源：[Accelerating Listwise Reranking](https://zijianchen.ca/papers/Accelerating%20Listwise%20Reranking%20Reproducing%20and%20Enhancing%20FIRST.pdf#page=6)，SIGIR 2025 author PDF; SHA256 snapshot 2026-11-15，Table 5。

<a id="variant-m14"></a>

### F02.6 · 证据充分对照

[主代码](../paper_expansion/2026-11-01/code/N03_oracle_evidence.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py)

输入：[browse_oracle.csv](../paper_expansion/2026-11-01/data/browse_oracle.csv)。

适用用途：重排开关是否改变最终答案质量，提供金标准证据后还剩多少回答失误？。

执行状态：本地可运行。BrowseComp-Plus 的 oracle 改变证据访问条件且部分结果含上下文溢出失败，不能当作同返回预算下的公平 baseline 或可直接实现的重排收益。

来源：[BrowseComp-Plus](https://arxiv.org/pdf/2508.06600v1#page=10)，2508.06600v1，Table 1 and §4.8.1。

<a id="variant-s06"></a>

### F02.7 · 检索暴露文本量

[主代码](../paper_expansion/2026-11-01/code/N01_retrieved_context.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py)

输入：[arag_context.csv](../paper_expansion/2026-11-01/data/arag_context.csv)。

适用用途：替换解码实现或检索接口后，重排时延与返回文本量各减少多少？。

执行状态：本地可运行。A-RAG 原实验未控制为本项目的 100 字符返回预算，检索暴露 token 也不能直接替代模型计费 input tokens。

来源：[A-RAG](https://arxiv.org/pdf/2602.03442v1#page=8)，2602.03442v1，Table 3。

<a id="variant-g01"></a>

### F02.8 · 配对样本与均值差分布

[主代码](../github_references/2026-11-15/code_sections/G01.py) · [原始快照](../github_references/2026-11-15/sources/effectiveness/source_code/G01_source.py) · [许可全文](../github_references/2026-11-15/sources/effectiveness/G01_paired_estimation_LICENSE.txt)

输入：[数据与环境](../github_references/2026-11-15/code_sections/effectiveness.json)。

适用用途：重排或 query 改写能否把相关、含答案材料提前，哪些题目获得收益或出现损失？；替换解码实现或检索接口后，重排时延与返回文本量各减少多少？。

执行状态：上游参考 · 未完整执行。上游图使用模拟数据，不能把当前均值差当作实测收益，也不能把配对样本拆成独立两组来计算区间。

上游原图：[ACCLAB/DABEST-python](https://github.com/ACCLAB/DABEST-python/blob/ec6172724e0397bf0546863c76949d40da9c5457/nbs/tests/mpl_image_tests/baseline_images/test_04_gardner_altman_paired_meandiff.png)；许可：Apache-2.0 in LICENSE; README badge says BSD-3-Clause-Clear (conflicting repository notices).。仅作带来源的研究参考；若对外再分发或改编应先澄清仓库许可冲突。

<a id="variant-t05"></a>

### F02.9 · 实测逐题配对比较模板

[主代码](../rerank_templates/2026-11-21/plot_paired.py) · [公共函数](../rerank_templates/2026-11-21/common.py)

输入：[示例 CSV](../rerank_templates/2026-11-21/data/demo/observations.csv) · [配置](../rerank_templates/2026-11-21/config.json)。

适用用途：重排开关是否改变最终答案质量，提供金标准证据后还剩多少回答失误？；重排或 query 改写能否把相关、含答案材料提前，哪些题目获得收益或出现损失？。

执行状态：本地可运行。子集区间未做多重比较校正；连续分数题目过多时图面等距抽样展示，区间仍基于全部配对题目计算。

本库独立实现的实测数据契约模板（2026-11-21）；默认数据为合成示例，附带 `config.measured.example.json`。

<a id="variant-a01"></a>

### F02.10 · ITER 查询输入消融

[主代码](../rerank_expansion/2026-11-21/code/A01_iter_query_ablation.py) · [公共函数](../rerank_expansion/2026-11-21/plotlib.py)

输入：[iter_query_ablation.csv](../rerank_expansion/2026-11-21/data/iter_query_ablation.csv)。

适用用途：重排或 query 改写能否把相关、含答案材料提前，哪些题目获得收益或出现损失？。

执行状态：本地可运行。文献数据重绘，不是我们的实测结果；i3/i5 中的 docs 为 64-token 历史搜索摘要，不同于正文自主逐字选段。

来源：[ITER](https://arxiv.org/abs/2608.27912)，2608.27912v2，Table 3, p. 15。

<a id="variant-a02"></a>

### F02.11 · ITER 跨 Backbone 迁移与 V/S 转化

[主代码](../rerank_expansion/2026-11-21/code/A02_iter_cross_agent.py) · [公共函数](../rerank_expansion/2026-11-21/plotlib.py)

输入：[iter_cross_agent.csv](../rerank_expansion/2026-11-21/data/iter_cross_agent.csv)。

适用用途：重排开关是否改变最终答案质量，提供金标准证据后还剩多少回答失误？。

执行状态：本地可运行。文献数据重绘；显著性星号分别相对同尺度基线（0.6B 对 LRAT，4B 对 AgentIR）。

来源：[ITER](https://arxiv.org/abs/2608.27912)，2608.27912v2，Table 2, p. 14。

<a id="f03"></a>

## F03 · 差值森林图

[代表图与多用途说明](../README.md#f03)

<a id="variant-t01"></a>

### F03.1 · 子集收益森林图 · 当前代表图

[主代码](../rerank_templates/2026-11-16/plot_forest.py) · [公共函数](../rerank_templates/2026-11-16/common.py)

输入：[逐题 CSV](../rerank_templates/2026-11-16/data/demo/observations.csv) · [配置](../rerank_templates/2026-11-16/config.json)。

适用用途：相对不重排基线，多种策略在总体与各题型上的质量差值及不确定性如何？。

执行状态：本地可运行。当前为合成示例，All 与其子组重叠，区间未做多重比较校正，不能将这些行视为独立证据累加。

图型参考：[LSYS/forestplot](https://github.com/LSYS/forestplot/blob/b7591e3be7004f9962fd7cd7f91aa4cac91c45fc/docs/images/multimodel.png)；本库独立实现，默认数据为合成示例。

<a id="variant-m09"></a>

### F03.2 · 组件消融森林图

[主代码](../examples/17_ablation_forest/plot.py) · [公共函数](../gallerylib/__init__.py)

输入：[ablations.csv](../data/demo/ablations.csv)。

适用用途：去掉 query、snippet、候选范围或调用时机等组件后，最终质量损失有多大？。

执行状态：本地可运行。当前为合成示例，各组件的独立消融差值不能直接相加为总贡献，区间也未进行多重比较校正。

图型参考：[SciencePlots](https://github.com/garrettj403/SciencePlots)。

<a id="variant-g02"></a>

### F03.3 · 多方法分组森林图

[主代码](../github_references/2026-11-15/code_sections/G02.py) · [原始快照](../github_references/2026-11-15/sources/effectiveness/source_code/G02_source_README.md) · [许可全文](../github_references/2026-11-15/sources/effectiveness/G02_multimodel_forest_LICENSE.txt)

输入：[数据与环境](../github_references/2026-11-15/code_sections/effectiveness.json) · [sleep-mmodel.csv](../github_references/2026-11-15/code_sections/assets/sleep-mmodel.csv)。

适用用途：相对不重排基线，多种策略在总体与各题型上的质量差值及不确定性如何？。

执行状态：上游参考 · 未完整执行。原图展示回归系数而非 rerank 分差，不能只替换坐标标题就沿用系数或区间。

上游原图：[LSYS/forestplot](https://github.com/LSYS/forestplot/blob/b7591e3be7004f9962fd7cd7f91aa4cac91c45fc/docs/images/multimodel.png)；许可：MIT。仓库 LICENSE 为 MIT，保留版权与许可证；未发现该原图的独立许可声明。

<a id="f04"></a>

## F04 · 分布雨云图

[代表图与多用途说明](../README.md#f04)

<a id="variant-t02"></a>

### F04.1 · 分面耗时雨云图 · 当前代表图

[主代码](../rerank_templates/2026-11-16/plot_raincloud.py) · [公共函数](../rerank_templates/2026-11-16/common.py)

输入：[逐题 CSV](../rerank_templates/2026-11-16/data/demo/observations.csv) · [配置](../rerank_templates/2026-11-16/config.json)。

适用用途：平均耗时之外，哪些方法出现慢题、长尾或大量零重排开销？；主模型输入 token 的节省是否普遍，还是主要来自少数高开销题目？；不同 benchmark 或题型的成本分布是否不同，整体长尾由哪一组产生？。

执行状态：本地可运行。当前为合成示例，每条密度单独归一化高度，云形宽度不代表样本量，缺失成本也不能当成零。

图型参考：[RainCloudPlots/RainCloudPlots](https://github.com/RainCloudPlots/RainCloudPlots/blob/4ceeb06dc5bd5b9911e7147d1b0b452c4c2f9b1d/figs/tutorial_python/figureP13.png)；本库独立实现，默认数据为合成示例。

<a id="variant-m11"></a>

### F04.2 · 逐题 Token 用量分布

[主代码](../examples/02_token_raincloud/plot.py) · [公共函数](../gallerylib/__init__.py)

输入：[questions.csv](../data/demo/questions.csv)。

适用用途：主模型输入 token 的节省是否普遍，还是主要来自少数高开销题目？。

执行状态：本地可运行。当前合成脚本在 log10 前排除非正值并报告数量，真实的零开销应另示或使用 T02 的 log1p 方案，不能静默删除。

图型参考：[RainCloudPlots](https://github.com/RainCloudPlots/RainCloudPlots)。

<a id="variant-g04"></a>

### F04.3 · 分面雨云图：分布、散点与四分位

[主代码](../github_references/2026-11-15/code_sections/G04.py) · [原始快照](../github_references/2026-11-15/sources/effectiveness/source_code/G04_source.ipynb) · [许可全文](../github_references/2026-11-15/sources/effectiveness/G04_faceted_raincloud_LICENSE.txt)

输入：[数据与环境](../github_references/2026-11-15/code_sections/effectiveness.json) · [simdat.csv](../github_references/2026-11-15/code_sections/assets/simdat.csv)。

适用用途：不同 benchmark 或题型的成本分布是否不同，整体长尾由哪一组产生？。

执行状态：上游参考 · 未完整执行。上游图是教程数据，密度宽度不代表样本量，真实零值和超时记录不能因画法需要而随意删除。

上游原图：[RainCloudPlots/RainCloudPlots](https://github.com/RainCloudPlots/RainCloudPlots/blob/4ceeb06dc5bd5b9911e7147d1b0b452c4c2f9b1d/figs/tutorial_python/figureP13.png)；许可：MIT。仓库 LICENSE 为 MIT，保留版权与许可证；未发现该原图的独立许可声明。

<a id="f05"></a>

## F05 · 双目标权衡散点图

[代表图与多用途说明](../README.md#f05)

<a id="variant-t03"></a>

### F05.1 · 质量—开销 Pareto 图 · 当前代表图

[主代码](../rerank_templates/2026-11-16/plot_pareto.py) · [公共函数](../rerank_templates/2026-11-16/common.py)

输入：[逐题 CSV](../rerank_templates/2026-11-16/data/demo/observations.csv) · [配置](../rerank_templates/2026-11-16/config.json)。

适用用途：不同 reranker、触发策略或滑动窗口设置中，哪些配置在质量与实测资源之间更合适？。

执行状态：本地可运行。当前为合成示例，非支配只描述观测均值，横纵边际区间不是联合置信区域，也不能据此声称统计显著胜出。

图型参考：[tommyod/paretoset](https://github.com/tommyod/paretoset/blob/6f2803057085a696cbe10118ca3164d993cee175/scripts/example_optimization.png)；本库独立实现，默认数据为合成示例。

<a id="variant-m07"></a>

### F05.2 · 重排窗口重叠的成本与收益

[主代码](../rerank_expansion/2026-11-15/code/R05_window_budget.py) · [公共函数](../rerank_expansion/2026-11-15/plotlib.py)

输入：[first_window_budget.csv](../rerank_expansion/2026-11-15/data/first_window_budget.csv)。

适用用途：不同 reranker、触发策略或滑动窗口设置中，哪些配置在质量与实测资源之间更合适？。

执行状态：本地可运行。现图仅使用原论文同一张表的数据，caption 与正文的模型名称存在冲突，不能外推为任意 reranker 或其他硬件的速度规律。

来源：[Accelerating Listwise Reranking](https://zijianchen.ca/papers/Accelerating%20Listwise%20Reranking%20Reproducing%20and%20Enhancing%20FIRST.pdf#page=7)，SIGIR 2025 author PDF; SHA256 snapshot 2026-11-15，Table 6。

<a id="variant-s04"></a>

### F05.3 · 引用支持率与有效证据量

[主代码](../paper_expansion/2026-11-01/code/N04_citation_support.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py)

输入：[deepbench_fact.csv](../paper_expansion/2026-11-01/data/deepbench_fact.csv)。

适用用途：增加有效证据覆盖时，引用是否仍能准确支撑回答中的声明？。

执行状态：本地可运行。现图是 DeepResearch Bench 的固定版本 FACT 结果，有效引用不是原始 URL 数，引用支持率也不是检索相关性或其他 benchmark 的答案准确率。

来源：[DeepResearch Bench](https://arxiv.org/pdf/2506.11763v1#page=6)，2506.11763v1，Table 1; Figure 1 (right)。

<a id="variant-s05"></a>

### F05.4 · 评估费用与人类一致性

[主代码](../paper_expansion/2026-11-01/code/N08_evaluator_budget.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py)

输入：[judge_batch.csv](../paper_expansion/2026-11-01/data/judge_batch.csv)。

适用用途：LLM judge 的批量设置如何影响评估费用和与人工标注的一致性？。

执行状态：本地可运行。原文校准仅涉及 10 份报告，这里的费用属于评估器而非 agent 推理成本，F1 也不是被评方法的任务得分。

来源：[DeepResearch Bench II](https://arxiv.org/pdf/2601.08536v3#page=8)，2601.08536v3，Table 4。

<a id="variant-g06"></a>

### F05.5 · 非支配方案的 Pareto 散点图

[主代码](../github_references/2026-11-15/code_sections/G06.py) · [原始快照](../github_references/2026-11-15/sources/efficiency/paretoset_examples.py) · [许可全文](../github_references/2026-11-15/sources/efficiency/paretoset_LICENSE.txt)

输入：[数据与环境](../github_references/2026-11-15/code_sections/efficiency.json)。

适用用途：不同 reranker、触发策略或滑动窗口设置中，哪些配置在质量与实测资源之间更合适？。

执行状态：上游参考 · 未完整执行。上游图由固定种子的随机目标向量生成，非支配不等于统计显著更好，不能照搬其坐标作为模型性能。

上游原图：[tommyod/paretoset](https://github.com/tommyod/paretoset/blob/6f2803057085a696cbe10118ca3164d993cee175/scripts/example_optimization.png)；许可：MIT。原图与代码按上游许可保留；原始许可证随文件保存。

<a id="variant-a03"></a>

### F05.6 · RARG 粗到细相关性引导前沿

[主代码](../rerank_expansion/2026-11-21/code/A03_rarg_coarse_to_fine.py) · [公共函数](../rerank_expansion/2026-11-21/plotlib.py)

输入：[rarg_main_bcplus.csv](../rerank_expansion/2026-11-21/data/rarg_main_bcplus.csv)。

适用用途：不同 reranker、触发策略或滑动窗口设置中，哪些配置在质量与实测资源之间更合适？。

执行状态：本地可运行。文献数据重绘；工具调用数反映接口动作而非等价墙钟耗时或计费，RISE/DCI 行为原表转引自 RISE。

来源：[RARG](https://arxiv.org/abs/2607.24223)，2607.24223v2，Table 1, p. 7。

<a id="variant-a05"></a>

### F05.7 · IndexAct 上下文权衡与观察策略消融

[主代码](../rerank_expansion/2026-11-21/code/A05_indexact_context_tradeoff.py) · [公共函数](../rerank_expansion/2026-11-21/plotlib.py)

输入：[indexact_bcplus_main.csv](../rerank_expansion/2026-11-21/data/indexact_bcplus_main.csv) · [indexact_observation_ablation.csv](../rerank_expansion/2026-11-21/data/indexact_observation_ablation.csv)。

适用用途：不同 reranker、触发策略或滑动窗口设置中，哪些配置在质量与实测资源之间更合适？。

执行状态：本地可运行。文献数据重绘；左右面板题集分母不同（830 vs. 100），SrcTok 与 AvgCtx 统计口径不同。

来源：[IndexAct](https://arxiv.org/abs/2610.07960)，2610.07960v1，Tables 1-2, pp. 7-8。

<a id="f06"></a>

## F06 · 趋势与敏感性曲线

[代表图与多用途说明](../README.md#f06)

<a id="variant-m08"></a>

### F06.1 · 模型规模与任务差异

[主代码](../rerank_expansion/2026-11-15/code/R06_model_scaling.py) · [公共函数](../rerank_expansion/2026-11-15/plotlib.py)

输入：[qwen3_scaling.csv](../rerank_expansion/2026-11-15/data/qwen3_scaling.csv)。

适用用途：增大重排模型容量是否在不同任务上都带来收益？。

执行状态：本地可运行。Qwen3 论文各列不是统一量纲，不能直接平均或混合排名，参数量也不能代替实测成本。

来源：[Qwen3 Embedding](https://arxiv.org/pdf/2506.05176v3#page=8)，2506.05176v3，Table 4。

<a id="variant-s02"></a>

### F06.2 · 预算—效果曲线 · 当前代表图

[主代码](../examples/14_budget_accuracy/plot.py) · [公共函数](../gallerylib/__init__.py)

输入：[budget_runs.csv](../data/demo/budget_runs.csv)。

适用用途：增加最大轮次或运行预算时，各方法的回答质量如何变化，收益是否趋于饱和？。

执行状态：本地可运行。当前为合成预算实验，不能把一次长轨迹事后截断当作独立低预算运行，轮次上限也不等于已支付成本。

图型参考：[SciencePlots](https://github.com/garrettj403/SciencePlots)。

<a id="variant-s07"></a>

### F06.3 · 调用投入与独立来源增长

[主代码](../paper_expansion/2026-11-01/code/N07_source_growth.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py)

输入：[fs_scaling.csv](../paper_expansion/2026-11-01/data/fs_scaling.csv)。

适用用途：增加搜索轮数还能带来多少独立来源，还是主要增加重复调用？。

执行状态：本地可运行。现图来自 FS-Researcher，右侧是均值之差的比值而非逐题新颖度，来源数增长也不等于相关证据或答案质量提高。

来源：[FS-Researcher](https://arxiv.org/pdf/2602.01566v2#page=17)，2602.01566v2，Tables 8 and 10。

<a id="variant-s08"></a>

### F06.4 · 任务难度分层

[主代码](../paper_expansion/2026-11-01/code/N05_task_complexity.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py)

输入：[rubric_complexity.csv](../paper_expansion/2026-11-01/data/rubric_complexity.csv)。

适用用途：方法在概念广度、推理嵌套或探索难度不同的任务组上，表现是否一致？。

执行状态：本地可运行。ResearchRubrics 的长报告指标不能直接当作 rerank 准确率，也不能与其他论文 benchmark 混排或据组间折线声称因果。

来源：[ResearchRubrics](https://arxiv.org/pdf/2511.07685v1#page=9)，2511.07685v1，Figure 6 printed numeric labels。

<a id="variant-t06"></a>

### F06.5 · 实测预算趋势曲线模板

[主代码](../rerank_templates/2026-11-21/plot_budget_curve.py) · [公共函数](../rerank_templates/2026-11-21/common.py)

输入：[示例 CSV](../rerank_templates/2026-11-21/data/demo/budget_runs.csv) · [配置](../rerank_templates/2026-11-21/config.json)。

适用用途：增加最大轮次或运行预算时，各方法的回答质量如何变化，收益是否趋于饱和？。

执行状态：本地可运行。逐点置信带不构成同时置信带；默认演示数据为合成示例。

本库独立实现的实测数据契约模板（2026-11-21）；默认数据为合成示例，附带 `config.measured.example.json`。

<a id="variant-a06"></a>

### F06.6 · RISE 10 倍扩容与 Top-K 消融

[主代码](../rerank_expansion/2026-11-21/code/A06_rise_scaling_and_topk.py) · [公共函数](../rerank_expansion/2026-11-21/plotlib.py)

输入：[rise_scaling_100k_1m.csv](../rerank_expansion/2026-11-21/data/rise_scaling_100k_1m.csv) · [rise_topk_ablation.csv](../rerank_expansion/2026-11-21/data/rise_topk_ablation.csv)。

适用用途：增大重排模型容量是否在不同任务上都带来收益？。

执行状态：本地可运行。文献数据重绘；1M 下 RISE 行均为无 TOC 预处理的 RISE-BM25，DCI 仅在 nano 跑了 1M 且有 33/100 超时。

来源：[RISE](https://arxiv.org/abs/2606.06880)，2606.06880v1，Tables 2-3, pp. 7-8。

<a id="f07"></a>

## F07 · 矩阵热图

[代表图与多用途说明](../README.md#f07)

<a id="variant-m06"></a>

### F07.1 · 证据排名迁移 · 当前代表图

[主代码](../examples/07_rank_transition/plot.py) · [公共函数](../gallerylib/__init__.py)

输入：[ranks.csv](../data/demo/ranks.csv)。

适用用途：证据从哪些原始名次区间被提前或压后，进入 top-k 的材料来自哪里？。

执行状态：本地可运行。当前为合成示例，颜色不是全体证据占比，不能只留下进入 top-k 的证据或把候选池外证据伪造为末位。

图型参考：[PyComplexHeatmap](https://github.com/DingWB/PyComplexHeatmap)。

<a id="variant-g05"></a>

### F07.2 · 附注释的分组热图

[主代码](../github_references/2026-11-15/code_sections/G05.py) · [原始快照](../github_references/2026-11-15/sources/efficiency/clustermap.ipynb) · [许可全文](../github_references/2026-11-15/sources/efficiency/PyComplexHeatmap_LICENSE.txt)

输入：[数据与环境](../github_references/2026-11-15/code_sections/efficiency.json)。

适用用途：候选评分或错误模式是否随题型、方法和文档属性形成可解释的局部结构？。

执行状态：上游参考 · 未完整执行。原图为随机生物信息示例，聚类和多种颜色仅为展示功能，不能为美观重排有序排名或把随机筛选标签当作发现。

上游原图：[DingWB/PyComplexHeatmap](https://github.com/DingWB/PyComplexHeatmap/blob/2db32554c62c99b7e1823f5b2059a8b341ad0a9b/docs/build/html/_images/notebooks_clustermap_7_0.png)；许可：MIT。原图与代码按上游许可保留；原始许可证随文件保存。

<a id="variant-g08"></a>

### F07.3 · 共享说明的矩阵式多面板布局

[主代码](../github_references/2026-11-15/code_sections/G08.py) · [原始快照](../github_references/2026-11-15/sources/efficiency/complex_layout.py) · [许可全文](../github_references/2026-11-15/sources/efficiency/Rougier_LICENSE.txt)

输入：[数据与环境](../github_references/2026-11-15/code_sections/efficiency.json)。

适用用途：多模型、多任务的若干固定指标能否在统一小面板布局中同时比较？。

执行状态：上游参考 · 未完整执行。随机示例不是实测结果，原图采用 CC BY-NC-SA 4.0、代码采用 BSD-2-Clause，不能把代码许可套用于原图。

上游原图：[rougier/scientific-visualization-book](https://github.com/rougier/scientific-visualization-book/blob/62fa569f30333c817c13e4dc757877c1192fd15a/figures/layout/complex-layout.pdf)；许可：Book/figure: CC BY-NC-SA 4.0; code: BSD-2-Clause。原图与代码按上游许可保留；原始许可证随文件保存。

<a id="variant-t07"></a>

### F07.4 · 实测排名迁移热图模板

[主代码](../rerank_templates/2026-11-21/plot_rank_transition.py) · [公共函数](../rerank_templates/2026-11-21/common.py)

输入：[示例 CSV](../rerank_templates/2026-11-21/data/demo/rank_transitions.csv) · [配置](../rerank_templates/2026-11-21/config.json)。

适用用途：证据从哪些原始名次区间被提前或压后，进入 top-k 的材料来自哪里？。

执行状态：本地可运行。颜色代表行内占比而非全体证据占比；不能将候选池外文档伪造为末位排名。

本库独立实现的实测数据契约模板（2026-11-21）；默认数据为合成示例，附带 `config.measured.example.json`。

<a id="variant-a04"></a>

### F07.5 · RARG 检索域排名命中热图

[主代码](../rerank_expansion/2026-11-21/code/A04_rarg_scope_heatmap.py) · [公共函数](../rerank_expansion/2026-11-21/plotlib.py)

输入：[rarg_scope_rank_heatmap.csv](../rerank_expansion/2026-11-21/data/rarg_scope_rank_heatmap.csv)。

适用用途：证据从哪些原始名次区间被提前或压后，进入 top-k 的材料来自哪里？。

执行状态：本地可运行。文献数据重绘；非 scope 方法按 RARG scope_1.txt 排名分桶，零值以浅灰标示。

来源：[RARG](https://arxiv.org/abs/2607.24223)，2607.24223v2，Figure 3, p. 9。

<a id="f08"></a>

## F08 · 条形与组成分析

[代表图与多用途说明](../README.md#f08)

<a id="variant-m12"></a>

### F08.1 · 工具调用与返回文本占比 · 当前代表图

[主代码](../examples/04_call_vs_output_share/plot.py) · [公共函数](../gallerylib/__init__.py)

输入：[tool_calls.csv](../data/demo/tool_calls.csv)。

适用用途：重排策略是否改变工具调用结构，调用频繁的工具是否也返回了最多文本？。

执行状态：本地可运行。当前为合成示例，两图分母不同且比例隐藏总量，返回字符不能当作计费输入 token 或总推理成本。

图型参考：[The-Python-Graph-Gallery](https://github.com/holtzy/The-Python-Graph-Gallery)。

<a id="variant-m13"></a>

### F08.2 · 模块耗时分解

[主代码](../paper_expansion/2026-11-01/code/N06_latency_components.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py)

输入：[fs_latency.csv](../paper_expansion/2026-11-01/data/fs_latency.csv)。

适用用途：总耗时主要来自检索、重排、生成还是 I/O，哪个阶段值得优化？。

执行状态：本地可运行。现图是 FS-Researcher 的模块统计且没有独立 reranker 项，不能从中推算本方法重排耗时或把并发模块时长直接相加。

来源：[FS-Researcher](https://arxiv.org/pdf/2602.01566v2#page=22)，2602.01566v2，Table 15。

<a id="variant-m15"></a>

### F08.3 · 分层失败归因

[主代码](../paper_expansion/2026-11-01/code/N02_failure_hierarchy.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py)

输入：[arag_failures.csv](../paper_expansion/2026-11-01/data/arag_failures.csv)。

适用用途：失败主要来自证据获取、证据利用、放弃作答还是评价问题，某类失败内部又如何构成？。

执行状态：本地可运行。现图重绘 A-RAG 的错误分类，左右面板分母不同不能相加，分类名称和比例也不能直接当作我们的失败分布。

来源：[A-RAG](https://arxiv.org/pdf/2602.03442v1#page=15)，2602.03442v1，Tables 7–8; Figure 5。

<a id="variant-s01"></a>

### F08.4 · 逐题结果与 Token 联动

[主代码](../examples/09_token_outcome_pairs/plot.py) · [公共函数](../gallerylib/__init__.py)

输入：[questions.csv](../data/demo/questions.csv)。

适用用途：哪些题目节省或增加了主模型 token，这些题目同时出现了哪些正确性翻转？。

执行状态：本地可运行。当前为合成示例，同题上的 token 与结果变化不等于因果关系，正确性不变也不表示答案内容完全相同。

图型参考：[2608.02751](https://arxiv.org/abs/2608.02751)。

<a id="variant-t08"></a>

### F08.5 · 实测工具与文本组成模板

[主代码](../rerank_templates/2026-11-21/plot_tool_composition.py) · [公共函数](../rerank_templates/2026-11-21/common.py)

输入：[示例 CSV](../rerank_templates/2026-11-21/data/demo/tool_calls.csv) · [配置](../rerank_templates/2026-11-21/config.json)。

适用用途：重排策略是否改变工具调用结构，调用频繁的工具是否也返回了最多文本？。

执行状态：本地可运行。返回字符数不等于模型计费 input tokens；池化占比先求和再相除。

本库独立实现的实测数据契约模板（2026-11-21）；默认数据为合成示例，附带 `config.measured.example.json`。

<a id="f09"></a>

## F09 · 工具轨迹图

[代表图与多用途说明](../README.md#f09)

<a id="variant-s03"></a>

### F09.1 · 工具轨迹时间线 · 当前代表图

[主代码](../examples/16_trajectory_timeline/plot.py) · [公共函数](../gallerylib/__init__.py)

输入：[timeline.csv](../data/demo/timeline.csv)。

适用用途：某次重排触发后，后续搜索、读取、首次看到答案证据与最终作答的路径如何改变？。

执行状态：本地可运行。现图是虚构案例，星形只表示看到含答案证据而非已正确利用，不能用来证明典型轨迹、总体收益或墙钟加速。

图型参考：[The-Python-Graph-Gallery](https://github.com/holtzy/The-Python-Graph-Gallery)。

<a id="variant-t09"></a>

### F09.2 · 实测工具轨迹时间线模板

[主代码](../rerank_templates/2026-11-21/plot_trajectory.py) · [公共函数](../rerank_templates/2026-11-21/common.py)

输入：[示例 CSV](../rerank_templates/2026-11-21/data/demo/trajectories.csv) · [配置](../rerank_templates/2026-11-21/config.json)。

适用用途：某次重排触发后，后续搜索、读取、首次看到答案证据与最终作答的路径如何改变？。

执行状态：本地可运行。单题轨迹仅用于机制诊断，不能替代全量题集统计结论。

本库独立实现的实测数据契约模板（2026-11-21）；默认数据为合成示例，附带 `config.measured.example.json`。

<a id="f10"></a>

## F10 · 多方法秩比较

[代表图与多用途说明](../README.md#f10)

<a id="variant-g03"></a>

### F10.1 · 平均百分位秩与差异检验（模拟演示） · 当前代表图

[主代码](../github_references/2026-11-15/code_sections/G03.py) · [原始快照](../github_references/2026-11-15/sources/effectiveness/source_code/G03_source_tutorial.rst) · [许可全文](../github_references/2026-11-15/sources/effectiveness/G03_critical_difference_LICENSE.txt)

输入：[数据与环境](../github_references/2026-11-15/code_sections/effectiveness.json)。

适用用途：在多个独立评价分块上，哪些方法通常排在前面，哪些方法间未检出差异？。

执行状态：上游参考 · 未完整执行。不能将本图误读为名次 1 最好的平均排名，未检出差异不证明等效，也不能默认连接线具有 95% 区间或已做多重校正的含义。

上游原图：[maximtrp/scikit-posthocs](https://github.com/maximtrp/scikit-posthocs/blob/07e4c182b83314785eb879c3046de8ac5cf4febc/docs/source/_static/cd_diagram1.png)；许可：MIT。仓库 LICENSE 为 MIT，保留版权与许可证；未发现该原图的独立许可声明。

## 复现与许可

完整构建保留每种用途所需的代码、数据和来源证据。运行报告在 `dist/figure_code_execution.json`，汇总文件为 `dist/图表汇总_2026-11-16.html`；其中可直接下载对应运行包。

本地实现的主脚本、公共函数和输入数据必须一起使用。未完整执行的参考源码需按其环境说明安装依赖。根目录 MIT 许可仅覆盖本库自主实现，原始素材按各自的许可使用。
