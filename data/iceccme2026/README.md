# ICECCME 2026 data

Canonical home for ICECCME 2026 data files.

Layout:

- `derived_public/`: sanitized human reference outputs
- `manifests/`: ICECCME run manifests
- `interim/`: local intermediate files, ignored by default
- `raw_private/`: private source workbooks, text files, and raw model outputs, ignored by default except README files
- `results/`: data-side JSON summaries generated with ICECCME manifests

The root-level `data/derived_public`, `data/manifests`, `data/interim`, `data/raw_private`, and `data/results` paths are compatibility symlinks.
