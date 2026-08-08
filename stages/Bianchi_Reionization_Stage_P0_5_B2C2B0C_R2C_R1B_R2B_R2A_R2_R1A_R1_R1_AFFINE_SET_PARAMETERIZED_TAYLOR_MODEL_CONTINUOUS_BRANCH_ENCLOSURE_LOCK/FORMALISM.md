# Formalism — source-safe branch rank and coherent quadratic auditor

## Conventions

Metric signature is `(-,+,+,+)`, `epsilon_123=+1`, and `c`, `hbar`, `k_B` remain explicit.  This stage changes no physical reaction, owner, thermal, or integration equation.

## Local branch derivatives

For one node, the He III cascade event has

\[
A_H=v w+(1-v)fz,
\qquad
A_{\rm HeI}=v m(1-y)+(1-v)f(1-z),
\]

where

\[
w=(\ell-m)+my,\qquad \ell=57/40,\qquad m=737/1000.
\]

If the cascade rate is `R`, the two population directions relevant for local branch rank have derivative matrix

\[
M_i=R_i
\begin{pmatrix}
 w_i-f_i z_i &(1-v_i)z_i\\
 m(1-y_i)-f_i(1-z_i)&(1-v_i)(1-z_i)
\end{pmatrix}.
\]

Its determinant simplifies exactly to

\[
\boxed{\det M_i=R_i^2(1-v_i)(w_i-\ell z_i).}
\]

The `f` terms cancel.  At any node with nonzero determinant, the local `v_i` and `f_i` sensitivity columns are linearly independent.  Different nodes have disjoint instantaneous output support, so local ranks add.

## Rank theorem for the source-safe family

The source-safe family contains independent parameters

\[
(v_1,f_1),\ldots,(v_N,f_N),\qquad N=46080.
\]

At the canonical initial state, 45,923 node blocks robustly have rank two at relative determinant threshold `1e-12`; the remaining 157 retain at least the positive `f_i` column.  Therefore

\[
\operatorname{rank} D_\theta F\ge 2(45923)+157=92003.
\]

A model using only two coherent global coordinates has first-order parameter rank at most two.  It cannot represent the source-safe tangent set without a nontrivial remainder spanning the missing local directions.

This is a representation no-go, not a physical-history no-go.

## Coherent quadratic auditor

The conditional auditor imposes

\[
v_i(\alpha)=v_{i,-}+\frac{1+\alpha}{2}(v_{i,+}-v_{i,-}),
\qquad
f_i(\beta)=0.55+0.45\beta,
\]

with the same `alpha,beta in [-1,1]` at every node.  Endpoint observables are fitted with

\[
P(\alpha,\beta)=c_0+c_1\alpha+c_2\beta+c_3\alpha^2+c_4\alpha\beta+c_5\beta^2.
\]

The exact range of this fitted quadratic on the square is obtained from corners, edge stationary points, and the interior stationary point.  Withheld trajectories measure empirical approximation error.  This is not a validated enclosure of the source-safe node-local family.

## Sparse next representation

A feasible source-safe representation is

\[
Y=c+\sum_i A_i\theta_{v,i}+\sum_i B_i\theta_{f,i}
  +\sum_i C_i\theta_{v,i}\theta_{f,i}+L\eta+\mathcal E.
\]

The local generators have block-diagonal support; `L eta` carries low-rank owner-normalization and forcing couplings.  For four reduced coordinates, two local linear generators and one local mixed generator require only

\[
12N\times 8\ {\rm bytes}=4.21875\ {\rm MiB},
\]

whereas a dense generator matrix would require about `0.124 TiB` before nonlinear remainders.
