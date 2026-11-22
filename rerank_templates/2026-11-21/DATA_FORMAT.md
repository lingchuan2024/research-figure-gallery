# 输入数据格式与实测字段契约（F01 / F02 / F06 / F07 / F08 / F09）

本目录模板与 `rerank_templates/2026-11-16/DATA_FORMAT.md` 保持一致的严格配对与零/缺失值规范。所有 CSV 均为 UTF-8（可带 BOM），第一行为唯一表头；缺失值留空（不填 `nan`/`inf`，不把缺失值当成 `0`）。

## 1. `observations.csv`（F01 主结果表、F02 逐题配对比较）
- 唯一键：`(benchmark, question_id, method)`；每个 `benchmark` 内所有配置方法必须覆盖完全相同的 `question_id` 集合，不自动取交集丢题。
- 必需列：`benchmark`、`question_id`、`subset`（`All` 保留给自动汇总）、`method`、`score`（`[0,1]`，binary 时严格 0/1）、`status`（`complete|timeout|no_final|error`）。
- 成本列（按需，空值视为缺失）：`wall_seconds`、`rerank_seconds`、`main_input_tokens`、`reranker_input_tokens`、`rerank_events`、`scored_passages`。

## 2. `budget_runs.csv`（F06 预算/轮次趋势曲线）
- 唯一键：`(benchmark, budget_value, question_id, method)`；每个 `budget_value` 下各方法必须严格配对同一题集。
- 必需列：`benchmark`、`question_id`、`method`、`budget_value`（正数）、`score`、`status`。每个预算点应对应真实独立运行，不能用单次长轨迹事后截断代替。

## 3. `rank_transitions.csv`（F07 排名迁移矩阵热图）
- 唯一键：`(benchmark, question_id, method, doc_id)`。
- 必需列：`benchmark`、`question_id`、`method`、`doc_id`、`rank_before`、`rank_after`、`is_relevant`（`0/1` 或 `true/false`）。
- 排名为正整数或 `outside`（候选池外，单独计数而不伪造为末位）。

## 4. `tool_calls.csv`（F08 工具与返回文本组成）
- 唯一键：`(benchmark, question_id, method, tool)`；每个 `benchmark` 下各方法必须覆盖相同 `question_id`。
- 必需列：`benchmark`、`question_id`、`method`、`tool`、`calls`（非负整数）、`returned_chars`（非负整数，不等同于计费 input tokens）。

## 5. `trajectories.csv`（F09 工具轨迹时间线）
- 唯一键：`(case_id, method, turn)`。
- 必需列：`case_id`、`method`、`turn`（正整数）、`tool`、`event_flag`（`none|first_evidence|rerank_hit|final_correct|final_wrong`）、`note`。

## 6. `config.json`（配置与溯源）
真实实验请以 `config.measured.example.json` 为起点，将 `data_kind` 设为 `measured` 并填完所有 `REPLACE_*` 字段。每张图输出 `*_summary.csv` 与不含本机绝对路径的 `*_provenance.json`。
