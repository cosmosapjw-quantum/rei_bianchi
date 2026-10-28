# Original PR257: independent phase-2 scientific review

Decision: **R6 PASS_SCOPED; C9 PASS_SCOPED for the original deterministic
source-bound GLS support implementation and reused saved mathematical results.**
The admitted result is the exact image of the declared EOS/Jeans outer box for
the frozen represented-real seven-row input and fixed template. This decision
does not change resource accounting, global physical gates, or historical
execution records. It does not admit empirical Gaussian significance.

Reviewer: `/root/uvb_theory_review`, a distinct task from the original producer.
Requested execution identity: Astra-tier independent theory/review. Observed
runtime model identity: unavailable. No model identity is inferred from routing.

## Independence and evidence boundary

I froze a source-only derivation before reading original theory, result, code,
or other review. The two unchanged phase-1 records are:

- `PHASE1_THEORY.md`, SHA256
  `7ecbfb7292c804ee9e9fd5b479f9563ec4b8330a1c2e0710f70cef52d2885061`.
- `THEORY_CONTRACT.json`, SHA256
  `0eb1134b7ff1f4554789d391e70ae0d24804f7f0fefe840cfa5f24012e48bcd1`.

After explicit phase-2 authorization I read original
`research/rei_uvb_eos_jeans_box_20261029/` source JSON,
`THEORY_AND_CONTRACT_KO.md`, `code/jeans_support.py`,
`code/reference_numpy.py`, `tests/test_saved_support.py`,
`results/EXACT_SUPPORT.json`, `results/NUMPY_REFERENCE.json`, the RUN,
REFERENCE and TESTS stdout/stderr/time/exit records, `FROZEN_EXECUTION.json`,
and `RESOURCE_ACCOUNTING_ADDENDUM.json`. I read no other review before this
verdict. No numerical suite, prior scientific worker, IVP, or plot was rerun.

The command `sha256sum` confirmed the actual source JSON bytes as
`13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b`.
By direct reading, its z, observed log rates, fixed template, C, v, theta bounds,
and Jeans lower/upper arrays match my blind intake. Metadata in the source
explicitly describes binary64 images as exact real numbers via
`Fraction.from_float`, not exact published decimal reals or PDF bytes.

The parent reports independent reacquisition of the primary Becker--Bolton
paper and agreement of Table 2's 100*C scaling and Table 1's EOS/Jeans arrays.
That is parent-reported corroboration; I did not independently retrieve or read
the raw PDF. No original-paper raw-PDF byte binding has been established by this
review. The provenance claim admitted here is the inspected frozen source
projection. The fixed Puchwein template's external physical correctness is an
input condition, not re-established by a GLS support calculation.

## Scientific comparison

With a=(beta,kappa), x=z-3.6, X=[1,x], and
r=d-m+theta*v+j, both the original derivation and implementation use

    A=(X^T C^{-1} X)^{-1}X^T C^{-1},
    a=A(d-m)+(A v)*theta+A*j.

The implementation solves C against 1 and x, constructs the symmetric 2x2
information matrix and its determinant, and constructs each column of A using
the correct inverse-information formula. Exact assertions A*1=(1,0) and
A*x=(0,1) are appropriate algebraic controls. The exact elimination and LDL
recurrences are consistent with their stated matrix operations. In the
quadratic routine the stored inverse columns are dotted against the vector;
symmetry of C^{-1} makes this equal to C^{-1} times that vector. No sign or
transpose defect was found for this frozen symmetric input.

The center and half-width code equals the independently derived zonotope
projection, with one common EOS scalar and seven independent deterministic
Jeans coordinates. The lower kappa witness selects theta=+1 because A_kappa*v
is negative; the first two slope weights are negative and the other five
positive, matching the published endpoint witness arrays. Upper witnesses
reverse these selections. A zero coefficient may choose either endpoint; the
implementation's choice differs from my optional midpoint tie convention but
is mathematically equivalent. Full support follows analytically in every
direction from the same linear map, even though the original worker explicitly
checks the four coordinate extrema.

