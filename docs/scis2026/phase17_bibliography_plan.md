# SCIS Phase 17 Bibliography Plan

This document records the citation plan derived from the ChatGPT Pro
bibliography proposal and the first Codex verification pass.

## Policy

The bibliography should support a six-page, award-targeting SCIS&ISIS full
paper without turning it into a benchmark survey. The paper's core remains:

> persona-temperature factorial deconfounding for LLM-based fuzzy emotion
> scoring.

Use references to support claims about:

- prior EQ-Fuzzy / emotional-individuality work;
- factorial design and interaction effects;
- persona prompting and role/persona behavior;
- decoding temperature and stochastic sampling;
- fuzzy sets, fuzzy entropy, and membership-function design;
- LLM emotion evaluation as background;
- literary emotion analysis as task-domain context.

Do not add citations only for breadth. Every citation should anchor a specific
claim in the text.

## Essential Reference Set

The target main bibliography should include approximately 12 essential
references, plus 2--4 optional references if page space allows.

| Key | Status | Use |
| --- | --- | --- |
| `shirahama2026math` | locally accepted; DOI still needs final publisher-page check | Direct prior EQ-Fuzzy / emotional-individuality pipeline and paired persona-temperature limitation. |
| `montgomery2019design` | accepted textbook reference; verify final edition details before final submission | Factorial design, main effects, interactions, and balanced decomposition. |
| `tseng2024personaSurvey` | verified via ACL Anthology | Persona / role-playing / personalization survey for prompt-side persona framing. |
| `jiang2024personallm` | verified via ACL Anthology | Assigned LLM personas can produce systematic behavior differences; use cautiously. |
| `holtzman2020curious` | verified via arXiv | Stochastic decoding and sampling controls as generation-side mechanisms. |
| `renze2024temperature` | verified via ACL Anthology | Empirical temperature effects are task-dependent; temperature should be isolated experimentally. |
| `zadeh1965fuzzy` | canonical; DOI should be checked in final bib cleanup | Fuzzy set foundation. |
| `shannon1948communication` | canonical; DOI should be checked in final bib cleanup | Shannon-type entropy form. |
| `deluca1972nonprobabilistic` | canonical; DOI should be checked in final bib cleanup | Nonprobabilistic fuzzy entropy / fuzziness precedent. |
| `umano2025membership` | verified via J-STAGE | Smooth membership-function rationale and sigmoid-composed S-function motivation. |
| `sabour2024emobench` | verified via ACL Anthology | Representative LLM emotional-intelligence benchmark; use to delimit scope, not benchmark comparison. |
| `kim2019literaryEmotion` | verified via University of Bamberg record | Computational literary emotion-analysis context. |

## Optional References

Use at most two to four:

| Key | Use if needed | Caution |
| --- | --- | --- |
| `paech2024eqbench` | Additional emotional-intelligence benchmark example. | ArXiv benchmark; do not turn Related Work into leaderboard positioning. |
| `chen2024emotionqueen` | Empathy-oriented benchmark reference. | Use only if one benchmark citation feels too thin. |
| `huang2023emotionbench` | Human-referenced emotion benchmark. | Avoid anthropomorphic "LLMs feel" language. |
| `cheng2023pal` | Persona in emotional-support generation. | Different task; cite only for persona-affect context. |
| `kosko1986fuzzy` | Additional fuzzy entropy background. | Include only if fuzzy-theory discussion expands. |
| `reagan2016emotionalArcs` | Computational emotion in stories. | English corpus / sentiment arcs, not Japanese fuzzy LLM scoring. |
| `suslov2025gendered` | Japanese literary digital-humanities affect context. | Domain-specific; use only if literary context needs more support. |

## First Verification Notes

Verified through primary or stable sources:

- `tseng2024personaSurvey`: ACL Anthology lists title, authors, pages
  16612--16631, DOI `10.18653/v1/2024.findings-emnlp.969`.
- `jiang2024personallm`: ACL Anthology lists title, authors, pages
  3605--3627, DOI `10.18653/v1/2024.findings-naacl.229`.
- `renze2024temperature`: ACL Anthology lists Matthew Renze as sole author,
  pages 7346--7356, DOI `10.18653/v1/2024.findings-emnlp.432`.
- `sabour2024emobench`: ACL Anthology lists the ACL 2024 long-paper citation,
  pages 5986--6004, DOI `10.18653/v1/2024.acl-long.326`.
- `umano2025membership`: J-STAGE lists DOI `10.14864/fss.41.0_70`, session
  `1C1-1`, title `Some Considerations on Membership Functions of Fuzzy Sets`,
  and author `Motohide UMANO`.
- `kim2019literaryEmotion`: University of Bamberg record lists
  `Zeitschrift für digitale Geisteswissenschaften`, no. 4, pages 1--23, DOI
  `10.17175/2019_008_v2`.

Still needing final source check before manuscript insertion:

- `shirahama2026math`: local and institutional information confirm the article,
  but final publisher page should be checked before final camera-ready bib
  cleanup.
- `zadeh1965fuzzy`, `shannon1948communication`, and
  `deluca1972nonprobabilistic`: canonical references, but exact DOI / page
  formatting should be checked when finalizing BibTeX.
- `montgomery2019design`: final edition / ISBN details should be checked if
  cited as a textbook reference.

## Citation Placement

Introduction:

- cite `shirahama2026math` where the prior paired persona-temperature design is
  introduced;
- cite `montgomery2019design` only if the introduction explicitly mentions
  factorial design and interaction effects.

Related Work:

1. LLM emotion evaluation:
   - `sabour2024emobench`
   - optionally `paech2024eqbench` or `chen2024emotionqueen`
2. Persona and decoding controls:
   - `tseng2024personaSurvey`
   - `jiang2024personallm`
   - `holtzman2020curious`
   - `renze2024temperature`
3. Fuzzy and literary emotion:
   - `zadeh1965fuzzy`
   - `shannon1948communication`
   - `deluca1972nonprobabilistic`
   - `umano2025membership`
   - `kim2019literaryEmotion`

Method:

- cite `montgomery2019design` near the balanced decomposition formulas;
- cite `zadeh1965fuzzy`, `shannon1948communication`, and
  `deluca1972nonprobabilistic` near entropy;
- cite `umano2025membership` near `sigmoid_s_v1`;
- cite `shirahama2026math` when defining `legacy_linear_v1` as the prior
  baseline.

Discussion and limitations:

- cite `renze2024temperature` when warning that temperature effects are
  task-dependent and provider-specific;
- cite `kim2019literaryEmotion` only for domain context, not as evidence that
  three selected Japanese texts generalize to literature.

## References to Avoid or Use Sparingly

- Avoid many LLM emotion benchmarks. One or two are enough.
- Avoid broad sentiment-analysis references unrelated to literature, LLM
  emotion scoring, persona, or fuzzy entropy.
- Avoid advanced fuzzy entropy variants not used in this paper.
- Avoid causal-inference references unless the text explicitly distinguishes
  balanced descriptive decomposition from causal inference.
- Avoid provider API documentation as a scholarly foundation; keep exact API
  model identifiers in reproducibility artifacts.

## Next Codex Editing Step

Before inserting the full bibliography, implement the high-priority text edits
that do not depend on final citation formatting:

1. revise title and abstract;
2. add exact sum-of-squares formulas;
3. add bootstrap-scope caveat;
4. add fuzzy-membership rationale;
5. add retry/model-provenance/robustness paragraphs.

Then insert the verified references and tighten Related Work around them.

