# SCIS Phase 14 Reviewer-Risk Diagnostics

This document records lightweight diagnostics for reviewer-facing risk checks.
These diagnostics use the completed SCIS main run and do not change the main
experimental design.

## Summary

```json
{
  "retry_gate_passed": true,
  "base_failed_rows": 4,
  "repaired_failed_rows": 0,
  "max_abs_leave_one_model_out_delta_interaction_burden": 0.0342526,
  "max_story_stratified_mean_interaction_burden": 0.3510455,
  "score_mean_interaction_burden_range": [
    0.034137611,
    0.131655278
  ],
  "entropy_mean_interaction_burden_range": [
    0.095581,
    0.282550667
  ],
  "entropy_sensitivity_cell_mean_correlation": "0.932668023",
  "entropy_sensitivity_mean_abs_delta": "0.129519388",
  "requires_main_run_redesign": false
}
```

Interpretation: the diagnostics do not indicate a need to redesign the `r = 5`
main run. They identify points to describe carefully in the manuscript or
appendix.

## Retry and Validity Check

| manifest_row | model_id | story_id | condition_id | persona_id | temperature | repetition | retry_ok | repaired_ok | base_failure_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 202 | openai/gpt-5.4 | T3 | C09 | p3 | 0.1 | 3 | True | True | Response content did not contain a JSON object. |
| 785 | x-ai/grok-4.20 | T1 | C14 | p4 | 0.4 | 1 | True | True | Response content did not contain a JSON object. |
| 916 | x-ai/grok-4.20 | T3 | C08 | p2 | 0.9 | 2 | True | True | Response content did not contain a JSON object. |
| 1358 | meta-llama/llama-4-maverick | T2 | C16 | p4 | 0.9 | 4 | True | True | invalid_reason:sadness |

## Emotion-Level Interaction Summary

| metric | emotion | n_units | mean_persona_share | mean_temperature_share | mean_interaction_burden | mean_separability_share |
| --- | --- | --- | --- | --- | --- | --- |
| H_norm_sigmoid_s_v1 | anger | 18 | 0.610205001 | 0.107258666 | 0.282550667 | 0.717449333 |
| H_norm_sigmoid_s_v1 | interest | 18 | 0.81661386 | 0.048332239 | 0.135054167 | 0.864945833 |
| H_norm_sigmoid_s_v1 | sadness | 18 | 0.870591902 | 0.033827062 | 0.095581 | 0.904419 |
| H_norm_sigmoid_s_v1 | surprise | 18 | 0.733133084 | 0.06865037 | 0.198217222 | 0.801782778 |
| score | anger | 18 | 0.808339565 | 0.060005109 | 0.131655278 | 0.868344722 |
| score | interest | 18 | 0.936769155 | 0.01769086 | 0.04554 | 0.95446 |
| score | sadness | 18 | 0.953340768 | 0.012521654 | 0.034137611 | 0.965862389 |
| score | surprise | 18 | 0.900213073 | 0.029799879 | 0.069986944 | 0.930013056 |

## Largest Leave-One-Model-Out Changes

| omitted_model_id | metric | emotion | full_mean_interaction_burden | leave_one_out_mean_interaction_burden | delta_interaction_burden |
| --- | --- | --- | --- | --- | --- |
| deepseek/deepseek-v3.2 | H_norm_sigmoid_s_v1 | anger | 0.282550667 | 0.248298067 | -0.0342526 |
| anthropic/claude-sonnet-4.5 | H_norm_sigmoid_s_v1 | surprise | 0.198217222 | 0.227831867 | 0.029614645 |
| google/gemini-2.5-pro | score | anger | 0.131655278 | 0.104214867 | -0.027440411 |
| google/gemini-2.5-pro | H_norm_sigmoid_s_v1 | surprise | 0.198217222 | 0.1711808 | -0.027036422 |
| x-ai/grok-4.20 | H_norm_sigmoid_s_v1 | anger | 0.282550667 | 0.3079484 | 0.025397733 |
| openai/gpt-5.4 | H_norm_sigmoid_s_v1 | interest | 0.135054167 | 0.159148133 | 0.024093966 |
| anthropic/claude-sonnet-4.5 | score | anger | 0.131655278 | 0.155383533 | 0.023728255 |
| openai/gpt-5.4 | H_norm_sigmoid_s_v1 | anger | 0.282550667 | 0.306219533 | 0.023668866 |
| x-ai/grok-4.20 | score | anger | 0.131655278 | 0.153285333 | 0.021630055 |
| google/gemini-2.5-pro | H_norm_sigmoid_s_v1 | interest | 0.135054167 | 0.113599933 | -0.021454234 |
| meta-llama/llama-4-maverick | score | surprise | 0.069986944 | 0.050498867 | -0.019488077 |
| meta-llama/llama-4-maverick | score | anger | 0.131655278 | 0.113397467 | -0.018257811 |

## Largest Story-Stratified Interaction Burdens

| story_id | metric | emotion | n_units | mean_persona_share | mean_temperature_share | mean_interaction_burden |
| --- | --- | --- | --- | --- | --- | --- |
| T3 | H_norm_sigmoid_s_v1 | anger | 6 | 0.541336562 | 0.107617987 | 0.3510455 |
| T1 | H_norm_sigmoid_s_v1 | anger | 6 | 0.571093594 | 0.130794667 | 0.298154833 |
| T3 | H_norm_sigmoid_s_v1 | surprise | 6 | 0.638052664 | 0.108675509 | 0.253275167 |
| T1 | score | anger | 6 | 0.709845565 | 0.085513381 | 0.204641 |
| T2 | H_norm_sigmoid_s_v1 | anger | 6 | 0.718184848 | 0.083363344 | 0.198451667 |
| T1 | H_norm_sigmoid_s_v1 | surprise | 6 | 0.780804755 | 0.038045755 | 0.1811495 |
| T3 | H_norm_sigmoid_s_v1 | interest | 6 | 0.774074091 | 0.045494326 | 0.180431 |
| T3 | H_norm_sigmoid_s_v1 | sadness | 6 | 0.802424378 | 0.032975098 | 0.164600167 |
| T2 | H_norm_sigmoid_s_v1 | surprise | 6 | 0.780541833 | 0.059229846 | 0.160227 |
| T2 | score | surprise | 6 | 0.811588366 | 0.048137328 | 0.140274167 |
| T3 | score | anger | 6 | 0.853601127 | 0.02640028 | 0.119998667 |
| T2 | H_norm_sigmoid_s_v1 | interest | 6 | 0.818792411 | 0.063301367 | 0.117907667 |

## Manuscript Use

- The retry check supports describing the four failed main-run rows as targeted
  repair cases rather than systematic failure.
- Leave-one-model-out and story-stratified outputs should be used as appendix
  material unless a reviewer asks whether a single model or text dominates the
  result.
- The emotion summary supports the current Results narrative: entropy has
  larger interaction burden than score, with anger and surprise requiring the
  most careful discussion.
