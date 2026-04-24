# Scripts

Scripts are grouped by workstream.

There are no root-level script wrappers. Workstream-specific scripts live under:

- `scripts/iceccme2026/`
- `scripts/scis2026/`
- `scripts/icicic2026/`

Shared reusable logic should generally move to `src/core/`, not to a shared script directory. Scripts should remain thin command-line entry points.
