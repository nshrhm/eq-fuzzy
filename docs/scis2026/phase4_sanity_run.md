# SCIS 2026 Phase 4 Sanity Run

This note records the Phase 4 sanity-run procedure and gate. The sanity run is
for execution and parser stability only; it must not be used for substantive
SCIS inference.

## Design

The locked sanity run is:

```text
2 models x 1 text x 16 persona-temperature conditions x 3 repeats = 96 trials
```

The two models are the first two models in `configs/scis/main_panel_v2.yaml`:

- `openai/gpt-5.4`
- `anthropic/claude-sonnet-4.5`

The text is `T1`.

## Commands

Build or refresh the sanity manifest:

```bash
python scripts/scis2026/build_factorial_manifest.py --stage sanity
```

Run the full sanity manifest:

```bash
python scripts/scis2026/run_factorial.py \
  --manifest runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/manifest.csv \
  --output-jsonl runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/raw.jsonl
```

Summarize:

```bash
python scripts/scis2026/summarize_factorial_run.py \
  --input-jsonl runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/raw.jsonl \
  --summary-json runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/summary.json \
  --cell-csv runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/cell_summary.csv
```

Check the sanity gate:

```bash
python scripts/scis2026/check_sanity_run.py
```

## Gate

Phase 4 passes if:

- `n_records = 96`
- `n_models = 2`
- `n_cells = 32`
- overall valid-output rate is at least `0.95`
- `validation_errors` is empty
- `error_status_codes` is empty
- `cell_summary.csv` exists

Before committing raw outputs, also check:

```bash
rg -n "user_[A-Za-z0-9]{10,}|Bearer [A-Za-z0-9]|sk-[A-Za-z0-9]|OPENROUTER_API_KEY=" \
  runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1
```

No matches are expected. Provider `user_id` values should be redacted by the
runner if they appear in error responses.

## Result

Phase 4 sanity passed on 2026-04-25.

Artifacts:

- `runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/raw.jsonl`
- `runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/summary.json`
- `runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/cell_summary.csv`

Summary:

- `n_records = 96`
- `n_ok = 96`
- `n_failed = 0`
- `valid_rate = 1.0`
- `n_models = 2`
- `n_cells = 32`
- `validation_errors = []`
- `error_status_codes = []`

The sensitive-value scan returned no matches.
