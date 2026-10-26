# Frozen Bianchi-I stress response for the selected H1 source

Unit REI-COUPLED-FOLLOWUP-20261026. Basis: derived; the scalar response identities have a separate Wolfram symbolic check. This is a conditional constant-background, collisionless nonrelativistic response component, with an explicit source orbit. It supplies a concrete geometry input/error map without replaying a trajectory.

## Definition, conventions and actual anchors

Use signature (-,+,+,+), proper time t in seconds and a Fermi-propagated normal orthonormal tetrad. Let expansion K_geom=H I+sigma with symmetric trace-free sigma. Physical kinetic stress P_ij has units J m^-3, U=tr(P)/2, p=tr(P)/3 and pi=STF(P). The kinetic approximation is E=p_particle^2/(2m); relativistic corrections and collisions are separate operators.

The preserved input is ../event_consumer_20261026/runtime_inputs/endpoint/ACTUAL_STATE_BINDING.json relative to the pilot parent (i.e. ../../event_consumer_20261026/... from this file). It is the saved endpoint, not a new interpolation:
H=6.6227883620909854e-18 s^-1,
sigma=diag(-s,-s,2s), s=8.642688723850055e-20 s^-1.
The previous source contraction supplies K_inj=1.4625823043267652e-36 J m^-3 s^-1. Its angular joint input remains unspecified.

The prescribed diagnostic orbit holds H, sigma and the proper-volume source fixed. This is an explicit mathematical continuation of an instantaneous input; its physical freezing error and collision-free validity time are not supplied by the endpoint.

For the previously derived unpolarized H1 ground-state E1 angular law, introduce the energy-weighted photon-direction moment M>=0, tr(M)=1. The momentum-stress injection is
S=(2 K_inj/5)(2I-M).
Consequently tr(S)=2 K_inj, S>=0 and STF(S)=-(2 K_inj/5)(M-I/3).
The actual energy marginal fixes K_inj but does not choose M.

## Moment equation and energy check

A freely moving nonrelativistic particle obeys dot(p_i)=-(H delta_ij+sigma_ij)p_j. Proper-volume number dilution contributes 3H. Differentiating the physical second moment therefore gives

dot(P)=-5H P-sigma P-P sigma+S.                                      (1)

An equivalent derivation integrates the homogeneous orthonormal Vlasov equation
partial_t f-(K_geom p).grad_p f=source
against p_i p_j/m, with vanishing momentum-boundary terms. One integration by parts contributes tr(K_geom)=3H and the two momentum factors contribute K_geom P+P K_geom.

Taking half the trace and the trace-free part gives

dot(U)=-5H U-sigma:pi+K_inj,                                      (2)
dot(pi)=-5H pi-STF(sigma pi+pi sigma)-2p sigma+STF(S).              (3)

Equation (2) equals dot(U)+3H(U+p)+sigma:pi=K_inj because p=2U/3. Dimensions on every term are J m^-3 s^-1. Expansion work is distinct from the local stopping/bath heat of stopping/DERIVATION.md. An implementation that retains only STF(S) and -5H pi drops the actual -2p sigma coupling.

For initially empty P and an isotropic incident moment M=I/3, S=(2K_inj/3)I:
pi(t)=-(2K_inj/3)sigma t^2+O(t^3).
Thus an isotropic injection does not stay isotropic on this anisotropically expanding background. This is a derived local response, not a newly claimed general no-go theorem.

## Exact positive response

Set B=(5H/2)I+sigma. For constant B and source S, P(0)=0,

P(t)=integral_0^t exp(-B v) S exp(-B v) dv.                        (4)

Every integrand is a congruence of a PSD matrix, so P(t)>=0. Positivity does not require B positive. For a diagonal sigma, define alpha_ij=5H+sigma_i+sigma_j and
A(a,t)=integral_0^t exp(-a v)dv,
A(a,t)=-expm1(-a t)/a when a!=0, A(0,t)=t.
Then P_ij(t)=S_ij A(alpha_ij,t). Source-free initial stress adds
P0_ij exp(-alpha_ij t).
This is a finite expression, with no time stepping or numerical quadrature.

For the actual endpoint, alpha_min=5H-2s>0. Let b_min=alpha_min. The operator norm in Frobenius norm satisfies
||L_t(X)||_F <= A(b_min,t)||X||_F.
For two angular inputs at the same K_inj,

