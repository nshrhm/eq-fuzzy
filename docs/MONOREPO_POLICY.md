# Monorepo policy for `eq-fuzzy`

## 1. Repository scope

`eq-fuzzy` is the private monorepo for the **EQ-Fuzzy benchmark line under KAKENHI**.

Included:
- ICECCME
- SCIS
- ICICIC
- later journal / benchmark-integration work derived from the same line

Excluded:
- SPReAD1000 application repository

## 2. Core principle

**One repository, multiple scientific questions.**

**Share code, not claims.**

The repository is shared because the infrastructure is shared.
The manuscripts remain separate because the claims are separate.

## 3. What may be centralized

### Data / metadata
- text registry
- translation provenance
- human reference metadata
- model manifest
- license / redistribution notes

### Execution
- provider abstraction
- rate-limit and retry handling
- manifest builders
- batch runners
- logging and timestamps

### Parsing and validation
- structured output parser
- score extraction
- response validation
- hash checks for text / prompt / schema versions

### Analytics
- MAE / Pearson / Spearman
- valid-output rate
- drift metrics
- variance
- fuzzy membership
- fuzzy entropy
- bootstrap confidence intervals

### Reproducibility
- run manifest format
- regeneration scripts
- artifact naming rules

## 4. What may not be centralized as “shared truth”

- research hypothesis text
- figure captions that contain a paper claim
- introduction and discussion prose
- paper titles and abstracts
- benchmark superiority claims
- submission-ready tables that define novelty

## 5. Run isolation rule

Raw outputs, manifests, processed datasets, and generated figures must be isolated by workstream.

Recommended naming:

```text
runs/<workstream>/...
data/raw/<workstream>/...
data/processed/<workstream>/...
artifacts/<workstream>/...
```

No workstream should overwrite another workstream’s derived outputs.

## 6. Migration rule

Do not perform a big-bang refactor.

### Allowed in the first migration pass
- add documentation
- add future directories
- add temporary compatibility wrappers only with an explicit removal plan
- extract clearly reusable helpers with tests

### Not allowed in the first migration pass
- breaking current ICECCME canonical commands
- renaming working files without a tested canonical replacement
- moving raw data locations in a way that invalidates the manuscript build

## 7. Branching rule

Recommended branch names:

- `feat/iceccme-*`
- `feat/scis-*`
- `feat/icicic-*`
- `refactor/core-*`
- `docs/monorepo-*`

Changes touching `core` must explicitly note downstream impact on all active workstreams.

## 8. Reproducibility minimum

Each run should preserve at least:

- workstream name
- run id
- timestamp
- model ids
- prompt version
- schema version
- text registry version
- seed / repeats
- language / persona / temperature settings
- git commit hash

## 9. Boundary to SPReAD1000

The SPReAD repository may import or vendor selected utilities from `eq-fuzzy`, but `eq-fuzzy` should not become dependent on SPReAD-specific workflow code, UI code, or annotation-ops logic.

The dependency direction should be:

```text
eq-fuzzy  ---> reusable utilities ---> SPReAD
```

and not the reverse.

SPReAD may reuse selected `eq-fuzzy` utilities later, but `eq-fuzzy` must not depend on SPReAD-specific workflow code, UI code, review queues, annotation-operation logic, or expert-log formats.
