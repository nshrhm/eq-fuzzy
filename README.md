# eq-fuzzy

Private monorepo for the JSPS KAKENHI-side **EQ-Fuzzy** research line on uncertainty-aware evaluation of LLM emotional intelligence.

This repository now covers three scientifically separate workstreams:

- **ICECCME 2026**: human-grounded multilingual pilot
- **SCIS 2026**: persona x temperature factorial deconfounding
- **ICICIC 2026**: benchmark positioning / matched comparison

The repository is shared because the implementation substrate is shared. The papers remain separate because the scientific claims are separate.

## Operating rule

**Share code, not claims.**

Shared infrastructure is encouraged when it supports reproducibility across the EQ-Fuzzy line:

- text and model registries
- prompt and response-schema infrastructure
- execution, retry, and provenance tooling
- parsing and validation
- alignment metrics, variance, fuzzy membership, and fuzzy entropy
- artifact regeneration for figures and tables

Shared novelty claims are not allowed. Each paper keeps its own main question, figure set, manuscript framing, discussion language, and submission-ready claims.

## Why these workstreams belong together

ICECCME, SCIS, and ICICIC all depend on the same benchmark substrate:

- literary text and translation provenance
- model panels and provider routing
- prompt templates and structured response schemas
- run manifests and normalized model-score tables
- metrics for human alignment, drift, validity, variance, and fuzzy behavior
- reproducible paper artifacts generated from the same audit trail

Keeping these pieces in one private monorepo reduces duplicated implementation work and makes it easier to trace results from raw outputs to paper figures without forcing the papers into one scientific story.

## What stays outside this repository

**SPReAD1000 stays separate.**

SPReAD1000 is an adjacent application / workflow PoC, not a workstream inside this benchmark monorepo. It is expected to have different assets and risks:

- annotation workflows
- review queues
- demo or UI layers
- expert-operation logs
- separate data-governance and deliverable requirements

SPReAD1000 may later reuse a small frozen utility package, vendored module, or extracted `eqf_core` component, but `eq-fuzzy` must not depend on SPReAD-specific workflow code, UI code, or annotation-ops logic.

## Workstream boundaries

| Workstream | Role | Main question | Not the claim |
|---|---|---|---|
| ICECCME 2026 | human-grounded multilingual pilot | Which current LLMs align best with Japanese human VAS references, and how robust is that alignment across EN/ZH? | full persona x temperature deconfounding |
| SCIS 2026 | factorial deconfounding | How much score variation is attributable to persona, temperature, and their interaction? | multilingual human-alignment ranking |
| ICICIC 2026 | benchmark positioning / matched comparison | What does EQ-Fuzzy capture beyond existing emotion benchmarks? | a rerun of ICECCME or SCIS |

## Current implementation status

The current working pipeline is still the ICECCME 2026 pipeline. This bootstrap does not move or rename it:

- `src/iceccme2026/` remains the working package.
- `paper/iceccme2026/` remains the working manuscript path.
- root-level commands in `main.py`, `run_openrouter_manifest.py`, and `scripts/*.py` remain the current runnable interface.
- `scripts/iceccme2026/` is the canonical home for ICECCME script implementations; root-level `scripts/*.py` files are compatibility wrappers.
- root-level `configs/*.yaml`, `prompts/*`, and `results/{csv,json,tables,figures}` are compatibility paths for the current pipeline.
- `results/iceccme2026/` is the canonical home for ICECCME result CSV/JSON/table/figure outputs.
- `data/iceccme2026/` is the canonical home for ICECCME data; root-level `data/derived_public`, `data/manifests`, `data/interim`, `data/raw_private`, and `data/results` are compatibility symlinks.
- SCIS and ICICIC directories are placeholders only until their real configs, prompts, and analysis code are designed.

Before SCIS or ICICIC work starts, path ownership is fixed in `docs/PATH_OWNERSHIP.md`. New generated outputs should use `runs/<workstream>/...` or `artifacts/<workstream>/...`; future SCIS and ICICIC code must not overwrite the existing ICECCME-compatible `results/*` outputs.

## Default current model panel for ICECCME (core 6)

- `openai/gpt-5.4`
- `anthropic/claude-sonnet-4.5`
- `google/gemini-2.5-pro`
- `x-ai/grok-4.20`
- `deepseek/deepseek-v3.2`
- `qwen/qwen3.6-plus`

See `docs/model_selection_openrouter_2026-04-17.md` for the rationale and reserve models.

## Important current ICECCME config files

