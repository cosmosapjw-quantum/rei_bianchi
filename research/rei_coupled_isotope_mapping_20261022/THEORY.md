# C2 derivation: compatible number and energy bindings

This note supplies the theoretical interpretation of the C2 binding diagnostic.
The event, mass-reference, charge and variable-particle EOS conventions are the
unchanged C1 contract. Numerical evidence is in `evidence/BINDING_CHECKS.json`;
no cosmological trajectory
is generated here. `CODE_MAP.md` identifies the actual implementation locations.

## 1. One electronic channel, several naming conventions

A recombination event has an initial target ion `(Z,q)` and product `(Z,q-1)`.
The donor's coefficient key is `Z:q`, with q the initial ionic charge. The
Verner–Ferland table names the recombined product and counts its electrons,
`N_product=Z-q+1`. Badnell's table counts electrons in the initial target,
`N_target=Z-q`, and adds an initial-state index M. An unqualified label such as
“Li I RR” therefore cannot serve as a universal join key.

| Electronic event | Donor key | VF product label / N | Badnell target N, M |
|---|---|---|---|
| H II + e -> H I | 1:1 | H I / 1 | not selected here |
| He II + e -> He I | 2:1 | He I (a) / 2 | not selected here |
| He III + e -> He II | 2:2 | He II / 1 | not selected here |
| Li II + e -> Li I | 3:1 | Li I / 3 | 2, 1 |
| Li III + e -> Li II | 3:2 | Li II / 2 | 1, 1 |
| Li IV + e -> Li III | 3:3 | Li III / 1 | 0, 1 |

For this model, H1/D/T share the first electronic row, He3/He4 share the two
He rows, and Li6/Li7 share the three Li rows. This produces 13 isotope-charge
RR edges without claiming isotope-specific measured cross sections. Photo
rows use the *initial lower* charge, so their key is `Z:q-1` for the inverse
electronic edge. The machine-readable map records both endpoints.

The six recovered candidate rows use VF coefficients. PR220 actually selects
VF for H/He and Badnell for Li. Their formulas have a common shape, but their
Li coefficients differ. The C2 probe preserves both choices. It does not infer
that either Li data set is more accurate from their numerical disagreement.
The source conventions follow the primary [VF table description][vf-table]
and [Badnell RR definition][badnell-rr].

## 2. Deriving the kinetic moment from a common cross section

Assume a stationary heavy target in a fixed internal state, nonrelativistic
Maxwellian electrons at temperature T, and an effective RR cross section
sigma(E) that does not independently depend on T or density. Let

    K = sqrt(8/(pi*m_e)) / k_B^(3/2)
    alpha(T) = K T^(-3/2) integral_0^infty E sigma(E) exp[-E/(k_B T)] dE
    lambda(T) = K T^(-3/2) integral_0^infty E^2 sigma(E) exp[-E/(k_B T)] dE.

Alpha has units m^3/s and lambda has units J m^3/s. The latter measures
the kinetic energy carried away by the electrons that actually recombine,
not the mean energy of an unweighted Maxwellian sample. Differentiating the
first integral under the same assumptions gives

    d alpha/d ln T = -(3/2) alpha + lambda/(k_B T),
    lambda = k_B T alpha [3/2 + d ln alpha/d ln T].

The cross-section and energy-weighted definitions agree with equations
(1)–(4) of [Mao, Kaastra and Badnell][rr-energy]. The derivative identity here
is a direct derivation from those Maxwellian integrals. It is not a claim that
the present empirical fit has been compared with that paper's energy data.
No data from its adf48 energy tables have been imported in this C2 unit.

This identity has a useful but finite scope. A finite collection of alpha(T)
samples does not determine the derivative without an interpolation model.
Using a differentiable analytic fit defines a **conditional derivative-of-fit
moment**. If alpha_fit=alpha_true*(1+epsilon(T)), then

    lambda_fit-lambda_true
      = k_B T alpha_true [(3/2+D_true)epsilon + d epsilon/d ln T].

Consequently, an error bound on the number-rate fit alone does not provide
an energy-moment error bound. Explicit temperature-dependent target fractions,
density suppression, or altered electron distributions also require their own
interpretation; their derivative cannot automatically be read as an electron
kinetic moment. These are applicability limits, not obstacles to evaluating
the clearly labelled finite fit diagnostic.

## 3. Badnell's temperature-dependent exponent

For either selected family write

    u=sqrt(T/T0), v=sqrt(T/T1), b=B+C exp(-T2/T)
    alpha=1e-6 A/[u(1+u)^(1-b)(1+v)^(1+b)].

The factor 1e-6 converts cm^3/s to m^3/s. VF corresponds to C=0. The
[Badnell definition][badnell-rr] explicitly includes the temperature-dependent
replacement for low-charge ions. Differentiation gives

    b_dot = d b/d ln T = C exp(-T2/T) T2/T
    D = -1/2 - (1-b)u/[2(1+u)] - (1+b)v/[2(1+v)]
        + b_dot [ln(1+u)-ln(1+v)].

The final term arises from differentiating the exponents, not from the square
roots. A VF-specific derivative with B merely replaced by b(T) omits it.
At 100–10000 K the selected Li correction is exponentially small, so those
temperatures alone would not expose that implementation mistake. A separate
1e6 K formula control, within the donor's allowed component temperature range,
is therefore included. It is not an extra high-temperature cosmological case.
The same five-point derivative criterion is applied to the correct expression
and to an intentionally incomplete expression, giving a useful negative control.

