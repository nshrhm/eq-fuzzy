# SCIS 2026 TODO

This TODO records the current SCIS 2026 planning conclusion in the
repository's canonical-path layout. It is a planning document, not evidence of
completed experiments, final claims, or accepted paper results.

## Paper Role

SCIS 2026 is planned as a method and analysis paper on persona-temperature
factorial deconfounding.

The central question is:

- How far can persona effects and temperature effects be separated in LLM-based
  fuzzy emotion scoring?

The paper should focus on factorial separation of:

- `score`
- `validity`
- `within-emotion variance`
- `fuzzy entropy`

For each metric, the analysis should distinguish:

- persona main effect
- temperature main effect
- persona x temperature interaction

Primary estimands should be defined before implementation. At minimum, compute
factorial effect components such as:

- `SS_persona`
- `SS_temperature`
- `SS_persona_x_temperature`

Derived separability summaries:

- `interaction_burden = SS_persona_x_temperature / (SS_persona + SS_temperature + SS_persona_x_temperature)`
- `separability_share = 1 - interaction_burden`

Low interaction burden supports practical separability. High interaction
burden means persona and temperature remain behaviorally entangled even after
experimental crossing.

## Scope

Include:

- fully crossed persona x temperature design
- mixed-effects, ANOVA-style summaries, and bootstrap confidence intervals
- interaction plots
- factorial heatmaps
- main-effect summary tables
- a representative model subset suitable for a conference-scale experiment

Exclude from the main paper:

- human-grounded validation as the primary claim
- multilingual robustness as the primary claim
- benchmark positioning as the primary claim
- annotation workflow or application proof-of-concept claims

## Design v1

Keep the main experiment comparable with the previous Mathematics paper while
changing the confounding structure.

Planned factors:

- 3 Japanese literary texts
- 4 emotion dimensions
- 4 personas
- temperatures: `0.1`, `0.4`, `0.7`, `0.9`
- fully crossed 4 x 4 persona-temperature conditions

Important separation rule:

- Temperature is set only as an API argument.
- Temperature must not be mentioned in the prompt text.
- Persona is expressed only through the interpretive stance in the prompt.

Minimum main run:

- 6 models x 3 texts x 16 conditions x 5 repeats = 1440 trials

Optional stretch run:

- 8 models x 3 texts x 16 conditions x 5 repeats = 1920 trials

Statistical-design note:

- Treat `r = 5` as viable for validity, score, entropy, and interaction
  screening.
- Treat within-emotion variance as secondary unless repeat depth is increased.
- If variance becomes co-primary, prefer increasing repeats to `r = 8` or
  `r = 10` before adding more models.

## Run Stages

1. Sanity run
   - 2 models x 1 text x 16 conditions x 3 repeats = 96 trials
   - Purpose: check parser stability and prompt-level separation.

2. Pilot run
   - 4 models x 3 texts x 16 conditions x 3 repeats = 576 trials
   - Purpose: check feasibility, precision, and whether interaction patterns
     are estimable.

3. Main run
   - 6 models x 3 texts x 16 conditions x 5 repeats = 1440 trials
   - Purpose: minimum submission-scale experiment.

If pilot confidence intervals are too wide, increase repeats selectively for
the affected model or metric rather than expanding every factor at once.

Pilot decision criteria:

- overall valid-output rate is at least 95%
- no main-panel model has systematic parsing failure
- every model-text-persona-temperature cell has enough valid repeats to compute
  means
- pilot residual variances support acceptable projected confidence intervals
  for the main run
- persona x temperature interaction is estimable without convergence problems
- leave-one-model-out summaries do not completely reverse the qualitative
  interpretation
- text effects do not force the paper to abandon a text-conditioned framing

## Candidate Model Panel

Policy decision:

- Use a contemporary model panel for the SCIS main experiment.
- Do not keep the previous paper's older model panel as the main panel.
- If continuity with the previous paper is needed, keep at most one older model
  as a bridge or appendix model.
- The main comparison with the previous paper should be design-based:
  diagonal-only bundled estimates versus full-factorial deconfounded estimates
  using the new SCIS data.

Candidate model families:

1. OpenAI GPT-5.2 or GPT-5.4 family, only if temperature can be varied under a
   fixed non-reasoning or equivalent setting.
2. Anthropic Claude 4 family.
3. Google Gemini 2.5 family.
4. DeepSeek current V3/V4 family.
5. Meta Llama 4 Maverick or another stable open-weight/open-available model.
6. xAI Grok 4 family or another contemporary non-OpenAI commercial model,
   only if temperature support is empirically confirmed.

Possible bridge or appendix candidates:

