# SCIS Phase 17 Submission Polish

This document records the initial submission-polish audit for the SCIS 2026
manuscript.

## Compile Check

Source:

- `paper/scis2026/main.tex`

Command:

```bash
cd paper/scis2026
pdflatex -interaction=nonstopmode main.tex
```

Observed result:

- PDF generated successfully.
- Output file: `paper/scis2026/main.pdf`
- Page count: 4 pages
- Paper size: letter
- PDF version: 1.5

The local environment prints `pyenv: cannot rehash` before LaTeX output. This
does not affect PDF generation.

## Warning Check

The current `main.log` was scanned for:

- `Warning`
- `undefined`
- `Undefined`
- `Citation`
- `Overfull`
- `Underfull`

No matches were found in the latest log scan.

## Font Check

Command:

```bash
pdffonts paper/scis2026/main.pdf
```

Observed result:

- All listed fonts are Type 1.
- All listed fonts are embedded.
- All listed fonts are subset.

This satisfies the current IEEEtran reminder about Type 1 fonts at this stage.

## Current Main-Text Artifact Set

The manuscript currently includes:

- `figure1a_prior_diagonal_design`
- `figure1b_factorial_design`
- `table1_run_validity`
- `effect_summary_bootstrap_ci`
- `figure2a_entropy_heatmap`
- `figure2b_score_heatmap`
- `figure3_model_metric_interaction_heatmap`
- `table4_entropy_sensitivity`

This matches the Phase 16 reproducibility map after the Phase 15 model-level
table decision.

## Remaining Submission-Polish Tasks

The manuscript is structurally compilable, but not submission-final. Remaining
tasks:

- add final references for LLM emotion evaluation, persona prompting,
  temperature/sampling behavior, and smooth membership-function design;
- tighten the Related Work section after references are selected;
- check the venue page limit and decide whether the current 4-page layout is
  acceptable or should be expanded with additional explanation;
- inspect the generated PDF visually for figure readability, caption length, and
  final-page column balance;
- decide whether the membership sensitivity table remains in the main text after
  final page-budget review;
- replace placeholder or internal-only funding/acknowledgment wording before
  submission if needed.

## Current Assessment

No compile, reference, font-embedding, or page-count blocker is visible in the
current local PDF. The next substantive polish task is citation completion and
Related Work tightening.