||delta pi(t)||_F <= (2K_inj/5) A(b_min,t)||delta M||_F.            (5)

Proof: ||exp(-Bv) X exp(-Bv)||_F <= exp(-b_min v)||X||_F; integrate, then use that STF is an orthogonal projection. Also
tr(P(t)) <= 2K_inj A(b_min,t).
These are source-orbit bounds, not numerical-discretization or source-calibration error estimates. If K_inj is also uncertain, propagate the full delta S; replacing it by a same-K angular error would omit the trace variation.

## Explicit stress-to-shear response of a fixed operator

In Bianchi I the trace-free Einstein equation, in these units, is
dot(sigma)+3H sigma=(8pi G/c^2)pi_total.
For the declared operator with H held fixed, define the forcing response
dot(delta sigma_forced)+3H delta sigma_forced=(8pi G/c^2)pi(t),
delta sigma_forced(0)=0.
This isolates the stress-forcing contribution. The full linearized Einstein system also contains -3 delta H sigma_background, changes in other sectors and the Hamiltonian constraint; these remain separate inputs.

Write R(a,b,t)=integral_0^t exp[-a(t-u)] A(b,u)du. Its closed form is
R(a,b,t)=[A(a,t)-A(b,t)]/(b-a), for a!=b.
For a=b!=0,
R(a,a,t)=[1-(1+a t)exp(-a t)]/a^2;
R(0,0,t)=t^2/2.
The integral representation covers all removable limits and proves nonnegativity for real a,b and t>=0. Its regular local series is
R=t^2/2-(a+b)t^3/6+(a^2+ab+b^2)t^4/24+O(t^5).

Let Z_ij=S_ij R(3H,alpha_ij,t). Then
delta sigma_forced=(8pi G/c^2) STF(Z),                            (6)
and
||delta(delta sigma_forced)||_F
 <= (8pi G/c^2)(2K_inj/5)R(3H,b_min,t)||delta M||_F.              (7)

Both sides of (6)-(7) have units s^-1. The dimensionless observable-facing diagnostic is delta sigma_forced/H for H!=0, with the signed tensor retained before any norm. For H=sigma=0, P=S t and delta sigma_forced=(8pi G/c^2)STF(S)t^2/2. For isotropic M on the nonzero background shear, the leading forced response is -(8pi G/c^2)(2K_inj/9)sigma t^3.

## Symmetry, invariants, observables and dependencies

- Symmetry/gauge: spatial orthonormal rotations act by congruence on P, sigma, S and M; the equations and Frobenius bounds are covariant. A Fermi frame fixes the rotational gauge. A rotating tetrad requires its commutator term. The diagonal formulas are a chart for the constant symmetric expansion tensor.
- Invariants/structure: tr(M)=1, PSD P, the exact kinetic energy/work identity (2), and signed STF projection. Local expansion work is not a globally conserved kinetic energy.
- Observable-facing output: signed pi and the forced shear contribution (6), with explicit angular uncertainty (5),(7). A coupled H/shear history requires the missing feedback terms, source history, collisions and a freezing-error budget.

This result maps to B3i/HE-FEEDBACK/REI-L3/L4 component obligations. Their original canonical gates remain open. It adds no canonical completed node.

## Primary comparison and verification

Heinzle and Uggla, arXiv:gr-qc/0512031v1, Sec.2 Eqs.(2c),(2f),(3), derive the homogeneous Vlasov representation and physical stress for Bianchi I. Their k_ij is minus our expansion convention; their G=c=1 is restored here. The present nonrelativistic frozen source response is derived above, not attributed as a theorem of that paper. Exa and SciSpace located the paper; arXiv PDF was read directly. SciSpace's repository date2022 is not the publication date: arXiv submission2005 and journal2006.

Wolfram returned zero for the response ODE residual, equal-rate limit residual, A-ODE residual and zero-rate limit residual, and the displayed R-series. Its removable-limit warnings are preserved with the actual response in WOLFRAM_CHECK.json. WolframContext initially returned an internal tool error; direct evaluator worked. Remote CPU is UNKNOWN_NOT_ZERO. No local scientific run, trajectory, plot or physical freezing-error calibration was performed for this derivation.
