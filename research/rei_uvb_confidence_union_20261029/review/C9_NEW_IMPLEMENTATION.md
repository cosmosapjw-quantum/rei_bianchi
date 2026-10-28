# C9 new confidence-union implementation review

**Scientific verdict: PASS_SCOPED.** The new implementation computes the frozen GLS confidence-union formulas correctly for its explicitly declared decimal-rational input interpretation, with floating quantiles, square roots and output rounding. Actual preserved evidence records eight grouped tests passing and child exit zero. The reported scalar95 kappa interval excludes zero; the projection of the joint2 95% union includes zero. These are conditional numerical conclusions under the reviewed sampling model.

**Accounting verdict: local metadata correction accepted; no scientific replay required.** The raw receipt omits 0.001970 seconds of observed prelaunch child CPU from its aggregate debit. The subsequently inspected `outputs/RESOURCE_ACCOUNTING_ADDENDUM.json` adds that amount, preserves the original receipt, and retains the unknown tail/overhead. This resolves the local arithmetic omission. It does not establish global budget PASS. No source or execution change was needed for this correction.

## Reviewer and actual evidence

Reviewer `/root/uvb_code_review` did not implement the new code. Its earlier independent R6 theorem review is separately recorded. This review read the new source, launcher, runner, tests, frozen intake/contract bindings, manifest, raw stdout/stderr, receipt, result and TSV. No old or new scientific suite, Python worker, CAS or renderer was run. Read-only SHA checks verified every entry in the frozen manifest, including the Python executable, and all output digests in the receipt. Requested role is scientific review; the tool interface does not expose an observed backend model identifier.

| Artifact | Verified SHA256 |
|---|---|
| `code/confidence_union.py` | `e975ba4a90934a7b0772c1a604c6f73a0b9cc83ef04379b3118692bb9f68f82a` |
| `code/run_science.py` | `cd18484e17f70aeda6077b3bb1b83e0a6dc36fc249107297e9a32579d43584eb` |
| `code/run_bounded.py` | `3b8be9bfc235b3e417bfc4495c1775ed3dd4cb0342c0515190968f3047c9fc1d` |
| `tests/test_confidence_union.py` | `75b25469e96ea48a47caa8cf9f7e8dd9a74eab4404f73f847a7e7c3ad95a129c` |
| `outputs/FROZEN_SHA256SUMS` | `159e96a2ddcbf0cfb34ab04473fd97db1d82acbc5b29e13940f1e32fc525141e` |
| `outputs/RESULT.json` | `f38b788c3470aac6ec63541c7c9f6c42f89211700b4ee33499f1c5c6c289f6e4` |
| `outputs/RUN_RECEIPT.json` | `4fbe497e3045428ce7c8bc5041aee37e2fe5c738173bb34a7de4bd3b305656f2` |

Raw `STDERR.txt` lists the eight test methods, `Ran 8 tests in 0.028s`, and `OK`. Receipt status is EXIT_ZERO, exit_code=0, elapsed wall=0.1520509799993306 seconds, with Python 3.12.14 and standard-library-only dependencies. These are preserved actual-run observations, not a fresh test execution by this reviewer. Source/result hashes and raw logs support their binding to the inspected code.

## Formula and source mapping

The intake contains the same seven observations, template values, full correlated covariance, EOS direction and Jeans bounds inspected in original-source C9. `load_source` checks intake, original and contract hashes. The algebra uses all entries of C. Finite dimensions, symmetry, ordered bounds and theta convention are checked before fitting. Exact LDL checks positive pivots and solves C systems without materializing its inverse. A separate floating Cholesky and reorthogonalized two-column whitening check validates numerical SPD/rank prerequisites. The exact 2x2 information-matrix solve is an appropriate stable alternative to floating QR for this small task; it has no elimination-roundoff error.

`wx` contains the two vectors `C^-1 X[:,k]`. Thus the constructed H is `X^T C^-1 X`, V is `H^-1`, and A is `V X^T C^-1`. `fit` forms the source response afresh with the correct positive corrections. Center and generator construction match `c=A(r+jc)` and `G=[Av,A diag(jh)]`. Support uses exact signed-generator sums; nuisance witnesses choose source endpoints by the corresponding coefficient signs, with midpoint/zero ties. The saved kappa-min witness has theta=+1 and the expected Jeans choices; the source convention maps this theta to gamma=1.6. A sign reversal of v would preserve an unlabeled symmetric hull but would change these source-labelled witnesses.

Confidence support uses `h_Z(s)+sqrt(q*s^T V s)` and displacement `sqrt(q)*V*s/sqrt(s^T V s)`. All off-diagonal V terms enter the displacement and oblique support. q=0 and zero direction are explicitly handled. Projection formulas and one-coordinate versus joint quantile labels are correct. The implementation does not estimate residual variance or use residual degrees of freedom for q. The two-row synthetic control specifically checks the known-C behavior when residual degrees of freedom vanish.

`nested` profiles the intercept using C solves and compares it with the affine fit at the same theta/j. `delta_q_range` minimizes squared slope over its complete interval, using exact convex nuisance interpolation for an interior zero. `lo==hi` is guarded; a zero endpoint is also valid. This handles the earlier R6 degenerate-range concern in code. The statistic is labelled as pointwise nested improvement, not a separately nuisance-profiled global statistic.

## Precision and representation finding

