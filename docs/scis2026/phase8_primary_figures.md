# SCIS Phase 8 Primary Figures

This document records the first primary figure candidates for the SCIS 2026
main paper. The figures are descriptive and should be paired with bootstrap
confidence intervals in a later phase before final claims are fixed.

## Generated Figures

| Figure | Path | Caption seed |
| --- | --- | --- |
| `figure1_design_comparison` | `artifacts/scis2026/main_figures_v1/figure1_design_comparison.png` | Prior diagonal persona-temperature bundles are contrasted with the SCIS fully crossed persona x temperature design. |
| `figure2_representative_heatmaps` | `artifacts/scis2026/main_figures_v1/figure2_representative_heatmaps.png` | H_norm_sigmoid_s_v1 anthropic/claude-sonnet-4.5 T3 anger burden=0.654771; score deepseek/deepseek-v3.2 T3 sadness burden=0.039432 |
| `figure3_model_metric_interaction_heatmap` | `artifacts/scis2026/main_figures_v1/figure3_model_metric_interaction_heatmap.png` | Mean interaction burden is summarized for score and normalized fuzzy entropy by model. |

## Construction Summary

```json
{
  "analysis_dir": "artifacts/scis2026/main_analysis_v1",
  "inspection_dir": "artifacts/scis2026/main_inspection_v1",
  "tables_dir": "artifacts/scis2026/main_tables_v1",
  "output_dir": "artifacts/scis2026/main_figures_v1",
  "primary_family": "sigmoid_s_v1",
  "n_figures": 3,
  "figures": [
    "figure1_design_comparison",
    "figure2_representative_heatmaps",
    "figure3_model_metric_interaction_heatmap"
  ],
  "representative_cases": [
    {
      "metric": "H_norm_sigmoid_s_v1",
      "model_id": "anthropic/claude-sonnet-4.5",
      "story_id": "T3",
      "emotion": "anger",
      "interaction_burden": "0.654771"
    },
    {
      "metric": "score",
      "model_id": "deepseek/deepseek-v3.2",
      "story_id": "T3",
      "emotion": "sadness",
      "interaction_burden": "0.039432"
    }
  ]
}
```
