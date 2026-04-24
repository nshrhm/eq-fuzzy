# Agent instructions

This repository is the private monorepo for the EQ-Fuzzy research line. It contains separate workstreams for ICECCME 2026, SCIS 2026, and ICICIC 2026.

## First-read documents

Before structural changes, read:

- `docs/PATH_OWNERSHIP.md`
- `docs/DEVELOPMENT_POLICY.md`
- `docs/MONOREPO_POLICY.md`

## Core rules

- Share code, not claims.
- Keep paper-specific hypotheses, captions, manuscript framing, and novelty claims inside the owning workstream.
- Use canonical paths only. Do not recreate root compatibility wrappers or compatibility symlinks.
- Do not add fake SCIS or ICICIC configs, prompts, experiments, outputs, or manuscript claims.
- Keep `.venv/` local and untracked.
- Keep `requirements.txt` as the shared baseline environment unless a concrete dependency conflict justifies an additional requirements file.
- Do not extract code into `src/core/` merely because it looks reusable. Extract only when a second workstream actually needs the same claim-neutral behavior and tests cover it.
- Do not split `tests/` speculatively. Split tests when shared core or new workstream implementation pressure requires it.
- Use `artifacts/scratch/` only for temporary cross-workstream drafts. Promote accepted artifacts into the owning workstream directory.

## Canonical ICECCME commands

Use module commands and workstream paths:

```bash
python -m src.iceccme2026.cli --help
python -m src.iceccme2026.openrouter_runner --dry-run --limit 1
python -m src.iceccme2026.verify
python -m unittest discover -s tests
```

The root `main.py`, `run_openrouter_manifest.py`, `verify_results.py`, root `scripts/*.py` wrappers, and compatibility symlinks have been removed intentionally.

## Documentation language

Repository documentation should be written in English unless the user explicitly asks otherwise.

Japanese may be used in conversation with the repository owner when that is the most effective collaboration language.
