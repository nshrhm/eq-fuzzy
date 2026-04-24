# Codex bootstrap prompt for converting the current repository into the `eq-fuzzy` monorepo

Paste the following prompt into Codex inside the repository root.

---

You are working inside the private repository `eq-fuzzy`.

This repository should become the **private monorepo for the KAKENHI-side EQ-Fuzzy research line**, covering:
- ICECCME 2026
- SCIS 2026
- ICICIC 2026

SPReAD1000 is **not** part of this repository and should remain separate.

## Scientific boundary

Keep these workstreams scientifically separate even though they share infrastructure:

- ICECCME: human-grounded multilingual pilot
- SCIS: persona × temperature factorial deconfounding
- ICICIC: benchmark positioning / matched comparison

Shared code is allowed.
Shared novelty claims are not.

## Current repository state

The current repository already has a working ICECCME pipeline.
Do not break it.
Preserve current commands, current manuscript paths, and current generated outputs unless a wrapper keeps backward compatibility.

## Your task

Perform a **documentation-first, non-destructive monorepo bootstrap**.

### Required changes

1. Update the top-level `README.md` so it describes the repository as the private `eq-fuzzy` monorepo rather than an ICECCME-only repo.
   - explain why ICECCME, SCIS, and ICICIC belong together
   - explain why SPReAD stays outside
   - state the rule “share code, not claims”

2. Add these documentation files if they do not exist:
   - `docs/WORKSTREAMS.md`
   - `docs/MONOREPO_POLICY.md`
   - `docs/MIGRATION_PLAN.md`
   - `docs/context/00_shared_context.md`
   - `docs/context/01_ICECCME.md`
   - `docs/context/02_SCIS2026.md`
   - `docs/context/03_ICICIC2026.md`

3. Add future-facing empty directories with `.gitkeep` where needed:
   - `configs/scis/`
   - `configs/icicic/`
   - `prompts/scis/`
   - `prompts/icicic/`
   - `paper/scis2026/`
   - `paper/icicic2026/`
   - `runs/scis/`
   - `runs/icicic/`
   - `artifacts/iceccme2026/`
   - `artifacts/scis2026/`
   - `artifacts/icicic2026/`

4. Do **not** move or rename the current ICECCME working files in this pass.
   - leave `src/iceccme2026/` intact
   - leave `paper/iceccme2026/` intact
   - leave current scripts runnable

5. Add a short note in the docs describing the next extraction targets for shared core logic, but do not perform a large refactor yet.

## Constraints

- Do not introduce a big-bang refactor.
- Do not break the current ICECCME workflow.
- Do not add fake implementation for SCIS or ICICIC beyond directory stubs and docs.
- Keep documentation specific and operational, not generic.
- Use Markdown only for the new documentation files.

## Acceptance criteria

Your output is acceptable only if all of the following are true:

1. `README.md` clearly frames the repo as the private EQ-Fuzzy monorepo.
2. SPReAD is explicitly documented as separate.
3. ICECCME commands remain unchanged.
4. New directories for SCIS and ICICIC exist.
5. The repo becomes easier to extend without implying that the three papers are scientifically the same.

## Reporting format

At the end, provide:
- a concise summary of changed files
- any compatibility risks
- the exact files that still require manual content later (for example SCIS / ICICIC configs)

---
