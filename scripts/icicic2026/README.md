# ICICIC 2026 scripts

Canonical scripts for the ICICIC 2026 benchmark-positioning / matched-comparison workstream.

## Comparison matrix

Build the benchmark coverage matrix:

```bash
python scripts/icicic2026/build_comparison_matrix.py
```

This writes CSV, LaTeX, and JSON summary outputs under
`artifacts/icicic2026/comparison_matrix_v1/`.

## EQ-Fuzzy matched subset

Build the sanity manifest:

```bash
python scripts/icicic2026/build_matched_subset_manifest.py --stage sanity
```

Preview the first OpenRouter request without calling the API:

```bash
python scripts/icicic2026/run_matched_subset.py --limit 1 --dry-run
```

After a completed raw JSONL run, analyze the matched subset:

```bash
python scripts/icicic2026/analyze_matched_subset.py \
  --input-jsonl runs/icicic2026/icicic2026_benchmark_positioning_v1_sanity/raw.jsonl
```

Build the main manifest after the sanity run passes:

```bash
python scripts/icicic2026/build_matched_subset_manifest.py --stage main
```

## External mini comparison

The external mini-comparison manifest is intentionally gated on a curated item
CSV with clear public-source and reuse notes. It does not create fake
EQ-Bench, EmoBench, or SECEU items.

```bash
python scripts/icicic2026/build_external_mini_manifest.py
```

If `configs/icicic/external_benchmark_items_v1.csv` is missing, the script
stops with an explicit error.

After curation and manifest generation, preview and run the external mini
comparison with:

```bash
python scripts/icicic2026/run_external_mini.py --limit 1 --dry-run
```

Summarize completed raw output with:

```bash
python scripts/icicic2026/analyze_external_mini.py
```
