# SCIS Phase 20 Reviewer Clarity Pass

This note records the reviewer-risk reduction pass applied after the manuscript
reached a stable six-page draft. The goal of this phase is not to add new
experiments, but to make the existing factorial evidence easier to read and
harder to misinterpret.

## Scope

This pass implements the following manuscript-level clarifications:

- clarify that the balanced decomposition is applied to score and entropy under
  the same persona-temperature cell geometry;
- state that repeat-level variability is summarized by within-cell bootstrap
  intervals rather than by an additional sum-of-squares component;
- state that interaction burden is not a global variance share over models,
  texts, emotions, repeats, or future provider versions;
- explain how to read the bootstrap confidence interval table, including the
  meaning of `n = 18`;
- replace internal metric labels with publication-facing labels such as
  `Score` and `Entropy H*`;
- clarify that representative heatmaps are illustrative cases and not panel
  averages;
- record the main collection window and keep exact provider identifiers,
  timestamps, prompt versions, parser versions, and manifest hashes in the
  reproducibility artifacts;
- state that a diagonal persona-temperature design cannot identify the
  persona-temperature interaction component.

The final reviewer follow-up added four more clarifications without changing
the experiment:

- define the structured-output validity gate in the Experiments section;
- list the main reproducibility artifacts retained outside the paper;
- add a Results guardrail that Table III describes within-subtable structure,
  not global variance over the full experiment;
- clarify Table IV notation for `Hmax` and `r`.

## Changed Artifacts

The pass updates the manuscript, table-generation scripts, and figure-generation
scripts:

- `paper/scis2026/main.tex`
- `scripts/scis2026/bootstrap_main_effects.py`
- `scripts/scis2026/build_primary_tables.py`
- `scripts/scis2026/build_primary_figures.py`
- `artifacts/scis2026/main_bootstrap_v1/effect_summary_bootstrap_ci.tex`
- `artifacts/scis2026/main_figures_v1/`
- `artifacts/scis2026/main_tables_v1/`

Generated table and figure captions now avoid internal variable names where
possible. The manuscript still keeps exact run details in reproducibility
artifacts rather than expanding provider-specific implementation details in the
main text.

## Verification

The verification gate for this phase was:

- regenerate affected table and figure snippets;
- compile `paper/scis2026/main.tex` twice with `pdflatex`;
- confirm the PDF remains six pages;
- confirm there are no undefined references, citation warnings, LaTeX errors,
  or overfull/underfull box warnings in `main.log`;
- confirm all PDF fonts are embedded Type 1 fonts.

Completed verification:

- `python -m py_compile scripts/scis2026/bootstrap_main_effects.py scripts/scis2026/build_primary_tables.py scripts/scis2026/build_primary_figures.py`
- `pdflatex -interaction=nonstopmode main.tex` twice from `paper/scis2026/`
- `pdfinfo paper/scis2026/main.pdf`: 6 pages, letter paper
- `pdffonts paper/scis2026/main.pdf`: all fonts Type 1 and embedded
- `rg "Warning|undefined|Overfull|Underfull|LaTeX Error|Citation.*undefined|Reference.*undefined" paper/scis2026/main.log`: no matches

## Remaining Human Checks

Before submission, manually inspect the final PDF for:

- two-column readability of Table III and Figs. 3--5;
- whether the final page uses the six-page limit without becoming visually
  crowded;
- English consistency of the new reviewer-clarity paragraphs;
- whether the exact collection-window wording should be kept in the main text
  or shortened in favor of artifact-only provenance.
