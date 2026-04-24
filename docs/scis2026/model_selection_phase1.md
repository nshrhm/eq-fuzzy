# SCIS 2026 Phase 1 Model Selection Rationale

This document records why models were selected or excluded after the SCIS 2026
Phase 1 model capability smoke test. It is intended to support later
methods-section writing and reviewer response, not to claim benchmark
superiority.

## Selection Criteria

The SCIS main panel is designed for a conference-scale method and analysis
paper on persona-temperature factorial deconfounding. The model panel should be
large enough to avoid a single-vendor anecdote, but small enough to keep a
fully crossed design feasible.

Primary criteria:

1. Contemporary model family available through the same OpenRouter execution
   surface.
2. Acceptance of all four SCIS API temperatures: `0.1`, `0.4`, `0.7`, `0.9`.
3. Stable response-schema behavior under the SCIS nested `scores` / `reasons`
   schema.
4. Fixed stochasticity and reasoning controls recorded in the manifest.
5. Vendor/ecosystem diversity where possible.
6. Feasible cost and latency for sanity, pilot, and main runs.

The Phase 1 gate is operational rather than inferential. Passing the gate means
that a model can be run in the SCIS design; it does not mean that the model is
better, more valid, or more human-aligned.

## Methods-Ready Selection Procedure

The model panel was selected in three steps:

1. Candidate models were identified from contemporary OpenRouter-accessible
   model families, prioritizing provider/ecosystem diversity and feasibility
   for a fully crossed SCIS design.
2. Each candidate was tested with the same minimal SCIS smoke prompt at four
   API-level temperature values: `0.1`, `0.4`, `0.7`, and `0.9`.
3. Models were eligible for the main panel only if all four requests completed
   and returned the required nested `scores` / `reasons` JSON schema.

The first pass yielded five main-panel models and one passed reserve
(`anthropic/claude-haiku-4.5`). A follow-up Meta/Llama smoke test was then run
because a Meta/Llama-family model would improve ecosystem diversity. Since
`meta-llama/llama-4-maverick` passed the same gate, it replaced
`anthropic/claude-haiku-4.5` in the final main panel.

Final selected panel for Phase 2 and later SCIS runs:

- `openai/gpt-5.4`
- `anthropic/claude-sonnet-4.5`
- `google/gemini-2.5-pro`
- `x-ai/grok-4.20`
- `deepseek/deepseek-v3.2`
- `meta-llama/llama-4-maverick`

## Selected Main Panel

| Model | Role in panel | Phase 1 result | Rationale |
|---|---|---:|---|
| `openai/gpt-5.4` | OpenAI frontier reference | pass | Contemporary OpenAI frontier anchor with long context and strong instruction-following positioning. |
| `anthropic/claude-sonnet-4.5` | Anthropic frontier reference | pass | Strong Anthropic reference model; useful as a second major frontier vendor. |
| `google/gemini-2.5-pro` | Google frontier reference | pass | Google-family frontier model with explicit thinking/reasoning mode recorded in the manifest. |
| `x-ai/grok-4.20` | xAI flagship-current reference | pass | Adds a non-OpenAI, non-Anthropic, non-Google commercial ecosystem and passed the strict structured-output gate. |
| `deepseek/deepseek-v3.2` | Efficient high-end reference | pass | Adds a lower-cost high-end model family and reduces the risk that the panel is only expensive proprietary frontier models. |
| `meta-llama/llama-4-maverick` | Meta/Llama open-available candidate | pass | Added after Phase 1b because it passed the same gate and improves provider/ecosystem diversity. |

## Excluded Candidates

| Model | Intended role | Phase 1 result | Reason for exclusion |
|---|---|---:|---|
| `qwen/qwen3.6-plus` | Efficient high-end / ecosystem-diversity candidate | fail | Accepted the requests but did not preserve the required nested `scores` / `reasons` response schema at any tested temperature. |
| `openai/gpt-5-mini` | Budget OpenAI substitute | fail | The tested OpenRouter route rejected disabled reasoning with HTTP 400 at all four temperatures. |

