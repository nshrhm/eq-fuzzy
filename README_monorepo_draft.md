# eq-fuzzy

Private monorepo for the JSPS KAKENHI **EQ-Fuzzy** research line on uncertainty-aware evaluation of LLM emotional intelligence.

## Why one repository

This repository should group the **KAKENHI-side workstreams** that share one scientific line, one experimental substrate, and one reproducibility surface:

- **ICECCME 2026**: human-grounded multilingual pilot
- **SCIS 2026**: persona × temperature deconfounding
- **ICICIC 2026**: benchmark positioning / matched comparison
- later journal / benchmark integration work under the EQ-Fuzzy program

The common assets are already substantial:

- text registry and metadata
- model manifests and provider routing
- prompt schema and structured output schema
- batch execution and retry logic
- parsing / validation
- alignment metrics, variance, fuzzy membership, fuzzy entropy
- figure regeneration and provenance logging

Keeping these in one private monorepo reduces duplication and makes it easier to preserve a single audit trail from raw outputs to paper figures.

## What stays outside this repository

**SPReAD1000 should be kept separate**.

Rationale:

- it is an adjacent application / workflow project rather than the benchmark core
- it is likely to introduce different assets (annotation workflows, demo UI, review queues, expert logs)
- its data-governance and deliverable surface are different from the KAKENHI benchmark line
- coupling it too tightly to the benchmark repo would increase accidental scope creep

Shared logic can still move across the boundary later through one of these paths:

1. copy a frozen snapshot of a small internal utility package
2. vendor a shared module directory with clear version notes
3. extract a minimal `eqf_core` package only after the interfaces stabilize

## Operating rule

**Share code, not claims.**

This repository is a monorepo for implementation and reproducibility, not a license to blur paper boundaries.

What may be shared:

- registries
- runners
- parsers
- metrics
- fuzzy utilities
- bootstrap CI helpers
- provenance and regeneration scripts

What must remain paper-specific:

- research question
- main figures and tables
- novelty claim
- introduction framing
- discussion / limitations language

## Recommended top-level workstream layout

```text
repo/
├─ docs/
│  ├─ context/
│  │  ├─ 00_shared_context.md
│  │  ├─ 01_ICECCME.md
│  │  ├─ 02_SCIS2026.md
│  │  └─ 03_ICICIC2026.md
│  ├─ WORKSTREAMS.md
│  ├─ MONOREPO_POLICY.md
│  └─ MIGRATION_PLAN.md
├─ configs/
│  ├─ shared/
│  ├─ iceccme/
│  ├─ scis/
│  └─ icicic/
├─ data/
│  ├─ registry/
│  ├─ raw/
│  │  ├─ iceccme/
│  │  ├─ scis/
│  │  └─ icicic/
│  ├─ interim/
│  └─ processed/
├─ prompts/
│  ├─ shared/
│  ├─ iceccme/
│  ├─ scis/
│  └─ icicic/
├─ src/
│  ├─ core/
│  └─ papers/
│     ├─ iceccme/
│     ├─ scis/
│     └─ icicic/
├─ paper/
│  ├─ iceccme2026/
│  ├─ scis2026/
│  └─ icicic2026/
├─ runs/
│  ├─ iceccme/
│  ├─ scis/
│  └─ icicic/
└─ artifacts/
   ├─ figures/
   ├─ tables/
   └─ manuscripts/
```

## Migration principle

This should be done **without breaking the current ICECCME pipeline**.

Phase 1 is documentation-first and non-destructive:

- keep current `main.py`, `run_openrouter_manifest.py`, `scripts/*`, and `paper/iceccme2026/*` working
- add monorepo policy documents and empty future directories
- treat `src/iceccme2026/*` as the current working implementation

Phase 2 extracts only clearly reusable code into `src/core/`.

Phase 3 adds SCIS and ICICIC project logic on top of the shared core.

## Immediate recommendation

Use `eq-fuzzy` as the **private monorepo for KAKENHI-side work**.
Do **not** open separate per-paper repositories unless there is a clear external-sharing reason later.
Keep SPReAD in a separate repository, with a narrow documented reuse boundary.