The new core uses `Fraction(str(value))`, including decimal pivot 3.6. Original PR257 uses `Fraction.from_float` and an exact binary64-image pivot. The new exact algebra therefore concerns the decimal round-trip interpretation of the parsed source numbers, not identical rational values to original PR257. Both source hashes remain correct; a byte-identical source can still be assigned different real-number interpretations. The code docstring and `test_evidence.source_algebra.arithmetic` disclose the new interpretation.

This distinction is **nonblocking for the present rounded numerical scope**, and is explicitly admitted here rather than silently treating the two rational models as identical. Previously saved original versus new deterministic kappa endpoints have identical displayed binary64 values; beta upper differs by about 7e-18. Saved Vkk changes from `0.00058681754958801291` to `0.0005868175495880131`, about 2e-19. These observed differences are far below the original deterministic comparison tolerance. No predecessor suite was rerun or its tolerance relaxed. No new theorem of bit-identical rational equivalence is claimed.

Fractions provide exact matrix identities and deterministic support within the new decimal interpretation. `NormalDist.inv_cdf`, `log`, `sqrt`, Fraction-to-float conversion and serialized endpoints are rounded binary64 operations. No directed rounding or interval arithmetic is implemented. Accordingly the JSON/TSV intervals have evidence status **numerically_checked**: they are numerical approximations to the mathematical confidence sets, not outward-certified enclosures or an exact-machine proof of 95% coverage. The mathematical coverage theorem and its explicit statistical assumptions remain the source of the confidence interpretation. Current sign margins are many orders larger than observed numerical residuals; this does not justify general certification for arbitrary ill-scaled inputs or arbitrarily tiny/huge directions.

## Test quality and observed result

Tests use exact AX=I and ACAT=V identities, independently formed residual normal equations, direct nested residual sums, displaced-coefficient quadratic completion, and residualized slope precision. These checks are stronger than comparing stored booleans. Some routines share the same LDL implementation and source model, so they are not a fully separate source solver. Independent analytic three-row A/V/Q values, a two-row known-C example, tabulated quantiles, an interior-zero example and a positive-deterministic/statistical-crossing example supply additional non-tautological controls.

Support is checked against direct corrected-response fitting at signed coordinate/oblique witnesses, rather than only the center/generator expression. Ellipsoid radius and attainment are checked independently through H and endpoint dot products. Saved joint-q ellipsoid residuals are around 1e-15 and the largest reported support-attainment residual is about 5.6e-17, within the new algebraic tolerances. Scalar-q output uses the same reviewed formula; the executed explicit radius controls focus on joint q. Degenerate `[0,0]` delta-Q behavior is guarded statically but does not have its own executed test. These are nonblocking limitations for the observed source and declared contract; no extra replay is warranted.

| Kappa quantity | Lower | Upper | Zero |
|---|---:|---:|---|
| Deterministic support | 0.053617504767915498 | 0.099225339666118351 | Excluded |
| Conditional scalar95 union projection | 0.0061387152719417776 | 0.14670412916209208 | Excluded |
| Conditional joint2 95% union projection | -0.0056774911759022301 | 0.15852033560993609 | Included |

Units are dex per redshift. The two confidence rows answer different coverage questions, and the pair of coordinate projection intervals does not itself describe the full joint set. Pointwise delta-Q ranges from approximately 4.899030064039117 to 16.77807359164515. Its numerical range is not a calibrated nuisance-profiled p-value.

## Accounting finding and minimal correction

`run_bounded.py` forms its debit as full parent-self CPU plus `children_after-children_before`. The raw snapshots are parent_self=0.066671, children_before=0.001970 and children_after=0.095978 seconds. Therefore the reported 0.160679 seconds excludes known observed prelaunch child CPU. For the full observed launcher family, the inclusive snapshot is `0.066671+0.095978=0.162649` seconds. The cause of that prelaunch child is not established by this review and need not be invented to count its observed cost.

The controller's additive correction is sufficient: preserve the raw receipt and frozen launcher, add the missing 0.001970 to the ledger, and record the inclusive snapshot. With prior known-plus-reserves 608.750604 and sibling reserve 70, this yields 678.913253 seconds. Adding the retained 1-second unmeasured-tail reserve gives 679.913253, below the temporary 700 ceiling. The 1 second is a reserve, not measured tail CPU or proof of a global upper bound. Parent receipt serialization, review/model/tool/metadata overhead and historical unobserved costs remain UNKNOWN_NOT_ZERO. The local correction requires no scientific recomputation. This reviewer subsequently read `outputs/RESOURCE_ACCOUNTING_ADDENDUM.json` and confirmed it records these corrections, retains the over-baseline balance, creates no new execution allowance, and preserves the global unresolved verdict.

The launcher applies per-process caps to itself and the child; the 10-second family reservation is not a single kernel-enforced aggregate cap, and startup occurs before `limits()`. Actual observed use is well inside the reservation. No heavy execution, old campaign replay, figure or IVP occurred in this recorded run. The receipt's global unresolved verdict must remain unresolved after the arithmetic correction.

## Admission and remaining obligations

The source, code, contract, raw tests and numerical outputs support **PASS_SCOPED for this conditional decimal-rational GLS model with rounded confidence-union numerics**. No blocking scientific code repair is identified. The separate accounting addendum resolves the observed local omission. Carry the representation/rounding qualification into final reporting and preserve the frozen run and existing original reviews.

Gaussianity, a correct fixed-template additive mean, known covariance, true nuisance inside the outer box, observational selection and physical joint attainability remain model/data assumptions. This review does not promote them, physical F4/L4/native25, temperatures/radii, or the central DAG. New IVPs remain zero. Only this review and its JSON companion were written by this reviewer.