- `configs/experiment.yaml` - default **primary neutral** run
- `configs/experiment_secondary_persona.yaml` - secondary persona sensitivity run
- `configs/models_default.yaml` - selected OpenRouter core-6 panel
- `configs/models_budget4.yaml` - smaller budget fallback panel
- `configs/texts_from_definitions.yaml` - source-of-truth text mapping from `definitions.py`
- `configs/personas_from_definitions.yaml` - original p1-p4 mapping from `definitions.py`
- `configs/personas_primary_neutral.yaml` - new p0 neutral persona for the main paper endpoint

These root-level files are compatibility symlinks. The canonical config locations are `configs/iceccme/` for ICECCME-specific experiment and paper settings, and `configs/shared/` for model/text/persona registries that can be reused by later workstreams.

## First commands to run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python main.py prepare-human   --input /absolute/path/to/文学短編作品.xlsx   --output-dir data/iceccme2026/derived_public

python main.py build-manifest   --config configs/iceccme/experiment.yaml   --models configs/shared/models_default.yaml   --output data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv

python main.py build-manifest   --config configs/iceccme/experiment_secondary_persona.yaml   --models configs/shared/models_default.yaml   --output data/iceccme2026/manifests/iceccme2026_secondary_persona_manifest.csv

python verify_results.py

# optional: normalize raw run outputs into the long-format file expected by score-alignment
python main.py normalize-model-scores   --input path/to/raw_outputs.jsonl   --manifest data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv   --join-on-order   --output data/iceccme2026/interim/model_scores.csv
```

## Prompt tooling

The root-level prompt files are compatibility symlinks. ICECCME prompt text lives in `prompts/iceccme/`, and the shared response schema lives in `prompts/shared/`.

Use the preview script before large runs:

```bash
python scripts/render_prompt_preview.py   --story-id T1   --persona-id p0   --language ja   --text-file data/iceccme2026/raw_private/texts/ja/T1.txt   --output T1_p0_ja_prompt.txt
```

## Paper artifact regeneration

After `results/iceccme2026/csv/ja_primary_ranking.csv` and `results/iceccme2026/csv/model_language_drift_vs_ja.csv` exist, regenerate Figure 2, Figure 3, and Table 2 with:

```bash
python scripts/plot_figure2_ja_ranking.py
python scripts/plot_figure3_cross_language_drift.py
python scripts/export_table2_primary.py
```

## Future directory stubs

The following directories are intentionally empty except for `.gitkeep` or a small README until the corresponding workstreams are ready:

- `configs/shared/`
- `configs/iceccme/`
- `configs/scis/`
- `configs/icicic/`
- `prompts/shared/`
- `prompts/iceccme/`
- `prompts/scis/`
- `prompts/icicic/`
- `src/core/`
- `scripts/iceccme2026/`
- `scripts/scis2026/`
- `scripts/icicic2026/`
- `data/iceccme2026/`
- `results/iceccme2026/`
- `paper/scis2026/`
- `paper/icicic2026/`
- `runs/iceccme/`
- `runs/scis/`
- `runs/icicic/`
- `artifacts/iceccme/`
- `artifacts/figures/`
- `artifacts/tables/`
- `artifacts/manuscripts/`

Do not add fake SCIS or ICICIC configs just to fill these directories.

## Next shared-core extraction targets

No large refactor is part of this bootstrap. The next conservative extraction candidates are:

- `src/iceccme2026/manifest.py` for shared manifest utilities
- `src/iceccme2026/metrics.py` for shared alignment and statistics utilities
- `src/iceccme2026/model_scores.py` for normalized score loading and validation
- generic pieces of `src/iceccme2026/reporting.py` and `src/iceccme2026/paper_exports.py`

Only extract code after a second workstream actually needs it and the behavior can be covered by tests.

## Monorepo docs

- `docs/WORKSTREAMS.md` - scientific separation of ICECCME, SCIS, and ICICIC
- `docs/MONOREPO_POLICY.md` - repository rules and SPReAD boundary
- `docs/MIGRATION_PLAN.md` - non-destructive migration sequence and shared-core targets
- `docs/PATH_OWNERSHIP.md` - ownership map for shared, ICECCME, SCIS, and ICICIC paths
- `docs/context/` - canonical context prompts for shared and per-workstream planning

## Archive note

The resent `jaciii_iihmsp2025.zip` still appears to contain directory entries only. The concrete reusable source in this update is therefore `external/jaciii_iihmsp2025/definitions.py`, which is also mirrored into `src/iceccme2026/source_of_truth.py` for easier downstream use.
