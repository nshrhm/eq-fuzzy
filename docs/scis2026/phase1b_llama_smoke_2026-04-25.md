# SCIS 2026 Phase 1b Llama Smoke Test Result, 2026-04-25

This note records the optional Meta/Llama-family smoke test run before SCIS
Phase 2 design lock. It is a model-entry gate only, not evidence for the SCIS
paper's substantive factorial claims.

## Run

- Manifest: `runs/scis2026/phase1b_llama_smoke_v1/manifest.csv`
- Raw JSONL: `runs/scis2026/phase1b_llama_smoke_v1/raw.jsonl`
- Summary JSON: `runs/scis2026/phase1b_llama_smoke_v1/summary.json`
- Summary CSV: `runs/scis2026/phase1b_llama_smoke_v1/summary.csv`
- Prompt version: `prompts/scis/smoke_v1_system.md` and `prompts/scis/smoke_v1_user_template.md`
- Response schema: `prompts/shared/response_schema.json`
- Temperatures tested as API parameters only: `0.1`, `0.4`, `0.7`, `0.9`

## Result

| Model | Accepted temperatures | Structured response | Phase 1b gate |
|---|---:|---:|---:|
| `meta-llama/llama-4-maverick` | 4/4 | 4/4 | pass |
| `meta-llama/llama-4-scout` | 4/4 | 4/4 | pass |

Both tested Meta/Llama candidates passed the same temperature and nested
response-schema gate used in Phase 1.

## Decision

Adopt `meta-llama/llama-4-maverick` into the SCIS main panel and move
`anthropic/claude-haiku-4.5` to passed-reserve status.

Rationale:

- `meta-llama/llama-4-maverick` passed the same 4-temperature, strict-schema
  gate as all other main-panel models.
- Replacing Haiku with Maverick improves provider/ecosystem diversity.
- The resulting main panel covers OpenAI, Anthropic, Google, xAI, DeepSeek, and
  Meta/Llama.
- `anthropic/claude-haiku-4.5` remains useful as a passed reserve candidate.
- `meta-llama/llama-4-scout` passed but remains a backup because Maverick is the
  stronger primary Meta/Llama candidate for the main panel.

The panel selected for Phase 2 is now `configs/scis/main_panel_v2.yaml`.
