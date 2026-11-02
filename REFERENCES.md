# 图型参考与代码来源说明

本仓库保留的 10 个 `examples/*/plot.py`、公共函数、演示数据生成器和排版均为本次编写的实现，使用 Matplotlib/NumPy/Pillow；**没有把其他项目的截图当作本地代码的运行结果，也没有将未找到的论文出图脚本写成已复现**。各图底部明确标出合成演示数据。本轮删除情况见 [CURATION.md](CURATION.md)。

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
| [draw.io diagrams](https://github.com/jgraph/drawio-diagrams) | 方法流程图的可编辑图型拓展参考 | [时序图 XML](https://github.com/jgraph/drawio-diagrams/blob/dev/diagrams/sequence.xml)；本库框架图由本地渲染器导出 XML，未复制该示例 |
| [Matplotlib for Papers](https://github.com/jbmouret/matplotlib_for_papers) | 论文级最简排版参考 | [箱线图代码](https://github.com/jbmouret/matplotlib_for_papers/blob/master/src/boxplot5.py) |
| [Awesome Scientific Figures](https://github.com/Figwise/awesome-scientific-figures) | 拓展检索导航 | [资源索引](https://github.com/Figwise/awesome-scientific-figures/blob/main/README.md)；索引不等于每张图都有绘图代码 |

## 与实验问题有关的论文和项目

| 研究参考 | 本库借鉴的内容 | 原代码状态与本库关系 |
| --- | --- | --- |
| [RankRAG](https://arxiv.org/abs/2407.02485) | 检索、排序与生成的阶段关系 | 保留为研究背景链接；对应的旧版 06/18 模板已删除 |
| [Lost in the Middle](https://arxiv.org/abs/2307.03172) | 证据位置与长上下文表现的研究问题 | 保留为研究背景链接；旧版 11 模板已删除 |
| [SIEVE](https://arxiv.org/abs/2608.02751) / [SkimSearchAgent](https://github.com/ielab/skim-search-agent) | 将逐题 token 差异与结果变化对齐 | 此前定位的 [appendix_token_columns.py](https://github.com/ielab/skim-search-agent/blob/main/analysis/appendix_token_columns.py) 是统计入口，不能当作配对图的已确认出图脚本；09 为本库自行实现 |
| [DeepHone](https://github.com/sahel-sh/DeepHone) | 搜索过程与工具行为分析的拓展阅读 | 此前定位了 [plot_etc_deepsearch.py](https://github.com/sahel-sh/DeepHone/blob/main/scripts_rerank/plot_etc_deepsearch.py)；本库未复制或运行该脚本，不将其中原图收入可复现示例 |

框架图另核对了 [A-RAG v1](https://arxiv.org/abs/2602.03442v1)、[FS-Researcher v2](https://arxiv.org/abs/2602.01566v2) 和 [WebThinker v2](https://arxiv.org/abs/2504.21776v2) 的原论文图与方法章节。这里只借鉴模块关系，重新编写布局和绘图代码，不将本地图称为作者原图或原始出图脚本。来源版本、原图页码、所检查仓库提交及各图取舍见 [框架说明](frameworks/2026-11-02/NOTES.md) 和 [来源清单](frameworks/2026-11-02/sources.json)。

图型参考清单沿用 2026-11-01 的检索记录，框架来源核对于 2026-11-02；上游分支与路径可能变化。每张 README 示例的实际代码由 `gallery.json`、`paper_expansion/*/manifest.json`、`frameworks/*/manifest.json` 映射，统一展示顺序见 [catalog.json](catalog.json)。外部链接用于说明参考关系，不参与出图。
