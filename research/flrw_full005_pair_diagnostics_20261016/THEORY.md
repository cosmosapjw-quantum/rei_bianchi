# Continuous piecewise-linear FULL005 pair diagnostics

## R1 — research position and contract

The task is to compute the full-overlap maximum absolute difference and integrated L1, L2 and RMS differences of the continuous piecewise-linear reconstructions of two saved adaptive histories in the coordinate `L = ln(a)`. The diagnostic acts on the existing validated history arrays; it does not alter a saved state or the solver. Completion requires the formulas, an independent symbolic or rational check, a discriminating narrow-peak example, a bounded implementation contract and integration into the FULL_PAIR postprocessor.

The inspected reader is `research/flrw_full005_postprocess_20261015/vendor/compare_histories.py`. `load_case` supplies `array('d')` sequences under `case['series']`. `L` is the stored binary64 `math.log(a)` value. Every row has already passed finite-value, strict coordinate/time ordering, H/He fraction, inventory, abundance/history, baryon and charge checks. The comparison observables are every series key except `L` and `time_s`: `xe`, the nine `FIELDS` entries, and the six baryon-normalized species abundances. The FULL_PAIR reader enforces the same represented endpoints, from `a=1/21` to `a=1/5`, and proper time starts at zero at zbar20.

`postprocess_flrw.run` currently calls `reader.compare`, which reports 1001 regularly spaced ln(a) samples. The vendor reader also contains an optional `exact_reconstruction_summaries` path using `reconstruction_support.reconstruction_norm`, an O(n+m) Fraction-arithmetic union-knot supremum with equal endpoints. This existing result is reused as the exact reference for small fixtures. The new work adds analytic integrated diagnostics and a bounded-memory binary64 sweep to the actual FULL_PAIR caller. Union-knot extrema are prior project knowledge, not a new mathematical claim.

The claim concerns saved-history reconstructions and has no continuum-solver error or convergence threshold attached. FULL005 source identity, single energy ownership, H/He normalizations, all-row validation, actual-gas-temperature chronology, elapsed proper-time convention, saved milestone definitions and the source005 admission boundary are preserved. The native solver and source006 experiments are outside this change.

The NCP postprocessor import failure and recovered package are separate environment/execution evidence owned by the controller. Their repair or full-data reduction is not required for this light mathematical and implementation unit.

R1 completion: the representation, integration coordinate, admissible changes and completion evidence are fixed. R2 must map the prior reconstruction helper and selected primary literature; R6/R7 require actual independent and discriminating evidence before scientific adoption.
