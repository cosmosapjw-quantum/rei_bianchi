# M2: curvature storage order and the projected momentum constraint

## Disposition

`PASS_REI_M2_EXACT_SIGN_DIAGNOSTIC` at implementation commit
`fee018efd2f1d91e2ef859c0ee91874c0437bb62`, tree
`c53b53e21f779fb7d6d0b054097063ff3a7277b1`.

This is an independent, geodesic-normal/Fermi-triad homogeneous formula oracle.
It is not a background solver, a native xTensor replay, or provider admission.
Common-geometry ownership remains with BASS. Its integration state is
`SIGN_RECONCILIATION_REQUIRED`.

The geometric sign of the momentum expression in REI PR #62 comment
[5545445810](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/62#issuecomment-5545445810)
is rejected under the conventions explicitly stated in that comment. The spatial
STF-divergence formula in the same comment survives unchanged. Preserve that
comment as historical evidence; do not silently rewrite it.

## Exact assumptions, order and units

The metric has signature `(-,+,+,+)`; the spatial orientation is epsilon_123=+1.
The normal is n=e_0, with n.n=-1; the normal is geodesic and the spatial triad
is Fermi propagated. Homogeneity refers to tetrad components, not vanishing
covariant spatial derivatives. Set s=c*t, not c=1.

The positive expansion tensor and the matter momentum convention are

\[
K_{ab}=h_a{}^c h_b{}^d\nabla_c n_d
      =H_{\rm geom}h_{ab}+\sigma_{ab},\qquad
q_a=-h_a{}^cT_{cd}n^d,\qquad \kappa_G=8\pi G/c^4.
\]

Here `[Hgeom]=[sigma]=[a]=[nB]=L^-1`, `[n(K)]=L^-2`, and rho and q have
energy-density units. The physical energy flux is c*q. Every constraint term
has units L^-2. Bianchi a is not the normal four-acceleration; nB is not n.

Define two distinct all-lower curvature storage orders:

\[
\mathscr D_{abcd}=g(e_d,R(e_a,e_b)e_c),\qquad
\mathscr O_{abcd}=g(e_a,R(e_c,e_d)e_b)=\mathscr D_{cdba},
\]

where `R(X,Y)Z=nabla_X nabla_Y Z-nabla_Y nabla_X Z-nabla_[X,Y]Z`.
Their Ricci contractions must be changed together with their storage order:

\[
R_{cb}=g^{ad}\mathscr D_{abcd},\qquad
R_{bd}=g^{ac}\mathscr O_{abcd}.
\]

BASS W3 at commit `80d271cc528e1a0ffa813ecd3e3fb7610f3fa755` explicitly
uses derivative-first storage. The W2 displayed Gauss/Codazzi forms can be
reconciled with output-first storage. This is an explicit adapter interpretation,
not a claim that the BASS owner has already approved or implemented that adapter.

## Direct connection derivation

Let `nabla_ea eb=Gamma^d_ba e_d`. The spatial connection is the unchanged M1
Koszul connection. Its 4D extension is

\[
\Gamma^0{}_{ji}=K_{ij},\qquad
\Gamma^j{}_{0i}=K^j{}_i,\qquad
\Gamma^a{}_{b0}=0,\qquad [e_0,e_i]=-K^j{}_i e_j.
\]

The time variation of the commutator variables is

\[
n(a)=-Ka,\qquad n(n_B)=Kn_B+n_BK-(\operatorname{tr}K)n_B.
\]

Consequently `n(nB*a)=(K-tr(K)I)*(nB*a)`, so the Jacobi constraint is preserved.
The curvature is computed from derivatives and products of these connection
coefficients, including the non-coordinate commutator term. Gauss and Codazzi
are comparison targets, never substitutes for that computation.

The derivative-first results are

\[
\mathscr D_{ijkl}={}^{(3)}\mathscr D_{ijkl}
   +K_{il}K_{jk}-K_{ik}K_{jl},\qquad
\mathscr D_{ijk0}=-(D_iK_{jk}-D_jK_{ik}).
\]

The output-first permutation gives the displayed W2 forms with the opposite
placement/sign of the corresponding K terms. Both contractions give

\[
R_{0a}=D^bK_{ab}-D_aK\equiv C_a.
\]

With `E_ab=R_ab-R*g_ab/2+Lambda*g_ab-kappa_G*T_ab`, the constraints are

\[
E_{nn}=\tfrac12{}^{(3)}R+3H_{\rm geom}^2
       -\tfrac12\sigma_{ab}\sigma^{ab}-\Lambda-\kappa_G\rho,
\]

\[
\boxed{M_a:=-h_a{}^c n^dE_{cd}=-C_a-\kappa_Gq_a.}
\]

For homogeneous data, `D_a K=0`, and the unchanged M1 result gives

\[
M_a=3a^b\sigma_{ab}+\epsilon_{abc}n_B{}^b{}_d\sigma^{cd}
    -\kappa_Gq_a.
\]

The Hamiltonian identity is even under K -> -K, while the geometric mixed
projection is odd. A correct Hamiltonian test cannot by itself certify the
momentum sign. Setting a=nB=sigma=0 recovers
`3*Hgeom^2-Lambda-kappa_G*rho`; since Htime=c*Hgeom this preserves explicit c.

## Class-B formula and independent coordinate witness

In the full-transverse chart `a=(A,0,0)` and `nB[1,*]=0`,

\[
C_3=N_{22}\Sigma_{12}+(N_{23}-3A)\Sigma_{13},
\]

\[
\boxed{M_3=-N_{22}\Sigma_{12}+(3A-N_{23})\Sigma_{13}-\kappa_Gq_3.}
\]

The previous claim was `C_3-kappa_G*q_3`; its residual against the direct
projection is `2*C_3`. This is not a harmless reversal of the entire constraint:
the matter term was not reversed with the geometric term.

The independent coordinate route differentiates the smooth local metric

\[
g=-ds^2+\omega^T(I+2sK)\omega,\qquad
\omega=(dx,e^{-Ax}dy,e^{-Ax}dz),
\]

at s=x=0, constructing metric derivatives, inverse-metric derivatives,
Christoffel symbols, Ricci and Einstein tensors without ONF connection rules.
It obtains `R_03=-3*A*k13` and exactly matches all three mixed projections and
the Hamiltonian. For A=k13=1/L0, q3=0 and other K entries zero, the derived
M3 is `+3/L0^2`; the previous formula gives `-3/L0^2`.
The spatial metric is positive definite in a sufficiently small neighbourhood
of s=0. This is an off-shell geometric counterexample, not a claimed
Einstein-matter solution or a reionization prediction.

## Evidence and boundaries

The frozen ten-test suite passed without errors or skips. The generated report
contains exact zeros for 81 Gauss, 27 Codazzi, 16 Ricci-adapter, 81 output-Gauss,
27 output-Codazzi, 64 torsion, 64 metric-compatibility, 3 Jacobi-rate,
1 Hamiltonian, 3 momentum and 4 independent-coordinate residuals.
Polynomial reduction is modulo the spatial Jacobi ideal; no floating tolerance
is used for these identities.

Eight exact fixtures produce all-zero locked residuals. Six hostile changes
probe the 3A channel, epsilon channel, Sigma13 omission, N22 omission, prior
geometric sign, and matter sign. They are inconsistent-channel mutations, not
legitimate complete frame/convention transformations. The old geometric sign
is detected in 7/8 fixtures; the remaining fixture is an intentional
cancellation locus, not evidence for universal correctness.

PNG/SVG/CSV/JSON and the source archive were generated and SHA-256-checked by
the runner. The current session could not open the downloaded artifact because
the file-execution backend failed before starting. Therefore direct visual
inspection and print-legibility review remain NOT_RUN. The numerical/semantic
mutation audit is complete; the full plot-driven visual closeout is not.

Method references (not coefficient authority): Gourgoulhon, arXiv:gr-qc/0703035,
and van Elst & Uggla, arXiv:gr-qc/9603026, retrieved through web/SciSpace.
Wolfram context and evaluator both returned upstream HTTP 502 before a result;
no fresh Wolfram or xAct PASS is claimed.

The next bounded research task is owner-bound storage-order/sign reconciliation
with the BASS native Einstein projection bridge, followed by constraint
propagation only after that bridge has actually passed. H1B1 signed-Snapshot
host census remains the separate runtime frontier. No first interval, provider,
normal/electron-tilt collision, or coupled-background admission follows here.
