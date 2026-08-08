# Formalism — validated continuous branch enclosure audit

## Scope and conventions

The metric signature is `(-,+,+,+)`, `epsilon_123=+1`, and `c`, `hbar`, and `k_B` remain explicit.  This stage concerns the first locked reionization thermochemistry microstep on the homogeneous background.  It does not implement CAMB transfer, a recombination splice, or Bianchi feedback.

The material state is represented in invariant coordinates

\[
X=(x_{\rm HI},x_{\rm HeI},r_{\rm HeIII},\ln T),
\qquad
r_{\rm HeIII}=\frac{x_{\rm HeIII}}{x_{\rm HeII}+x_{\rm HeIII}}.
\]

Then

\[
x_{\rm HII}=1-x_{\rm HI},
\]

\[
x_{\rm HeII}=(1-x_{\rm HeI})(1-r_{\rm HeIII}),
\qquad
x_{\rm HeIII}=(1-x_{\rm HeI})r_{\rm HeIII}.
\]

This coordinate map preserves the hydrogen identity and helium simplex structurally.  No projection or clipping is used.

## Source uncertainty

For `T<10^4 K`, the source-safe branch probability remains

\[
v\in[0,1].
\]

Inside the Hummer--Seaton table, `v` is bounded by the two source nodes bracketing the current temperature.  A continuous interpolant is not assumed.  The He II Ly-alpha absorbed fraction remains

\[
f\in[0.1,1].
\]

The event coefficients are multi-affine in `(v,f)` at fixed material state, but the integrated state is nonlinear because temperature, owner fractions, reaction rates, and table-cell membership all depend on the evolving state.

## Constant orthant comparison audit

Let `F(X)` denote the reduced RHS.  A constant diagonal sign transformation `S=diag(s_i)`, `s_i in {+1,-1}`, changes one off-diagonal Jacobian entry by the fixed factor `s_i s_j`.  Therefore, if the same entry has opposite robust signs at two admissible states, no constant diagonal orthant can make that entry nonnegative everywhere.

The audited entry was

\[
\frac{\partial \dot{\ln T}}{\partial x_{\rm HII}}.
\]

At node 12800 (`T=2096.738912832555 K`) it is

\[
-9.155751112855815\times10^{-14},
\]

whereas at node 43452 (`T=59320.63596390174 K`) it is

\[
+5.922708052362587\times10^{-11}.
\]

The sign is stable under central-difference steps `1e-6` and `2e-7`.  This excludes constant diagonal orthant comparison only; nonlinear or state-dependent cones remain open.

## Directed-rounding interval extension

Every primitive binary64 operation is stepped outward with `nextafter`.  PCHIP forcing is enclosed piecewise through a cubic Bernstein hull.  Global owner normalization is evaluated as an interval low-rank coupling, and the H/He identities remain structural in the reduced coordinates.

For one time slab `[t_0,t_1]`, an a-priori tube `B` must satisfy

\[
X_0+[0,h]F([t_0,t_1],B)\subseteq B,
\qquad h=t_1-t_0.
\]

Only then is

\[
X(t_1)\in X_0+hF([t_0,t_1],B)
\]

a validated endpoint enclosure.

The same implementation certifies the analytic control problem `y'=-0.5 y`, `y(0)=1`, over `h=0.2`, so the project failure is not a universally broken Picard implementation.

## Project result and wrapping interpretation

For locked partitions 16, 32, and 64, the first Picard expansion enlarges the componentwise tube until the temperature box crosses `10^5 K`.  Source policy forbids extrapolation beyond that knot, so each attempt terminates as `TABLE_TOPOLOGY_EVENT_UNLOCALIZED` before accepting a subsegment.

The maximum internal-coordinate widths were respectively

\[
1.1106807367,\quad 1.1104057298,\quad 1.1102682264.
\]

These widths are not physical trajectory widths.  They are dependency/wrapping overestimation.  The preceding 24 numerical realization endpoints remain narrow and satisfy all physical ledgers, but they are regression evidence rather than a continuous-family proof.

## Required next mathematical architecture

The next method must retain parameter dependence instead of repeatedly replacing it by an axis-aligned box.  The authorized route is an affine set-parameterized Taylor model:

\[
X(t,\theta)\subset P_k(t,\theta)+\mathcal R(t),
\]

where `theta` represents the admissible branch-function uncertainty and `R` is a validated affine/ellipsoidal or interval remainder.  Hummer--Seaton table crossings must be localized as discrete compiler events.  H/He invariant directions must be removed analytically, and low-rank owner-normalization dependence should be kept as explicit generators rather than intervalized independently at each algebraic use.
