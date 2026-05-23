# FSS 2026 paper

This directory is reserved for the FSS 2026 short-note manuscript:

**Membership Specification and Sensitivity Reporting for
Fuzzy-Entropy-Based LLM Emotion Scoring**

Japanese title:

**ファジィエントロピー型LLM感情評価におけるメンバシップ関数仕様と感度報告**

Keep manuscript claims scoped to:

- membership-function specification
- entropy-response reporting over the 0-100 score axis
- minimal sensitivity reporting across membership-function families
- reproducibility requirements for fuzzy-entropy descriptors

Do not use this manuscript directory for SCIS persona x temperature
deconfounding, ICECCME human-grounded multilingual ranking, ICICIC
benchmark-positioning claims, or target-shift analysis.

## Template

Official FSS2026 UTF-8 Linux LaTeX template:

https://soft-cr.org/fss/2026/files/FSS2026sample-LaTeX-win_utf8_linux.zip

The downloaded archive is kept under:

```text
paper/fss2026/template_reference/
```

The sample template uses pLaTeX with DVI-to-PDF conversion by `dvipdfmx`.
The sample source successfully produced `fss2026.dvi` with:

```bash
latexmk -pdfdvi -latex='platex -kanji=utf8 -interaction=nonstopmode -halt-on-error %O %S' -e '$dvipdf = "dvipdfmx %O -o %D %S";' fss2026.tex
```

In this local environment, the original sample's final PDF conversion failed
because the sample uses `sample.eps` and Ghostscript (`gs`) is not installed.
The FSS manuscript uses a PNG figure and is built with the same pLaTeX and
`dvipdfmx` engine path.

Build the FSS manuscript from this directory with:

```bash
latexmk -pdfdvi -latex='platex -kanji=utf8 -interaction=nonstopmode -halt-on-error %O %S' -e '$dvipdf = "dvipdfmx %O -o %D %S";' main.tex
```

Expected PDF:

```text
paper/fss2026/main.pdf
```
