# BASS_HE CODE-I02 R6 post-implementation research loop

Date: 2026-09-29 KST
Scope: post-implementation repository survey, adversarial design research, and L2 theory development. No production source was modified.

## 0. Fresh repository state

Fresh GitHub reads show that R5 has now been implemented.

### PR #15

Current HEAD:

`b8b2fe47a367459f6faf6796eb2f251feacbbd7c`

tree:

`f5777ecf0b648cd5b4124bc170e9b5a5f3b38db8`

Lineage from the previous reviewed target:

- baseline: `ac04d2a9e62120a0da4377ddf92451fde0c44431`
- first R5 implementation: `d507989da43423f1226468b06a258daa33058ffa`
- final source/test commit: `8bf9ce27a39be06d2487fffd40c2b97a2cdb3e1a`
- final branch HEAD: `b8b2fe47a367459f6faf6796eb2f251feacbbd7c`

The final HEAD is one commit ahead of `8bf9ce2` and adds only the final backup receipt. Therefore code-review identity should distinguish:

- source/test identity: `8bf9ce27...`, tree `54c522773944ca00d3eee0b91952ffce5ecd413a`;
- publication/branch identity: `b8b2fe47...`, tree `f5777ecf0b648cd5b4124bc170e9b5a5f3b38db8`.

Current source blobs include:

- `src/bass_he/spectral.py`: `c41dc2bfacff6140fc130a787a856eae389a23b4`
- `tests/test_code_i02_r5_admission.py`: `d62681d71cd96d1dc11dc849315f44060d73e2c6`

### Implementer evidence

`RED_GREEN_EVIDENCE.json` reports:

- initial R5 RED: 28 failed, 1 passed;
- additional RED cases for caller-cache injection, extended-precision alias, and integer-charge compatibility;
- final focused GREEN: 57 passed;
- final repository suite: 189 passed in 58.33 s;
- compileall exit 0;
- `git diff --check` exit 0;
- cold semantic revalidation ~0.713 s;
- repeated exact cached validation ~0.000214 s;
- one-ULP R change cache miss ~0.719 s.

These are implementer-generated evidence, not an independent rereview.

The implementation keeps:

- `CODE_I02_CLOSED=false`
- `scientific_PROMOTE=HOLD`
- `Eq55_next_node_authorized=false`
- `Eq55=NOT_RUN`.

## 1. What the implementation now does

Source inspection confirms the intended R5 architecture:

1. stored binding is canonicalized as deterministic JSON bytes with `allow_nan=False`;
2. stored digest is checked against the stored canonical bytes;
3. policy tolerance/probe scale are verifier-owned constants at admission;
4. `passed` and stored `simple_fold` must be strict Python `True`;
5. matching error must be strict float64/Python-float, finite and nonnegative;
6. the current endpoint is freshly revalidated through `spectral_certificate` and `_pair_membership_certificate`;
7. `sturm_geometry.contour_geometry` calls the validator before the first real anchor;
8. a process-local semantic cache is addressed by SHA256 of canonical exact identity plus a code-owned verifier revision.

This directly addresses the previously demonstrated stale/alias/fabrication attacks at the runtime admission boundary.

R6 does not independently certify that these changes close CODE-I02. That remains the next review node.

## 2. New research issue P1: exact stored-error equality versus portability

The validator currently requires

`stored_error.hex() == fresh_error.hex()`.

This is stronger than the actual membership predicate.

The literature on reproducible floating-point computation shows that bitwise reproducibility is not automatic across platforms, reduction orders, thread schedules, or linear-algebra implementations. BASS_HE uses SVD and nonlinear solves in the fresh revalidation path, so cross-host bitwise identity must be demonstrated rather than assumed.

This is not currently evidence of false admission. The exact-hex rule is fail-closed. The risk is false rejection / portability failure when a legitimate restored certificate is checked on another supported numerical environment.

The representative hostile-review endpoint had:

- matching error `3.156324676166531e-11`;
- policy tolerance `5e-6`;

a threshold/error ratio of about `1.584e5`. This is a large empirical margin, but not a cross-platform error bound.

### Matching-error stability theorem

For the 2x2 distance matrix D,

[
E(D)=\min\{\max(d_{00},d_{11}),\max(d_{01},d_{10})\}
]

is 1-Lipschitz in the componentwise sup norm:

