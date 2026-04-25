# Phase 19: Submission QA

## Purpose

Phase 19 performs a submission-oriented QA pass after the manuscript reached a
six-page full-paper draft.

## Checks Performed

Build command:

```bash
cd paper/scis2026
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

PDF metadata:

- pages: 6
- page size: letter
- encrypted: no
- PDF version: 1.5

Log scan:

- undefined references: none detected
- citation warnings: none detected
- LaTeX errors: none detected
- overfull boxes: none detected
- underfull boxes: none detected

Font check:

- `pdffonts paper/scis2026/main.pdf`
- all listed fonts are Type 1
- all listed fonts are embedded and subsetted

## Manuscript QA Edits

Updated `paper/scis2026/main.tex` so all main-text figure/table assets are
explicitly referenced in prose:

- Fig. 1a prior diagonal design
- Fig. 1b factorial design
- Table 1 validity
- Table 2 bootstrap CI summary
- Fig. 2a entropy heatmap
- Fig. 2b score heatmap
- Fig. 3 model-level score/entropy interaction heatmap
- Table 4 entropy sensitivity
- experimental panel table added in Phase 18

## Remaining Human Checks

Before final submission:

- visually inspect the final PDF in a PDF viewer;
- confirm whether the final page needs manual column balancing;
- verify bibliography typography for DOI strings containing underscores;
- confirm final author affiliations and emails;
- perform final English proofreading.
