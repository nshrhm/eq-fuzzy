# Shared Private Text Inputs

This is the canonical local directory for validated EQ-Fuzzy text bodies reused
across ICECCME, SCIS, and ICICIC.

The text bodies themselves are private local inputs and remain untracked. The
tracked metadata lives in:

- `configs/shared/texts_from_definitions.yaml`
- `data/catalogs/text_catalog.csv`

Expected layout:

- `ja/T1.txt`, `ja/T2.txt`, `ja/T3.txt`
- `en/T1.txt`, `en/T2.txt`, `en/T3.txt`
- `zh/T1.txt`, `zh/T2.txt`, `zh/T3.txt`

The previous ICECCME-local directory,
`data/iceccme2026/raw_private/texts`, is a legacy alias only. It should contain
no text bodies in new checkouts.
