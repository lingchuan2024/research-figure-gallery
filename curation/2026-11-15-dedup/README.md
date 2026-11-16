# 2026-11-15 去重记录

按用户“删除重复图”的要求，对当时 24 张图逐一检查文件摘要、解码后的 RGB 像素和科学问题。**没有字节完全相同或像素完全相同的图。** 本次删除 1 张内容冗余的合成模板，并清理 5 份逐字节相同的 CSV 临时副本；保留 23 张图，其中主图库 15 张、补充 8 张。

## 删除的图

删除 `12_accuracy_cost_frontier` 的 PNG、SVG 和绘图脚本，保留 `14_budget_accuracy`。两图使用同一 `budget_runs.csv`、同一 4 种方法和 5 档预算的正确率及 Wilson 区间；12 的成本并非独立测量，只是轮数乘固定倍数（Auto rerank 为 1.25，其余为 1）。因此保留能直接说明轮数预算的 14，避免把同一组结果重复包装为独立成本分析。

共同的数据 `budget_runs.csv` 保留。`assets/overview.png` 和 `docs/gallery_overview.png` 按现行目录重新生成，删除项不再出现。

## 合并的数据副本

以下文件统一保留在 `rerank_expansion/2026-11-15/data/`，删除 `research_effectiveness/` 或 `research_efficiency/` 中的同名副本。后续仓库整理已将调研片段合并至该日期的主 RESEARCH_NOTES.md 与 data_provenance.json；原 PDF 与表格截图集中存入 sources/ 和 source_pages/。

- `rankrag_qa_ablation.csv`
- `rankrag_answer_recall.csv`
- `rankzephyr_order_robustness.csv`
- `first_decoding_latency.csv`
- `first_window_budget.csv`

## 保留的相似图型

相同图型不等于相同研究问题：最终回答 EM、Answer Recall、输入顺序鲁棒性和解码时延虽然都适合配对点图，但指标、干预和实验范围不同，全部保留。排名迁移与前五召回、组件消融与重排开关、模块耗时与解码时延也未合并删除。新增的 6 张 rerank 文献重绘均保持不变。

删除前 SHA256、替代文件、重建总览前后 SHA256 和所有保留图的摘要见 [机器可核验记录](deletions.json)。历史 preservation baseline 未重写；测试仅允许本记录列出的删除和总览重建，并继续验证其余图片的原始字节。
