# Independent panel implementation review

2026-10-07. Scope: fixed-shape positive parent-measure restriction only. This module does not solve the inverse N/M closure problem and is not reviewed as such.

Inspected source SHA-256 before correction: `ac568c91c7f75a77a6c4ad44be45a4d8aa65ab3621fda9f762d842a54e4c9035`.

## Verified source properties

- Parent domain is finite, endpoints lie within [-32,32], exact endpoint difference is admitted against [1e-7,32], and beta is bounded by 128 in absolute value.
- Restriction integrates the parent Ordinary or RightFront measure; a right-front interior child retains the old taper and is not retapered as a new source frontier.
- Positive eight-point Gauss rules are subdivided and scaled, with compensated positive sums and independently monitored count/normalized-mean convergence. This is empirical quadrature admission, not an interval proof.
- The amplitude and shape are independent. Geometry-empty intersection returns `None`; positive tail shape remains representable.
- Narrow positive restrictions can have no representable interior stock-rule site. `quadrature_node` correctly rejects such an atomization while retaining the continuous restriction.
- The saved 601-case Decimal160 oracle uses exact supplied binary64 endpoints and independent analytic exponential primitives. Its reported 1803 comparisons test mass fraction, normalized mean, and mean exp(eta). They do not initially test the final parent-log-plus-fraction amplitude addition.

## Confirmed defect: loss of restricted amplitude under an accepted log input

The reviewer compiled the actual module into `panel_adversarial.rs` and executed five ordinary half-panel restrictions and three small domain/endpoint assertions. No candidate source was modified. For beta=0 on [0,1] restricted to [0,1/2], the exact amplitude is exp(ln_N_parent)/2, so the authoritative log is ln_N_parent-ln2.

At ln_N_parent=-1e12, the module accepted the result but its single binary64 `ln_n` produced a relative physical count error 3.194669523010957e-5, exceeding the frozen 3e-12 owner target. The shape and log fraction were accurate; the final log addition lost information. Tail inputs -750 and -1000 passed at approximately 5.50e-14 and -1e5 passed at 1.65e-12. Thus the reported fixture accuracy is not contradicted, but finite-log API admission was too broad for its amplitude output.

Artifacts: `PANEL_ADVERSARIAL_RESULT.json`, `panel_adversarial.rs`, `panel_adversarial.log`. The failing witness must remain unchanged. An acceptable correction retains the exact two-sum high/low pair or fails closed when amplitude precision cannot meet its declared budget. Merely documenting the lost count as underflow would be incorrect: this is log-addition rounding, not linear-readout underflow.

## Correction requirements

The panel owner proposes `ln_n` plus `ln_n_lo`, with the pair authoritative. Review the corrected docs and every actual consumer. Pair-aware independent comparison must evaluate Decimal(hi)+Decimal(lo) without a binary64 hi+lo operation. The fixed-shape restriction still does not certify arbitrary inverse closure reconstruction, repeated projection, gas feedback, or long-history export.

## Correction independently accepted

The corrected source retains an exact TwoSum pair `ln_n` and `ln_n_lo`, exposes `log_amplitude_parts()`, and explicitly prohibits consuming only the high part. The reviewer recompiled the corrected actual module and repeated all five amplitude witnesses using Decimal(hi)+Decimal(lo) without binary64 recombination. Every case passes; maximum relative amplitude error is 2.3190468138462996e-17. The previous red witness and failed source identity are retained. Gate: ACCEPTED_BOUNDED_PANEL_RESTRICTION, conditional on consumer use of both amplitude parts. Paired-parent feedback and inverse moment fitting remain outside scope.

## Subnormal geometry correction independently accepted

A subsequent owner self-review identified a second arithmetic coverage gap: a right-front restriction on [-2u,-u] for u=MIN_SUBNORMAL quantizes the expm1 normalized-energy target. The reviewer executed the actual pre-guard module and obtained 0.4166666666666667 instead of 4/9 up to O(u), retaining `PANEL_SUBNORMAL_RED.json`. The final module rejects nonnormal geometric width, stretch or taper scale before quadrature. The reviewer recompiled and reran the same witness: `REJECT Err(Arithmetic)`. Final bounded panel gate remains accepted; unsupported subnormal geometry is fail-closed, not inaccurately promoted.
