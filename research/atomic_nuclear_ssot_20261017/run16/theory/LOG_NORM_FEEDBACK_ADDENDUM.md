# RUN16: residual sign and a constructive feedback comparison

Status: **DERIVED**, conditional on the explicitly stated tube and defect
bounds. The recorded point values below are **NUMERICALLY_CHECKED** by the
feedback producer, not a verified trajectory enclosure.

## 1. Signed residual and terminal adjoint identity

Use one sign convention throughout. For the actual ODE
`g'=F(z,g)`, an absolutely continuous reconstruction `hat_g`, and
`e=g-hat_g`, define

\[
r(z)=\hat g'(z)-F(z,\hat g(z)).
\]

Then

\[
e'=F(z,g)-F(z,\hat g)-r
   =J(z)e-r+N(z,e),\qquad
J(z)=D_gF(z,\hat g(z)),
\tag{A1}
\]

where `N=F(z,hat_g+e)-F(z,hat_g)-J*e`. For a terminal linear
observable `ell^T g(T)`, let
`-lambda'=J^T lambda`, `lambda(T)=ell`. Direct differentiation gives

\[
\ell^T e(T)=\lambda(0)^T e(0)
-\int_0^T\lambda(z)^T r(z)\,dz
+\int_0^T\lambda(z)^T N(z,e(z))\,dz.
\tag{A2}
\]

Thus the residual contribution has a **minus** sign for these definitions.
A nonlinear terminal functional adds its own terminal Taylor remainder.
If the system is piecewise smooth with continuous state and fixed event
times, apply the identity on each interval and telescope the continuous
boundary terms. Nontrivial reset maps or reconstruction jumps require their
explicit jump terms. These equations are independently derived here; a
literature extraction's inconsistent error/residual definitions cannot
override them.

The earlier main note's integral defect is
`r_I=hat_g-T[hat_g]`. With the same initial value,
`r_I(z)=integral_0^z r(s) ds`; an initial mismatch adds the corresponding
constant. The sign disappears after taking a norm but is essential for a
goal-weighted signed estimate.

## 2. Five gas coordinates and optical-depth memory

On the native H/D/He and thermal invariant manifold, use

\[
q=(x_{\rm HII},x_{\rm DII},x_{\rm HeII},x_{\rm HeIII},U/U_0).
\]

For a fixed finite birth/angular/spectral measure and prescribed geometry,
keep all cohort slots, setting the inactive optical-depth derivative to zero.
At active times, write

\[
q'=G(z,q)+\sum_{i,a}v_{ia}(z)K_{ia}(z)
                 g_{\mathrm{lower},a}(q)B_i e^{-\tau_i},
\qquad
\tau'_i=\sum_aK_{ia}(z)g_{\mathrm{lower},a}(q).
\tag{A3}
\]

Here `v` includes the same species-fraction and initial-thermal
normalizations used by the original native equations. The neutral-lower
population is affine in these five coordinates. Therefore the Jacobian
block structure is

\[
\begin{pmatrix}\delta q'\\\delta\tau'\end{pmatrix}
=
\begin{pmatrix}A&B\\C&0\end{pmatrix}
\begin{pmatrix}\delta q\\\delta\tau\end{pmatrix},
\qquad
A=G_q+F_{\rm photo,q}|_\tau,quad
B=F_{\rm photo,\tau},quad C=K g_{\rm lower,q}.
\tag{A4}
\]

The zero depth-depth block is exact for this optical-depth representation
on a fixed support. It does not remove feedback: changing gas changes
depth, which changes later photo-forcing.

## 3. A comparison that preserves direct gas damping

Let `u=||e_q||_infinity`, `v=||e_tau||_infinity`. Suppose a verified
admissible tube, with positive temperature and valid species fractions,
contains the actual solution and reconstruction and the line segments used
to compare them. On every relevant event interval suppose integrable
functions satisfy

\[
a(z)\ge\sup_{\rm tube}\mu_\infty(A),\qquad
b(z)\ge\sup_{\rm tube}\|B\|_\infty,\qquad
c(z)\ge\sup_{\rm tube}\|C\|_\infty,
\tag{A5}
\]

and `rho_q,rho_tau` enclose the reconstruction residuals, with initial
and event/source defects explicitly included. Here

\[
\mu_\infty(A)=\max_i\left(A_{ii}+\sum_{j\ne i}|A_{ij}|\right).
\]

Convexity of the matrix measure permits the same bound for the averaged
Jacobian along a segment in the tube. The upper Dini derivatives obey

