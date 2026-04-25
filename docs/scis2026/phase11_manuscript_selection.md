# SCIS Phase 11 Manuscript Table/Figure Selection

This document records the first page-budget-oriented selection pass for the
SCIS 2026 manuscript.

## Main-Paper Selection

The manuscript currently keeps the following generated artifacts in the main
text:

- `figure1a_prior_diagonal_design`: prior bundled design.
- `figure1b_factorial_design`: SCIS fully crossed design.
- `table1_run_validity`: run completeness and structured-output validity.
- `effect_summary_bootstrap_ci`: primary decomposition with uncertainty.
- `figure2a_entropy_heatmap`: representative entropy grid.
- `figure2b_score_heatmap`: representative score grid.
- `table3_model_metric_summary`: model-level score versus entropy summary.
- `figure3_model_metric_interaction_heatmap`: compact model x metric view.
- `table4_entropy_sensitivity`: membership-family sensitivity summary.

## Moved Out of Main Flow

The following artifacts remain tracked and reproducible, but are no longer
included directly in `paper/scis2026/main.tex`:

- `table2_effect_summary`: point estimates without bootstrap intervals. The
  CI table supersedes it in the main paper.
- `table5_top_interaction_cases`: useful for appendix selection or qualitative
  follow-up, but too case-specific for the first main-paper layout.
- `figure1_design_comparison`: useful as a full-width or slide figure, but split
  one-column panels are more readable in a two-column paper.
- `figure2_representative_heatmaps`: useful as a full-width overview, but split
  heatmaps keep labels, cell values, and colorbars readable in one-column
  placement.

## Rationale

The point-estimate table and CI table communicate the same decomposition. For a
conference paper, the CI table is the stronger main table because it includes
uncertainty while preserving the same point estimates. Top interaction cases
are useful for diagnosing examples, but they should not compete with the main
model-level and metric-level summaries.

The original paired Fig. 1 and Fig. 2 layouts were also replaced in the main
text by split one-column panels. This keeps labels and heatmap values readable
under the two-column IEEE layout while preserving the paired versions as
tracked artifacts for slides or alternate formatting.

## Next Steps

1. Review whether the model-level table and model-level heatmap are redundant.
2. Decide whether the entropy sensitivity table remains in the main text or
   moves to an appendix.
3. Add final citations for LLM emotion benchmarks and membership-function
   design.
4. Tighten the manuscript prose to the SCIS page limit after the final venue
   template constraints are known.
