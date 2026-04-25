# SCIS Phase 6.5 Main Result Inspection

This document records the first descriptive inspection of the SCIS 2026 main
run. It is an analysis-readiness and result-shaping note, not the final paper
interpretation.

## Input

- Analysis directory: `artifacts/scis2026/main_analysis_v1/`
- Inspection directory: `artifacts/scis2026/main_inspection_v1/`
- Run id: `scis2026_factorial_v1_main_manifest_v1`
- Primary membership family: `sigmoid_s_v1`

## Readiness Facts

- Responses: `1440 / 1440`
- Emotion rows: `5760`
- Missing score rows: `0`
- Missing structural cells: `0`
- Non-estimable decomposition units: `0`
- Readiness passed: `True`

## Inspection Scope

The inspection computes the same balanced persona x temperature decomposition
for:

- `score`, using cell-level mean scores.
- `H_norm_sigmoid_s_v1`, using normalized fuzzy entropy under the primary
  `sigmoid_s_v1` membership family.

The quantities are descriptive effect components, not confirmatory inference:

- `SS_persona`
- `SS_temperature`
- `SS_persona_x_temperature`
- `interaction_burden`
- `separability_share`

## Metric-Level Summary

| metric | emotion | n_units | mean_SS_persona | mean_SS_temperature | mean_SS_persona_x_temperature | mean_total_SS | mean_interaction_burden | mean_separability_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H_norm_sigmoid_s_v1 | anger | 18 | 0.334538667 | 0.033832556 | 0.084602222 | 0.452973444 | 0.282550667 | 0.717449333 |
| H_norm_sigmoid_s_v1 | interest | 18 | 0.327153 | 0.014424444 | 0.044711111 | 0.386288556 | 0.135054167 | 0.864945833 |
| H_norm_sigmoid_s_v1 | sadness | 18 | 1.023689611 | 0.025274111 | 0.059308556 | 1.108272278 | 0.095581 | 0.904419 |
| H_norm_sigmoid_s_v1 | surprise | 18 | 0.406081556 | 0.020895778 | 0.074236444 | 0.501213778 | 0.198217222 | 0.801782778 |
| score | anger | 18 | 2449.15375 | 37.408194444 | 74.072361111 | 2560.634305556 | 0.131655278 | 0.868344722 |
| score | interest | 18 | 2419.269722222 | 20.421944444 | 62.309166667 | 2502.000833333 | 0.04554 | 0.95446 |
| score | sadness | 18 | 3700.667083333 | 14.382638889 | 71.360138889 | 3786.409861111 | 0.034137611 | 0.965862389 |
| score | surprise | 18 | 2655.211805556 | 27.74625 | 80.724305556 | 2763.682361111 | 0.069986944 | 0.930013056 |

## Largest Relative Interaction Burdens

These rows are useful for selecting representative figures and for checking
where persona and temperature are least separable.

| metric | model_id | story_id | emotion | SS_persona | SS_temperature | SS_persona_x_temperature | total_SS | interaction_burden | separability_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H_norm_sigmoid_s_v1 | anthropic/claude-sonnet-4.5 | T3 | anger | 0.051893 | 0.038175 | 0.170826 | 0.260894 | 0.654771 | 0.345229 |
| H_norm_sigmoid_s_v1 | deepseek/deepseek-v3.2 | T3 | anger | 0.06248 | 0.056133 | 0.218355 | 0.336968 | 0.647999 | 0.352001 |
| score | google/gemini-2.5-pro | T1 | anger | 0.75 | 0.75 | 2.25 | 3.75 | 0.6 | 0.4 |
| H_norm_sigmoid_s_v1 | google/gemini-2.5-pro | T1 | anger | 0.000315 | 0.000315 | 0.000944 | 0.001574 | 0.6 | 0.4 |
| H_norm_sigmoid_s_v1 | x-ai/grok-4.20 | T3 | interest | 0.061204 | 0.040656 | 0.142675 | 0.244535 | 0.583454 | 0.416546 |
| H_norm_sigmoid_s_v1 | google/gemini-2.5-pro | T3 | surprise | 0.213178 | 0.03581 | 0.224718 | 0.473706 | 0.474383 | 0.525617 |
| score | meta-llama/llama-4-maverick | T2 | surprise | 33.0 | 17.0 | 45.0 | 95.0 | 0.473684 | 0.526316 |
| H_norm_sigmoid_s_v1 | deepseek/deepseek-v3.2 | T3 | surprise | 0.10859 | 0.079415 | 0.154584 | 0.342589 | 0.451223 | 0.548777 |
| H_norm_sigmoid_s_v1 | x-ai/grok-4.20 | T1 | surprise | 0.24738 | 0.018979 | 0.207502 | 0.473861 | 0.437897 | 0.562103 |
| H_norm_sigmoid_s_v1 | meta-llama/llama-4-maverick | T2 | surprise | 0.026265 | 0.011535 | 0.027989 | 0.065789 | 0.425432 | 0.574568 |
| H_norm_sigmoid_s_v1 | deepseek/deepseek-v3.2 | T1 | anger | 0.121669 | 0.050436 | 0.117236 | 0.289341 | 0.405184 | 0.594816 |
| H_norm_sigmoid_s_v1 | x-ai/grok-4.20 | T3 | sadness | 0.196297 | 0.012376 | 0.126713 | 0.335386 | 0.377812 | 0.622188 |

