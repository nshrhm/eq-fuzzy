# Prompting assets

Prompt assets are grouped by ownership.

The root-level prompt files are compatibility symlinks for existing manifests and runner commands. Canonical files live under:

- `prompts/iceccme/` for ICECCME 2026 prompt text
- `prompts/shared/` for claim-neutral shared schemas or prompt fragments
- `prompts/scis/` for future SCIS 2026 prompts
- `prompts/icicic/` for future ICICIC 2026 prompts

## Policy

Version prompt text and schemas together with every major experiment run.
If a prompt changes, bump or record the prompt version in the run manifest and note the change in the relevant paper methods section.
