# Unit6 lane A: cached residual compression by streamed QR

Frozen 2026-10-16. Scientific author role: requested Astra; observed runtime
model UNKNOWN. This is a standalone opt-in postprocessor specification, not
a change to the active Unit5 runner, allocation, solver, or physical model.
The authoritative executable details are in `RESIDUAL_CONTRACT.json`.

## Object and exact identity

Retain Unit5's saved-space operator K=Q(H−E0)Q, atomic units, and energies in
Hartree (Eh). For cached V and KV, set

    C=V†KV, J=(C+C†)/2, d=u−V[:,0], E=KV−VJ,
    t=(zI−J)^−1 e1, z=ω+iη, η>0,
    δ=(u†V−e1†)t.

No orthogonality assumption on V is needed for the algebra below. The cache
must represent KV for the same self-adjoint K to interpret the physical
resolvent inequality. Since (zI−J)t=e1,

    u−(zI−K)Vt = d+Et.

The resolvent identity and ||(zI−K)^−1||₂≤1/η imply

    |u†(zI−K)^−1u−e1†t| ≤ B(z),
    B(z)=||u||₂ ||d+Et||₂/η + |δ|.

The density bound remains W B/π. Keep the coordinate correction even when
small; keep J rather than C in both the resolvent and E. No last-beta
replacement is allowed. Unit5's refinement rule and historical HOLD are
unchanged. This is a floating-point conditional diagnostic, not an interval
certificate or a new convergence criterion.

Let p=m+1, A=[d,E], x=[1;t]. For any thin QR A=QR with Q†Q=I on its retained
columns, ||d+Et||₂=||Rx||₂. For N<p, a reduced QR has fewer rows in R; the
identity still holds. Rank deficiency does not invalidate QR or require
division by R's diagonal. Do not truncate columns, impose numerical rank,
invert R, replace QR by Cholesky of A†A, or square a residual norm through a
Gram quadratic form. QR phases/signs need not agree across block sizes;
residual norms and final observables are the comparison objects.

For row blocks A_b, reduce each block to R_b; combine by reducing the vertical
stack [R_previous; R_b]. If A_b=Q_b R_b and the stacked R factors equal Q_c R,
the product of the block-diagonal isometry and Q_c is an isometry. Induction
therefore proves ||Ax||₂=||Rx||₂ for every x. An equivalent implementation
directly reduces [R_previous; A_b] at each step. This sequential TSQR variant
needs neither global Q nor global A. Short final blocks and block_rows<p
are valid with reduced trapezoidal R.

## Concrete two-pass cache algorithm

1. Validate finite float64/complex128 inputs V, KV of shape (N,m), u of
   shape (N,), N≥m≥1, real finite W≥0, finite grid and strictly positive η.
   Promote real input to double and preserve complex conjugations. Reject
   integer/object arrays rather than inventing a physical conversion.
2. Stream rows to accumulate C=ΣV_b†KV_b, u†V=Σu_b†V_b and ||u||₂.
   Symmetrize once after the sum. Diagonalize J once, J=Y diag(λ)Y†.
3. Stream rows again. Form only d_b=u_b−V_b[:,0] and E_b=KV_b−V_b J,
   then update R from [R; d_b,E_b] using reduced Householder QR (NumPy QR
   is sufficient). Record Frobenius norms of d, E, KV, V and ||J||₂ for
   numerical scale diagnostics. No operator callback or Hamiltonian module
   is imported. Loading a local NPZ may materialize V/KV, so distinguish
   existing-cache storage from incremental workspace; NPZ is not claimed
   to provide memory mapping or disk streaming.
4. For batches of at most 256 spectral points, form
   t=Y[(Y†e1)/(z−λ)], x=[1;t], and ||Rx||₂; form δ from the cached row.
   Report the same scalar resolvent, residual_norm, coordinate_delta,
   scalar_bound, density_bound, maxima per η and grid trapezoid diagnostic
   as Unit5. A trapezoid sum is not a certified continuum integral.

## Floating-point boundary

For the formed matrix A_hat, backward-stable QR gives, schematically,
A_hat+ΔA=Q_hat R_hat with ||ΔA|| bounded by roundoff times a dimension and
reduction dependent constant times ||A_hat||. Thus residual norm error is
absolute, of order eps ||A_hat|| ||x||, not necessarily relative to the
small residual. Multiple row reductions also accumulate roundoff; no fixed
dimension-independent rigorous constant is claimed. Forming E=KV−VJ can
already lose relative accuracy near invariance. QR cannot restore those
lost digits or correct an inaccurate cache. Its benefit is avoiding the
additional squaring/cancellation of x†(A†A)x, which can turn a positive tiny
norm into zero or a negative number. No Gram clipping branch is needed.

