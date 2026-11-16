# 34 图与全部代码索引

[返回仓库首页](../README.md) · [15 图完整说明](GALLERY.md) · [补充理由](../SUPPLEMENT.md)

本页覆盖 **34 张图：26 个本地可运行实现、8 个上游代码参考**。编号与离线 HTML 一致。点击图名查看规范预览；每行列出主代码及运行所需的公共函数、数据或环境说明。

完整构建会生成并独立执行 26 个本地代码包。8 个上游参考包保留提取代码、原始快照和许可证，未在本项目完整执行，不保证在当前依赖下复现原图。不要把上游图片当作本地重跑结果。

构建后打开 `dist/图表汇总_2026-11-16.html`，可离线阅读和下载逐图代码包；`dist/research-figure-gallery.zip` 是完整发布包。构建产物不会纳入 Git，需在本地生成或从 GitHub Actions 下载。运行状态与环境见 `dist/figure_code_execution.json`。

## 可运行的 Rerank 模板 · 3 张

| 编号 | 图表 / 数据类型 | 代码 | 输入与说明 | 状态 |
| --- | --- | --- | --- | --- |
| T01 | [子集收益森林图](../rerank_templates/2026-11-16/figures/forest.png)<br>合成模板 | [主代码](../rerank_templates/2026-11-16/plot_forest.py) · [公共函数](../rerank_templates/2026-11-16/common.py) | [逐题 CSV](../rerank_templates/2026-11-16/data/demo/observations.csv) · [配置](../rerank_templates/2026-11-16/config.json) | 本地可运行 |
| T02 | [分面耗时雨云图](../rerank_templates/2026-11-16/figures/raincloud.png)<br>合成模板 | [主代码](../rerank_templates/2026-11-16/plot_raincloud.py) · [公共函数](../rerank_templates/2026-11-16/common.py) | [逐题 CSV](../rerank_templates/2026-11-16/data/demo/observations.csv) · [配置](../rerank_templates/2026-11-16/config.json) | 本地可运行 |
| T03 | [质量—开销 Pareto 图](../rerank_templates/2026-11-16/figures/pareto.png)<br>合成模板 | [主代码](../rerank_templates/2026-11-16/plot_pareto.py) · [公共函数](../rerank_templates/2026-11-16/common.py) | [逐题 CSV](../rerank_templates/2026-11-16/data/demo/observations.csv) · [配置](../rerank_templates/2026-11-16/config.json) | 本地可运行 |

## 精选图库 · 15 张

