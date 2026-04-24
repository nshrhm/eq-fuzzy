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
| `configs/*.yaml` | `iceccme` compatibility | Current experiment, model, persona, text, and paper config files. |
| `prompts/*.md`, `prompts/*.json` | `iceccme` compatibility | Current prompt contract for the ICECCME runs. |
| `results/` | `iceccme` compatibility | Existing derived CSV/JSON outputs used by ICECCME scripts. |
| `data/manifests/iceccme2026_*.csv` | `iceccme` | ICECCME run manifests. |
| `data/results/json/iceccme2026_*.json` | `iceccme` | ICECCME manifest summaries preserved for compatibility. |

## Future canonical paths

New work should use these paths once each workstream has a real design.

| Path | Owner | Rule |
|---|---|---|
| `src/core/` | `shared` | Future shared utilities only after a second workstream needs them. |
| `configs/shared/` | `shared` | Shared registry/config fragments, not paper-specific experiment plans. |
| `prompts/shared/` | `shared` | Shared schemas or prompt fragments only when they are claim-neutral. |
| `data/catalogs/` | `shared` | Text, persona, and model catalogs with provenance. |
| `configs/iceccme/` | `iceccme` | Future canonical ICECCME configs; root configs remain compatibility paths. |
| `prompts/iceccme/` | `iceccme` | Future canonical ICECCME prompts; root prompts remain compatibility paths. |
| `scripts/iceccme2026/` | `iceccme` | Canonical ICECCME script implementations; root scripts remain compatibility wrappers. |
| `runs/iceccme/` | `iceccme` | New ICECCME run outputs and logs. |
| `artifacts/iceccme/` | `iceccme` | New ICECCME generated figures, tables, and manuscript exports. |
| `configs/scis/` | `scis` | Real SCIS configs only; no placeholder experiment YAML. |
| `prompts/scis/` | `scis` | Real SCIS prompts only; no fake prompt variants. |
| `paper/scis2026/` | `scis` | SCIS manuscript source. |
| `scripts/scis2026/` | `scis` | SCIS command-line scripts. Placeholder only for now. |
| `runs/scis/` | `scis` | SCIS run outputs and logs. |
| `configs/icicic/` | `icicic` | Real ICICIC configs only; no placeholder experiment YAML. |
| `prompts/icicic/` | `icicic` | Real ICICIC prompts only; no fake prompt variants. |
| `paper/icicic2026/` | `icicic` | ICICIC manuscript source. |
| `scripts/icicic2026/` | `icicic` | ICICIC command-line scripts. Placeholder only for now. |
| `runs/icicic/` | `icicic` | ICICIC run outputs and logs. |

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
