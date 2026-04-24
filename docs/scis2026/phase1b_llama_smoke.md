# SCIS 2026 Phase 1b Llama Candidate Smoke Test

This note prepared the optional Phase 1b smoke test for Meta/Llama-family
candidates before locking the SCIS Phase 2 design. The run result is recorded
in `docs/scis2026/phase1b_llama_smoke_2026-04-25.md`.

## Motivation

The current Phase 1 main panel passed the operational temperature/schema gate,
but it includes two Anthropic models:

- `anthropic/claude-sonnet-4.5`
- `anthropic/claude-haiku-4.5`

This is acceptable for the conference-scale SCIS method paper, but a
Meta/Llama-family model would improve ecosystem diversity if it passes the same
gate. The intended replacement candidate is the reserve Anthropic slot, not
the frontier Anthropic Sonnet slot.

## Candidates

Primary candidate:

- `meta-llama/llama-4-maverick`

Backup candidate:

- `meta-llama/llama-4-scout`

Both are configured in `configs/scis/model_candidates_smoke_v1.yaml` under
`llama_candidates`.

## Gate

Use the same gate as Phase 1:

- accepts API temperatures `0.1`, `0.4`, `0.7`, `0.9`
- returns the expected nested `scores` / `reasons` response schema
- uses temperature only as an API/config parameter, never in prompt text
- records route, reasoning controls, prompt/schema hashes, and raw responses

## Commands

Build the Llama-only smoke manifest:

```bash
python scripts/scis2026/build_temperature_smoke_manifest.py \
  --include-group llama_candidates \
  --output runs/scis2026/phase1b_llama_smoke_v1/manifest.csv
```

Preview the first request without calling the API:

```bash
python scripts/scis2026/run_temperature_smoke.py \
  --manifest runs/scis2026/phase1b_llama_smoke_v1/manifest.csv \
  --output-jsonl runs/scis2026/phase1b_llama_smoke_v1/raw.jsonl \
  --limit 1 \
  --dry-run
```

Run the smoke test:

```bash
python scripts/scis2026/run_temperature_smoke.py \
  --manifest runs/scis2026/phase1b_llama_smoke_v1/manifest.csv \
  --output-jsonl runs/scis2026/phase1b_llama_smoke_v1/raw.jsonl
```

Summarize results:

```bash
python scripts/scis2026/summarize_temperature_smoke.py \
  --input-jsonl runs/scis2026/phase1b_llama_smoke_v1/raw.jsonl \
  --summary-json runs/scis2026/phase1b_llama_smoke_v1/summary.json \
  --summary-csv runs/scis2026/phase1b_llama_smoke_v1/summary.csv
```

## Decision Rule

If `meta-llama/llama-4-maverick` passes all four temperatures and the strict
schema gate, create a new `configs/scis/main_panel_v2.yaml` that replaces
`anthropic/claude-haiku-4.5` with `meta-llama/llama-4-maverick`.

If Maverick fails but `meta-llama/llama-4-scout` passes, evaluate whether Scout
is scientifically strong enough for the main panel or should remain an appendix
candidate. Do not automatically replace Haiku with Scout without recording the
reason.

If both Llama candidates fail, keep `configs/scis/main_panel_v1.yaml` and
record the Llama failure modes as Phase 1b exclusions.

## Paper-Framing Impact

If Maverick passes and replaces Haiku, the model panel can be described as a
six-ecosystem contemporary API panel:

- OpenAI
- Anthropic
- Google
- xAI
- DeepSeek
- Meta/Llama

This is stronger for reviewer-facing model-selection rationale than the current
five-ecosystem panel with two Anthropic models.

If the panel remains unchanged, the paper should keep the existing limitation:
Anthropic appears twice because the only passing reserve candidate was Claude
Haiku 4.5.

## Public Metadata Checked

The local smoke test remains the controlling eligibility evidence. Public
OpenRouter pages were checked only to identify candidate IDs and describe the
model family:

- `meta-llama/llama-4-maverick`: https://openrouter.ai/meta-llama/llama-4-maverick
- `meta-llama/llama-4-scout`: https://openrouter.ai/meta-llama/llama-4-scout
