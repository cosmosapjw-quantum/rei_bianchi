# Independent H1 CI gain-moment derivation

Status: constructed for the HE36 follow-up, workflow1.0.0 / approval0.2. This is
an independent derivation and a source-model qualification; it is not a new
novelty or strong no-go claim. No HE32–HE36 IVP, scientific suite or plot is
re-executed here.

## 1. Definitions and the admitted limit

Use the local orthonormal common-bulk rest frame, metric convention (-+++),
and explicit SI constants. Write θ=k_B T_e, E=m_e v²/2 for incident electron
laboratory kinetic energy, and I>0 for the chosen ground-state ionization
defect. The target is H1 in a stationary, infinitely heavy-target limit. The
reaction is e+H→e+e+p. Its event cross section σ(E) counts one ionization,
not two final electrons; K(E)=sqrt(2E/m_e) σ(E). All electron products remain
in the kinetic inventory under consideration. A separate thermalization or
finite-amplitude closure is not inferred.

The incident electron distribution has the infinitesimal STF first variation

    f_e(v)=f_M(v) [1 + E π_e:(n n)/(n_e θ²)] + O(π_e²),

where n=v/|v|, tr π_e=0 and P_e=n_e θ Id+π_e. This is the derivative at a
Maxwellian, not a claim that a finite polynomial Grad distribution is globally
positive. Scalar rate, energy and tensor sources below are instantaneous
first-variation results at this reference state.

The radial Maxwellian probability measure is

    dM_T(E) = 2 sqrt(E) exp(-E/θ) dE / (sqrt(π) θ^(3/2)).

Define α=<K>, β=<E K>, γ=<E² K>, where <> means this radial measure. These are
the same definitions as HE36. Rates are evaluated only for a declared common
energy support and the same cross-section owner.

## 2. Minimal outgoing data: an inclusive second moment

At fixed E and incident direction n, let μ_E(dε dΩ) be the **inclusive outgoing
one-electron counting measure per ionization event**. It includes both final
electrons. Thus, in the recoil-free limit,

    ∫dμ_E=2,
    U(E):=∫ε dμ_E=E-I,
    D(E):=∫ε P₂(n·r) dμ_E,

where r is an outgoing electron direction and P₂(z)=(3z²-1)/2. Nonnegative
energy/differential probabilities and rotational covariance about n imply

    -(E-I)/2 ≤ D(E) ≤ E-I.                                      (1)

The conditional gain pressure tensor is

    B_gain(E,n) = ∫2ε r r dμ_E
                = (2U/3) Id + 2D (n n-Id/3).                   (2)

To verify the factor of two, the longitudinal contraction is
2∫ε cos²χ dμ_E = 2U/3+4D/3, while tr B_gain=2U. There are only two scalar
invariants for this axisymmetric symmetric second tensor. Higher angular
Legendre orders and correlations between the two outgoing electrons do not
enter number or the additive second moment. They may matter for other
observables and for a nonlinear kinetic closure.

A two-electron joint differential cross section is sufficient but unnecessary
for these observables. An inclusive energy/angular DDCS with the normalization
above is sufficient. A total cross section alone, or a singly differential
energy distribution without angular information, does not supply D. If a
source reports only the slower electron on [0,(E-I)/2], it is necessary to
recover the other electron's angular moment or a stated model; doubling the
slow-electron energy moment is generally wrong.

One may avoid division by a vanishing σ near threshold by using cross-section
weighted moments directly:

    Nσ(E)=∫dσ_inc=2σ(E),
    Uσ(E)=∫ε dσ_inc=(E-I)σ(E),
    Dσ(E)=∫εP₂(n·r)dσ_inc=D(E)σ(E).

The event cross-section and inclusive DDCS multiplicity conventions must be
matched before admission.

## 3. Incoming loss plus outgoing gain

The removed incident electron contributes B_loss=-2E n n per event. Angular
isotropy gives

    <(n n-Id/3)(π_e:n n)>_Ω = 2π_e/15.

Combining this identity with (2), the scalar and STF sources are

    R_e = +n_e n_H α,
    R_H = -n_e n_H α,   R_p = +n_e n_H α,                       (3)
    Q_gain = n_e n_H (β-Iα),
    Q_loss = -n_e n_H β,
    Q_net  = -n_e n_H Iα,                                      (4)
    J_gain = (4n_H/(15θ²)) <E K D> π_e,
    J_loss = -(4n_H/(15θ²)) γ π_e,
    J_net  = -ν_net π_e,
    ν_net  = (4n_H/(15θ²)) <E K(E-D)>.                         (5)

