# R2A constrained macro-distribution operator

## Locked quantities and units

At each validated B2C2B0C reduced-DAE substep, the stage holds fixed
\(N_{\rm H,sink}\,[{\rm H\,cMpc^{-3}}]\), \(x_{\rm HII,sink}\),
\(T_{\rm sink}\,[{\rm K}]\), \(\kappa_g\,[{\rm cMpc^{-1}}]\),
\(J_g\,[{\rm s^{-1}\,cMpc^{-3}}]\), and the diffuse/sink H-transfer rate.
The current-Gamma flux is \(\Phi_g=J_g/\kappa_g\) and
\(J_{mg}=\Phi_g\kappa_{mg}\).

## Prior and information projection

For active groups \(g\in\{G1,G2a\}\), B2C2B0A HI macro allocation gives
strictly positive \(p_{mg}\), normalized over the 18 macros. Set

\[
q_g=J_g/\sum_hJ_h,\qquad p^M_m=\sum_gq_gp_{mg}.
\]

For \(m_m=M_m/N_{\rm H,sink}\) and
\(k_{mg}=\kappa_{mg}/\kappa_g\), minimize

\[
\mathcal I=\frac12D(m\Vert p^M)
+\frac12\sum_gq_gD(k_g\Vert p_g),\quad
D(x\Vert p)=\sum_m[x_m\ln(x_m/p_m)-x_m+p_m].
\]

The constraints are the mass and opacity moment sums, non-negativity,
\(M_m\le N_H^cf_m^{\rm macro}\), macro volume filling at most one, and

\[
\sum_gJ_{mg}\le M_m\left[\frac{1-x_{\rm HII,sink}}{\Delta t}
+\frac{R_{\rm rec,sink}}{N_{\rm H,sink}}\right].
\]

The bracket has dimension s^-1, so the right-hand side has the same
s^-1 cMpc^-3 dimension as the assigned absorption.

## Exact identity projection for the locked data

Because \(m=p^M\), \(k_g=p_g\), and
\(p^M_m=\sum_gq_gp_{mg}\), the macro capacity slack is

\[
C_m-J_m=J_{\rm sink}(\rho-1)p^M_m,
\quad \rho=C_{\rm global}/J_{\rm sink}>1.
\]

All mass/volume caps also have strict positive slack. Generalized KL is
non-negative and vanishes only at the prior; therefore the prior is the unique
constrained optimum. Equality and inequality dual multipliers can all be zero,
which closes stationarity, dual feasibility, and complementarity analytically.

## Geometry and forbidden closure

The inherited single-size Jeans/self-shielding density and radius are used only
to audit cloud count and volume filling after mass allocation. Neither opacity
nor cloud abundance is inverted to redefine macro mass. G2b/G3 effective-HI
sink opacity and primary HeII/G3 absorption are exact zeros. No node chemistry,
unresolved subtraction, front/Q_M, source/fesc, primordial recombination, or
Bianchi feedback is introduced in R2A.