| 编号 | 图表 / 数据类型 | 代码 | 输入与说明 | 状态 |
| --- | --- | --- | --- | --- |
| M01 | [推理时重排对最终回答的影响](../rerank_expansion/2026-11-15/figures/R01_rerank_qa.png)<br>论文数值重绘 | [主代码](../rerank_expansion/2026-11-15/code/R01_rerank_qa.py) · [公共函数](../rerank_expansion/2026-11-15/plotlib.py) | [rankrag_qa_ablation.csv](../rerank_expansion/2026-11-15/data/rankrag_qa_ablation.csv) | 本地可运行 |
| M02 | [前 5 条中的含答案材料召回](../rerank_expansion/2026-11-15/figures/R02_answer_recall.png)<br>论文数值重绘 | [主代码](../rerank_expansion/2026-11-15/code/R02_answer_recall.py) · [公共函数](../rerank_expansion/2026-11-15/plotlib.py) | [rankrag_answer_recall.csv](../rerank_expansion/2026-11-15/data/rankrag_answer_recall.csv) | 本地可运行 |
| M03 | [主结果表](../assets/19_results_table.png)<br>合成模板 | [主代码](../examples/19_results_table/plot.py) · [公共函数](../gallerylib/__init__.py) | [questions.csv](../data/demo/questions.csv) · [tool_calls.csv](../data/demo/tool_calls.csv) | 本地可运行 |
| M04 | [输入顺序鲁棒性](../rerank_expansion/2026-11-15/figures/R03_order_robustness.png)<br>论文数值重绘 | [主代码](../rerank_expansion/2026-11-15/code/R03_order_robustness.py) · [公共函数](../rerank_expansion/2026-11-15/plotlib.py) | [rankzephyr_order_robustness.csv](../rerank_expansion/2026-11-15/data/rankzephyr_order_robustness.csv) | 本地可运行 |
| M05 | [Query 配对比较](../assets/08_query_paired_comparison.png)<br>合成模板 | [主代码](../examples/08_query_paired_comparison/plot.py) · [公共函数](../gallerylib/__init__.py) | [query_pairs.csv](../data/demo/query_pairs.csv) | 本地可运行 |
| M06 | [证据排名迁移](../assets/07_rank_transition.png)<br>合成模板 | [主代码](../examples/07_rank_transition/plot.py) · [公共函数](../gallerylib/__init__.py) | [ranks.csv](../data/demo/ranks.csv) | 本地可运行 |
| M07 | [重排窗口重叠的成本与收益](../rerank_expansion/2026-11-15/figures/R05_window_budget.png)<br>论文数值重绘 | [主代码](../rerank_expansion/2026-11-15/code/R05_window_budget.py) · [公共函数](../rerank_expansion/2026-11-15/plotlib.py) | [first_window_budget.csv](../rerank_expansion/2026-11-15/data/first_window_budget.csv) | 本地可运行 |
| M08 | [模型规模与任务差异](../rerank_expansion/2026-11-15/figures/R06_model_scaling.png)<br>论文数值重绘 | [主代码](../rerank_expansion/2026-11-15/code/R06_model_scaling.py) · [公共函数](../rerank_expansion/2026-11-15/plotlib.py) | [qwen3_scaling.csv](../rerank_expansion/2026-11-15/data/qwen3_scaling.csv) | 本地可运行 |
| M09 | [组件消融森林图](../assets/17_ablation_forest.png)<br>合成模板 | [主代码](../examples/17_ablation_forest/plot.py) · [公共函数](../gallerylib/__init__.py) | [ablations.csv](../data/demo/ablations.csv) | 本地可运行 |
| M10 | [解码方式与重排时延](../rerank_expansion/2026-11-15/figures/R04_decoding_latency.png)<br>论文数值重绘 | [主代码](../rerank_expansion/2026-11-15/code/R04_decoding_latency.py) · [公共函数](../rerank_expansion/2026-11-15/plotlib.py) | [first_decoding_latency.csv](../rerank_expansion/2026-11-15/data/first_decoding_latency.csv) | 本地可运行 |
| M11 | [逐题 Token 用量分布](../assets/02_token_raincloud.png)<br>合成模板 | [主代码](../examples/02_token_raincloud/plot.py) · [公共函数](../gallerylib/__init__.py) | [questions.csv](../data/demo/questions.csv) | 本地可运行 |
| M12 | [工具调用与返回文本占比](../assets/04_call_vs_output_share.png)<br>合成模板 | [主代码](../examples/04_call_vs_output_share/plot.py) · [公共函数](../gallerylib/__init__.py) | [tool_calls.csv](../data/demo/tool_calls.csv) | 本地可运行 |
| M13 | [模块耗时分解](../paper_expansion/2026-11-01/figures/N06_latency_components.png)<br>论文数值重绘 | [主代码](../paper_expansion/2026-11-01/code/N06_latency_components.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py) | [fs_latency.csv](../paper_expansion/2026-11-01/data/fs_latency.csv) | 本地可运行 |
| M14 | [证据充分对照](../paper_expansion/2026-11-01/figures/N03_oracle_evidence.png)<br>论文数值重绘 | [主代码](../paper_expansion/2026-11-01/code/N03_oracle_evidence.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py) | [browse_oracle.csv](../paper_expansion/2026-11-01/data/browse_oracle.csv) | 本地可运行 |
| M15 | [分层失败归因](../paper_expansion/2026-11-01/figures/N02_failure_hierarchy.png)<br>论文数值重绘 | [主代码](../paper_expansion/2026-11-01/code/N02_failure_hierarchy.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py) | [arag_failures.csv](../paper_expansion/2026-11-01/data/arag_failures.csv) | 本地可运行 |

## 补充图库 · 8 张

