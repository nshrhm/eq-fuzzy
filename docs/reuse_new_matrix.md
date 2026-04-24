# Reuse vs New Build Matrix

## Reused directly

| Asset | Source | How it is reused |
|---|---|---|
| IEEE conference LaTeX class and example | uploaded `ICECCME2026_latex.zip` | copied into `paper/iceccme2026/` as the formatting base |
| Public reproducibility repo pattern | previous public repository layout | same top level pattern: `src/`, `results/`, `main.py`, `verify_results.py`, quickstart docs |
| Four emotion design | human survey and prior papers | preserved exactly for comparability: interest, surprise, sadness, anger |
| Persona framing | prior LLM-only study | preserved as a controllable analysis factor, but human alignment becomes the primary endpoint |

## Reused conceptually but rewritten

| Asset | Why rewritten |
|---|---|
| prior multilingual paper flow | its main question is language effect; the ICECCME paper needs human-grounded evaluation as the main question |
| old result figures | reusing the same main figures would blur originality and paper separation |
| runner outputs | the current uploaded ZIP did not include inspectable source files, so interfaces were recreated from scratch |

## Newly created here

| File group | Why it is new |
|---|---|
| `src/iceccme2026/human_data.py` | de-identification and aggregation of the human VAS workbook |
| `src/iceccme2026/metrics.py` | human alignment and cross-language drift scoring |
| `data/iceccme2026/derived_public/*` | sanitized human reference data |
| `data/iceccme2026/manifests/iceccme2026_default_manifest.csv` | the ICECCME specific multilingual run grid |
| `prompts/*` | versioned prompt and schema assets for this paper |
| `docs/paper_blueprint.md` | title, abstract, figure plan, and section budget fixed for the conference paper |
| `paper/iceccme2026/*` | ICECCME specific paper skeleton on the uploaded IEEE template |
