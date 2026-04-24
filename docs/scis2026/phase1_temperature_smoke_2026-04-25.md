# SCIS 2026 Phase 1 Temperature Smoke Test, 2026-04-25

This note records the first SCIS 2026 Phase 1 model capability smoke test. It
is a model-entry gate only, not evidence for the SCIS paper's substantive
factorial claims.

For model-selection rationale and reviewer-facing wording, see
`docs/scis2026/model_selection_phase1.md`.

## Run

Main-panel candidate run:

- Manifest: `runs/scis2026/phase1_temperature_smoke_v1/manifest.csv`
- Raw JSONL: `runs/scis2026/phase1_temperature_smoke_v1/raw.jsonl`
- Summary JSON: `runs/scis2026/phase1_temperature_smoke_v1/summary.json`
- Summary CSV: `runs/scis2026/phase1_temperature_smoke_v1/summary.csv`

Reserve-candidate run:

- Manifest: `runs/scis2026/phase1_temperature_smoke_reserve_v1/manifest.csv`
- Raw JSONL: `runs/scis2026/phase1_temperature_smoke_reserve_v1/raw.jsonl`
- Summary JSON: `runs/scis2026/phase1_temperature_smoke_reserve_v1/summary.json`
- Summary CSV: `runs/scis2026/phase1_temperature_smoke_reserve_v1/summary.csv`

- Prompt version: `prompts/scis/smoke_v1_system.md` and `prompts/scis/smoke_v1_user_template.md`
- Response schema: `prompts/shared/response_schema.json`
- Temperatures tested as API parameters only: `0.1`, `0.4`, `0.7`, `0.9`
- Prompt-temperature separation: the SCIS runner checks that the rendered prompt
  text does not contain the forbidden term before sending requests.

## Main-panel candidate result

| Model | Accepted temperatures | Structured response | Phase 1 gate |
|---|---:|---:|---:|
| `openai/gpt-5.4` | 4/4 | 4/4 | pass |
| `anthropic/claude-sonnet-4.5` | 4/4 | 4/4 | pass |
| `google/gemini-2.5-pro` | 4/4 | 4/4 | pass |
| `x-ai/grok-4.20` | 4/4 | 4/4 | pass |
| `deepseek/deepseek-v3.2` | 4/4 | 4/4 | pass |
| `qwen/qwen3.6-plus` | 0/4 under strict schema validation | 0/4 | fail |

## Reserve-candidate result

| Model | Accepted temperatures | Structured response | Phase 1 gate |
|---|---:|---:|---:|
| `anthropic/claude-haiku-4.5` | 4/4 | 4/4 | pass |
| `openai/gpt-5-mini` | 0/4 | 0/4 | fail |

## Qwen failure mode

`qwen/qwen3.6-plus` did not fail with an HTTP/API temperature rejection. It
returned JSON-like content at all four temperatures, but did not follow the
required nested response schema consistently:

- missing `scores`
- missing `reasons`
- scores emitted as top-level emotion fields or nested per-emotion objects
- reasons emitted as top-level `*_reason` fields or mixed with top-level scores

Because SCIS Phase 1 requires stable response-schema behavior, this model
should not enter the SCIS main panel in its current route/mode. It can remain a
stress-test or appendix candidate if useful.

## GPT-5 mini failure mode

`openai/gpt-5-mini` failed before schema validation. The OpenRouter route
returned HTTP 400 for all four temperatures:

- `Reasoning is mandatory for this endpoint and cannot be disabled.`

Because the smoke catalog tested the model under disabled reasoning, this route
does not pass the current SCIS Phase 1 main-panel gate. It can be retested later
under a fixed mandatory-reasoning mode if a reserve OpenAI model is needed, but
it should not displace a passing model for the first SCIS main panel.

## Decision

The Phase 1 passing SCIS main panel before Phase 1b was:

- `openai/gpt-5.4`
- `anthropic/claude-sonnet-4.5`
- `google/gemini-2.5-pro`
- `x-ai/grok-4.20`
- `deepseek/deepseek-v3.2`
- `anthropic/claude-haiku-4.5`

The excluded candidates from this gate are:

- `qwen/qwen3.6-plus`
- `openai/gpt-5-mini`

The next step is Phase 2: lock the factorial condition table and SCIS prompt
templates for the 4 x 4 persona-temperature design.

Update: Phase 1b subsequently tested Meta/Llama candidates. Llama 4 Maverick
passed and replaces Claude Haiku 4.5 in `configs/scis/main_panel_v2.yaml`.
