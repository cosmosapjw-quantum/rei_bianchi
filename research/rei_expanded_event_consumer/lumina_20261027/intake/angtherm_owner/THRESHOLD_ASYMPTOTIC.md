# ANGTHERM02: local threshold asymptotics

Independent constructive derivation. No new numerical gate, IVP, or criterion
change is introduced. The variable mu below is the conserved initial direction
mu0, with fixed-q measure dmu0. The calculation concerns the optically thin rate
already defined in THEORY_CONTRACT.md.

## Assumptions and notation

Let eta_L be the last transverse crossing for the positive-b background:

    E0 exp[b(eta_L)-eta_L] = chi,  E0=10 eV, chi=5.392 eV.

Put t=eta_L-eta>0 and define

    beta_* = 1-b'(eta_L) > 0,
    C_* = 1-exp[-6b(eta_L)] > 0,
    K_* = (c nHref/H)(eta_L),
    sigma_* = sigma_LiI(chi+).

Assume the background has the local regularity needed for the Taylor
remainders: b is C2 (or has a one-sided second-order expansion), nHref/H is
C1, and the adopted cross-section fit is C1 from above at chi. These conditions
refer to the local interpolant, not an unsaved Einstein-solution error bound.
The adopted nonzero right-threshold cross section is essential for the stated
leading powers. This expansion does not apply to the degenerate b=0 common
threshold.

## Active angular width

Write the characteristic energy as

    E(eta,mu0) = E_perp(eta) sqrt[1-C(eta) mu0^2],
    E_perp(eta) = E0 exp[b(eta)-eta],
    C(eta) = 1-exp[-6b(eta)].

At eta=eta_L-t,

    E_perp = chi [1+beta_* t+O(t^2)],
    C = C_*+O(t).

The exact threshold equation is

    C mu_c^2 = 1-[chi/E_perp]^2 = 2 beta_* t+O(t^2).

Consequently

    mu_c = sqrt(2 beta_*/C_*) t^(1/2)+O(t^(3/2)).

Thus a positive-b transverse last crossing closes an interval of fixed-q
angular measure proportional to sqrt(t).

## Rate and photoelectron-heating coefficients

Rescale the active interval by mu0=mu_c x, 0<=x<=1. Uniformly on that interval,

    E-chi = chi beta_* t (1-x^2)+O(t^2),
    sigma_LiI(E) = sigma_*+O(t),
    c nHref/H = K_*+O(t).

Define the positive coefficient

    A_* = G0 K_* sigma_* sqrt(2 beta_*/C_*),  G0=0.05.

The photoionization coefficient is therefore

    Lambda0 = A_* t^(1/2)+O(t^(3/2)).

For the excess photon energy transferred to the photoelectron,

    LambdaE-chi Lambda0
      = G0 integral_0^mu_c (E-chi)(c nHref/H)sigma_LiI(E) dmu0
      = (2/3) chi beta_* A_* t^(3/2)+O(t^(5/2)),

where the factor 2/3 is integral_0^1 (1-x^2) dx.

The proposed controller coefficients and remainder orders are correct under
the assumptions above. No fit-specific numerical evaluation is needed to
establish these powers.

## Physical and numerical interpretation

Near the final crossing, photoionization retains the leading sqrt(t)
dependence of the surviving angular width. Photoelectron heat has one extra
power of t because each surviving photon has only O(t) energy above threshold.
Multiplication by the actual fLiI gives the event terms; converting them to
per-Href quantities additionally multiplies by YLi.

This explains why an angular-support error can be prominent in native Li
fractions while the corresponding photoelectron-heating contribution is
weaker. It does not bound the total temperature error, RR cooling, or coupling
to other species. In particular, the ionization-potential contribution
chi Lambda0 remains of order sqrt(t); it is the *excess-energy heating*
coefficient that is suppressed.

Although Lambda0 reaches zero continuously, its time derivative generally
diverges as -A_*/[2 sqrt(eta_L-eta)]. The heat coefficient has a finite
vanishing first derivative but generally a singular second derivative.
The existing endpoint time split is therefore justified by the local
structure of the continuum rate. A finite fixed-ray rule instead loses each
ray's nonzero threshold cross section in separate jumps; the continuum
square-root limit is obtained only after angular integration.

If fLiI stays finite and continuous at eta_L, the integrated final-window
photoionization contribution scales as t^(3/2), whereas the integrated
photoelectron heat scales as t^(5/2). These are local leading-order statements,
not a numerical convergence order or an additional acceptance test.