[
|E(D)-E(D')|\le\|D-D'\|_\infty.
]

Thus if the four distances had rigorous interval enclosures, membership itself could be certified by the upper/lower enclosure of E, without bitwise reproducibility.

### Decision deferred to independent rereview

Two contracts are coherent:

- environment-bound record: retain exact hex equality and bind the numerical environment as part of the record contract;
- portable semantic record: fresh semantic revalidation owns admission, while stored matching error becomes diagnostic metadata rather than a bitwise cross-host authority.

R6 does not modify the implementation. The independent reviewer should determine which contract PR #15 actually claims.

## 3. New research issue P2: policy SSOT drift risk

The verifier now defines:

- `PAIR_MEMBERSHIP_TOLERANCE = 5e-6`
- `PAIR_MEMBERSHIP_PROBE_SCALE = 1e-4`

but `_pair_membership_certificate` still has literal defaults:

- `tolerance=5e-6`
- `probe_scale=1e-4`

and `find_exceptional_point` invokes that function without explicitly passing the verifier constants.

The values are identical now, so this is not a present scientific mismatch. But it creates two policy spellings. A future policy edit could change the verifier constants without changing constructor defaults, causing newly generated certificates to disagree with the verifier.

Classification in this research loop: latent policy-SSOT maintenance risk, not a current CODE-I02 failure. The independent reviewer should decide whether closure requires eliminating this duplication or merely documenting it.

## 4. Cache/source identity assessment

The process-local cache includes:

- verifier revision string;
- reconstructed binding;
- original `Z1/Z2` scalar type tags.

The R5 tests explicitly close nested tuple aliases, extended-precision aliases, one-ULP misses, policy/revision misses, and caller-injected alternate cache objects.

Because the cache is process-local, it cannot silently reuse a previous process's result after a Git checkout changes. The manual `SEMANTIC_ADMISSION_REVISION` remains a maintenance contract rather than a cryptographic transitive-source hash. For the current process-local scope this is reasonable; a future persistent cache would need exact transitive source identity.

## 5. L2 theory progressed in parallel

R6 derived an analytic second-order CF recurrence suitable for a future interval/Krawczyk fold certificate.

For

[
q=B-\frac{AC}{D},
\qquad N=AC,
]

the Hessian update is

[
q_{ij}
=
B_{ij}
-\frac{N_{ij}}{D}
+\frac{N_iD_j+N_jD_i+ND_{ij}}{D^2}
-\frac{2ND_iD_j}{D^3}.
]

The radial coefficient Hessians were derived explicitly; angular coefficient Hessians vanish because the angular coefficients are affine in ((p,\lambda,R)). SymPy symbolic checks returned zero residual matrices for the proposed formulas.

For the augmented fold system

[
H=(F_1,F_2,\det J_z),
]

the identity

[
\partial_\xi\det J_z=
\operatorname{tr}(\operatorname{adj}J_z\,\partial_\xi J_z)
]

means that an interval enclosure of DH needs only second derivatives of F, not third derivatives.

This turns L2-A into a concrete future implementation program:

1. interval value/gradient/Hessian propagation through every CF recurrence;
2. interval exclusion of every denominator from zero;
3. realified six-dimensional Krawczyk/interval-Newton certification of the augmented fold.

Pair membership remains a separate L2-B validated-continuation problem.

No interval/Krawczyk code was executed in R6.

## 6. Literature support

SciSpace retrieval added two useful strands.

### Portability/reproducibility

- Demmel & Nguyen, ARITH 2013, DOI `10.1109/ARITH.2013.43`;
- Collange et al., Parallel Computing 2015, DOI `10.1016/J.PARCO.2015.09.001`;
- ExBLAS reproducible BLAS work;
- Revol & Théveny on reproducibility and interval algorithms.

The important distinction is that bitwise reproducibility and validated inclusion/correctness are different properties.

### Future rigorous continuation/certification

- Krawczyk-like nonlinear system algorithms, DOI `10.1137/0722048`;
- validated nonlinear systems, DOI `10.1137/0731013`;
- Breiding–Rose–Timme, DOI `10.1145/3580277`;
- certified homotopy tracking via parametric Krawczyk, arXiv:2402.07053;
- higher-order AD continuation/bifurcation, DOI `10.1080/10556788.2018.1428604`.

SciSpace did not return extra `methodology`/`conclusions` columns for the selected papers, so no stronger paper-specific claims are made beyond indexed metadata/abstracts.

## 7. Wolfram status

Fresh Wolfram calls for the R6 portability theorem were attempted repeatedly, including a minimal evaluator sanity call, but the connector returned internal tool errors. No fresh Wolfram result is claimed.

Prior R5 Wolfram results remain preserved in the repository and are still relevant:

- `det(realification(J)) = |det J|^2`;
- `d(det J)=Tr(adj(J)dJ)`;
- adapted fold augmented determinant `=-a^2 alpha beta`.

The new R6 CF-Hessian identities were checked with SymPy, not Wolfram.

## 8. Converged next step

The canonical next node is separate independent rereview of current PR #15 HEAD.

The rereviewer should reproduce the original hostile attacks and also answer two R6 questions:

1. Is exact stored matching-error hex equality part of an intentionally environment-bound record contract, or does it create an unacceptable cross-host portability false-negative for the project's restored-certificate workflow?
2. Is the duplicated policy default a closure blocker, a minor maintenance finding, or acceptable current-state duplication?

Do not reopen Eq.(55), run 56-action replay, or start L2 interval work before this rereview.

## 9. Gate

- `CODE_I02_CLOSED = false`
- `full_certificate_fail_closed = PENDING_INDEPENDENT_REREVIEW`
- `scientific_PROMOTE = HOLD`
- `Eq55_next_node_authorized = false`
- `Eq55 = NOT_RUN`
- R5 implementation = `IMPLEMENTED_WITH_IMPLEMENTER_GREEN_EVIDENCE`
- independent closure = `NOT_RUN`
