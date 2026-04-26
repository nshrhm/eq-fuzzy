# ICICIC 2026 implementation plan v2

This plan extends the committed v1 benchmark-positioning implementation.
It keeps ICICIC centered on matched comparison and added descriptors, not on
ICECCME human alignment or SCIS persona-temperature deconfounding.

## Phase 1: matched-subset sanity gate

- Run the 4-row sanity manifest with `run_matched_subset.py`.
- Analyze raw JSONL with `analyze_matched_subset.py`.
- Gate the analysis with `check_matched_subset_run.py --stage sanity`.
- If only a small number of rows fail, build a retry manifest with
  `build_matched_subset_retry_manifest.py`.

## Phase 2: matched-subset main run

- Run the existing 240-row main manifest.
- Analyze into `artifacts/icicic2026/matched_subset_analysis_v1/`.
- Build manuscript-facing tables with `build_icicic_primary_tables.py`.
- Build figure candidates with `build_icicic_primary_figures.py`.

## Phase 3: external mini comparison

- Curate `configs/icicic/external_benchmark_items_v1.csv` manually from public
  sources with explicit reuse notes.
- Do not add fake items.
- Keep SECEU as coverage-matrix-only unless item reuse is clear.
- Use external mini outputs descriptively: native exact-match and valid-output
  rate only.

## Phase 4: manuscript scaffold

- Use `paper/icicic2026/main.tex` as the initial manuscript shell.
- Include only regenerated tables and figures from `artifacts/icicic2026/`.
- Keep all claim language bounded to benchmark positioning and added
  descriptors.
