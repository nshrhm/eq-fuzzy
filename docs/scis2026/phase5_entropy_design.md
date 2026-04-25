# SCIS 2026 Phase 5.5 Fuzzy Entropy Design

This note locks the SCIS 2026 fuzzy entropy implementation before the Phase 6
main run. The entropy design is an analysis specification, not a new paper
claim by itself.

## Decision

SCIS uses `sigmoid_s_v1` as the primary membership family and keeps
`legacy_linear_v1` as the reproducibility and sensitivity baseline.

The semantic breakpoints are unchanged from the prior implementation:

- Low: transition over `0-30`
- Medium: rise over `10-30`, plateau over `30-50`, fall over `50-70`
- High: transition over `50-100`

The change is only the transition shape. `legacy_linear_v1` uses piecewise
linear ramps. `sigmoid_s_v1` maps each transition interval through a sigmoid
and then applies an S-function ramp with domain anchors `0.1` and `0.9`.

## Rationale

The Phase 6 main run compares persona and API temperature as crossed factors.
The membership function must therefore remain fixed across all conditions while
avoiding artificial sensitivity at linear breakpoints.

The local review of Umano, "Some Considerations on Membership Functions of
Fuzzy Sets" (FSS2025), supports this choice:

- triangular and trapezoidal membership functions are continuous but not smooth
  at their parameter points;
- the S-function family gives a C1 piecewise-smooth transition;
- Gaussian functions are smooth but do not naturally reach 0 or 1;
- composing a sigmoid transform with an S-function can keep stronger
  discrimination near the focal value while reducing differences farther away.

SCIS should describe this as a fixed, smoother membership specification. It
must not claim that this membership family is uniquely correct or that fuzzy
entropy directly measures true emotional ambiguity.

## Entropy

For every valid emotion score `x`, both membership families produce:

- `mu_low`
- `mu_medium`
- `mu_high`
- `H_raw = -sum(mu_i * log2(mu_i))`
- `H_norm = H_raw / Hmax_family`

The zero convention is `0*log2(0)=0`.

`Hmax_family` is computed deterministically from the membership configuration
using a dense grid over `0-100` with step `0.001`. The config hash and Hmax
values are stored in the analysis summary.

## Analysis Use

Main SCIS analysis should use:

- primary membership family: `sigmoid_s_v1`
- primary entropy outcome: `H_norm`
- baseline/sensitivity family: `legacy_linear_v1`

Sensitivity analysis should compare condition-level `H_norm` summaries across
families and report whether the qualitative interaction pattern is stable.
