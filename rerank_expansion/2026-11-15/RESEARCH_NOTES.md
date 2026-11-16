# Rerank 论文图表更新 · 2026-11-15

本轮从 **RankRAG、RankZephyr、FIRST 复现研究和 Qwen3 Embedding** 四篇论文中整理六张图，回答排序收益、顺序敏感性、计算预算和模型选择问题。数值来自论文表格，全部是**文献数据重绘，不是我们的实验结果**；绘图代码为本库实现，不宣称复现了作者训练或评测过程。

[六图总览](rerank_overview.png) · [返回统一图库](../../README.md) · [数据与来源审计](data_provenance.json) · [视觉筛选记录](AESTHETIC_REVIEW.md)

## 本轮图表与实验用途

| 图 | 来源 | 回答的问题 | 接入我们的实验时需要什么 |
| --- | --- | --- | --- |
| R01 · 最终回答对照 | RankRAG，Table 3，p. 8 | 在同一已训练模型中关闭推理时重排，最终 EM 如何变化？ | 同题、同主模型、同停止条件的 rerank 开关对照，另行记录成本 |
| R02 · 前排含答案材料召回 | RankRAG，Table 8，p. 21 | 重排是否让含答案材料进入前 5 条？ | 固定候选集合；记录重排前后答案证据所在位置，并保持 answer recall 的定义一致 |
| R03 · 输入顺序鲁棒性 | RankZephyr，Table 7，p. 11 | 仅打乱候选顺序是否改变结果？ | 固定候选成员，多次随机排列；记录分数均值与随机性来源 |
| R04 · 解码耗时 | FIRST 复现，Table 5，p. 6 | 输出整个排列和使用首标识符 logits 的耗时差多少？ | 单独记录 reranker 推理耗时、窗口调用数与输出 token；硬件、batch 和候选长度需一致 |
| R05 · 滑窗计算预算 | FIRST 复现，Table 6，p. 7 | 固定窗口大小，增加重叠和调用能否持续提高排序质量？ | 同一数据集、同候选池下改变 stride；同时报告 nDCG 与实际延迟 |
| R06 · 模型规模 | Qwen3 Embedding，Table 4，p. 8 | 更大 reranker 是否在每类任务都更好？ | 相同 first-stage 候选池；在我们自己的数据上分别测质量、延迟和显存 |

## 指标和对照边界

**RankRAG：把排序指标与最终回答分开。** R01 保留 Table 3 中全部五个采用 EM 的 OpenQA 数据集，不把其余任务的 F1/Accuracy 混入平均值。R02 显示 Table 8 全部六个“数据集 × 检索器”的 R@5，R@10/20 也完整保留在 CSV。Answer Recall 衡量前 k 条中是否存在含答案材料，不是找齐全部 gold 文档的比例。这里的 k 是评价截断位置，并非 reranker 的候选数量。论文未为 Table 3 每行提供最终 k，因此不能把该图解释为已核实的同 token 预算对比。

**RankZephyr：误差条的随机性来自输入排列。** 图中打乱后的均值及 99% 置信区间来自六次 shuffled order。原始顺序点没有报告区间，图中也不补造。该区间不能解释为对用户问题总体的置信区间。两个检索器分别提供 top-100 候选；同一行只改变顺序，跨检索器并非相同候选集合。

**FIRST：输出 token 减少不等于同倍数加速。** Table 5 的 711 与 18 是整题九次窗口调用的输出量；18 包含每窗口两个 token，并非整题只输出一个 token。延迟测量使用单张 RTX 4090，不能直接当作我们服务器的延迟，也不包含 agent 的整个搜索过程。不同训练 checkpoint 的质量表与这张解码耗时表不拼接成虚假的质量—速度点。

R05 只使用 Table 6 同一表内的延迟与 nDCG，展示固定窗口 20、stride 10/5/2 的对照，完整五种窗口配置的数据仍保存。主图展示 DL19、DL20，其余 DL21–23 保留在 CSV；DL20 中更多重叠并未带来持续提升，不据此代表全部五个数据集。原文 Table 6 的 caption 使用 RankMistral，而正文使用 FIRST，故图中采用中性方法说明并标注命名不一致，不擅自确定 checkpoint 身份。

**Qwen3：保留下降及不同任务的指标口径。** R06 保留原表全部六列，展示三个 Qwen3 reranker 的规模变化，并以同一 Qwen3-Embedding-0.6B 为检索基线。0.6B 在 MTEB-Code 低于检索基线，8B 在 MTEB-R 和 FollowIR 低于 4B，这些值均原样保留。图使用各 benchmark 原生分数和独立纵轴，尤其不把 FollowIR 与其余分数混合平均。参数量不是延迟，图中没有把参数比当成计算成本比。

这些研究主要评估静态 retrieve–rerank–generate 或离线排序，**尚不能直接回答多轮 agent 应在何时调用 rerank**。要检验按需调用，仍需对相同题目设置不重排、每次重排、按需重排，并记录触发次数、实际评分片段数、证据覆盖和最终质量。

## 来源及可复现文件

| 论文固定版本 | 原始来源 | 已核对页面 |
| --- | --- | --- |
| RankRAG，2407.02485v1 | [论文](https://arxiv.org/abs/2407.02485v1) · [本地 PDF](sources/rankrag_2407.02485v1.pdf) | [p. 8](source_pages/rankrag_table3_page08.png)、[p. 21](source_pages/rankrag_table8_page21.png) |
| RankZephyr，2312.02724v1 | [论文](https://arxiv.org/abs/2312.02724v1) · [本地 PDF](sources/rankzephyr.pdf) | Table 7，p. 11 |
| Accelerating Listwise Reranking: Reproducing and Enhancing FIRST，SIGIR 2025 作者版 | [作者 PDF](https://zijianchen.ca/papers/Accelerating%20Listwise%20Reranking%20Reproducing%20and%20Enhancing%20FIRST.pdf) · [本地 PDF](sources/first_reproduction_sigir2025.pdf) | Tables 5–6，pp. 6–7 |
| Qwen3 Embedding，2506.05176v3 | [论文](https://arxiv.org/abs/2506.05176v3) · [本地 PDF](sources/qwen3_embedding_2506.05176v3.pdf) | [Table 4，p. 8](source_pages/qwen3_p08.png) |

来源审计记录原始 PDF 与 CSV 的 SHA256、页码、筛选范围和派生计算。没有逐题样本的表格不附加虚构误差条。没有利用图中像素估读曲线，也没有把不同论文的分数合并排行。

```bash
# 在图库根目录运行，只重建本轮六张图
python rerank_expansion/2026-11-15/build.py
# 重建统一文档并核验；不会重画旧图
python scripts/build_gallery.py --keep-existing-images
```

每张脚本都支持 `--data-dir`、`--output-dir`、`--formats png svg`。更换为自己的实验数据时另存输出，并同步更改标题、来源声明和条件说明。
