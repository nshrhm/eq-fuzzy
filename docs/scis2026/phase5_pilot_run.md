# SCIS 2026 Phase 5 Pilot Run

This note records the Phase 5 pilot-run procedure and gate. The pilot run is
for feasibility, parser stability, and preliminary interaction estimability. It
should inform whether the locked design is viable for the main run, but it
should not be treated as the final SCIS evidence base.

## Design

The locked pilot run is:

```text
4 models x 3 texts x 16 persona-temperature conditions x 3 repeats = 576 trials
```

The four pilot models are the first four models in
`configs/scis/main_panel_v2.yaml`:

- `openai/gpt-5.4`
- `anthropic/claude-sonnet-4.5`
- `google/gemini-2.5-pro`
- `x-ai/grok-4.20`

The texts are `T1`, `T2`, and `T3`.

## Commands

Build or refresh the pilot manifest:

```bash
python scripts/scis2026/build_factorial_manifest.py --stage pilot
```

Optional one-request dry run:

```bash
python scripts/scis2026/run_factorial.py \
  --manifest runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1/manifest.csv \
  --output-jsonl runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1/raw_dry_run.jsonl \
  --limit 1 \
  --dry-run
```

Run the full pilot manifest:

```bash
python scripts/scis2026/run_factorial.py \
  --manifest runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1/manifest.csv \
  --output-jsonl runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1/raw.jsonl
```

Summarize:

```bash
python scripts/scis2026/summarize_factorial_run.py \
  --input-jsonl runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1/raw.jsonl \
  --summary-json runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1/summary.json \
  --cell-csv runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1/cell_summary.csv
```

Check the pilot gate:

```bash
python scripts/scis2026/check_pilot_run.py
```

## Gate

Phase 5 passes the operational gate if:

- `n_records = 576`
- `n_models = 4`
- `n_cells = 192`
- overall valid-output rate is at least `0.95`
- `validation_errors` is empty
- `error_status_codes` is empty
- every cell has exactly `3` attempts
- every cell has at least `2` valid repeats
- `cell_summary.csv` exists

Before committing raw outputs, also check:

```bash
rg -n "user_[A-Za-z0-9]{10,}|Bearer [A-Za-z0-9]|sk-[A-Za-z0-9]|OPENROUTER_API_KEY=" \
  runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1
```

No matches are expected. Provider `user_id` values should be redacted by the
runner if they appear in error responses.

## Decision Use

Use the pilot to decide whether the main run can proceed unchanged. The main
run should remain the primary conference-paper evidence base. If pilot failures
are concentrated in one model or condition, document the failure mode before
changing the panel, prompt, or repeat depth.

## Result

Phase 5 pilot passed on 2026-04-25.

Artifacts:

- `runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1/raw.jsonl`
- `runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1/summary.json`
- `runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1/cell_summary.csv`

Summary:

- `n_records = 576`
- `n_ok = 576`
- `n_failed = 0`
- `valid_rate = 1.0`
- `n_models = 4`
- `n_cells = 192`
- `validation_errors = []`
- `error_status_codes = []`

Model valid rates:

- `openai/gpt-5.4 = 1.0`
- `anthropic/claude-sonnet-4.5 = 1.0`
- `google/gemini-2.5-pro = 1.0`
- `x-ai/grok-4.20 = 1.0`

The sensitive-value scan returned no matches.