- `gpt-4o-mini`
- `claude-3-5-haiku-20241022`
- `gemini-2.0-flash`

Before implementation:

- Verify current provider IDs and OpenRouter IDs.
- Verify availability and temperature support.
- Verify whether any model has a known high malformed-data rate.

Temperature smoke-test gate:

- A model can enter the main panel only after it accepts all four temperature
  values: `0.1`, `0.4`, `0.7`, `0.9`.
- Temperature must be an API/config parameter only; it must not appear in the
  prompt text.
- Fix all other available stochasticity controls, such as `top_p`, seed,
  thinking budget, reasoning effort, or equivalent provider-specific settings.
- If a model supports temperature only under a specific mode, record that mode
  in the model catalog and use it consistently.
- If a model silently ignores temperature or rejects non-default temperature
  values, exclude it from the main SCIS panel.
- If a reasoning model supports no usable temperature control, use it only as a
  non-primary appendix comparison or exclude it.

Models with high parser failure or malformed-data rates should be kept out of
the main panel and, if useful, treated as appendix or stress-test material.

## Analysis TODO

Build emotion-level cell summaries before pooled interpretation. Treat model
and text as fixed effects in the primary analysis because the planned panel has
only six selected models and three selected texts. Random-effect models can be
used only as sensitivity analyses, with cautious language.

Temperature should be categorical in the primary analysis. Numeric or
polynomial temperature trends can be secondary analyses only.

Recommended primary analysis levels:

1. fixed-effect factorial analysis over the selected models and texts
2. model-stratified summaries
3. random-effect sensitivity analysis only if useful and stable

Recommended starting formulas after statistical review:

- Validity:
  - Whole-response validity:
    `logit(valid) ~ model + text + persona * temperature`
  - Per-emotion validity, if used:
    `logit(valid) ~ model + text + emotion + persona * temperature + (1|response_id)`
  - If invalid outputs are rare or concentrated, report Wilson intervals and
    consider Firth or Bayesian logistic regression as sensitivity analyses.

- Score:
  - Preferred joint model:
    `score ~ model * emotion + text * emotion + persona * temperature * emotion + (1|response_id)`
  - Simpler conference-paper fallback:
    fit one model per emotion with
    `score_e ~ model + text + persona * temperature`

- Entropy:
  - Per-score entropy model:
    `Hf ~ model * emotion + text * emotion + persona * temperature * emotion + (1|response_id)`
  - Cleaner trial-level fallback:
    `mean_Hf ~ model + text + persona * temperature`
  - Present entropy as a fuzzy-theoretic descriptor derived from score
    placement, not as evidence independent from score.

- Variance and dispersion:
  - Treat cell-level variance as secondary when `r = 5`.
  - Preferred heavy option: location-scale model with mean and residual
    variance modeled simultaneously.
  - Practical fallback: Brown-Forsythe-style dispersion outcome,
    `d = |score - median_cell|`, analyzed with
    `d ~ model + text + emotion + persona * temperature`.
  - If using `log(var)`, report zero-variance cells and pre-specify any
    offset for `log(var + c)`.

Add bootstrap confidence intervals for the fixed-effect summaries and main
effect-size table.

Primary uncertainty plan:

- Use a stratified within-cell bootstrap as the primary bootstrap.
- Keep model x text x persona x temperature cells fixed.
- Resample repeats within each cell.
- Preserve the four emotion scores from the same response as a block.
- Recompute estimands for each bootstrap sample.

Sensitivity uncertainty plan:

- Clustered bootstrap over models and texts can be added as a sensitivity
  analysis, but it should be labeled unstable because there are only six models
  and three texts.
- Use paired bootstrap for diagonal-only versus full-factorial comparisons.

## Main Figures and Tables

Planned main materials:

- Fig. 1: old diagonal persona-temperature bundle design vs new 4 x 4
  factorial design
- Fig. 2: model-specific interaction plots for representative outcomes
- Fig. 3: model x metric effect-size heatmap, using effect sizes rather than
  p-values
- Table 1: persona, temperature, interaction, interaction-burden, and
  separability-share summary with confidence intervals

Optional:

- Fig. 4: comparison between diagonal-only confounded estimates and
  deconfounded full-factorial estimates using the new data
- appendix table: invalid-output rates by model and condition

## Canonical Repository Tasks

Create only real planning and implementation files. Do not add fake outputs or
placeholder experimental claims.

Configuration and prompt tasks:

- `configs/scis/factorial_v1.yaml`
- `configs/scis/condition_table_v1.csv`
- `prompts/scis/factorial_v1_system.md`
- `prompts/scis/factorial_v1_user_template.md`

Implementation tasks:

