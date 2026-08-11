# Results and durable verdict

## Verdict

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-R1-R1-CROSS-SITE-STATE-FEEDBACK-REMAINDER-AND-TABLE-EVENT-LOCK

DURABLE_PASS_R2_R1A_R1_R1_R1_R1_R1_FOUR_SITE_MICROSTEP_ENCLOSURE_LOCAL_ERROR_CONTAINMENT_TABLE_RESTART_AND_STRUCTURAL_LEDGER_PASS_FIRST_CANONICAL_INTERVAL_AUTHORIZED
```

This bounded stage certifies one accepted four-site FLRW thermochemistry
microstep at partition `2048`. It does **not** certify the whole first canonical
interval, production node chemistry, `R2C-R2`, `B2C2B`, CAMB transfer, or
Bianchi feedback.

## Load-bearing result

The source-safe branch variables at

1. `population_t0`,
2. `population_t1_predictor`,
3. `thermal_tgamma`, and
4. `thermal_t1_final`

were kept independent. Their nonlinear MPRK22(1)-Alexander-SDIRK2 discrete map
was enclosed by project-policy outward binary64 interval arithmetic, local
Krawczyk certificates, analytic thermal derivative intervals, and explicit
owner-normalization feedback.

All three shape lanes passed:

```text
LOCAL_NEUTRAL_HAZARD_PRIMARY
RECOMBINATION_WEIGHTED_AUDITOR
SCRIPT_SELF_SHIELDING_AUDITOR
```

The maximum public widths were

\[
\Delta x_{\rm HII}=2.6643106193491306e-06,
\]

\[
\Delta x_{\rm HeII}=1.2958711863020334e-05,
\qquad
\Delta x_{\rm HeIII}=2.8461103586743808e-08,
\]

\[
\Delta\ln T=4.5248865610858502e-05.
\]

The largest width is smaller than the locked `2e-3` gate by a factor
`44.200003094`.

## Validated adaptive local error

A full-step image and two successive half-step images were constructed for the
same uncertainty family. The maximum blockwise full-versus-two-half bound at
partition `2048` is

\[
\epsilon_{\rm local}^{\max}=0.00011621773858117024<2\times10^{-4}.
\]

The component bounds are:

```text
x_HII   3.0668487366769526e-05
x_HeII  5.6861223254101034e-05
x_HeIII 1.2470579114649133e-06
log_T   0.00011621773858117024
```

This gate was added after adversarial review. Partition `1024` still encloses
the map but fails the local-error gate; partitions `2048` and `4096` pass:

```text
1024  FAIL  0.00023307125014504493
2048  PASS  0.00011621773858117024
4096  PASS  7.352490614742635e-05
```

Both public widths and validated local error decrease under refinement.

## Containment

The certified images contain:

- both strict static endpoint trajectories;
- the upper-then-lower stagewise-switch witness that escaped the old static
  four-corner hull;
- the stored coherent 3x3 and withheld/interior falsification points;
- all three shape lanes.

The maximum inherited static-hull escape in `x_HeIII` was
`6.979149463209877e-12`; direct replay of every lane has zero significant
outside entries in the new image.

## Table-event contract

The load-bearing microstep is event-free. The minimum path-hull distance to a
Hummer-Seaton knot is

\[
0.00028926282673857884
\]

in `ln T`. A synthetic between-site crossing is detected and localized in both
time directions to width

\[
9.0949470177292824e-13,
\]

while parent state and ledger bytes remain unchanged. This locks the
transactional event/restart semantics; it is not evidence that a real event
occurs in the certified microstep.

## Conservation and energy ownership

The load-bearing conservation authority is structural:

- every event stoichiometric vector preserves H and He nuclei;
- MPRK transfer columns sum exactly to one;
- owner fractions sum exactly to one;
- group photon destruction equals the sum of its named owners;
- photon plus chemical plus resolved/unresolved/escaped energy has exact zero
  residual.

All symbolic residuals are exactly zero. Raw componentwise interval ledger
boxes also include zero, but their large widths are dependency diagnostics and
are **not** interpreted as physical uncertainty bounds.

## Numerical claim boundary

The enclosure uses project-policy outward binary64 `nextafter` arithmetic and
large Krawczyk margins. It is a reproducible project certificate, not a claim of
an arbitrary-platform MPFR/MPFI computer-assisted proof. The independent
validator checks all sealed identities, widths, local errors, containment,
refinement and event receipts without importing the interval-map
implementation. Repository-wide file-isolated verification passed `291` assertions across `75` test files with no failures.

## Authorization

```text
next stage authorized: true
production history: false
production node chemistry: false
R2C-R2: false
B2C2B: false
```

Next:

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-R1-R1-R1-UNCERTAINTY-QUALIFIED-FIRST-CANONICAL-INTERVAL-ADAPTIVE-HISTORY
```