For local acceptance define

    alpha=||d||₂+||E||F ||t||₂,
    rho=||u||₂+||V[:,0]||₂+(||KV||F+||V||F ||J||₂)||t||₂,
    norm_slack=5e−12 max(1,alpha)+50 eps max(1,rho).

Require |norm_QR−norm_direct|≤norm_slack pointwise; record the actual maximum
error, slack and normalized error. This is an engineering acceptance
tolerance for the bounded double-precision fixtures, not a proof of a
production error envelope. A well-conditioned standalone cancellation
fixture additionally requires relative resolution of its tiny residual, so
the broad absolute tolerance cannot hide failure of the intended mechanism.
Record the solve defect q=e1−(zI−J)t and require
||q||≤1e−11 max(1,(|z|+||J||₂)||t||₂). The preserved formula B assumes q=0;
in floating arithmetic an exact bound for the computed t would also need
||u|| ||Vq||/η and rounding margins. Do not describe the unaugmented B as
rigorously certified. Independent dense-resolvent comparison uses the
explicit slack in the contract.

## Cost and limits

Let P be the total number of (ω,η) pairs and b the block size. Cached C,
residual formation and QR cost O(N m²), with sequential reduction overhead
O(ceil(N/b)m³) if b is small. J diagonalization costs O(m³); evaluation costs
O(P m²). Extra factorization workspace is O(bm+m²), plus O(m times batch)
and O(P) outputs. Cached V/KV themselves occupy O(Nm); do not omit that cost
from total memory. Unit5 direct evaluation costs O(PNm) after residual
formation. This removes P large-space residual matvecs in exchange for a
one-time reduction. It is not a claim that a specific production run fits
an allocation or is faster. Local timing includes setup and grid evaluation
for each method, using identical seed, dtype and arrays. Record setup and
evaluation separately and total ratio once; no benchmark tuning campaign.

## Exact and meaningful bounded cases

* K=[[2,1],[1,3]], V=u=e1, z=2+i: J=2, E=e2, t=−i,
  residual_norm=1, δ=0, B=1, exact full scalar (1−3i)/5, and
  scalar error=1/sqrt(5). W=1 gives density_bound=1/π.
* K=diag(1,3), V=u=(1,i)/sqrt(2), z=2+i: J=2,
  E=(−1,i)/sqrt(2), residual_norm=1, B=1, full scalar=−i/2;
  scalar error=1/2. This catches missing conjugations.
* K=diag(2,3), V=2e1, u=e1, z=8+i: J=8, d=−e1,
  E=−12e1, t=−i, |δ|=1, residual_norm=sqrt(145),
  B=sqrt(145)+1. Nonorthogonality is intentional, with no basis gate here.
* K diagonal and V selected coordinate columns with u=V[:,0] is an exact
  invariant case: d=E=0, residual_norm=B=0 (up to computation roundoff).
* A=[e1,e1+1e−10 e2], x=[1,−1] has ||Ax||=1e−10 exactly in real
  arithmetic. QR must resolve it to relative 1e−6 plus 1e−15 absolute.
  Record the Gram result as illustrative evidence only; do not demand that
  every BLAS implementation reproduce a particular Gram cancellation.

Add seeded real and complex Hermitian dense K with N≤512,m≤32, truncated
orthonormal V, deliberately nonorthogonal V, nonzero d, and a near-invariant
case with external coupling 1e−12. Use KV=K@V consistently for all physical
bound tests. C=V†KV is Hermitian for self-adjoint K even if V is nonorthogonal.
Add a separate synthetic cache test KV_bad=K@V+V*S with a nonzero skew-
Hermitian S of norm 1e−5. It must show material C−J and catch C/J mixing by
comparison to direct d+(KV_bad−VJ)t. This deliberately inconsistent cache
tests algebra only: do not claim the self-adjoint-K physical bound for it.
Independent full-space solve supplies u†(zI−K)^−1u on consistent caches. Compare norms to direct
d+Et, not to a Gram reference. Cover block sizes 1, p−1, p and >N, zero E,
rank-deficient A, and unequal last blocks. Scalar bounds need not be sharp
or monotonic in m. Rejected-input checks cover shape/nonfinite/η/W errors.

## Admission and stopping

Allowed writes for the implementation are Unit6 lane-A code, tests, raw
results and factual documentation. Existing Unit5 and actual remote runner
remain read-only. No physical H actions, NCP execution, downloads, new
allocation or actual checkpoint compatibility claim. Maximum local fixture
N=512,m=32; one thread; each command less than 30 seconds. Stop at the
bounded suite and one independent scientific review; at most one explicitly
authorized targeted repair. PASS means a locally validated alternative
postprocessor. Production timing and actual checkpoint execution remain
NOT_MEASURED/NOT_RUN. A failed tolerance returns to scientific authority;
the coder must not relax tolerance or alter the physical conventions.
