# Frozen confidence-union implementation

Execution status before controller release: NOT_RUN. The only scientific entry
point is `code/run_science.py`, invoked once by `code/run_bounded.py`. The latter
checks prefrozen executable, code, tests and input hashes before launching the
bounded child. No predecessor suite, IVP or presentation renderer is invoked.

`confidence_union.py` implements the frozen contract with standard-library
Fraction LDL solves for the small covariance and 2-by-2 normal system. Source
decimal values are exact rationals. A separate floating Cholesky checks positive
definiteness without jitter; whitened two-column reorthogonalized QR checks
numerical rank. No explicit covariance inverse or variance estimate is needed.
Only ellipsoid square roots, quantiles and output serialization use floats.

The new tests use exact algebraic identities, independently evaluated nested
residual sums of squares at the same nuisance, direct endpoint response fits,
ellipse quadratic radii, analytic three-row/two-row cases, an interior
zero-crossing minimum, and a positive deterministic slope whose statistical
interval crosses zero. Synthetic evidence is explicitly separate from the
seven-row source in `RESULT.json`. Numeric comparisons retain rtol=1e-10 and
atol=1e-12. No full corner campaign is performed.

After release, the single runner writes raw stdout/stderr, one start marker,
one receipt with environment/hashes/limits/usage/cumulative accounting, and
(only if tests pass) `RESULT.json` plus `intervals.tsv`. Existing start markers
prevent a repeated attempt. Failures stop for the controller. Original source,
blind source, and theory contract SHA identities are all checked.

The runner snapshots full parent and child CPU usage. Receipt serialization
tail and historical unobserved work remain UNKNOWN_NOT_ZERO; conservative
known-plus-reserve accounting is not a global budget PASS. The temporary unit
ends with original policy caps restored while retaining all cumulative debit.
Figures are NOT_RUN_BUDGET_DEPENDENCY because the presentation allowance is zero.

Conditional Gaussian coverage requires the contract's fixed known covariance,
fixed design/template/response/domain, correct additive affine mean, and true
nuisance in the declared domain. The computed source interval is not primary
data reacquisition or a physical closure claim. Fresh Astra review remains
required for scientific admission. No commit or push is performed by this code.