Because `interaction_burden` is a ratio, rows with small absolute variation can
rank highly. The following table ranks by absolute interaction sum of squares.

## Largest Absolute Interaction Components

| metric | model_id | story_id | emotion | SS_persona | SS_temperature | SS_persona_x_temperature | total_SS | interaction_burden | separability_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| score | deepseek/deepseek-v3.2 | T3 | sadness | 9244.6875 | 13.6875 | 380.0625 | 9638.4375 | 0.039432 | 0.960568 |
| score | deepseek/deepseek-v3.2 | T3 | anger | 1838.75 | 82.25 | 362.75 | 2283.75 | 0.15884 | 0.84116 |
| score | google/gemini-2.5-pro | T3 | surprise | 5652.0 | 57.5 | 292.5 | 6002.0 | 0.048734 | 0.951266 |
| score | google/gemini-2.5-pro | T1 | interest | 2992.1875 | 96.6875 | 282.5625 | 3371.4375 | 0.083811 | 0.916189 |
| score | x-ai/grok-4.20 | T3 | sadness | 11576.1875 | 19.1875 | 278.5625 | 11873.9375 | 0.02346 | 0.97654 |
| score | deepseek/deepseek-v3.2 | T3 | surprise | 4887.5 | 216.5 | 218.0 | 5322.0 | 0.040962 | 0.959038 |
| score | meta-llama/llama-4-maverick | T3 | anger | 297.0 | 51.0 | 195.0 | 543.0 | 0.359116 | 0.640884 |
| score | x-ai/grok-4.20 | T3 | anger | 3684.58 | 80.78 | 194.24 | 3959.6 | 0.049055 | 0.950945 |
| score | deepseek/deepseek-v3.2 | T1 | surprise | 5472.1875 | 24.1875 | 191.5625 | 5687.9375 | 0.033679 | 0.966321 |
| score | google/gemini-2.5-pro | T3 | interest | 8468.1875 | 42.1875 | 176.5625 | 8686.9375 | 0.020325 | 0.979675 |
| score | google/gemini-2.5-pro | T1 | surprise | 4797.5 | 12.5 | 164.0 | 4974.0 | 0.032971 | 0.967029 |
| score | meta-llama/llama-4-maverick | T3 | sadness | 666.75 | 50.75 | 136.25 | 853.75 | 0.15959 | 0.84041 |

## Next Use

Use this inspection to choose Phase 7 tables and Phase 8 figures. The current
results support moving from run validation to descriptive result construction,
while bootstrap confidence intervals remain a separate Phase 9 task.

## Machine-Readable Summary

```json
{
  "analysis_dir": "artifacts/scis2026/main_analysis_v1",
  "output_dir": "artifacts/scis2026/main_inspection_v1",
  "primary_membership_family": "sigmoid_s_v1",
  "valid_output": {
    "n_response_rows": 1440,
    "n_response_ok": 1440,
    "valid_output_rate": 1.0,
    "n_emotion_rows": 5760,
    "n_missing_score_rows": 0,
    "n_missing_structural_cells": 0,
    "n_non_estimable_decomposition_units": 0,
    "readiness_passed": true
  },
  "n_score_decomposition_units": 72,
  "n_entropy_decomposition_units": 72,
  "n_metric_decomposition_units": 144,
  "n_decomposition_summary_rows": 8,
  "top_n": 20,
  "max_interaction_burden": 0.654771,
  "max_interaction_metric": "H_norm_sigmoid_s_v1",
  "max_absolute_interaction": 380.0625,
  "max_absolute_interaction_metric": "score"
}
```
