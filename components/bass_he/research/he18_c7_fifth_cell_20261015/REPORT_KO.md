# HE18 C7 fifth warm P01 cell: local theory and coding results

2026-10-15 KST, actual fixed-slab local execution. Scientific status: **SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES**; no independent interval library verification, binary64/provider roundoff, physical model uncertainty, full 16-cell EoR or observer claim.

**Source identities:** BASS_HE PR60 head e08a3695db89a817675778dcff11b801f53e904d; rei_bianchi source commit a5c958c414dea41216b445c05f58df837f05cacb. C6 result and outgoing 2904-component SHA256 verified before use. Original HM12/FT03 warm source, not cold gas chemistry or HH Coulomb scattering.

## Actual physics and output

- Fifth proper-time slab `[2.5e10,3.125e10]` s; original reference epoch and global shear time kept.
- Two saved-source RHS endpoint calls to freeze Hermite, no new full source ODE.
- Two concurrent 2904-photon interval/Taylor evaluations, ~13.17s total.
- Fifth optical depth outward `[7.99990605978933518276,7.99990605978934068811]e-9`.
- Five-cell cumulative optical depth outward `[3.99995635208935971727,3.99995635208936124816]e-8`.
- Five-cell first collision probability outward `[3.99995627209110669080,3.99995627209110822169]e-8`.
- Fifth column error radius <41378.295 m^-2, positive 4-gas comparison gain <0.002305100, original gas box usage <0.194524.
- All 2904 photon incoming and outgoing errors retained, 784 true opacity-zero rays. Actual exact-rational validation: 11/11 groups pass.

## Mathematical optimization

For p(z)=c0+c1z+c2z² on [a,b], the three Bernstein controls are
B0=p(a), B1=c0+c1(a+b)/2+c2ab, B2=p(b).
Setting t=(z-a)/(b-a), we have the exact identity
p(z)=(1-t)² B0+2t(1-t)B1+t² B2.
The nonnegative weights sum to1, hence `sup |p(z)| <= max_j |Bj|`.
For coefficients in independently enclosed intervals, evaluate each Bj with exact rational endpoint signs. This incurs no additional floating outward-rounding uncertainty. The inherited cubic remainder c3 has whole-[-1/2,1/2] absolute bounds: sup |c3 z³|<=|c3|/8, integral <=|c3|/32, and positively weighted integral <=|c3|/64.

Changed only that residual upper-bound kernel, not source, photon evolution, rates, global shear, first-event law or scientific tolerance. **Baseline assembly 10.12s, exact Fraction Bernstein 8.01s**, measured speedup **1.2634x** on the same real fifth-cell jets. 8,712 scalar photon-bound comparisons (3 per node), 7,030 changed to no larger upper bounds, zero worsened. The optical-depth intervals overlap and comparison gain is unchanged. Exact state/source midpoint/whole array bytes are identical.

## Checks

- Public-only Python source/clock/negative-data/Bernstein regression: 6/6 passed.
- Local Wolfram15 xTensor1.3.0: 8 physical tensor groups, nine exact-zero residuals. Online Wolfram15.0.1: seven fifth original-time redshift and Hermite assertions True. Global signature (-,+,+,+), c,hbar,k_B retained.
- NumPy vectorized 2904 diagnostic cost ~0.089ms; exactly the same 784 transparent nodes; **not used for certification**.
- Native subagents NOT_RUN (no host dispatch surfaced); separate local Codex NOT_INVOKED.
- Initial source-stage code anchoring failures and two mistaken test-fixture keys were corrected and rerun without changing the physics. Full original logs and data remain private, not added to the public PR.

Cross-repo: newer bass_cr PR68 uses different low-energy cohort Verner curvature; WU088_HH PR75 is two-centre source cancellation, not an atomic input to HE; rei_bianchi PR117 pursues BBN-style ionization-history plots independently. Shared numerics (exact source identity, conservative safe fast paths) are reused, no cross-physics rates imported. Literature: Neher, Jackson & Nedialkov 2007 SIAM J Numer Anal DOI10.1137/050638448 on Taylor-model IVP enclosures, not a certification of the user mpmath implementation.

Next physical P01 interval `[3.125e10,3.750e10]` s with full 2904 incoming radii; preserve initial-epoch shear, positivity, threshold and source-knot guards, and compare assembly with the exact Fraction kernel. Native binary64 errors and formal interval backend audit remain separate.