| 编号 | 图表 / 数据类型 | 代码 | 输入与说明 | 状态 |
| --- | --- | --- | --- | --- |
| S01 | [逐题结果与 Token 联动](../assets/09_token_outcome_pairs.png)<br>合成模板 | [主代码](../examples/09_token_outcome_pairs/plot.py) · [公共函数](../gallerylib/__init__.py) | [questions.csv](../data/demo/questions.csv) | 本地可运行 |
| S02 | [预算—效果曲线](../assets/14_budget_accuracy.png)<br>合成模板 | [主代码](../examples/14_budget_accuracy/plot.py) · [公共函数](../gallerylib/__init__.py) | [budget_runs.csv](../data/demo/budget_runs.csv) | 本地可运行 |
| S03 | [工具轨迹时间线](../assets/16_trajectory_timeline.png)<br>合成模板 | [主代码](../examples/16_trajectory_timeline/plot.py) · [公共函数](../gallerylib/__init__.py) | [timeline.csv](../data/demo/timeline.csv) | 本地可运行 |
| S04 | [引用支持率与有效证据量](../paper_expansion/2026-11-01/figures/N04_citation_support.png)<br>论文数值重绘 | [主代码](../paper_expansion/2026-11-01/code/N04_citation_support.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py) | [deepbench_fact.csv](../paper_expansion/2026-11-01/data/deepbench_fact.csv) | 本地可运行 |
| S05 | [评估费用与人类一致性](../paper_expansion/2026-11-01/figures/N08_evaluator_budget.png)<br>论文数值重绘 | [主代码](../paper_expansion/2026-11-01/code/N08_evaluator_budget.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py) | [judge_batch.csv](../paper_expansion/2026-11-01/data/judge_batch.csv) | 本地可运行 |
| S06 | [检索暴露文本量](../paper_expansion/2026-11-01/figures/N01_retrieved_context.png)<br>论文数值重绘 | [主代码](../paper_expansion/2026-11-01/code/N01_retrieved_context.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py) | [arag_context.csv](../paper_expansion/2026-11-01/data/arag_context.csv) | 本地可运行 |
| S07 | [调用投入与独立来源增长](../paper_expansion/2026-11-01/figures/N07_source_growth.png)<br>论文数值重绘 | [主代码](../paper_expansion/2026-11-01/code/N07_source_growth.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py) | [fs_scaling.csv](../paper_expansion/2026-11-01/data/fs_scaling.csv) | 本地可运行 |
| S08 | [任务难度分层](../paper_expansion/2026-11-01/figures/N05_task_complexity.png)<br>论文数值重绘 | [主代码](../paper_expansion/2026-11-01/code/N05_task_complexity.py) · [公共函数](../paper_expansion/2026-11-01/plotlib.py) | [rubric_complexity.csv](../paper_expansion/2026-11-01/data/rubric_complexity.csv) | 本地可运行 |

## GitHub 原图参考 · 8 张