Both Li alpha and lambda ratios are reported. Combining donor Badnell alpha
with the recovered VF lambda, or attaching a VF-derived mean energy to a
different alpha without saying so, would introduce an unrecorded hybrid model.
The permitted binding is `(source row, alpha, D, lambda, applicability)` as
one package, with isotope endpoints added explicitly.

## 4. Translational cooling, ionic binding and photons

For an RR edge `i -> f` with threshold difference
`chi=I_i-I_f > 0`, number events per baryon per second are

    R_RR = n_e,thermal * alpha(T) * Y_i.

Within the conditional heavy-target model, its thermal kinetic source is

    dot e_th,RR = -n_e,thermal * Y_i * lambda(T).

If the emitted cascade reaches the recorded ionic ground state and all its
energy is assigned to the photon reservoir, the other ledger entries are

    dot e_ion,RR = -chi * R_RR
    dot e_gamma,RR = chi * R_RR + n_e,thermal * Y_i * lambda(T).

Their sum is zero for the atomic event under the neutral-atom rest reference.
Metastable/excited storage, photon escape versus reabsorption, and a spectrum
would need additional inputs. The moment identity supplies none of those
branching or transport data. Multiplication by n_B converts these per-baryon
sources to J m^-3 s^-1.

The actual donor returns `Gne=Grr+Gdr`. A new RR energy term must bind to
`rr_m3_s`/`Grr`, not to their RR+DR sum. The [Badnell DR definition][badnell-dr]
uses `T^(-3/2) sum c_i exp(-E_i/T)` with E_i in kelvin here. The actual rows
contain signed amplitudes: an individual term is not a physical branching
probability. This C2 unit maps DR number rows and their units; it does not
admit a DR energy spectrum or a newly validated DR cooling provider.

For photoionization the actual finite-quadrature identity is

    absorbed_power_per_ion
      = chi * photo_rate + primary_kinetic_power + unresolved_core_power.

At 200 eV the Li I 1s contribution stores the core-excitation difference
separately. Assigning *all* absorbed energy or *all* threshold-subtracted energy
to immediate heat would discard that distinction. At a 60 eV external cutoff,
Li 1s and Li II/III photoionization have no support. This describes only that
specified external spectrum; it does not remove nuclear-produced hard photons.
The C2 check establishes internal equality of this saved quadrature model,
not convergence of its continuum integrals.

## 5. Exact beta separation at the reusable API

For all-thermal charge neutrality, `n_e=n_B q.Y`. The donor provides independent
matrices G0, Grr, Gdr and D. Define

    Gne = Grr+Gdr
    F_atom = (G0+n_e Gne)Y
    J_atom = G0+n_e Gne+n_B outer(Gne Y,q).

The donor's old `evaluate()` instead returns `F_atom+D.Y` and `J_atom+D`.
Therefore the new coupled operator can call `rates()` and leave D unused.
No modification of the old model JSON or completed evidence is necessary.
The C2 manufactured state includes nonzero n/T so the equality and the
duplicate-D negative control exercise the relevant boundary.

The sole conditional decay constants in the new coupled assembly remain the
evaluated nuclear input of C1. The old atomic T half-life and its matrix are
kept as historical source facts. A charge-resolved beta event must still name
its daughter branch. The electron source is q.dotY; it is not an extra
unconditional `+one electron` appended to an already charge-balanced event.
For a thermal/fast split, use the declared n_e,thermal in recombination and
differentiate its actual dependence when forming the new Jacobian.

## 6. The smallest next executable construction

The 21-state local source interface can accept a supplied branch-event list
without inventing missing nuclear physics. Each event record needs its
reactant and product charge slots, rate and units, provider/applicability, and
signed per-event energy allocation. It then forms

    dotY = F_atom + sum_j nu_j R_j
    dotY_e,total = q.dotY
    dotY_N = 1.dotY
    dotC_thermal = (1+q).dotY       [all-thermal limit only].

The existing nuclear history offers a read-only event-replay input for the old
passive-background calculation. Its saved flux is F(Y_old,T_old,n_B,old), not
a rate coefficient valid for arbitrary Y. Its saved log k can be reused at
the same sampled T under the same provider assumptions; off-grid behavior
requires C3's interpolation/numerical design. Structural support zero, absent
reverse channel, zero initial population and floating underflow are separate
statuses even if an array uses negative infinity for several of them.

The outer solver alone applies `dotY/(scale*H)` to obtain the scaled derivative
with respect to x. The old fixed isotope quotient sets n/T to zero and cannot
carry a positive injection into those slots. A new representation must retain
absolute zero-inventory states and resolve the saved tiny positive T/n stocks.
This is the direct C2 PASS -> C3 action. It does not require waiting for a
complete radiation/thermal closure to begin conditional numerical work.

[vf-table]: https://www.pa.uky.edu/~verner/dima/rec/table.txt
[vf-rr]: https://www.pa.uky.edu/~verner/rec.html
[badnell-rr]: https://amdpp.phys.strath.ac.uk/tamoc/RR/
[badnell-dr]: https://amdpp.phys.strath.ac.uk/tamoc/DR/
[rr-energy]: https://arxiv.org/abs/1612.01017
