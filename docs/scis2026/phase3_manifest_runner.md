# SCIS 2026 Phase 3 Manifest and Runner

This note records the Phase 3 implementation entry points for building and
running SCIS factorial manifests. It is an implementation note, not evidence of
completed sanity, pilot, or main experiments.

## Scripts

- Build manifests: `scripts/scis2026/build_factorial_manifest.py`
- Run manifests: `scripts/scis2026/run_factorial.py`
- Summarize raw JSONL: `scripts/scis2026/summarize_factorial_run.py`

## Build Manifests

Sanity stage:

```bash
python scripts/scis2026/build_factorial_manifest.py --stage sanity
```

Pilot stage:

```bash
python scripts/scis2026/build_factorial_manifest.py --stage pilot
```

Main stage:

```bash
python scripts/scis2026/build_factorial_manifest.py --stage main
```

Default outputs are written under:

```text
runs/scis2026/scis2026_factorial_v1_<stage>_manifest_v1/
```

## Preview a Request

```bash
python scripts/scis2026/run_factorial.py \
  --manifest runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/manifest.csv \
  --output-jsonl runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/raw.jsonl \
  --limit 1 \
  --dry-run
```

The dry run prints the request payload without calling OpenRouter.

## Run

After setting `OPENROUTER_API_KEY`, run:

```bash
python scripts/scis2026/run_factorial.py \
  --manifest runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/manifest.csv \
  --output-jsonl runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/raw.jsonl
```

## Summarize

```bash
python scripts/scis2026/summarize_factorial_run.py \
  --input-jsonl runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/raw.jsonl \
  --summary-json runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/summary.json \
  --cell-csv runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/cell_summary.csv
```

## Invariants

- Raw outputs stay under `runs/scis2026/<run-id>/`.
- The request payload contains API-level `temperature`.
- The rendered prompt must not contain the forbidden term recorded in
  `configs/scis/factorial_v1.yaml`.
- Manifest rows preserve hashes for the factorial config, condition table,
  main panel, prompts, response schema, text registry, and persona registry.

## API Smoke Result

A one-request API smoke test was run against the sanity manifest:

```bash
python scripts/scis2026/build_factorial_manifest.py --stage sanity
python scripts/scis2026/run_factorial.py \
  --manifest runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/manifest.csv \
  --output-jsonl runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/raw_smoke_1.jsonl \
  --limit 1
python scripts/scis2026/summarize_factorial_run.py \
  --input-jsonl runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/raw_smoke_1.jsonl \
  --summary-json runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/summary_smoke_1.json \
  --cell-csv runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/cell_summary_smoke_1.csv
```

Observed result:

- model: `openai/gpt-5.4`
- story: `T1`
- condition: `C01`
- persona: `p1`
- API temperature: `0.1`
- valid response: yes
- summary valid rate: `1.0`
- prompt text contained the forbidden term: no
- parsed response preserved nested `scores` and `reasons`: yes

This confirms that the Phase 3 runner can execute a factorial manifest row via
the API. The full 96-request sanity run remains Phase 4 work.
