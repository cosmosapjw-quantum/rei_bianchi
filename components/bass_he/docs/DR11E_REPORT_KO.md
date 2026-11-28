# DR11E: fixed-index Sturm real anchors

Parent scientific publication: PR9 `d763f2706769802e16d9227eeb0304c85701fcf2`.
This is an **opt-in research candidate**, not a default production replacement.

## Mathematical result

Let `r=R/a0`, `u=p^2`, `a=(Z1+Z2)r`, `b=(Z2-Z1)r`, and use the code convention `lambda -> l(l+1)`. The regular/decaying separated self-adjoint operators are

```
Hxi = -d_xi[(xi^2-1)d_xi] + m^2/(xi^2-1) + u(xi^2-1) - a xi
Heta = -d_eta[(1-eta^2)d_eta] + m^2/(1-eta^2) + u(1-eta^2) + b eta
```

Eta is oriented as `(r2-r1)/R`. The ordered eigenvalues obey
`mu_k(u)+lambda_q(u)=0`, with `k=N-l-1`, `q=l-m`.
For normalized simple bound eigenstates, differentiating the eigenproblem gives

```
d(mu_k+lambda_q)/du = <xi^2-1>_k + <1-eta^2>_q > 0.
```

Thus a fixed labelled pair has at most one positive root; an actual sign-changing bracket is required, not assumed. CF matching index is not a quantum-state label. For an invertible left/right partition, its meromorphic Schur chart obeys `F_j=det(T)/(det(T_left)det(T_right))`, so raw residuals can be severely amplified without large root error.

## Fixed-basis discretization

The radial scale `tau=a/(2*Nref)` is held fixed during each scalar solve; both states use the same pair scale. With `x=2tau(xi-1)`, `Q=x(x+4tau)`, and `F=Q^(m/2)exp(-x/2)v`, the transformed operator is

```
-Q v'' + [Q-(m+1)Q'] v'
+ [2tau(m+1)-m(m+1)-a+(m+1-a/(2tau))x
   +(u-tau^2)Q/(4tau^2)]v.
```

Laguerre polynomials give a symmetric generalized radial pencil. Whitening the positive Gram matrix and using `w=(p/tau)^2` gives `A+wB` with `B>0`. The Legendre angular pencil also has a positive slope. Its quadratic multiplication term is `P X^2 P`, **not** `(P X P)^2`; one extra mode is retained before squaring. Fixed-index finite eigenvalues therefore remain monotone. Nested bases give a variational direction in exact arithmetic, but the reported errors are numerical convergence estimates, not interval bounds.

## Evidence

- Exact radial-gauge, Schur and Legendre/hypergeometric identities: Wolfram and independent SymPy residuals zero.
- Requested Precise Special Functions oracle: `2F1(-9,16;4;3/8)=16193/33554432`.
- Old bad coordinate `(4,2,0), R=1.4822661233645524`: energy agrees with 75-digit depth160 CF within `7.40e-15 Eh`, despite old float64 raw CF residual `1.72e-6`.
- New tests: 21 PASS after recorded RED. Recovered affected baseline: 32 PASS. Total **53/53**, not the whole latest PR9 repository test suite.
- Fresh DR11D replay: Q12 control PASS, 7/7 EP160, 56/56 action cases across 7 branches, rho/ReRc={0,.25,.5,.75}, panels={32,64}.
- Worst panel relative change `1.4588e-5`; max complex residual `1.9998e-11`; minimum normalized sheet gap `0.01949897`.
- 56 real anchors x3 independent scale choices at basis72: max energy change `5.84e-13 Eh`.
- Same-runtime cold anchor speedups 7.97–32.45x; warm 10.49–49.53x. A complete Q3p/4d geometry case improves only **1.268x**; anchor speedup is not whole-solver speedup.

No original solver files are changed. `sturm_geometry` imports the existing complex pair tracker. The local execution environment was a recovered scoped source snapshot: 16 parent-identical core files plus the inherited geometry core, not a full PR9 checkout. Raw logs, full proofs, scripts, prior failed attempts, and precise provenance are in the separately backed-up DR11E archive.

A combined container call timed out after control/EP; those records were kept and only missing D0 was restarted. Subsequent geometry records are immutable per-case. This scheduling failure is not a physical counterexample.

## Claim ceiling

`DR11E/DR11D_NUMERICAL_REPLAY_PASS__PROMOTE_HOLD_INDEPENDENT_REVIEW_UNAVAILABLE`.
An author self-audit is recorded but is not independent review. Eq55, P_rot, Eq50, Eq54, full Nmax4 channel completion and continuum ionization remain NOT_RUN/NOT_ADMITTED. The inherited failed S3d-pi path remains a failed named-pair path after an exploratory anchor replacement, not proof of a virtual state's identity. Bounded failure to discover Q3s/4p is not a theorem of branch nonexistence.

Primary basis: Gusev–Solov'ev–Vinitsky, CPC286(2023)108662, DOI10.1016/j.cpc.2023.108662 (provided original pp.3–6); NIST DLMF1.13,1.18,14.10,18.3,18.9; Feynman, Phys.Rev.56(1939)340, DOI10.1103/PhysRev.56.340. The particular monotone matching and fixed-scale matrix derivations are supplied here, not attributed as verbatim algorithms from those sources.
