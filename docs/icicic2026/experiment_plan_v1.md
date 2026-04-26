# ICICIC 2026 experiment plan v1

ICICIC 2026 is the benchmark positioning / matched comparison workstream. The
main question is what EQ-Fuzzy adds beyond existing emotion and emotional
intelligence benchmarks, not whether EQ-Fuzzy replaces them.

## Locked design

- Comparison targets: EQ-Bench, EmoBench, and SECEU / Emotion Understanding.
- Main ICICIC language: English.
- Model panel: `configs/icicic/models_stable6_from_scis.yaml`.
- EQ-Fuzzy subset: `T1`, `T2`, `T3`; four emotions; 10 repetitions.
- Target modes: `reader_side` and `character_side`.
- Primary descriptors: valid-output rate, cell mean, within-cell SD/IQR,
  fuzzy entropy, profile entropy, and reader-vs-character target shift.

## Commands

```bash
python scripts/icicic2026/build_comparison_matrix.py
python scripts/icicic2026/build_matched_subset_manifest.py --stage sanity
python scripts/icicic2026/run_matched_subset.py --limit 1 --dry-run
python scripts/icicic2026/analyze_matched_subset.py \
  --input-jsonl runs/icicic2026/icicic2026_benchmark_positioning_v1_sanity/raw.jsonl
```

The main run manifest is built only after the sanity run passes:

```bash
python scripts/icicic2026/build_matched_subset_manifest.py --stage main
```

## Claim discipline

The ICICIC tables may describe uncertainty-aware, stability-oriented, and
target-controllable descriptors. They must not claim universal benchmark
superiority, standalone human validity, or SCIS-style persona-temperature
deconfounding.

External benchmark mini-comparison items must be manually curated from public
sources with clear reuse notes before `build_external_mini_manifest.py` is run.

## Comparator source anchors

- EQ-Bench arXiv: https://arxiv.org/abs/2312.06281
- EQ-Bench leaderboard: https://eqbench.com/eqbench-v2.html
- EmoBench ACL Anthology: https://aclanthology.org/2024.acl-long.326/
- SECEU / Emotion Understanding study: https://journals.sagepub.com/doi/10.1177/18344909231213958
