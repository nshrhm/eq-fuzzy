# FSS 2026 scripts

Canonical scripts for the FSS 2026 membership-specification short note.

Build score-axis membership and entropy-response grids:

```bash
uv run python scripts/fss2026/build_membership_response_curves.py
```

Export the membership specification card:

```bash
uv run python scripts/fss2026/export_membership_spec_card.py
```

Build the score-axis family sensitivity matrix:

```bash
uv run python scripts/fss2026/analyze_membership_sensitivity_protocol.py
```

Build manuscript-facing table and figure artifacts:

```bash
uv run python scripts/fss2026/build_fss_tables.py
uv run python scripts/fss2026/build_fss_figures.py
```

These scripts are offline score-axis utilities. They do not call model APIs,
read raw JSONL run files, copy raw JSONL files, compute persona-temperature
decompositions, or produce model-ranking/benchmark-positioning artifacts.
