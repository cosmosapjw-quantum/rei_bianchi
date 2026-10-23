# Angular thermochemistry synthesis — constructive theory

Authority: Astra controller. Protocol: physmath-research-loop intrinsic 1.0.0,
approved v0.2. Date: 2026-10-23. This is an additive continuation of REI PR221
at `73c5e00cac26b4efc782446975bd6b6762555997`.

## Question and precise new contribution

Combine the already implemented C13/C15 photon characteristics and C16
pressure/shear work with the latest C22A 21-population photoionization,
Case-A recombination and common-temperature event ledger. Evolve this trace
system on two actual saved C21O backgrounds over z=20 to 2. Establish an exact
joint isotope/angular quotient and use optical-depth photon coordinates to
avoid numerically evolving rapidly extinguished photon inventories.

Directional transport itself is reused, not a new discovery. C13–C16 cover
a=.1999 to .2 and H/He gas with a different warm Grackle rate model. C22A
uses the latest H/D/T/He3/He4/Li6/Li7 bookkeeping and a dynamic temperature,
but its six UV cohorts redshift with the mean scale factor. This unit joins
the compatible equations and tests the new composition and reductions.

The saved background is prescribed. The new UV/gas trace does not modify
the donor H, shear, CMB, neutrino or massive-Vlasov history. Its new electron
density and Thomson optical depth are computed separately. The original
background's Thomson calculation used its original chemical history.
The result is a conditional source-preserving numerical experiment, not an
astrophysical reionization history or a closed Einstein–Boltzmann model.

## 1. Source and convention map

* REI C13 `d7d0e3ad2d6d7cccdfd70df3a0f310df93ec553d`,
  `research/rei_c13_live_source_20261015/short_interval.py`, PhotonCloud.drift:
  exact fixed-Killing-momentum map and number-per-H measure.
* REI C15 `435c94308c0cd7b1ba8ff6518246da061f2fc2fa` and C16
  `af67c5314669492b07cb574170c09f70994974e4`: signed radiation moment and
  independent geometry-work identity. Historical display norm sqrt(3)|s|/H
  is replaced by the current full Frobenius convention sqrt(6)|s|/H.
* BASS_CR `15fd250ab91574bd4f3348e91d739a15a6ed6005`, C22A model.py and
  rr_energy_moment.py: common-T photo/RR event ledger and VF-fit kinetic
  capture-energy moment. Atomic provider files are also present and verified
  at reachable selected-source commit `ba39fc75521aa18705ec832d789e50dd5c6565bc`.
* BASS_CR C21O grid044 and grid022 at the former commit: two saved 201-node
  backgrounds, not new integrations. Their raw identities are in inputs.
* Verner et al. (1996), https://www.pa.uky.edu/~verner/photo.html:
  adopted ground-state photoionization fits and original tables. Cross
  sections returned in Mb convert to cm² by 1e-18.
* Pawlik & Schaye, arXiv:1008.1071; Friedrich et al., arXiv:1201.0602:
  photon-conserving multifrequency event/heat construction is established
  literature. Their independent algorithms are methodological references;
  this implementation does not import their full RT codes or claim their
  validation results for the present model.

Metric signature is (-,+,+,+); c, hbar, k_B are explicit. Proper H and s have
units s^-1. eta=ln(a/a_initial), so d/deta=H^-1 d/dt. Counts are per reference
H nucleus, not per baryon. Energies are eV per reference H nucleus. The exact
original composition has baryon/Href ratio B=1.32808000350006. Conversion to
per-baryon quantities divides counts and energies by B; n_B=B n_Href.

The frozen initial totals per Href are H1=1, D=2.5e-5, T=0, He3=1e-5,
He4=.082, Li7=5e-10, Li6=1e-14, n=0. Electronic isotope equality is an
explicit inherited approximation. Nonzero n/T beta heat remains an open
input and is not supplied by this unit.

## 2. Exact directional geometry and its number measure

Use the existing LRS Bianchi-I metric

    ds² = -c²dt² + a²e^(-2b)(dx²+dy²) + a²e^(4b) dz²,
    sigma_ij = diag(-s,-s,2s),  s=db/dt.

