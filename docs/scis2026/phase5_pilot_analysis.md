# SCIS 2026 Phase 5.5 Pilot Analysis Readiness

This note records the lightweight pilot analysis-readiness pass. The pilot
analysis is not main-paper evidence. Its purpose is to check whether the
factorial outputs can be expanded and decomposed before the Phase 6 main run.

## Inputs and Outputs

Input:

- `runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1/raw.jsonl`

Output directory:

- `artifacts/scis2026/pilot_analysis_v1/`

Generated files:

- `emotion_long.csv`: one row per response-emotion pair.
- `entropy_long.csv`: one row per response-emotion-membership-family
  combination.
- `cell_score_summary.csv`: model x story x persona x temperature x emotion
  score summaries.
- `entropy_cell_summary.csv`: model x story x persona x temperature x emotion
  entropy summaries by membership family.
- `entropy_family_comparison.csv`: condition-level normalized entropy
  comparison between the primary and baseline membership families.
- `persona_temperature_mean_grid.csv`: model/story/emotion grids for the 4 x 4
  persona-temperature means.
- `factorial_decomposition.csv`: balanced two-way persona-temperature
  decomposition by model, story, and emotion.
- `analysis_summary.json`: readiness counts and pass/fail status.

## Command

```bash
python scripts/scis2026/analyze_factorial_scores.py
```

## Readiness Criteria

Phase 5.5 passes if:

- `n_response_rows = 576`
- `n_emotion_rows = 2304`
- `n_valid_score_rows = 2304`
- `n_missing_score_rows = 0`
- `n_entropy_rows = 4608`
- `n_cell_summary_rows = 768`
- `n_entropy_cell_summary_rows = 1536`
- `n_decomposition_units = 48`
- `n_missing_structural_cells = 0`
- `n_zero_valid_score_cells = 0`
- `n_non_estimable_decomposition_units = 0`

These checks confirm that the pilot data can support the planned descriptive
persona-temperature decomposition. They do not justify final SCIS conclusions.

## Result

Phase 5.5 pilot analysis readiness passed on 2026-04-25.

Summary:

- `n_response_rows = 576`
- `n_response_ok = 576`
- `n_emotion_rows = 2304`
- `n_valid_score_rows = 2304`
- `n_missing_score_rows = 0`
- `n_entropy_rows = 4608`
- `n_cell_summary_rows = 768`
- `n_entropy_cell_summary_rows = 1536`
- `n_decomposition_units = 48`
- `n_non_estimable_decomposition_units = 0`
- `readiness_passed = true`

Entropy specification:

- primary membership family: `sigmoid_s_v1`
- baseline membership family: `legacy_linear_v1`
- primary entropy outcome for SCIS analysis: `H_norm`
- `Hmax_legacy_linear_v1 = 1.057697511124`
- `Hmax_sigmoid_s_v1 = 1.018502773018`

Primary-vs-baseline sensitivity snapshot:

- condition-level `H_norm` cell pairs: `768`
- Pearson correlation: `0.920492937`
- mean absolute normalized entropy difference: `0.136379089`

No pilot failure mode requires changing the current main-run design. The Phase
6 main run remains:

```text
6 models x 3 texts x 16 persona-temperature conditions x 5 repeats = 1440 trials
```
