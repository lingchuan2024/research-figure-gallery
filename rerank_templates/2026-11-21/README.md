# Rerank 实测数据绘图模板（F01 / F02 / F06 / F07 / F08 / F09）· 2026-11-21

本目录与 [2026-11-16 模板](../2026-11-16/README.md)（F03 森林图、F04 雨云图、F05 Pareto 散点图）互补，补齐剩余 **6 类高频论文正文/附录图表** 的可复现、严格校验 Python 模板。所有脚本均输出 `PNG + SVG + PDF`、`*_summary.csv` 以及不含本机绝对路径的 `*_provenance.json`。

[六图总览](templates_overview.png) · [实测配置示例](config.measured.example.json)

## 模板清单与输入 CSV 契约

| 图型 | 脚本 | 默认输入 CSV | 核心字段要求 |
| --- | --- | --- | --- |
| **F01 · 主结果表** | `plot_results_table.py` | `observations.csv` | 与 2026-11-16 完全兼容：`(benchmark, question_id, subset, method, score, status, ...)`，严格配对 |
| **F02 · 配对比较** | `plot_paired.py` | `observations.csv` | 自动适配 `score.kind=binary`（翻转统计 + 分组配对差 CI）或 `bounded`（逐题哑铃图 + 排序差值条） |
| **F06 · 预算曲线** | `plot_budget_curve.py` | `budget_runs.csv` | `(benchmark, question_id, method, budget_value, score, status)`，每个预算点独立运行且严格配对 |
| **F07 · 排名迁移热图** | `plot_rank_transition.py` | `rank_transitions.csv` | `(benchmark, question_id, method, doc_id, rank_before, rank_after, is_relevant)`；池外填 `outside` 单独计数 |
| **F08 · 工具与文本组成** | `plot_tool_composition.py` | `tool_calls.csv` | `(benchmark, question_id, method, tool, calls, returned_chars)`，严格配对，池化占比与均量并列 |
| **F09 · 工具轨迹时间线** | `plot_trajectory.py` | `trajectories.csv` | `(case_id, method, turn, tool, event_flag, note)`，单题机制诊断，自动标注 `first_evidence` 与 `rerank_hit` |

## 快速运行与接入实测数据

```bash
# 1. 生成合成示例数据并渲染全部 6 张模板 + 总览图
python run_all.py

# 2. 运行全部契约校验与单元测试
python verify.py

# 3. 接入真实实验数据（先复制 config.measured.example.json 并填完所有 REPLACE_* 字段）
python plot_results_table.py --data /path/to/observations.csv --config my_config.json --output-dir out/measured
python plot_paired.py --data /path/to/observations.csv --config my_config.json --method agent_rerank --output-dir out/measured
```