Spatial translation invariance conserves covariant photon momenta q_i.
At eta=0 set b=0 by a constant spatial coordinate rescaling. For a photon
with initial energy E0 and initial directional cosine mu0,

    D² = (1-mu0²) exp(2b) + mu0² exp(-4b),
    E = E0 exp(-eta) D,
    mu = mu0 exp(-2b)/D,
    E'/E = -[1 + b'(3mu²-1)] = -[1+2b'P2(mu)].

These formulas follow directly from E²=c² g^{ij}q_i q_j. Differentiating
mu gives mu'=-3b' mu(1-mu²). The code evaluates the exact map, not this ODE.
The stable form uses expm1/log1p for D near unity, as in C13.

For a homogeneous distribution the physical phase measure is
dn_gamma=2 f(q) d³q/[(2pi hbar)³ a³], with the initial scale normalization
included in q. A fixed q-space cell therefore contains a constant number
per conserved Href nucleus in collisionless evolution. A second angular
Jacobian must not be applied to those packet counts. Direction and energy
are pushed forward; the already integrated packet measure is retained.

For counts g_j define per-Href moments

    U_gamma = sum_j E_j g_j,
    Q = sum_j E_j g_j P2(mu_j),
    P = diag((U_gamma-Q)/3, (U_gamma-Q)/3, (U_gamma+2Q)/3),
    pi = diag(-Q/3,-Q/3,2Q/3).

Physical energy/stress is n_Href times these per-Href quantities (with unit
conversion to SI as needed). Tr(P)=U_gamma; sigma:pi=2sQ;
|sigma|_F/H=sqrt(6)|s|/H, |pi|_F=sqrt(2/3)|Q| per Href. Signed Q must be
retained before any tensor sum. UV is a radiation component; it is never
added to the massive-Vlasov matter stress by taking a sum of norms.

In collisionless evolution U_gamma'=-U_gamma-2b'Q. Since n_Href'=-3n_Href,
rho_gamma'+4rho_gamma+2b' n_Href Q=0. This is the required pressure-work
identity, including the angular motion of photons.

## 3. Event equations and one common temperature

Let y_i=n_i/n_Href, z_i be ionic charge, v=sum_i z_i y_i, and N_nuc the
conserved sum of nuclei per Href. Electron density is n_e=n_Href v.
U=(3/2) k_B (N_nuc+v) T. There is no additional evolved electron state.

For each adjacent electronic edge e:l->u and photon cohort j,

    A_ej = (c n_Href/H) y_l sigma_e(E_j) g_j,
    R_e  = (n_Href/H) v y_u alpha_e(T).

Here c is in cm/s, n_Href in cm^-3, sigma in cm², alpha in cm³/s; A,R are
counts per Href per eta. The same event is used for charge, photon loss,
thermal energy and the escaped reservoir:

    y_i' = sum_e nu_ie [sum_j A_ej - R_e],
    g_j' = -sum_e A_ej,
    U' = -2U + sum_ej (E_j-chi_e) A_ej - sum_e K_e(T) R_e,
    E_esc' = sum_e [chi_e+K_e(T)] R_e,
    W_gas' = 2U,
    W_mean' = U_gamma,
    W_shear' = 2b' Q,
    C_RR' = sum_e R_e,  C_abs' = sum_ej A_ej,
    tau_T' = (c sigma_T n_Href/H) v.

The thermal gas is nonrelativistic and isotropic. Its expansion work has
no shear contraction. Escaped Case-A photons are a bolometric ledger,
not a transported spectrum or a gravitating radiation distribution.
No external stellar emission is added in this finite-inventory experiment.

The VF fit is alpha=A/[r0(1+r0)^(1-bv)(1+r1)^(1+bv)],
r_i=sqrt(T/T_i). Define D_alpha=d ln(alpha)/d ln(T). The adopted capture
energy is K=k_B T (3/2+D_alpha), equivalently

    K/(k_B T) = (1-bv)/[2(1+r0)] + (1+bv)/[2(1+r1)].

For -1<=bv<=1 this form is positive. The Maxwellian differentiation identity
is exact for a temperature-independent microscopic kernel; applying it to
the frozen rate fit is a conditional constitutive closure. Number-fit
accuracy does not establish accuracy of its derivative or heat moment.
Reuse the unmodified C22A provider rather than substitute a different
cooling coefficient. Direct secondary ionization, CI, DR, line excitation,
free-free, Compton and nuclear/beta energy are not activated by this unit.
C22D/E/REC125 additions remain separately qualified donors, not silently
included in this event model.

Let I=sum_i B_i y_i with B_u-B_l=chi_e. Direct substitution proves

    d/deta [U+I+U_gamma+E_esc+W_gas+W_mean+W_shear] = 0,
    d/deta [v+C_RR-C_abs] = 0,
    d/deta [sum_j g_j+C_abs] = 0.

Each nucleus block is also conserved. These are independent checks when
the work/reservoir/count variables are integrated from their RHS, rather
than reconstructed by subtracting the other energies.

## 4. Exact isotope quotient

Write y_(a,q)=Y_a f_(a,q), where Y_a is the conserved isotope total. For
isotopes of the same electronic element the generator M_g(T,g,n_e) is the
same under the adopted equality approximation. If their initial fractions
are identical, uniqueness of the common linear conditional equation gives
f_(a,q)=f_(g,q) at every eta, even though M depends nonlinearly on the common
electron density, temperature and radiation. Then

    Y_H=1.000025, Y_He=.08201, Y_Li=5.0001e-10,
    v=sum_g Y_g sum_q q f_gq.

Three electronic blocks of sizes 2,3,4 replace 21 scaled populations. All
nine fractions are retained: neutral fractions are not obtained by a
potentially cancelling subtraction from one. Full isotope outputs are
lifted by their individual totals/scales. The zero n/T face is retained.
Mismatched initial fractions invalidate this quotient and must be reported;
they are not projected onto the quotient. No broad isotope or beta theorem
is claimed beyond these stated generator and initial-data equalities.

## 5. Exact angular quotient and optical depth

For the finite angular oracle choose M Gauss–Legendre nodes on mu0 in [0,1]
with weights summing to one. The expanded representation has +/-mu0 and
four uniform azimuths per node, each with one-eighth the group count.
The energy, radial cross sections and absorption coefficient depend only
on |mu0|, so all eight members of a group have the same extinction rate.
Their sum G_bm obeys exactly the same scalar absorption equation. Uniform
azimuth summation gives the stated diagonal pressure tensor exactly.

Thus 6*8*M packet counts become 6*M counts with exact finite-system
equivalence. This is not an angular-continuum accuracy assertion. The
folded tensor calculation assumes reflection/azimuth symmetry; an odd
dipole or a resolved nonaxisymmetric field requires additional moments.
The isotropic finite initial inventory in C22A satisfies these assumptions.

For G0_j>0 set ell_j=log(G0_j)-tau_j and G_j=exp(ell_j), where

    tau_j' = (c n_Href/H) sum_e y_l sigma_e(E_j), tau_j(0)=0.

This is an exact change of coordinates. It removes the decaying photon
diagonal -kappa_j from the photon subsystem, while retaining its coupling
to the gas. It guarantees nonnegative reconstructed counts in exact
arithmetic and stores log counts after ordinary counts underflow. It does
not prove that the whole nonlinear system is nonstiff.
Compute photo coefficients directly as exp(log(c n_Href/H)+log(sigma)+ell)
before multiplying by the signed trial population. Do not exponentiate a
raw photon count first and then multiply by a large conversion factor.
An exactly zero initial photon group remains a structural zero and has
no log(0) evaluation. Neither abundance floors nor clipping are permitted.

The full reference retains all 21 scaled populations and 48M direct photon
counts, with independent explicit event assembly. The optimized system
has 9 fractions, 6M optical depths and 8 integrated scalar ledgers,
so dimensions are 29+48M and 17+6M (M=4:221 versus41).

## 6. Jacobian and discriminating controls

T=U/[C_T(N_nuc+v)], C_T=3k_B/2. Therefore
T_U=1/[C_T(N_nuc+v)] and T_f=-T v_f/(N_nuc+v).
For a RR event, dR=(n_Href/H)[alpha(y_u dv+v dy_u)
+v y_u alpha_T dT], alpha_T=alpha D_alpha/T.
For a photo event at fixed eta, dA=(c n_Href/H)sigma[G dy_l+y_l dG].
In optical coordinates dG=-G dtau. Differentiating K from its positive
rational expression gives thermal and escape rows without finite-difference
rate approximations. This defines the analytic state Jacobian; finite
differences independently check it at interior states away from support
crossings. The reference may use a numerical Jacobian independently.

Controls must include: exact zero-shear map; collisionless number/energy
and pressure trace; opposite shear sign; the actual nearly-FLRW donor;
zero UV; isotope-ineligible initial data; odd-angular data; a deliberately
omitted shear-work term; and a direct-scaled subnormal photo coefficient.
The latter is a local representation control, not a new cosmic trajectory.
Support crossings of all thresholds and the LiI64.39eV provider switch are
split explicitly. The saved background is monotone-redshifting for the
adopted rays; verify this property for the actual interpolant.

## 7. Source background interpolation and error boundary

Use raw 201-node grid044/grid022 arrays. Subtract only b(0) as a constant
coordinate normalization. Define b(eta) by CubicHermiteSpline with donor
slopes s/H. Use the derivative of that same interpolant in work and
characteristic formulas. Define log H by PCHIP and n_Href by
n_Href(0) exp(-3eta), after comparing the latter with saved values.
This interpolation is part of the frozen prescribed model; no interpolant
error is promoted to an Einstein-solution error bound. Retain the tiny
nonzero b of grid022 in the actual donor case. A separate algebraic b=0
control tests the exact FLRW formula.

Continuum positivity follows from nonnegative event coefficients and
Metzler population generators. Numerical positivity is measured; it is
not guaranteed for general Radau/BDF stages. Signed Newton trial states
are allowed. No clipping, population renormalization or missing-rate zeros
are introduced. Below-threshold sigma=0 is physical support of the adopted
fit; unavailable processes remain explicitly outside this model.

## 8. Completion boundary

Admit this new finite synthesis only after independent math and math-code
review, agreement with the unfolded event oracle, conservation checks,
tolerance/refinement diagnostics and direct plot inspection. Preserve all
raw outcomes and costs. No universal speedup, new no-go theorem, fully
self-consistent reionization prediction, all-Bianchi completion or new
physical atomic accuracy is inferred from these checks.
