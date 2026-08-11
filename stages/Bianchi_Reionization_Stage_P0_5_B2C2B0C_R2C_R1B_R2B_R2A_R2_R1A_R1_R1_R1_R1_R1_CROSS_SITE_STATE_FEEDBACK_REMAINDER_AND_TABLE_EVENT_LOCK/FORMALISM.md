# Four-site cross-site remainder and table-event formalism

## Scope

This stage certifies a single accepted FLRW reionization thermochemistry
microstep. Metric signature is `(-,+,+,+)`, `epsilon_123=+1`, and `c`, `hbar`
and `k_B` remain explicit in inherited physics modules.

The material state is invariant-reduced to

\[
Y_i=(x_{{\rm HI},i},x_{{\rm HeI},i},r_{{\rm HeIII},i},\ln T_i),
\]

with H and He dependent fractions reconstructed analytically. Four independent
source-evaluation sites are retained:

\[
s\in\{{\mathrm{pop0},\mathrm{pop1},\mathrm{th\gamma},\mathrm{th1}}\}.
\]

No temporal coherence among their local `(v,f)` variables is assumed.

## Source-safe interval event graph

At each node and site the full-OTS source is evaluated over the locked
Hummer-Seaton `v` interval and

\[
f\in[0.1,1].
\]

The local `vf` mixed term is evaluated directly rather than decorrelated from
its factors. Exact-zero species/group support is structural. The resulting
production-destruction flux intervals are nonnegative.

## MPRK22 interval map

Each H or He Patankar stage is

\[
A_k(X,\Theta)Z_k=b_k(X,\Theta).
\]

For a midpoint inverse `C_k`, the outward Krawczyk image is

\[
K_k(X)=z_0-C_kF_k(z_0)+\bigl(I-C_kJ_k(X)\bigr)(X-z_0).
\]

Only the certified image is propagated; the wider construction tube is kept as
diagnostic metadata. H and He invariant directions are eliminated exactly.
The largest observed row-sum bound at partition `2048` is

\[
0.015847428383092121<1.
\]

## Coupled thermal roots

Alexander SDIRK2 uses

\[
\gamma=1-\frac1{\sqrt2}.
\]

For each scalar stage root

\[
r_j(\ln T_j;Y,\Theta)=0,
\]

the analytic outward interval for `partial r_j / partial lnT_j` is used. A
secant across different branch parameter boxes is forbidden. Interval
Newton/Krawczyk intersection gives the root image; an interval containing zero
in the derivative is an immediate rejection.

## Owner feedback

For owner measure

\[
q_i=\frac{h_i}{H},\qquad H=\sum_jh_j,
\]

the exact first variation is

\[
\delta q_i=\frac{\delta h_i}{H}-q_i\frac{\sum_j\delta h_j}{H}.
\]

The first term is node-local diagonal and the second is a named rank-one
reduction. The implemented interval map evaluates the normalized measure over
the complete state image; it does not form a dense 368012-column Jacobian.

## Full-step versus two-half-step gate

Let `Phi_h` denote the outward map for one step and `Phi_{h/2}^2` the composed
two-half-step map. For each public block, the validated local error is the
maximum distance between the two images. Acceptance requires

\[
\max_B\epsilon_B<2\times10^{-4}.
\]

The final state image is the two-half-step image, consistent with the inherited
adaptive controller.

## Table topology events

Hummer-Seaton knots are

\[
T_k=10^{4+0.25k}\,\mathrm K,\qquad k=0,\ldots,4.
\]

Event detection uses the hull of every validated temperature image along the
source evaluation path, not endpoint boxes alone. If a knot is touched:

1. reject the attempt;
2. preserve parent state and all ledgers byte-for-byte;
3. localize the earliest crossing by bisection;
4. rebuild the fixed-topology source cell;
5. restart the validated map.

## Structural ledgers

Let `s_e` be each typed event stoichiometric vector. Exact identities are

\[
c_H\cdot s_e=0,\qquad c_{\rm He}\cdot s_e=0,
\]

\[
\sum_o q_{go}=1,\qquad N_{\gamma,g}^{\rm destroyed}=\sum_oN_{\gamma,g,o},
\]

and, event by event,

\[
\Delta E_\gamma+\Delta E_{\rm chem}+\Delta U_{\rm resolved}
+\Delta E_{\rm OTS}+\Delta E_{\rm escaped}=0.
\]

These exact identities are the conservation authority. Componentwise interval
subtractions can be wide because repeated variables are decorrelated; they are
kept only as a zero-inclusion diagnostic.

## Units and limits

- ion fractions and `ln T` are dimensionless;
- temperature is in kelvin;
- reaction rates are inherited in `s^-1`;
- time conversion remains the inherited FLRW physical-time path;
- no Bianchi background driver is coupled in this stage.

Point-degenerate branch intervals recover the inherited primal map. The
refinement sequence `1024,2048,4096` shows decreasing widths and local error.
