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

`configs/icicic/external_benchmark_items_v1.csv` contains manually curated
public items with source URLs and reuse notes:

- EQ-Bench v2 qid 1-12 from the official MIT-licensed EQ-Bench repository.
- EmoBench English EA qid 1-6 and EU qid 1-6 from the official MIT-licensed
  EmoBench repository.
- SECEU remains coverage-matrix-only unless item reuse terms are explicitly
  clear.

Build, preview, run, and analyze the external mini comparison with:

```bash
python scripts/icicic2026/build_external_mini_manifest.py
python scripts/icicic2026/run_external_mini.py --limit 1 --dry-run
python scripts/icicic2026/run_external_mini.py
python scripts/icicic2026/analyze_external_mini.py
```

The analysis reports native EQ-Bench fullscale item scores where parseable,
EmoBench exact-match rates, model/benchmark valid-output rates, and confidence.

## Claim discipline

ICICIC outputs may describe uncertainty-aware, stability-oriented, and
target-controllable descriptors. They must not claim universal benchmark
superiority, standalone human validity, or SCIS-style persona-temperature
deconfounding.
