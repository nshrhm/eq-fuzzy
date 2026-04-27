# ICICIC 2026 budget4 pilot archive v1

This archive indexes the earlier Qwen-containing budget4 matched-subset run.
It is preserved as pilot/provenance material only.

## Pilot artifacts

- Sanity run: `runs/icicic2026/icicic2026_benchmark_positioning_v1_sanity/`
- Main run: `runs/icicic2026/icicic2026_benchmark_positioning_v1_main/`
- Sanity analysis: `artifacts/icicic2026/matched_subset_sanity_analysis_v1/`
- Main analysis: `artifacts/icicic2026/matched_subset_analysis_v1/`
- Model panel: `configs/shared/models_budget4.yaml`

## Reason for archive status

The budget4 pilot used four models and produced 240 main response rows.
It showed schema noncompliance for `qwen/qwen3.6-plus`, so it must not be used
as the final ICICIC main panel.

The accepted matched-subset main materials are the stable6 outputs:

- Main run: `runs/icicic2026/icicic2026_benchmark_positioning_v1_stable6_main/`
- Main analysis: `artifacts/icicic2026/matched_subset_stable6_analysis_v1/`
- Model panel: `configs/icicic/models_stable6_from_scis.yaml`

Do not build manuscript-facing result tables or figures from the budget4 pilot.