Here Q=tr S/2 and J=S-(2Q/3)Id. Consequently

    S_net = -(2n_e n_H Iα/3) Id - ν_net π_e,                   (6)

and tr S_net/2=Q_net. The scalar first-variation contributions vanish because
tr π_e=0. Incident parity also makes the bulk momentum source vanish in this
common-rest/no-drift reference problem. This parity statement does not
justify omitting momentum data in a drifting or asymmetric problem.

The heavy atom-to-ion pressure/kinetic content is carried with the heavy
particle unchanged at leading recoil-free order. If a heavy Maxwellian
inventory is retained, its parent/daughter transfer cancels in the sum; it
must not be discarded twice. The stationary-target kernel does not certify a
finite-mass proton recoil tensor or the full finite-mass HE36 pair source.

For an all-retained common thermal pool the total particle source is the
electron source R_part=R_e, because R_H+R_p=0. The non-expanding reaction-only
temperature balance is

    dot T = [2Q_net/(3k_B) - T R_part]/n_part
          = -[n_e n_H α/n_part] [T+2I/(3k_B)].                 (7)

The number-change term is essential and must not also be inserted into the
energy ledger. Equation (7) assumes such a common-T thermal closure. It is not
a proof that newly ionized electrons equilibrate instantaneously. With a fast
electron population the separate thermal number and energy sources are needed.

## 4. Constructive angular bounds

From (1), E-D lies between I and (3E-I)/2. Therefore

    4n_H Iβ/(15θ²) ≤ ν_net ≤ 2n_H(3γ-Iβ)/(15θ²).              (8)

These are bounds over nonnegative rotationally covariant recoil-free outgoing
models at fixed σ, not an uncertainty estimate for actual H1 differential data.
Forward emission of all final kinetic energy saturates the lower pointwise
bound; perpendicular emission saturates the upper pointwise bound. The
isotropic-outgoing case D=0 is between them. The coefficient is nonnegative,
but this is not a complete coupled-system entropy or finite-anisotropy theorem.

Relative to κ₂=4γ/(15θ²), write r=Iβ/γ ∈ (0,1]. Then

    r ≤ ν_net/(n_H κ₂) ≤ (3-r)/2.                             (9)

This interval quantifies what angular information is still unselected if only
the event cross section is known. It does not select a physical point inside
the interval. If D(E)=b(E)(E-I), a constant b gives

    ν_net=4n_H[(1-b)γ+b Iβ]/(15θ²), -1/2≤b≤1.

## 5. Source-qualified isotropic model

H. P. Le and J.-L. Cambier, *Modeling of ionization/recombination processes
using a multifluid framework*, Physics of Plasmas 23, 063505 (2016),
doi:10.1063/1.4953050, https://arxiv.org/abs/1605.06545, supplies the selected
published approximation. The author manuscript was inspected directly in
`/tmp/he37_sources/raw/le_cambier_2016.txt`:

* Eq. (7), printed p.5, sets the energy transfer Υ and its interval [I,E].
* Section III.E, printed p.15 (text extraction lines ~780–798), takes the
  small electron/heavy mass ratio limit and explicitly assumes
  G_ion=1/(16π²), the uniform two-outgoing-solid-angle law. This is an assumed
  model, not a measurement or CCC-calibrated angular law.
* Section VI.A, Eq. (85), printed p.25 (lines ~1291–1316), specifies the
  semiclassical differential and integrated cross sections. The paper refers
  this cross section to its reference26; that book was not independently
  audited here.

For ground H, I=I_H=13.6 eV is the source-model value and

    dσ/dΥ = A/(Υ² E),       A=4π a₀² I_H²,
    σ(E)  = A(E-I)/(I E²),  E>I,
    σ(E)  = 0,              E≤I.                             (10)

Source numbers a₀=0.529 Å and I_H=13.6 eV differ from a modern-constants
realization; whichever is used must be recorded as part of the provider
identity. The source's threshold is not silently replaced by the existing CCC
fixed-nucleus table threshold13.6058eV, or by an isotope-adjusted threshold.

The conditional energy-transfer density is

    p(Υ|E)=I E/[(E-I)Υ²],  I≤Υ≤E,                            (11)

which integrates to one. In this mass approximation the two outgoing
electron energies are ε₁=E-Υ and ε₂=Υ-I. They sum to E-I for every event.
The labels are ordered scattering/ejected roles in the model; observables
sum both electrons, without doubling the event cross section. Relabeling or
symmetrizing the joint law leaves these additive observables unchanged.

