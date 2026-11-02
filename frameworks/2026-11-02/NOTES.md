# 框架图：来源、取舍与迁移

这四张图补充的是论文方法部分的结构表达。前三张依据原论文的模块关系重新绘制；第四张依据当前讨论设计，尚未与实际 search / rerank 工具实现逐项核对。它们不含实验数值，也不证明任何方法更优。

每张图对应一份 Python 入口、一份可编辑 JSON 结构，以及 PNG、SVG、draw.io 文件。代码均为本库编写，未使用或宣称获得作者原始出图代码。SVG 保留文本，draw.io 为未压缩 XML，可在 diagrams.net 打开。图内用英文便于迁移到论文，中文用途说明位于主 README。

## 哪种结构适合我们

| 图 | 参考来源与范围 | 可借鉴的表达 | 使用边界 |
| --- | --- | --- | --- |
| F01 | [A-RAG v1, Fig. 3, PDF p4](https://arxiv.org/pdf/2602.03442v1#page=4)；方法 §§3.1–3.3 | Agent、工具接口、语料视图三层对齐；选择与观察构成闭环 | 原方法没有 reranker。keyword search 是运行时文本匹配，不能标成倒排索引；重复读取会返回状态提示，不能说所有成本为零。 |
| F02 | [FS-Researcher v2, Fig. 2, PDF p3](https://arxiv.org/pdf/2602.01566v2#page=3)；方法 §§2.1–2.3 | 两阶段 Agent 通过持久文件交接；证据、笔记、状态和报告分层摆放 | Writer 在知识库完成后启动，只有文件系统工具。当前短答案任务不必强行增加 Report Writer。 |
| F03 | [WebThinker v2, Fig. 3, PDF p4](https://arxiv.org/pdf/2504.21776v2#page=4)；方法 §§3.2–3.4 | 主推理调用嵌套探索器，探索器内部继续选择搜索/导航动作 | 只画 problem-solving 模式；省略报告撰写、报告 document memory 和 RL，不能称为完整训练/报告架构。 |
| F04 | 当前讨论的实验设计草图，无外部论文原图 | 对齐自动重排与自主调用的控制点，显式标出 search 观察和 rerank 观察 | 固定触发规则、自动 ranking query、snippet 构造与候选范围均需检查实现；不能当作已经核验的系统结构。 |

F01 最适合借鉴工具库的表达，F03 最适合借鉴推理闭环；F04 与当前 search / rerank 实验最直接。F02 是扩展到长报告和持久证据管理时的结构参考。

## F04 的阅读口径

- 上层：在此比较单元内，搜索后由固定策略触发 reranker，模型看到处理后的返回内容。自动 ranking query 的生成规则保留为“verify configuration”。
- 下层：模型先看到 search 返回，再决定是否显式调用 rerank，并指定 ranking query `q_r`；若调用，会多得到一次 rerank 返回。下层的 Agent 与 Agent decision 表示同一模型的不同决策时刻；上下层代表两种方案。
- `C` 是候选集合。离线验证可以固定同一次搜索的候选快照以隔离变量；完整在线轨迹的候选池可能变化。
- `B` 是每次工具响应的字符上限，例如 100 字符。它不是 reranker 输入长度，也不是整题总返回量或总 token 预算。还需在实现中说明按每条结果还是整个响应截断；图中暂用整个响应的设计口径。
- `snippet → ≤ B` 表示返回处理，不规定 snippet 怎样选取。相关片段、头部截断等需要分别作为实验变量确认。
- 为判断自主调用的贡献，应分别控制 ranking query、snippet、候选池与调用策略；仅比较两条完整轨迹不能自动归因于调用权。

## 编辑与复现

从仓库根目录运行：

```bash
python frameworks/2026-11-02/code/F01_arag_hierarchical.py --output-dir output/frameworks --formats png svg
python frameworks/2026-11-02/build.py --output-dir output/frameworks
```

修改对应 `specs/F*.json` 中的模块文字、坐标、连接点和配色即可调整布局；`render.py` 同时生成 PNG/SVG 与 draw.io。draw.io 可独立拖拽编辑，但不会反向更新 JSON；希望代码再次复现时，应把修改同步到 JSON。

蓝/绿实线表示数据、读写或观察，橙色虚线表示选择、触发或阶段控制。该图例在每个源图中按实际关系使用，不表示执行耗时、收益或统计显著性。

版本、页码、官方仓库及所检查提交见 [sources.json](sources.json)；图与代码映射见 [manifest.json](manifest.json)。PDF 的 SHA-256 用于固定核对版本，缓存不随发布包分发。原有 39 个图片文件的摘要见 [preservation-baseline.json](preservation-baseline.json)。
