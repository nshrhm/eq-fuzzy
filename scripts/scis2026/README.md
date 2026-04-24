# SCIS 2026 scripts

Canonical scripts for the SCIS 2026 workstream.

## Phase 1: temperature smoke test

Build the main-panel candidate manifest:

```bash
python scripts/scis2026/build_temperature_smoke_manifest.py
```

Preview the first OpenRouter request without calling the API:

```bash
python scripts/scis2026/run_temperature_smoke.py --limit 1 --dry-run
```

Run the manifest after setting `OPENROUTER_API_KEY`:

```bash
python scripts/scis2026/run_temperature_smoke.py
```

Summarize raw JSONL results:

```bash
python scripts/scis2026/summarize_temperature_smoke.py
```

Reserve or bridge candidates can be included explicitly:

```bash
python scripts/scis2026/build_temperature_smoke_manifest.py \
  --include-group main_panel_candidates \
  --include-group reserve_candidates \
  --include-group bridge_or_appendix_candidates
```

Meta/Llama candidates can be tested separately before panel lock:

```bash
python scripts/scis2026/build_temperature_smoke_manifest.py \
  --include-group llama_candidates \
  --output runs/scis2026/phase1b_llama_smoke_v1/manifest.csv
```

Temperature must remain an API/config parameter only. The runner checks that
the rendered SCIS prompt text does not contain the forbidden term before
sending requests.

## Phase 2: design lock validation

Validate the locked factorial design, prompt separation rule, and expected
trial counts:

```bash
python scripts/scis2026/validate_phase2_design.py
```