With G=1/(16π²), both single-electron angular marginals are isotropic and
D(E)=0. Thus the complete gain calculation for number, energy and this STF
first variation requires no energy-sharing quadrature:

    R_e=+n_e n_H α,
    Q_net=-n_e n_H Iα,
    J_net=-n_H κ₂ π_e,  κ₂=4γ/(15θ²).                         (12)

The equality of this STF coefficient to the HE36 incoming-only coefficient
does not make the old incoming-only heat a net heat. The isotropic gain
returns β-Iα to scalar electron kinetic energy while returning zero STF in
this model. This is a constructive reduction of a specific differential
model, not a claim that physical H1 CI angular anisotropy vanishes.

## 6. Analytic Maxwellian moments and stable computation

For (10), define

    C=sqrt(8/(πm_e)) (A/I) θ^(-3/2),   x=I/θ.

Direct substitution into the Maxwellian integral gives

    α=C[θ exp(-x)-I E₁(x)],
    β=C θ² exp(-x),
    γ=C θ²(I+2θ) exp(-x),
    δ=C θ²(I²+4Iθ+6θ²) exp(-x).                              (13)

Here E₁(x)=∫_x^∞exp(-y)dy/y. The source model is integrated over its declared
nonrelativistic domain [I,∞); these analytic expressions do not certify its
physical calibration or relativistic accuracy outside a separately admitted
temperature range. The rate can be evaluated without subtracting nearly
equal large-x terms:

    F(x)=∫₀^∞ [t/(x+t)] exp(-t)dt=1-x exp(x)E₁(x)>0,
    α=C θ exp(-x) F(x).                                      (14)

This representation uses a positive one-dimensional quadrature or a qualified
scaled special function. β,γ,δ then require no quadrature. The formal
large-x expansion is

    F(x) ~ 1/x - 2/x² + 6/x³ - 24/x⁴ + ….

It is asymptotic, not a convergent fixed polynomial valid at all x. For x>0,
Jensen applied first to the Gamma(shape2,scale1) representation of F, and then
to E₁'s exponential representation, gives

    1/(x+2) ≤ F(x) ≤ 1/(x+1),
    I+θ ≤ β/α ≤ I+2θ,
    γ/β = I+2θ,
    4(x+2)(x+1)/15 ≤ κ₂/α ≤ 4(x+2)²/15.                     (15)

These are stable provider sanity bounds, not empirical errors. At tiny rates
the common exp(-x) factor must retain a log representation/underflow status;
a nonzero rate rounded to zero cannot be called a physical support zero.

## 7. Finite target recoil is a separate dependency

For a stationary finite-mass target, the outgoing ion momentum is
q=p₀-p₁-p₂. Since ε₁+ε₂≤E-I,

    E_recoil=q²/(2M)
      ≤ (m_e/M) [sqrt(E)+sqrt(2(E-I))]².                     (16)

This follows from the triangle and Cauchy inequalities. It bounds an energy
scale at a fixed incident energy; it is not a bound on the full finite-mass
differential kernel, angular source, common-T closure or stress-tensor error.
For positive radial weights it also implies

    <K E_recoil> ≤ (m_e/M)
      [3β-2Iα+2 sqrt(2β(β-Iα))].                             (17)

The inequality uses Cauchy on <K sqrt(E(E-I))>. Equation (17) is conditional
on the same incident event kernel and is not a license to add recoil heat to
a kernel whose outgoing energies already exhaust E-I. A finite-recoil model
must change energy sharing and conserve energy consistently.

## 8. Independent validation scope

`check_gain_derivation.py` performs new deterministic direct angular
integrations of number, energy, second-tensor baseline and the infinitesimal
Grad derivative, using an explicit pair of outgoing electron vectors and
the source energy-transfer CDF. It compares these raw moments with (2)–(6)
for an isotropic and an energy-dependent positive P₂ toy law. The latter is
a manufactured discriminating control, not admitted H1 data. It also checks
(13)–(15) by a separate adaptive radial integral and the normalization of
(11). The tests are for this new outgoing-gain dependency only.

Required remaining physical dependencies are calibrated H1 angular DDCS if
replacing this model, finite-mass recoil/thermal transfer for such an
extension, separate thermalization/fast-electron census when needed, and the
chosen thermal/UV, other atomic and nuclear process providers. None is
declared completed by equations (12)–(15).
