# ICICIC 2026 external mini-comparison provenance

This external mini comparison is descriptive only.

## Curated public items

- `eq_bench_v2`: 12 items from EQ-Bench v2 qid 1-12.
- `emobench_ea_en`: 6 English Emotion Application items from EmoBench EA qid 1-6.
- `emobench_eu_en`: 6 English Emotion Understanding items from EmoBench EU qid 1-6.

The source repositories are MIT licensed:

- EQ-Bench: `https://github.com/EQ-bench/EQ-Bench/blob/main_v2_4/LICENSE`
- EmoBench: `https://github.com/Sahandfer/EmoBench/blob/master/LICENSE`

SECEU remains coverage-matrix-only in this phase because item reuse terms were
not treated as explicitly clear for a mini-run.

## Output interpretation

The analysis reports valid-output rate for all model/benchmark cells. EQ-Bench
rows use parsed fullscale item scores when the answer string contains the
required emotion-score profile. EmoBench rows use exact-match against the
benchmark answer label. These outputs must not be interpreted as universal
benchmark superiority or standalone human-validity evidence.
