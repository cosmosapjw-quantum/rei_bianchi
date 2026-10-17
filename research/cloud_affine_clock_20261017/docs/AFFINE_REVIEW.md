# Independent review: prescribed-affine scalar birth clock

## Scope and review basis

Read-only inspection of `crate/src/affine_birth_clock.rs`, `crate/tests/affine_birth_clock.rs`, `crate/examples/affine_probe.rs`, `scripts/check_affine_oracle.py`, and `evidence/AFFINE_ORACLE.json`. No tests, probes, or symbolic computations were rerun by this reviewer.

This API is a supporting scalar Duhamel reference for externally prescribed nonnegative affine emission and opacity rates, at fixed photon energy and proper volume. It does not compute gas evolution, allocate species events, or integrate geometry. Its admission cannot complete a coupled H/He/D, variable-Bianchi, or full source-age gate.

## Decision and closed numerical finding

**PASS, strictly scoped to the prescribed-affine scalar reference and its explicit supported numerical domain.** Final code inspection confirms closure of the preprocessing-underflow finding below. No blocking issue remains in the reviewed revision.

The initial implementation averages rate endpoints before multiplying by duration, and halves duration before constructing quadrature weights. This can silently underflow despite a representable physical integral. For example, equal emission endpoints `f64::from_bits(1)`, duration `1e300`, zero opacity, and zero old inventory should inject approximately `4.94e-24` photons per volume, but halving the endpoints first produces zero. The constant-kernel route cannot recover information already lost in preprocessing.

The revised implementation now forms duration-scaled endpoint integrals `h*j_i` (number density) and `h*lambda_i` (dimensionless optical depth) first, computes their stable mean, and constructs quadrature weights/tail depths from those scaled values. Positive products rounded to zero and nonfinite products fail closed. The variable branch additionally rejects positive subnormal endpoint integrals; the constant branch may use the existing hardened Phi kernel. This deliberately excludes some inputs whose exact averaged integral would fit but whose endpoint products do not. That conservative restriction is acceptable when stated explicitly.

The added rate/time-rescaling test covers the original minimum-subnormal-rate counterexample and a large-duration reciprocal rescaling. A dedicated test rejects unsupported subnormal variable integrals. A reciprocal very-small-duration/large-rate regression would further improve coverage but is not a blocker for the inspected multiplication ordering.

## Correct mathematical structure

- The total optical depth is the exact integral of affine opacity; the tail optical depth from a birth node to the interval end is its exact trapezoidal integral.
- Two Gauss nodes use positive weights. Identical node weights supply survival through `exp(-tail)` and absorption through `-expm1(-tail)`.
- The integrated affine birth count is exact in real arithmetic, and the paired survival/absorption weights preserve the scalar photon ledger up to floating-point arithmetic.
- Constant emission and opacity use the exact uniform-source Phi kernel. Variable-rate intervals reject integrated optical depth greater than one. That restriction is not an error estimator or certificate.
- Zero duration is explicitly an identity after endpoint validation. Inputs are values and the API is stateless, so failed calls cannot mutate a history.

## Evidence and order interpretation

The refreshed `evidence/AFFINE_ORACLE.json` and `affine_oracle_v2.stdout`, generated from `affine_probe_v2.stdout`, contain 24 rows: three genuinely affine manufactured rate pairs and one constant pair, each subdivided into 1, 2, 4, 8, 16, and 32 intervals. The independent 100-digit mpmath birth integral and symbolic affine hazard/injection identities support the stated fixture results. The script checks global photon residuals, constant-branch accuracy, and observed order between 3.8 and 4.2 for the refined variable cases. The refreshed result reports `PASS_SCOPED`. These are sampled regression gates, not rigorous error bounds. The final inspected `affine_guard_tests.stdout` records ten passing affine tests; this reviewer did not rerun them.

For genuinely affine prescribed rates, the two-node quadrature has local fifth-order integral error and generally fourth-order global convergence under coherent refinement. Approximating arbitrary smooth physical rates by endpoint-linear interpolation normally introduces second-order error. Neither conclusion transfers automatically to gas-dependent opacity or operator-split chemistry.

## Remaining boundaries

There is deliberately no species allocation. If future consumers require H/He/D events with changing channel fractions, they must integrate those channel events consistently; splitting total absorption by a single opacity ratio is not generally correct. At fixed externally chosen energy, scalar count conservation implies the corresponding photon-energy accounting, but this API does not itself validate thermal or chemical energy.

The existing finite fixture set does not certify every floating-point dynamic range. The old-inventory, injected-count, and rate integrals must remain finite; unsupported extreme products may fail closed. Small-increment accuracy cannot be inferred solely from an inventory-scaled conservation tolerance.

The work is appropriately described as a joint-quadrature prerequisite/reference. Full P4, SA-01, SA-02, FLRW-CONV, BI-SIGNED, coupled higher-order convergence, and FULL_EOR remain outside its admission.
