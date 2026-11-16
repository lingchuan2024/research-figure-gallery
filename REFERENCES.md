# 图型参考与代码来源说明

本仓库保留的 9 个 `examples/*/plot.py`、公共函数、演示数据生成器和排版均为本库编写的实现，使用 Matplotlib/NumPy/Pillow；**没有把其他项目的截图当作本地代码的运行结果，也没有将未找到的论文出图脚本写成已复现**。这 9 个模板的图底明确标出合成演示数据。历史视觉筛选见 [CURATION.md](CURATION.md)，2026-11-15 去重见 [删除记录](curation/2026-11-15-dedup/README.md)。

下面列出此前检索中用到的图型、布局及研究问题参考。外部链接用于继续阅读，不是本库运行依赖。本库 MIT 许可仅覆盖本库自主编写的内容，不改变外部资源的许可。仓库本身使用某种许可证，也不保证它的每个第三方素材都适用同一许可。

| 来源 | 用途 | 原项目入口 / 示例 |
| --- | --- | --- |
| [SciencePlots](https://github.com/garrettj403/SciencePlots) | 统一论文图的字体、刻度、线宽等设计意识 | [样式示例](https://github.com/garrettj403/SciencePlots/blob/master/examples/plot-examples.py)；本库使用自定义 rcParams，不依赖 SciencePlots |
| [Python Graph Gallery](https://github.com/holtzy/The-Python-Graph-Gallery) | 百分比堆叠、哑铃图、散点与排版参考 | [堆叠条形示例](https://github.com/holtzy/The-Python-Graph-Gallery/blob/master/content/posts/13-percent-stacked-barplot/index.md)、[哑铃图示例](https://github.com/holtzy/The-Python-Graph-Gallery/blob/master/content/posts/web-dumbell-chart/index.md) |
| [RainCloudPlots](https://github.com/RainCloudPlots/RainCloudPlots) | 密度、四分位与逐题点组合 | [Python 教程](https://github.com/RainCloudPlots/RainCloudPlots/blob/master/tutorial_python/raincloud_tutorial_python.ipynb)；本库 02 用 Matplotlib 自行绘制半小提琴 |
| [PyComplexHeatmap](https://github.com/DingWB/PyComplexHeatmap) | 带注释热图、多矩阵对齐 | [组合热图](https://github.com/DingWB/PyComplexHeatmap/blob/main/notebooks/composite_heatmaps.ipynb)；本库保留的 07 用 imshow 自行绘制 |
| [patchworklib](https://github.com/ponnhide/patchworklib) | 多面板布局思路 | [API 与布局例子](https://github.com/ponnhide/patchworklib/blob/main/API.md)；本库使用 subplots/GridSpec |
| [Scientific Visualization Book](https://github.com/rougier/scientific-visualization-book) | 科研排版与信息层次 | [复杂布局示例](https://github.com/rougier/scientific-visualization-book/blob/master/code/layout/complex-layout.py) |
| [cmcrameri](https://github.com/callumrollo/cmcrameri) | 科学配色的进一步选择 | [项目说明](https://github.com/callumrollo/cmcrameri/blob/main/README.md)；本库不依赖此包 |
| [draw.io diagrams](https://github.com/jgraph/drawio-diagrams) | 方法流程图的可编辑图型拓展参考 | [时序图 XML](https://github.com/jgraph/drawio-diagrams/blob/dev/diagrams/sequence.xml)；当前精选库未保留方法流程图 |
| [Matplotlib for Papers](https://github.com/jbmouret/matplotlib_for_papers) | 论文级最简排版参考 | [箱线图代码](https://github.com/jbmouret/matplotlib_for_papers/blob/master/src/boxplot5.py) |
| [Awesome Scientific Figures](https://github.com/Figwise/awesome-scientific-figures) | 拓展检索导航 | [资源索引](https://github.com/Figwise/awesome-scientific-figures/blob/main/README.md)；索引不等于每张图都有绘图代码 |

## 与实验问题有关的论文和项目

| 研究参考 | 本库借鉴的内容 | 原代码状态与本库关系 |
| --- | --- | --- |
| [RankRAG](https://arxiv.org/abs/2407.02485) | 检索、排序与生成的阶段关系 | 保留为研究背景链接；对应的旧版 06/18 模板已删除 |
| [Lost in the Middle](https://arxiv.org/abs/2307.03172) | 证据位置与长上下文表现的研究问题 | 保留为研究背景链接；旧版 11 模板已删除 |
| [SIEVE](https://arxiv.org/abs/2608.02751) / [SkimSearchAgent](https://github.com/ielab/skim-search-agent) | 将逐题 token 差异与结果变化对齐 | 此前定位的 [appendix_token_columns.py](https://github.com/ielab/skim-search-agent/blob/main/analysis/appendix_token_columns.py) 是统计入口，不能当作配对图的已确认出图脚本；09 为本库自行实现 |
| [DeepHone](https://github.com/sahel-sh/DeepHone) | 搜索过程与工具行为分析的拓展阅读 | 此前定位了 [plot_etc_deepsearch.py](https://github.com/sahel-sh/DeepHone/blob/main/scripts_rerank/plot_etc_deepsearch.py)；本库未复制或运行该脚本，不将其中原图收入可复现示例 |

以上参考清单沿用 2026-11-01 的检索记录；上游分支与路径可能变化。每张 README 示例对应的**实际可运行本地代码**见 `gallery.json` 或文献 `manifest.json` 中的 `script` 路径，外部链接用于说明参考关系，不参与出图。

## Rerank 文献图更新

2026-11-15 的重排专题见 [论文与实验契合分析](rerank_expansion/2026-11-15/RESEARCH_NOTES.md)及 [数值来源审计](rerank_expansion/2026-11-15/data_provenance.json)。各图的本地脚本、CSV、PNG 和 SVG 由该目录的 `manifest.json` 对应。图中数值属于来源论文的实验；本库自行重绘，不将其标作我们的实验结果或作者原始出图代码。

## GitHub 原图独立参考

2026-11-15 另整理了 [GitHub 科研绘图参考](github_references/2026-11-15/GitHub科研绘图参考.md)（[离线图文版](dist/GitHub科研绘图参考.html)）：8 个仓库的 8 张原始示例图，各附对应源码、固定 commit、许可、适合 rerank 的用途和数据要求。原图未重绘，上游源码仅核对和留存，未运行；G08 的 PNG 预览由原 PDF 栅格化。来源与摘要见 [独立清单](github_references/2026-11-15/manifest.json)。这些原图和源码不适用本库自编代码的 MIT 授权，各自许可证随文件保留。

2026-11-16 将其中 G02、G04、G06 的图型做成了 [独立可运行的 Rerank 模板](rerank_templates/2026-11-16/README.md)，分别为多方法森林图、分面雨云图和 Pareto 图。新代码为本库使用 Matplotlib/NumPy 的独立实现，未复制上游源码；固定参考链接见 [sources.json](rerank_templates/2026-11-16/sources.json)。默认数据完全合成，实际逐题输入格式、成本缺失处理与真实日志字段映射均另附说明。
