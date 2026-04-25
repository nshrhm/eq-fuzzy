# SCIS 2026 Phase 6 Main Run

This note records the Phase 6 main-run procedure and operational gate. The main
run is the minimum conference-paper evidence base for the locked SCIS 2026
factorial design.

## Design

The locked main run is:

```text
6 models x 3 texts x 16 persona-temperature conditions x 5 repeats = 1440 trials
```

The six models are the models in `configs/scis/main_panel_v2.yaml`:

- `openai/gpt-5.4`
- `anthropic/claude-sonnet-4.5`
- `google/gemini-2.5-pro`
- `x-ai/grok-4.20`
- `deepseek/deepseek-v3.2`
- `meta-llama/llama-4-maverick`

The texts are `T1`, `T2`, and `T3`.

## Commands

Build or refresh the main manifest:

```bash
python scripts/scis2026/build_factorial_manifest.py --stage main
```

Optional one-request dry run:

```bash
python scripts/scis2026/run_factorial.py \
  --manifest runs/scis2026/scis2026_factorial_v1_main_manifest_v1/manifest.csv \
  --output-jsonl runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw_dry_run.jsonl \
  --limit 1 \
  --dry-run
```

Run the full main manifest:

```bash
python scripts/scis2026/run_factorial.py \
  --manifest runs/scis2026/scis2026_factorial_v1_main_manifest_v1/manifest.csv \
  --output-jsonl runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw.jsonl
```

Summarize:

```bash
python scripts/scis2026/summarize_factorial_run.py \
  --input-jsonl runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw.jsonl \
  --summary-json runs/scis2026/scis2026_factorial_v1_main_manifest_v1/summary.json \
  --cell-csv runs/scis2026/scis2026_factorial_v1_main_manifest_v1/cell_summary.csv
```

Check the main gate:

```bash
python scripts/scis2026/check_main_run.py
```

If the main run contains only a small number of invalid rows, retry only those
rows:

```bash
python scripts/scis2026/build_factorial_retry_manifest.py

python scripts/scis2026/run_factorial.py \
  --manifest runs/scis2026/scis2026_factorial_v1_main_manifest_v1/retry_failed_v1_manifest.csv \
  --output-jsonl runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw_retry_failed_v1.jsonl

python scripts/scis2026/merge_factorial_retry.py
```

The merge step writes `raw_repaired.jsonl` and leaves the original `raw.jsonl`
unchanged.

After the main gate passes, create analysis-ready outputs with:

```bash
python scripts/scis2026/analyze_factorial_scores.py \
  --input-jsonl runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw.jsonl \
  --output-dir artifacts/scis2026/main_analysis_v1 \
  --membership-config configs/scis/fuzzy_membership_v1.yaml \
  --expected-responses 1440 \
  --expected-emotion-rows 5760 \
  --expected-decomposition-units 72
```

## Gate

Phase 6 passes the operational gate if:

- `n_records = 1440`
- `n_models = 6`
- `n_cells = 288`
- overall valid-output rate is at least `0.95`
- `validation_errors` is empty
- `error_status_codes` is empty
- every cell has exactly `5` attempts
- every cell has at least `4` valid repeats
- `cell_summary.csv` exists

Before committing raw outputs, also check:

```bash
rg -n "user_[A-Za-z0-9]{10,}|Bearer [A-Za-z0-9]|sk-[A-Za-z0-9]|OPENROUTER_API_KEY=" \
  runs/scis2026/scis2026_factorial_v1_main_manifest_v1
```

No matches are expected. Provider `user_id` values should be redacted by the
runner if they appear in error responses.
