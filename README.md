# Rerank Research Figure Gallery

面向 search、rerank 与自主工具调用实验的科研绘图参考库：**34 张图，每张均有代码、输入说明与来源**。包含 3 张可运行 Rerank 模板、15 张精选图、8 张补充图，以及 8 张 GitHub 上游原图。

**从这里开始：**[34 图与全部代码索引](docs/FIGURE_INDEX.md) · [15 图完整说明](docs/GALLERY.md) · [Rerank 模板使用指南](rerank_templates/2026-11-16/README.md)

26 个本地实现可生成独立运行包；8 个上游参考包保留对应代码、原始快照与许可，**未在本项目完整执行**。文献数值、合成演示和上游示例均注明类型，不包含我们的实测实验结果。

## 快速开始 / Quick start

在仓库根目录，使用 Python 3.10+：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python scripts/build_gallery.py --keep-existing-images
```

构建后打开 `dist/图表汇总_2026-11-16.html`：图片、逐图代码与下载包内嵌，可离线使用。完整发布包位于 `dist/research-figure-gallery.zip`。构建产物放在 `dist/`，不提交到 Git；这些文件需先构建生成。

**从 GitHub 下载：**进入仓库的 **Actions** 页面，选择一次成功的构建，在 **Artifacts** 中下载产物并解压。流程定义见[构建工作流](.github/workflows/build.yml)。完整构建独立执行 26 个本地代码包，8 个上游包检查完整性；报告位于 `dist/`。

## 选择与运行单图

在[34 图索引](docs/FIGURE_INDEX.md)中查看主脚本、公共函数及输入文件。三个新模板共享逐题 CSV 与配置；[数据格式](rerank_templates/2026-11-16/DATA_FORMAT.md)说明如何接入真实日志。单独复制主脚本时，需一并保留公共函数和数据。

```bash
python rerank_templates/2026-11-16/plot_pareto.py --output-dir dist/custom-pareto
```

上游示例的依赖、数据和运行路径见对应代码参考包，不能用原图代替重跑验证。

## 目录与来源

| 内容 | 入口 |
| --- | --- |
| 全部图、代码与输入 | [34 图索引](docs/FIGURE_INDEX.md) |
| 精选说明与补充理由 | [精选图文](docs/GALLERY.md) · [补充索引](SUPPLEMENT.md) |
| 论文数值与出处 | [Deep Research](paper_expansion/2026-11-01/RESEARCH_NOTES.md) · [Rerank](rerank_expansion/2026-11-15/RESEARCH_NOTES.md) |
| GitHub 原图、快照与许可 | [上游参考文档](github_references/2026-11-15/GitHub科研绘图参考.md) |
| 目录维护与去重记录 | [catalog.json](catalog.json) · [筛选说明](CURATION.md) · [去重记录](curation/2026-11-15-dedup/README.md) |

本库自编代码采用 [MIT 许可](LICENSE)。上游原图与源码各自保留原许可，详见[参考来源](REFERENCES.md)；根目录许可证不覆盖这些上游材料。
