# ICICIC 2026 reproducibility package v1

This note maps the ICICIC benchmark-positioning pipeline from manifests to
paper-facing artifacts. It records reproducibility structure only; it is not a
submission-ready claim document.

## Fixed inputs

- Design config: `configs/icicic/benchmark_positioning_v1.yaml`
- External mini-comparison config: `configs/icicic/external_mini_comparison_v1.yaml`
- Matched-subset prompts: `prompts/icicic/eq_fuzzy_matched_subset_*.md`
- Shared response schema: `prompts/shared/response_schema.json`
- Model panel: `configs/icicic/models_stable6_from_scis.yaml`
- Text registry: `configs/shared/texts_from_definitions.yaml`
- Text bodies: `data/catalogs/texts_private`

## Matched-subset chain

1. Build sanity manifest:
   `python scripts/icicic2026/build_matched_subset_manifest.py --stage sanity`
2. Preview request:
   `python scripts/icicic2026/run_matched_subset.py --limit 1 --dry-run`
3. Run sanity raw output:
   `runs/icicic2026/icicic2026_benchmark_positioning_v1_sanity/raw.jsonl`
4. Analyze raw output:
   `python scripts/icicic2026/analyze_matched_subset.py --input-jsonl <raw>`
5. Gate-check analysis:
   `python scripts/icicic2026/check_matched_subset_run.py --stage sanity`
6. Build and run retry manifest only for failed rows if needed:
   `python scripts/icicic2026/build_matched_subset_retry_manifest.py`

After sanity passes, repeat the same chain for the main manifest:
`runs/icicic2026/icicic2026_benchmark_positioning_v1_stable6_main/manifest.csv`.

## Paper artifact chain

- Tables:
  `python scripts/icicic2026/build_icicic_primary_tables.py`
- Figures:
  `python scripts/icicic2026/build_icicic_primary_figures.py`
- Manuscript scaffold:
  `paper/icicic2026/main.tex`

## External mini-comparison chain

`configs/icicic/external_benchmark_items_v1.csv` is intentionally empty until
public benchmark items are manually curated with clear source URLs and reuse
notes. The manifest builder must stop if this file has no curated rows.

## Claim discipline

ICICIC outputs may describe uncertainty-aware, stability-oriented, and
target-controllable descriptors. They must not claim universal benchmark
superiority, standalone human validity, or SCIS-style persona-temperature
deconfounding.
