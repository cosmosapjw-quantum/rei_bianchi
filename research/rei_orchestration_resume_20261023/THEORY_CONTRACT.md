# D10: generated matter stress on 35 saved histories

Authority: Astra theory contract, 2026-10-23 KST. This resumes the exact
`D10_ZERO_INITIAL_MATTER_STRESS_GENERATION` node of
`research/rei_unified_sigma_pi_20261021/UNIFIED_DAG.json` at
`cce008b3fc32c298185b30550b2cd909d74fcd87`. D9 source/results are
`407f2a30efcdd0c4c4afb180cbe7d31f90cc0401`; its final metadata is the former
pin. The distinct AGE DAG's empty ready list does not describe this lane.

Use built-in physmath 1.0.0, approval v0.2, R1–R10/C1–C10 selectively.
The handoff's tagged1.3.0 label is historical. Preserve AGENTS tiered execution:
Astra derivation/contract, lower-tier implementation, fresh Astra review.
The available local source recovery has no `.git`; no local HEAD is claimed.
No clone/worktree, historical IVP, ODE callback, NCP submission or momentum
quadrature is part of this unit. Publication belongs to root on additive PR222.

## Frozen physical model and source

Reuse the collisionless massive distribution, cosmology, initial calibration,
and trajectories of the owner B lane, with signature (-,+,+,+). Let
`a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, `s=dot b`, `H=dot a/a>0`,
`x=ln(a/a_i)`, `r=s/H`, and `K=8 pi G/c^2`. In a normal orthonormal frame,
`pi_m=diag(-p_m,-p_m,2p_m)` and
`p_m=(P_parallel-P_perp)/3`. Signed normalized quantities are
`S_F=sqrt(6)s/H`, `P_m,F=sqrt(6)K p_m/H^2`. The grid uses full Frobenius
normalization. Massive matter here is the owner's collisionless nonbaryonic
component (fraction0.1, reference mass/temperature ratio30), not baryon gas.

The exact source conventions and conserved momentum representation are in
`PHYSICAL_CONVENTION_ADAPTER.md` at the source pin. We reuse its source mapping
and D9's immutable compact array input; no literature novelty is claimed.
Physical target P_m,i=0 selects isotropic initial angular matter distribution
in this specified one-parameter owner family. Zero stress alone would not
imply isotropic distribution for arbitrary distribution families.

## Exact pressure hierarchy

Let conserved covariant momenta be q_i, physical orthonormal momenta
`k_i=q_i/a_i`, energy `E=sqrt(m^2 c^4+c^2 sum k_i^2)`, and physical volume
factor `V=a_perp^2 a_parallel=a^3`. All integrals below include the same
positive number normalization and conserved distribution f(q). Define

    P_i = V^-1 integral f c^2 k_i^2/E d^3q
    Q_ij = V^-1 integral f c^4 k_i^2 k_j^2/E^3 d^3q.

Since `dot k_i=-H_i k_i`, `dot V=3HV`, and
`dot E=-sum_j H_j c^2 k_j^2/E`, differentiation gives exactly

    dot P_i = -(3H+2H_i) P_i + sum_j H_j Q_ij.

Equivalently `P_i'=-(3+2g_i)P_i+sum_j g_j Q_ij`, where
`g_perp=1-r`, `g_parallel=1+2r`. These are energy density pressures;
both P and Q have units J/m^3. This hierarchy involves higher moments and
does not by itself impose a closed fluid model.

At initial isotropy P_i=Pbar, Q_ii=3q4, and Q_ij=q4 for i!=j. Define

    beta_P = [integral f (c^2 k^2/E)(c^2 k^2/E^2) d^3q]
             /[integral f c^2 k^2/E d^3q],
    q4 = Pbar beta_P/5.

Positive massive distributions with nonzero pressure have 0<=beta_P<1;
the massless limit is beta_P=1. Taking the parallel-minus-perpendicular
equation divided by three yields

    p_m'(0) = -2 r_0 Pbar_m,0 (1-beta_P,0/5),
    P_m,F'(0) = -2 S_F,0 [K Pbar_m,0/H_0^2](1-beta_P,0/5).

Thus positive initial shear generates negative signed matter stress. Its
initial sign is fixed without needing the numerical pressure amplitude.
When S_F,0=0 and P_m,F,0=0, initially all momentum directions redshift
isotropically, so the first anisotropic derivative vanishes. Using the owner
shear equation `S_F'=-(3+H'/H)S_F+P_m,F+P_r,F`, one more derivative gives

    P_m,F''(0) = -2 P_r,F,0 [K Pbar_m,0/H_0^2](1-beta_P,0/5).

Nonzero radiation stress then generates matter stress at quadratic order
with opposite sign. If all three initial signed axes vanish, isotropic
evolution preserves p_m=0 in the continuum model. The saved samples are a
finite numerical realization, not exact derivatives at x=0.