`qwen/qwen3.6-plus` remains scientifically interesting because it would have
improved ecosystem diversity and cost balance. It should not enter the SCIS
main panel under the current route/mode because schema noncompliance would
confound model behavior with parser/format instability.

`openai/gpt-5-mini` can be retested later under a fixed mandatory-reasoning
mode if an OpenAI budget model is needed. It should not be used in the first
SCIS main panel because the Phase 1 gate was defined around fixed, disabled or
excluded reasoning where possible.

## Passed Reserve Candidates

| Model | Phase | Status | Reason |
|---|---|---|---|
| `anthropic/claude-haiku-4.5` | Phase 1 reserve smoke test | passed reserve | Passed the operational gate, but was replaced by Llama 4 Maverick to improve ecosystem diversity. |
| `meta-llama/llama-4-scout` | Phase 1b Llama smoke test | passed reserve | Passed the operational gate, but Maverick is the stronger primary Meta/Llama candidate. |

## Suitability Assessment

The final six-model panel is suitable for the SCIS conference paper if the
paper frames the panel as a selected contemporary API-model panel, not as a
complete benchmark of all major LLM families.

Strengths:

- Covers six provider ecosystems: OpenAI, Anthropic, Google, xAI, DeepSeek, and
  Meta/Llama.
- Includes multiple high-capability frontier or flagship models.
- Includes a lower-cost high-end tier through DeepSeek V3.2 and an
  open-available Meta/Llama-family model.
- Every selected model passed the same temperature and structured-output gate.
- The panel is feasible for the planned 6-model main run:
  `6 models x 3 texts x 16 persona-temperature cells x 5 repeats = 1440 trials`.

Limitations to disclose:

- The panel is API-route-specific and OpenRouter-mediated; it is not a claim
  about native provider APIs in general.
- Claude Haiku 4.5 passed the gate but was moved to reserve status after Llama
  4 Maverick passed Phase 1b. This improves provider balance but removes the
  original budget Anthropic contrast from the main panel.
- Qwen would have improved ecosystem diversity, but it failed the strict schema
  gate. Excluding it is an operational reproducibility decision, not a quality
  judgment about Qwen as a model family.
- Phase 1 confirms API-temperature acceptance and response-schema stability; it
  does not prove that temperature has equal behavioral meaning across models.

Recommended paper wording:

> We used a six-model contemporary API panel selected by a pre-registered
> operational gate: each model had to accept all four decoding temperatures as
> API parameters and return the specified nested JSON schema in a smoke test.
> The panel was chosen for vendor/ecosystem diversity, feasibility in a fully
> crossed design, and structured-output reliability rather than for benchmark
> completeness.

Avoid wording such as:

- "representative of all current LLMs"
- "best available models"
- "proves cross-provider temperature equivalence"
- "excludes failed models because they are lower quality"

## Public Model Metadata Checked

The local Phase 1 run is the controlling evidence for SCIS eligibility. Public
model pages were checked only to support methods-section descriptions of model
recency, context scale, and cost tier.

Checked OpenRouter pages:

- `openai/gpt-5.4`: https://openrouter.ai/models/openai/gpt-5.4
- `anthropic/claude-sonnet-4.5`: https://openrouter.ai/anthropic/claude-sonnet-4.5
- `google/gemini-2.5-pro`: https://openrouter.ai/google/gemini-2.5-pro
- `x-ai/grok-4.20`: https://openrouter.ai/x-ai/grok-4.20
- `deepseek/deepseek-v3.2`: https://openrouter.ai/deepseek/deepseek-v3.2
- `anthropic/claude-haiku-4.5`: https://openrouter.ai/anthropic/claude-haiku-4.5
- `qwen/qwen3.6-plus`: https://openrouter.ai/qwen/qwen3.6-plus
- `openai/gpt-5-mini`: https://openrouter.ai/openai/gpt-5-mini
- `meta-llama/llama-4-maverick`: https://openrouter.ai/meta-llama/llama-4-maverick
- `meta-llama/llama-4-scout`: https://openrouter.ai/meta-llama/llama-4-scout

Accessed for planning on 2026-04-25.
