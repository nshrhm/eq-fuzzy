# SCIS Phase 15 Figure and Table Finalization

This document records the first figure/table finalization decision for the
SCIS 2026 manuscript.

## Table 3 versus Fig. 3 Check

The first Phase 15 check compared:

- `table3_model_metric_summary`
- `figure3_model_metric_interaction_heatmap`

Both artifacts summarize model-level score versus normalized fuzzy entropy
interaction burden. Table 3 contains exact persona, temperature, mean
interaction, and maximum interaction shares. Fig. 3 shows the mean interaction
burden as a compact heatmap.

## Decision

Keep Fig. 3 in the main text and move Table 3 out of the main flow.

Rationale:

- The main-paper claim is comparative: entropy has higher
  persona-temperature interaction burden than score across the model panel.
- Fig. 3 communicates this comparison more efficiently under a two-column
  layout.
- Table 3 duplicates the same model-level contrast and consumes a full-width
  table slot.
- Exact model-level shares remain tracked in
  `artifacts/scis2026/main_tables_v1/table3_model_metric_summary.csv` and
  `.tex` for appendix or reproducibility use.

## Manuscript Change

`paper/scis2026/main.tex` now references Fig. 3 only for the model-level
summary and states that detailed model-level shares are retained in the
reproducibility artifacts.

## Remaining Phase 15 Checks

- Decide whether `table4_entropy_sensitivity` remains in the main text.
- Shorten figure captions if needed after final page-budget review.
- Verify that every included figure/table is referenced in the text.
- Compile and inspect the PDF after any additional figure/table changes.

