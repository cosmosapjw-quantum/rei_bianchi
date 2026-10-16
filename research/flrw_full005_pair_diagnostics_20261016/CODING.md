# FULL005 pair diagnostics implementation

## C1 — goal and baseline

The frozen R10 contract calculates continuous piecewise-linear reconstruction diagnostics using dimensionless d ln(a). Baseline file hashes match CONTRACT.json. The supplied snapshot has no Git metadata; publication belongs to the controller/publisher. R10 immutable capture released this implementation. Existing successful FULL005 postprocessing and physical validation are reused; native solver runs and physical-history reads in this unit remain zero. All tests below use small synthetic arrays or files. Current actual full-history continuous norms remain NOT_RUN.

The helper and standalone use only Python standard library. Test-only moderate-fixture comparisons use the frozen relative 1e-12 and absolute 1e-14 tolerances; these are not physical acceptance thresholds. C9 and C10 belong to the independent reviewer and publisher.

## C2 — equations, data and code

`reader.FIELDS`, `SPECIES` and `CLOCK` define the identical 16 observables and clock. A direct standalone loader constructs those arrays from history and abundance streams, hashes each stream inline once, and verifies numeric shape/order prerequisites. The successful prior receipt transfers unchanged physical and ledger validation through content identity. The new helper maps the union partition and R5 segment formulas to per-observable accumulator state. A minimal opt-in caller hook writes the new JSON/CSV after the existing sampled comparison. See coding_evidence/C2.json for the full mapping.

## C3 — numerical design

The helper validates arrays without copying, locates the overlap brackets, and streams exact-equality merged knots. Own-knot values bypass interpolation; interior queries use convex weights. Endpoint differences determine the supremum and analytic L1/I2 contributions. Normalized endpoint values avoid unnecessary squaring overflow, and Neumaier sums retain O(k) auxiliary state. Every computed output must be finite. Strict maximum replacement preserves the earliest exact floating tie. Ordinary binary64 rounding and underflow remain within the declared arithmetic scope.

## C4 — execution and resources

Implementation precedes targeted implementation tests, independent rational/science checks, then a bounded 2,000/20,000-knot single-observable synthetic benchmark. The benchmark records CPU, wall and traced auxiliary memory with input arrays allocated before measurement. Native solver runs and physical-history reads are zero. The exact commands and stage owners are in coding_evidence/C4.json. C8 completion hands observed results to the fresh independent reviewer; actual full-data execution belongs to a future owner action under the retained external budget.