## Finite-deformation sign relation

For fixed x and conserved q, put `u=c^2 k_parallel^2`,
`v=c^2(k_x^2+k_y^2)`, and `M=m^2c^4`. The LRS pressure difference
integrand is `D=(u-v/2)/sqrt(M+u+v)`. Here `du/db=-4u`, `dv/db=2v`.
Direct differentiation gives

    dD/db = -[M(4u+v)+2u^2+7uv+v^2/2]/(M+u+v)^(3/2).

This is negative for each nonzero momentum. V is independent of b. For an
initially isotropic conserved distribution, its integrated pressure
difference vanishes at b=0 for every fixed x. Therefore the exact continuum
stress has sign(p_m)=-sign(b), and vanishes exactly at b=0. This relates stress
to accumulated anisotropic deformation, rather than the instantaneous shear.
The mathematical result requires positive, nonzero isotropic distribution
and finite differentiable pressure integrals, satisfied by the owner's
finite-temperature reference distribution. We make no new no-go claim;
NG1–NG7 novelty admission is not applicable.

## Data-only implementation and acceptance

Recover byte-exact `D9_COMPACT_INPUT.npz` and `D9_COMPACT_IDENTITY.json`
from the source pin under D9 `results/portable_input/`. Retain source and
identity mappings. Select 35 distinct histories by the physical initial
target P_m=0: seven initial Sigma_F values [0,.0003,.001,.003,.01,.03,.1]
times five signed radiation values [-.001,-.0003,0,.0003,.001]. Do not
select by rounding the realized stress. Use all153 saved epochs z20→2.

If compact input has no b, compute `b_reconstructed=integral s/H dx` with
b_i=0 and cumulative Simpson. It is a sampled quadrature reconstruction;
record trapezoid-minus-Simpson sensitivity and never label it stored b or
an exact continuum reconstruction. Existing D9 budget computation is not
rerun. Production does not evaluate momentum moments.

Per case report initial/final/maximum-absolute signed normalized matter stress,
first sample with |P_m,F|>1e-12, initial shear/radiation, final reconstructed b,
quadrature sensitivity, and stress/deformation sign counts. For sign comparison
omit |P_m,F|<=1e-12 or |b_reconstructed|<=1e-10 and classify them explicitly as
nearzero/unresolved. These thresholds classify finite diagnostics; they are
not a claimed rigorous integration error. Preserve every unexpected sign.
If the two quadrature choices disagree in sign, classify the deformation
comparison as quadrature-sensitive, even if its magnitude exceeds threshold.
The local predicted onset signs may be compared to the first resolved sample
as observations, never promoted to a derivative estimate.

Acceptance for this bounded unit: correct immutable source and selector,
finite arrays/positive a,H/strictly increasing x/common grids, complete35-case
output, honest sign/sensitivity classifications, and targeted controls.
Unexpected physical signs require return to Astra; no silent tuning of
thresholds. A new output can legitimately preserve a diagnostic discrepancy.
Controls: analytic quadratic s/H on a nonuniform x grid, neutral case,
wrong-case-count/axis-grid rejection, and nonmonotone-grid rejection.
Aggregate implementation-test/analysis CPU60s and each process wall60s,
BLAS1; one production pass. Stop after one sufficient independent review,
with targeted repair only for a concrete defect. No performance campaign.

Deliver executable Python, full inputs and source identity, RESULT/CSV/raw
logs/timing, concise implementation note and an actual-data figure. Root owns
publication and backups, and a fresh Astra reviewer owns scientific admission.
R1–R3/C1–C2 reuse exact owner evidence; R4–R5/R9 and C3–C4 are this derivation
and contract; R6–R8/C5–C9 require actual execution/review; R10/C10 bind the
final scoped outcome and delivery. Prior cohorts and failed AGE gates retain
their identities and are never merged with these35 reused trajectories.

## N6 deduplication

PR221 latest9620e1fcc4bdda76e0311206f614234926600381 was read directly.
Its PR body still describes the older569f784e atomic unit; the actual head
files, specifically `rei_coupled_local_flow_20261022/RESUME.md`, are
authoritative for the later completed local-flow work.
The original atomic sandbox569f784e already has rank-one electron feedback,
conditional coefficient policy, supplied-event assembly, and156 baseline
checks plus two separately invoked onset checks. Latest9620 adds
`rei_coupled_local_flow_20261022`: evolving-T pure-H Case-A RR with escaped
energy, prescribed-T neutron beta/RR, exact VF thermal orbit, Bessel
reference, positive Strang stages;103 baseline checks and separate96 timing
guards. Reuse all as prior units. Thermally coupled beta/RR next requires
electron/neutrino/recoil partition and stopping/escape choices. No physical
daughter branching, beta heating partition, or unprovided coefficient is
fabricated in D10.