| 编号 | 图表 / 数据类型 | 代码 | 输入与说明 | 状态 |
| --- | --- | --- | --- | --- |
| G01 | [配对样本与均值差分布](../github_references/2026-11-15/sources/effectiveness/G01_paired_estimation.png)<br>上游原图 | [主代码](../github_references/2026-11-15/code_sections/G01.py) · [原始快照](../github_references/2026-11-15/sources/effectiveness/source_code/G01_source.py) · [许可](../github_references/2026-11-15/sources/effectiveness/G01_paired_estimation_LICENSE.txt) | [数据与环境](../github_references/2026-11-15/code_sections/effectiveness.json) | 上游参考 · 未完整执行 |
| G02 | [多方法分组森林图](../github_references/2026-11-15/sources/effectiveness/G02_multimodel_forest.png)<br>上游原图 | [主代码](../github_references/2026-11-15/code_sections/G02.py) · [原始快照](../github_references/2026-11-15/sources/effectiveness/source_code/G02_source_README.md) · [许可](../github_references/2026-11-15/sources/effectiveness/G02_multimodel_forest_LICENSE.txt) | [数据与环境](../github_references/2026-11-15/code_sections/effectiveness.json) · [sleep-mmodel.csv](../github_references/2026-11-15/code_sections/assets/sleep-mmodel.csv) | 上游参考 · 未完整执行 |
| G03 | [平均百分位秩与差异检验（模拟演示）](../github_references/2026-11-15/sources/effectiveness/G03_critical_difference.png)<br>上游原图 | [主代码](../github_references/2026-11-15/code_sections/G03.py) · [原始快照](../github_references/2026-11-15/sources/effectiveness/source_code/G03_source_tutorial.rst) · [许可](../github_references/2026-11-15/sources/effectiveness/G03_critical_difference_LICENSE.txt) | [数据与环境](../github_references/2026-11-15/code_sections/effectiveness.json) | 上游参考 · 未完整执行 |
| G04 | [分面雨云图：分布、散点与四分位](../github_references/2026-11-15/sources/effectiveness/G04_faceted_raincloud.png)<br>上游原图 | [主代码](../github_references/2026-11-15/code_sections/G04.py) · [原始快照](../github_references/2026-11-15/sources/effectiveness/source_code/G04_source.ipynb) · [许可](../github_references/2026-11-15/sources/effectiveness/G04_faceted_raincloud_LICENSE.txt) | [数据与环境](../github_references/2026-11-15/code_sections/effectiveness.json) · [simdat.csv](../github_references/2026-11-15/code_sections/assets/simdat.csv) | 上游参考 · 未完整执行 |
| G05 | [附注释的分组热图](../github_references/2026-11-15/sources/efficiency/annotated_heatmap.png)<br>上游原图 | [主代码](../github_references/2026-11-15/code_sections/G05.py) · [原始快照](../github_references/2026-11-15/sources/efficiency/clustermap.ipynb) · [许可](../github_references/2026-11-15/sources/efficiency/PyComplexHeatmap_LICENSE.txt) | [数据与环境](../github_references/2026-11-15/code_sections/efficiency.json) | 上游参考 · 未完整执行 |
| G06 | [非支配方案的 Pareto 散点图](../github_references/2026-11-15/sources/efficiency/pareto_optimization.png)<br>上游原图 | [主代码](../github_references/2026-11-15/code_sections/G06.py) · [原始快照](../github_references/2026-11-15/sources/efficiency/paretoset_examples.py) · [许可](../github_references/2026-11-15/sources/efficiency/paretoset_LICENSE.txt) | [数据与环境](../github_references/2026-11-15/code_sections/efficiency.json) | 上游参考 · 未完整执行 |
| G07 | [证据集合交集与分布联合图](../github_references/2026-11-15/sources/efficiency/complex_upset_movies.png)<br>上游原图 | [主代码](../github_references/2026-11-15/code_sections/G07.R) · [原始快照](../github_references/2026-11-15/sources/efficiency/complex_upset_README.md) · [许可](../github_references/2026-11-15/sources/efficiency/ComplexUpset_LICENSE.txt) | [数据与环境](../github_references/2026-11-15/code_sections/efficiency.json) | 上游参考 · 未完整执行 |
| G08 | [共享说明的矩阵式多面板布局](../github_references/2026-11-15/sources/efficiency/complex_layout_original_raster.png)<br>上游原图 | [主代码](../github_references/2026-11-15/code_sections/G08.py) · [原始快照](../github_references/2026-11-15/sources/efficiency/complex_layout.py) · [许可](../github_references/2026-11-15/sources/efficiency/Rougier_LICENSE.txt) | [数据与环境](../github_references/2026-11-15/code_sections/efficiency.json) | 上游参考 · 未完整执行 |

## 使用边界

- T01–T03 共享逐题 CSV 与 JSON 配置；见[字段契约](../rerank_templates/2026-11-16/DATA_FORMAT.md)。
- M/S 中的论文数值来自公开表格，不能据此补造逐题分布；合成数据仅展示画法。
- G03 原图显示模拟数据的平均百分位秩；G08 图像与代码许可不同，详见[上游参考文档](../github_references/2026-11-15/GitHub科研绘图参考.md)。
- 上游源码快照与许可证是来源材料，不能作为缓存删除。索引由 `catalog.json`、来源 manifest 和 `code_sections` 元数据生成。
