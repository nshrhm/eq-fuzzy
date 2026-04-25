# SCIS Phase 12 Writing and Experiment-Improvement Roadmap

This document records the post-main-run roadmap for SCIS 2026. The main run has
already been completed; the next priority is to turn the current analysis into a
submission-ready manuscript while adding only those diagnostics that reduce
review risk.

## Guiding Policy

Do not expand the main experiment unless a concrete diagnostic reveals a
submission-blocking failure. The immediate goal is not to add more models,
texts, or repeats, but to make the completed factorial experiment readable,
reproducible, and defensible.

The core SCIS claim remains:

- persona and temperature were independently crossed;
- score-level effects are mainly persona-driven;
- normalized fuzzy entropy exposes stronger persona-temperature interaction
  patterns than mean score alone;
- membership-function dependence is handled as a sensitivity issue, not as the
  central novelty claim.

## Phase 12: Manuscript Structure Lock

Purpose: fix the manuscript layout and artifact selection before heavy prose
editing.

Tasks:

- confirm the split one-column versions of Fig. 1 and Fig. 2 in the IEEE
  two-column layout;
- keep full paired versions as tracked alternate artifacts, not as main-text
  figures;
- decide which generated tables remain in the main text and which become
  appendix or reproducibility artifacts;
- keep the main manuscript focused on validity, bootstrap effect summaries,
  representative heatmaps, model-level summaries, and membership sensitivity.

Exit criteria:

- `paper/scis2026/main.tex` compiles without missing references;
- the main figure/table set is fixed for the first full writing pass;
- `docs/scis2026/phase11_manuscript_selection.md` matches the manuscript.

## Phase 13: Result Narrative Draft

Purpose: align prose, tables, figures, and claims.

Tasks:

- refine Abstract, Introduction, Methods, Results, Discussion, and Conclusion;
- make every quantitative claim traceable to a table or figure;
- keep the language descriptive and factorial, not causal;
- explain why temperature is treated as a categorical experimental factor in
  the primary analysis;
- state that fuzzy entropy is a derived score-placement descriptor under a
  fixed membership specification.

Exit criteria:

- the manuscript can be read end to end as a coherent method/analysis paper;
- no result paragraph depends on an artifact excluded from the main text;
- limitations are explicit and not postponed to future work only.

## Phase 14: Reviewer-Risk Diagnostics

Purpose: add lightweight diagnostics that answer likely reviewer objections
without changing the main run design.

Priority diagnostics:

- main-run completeness, including the four retry rows and their successful
  replacement records;
- `sigmoid_s_v1` versus `legacy_linear_v1` sensitivity;
- leave-one-model-out or model-stratified checks to ensure one model does not
  dominate the main interpretation;
- story-stratified checks to ensure one text does not dominate the pattern;
- emotion-stratified checks to clarify whether entropy interaction is driven by
  anger, surprise, sadness, or interest;
- output-validity checks that malformed or retried responses are not
  concentrated in one condition.

Exit criteria:

- each diagnostic either supports the current main-run design or is explicitly
  documented as a limitation;
- no diagnostic requires changing the planned `r = 5` main-run design for the
  SCIS submission.

## Phase 15: Figure and Table Finalization

Purpose: make the paper assets readable under two-column constraints.

Tasks:

- verify all included figures at manuscript scale;
- shorten captions while preserving methodological meaning;
- avoid duplicating the same decomposition in multiple large tables;
- keep detailed point estimates and top-interaction cases as reproducibility or
  appendix candidates unless the page budget allows them.

Exit criteria:

- figures and tables are readable in the generated PDF;
- every figure/table is referenced in the text;
- no main-text table is present only because it was generated.

## Phase 16: Reproducibility Package

Purpose: make the analysis chain auditable.

Tasks:

- document the relationship between manifest, raw JSONL, retry JSONL, analysis
  tables, figures, and manuscript includes;
- record model IDs, prompt version, parser version, condition table version,
  membership family, and Hmax grid settings;
- make clear which raw files are immutable run records;
- ensure regenerated tables and figures are produced from canonical SCIS paths.

Exit criteria:

- a future reader can reproduce the main tables and figures from tracked code
  and recorded run artifacts;
- retry handling is explicit and not hidden inside downstream summaries.

## Phase 17: Submission Polish

Purpose: prepare the manuscript for submission.

Tasks:

- add final citations for persona prompting, LLM emotion evaluation, fuzzy
  membership functions, and entropy-style fuzzy descriptors;
- tighten the title, abstract, and contribution bullets;
- check IEEE formatting, column balance, figure resolution, and font embedding;
- remove or defer any claim that cannot be supported within the page budget.

Exit criteria:

- submission PDF compiles cleanly;
- page limit is satisfied;
- claims, artifacts, and limitations are aligned.

## Deferred Work

The following are journal-extension candidates, not SCIS submission blockers:

- increasing repeats from `r = 5` to `r = 10`;
- adding more model families;
- adding human-grounded validation;
- extending to multilingual texts;
- turning variance or dispersion into a co-primary endpoint.

