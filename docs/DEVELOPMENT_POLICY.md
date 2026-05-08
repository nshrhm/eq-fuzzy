# Development policy

This document records development decisions for the `eq-fuzzy` monorepo before new SCIS 2026 and ICICIC 2026 implementation work begins.

## Python environment

Use one repository-level Python environment.

- `.venv/` is a local developer environment and remains untracked.
- `pyproject.toml`, `uv.lock`, and `.python-version` define the shared baseline environment for the EQ-Fuzzy repository.
- Use `uv sync` to create or update the local environment.
- Run repository Python commands through `uv run`, for example `uv run python -m unittest discover -s tests`.
- `requirements.txt` is retained temporarily as a migration compatibility file; the uv project files are authoritative.
- Do not create per-conference virtual environments or per-conference baseline requirements files by default.

This is intentional. ICECCME, SCIS, and ICICIC share the same benchmark substrate, analysis style, plotting stack, and reproducibility surface. Splitting the Python environment too early would increase maintenance cost and make dependency drift more likely.

Additional requirement files may be added only when there is a concrete need, for example:

- `requirements-dev.txt` for development-only tooling.
- `requirements-paper.txt` for manuscript-build tooling.
- `requirements-scis.txt` or `requirements-icicic.txt` only if a workstream genuinely needs dependencies that should not be part of the shared baseline.

## Source organization

Keep `src/iceccme2026/` stable as the current ICECCME implementation package.

Do not move code into `src/core/` merely because it looks reusable. Shared code should be extracted only when a second workstream actually needs the same behavior.

Core extraction requires all of the following:

- SCIS or ICICIC needs the behavior in practice.
- The extracted behavior is claim-neutral.
- The extracted behavior has tests.
- ICECCME remains runnable through stable package modules.
- Paper-specific paths, captions, novelty claims, and manuscript framing stay outside `src/core/`.

Likely future candidates include generic parts of manifest construction, normalized score loading, response validation, alignment metrics, correlation helpers, drift metrics, and export helpers. These are candidates, not commitments.

## Test organization

Keep the current test layout until implementation pressure justifies a split.

When shared code is extracted, add focused tests for that shared behavior. A future layout may include:

- `tests/core/`
- `tests/iceccme2026/`
- `tests/scis2026/`
- `tests/icicic2026/`

Do not create empty or speculative test directories just to mirror the repository structure.

## Artifact scratch policy

Use `artifacts/scratch/` only for temporary cross-workstream drafts.

Accepted or submission-relevant outputs must be promoted into the owning workstream directory, such as:

- `artifacts/iceccme2026/`
- `artifacts/scis2026/`
- `artifacts/icicic2026/`

Scratch artifacts are not archival, not submission-ready, and not part of the reproducibility record until promoted.

## Decision rule

Prefer canonical paths and simple shared infrastructure.

Separate by workstream when the separation protects scientific claims, generated outputs, or manuscript assets. Keep repository-level infrastructure shared when splitting it would mainly create operational overhead.
