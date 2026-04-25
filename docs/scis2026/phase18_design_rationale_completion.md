# Phase 18: Design Rationale and Six-Page Completion Pass

## Purpose

Phase 18 expands the SCIS manuscript from a compact five-page draft into a
six-page full-paper draft while preserving the main scope:

- persona-temperature factorial deconfounding;
- score versus normalized fuzzy entropy separability;
- fixed-panel, design-conditional claims;
- no new experiments or untracked claims.

## Main Manuscript Changes

Updated `paper/scis2026/main.tex` with:

- a broader introduction paragraph explaining why prompt-side and decoding-side
  controls should not be bundled in LLM evaluation protocols;
- a `Design Rationale` subsection clarifying fixed model/text panels,
  categorical treatment of temperature, `r=5` repeat depth, immutable manifest
  rows, and targeted retry repair;
- a compact main-run experimental panel table;
- an expanded result interpretation paragraph explaining why score means and
  normalized fuzzy entropy reveal different separability profiles;
- a standalone `Discussion` section framing the paper as a design diagnostic
  rather than a model leaderboard;
- a standalone `Limitations and Extension` section documenting the
  design-conditional scope and journal-extension path.

## Verification

`pdflatex -interaction=nonstopmode main.tex` was run from `paper/scis2026`.

Current output:

- PDF length: 6 pages
- paper size: letter
- LaTeX warnings: none detected by log scan
- overfull / underfull boxes: none detected by log scan

## Remaining Polish

Before final submission:

- visually inspect the generated 6-page PDF;
- decide whether the final page should be column-balanced;
- verify final reference formatting for all bibliography entries;
- perform one final pass for title, abstract, contribution wording, and figure
  captions.
