# Sparse local-generator and evaluation-site formalism

## Conventions and units

Metric signature is `(-,+,+,+)`, `epsilon_123=+1`, and `c`, `hbar`, `k_B`
remain explicit. The branch coordinates `theta_v`, `theta_f` are dimensionless.
The reduced source coordinates are

\[
Y=(x_{\rm HI},x_{\rm HeI},r_{\rm HeIII},\ln T),
\]

so every generator in the instantaneous RHS has units `s^-1`.

## Local bilinear source polynomial

At node `i`, write

\[
v_i=v_{c,i}+v_{h,i}\theta_{v,i},\qquad
f_i=0.55+0.45\theta_{f,i},\qquad
\theta_{v,i},\theta_{f,i}\in[-1,1].
\]

The locked He III cascade branches

\[
A_H=vw+(1-v)fz,
\qquad
A_{\rm HeI}=vm(1-y)+(1-v)f(1-z)
\]

are exactly bilinear in the two local parameters. Hence the instantaneous
reduced source is represented exactly as

\[
F_i=c_i+A_i\theta_{v,i}+B_i\theta_{f,i}
     +C_i\theta_{v,i}\theta_{f,i}.
\]

No cross-node local polynomial is materialized. H and He population generators
lie exactly in the nuclei-invariant tangent space.

## Low-rank global owner coupling

For one supported owner/group node measure,

\[
q_i=\frac{h_i}{H},\qquad H=\sum_jh_j.
\]

Its directional derivative is

\[
\delta q_i=\frac{\delta h_i}{H}
-q_i\frac{\sum_j\delta h_j}{H}.
\]

The first term is local diagonal action. The second is one fixed vector `q`
times one scalar reduction and is therefore rank one. There are eight supported
owner/group channels.

The global owner amplitudes depend on only

\[
\bar x_{\rm HII},\qquad
\bar x_{\rm HeI},\qquad
\bar x_{\rm HeII/H},
\]

so their state-dependent image has rank at most three. The conservative global
rank upper bound is `3+8=11`, while the local source rank lower bound is `92003`.
A dense node-by-node global Jacobian is neither necessary nor allowed.

## Outward bounds

The local polynomial range on the square is obtained exactly from the four
local corners. Named global generators contribute their absolute radius; the
explicit remainder interval is then added. Both Python and Rust move the final
lower and upper values one representable binary64 number outward.

## Evaluation-site theorem

The locked trial uses four source evaluations at distinct thermochemical
states. In the absence of a source-derived temporal/state regularity relation,
the source-safe interval selections at these sites cannot be collapsed to one
fixed local pair. The required sparse representation is

\[
Y=c+\sum_{s=1}^{4}\sum_i
\left(A_{s,i}\theta^s_{v,i}
+B_{s,i}\theta^s_{f,i}
+C_{s,i}\theta^s_{v,i}\theta^s_{f,i}\right)
+L\eta+\mathcal E.
\]

`L eta` contains named low-rank owner/normalization modes and `E` is a validated
remainder for state feedback and neglected cross-site terms. A static one-site
model is a conditional auditor only.

## Event surfaces

Every crossing of

\[
T=10^{4+0.25k}\ {\rm K},\qquad k=0,\ldots,4,
\]

is a topology event. The accepted step must stop, localize the event, rebuild
the source cell, and restart. The canonical initial minimum event distance is
only `3.08424459328549e-04` in `ln T`.
