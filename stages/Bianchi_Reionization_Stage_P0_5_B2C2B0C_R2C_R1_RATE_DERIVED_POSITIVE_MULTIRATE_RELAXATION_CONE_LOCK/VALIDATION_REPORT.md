# R2C-R1 validation report

## Fresh checks executed at closeout

- unit tests: `19 passed`;
- independent output validator: `PASS`;
- exact SymPy/90-digit Decimal/100-digit mpmath fallback: `PASS`;
- repository verifier before registry update: `PASS`;
- 540 unique macro result rows, 540 dual rows, and 540 trajectory rows;
- 497 self-contained Farkas certificates independently replayed;
- 43 self-contained KKT certificates independently replayed;
- 540 literal structural-zero rows;
- no node-rate fitting, clipping, or dynamic KL projection.

Machine-readable receipts are in `receipts/` and the corresponding stdout logs
are in `logs/`.

## Independent replay maxima

| gate | value | tolerance/status |
|---|---:|---|
| Farkas minimum positive box gap | `1.060054463e-02` | positive |
| largest normalized Farkas `h.y` | `-8.645235618e-14` | negative |
| KKT relative stationarity | `2.026618404e-16` | `<1e-11` |
| relative duality gap | `1.039307529e-13` | `<1e-11` |
| complementarity | `1.039772222e-13` | `<1e-11` |
| endpoint relative residual | `5.707954323e-17` | `<2e-11` |
| current-Gamma relative residual | `9.143461260e-16` | `<2e-11` |
| Taylor interval evaluations | `37` maximum | `<200000` |
| Taylor depth | `11` maximum | `<24` |

The raw HiGHS absolute stationarity residual is not used as the acceptance
metric because it is not scale invariant under `1e11` dual cancellation. The
stored active-set NNLS certificate and the independent replay use the
componentwise scale

\[
|c_i|+\sum_j\lambda_j|G_{ji}|,
\]

which tests the actual KKT cancellation. The initial fallback that divided
only by `|c_i|` is preserved and labelled a false negative.

## Analytic trajectory certificate

The final auditor is a centered fourth-order Taylor expansion with a Lagrange
remainder on dyadic intervals. Derivative contributions are summed before
absolute values are taken, preserving cancellation between nearly equal
exponential modes. It returns only:

- `CERTIFIED`;
- `REAL_NEGATIVE_SLACK` with an explicit sample;
- or fail-closed work/depth exhaustion.

The superseded direct interval decomposition that branched explosively is
preserved as Attempt 6. The final run used at most 37 interval evaluations and
depth 11.

## Symbolic and special-function verification

`wolfram_r2c_r1_multirate_cone_validation.wl` contains the canonical Wolfram
checks. Native Wolfram and the requested special-function plugin were not
exposed in this runtime, so their execution is not claimed. The exact fallback
checks:

- one-mode endpoint identity;
- two-mode endpoint attenuation identity;
- exponential derivatives through order eight;
- active and inactive KKT complementarity;
- a representative self-contained Farkas ray at 90 digits;
- a representative KKT certificate at 90 digits;
- exact structural zeros;
- `Gamma(3/2)=sqrt(pi)/2` at 100 digits.

All fallback gates pass.

## Preserved failed attempts

1. `ATTEMPT_1_TWO_MODE_BOUND_ROUNDOFF_ABORT`
2. `ATTEMPT_2_CONCURRENT_RUN_OUTPUT_TRUNCATION`
3. `ATTEMPT_3_TOOL_EXECUTION_TIMEOUT_PARTIAL`
4. `ATTEMPT_4_ABSOLUTE_KKT_CANCELLATION_FALSE_NEGATIVE`
5. `ATTEMPT_5_HIGHS_MARGINAL_KKT_PRECISION_FAIL`
6. `ATTEMPT_6_DYADIC_CERTIFICATE_BRANCH_EXPLOSION`
7. `ATTEMPT_7_SUMMARY_LANE_COUNT_SEMANTICS`
8. `ATTEMPT_8_CERTIFICATE_PAYLOAD_NOT_SELF_CONTAINED`
9. `ATTEMPT_9_FALLBACK_KKT_SCALE_FALSE_NEGATIVE`

No attempt is overwritten by the final run.
