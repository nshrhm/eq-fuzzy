# SCIS Phase 9 Bootstrap Confidence Intervals

This phase adds uncertainty estimates to the primary descriptive effect
summaries. The bootstrap keeps model, text, persona, and temperature cells
fixed, resamples repeats within each cell, and preserves the four emotion
scores from the same response as a block. Machine-readable outputs include
percentile, basic, and point-centered normal bootstrap intervals; the
manuscript-facing LaTeX table uses the point-centered normal intervals for
readability.

## Outputs

- `artifacts/scis2026/main_bootstrap_v1/effect_summary_bootstrap_ci.csv`
- `artifacts/scis2026/main_bootstrap_v1/effect_summary_bootstrap_ci.tex`
- `artifacts/scis2026/main_bootstrap_v1/bootstrap_summary.json`

## Primary CI Summary

| metric | emotion | mean_persona_share_point | mean_persona_share_normal_ci_low | mean_persona_share_normal_ci_high | mean_temperature_share_point | mean_temperature_share_normal_ci_low | mean_temperature_share_normal_ci_high | mean_interaction_burden_point | mean_interaction_burden_normal_ci_low | mean_interaction_burden_normal_ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H_norm_sigmoid_s_v1 | anger | 0.610205001 | 0.560544084 | 0.659865918 | 0.107258666 | 0.080566712 | 0.13395062 | 0.282536333 | 0.229480178 | 0.335592488 |
| H_norm_sigmoid_s_v1 | interest | 0.81661386 | 0.763575901 | 0.869651819 | 0.048332239 | 0.030128822 | 0.066535656 | 0.135053901 | 0.093443038 | 0.176664764 |
| H_norm_sigmoid_s_v1 | sadness | 0.870591902 | 0.837166742 | 0.904017062 | 0.033827062 | 0.01832116 | 0.049332964 | 0.095581036 | 0.067495404 | 0.123666668 |
| H_norm_sigmoid_s_v1 | surprise | 0.733133084 | 0.688671374 | 0.777594794 | 0.06865037 | 0.042783283 | 0.094517457 | 0.198216546 | 0.157976352 | 0.23845674 |
| score | anger | 0.808339565 | 0.773977441 | 0.842701689 | 0.060005109 | 0.040740315 | 0.079269903 | 0.131655326 | 0.091700028 | 0.171610624 |
| score | interest | 0.936769155 | 0.91723497 | 0.95630334 | 0.01769086 | 0.008048546 | 0.027333174 | 0.045539984 | 0.029861952 | 0.061218016 |
| score | sadness | 0.953340768 | 0.936853431 | 0.969828105 | 0.012521654 | 0.004498426 | 0.020544882 | 0.034137578 | 0.021068026 | 0.04720713 |
| score | surprise | 0.900213073 | 0.878300565 | 0.922125581 | 0.029799879 | 0.014907892 | 0.044691866 | 0.069987048 | 0.049694939 | 0.090279157 |

## Construction Summary

```json
{
  "input_jsonl": "runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw_repaired.jsonl",
  "membership_config": "configs/scis/fuzzy_membership_v1.yaml",
  "primary_table": "artifacts/scis2026/main_tables_v1/table2_effect_summary.csv",
  "output_dir": "artifacts/scis2026/main_bootstrap_v1",
  "primary_family": "sigmoid_s_v1",
  "n_records": 1440,
  "n_cells": 288,
  "cell_sizes": [
    5
  ],
  "n_bootstrap": 500,
  "seed": 20260425,
  "ci_level": 0.95,
  "latex_ci_method": "point_centered_normal_bootstrap",
  "n_ci_rows": 8
}
```
