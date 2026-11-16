# 文件夹与使用入口

从 [README 图型目录](../README.md#figure-catalog) 选择图型。页面展示 **11 张代表图、28 个用途**；同一图型的其他实现放在[代码、数据与来源索引](FIGURE_INDEX.md)，不重复展示预览图。

## 目录分工

| 位置 | 内容与使用方式 |
| --- | --- |
| [README.md](../README.md) | 每张代表图的读法、实验用途、论文位置、运行命令与使用边界。 |
| [docs/FIGURE_INDEX.md](FIGURE_INDEX.md) | 34 份实现或上游参考的统一索引，包含代码、输入、出处和许可。 |
| [docs/REFERENCES.md](REFERENCES.md)、[docs/CURATION.md](CURATION.md) | 参考资料及筛选、合并原则。 |
| [docs/catalog/](catalog/) | 图表清单：`figure_families.json` 定义 11 类图型及用途；`catalog.json` 与 `gallery.json` 保留底层实现的编号与路径。修改展示内容后运行 README 生成器。 |
| [examples/](../examples/)、[gallerylib/](../gallerylib/)、[data/](../data/) | 通用绘图脚本、公共函数和合成示例数据。 |
| [rerank_templates/2026-11-16/](../rerank_templates/2026-11-16/) | 共用逐题数据格式的森林图、雨云图和双目标散点图模板；输入要求见 [DATA_FORMAT.md](../rerank_templates/2026-11-16/DATA_FORMAT.md)。 |
| [paper_expansion/](../paper_expansion/)、[rerank_expansion/](../rerank_expansion/) | 公开材料的重绘脚本、转录数据、来源记录及图件。 |
| [github_references/](../github_references/) | 固定版本的上游图片、代码快照、数据格式与许可。 |
| [assets/](../assets/)、[docs/gallery_overview.png](gallery_overview.png) | 示例图片与 11 张代表图的总览。其他图件随各实现放在对应目录。 |
| [scripts/](../scripts/)、[tests/](../tests/)、[.github/workflows/](../.github/workflows/) | 文档生成、完整构建、独立代码包验收及 GitHub 自动检查。 |
| [curation/](../curation/) | 历史整理记录和图片保留凭据，用于检查图件是否被意外改动。 |
| `dist/` | 构建生成的离线 HTML、代码 ZIP、完整仓库 ZIP 和验收报告；不纳入 Git 跟踪。 |

底层目录沿用原始路径，便于复现和核对出处；README 与代码索引统一按图型组织，所有来源采用同一套说明方式。34 份底层实现中，26 份可在本地独立执行，8 份为上游参考；代表图中对应 9 份本地实现和 2 份上游参考。不要将“参考代码已收录”当作“完整上游环境已运行”。

## 运行与验收

在仓库根目录执行：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python scripts/build_gallery.py --keep-existing-images
```

构建会检查已保留图件、运行模板测试和仓库测试、在独立目录执行本地代码包，并生成：

- `dist/图表汇总_2026-11-16.html`：可离线打开的单文件图册，含每类代表图、用途、代码与下载入口。
- `dist/figure_code/all-figure-code.zip`：全部 34 份代码与参考资料包。
- `dist/research-figure-gallery.zip`：源码、数据、说明与构建结果的完整压缩包。
- `dist/verification.json` 与 `dist/figure_code_execution.json`：构建及独立代码包验收记录。

仅修改说明文字或图型用途时，可运行 `python scripts/render_readme.py` 更新 README 和索引；发布前仍应运行完整构建。`--keep-existing-images` 保留已审核图件，并核对其内容，避免字体环境差异改变原图。

历史整理记录中的根目录 `figure_families.json` 指整理当时的路径；该文件现在位于 [docs/catalog/figure_families.json](catalog/figure_families.json)。历史凭据保留原文，当前代码使用新路径。