\[
D^+\begin{pmatrix}u\\v\end{pmatrix}
\le
\begin{pmatrix}a&b\\c&0\end{pmatrix}
\begin{pmatrix}u\\v\end{pmatrix}
+\begin{pmatrix}\rho_q\\\rho_\tau\end{pmatrix}.
\tag{A6}
\]

The off-diagonal entries are nonnegative, so this is a cooperative linear
comparison. Its nonnegative fundamental matrix `Psi` gives

\[
\begin{pmatrix}u(z)\\v(z)\end{pmatrix}
\le\Psi(z,0)\begin{pmatrix}u(0)\\v(0)\end{pmatrix}
+\int_0^z\Psi(z,s)
\begin{pmatrix}\rho_q(s)\\\rho_\tau(s)\end{pmatrix}ds.
\tag{A7}
\]

A negative direct-gas logarithmic norm is retained in `a`; replacing it
by the full ordinary matrix norm can discard useful damping. Eliminating
`v` yields a finite-time Volterra comparison. Integrable/bounded
coefficients have a finite-time propagator/resolvent; **no global
contraction constant below one is required**.

The inequality remains conditional until a self-consistent tube and
between-knot residual bounds are supplied. Three point Jacobians, small
endpoint differences, and local solver tolerances are not those bounds.
If quadrature or cohort support changes, its forcing discrepancy belongs
in a separately bounded source defect; matrices for different finite
cohort lists cannot simply be subtracted as if they had identical slots.
The full source and all four channels enter (A3), although RUN16's
goal-specific fixed-core response is H-only with D inactive.

## 4. What the actual recorded diagnostic shows

Producer:
`../feedback/recorded_state_feedback.py`, SHA-256
`d843facd5d50b7d4aec6f80b2518589a5d3570c207d0c2b9e70fad11b84e2ac4`.

Recorded result:
`../feedback/execution01/RECORDED_STATE_FEEDBACK.json`, SHA-256
`385f61f57b5d314dbf69d2111f5576bf4be09fc0d94f67682eeb7a95daf25515`.

The producer evaluated 85 original native RHS calls at three archived
states and performed zero IVP solves. In the stated five coordinates:

| Normalized z | Gas ordinary infinity norm | Gas logarithmic infinity norm | Full fixed-depth logarithmic norm | Direct photo infinity norm |
|---:|---:|---:|---:|---:|
| 0 | 33.6199396799874 | 0.1408114398541187 | 0.1408114398541187 | 0 |
| 0.7609039888237062 | 33.59651303280653 | 0.13830094487512667 | 0.13819500415022645 | 0.0007862848018456046 |
| 1 | 33.58995725427915 | 0.1382377295074022 | 0.1379124372124565 | 0.0014544156367428352 |

At the two noninitial points the respective `||B||_infinity` values
are `0.0006244196051542758` and `0.0011989314366697198`;
the `||C||_infinity` values are `398.8354347572113` and
`398.77796414274724`. These numbers motivate investigating (A5);
they are **pointwise numerical scales**, not coefficients already
certified for (A7).

The componentwise PCHIP reconstruction reports its nuclear-total
derivative drift explicitly. It must not silently be treated as a
conservation-exact gas reconstruction. A future manifold reconstruction
or inclusion of the omitted constraint residuals is needed before using
the five-coordinate comparison as a full-path certificate.

## 5. Transfer back to the selected survivor observable

Once an actual bound on `|e_q,HII(z)|` is available, conservation on
the same native H manifold gives the corresponding neutral-H density
bound. In original scaled gas units,
`|delta Y_HI| <= H_total * u(z)`; the common positive proper-density
conversion supplies `|delta n_HI|`. Divide by a verified positive
baseline HI density only when a relative envelope is desired.

The positive response kernel and conditional bounds in the main note
then propagate this HI envelope to the fixed-core sub-H-fit survivor.
Core energy/time quadrature error, the inherited H-only tail estimate,
and the full-source defect entering the feedback reconstruction remain
separate obligations. This advances the existing
`P4-S4C-SPECTRAL-EDGE-SUPPORT` node without deleting or redefining any
45-node/26-node DAG obligations.

## References and scope

Cao and Petzold, SIAM Journal on Scientific Computing 26(2), 359--374
(2004), DOI 10.1137/S1064827503420969, supports goal-weighted residual
analysis with a nonlinear remainder. Primary author PDF:
https://people.cs.vt.edu/~ycao/publication/siam_42096.pdf .

Ranocha and Giesselmann, arXiv:2307.12677, section 2.1 and Lemma 2.1,
supports residual-based stability using a one-sided Lipschitz bound and
a sufficiently regular reconstruction:
https://arxiv.org/pdf/2307.12677 .

Equations (A1)--(A7) are the present conditional derivation. Neither
reference supplies this project's missing numerical tube constants.