- add SCIS-specific scripts under `scripts/scis2026/`
- add manifest generation for fully crossed persona-temperature conditions
- add runner support that records model ID, prompt version, parser version,
  schema version, text registry version, repeats, and commit hash
- keep raw outputs immutable under `runs/scis2026/<run-id>/`
- send accepted SCIS paper artifacts to `artifacts/scis2026/`
- use `artifacts/scratch/` only for temporary cross-workstream exploration

Data/output tasks:

- Decide whether `data/scis2026/` is needed before creating it.
- Decide whether `results/scis2026/` is needed before creating it.
- If either directory is added, update `docs/PATH_OWNERSHIP.md`.

Shared-code policy:

- Do not move ICECCME code into `src/core/` before SCIS has a real reuse need.
- Extract shared text registry, prompt schema, runner, parser, or fuzzy entropy
  code only when SCIS implementation proves the shared boundary.
- Preserve workstream ownership when extracting shared utilities.

## Development Roadmap

### Phase 0: Planning Lock

- Keep this TODO as the SCIS planning anchor.
- Decide whether `r = 5` remains the conference-paper repeat count.
- Treat `r = 10` as a journal-extension option unless variance becomes a
  co-primary SCIS outcome.
- Finalize the candidate model families only after temperature smoke tests.

### Phase 1: Model Capability Smoke Test

- Create a SCIS model-candidate catalog under `configs/scis/`.
- Add a small smoke-test manifest for candidate models and the four
  temperatures.
- Run a minimal prompt that exercises the expected response schema.
- Record, per model:
  - exact model ID
  - provider or OpenRouter route
  - accepted temperature values
  - required reasoning/thinking mode
  - structured-output behavior
  - malformed-output rate
  - cost and latency notes
- Promote only passing models to the main-panel config.

### Phase 2: Design and Prompt Lock

- Create `configs/scis/condition_table_v1.csv` with the fully crossed
  persona-temperature cells.
- Create `configs/scis/factorial_v1.yaml`.
- Create SCIS prompt templates under `prompts/scis/`.
- Verify that temperature is absent from prompt text.
- Verify that persona is encoded only as interpretive stance.
- Record prompt schema and response schema versions.

### Phase 3: Manifest and Runner Implementation

- Add SCIS-specific manifest generation under `scripts/scis2026/`.
- Add or adapt runner support for SCIS runs without writing to ICECCME paths.
- Store raw outputs under immutable `runs/scis2026/<run-id>/` directories.
- Record commit hash, model IDs, prompt version, parser version, schema
  version, text registry version, and repeat count in every run manifest.

### Phase 4: Sanity Run

- Run 2 models x 1 text x 16 conditions x 3 repeats.
- Check parser stability, valid-output rate, prompt leakage, and condition
  table correctness.
- Do not use the sanity run for inference.

### Phase 5: Pilot Run

- Run 4 models x 3 texts x 16 conditions x 3 repeats.
- Estimate expected main-run precision.
- Check whether interaction effects are estimable.
- Decide whether the main run can remain at `r = 5`.
- Replace failing models before the main run.

### Phase 6: Main Run

- Run 6 models x 3 texts x 16 conditions x 5 repeats.
- Keep raw outputs immutable.
- Generate analysis-ready tables under SCIS-owned output paths.
- Keep variance and dispersion secondary unless repeat depth is increased.

### Phase 7: Analysis and Paper Assets

- Compute fixed-effect factorial summaries.
- Compute interaction burden and separability share.
- Run stratified within-cell bootstrap.
- Produce the planned figures and tables under `artifacts/scis2026/`.
- Keep scratch experiments under `artifacts/scratch/`.

### Phase 8: Paper Draft

- Write the SCIS paper as a six-page method/analysis paper.
- Center the claim on factorial deconfounding and interaction burden.
- Present diagonal-only versus full-factorial comparison as design-induced
  aliasing, not as a claim that the previous paper was wrong.
- Keep journal-extension notes separate from the SCIS submission material.

## Do Not Do

- Do not reintroduce root compatibility wrappers.
- Do not write SCIS outputs into ICECCME directories.
- Do not overwrite ICECCME `results/`, `runs/`, `data/`, or `artifacts/`.
- Do not treat diagonal-only estimates as causal evidence.
- Do not claim universal causal persona or temperature effects.
- Do not claim that API temperature has the same behavioral meaning across all
  providers.
- Do not claim that three selected texts represent Japanese literature.
- Do not present fuzzy entropy as independent validation of emotional
  ambiguity.
- Do not make strong cell-level variance claims with `r = 5`.
- Do not make human validation, multilingual robustness, or benchmark
  positioning the main SCIS claim.
