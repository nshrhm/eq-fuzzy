# Migration plan: from the current ICECCME repository scaffold to the `eq-fuzzy` monorepo

## Current state

The current repository already contains a working ICECCME pipeline with:

- configs
- prompts
- human-data preparation
- manifest building
- alignment scoring
- figure and table regeneration
- manuscript files under `paper/iceccme2026/`

This is a good starting point for the broader monorepo.
The migration goal is **not** to replace it immediately, but to widen it safely.

## Phase 0 — keep the paper stable

Before restructuring, confirm that the current ICECCME build still works end to end.

Minimum must-pass commands:

```bash
python main.py prepare-human ...
python main.py build-manifest ...
python main.py score-alignment ...
python scripts/iceccme2026/plot_figure2_ja_ranking.py
python scripts/iceccme2026/plot_figure3_cross_language_drift.py
python scripts/iceccme2026/export_table2_primary.py
```

## Phase 1 — documentation-first monorepo conversion

### Goal
Create the monorepo framing without breaking any working command.

Operating rule: **Share code, not claims.**

### Actions
1. add the new repository-level docs:
   - `docs/WORKSTREAMS.md`
   - `docs/MONOREPO_POLICY.md`
   - `docs/MIGRATION_PLAN.md`
2. add workstream context docs under `docs/context/`
3. isolate workstream-specific docs under:
   - `docs/iceccme2026/`
   - `docs/scis2026/`
   - `docs/icicic2026/`
4. add empty future directories:
   - `configs/scis/`
   - `configs/icicic/`
   - `prompts/scis/`
   - `prompts/icicic/`
   - `paper/scis2026/`
   - `paper/icicic2026/`
   - `runs/scis2026/`
   - `runs/icicic2026/`
   - `artifacts/iceccme2026/`
   - `artifacts/scis2026/`
   - `artifacts/icicic2026/`
   - `snapshots/iceccme2026/`
   - `snapshots/scis2026/`
   - `snapshots/icicic2026/`
5. keep `src/iceccme2026/` as-is
6. do not move current raw or processed ICECCME files

### Result
The repository remains operational for ICECCME and becomes ready for SCIS / ICICIC.
The SCIS and ICICIC directories are placeholders only at this stage; do not add fake configs, prompts, analysis code, or manuscript claims.

## Phase 2 — extract shared code conservatively

### Candidate extraction targets from `src/iceccme2026/`

- `manifest.py` -> shared manifest utilities
- `metrics.py` -> shared alignment/statistics utilities
- `model_scores.py` -> shared normalized score table loader / validator
- `reporting.py` / `paper_exports.py` -> shared export helpers where generic

### New target structure

```text
src/
├─ core/
│  ├─ manifest/
│  ├─ metrics/
│  ├─ parsing/
│  ├─ validation/
│  └─ reporting/
└─ papers/
   ├─ iceccme/
   ├─ scis/
   └─ icicic/
```

### Safety rule
Only extract code that is actually reusable and can be covered by tests.
If a function bakes in ICECCME assumptions, leave it in the ICECCME package.

## Phase 3 — add SCIS and ICICIC as new workstreams

### SCIS
Add:
- `configs/scis/`
- `prompts/scis/`
- `src/papers/scis/`
- `paper/scis2026/`
- `runs/scis2026/`

Initial contents:
- condition table builders
- fully crossed persona × temperature configs
- effect-size and interaction-analysis scripts

### ICICIC
Add:
- `configs/icicic/`
- `prompts/icicic/`
- `src/papers/icicic/`
- `paper/icicic2026/`
- `runs/icicic2026/`

Initial contents:
- benchmark adapter stubs
- aligned subset configs
- comparison-matrix exports

## Phase 4 — optional package extraction for SPReAD reuse

Do this only after the API stabilizes.

Possible extraction:
- a small internal utility package such as `eqf_core`

Contents may include:
- registry readers
- score schema validators
- common metrics
- fuzzy functions

Do **not** extract manuscript-facing code or benchmark-claim logic into that package.

## Anti-patterns to avoid

- moving everything at once
- renaming working ICECCME paths without wrappers
- coupling SPReAD-specific workflow code back into the benchmark repository
- building abstractions before SCIS / ICICIC actually need them

## Definition of success

The migration is successful when:

1. ICECCME still runs unchanged
2. SCIS and ICICIC can be added without copy-pasting the ICECCME stack
3. shared code is smaller and clearer, not more abstract for its own sake
