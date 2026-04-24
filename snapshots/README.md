# Snapshot ownership

Frozen experiment snapshots are isolated by workstream.

- `snapshots/iceccme2026/` stores ICECCME 2026 frozen run states and repair checkpoints.
- `snapshots/scis2026/` is reserved for SCIS 2026 snapshots once real runs exist.
- `snapshots/icicic2026/` is reserved for ICICIC 2026 snapshots once real runs exist.

Do not add new snapshots directly under `snapshots/`.
Use a dated subdirectory inside the owning workstream directory.