Exact positive LDL pivots and positive information determinant are reused from
the inspected saved run, rather than newly computed. The original source
worker performs these checks before generating its successful result. The
separate saved NumPy reference uses Cholesky plus linear solves and full
256-corner enumeration without importing the exact worker. It corroborates
positive definiteness and the coordinate extrema to the source tolerances.

| Saved quantity | Original exact-worker output |
|---|---:|
| beta lower | -0.13087466565371772 dex |
| beta upper | 0.051206812137275709 dex |
| kappa lower | 0.053617504767915498 dex/redshift |
| kappa upper | 0.099225339666118351 dex/redshift |
| conditional V_kappa,kappa | 0.00058681754958801291 |
| exact covariance positive pivots | 7 |
| nuisance corners checked | 256 |

These are copied saved observations, not new numerical results. The reference
outputs are respectively -0.13087466565371775, 0.0512068121372757,
0.05361750476791549, and 0.09922533966611838. Their displayed differences are
consistent with the original absolute 1e-13 plus relative 1e-11 test criterion.
The original tests, not this review, performed the numeric comparisons.

For identical eta in the nested models, my independent derivation gives

    DeltaQ=Q_intercept_min-Q_affine_min=kappa_hat^2/V_kappa,kappa>=0.

The original theoretical expression using the W-orthogonalized x is identical.
Its code correctly fits the intercept-only and affine responses at each common
corner and asserts their nested nonnegative ordering.

## One bounded evidence-wording finding

**Finding F1 (nonblocking, historical validation description):** the original
theory text says that the nested chi-square identity was checked at all 256
corners. The code actually asserts `q0>=q2 and q2>=0`; it does not numerically
assert equality of `q0-q2` with `kappa^2/Vkk`. Accordingly the saved control
`all_256_nested_chi2` supports the nested inequalities. The stronger identity
is established analytically by the original formula and my independent
completion-of-square derivation. The minimal correction is to describe the
historical execution as 256 nested-inequality checks; no rerun is required for
the original deterministic-support admission. This review records the accurate
scope without editing historical artifacts or claiming a missing test ran.

The cited Wolfram comparison is not used as evidence in this review because
no corresponding raw result was read. No additional scientific defect was
found within this frozen-input scope. No new no-go theorem or novelty is claimed.

## Reused execution and gates

RUN, REFERENCE, and TESTS each have saved exit code 0. RUN and REFERENCE stderr
are empty. TESTS stderr records eight named tests followed by `Ran 8 tests` and
`OK`; TESTS stdout is empty as expected for this unittest runner. Saved run and
reference stdout agree with their saved JSON values. Recorded costs are:

| Reused job | User CPU s | System CPU s | Wall s |
|---|---:|---:|---:|
| Exact source worker | 0.37 | 0.00 | 0.37 |
| NumPy reference | 1.16 | 0.08 | 0.84 |
| Saved-result tests | 0.03 | 0.01 | 0.04 |

These are historical measurements, not a fresh grant or fresh execution.
The accounting addendum separately preserves figure resource concern
`CONCERN_FIGURE_NOT_PREFROZEN`, `global_budget_PASS=false`, unreconciled
inherited entries, and `UNKNOWN_NOT_ZERO` overhead. This scientific review
does not resolve or transfer those costs and does not authorize new plotting.

R6 is closed for the original source-conditional mathematical claim by the
distinct-author blind derivation and phase-2 comparison. C9 is closed in the
same scoped scientific/implementation sense by static source inspection and
reuse of actual original raw execution evidence. R7/C8 numerical evidence is
reused within that scope; no fresh execution is claimed. Whole-project or
resource admission remains a separate controller decision. Historical
`native_independent_reviewer=NOT_RUN` accurately describes the old run and
need not be overwritten; this later record supplies the now-performed review.

The existing physical_F4=PARTIAL, L4_ready=false, null actual_REI_T and physical
radii, no-new-IVP state, and unchanged DAG counters are not promoted here.
Positive deterministic kappa throughout this outer box is admitted as a
deterministic result. Its statistical interpretation requires the separate
conditional Gaussian contract and its known-C, correct-model assumptions;
the original run alone establishes no empirical confidence or discovery claim.

Next allowed scientific use: reuse the accepted source map and original saved
results as the input to the independently frozen confidence-union contract,
subject to the controller's separately established bounded execution allowance.
