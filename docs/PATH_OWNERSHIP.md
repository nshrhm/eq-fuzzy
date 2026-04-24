# Path ownership

This document fixes the repository boundaries before SCIS 2026 and ICICIC 2026 work starts.

The migration policy is compatibility-first: the current ICECCME 2026 pipeline remains runnable from the existing root-level commands and paths.

## Ownership classes

| Class | Meaning |
|---|---|
| `shared` | Reusable implementation substrate that does not encode a paper-specific claim. |
| `iceccme` | ICECCME 2026 experiment, manuscript, generated paper assets, and compatibility paths. |
| `scis` | SCIS 2026 experiment, manuscript, and generated assets. Placeholder only for now. |
| `icicic` | ICICIC 2026 experiment, manuscript, and generated assets. Placeholder only for now. |

## Current compatibility paths

These paths remain valid for the current ICECCME 2026 workflow. Do not move them until wrappers and tests are in place.

| Path | Current owner | Notes |
|---|---|---|
| `main.py` | `iceccme` compatibility | Root CLI for the current ICECCME pipeline. |
| `run_openrouter_manifest.py` | `iceccme` compatibility | Current OpenRouter runner. |
| `scripts/*.py` | `iceccme` compatibility | Root-level wrappers for existing figure, table, prompt-preview, and helper commands. |
| `scripts/iceccme2026/` | `iceccme` | Canonical home for ICECCME script implementations. |
| `src/iceccme2026/` | `iceccme` | Working implementation package. |
| `paper/iceccme2026/` | `iceccme` | Manuscript source and submission-specific assets. |
| root-level ICECCME guide docs | deprecated compatibility location | ICECCME guides now belong under `docs/iceccme2026/`; do not add new workstream-specific docs at the repository root. |
| `configs/*.yaml` | compatibility symlinks | Root-level links preserving current commands while canonical configs live under `configs/iceccme/` and `configs/shared/`. |
| `prompts/*.md`, `prompts/*.json` | compatibility symlinks | Root-level links preserving current manifests and runner commands while canonical prompt assets live under `prompts/iceccme/` and `prompts/shared/`. |
| `results/{csv,json,tables,figures}` | compatibility symlinks | Root-level links preserving current commands while canonical ICECCME results live under `results/iceccme2026/`. |
| `data/derived_public`, `data/manifests`, `data/interim`, `data/raw_private`, `data/results` | compatibility symlinks | Root-level links preserving current commands while canonical ICECCME data lives under `data/iceccme2026/`. |

## Future canonical paths

New work should use these paths once each workstream has a real design.

| Path | Owner | Rule |
|---|---|---|
| `src/core/` | `shared` | Future shared utilities only after a second workstream needs them. |
| `configs/shared/` | `shared` | Shared model, text, and persona registry/config fragments, not paper-specific experiment plans. |
| `prompts/shared/` | `shared` | Shared schemas or prompt fragments only when they are claim-neutral. |
| `data/catalogs/` | `shared` | Text, persona, and model catalogs with provenance. |
| `configs/iceccme/` | `iceccme` | Canonical ICECCME experiment and paper configs; root configs remain compatibility symlinks. |
| `prompts/iceccme/` | `iceccme` | Canonical ICECCME prompt text; root prompts remain compatibility symlinks. |
| `scripts/iceccme2026/` | `iceccme` | Canonical ICECCME script implementations; root scripts remain compatibility wrappers. |
| `data/iceccme2026/` | `iceccme` | Canonical ICECCME derived data, manifests, interim files, raw-private local data, and data-side summaries. |
| `results/iceccme2026/` | `iceccme` | Canonical ICECCME result CSV/JSON/table/figure outputs. |
| `runs/iceccme/` | `iceccme` | New ICECCME run outputs and logs. |
| `artifacts/iceccme2026/` | `iceccme` | New ICECCME generated figures, tables, and manuscript exports. |
| `snapshots/iceccme2026/` | `iceccme` | Frozen ICECCME run states, repair checkpoints, and generated-output snapshots. |
| `docs/iceccme2026/` | `iceccme` | ICECCME run guides, output inventories, reproducibility notes, model-selection notes, and paper-planning notes. |
| `artifacts/figures/`, `artifacts/tables/`, `artifacts/manuscripts/` | deprecated compatibility placeholders | Do not add new workstream outputs here. |
| `configs/scis/` | `scis` | Real SCIS configs only; no placeholder experiment YAML. |
| `prompts/scis/` | `scis` | Real SCIS prompts only; no fake prompt variants. |
| `paper/scis2026/` | `scis` | SCIS manuscript source. |
| `scripts/scis2026/` | `scis` | SCIS command-line scripts. Placeholder only for now. |
| `runs/scis/` | `scis` | SCIS run outputs and logs. |
| `artifacts/scis2026/` | `scis` | SCIS generated artifacts. Placeholder only for now. |
| `snapshots/scis2026/` | `scis` | SCIS frozen run states. Placeholder only for now. |
| `docs/scis2026/` | `scis` | SCIS planning and operational notes. Placeholder only for now. |
| `configs/icicic/` | `icicic` | Real ICICIC configs only; no placeholder experiment YAML. |
| `prompts/icicic/` | `icicic` | Real ICICIC prompts only; no fake prompt variants. |
| `paper/icicic2026/` | `icicic` | ICICIC manuscript source. |
| `scripts/icicic2026/` | `icicic` | ICICIC command-line scripts. Placeholder only for now. |
| `runs/icicic/` | `icicic` | ICICIC run outputs and logs. |
| `artifacts/icicic2026/` | `icicic` | ICICIC generated artifacts. Placeholder only for now. |
| `snapshots/icicic2026/` | `icicic` | ICICIC frozen run states. Placeholder only for now. |
| `docs/icicic2026/` | `icicic` | ICICIC planning and operational notes. Placeholder only for now. |

## Sharing rule

Share code, not claims.

Code may move from `src/iceccme2026/` to `src/core/` only when:

- SCIS or ICICIC actually needs the behavior.
- The extracted code has tests.
- ICECCME imports continue to work through compatibility wrappers.
- The extracted code does not contain manuscript framing, captions, or novelty claims.

Good candidates for later extraction are generic parts of manifest construction, score normalization, alignment metrics, correlation helpers, drift metrics, and table/figure utilities that are independent of ICECCME paper claims.

## Artifact isolation rule

New generated outputs should go under `runs/<workstream>/...` or `artifacts/<workstream>/...`.

The existing `results/` directory remains an ICECCME compatibility output location. Future SCIS and ICICIC code must not overwrite `results/*` unless a compatibility wrapper explicitly documents why.

## Documentation isolation rule

Repository-level policies, ownership maps, migration notes, and cross-workstream context prompts may live directly under `docs/`.

Workstream-specific run guides, output inventories, model-selection notes, reproducibility notes, and paper-planning notes must live under `docs/<workstream>/...`.

## Snapshot isolation rule

Frozen experiment states must live under `snapshots/<workstream>/...`.

The root of `snapshots/` is only an index and ownership boundary. Do not add new dated snapshot directories directly under `snapshots/`.
