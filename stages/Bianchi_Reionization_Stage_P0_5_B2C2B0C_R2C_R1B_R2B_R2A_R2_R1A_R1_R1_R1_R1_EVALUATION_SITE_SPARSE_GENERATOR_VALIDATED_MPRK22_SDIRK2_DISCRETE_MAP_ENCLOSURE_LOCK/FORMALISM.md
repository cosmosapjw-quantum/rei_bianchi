# Evaluation-site sparse-generator validated MPRK22–SDIRK2 discrete-map enclosure

## Status and scope

This specification begins from durable commit
`ae9ae16b63036aa2e425ac82c183ec66062134a5`.  It does not inherit any
post-lock plot or transcript-only numerical conclusion.  The target is the
single canonical microstep map with four independent source-evaluation sites:

1. `population_t0`;
2. `population_t1_predictor`;
3. `thermal_tgamma`;
4. `thermal_t1_final`.

No temporal coherence among their branch variables is assumed.

## State and parameter representation

Use invariant-reduced node state

\[
Y_i=(x_{{\rm HI},i},x_{{\rm HeI},i},r_{{\rm HeIII},i},\log T_i)
\]

with dependent ion fractions reconstructed analytically.  At each site `s`,
retain independent local normalized parameters

\[
\theta^{(s)}_{v,i},\theta^{(s)}_{f,i}\in[-1,1]
\]

and the local mixed monomial
\(\theta^{(s)}_{v,i}\theta^{(s)}_{f,i}\).  A validated state is represented as

\[
Y=c+\sum_{s,i}\left(A^{(s)}_i\theta^{(s)}_{v,i}
+B^{(s)}_i\theta^{(s)}_{f,i}
+C^{(s)}_i\theta^{(s)}_{v,i}\theta^{(s)}_{f,i}\right)
+L\eta+\mathcal E,
\]

where `L eta` contains named global owner-normalization/forcing modes and
`E` is an outward interval or ellipsoidal remainder.

## MPRK22(1) implicit tangent contract

Write each Patankar stage as a positive linear solve

\[
A_k(Y,\theta)\,Z_k=b_k(Y,\theta).
\]

The tangent in any generator direction is not approximated by finite
difference.  It is obtained from

\[
A_k\,\delta Z_k=\delta b_k-(\delta A_k)Z_k.
\]

The validated solve uses a midpoint inverse `C_k` and a Krawczyk enclosure

\[
K_k(X)=z_0-C_kF_k(z_0)+(I-C_kJ_k(X))(X-z_0).
\]

Each local 2x2 H block and 3x3 He block must satisfy

\[
K_k(X)\subset\operatorname{int}X
\]

with an outward-rounded row-sum certificate.  The Patankar denominators must
remain strictly positive over the complete enclosure.  H and He invariant
rows are removed analytically rather than bounded numerically.

## Alexander SDIRK2 thermal tangent contract

Let

\[
\gamma=1-\frac1{\sqrt2}.
\]

Each thermal stage is the scalar implicit equation

\[
r_j(\log T_j;Y_{\rm in},\theta^{(s)})=0.
\]

For every generator,

\[
\delta\log T_j=-\frac{\partial r_j/\partial q}{
                              \partial r_j/\partial\log T_j}.
\]

The denominator is interval-evaluated and must exclude zero.  A scalar
Krawczyk operator validates the root.  Safeguard branch changes and bracket
fallbacks are discrete events; differentiation through a changed branch is
forbidden.  The interval is bisected and the map restarted instead.

## Owner-normalization derivative

For

\[
q_i=h_i/H,\qquad H=\sum_jh_j,
\]

use the exact decomposition

\[
\delta q_i=\frac{\delta h_i}{H}
-q_i\frac{\sum_j\delta h_j}{H}.
\]

The first term stays node-local diagonal.  The second is a named rank-one
reduction per owner/group/site.  Dense interval Jacobians are forbidden.
Woodbury/Sherman–Morrison correction is allowed only with a validated
nonzero denominator and an outward residual receipt.

## Higher-order remainder

The branch source is locally bilinear, but the complete discrete map is not.
Retain all local `vf` monomials exactly.  Bound omitted terms by interval
Hessian-vector contractions over the validated stage boxes.  The remainder
must include:

- state dependence of atomic rates and cooling;
- owner-normalization state feedback;
- cross-site composition terms;
- thermal-root curvature;
- floating-point outward-rounding error.

A posteriori sampling can falsify the enclosure but cannot certify it.

## Hummer–Seaton topology events

The surfaces

\[
T=10^{4+0.25k}\,\mathrm K,\qquad k=0,\ldots,4
\]

are discrete compiler events.  If a validated temperature tube intersects a
surface, reject the current attempt, localize the earliest crossing by time
bisection, commit no state, rebuild the fixed-topology branch cell and restart.
Silent extrapolation and numerical floors are forbidden.

## Required inclusion tests

The final set must contain, componentwise and in all named ledgers:

- all 24 inherited static corner/adapter trajectories;
- the upper-then-lower stagewise-switch witness that escaped the static hull;
- at least the locked interior falsification sample set;
- all three shape lanes.

Point-degenerate parameters must reproduce the existing physical trial within
its locked tolerance.  Rejected attempts and rollback must leave parent state,
accepted history and all ledgers byte-identical.

## Set-valued conservation gates

For every generator and remainder interval, verify:

\[
\delta(N_{\rm HI}+N_{\rm HII})=0,
\]

\[
\delta(N_{\rm HeI}+N_{\rm HeII}+N_{\rm HeIII})=0.
\]

The interval ledgers for group photons, resolved heat, unresolved OTS energy,
escaped radiation and total energy must contain exact zero residual.  The
`EFFECTIVE_HI_SUBGRID` resolved H/He/thermal source stays structural zero.

## Public-width approval gate

Only certify the next stage if all three shape lanes satisfy

\[
\Delta x_{\rm HII},\Delta x_{\rm HeII},
\Delta x_{\rm HeIII},\Delta\log T<2\times10^{-3}
\]

and every Krawczyk, event, containment, transaction and ledger gate passes.
Otherwise preserve the earliest failure as a fail-closed certificate; do not
clip, correlate parameters post hoc or choose a favorable lane.

## Rust/BASS boundary

Python outward-validated arithmetic remains the scientific authority.  Rust
1.94.1 may accelerate only pure sparse contractions whose Python oracle,
containment direction and ULP receipt are all locked.  The Rust path must not
own event localization, topology decisions or acceptance policy in this stage.
