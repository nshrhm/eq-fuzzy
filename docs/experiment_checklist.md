# Experiment Checklist

## Before the run
- [ ] Verify T1–T3 mapping against `external/jaciii_iihmsp2025/definitions.py`.
- [ ] Confirm that the EN and ZH texts are the validated translations you want to compare.
- [ ] Freeze the model IDs in `configs/shared/models_default.yaml`.
- [ ] Freeze the prompt files and response schema.
- [ ] Decide whether the paper will report only the primary neutral run or also one compact persona-sensitivity figure.

## During the run
- [ ] Save raw request logs privately.
- [ ] Disable visible reasoning traces where the provider allows it.
- [ ] Save numeric score outputs in the repository schema.
- [ ] Track timestamps, provider, and parse failures by model and language.

## After the run
- [ ] Export one merged long CSV with the repository schema.
- [ ] Run the human-alignment script.
- [ ] Inspect cell-level outliers before writing conclusions.
- [ ] Keep Japanese as the primary endpoint.
- [ ] Keep EN/ZH as robustness analyses unless new human references are collected.
