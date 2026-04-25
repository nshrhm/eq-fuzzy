# SCIS Phase 12 Manuscript Structure Lock

This document records the first manuscript-structure lock after the main run,
primary tables, bootstrap intervals, and split manuscript figures were
generated.

## Current Manuscript State

Source:

- `paper/scis2026/main.tex`

Latest local compile check:

- command: `pdflatex -interaction=nonstopmode main.tex`
- output: `paper/scis2026/main.pdf`
- page count at lock time: 4 pages
- paper size: letter

This lock does not mean the prose is final. It fixes the first main-text
artifact set for the next writing pass.

## Main-Text Artifact Set

The manuscript currently includes the following generated artifacts:

1. `figure1a_prior_diagonal_design`
2. `figure1b_factorial_design`
3. `table1_run_validity`
4. `effect_summary_bootstrap_ci`
5. `figure2a_entropy_heatmap`
6. `figure2b_score_heatmap`
7. `table3_model_metric_summary`
8. `figure3_model_metric_interaction_heatmap`
9. `table4_entropy_sensitivity`

The selection matches `docs/scis2026/phase11_manuscript_selection.md`.

## Locked Decisions

- Use split one-column versions of Fig. 1 and Fig. 2 in the main text.
- Keep the paired full-width versions as tracked alternate artifacts for slides
  or later appendix formatting.
- Use the bootstrap CI table as the primary decomposition table.
- Keep point-estimate-only decomposition and top-interaction case tables out of
  the first main-paper layout.
- Keep the membership sensitivity table in the main text for now because it
  directly addresses a likely reviewer concern.

## Open Layout Questions

These should be revisited during Phase 15 figure and table finalization:

- whether `table3_model_metric_summary` and
  `figure3_model_metric_interaction_heatmap` are redundant;
- whether `table4_entropy_sensitivity` remains in the main text or moves to an
  appendix after the page limit is known;
- whether Fig. 1a and Fig. 1b should stay as separate figures or become
  subfigures if the final template supports readable subfigure labels;
- whether captions can be shortened without losing the design rationale.

## Next Phase

Proceed to Phase 13: Result Narrative Draft.

The next writing pass should align prose with the locked artifact set, tighten
the contribution framing, and avoid introducing claims that are not supported
by the included figures and tables.

