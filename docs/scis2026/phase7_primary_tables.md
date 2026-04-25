# SCIS Phase 7 Primary Tables

This document records the construction of primary paper-table candidates from
the SCIS 2026 main-run inspection artifacts. These tables are descriptive and
are intended to guide manuscript drafting before bootstrap confidence intervals
are added.

## Inputs

- Main analysis: `artifacts/scis2026/main_analysis_v1/`
- Main inspection: `artifacts/scis2026/main_inspection_v1/`
- Primary tables: `artifacts/scis2026/main_tables_v1/`

## Generated Tables

- `table1_run_validity`: run completeness and valid-output rate.
- `table2_effect_summary`: metric x emotion persona-temperature decomposition
  shares.
- `table3_model_metric_summary`: model x metric decomposition shares.
- `table4_entropy_sensitivity`: `sigmoid_s_v1` versus `legacy_linear_v1`
  normalized entropy comparison.
- `table5_top_interaction_cases`: largest relative and absolute interaction
  cases for figure and appendix selection.

Each table is written as both CSV and LaTeX (`.tex`) output.

## Run Validity

| response_rows | response_ok | valid_output_rate | emotion_rows | missing_score_rows | missing_structural_cells |
| --- | --- | --- | --- | --- | --- |
| 1440 | 1440 | 1.0 | 5760 | 0 | 0 |

## Effect Summary

| metric | emotion | n_units | mean_persona_share | mean_temperature_share | mean_interaction_burden | mean_separability_share |
| --- | --- | --- | --- | --- | --- | --- |
| H_norm_sigmoid_s_v1 | anger | 18 | 0.610205001 | 0.107258666 | 0.282536333 | 0.717463667 |
| H_norm_sigmoid_s_v1 | interest | 18 | 0.81661386 | 0.048332239 | 0.135053901 | 0.864946099 |
| H_norm_sigmoid_s_v1 | sadness | 18 | 0.870591902 | 0.033827062 | 0.095581036 | 0.904418964 |
| H_norm_sigmoid_s_v1 | surprise | 18 | 0.733133084 | 0.06865037 | 0.198216546 | 0.801783454 |
| score | anger | 18 | 0.808339565 | 0.060005109 | 0.131655326 | 0.868344674 |
| score | interest | 18 | 0.936769155 | 0.01769086 | 0.045539984 | 0.954460016 |
| score | sadness | 18 | 0.953340768 | 0.012521654 | 0.034137578 | 0.965862422 |
| score | surprise | 18 | 0.900213073 | 0.029799879 | 0.069987048 | 0.930012952 |

## Entropy Sensitivity

| primary_family | baseline_family | n_cell_pairs | pearson_H_norm_cell_mean | mean_abs_H_norm_diff | max_abs_H_norm_diff |
| --- | --- | --- | --- | --- | --- |
| sigmoid_s_v1 | legacy_linear_v1 | 1152 | 0.932668023 | 0.129519388 | 0.47861575 |

## Construction Summary

```json
{
  "analysis_dir": "artifacts/scis2026/main_analysis_v1",
  "inspection_dir": "artifacts/scis2026/main_inspection_v1",
  "output_dir": "artifacts/scis2026/main_tables_v1",
  "primary_family": "sigmoid_s_v1",
  "n_run_validity_rows": 1,
  "n_effect_summary_rows": 8,
  "n_model_metric_rows": 12,
  "n_entropy_sensitivity_rows": 1,
  "n_top_case_rows": 16,
  "latex_tables": [
    "table1_run_validity.tex",
    "table2_effect_summary.tex",
    "table3_model_metric_summary.tex",
    "table4_entropy_sensitivity.tex",
    "table5_top_interaction_cases.tex"
  ]
}
```
