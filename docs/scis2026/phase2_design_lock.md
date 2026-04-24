# SCIS 2026 Phase 2 Design Lock

This note records the Phase 2 design lock for the SCIS 2026
persona-temperature factorial deconfounding experiment. It is a design record,
not a report of completed factorial experiment results.

## Locked Files

- Factorial config: `configs/scis/factorial_v1.yaml`
- Condition table: `configs/scis/condition_table_v1.csv`
- Main model panel: `configs/scis/main_panel_v2.yaml`
- System prompt: `prompts/scis/factorial_v1_system.md`
- User prompt template: `prompts/scis/factorial_v1_user_template.md`
- Response schema: `prompts/shared/response_schema.json`

## Design

Primary factors:

- 3 Japanese literary texts: `T1`, `T2`, `T3`
- 4 personas: `p1`, `p2`, `p3`, `p4`
- 4 API temperatures: `0.1`, `0.4`, `0.7`, `0.9`
- 16 fully crossed persona-temperature conditions
- 4 emotion dimensions: `interest`, `surprise`, `sadness`, `anger`
- 6 Phase 1/1b qualified models from `configs/scis/main_panel_v2.yaml`

The primary main run remains:

```text
6 models x 3 texts x 16 conditions x 5 repeats = 1440 trials
```

## Separation Rule

Temperature is specified only as an API/config parameter. It must not appear in
the system prompt or user prompt template.

Persona is specified only as the interpretive stance in the user prompt.

## Validation

Run:

```bash
python scripts/scis2026/validate_phase2_design.py
```

The validator checks:

- `condition_table_v1.csv` is a complete 4 x 4 persona-temperature cross
- condition IDs are unique
- factorial prompt files do not contain forbidden prompt terms
- `main_panel_v2.yaml` contains exactly six unique models
- sanity, pilot, and main expected trial counts match the locked design
