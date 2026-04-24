# Scripts

Scripts are grouped by workstream.

The root-level `scripts/*.py` files are compatibility wrappers for the current ICECCME 2026 workflow. New workstream-specific scripts should live under:

- `scripts/iceccme2026/`
- `scripts/scis2026/`
- `scripts/icicic2026/`

Shared reusable logic should generally move to `src/core/`, not to a shared script directory. Scripts should remain thin command-line entry points.
