# Covariant H/He event exchange and the gas equations

This note proves C01, C02, C06 and C07 under SCIENTIFIC_CONTRACT.md. C03–C05
are developed in the companion radiation/geometry note. All powers below are
physical powers until a per-H normalization is explicitly introduced.

## 1. Conventions and dimensional map

Take `g_ab` of signature `(-+++)` and a common future unit gas velocity

\[
u^a u_a=-1,\qquad U^a=c u^a,\qquad h^a{}_b=\delta^a{}_b+u^a u_b.
\tag{1}
\]

Coordinates have length units, including `x^0=c t`. Write

\[
\dot X=c u^a\nabla_aX,\quad D_a X=h_a{}^b\nabla_bX,\quad
\Theta=c\nabla_a u^a,\quad a^b=c^2u^a\nabla_a u^b.
\tag{2}
\]

For a tensor divergence `G^b=∇_a T^{ab}`, define the gas-frame power and force

\[
\mathcal Q(G)=-c u_bG^b,\qquad f^a(G)=h^a{}_bG^b,\qquad
G^a={\mathcal Q(G)\over c}u^a+f^a(G).
\tag{3}
\]

`rho,p,pi` have units erg cm^-3; physical energy flux `q` has units
erg cm^-2 s^-1; `G,f` have units erg cm^-4 = dyn cm^-3;
`Q` has units erg cm^-3 s^-1. The powers in the retained per-H event ledger
have units eV H^-1 s^-1. Denote the conversion by `epsilon_eV` in erg/eV.
Photon energy is

\[
\mathcal E_q=\epsilon_{\rm eV}E_q=\hbar\omega_q,
\qquad p_q^a={\mathcal E_q\over c}(u^a+e_q^a),
\quad u\cdot e_q=0,\quad e_q\cdot e_q=1.
\tag{4}
\]

Thus `p_q.p_q=0` and `-c u.p_q=mathcal E_q`. No natural-unit replacement of
`c`, `hbar` or `k_B` is made. The frequency in (4) is angular frequency.

## 2. Absorption: a constructive four-force

For species channel `i` and node `q`, let `R_iq >= 0` be the absorption event
rate per proper volume per proper time. In the adopted isotropic absorber model,

\[
\mathcal R_{iq}=c n_i\sigma_i(E_q)n_q
=n_H\mathcal P_{iq},\qquad
\kappa_q=\sum_i n_i\sigma_i(E_q),
\tag{5}
\]

where `n_q` is the angular/spectral-bin integrated proper photon number density
and `mathcal P_iq` is the previous per-H event rate. Node weights are already
included in `n_q`; they are not applied a second time.

Add the absorbed photon momenta themselves:

\[
\boxed{\mathcal A^a=\sum_{iq}{\epsilon_{\rm eV}E_q\over c}
\mathcal R_{iq}(u^a+e_q^a).}
\tag{6}
\]

This is a nonnegative sum of future null momenta per proper spacetime volume.
Its two projections are

\[
\mathcal Q_{\rm abs}=\sum_{iq}\epsilon_{\rm eV}E_q\mathcal R_{iq},
\qquad
f_{\rm abs}^a={1\over c}\sum_{iq}
\epsilon_{\rm eV}E_q\mathcal R_{iq}e_q^a.
\tag{7}
\]

The `E_q-chi_i` part is thermal photoheating, while the remaining `chi_i`
changes atomic binding/rest energy. **The entire `E_q/c` is the absorbed photon
momentum.** Replacing it by `(E_q-chi_i)/c` would omit momentum from the same
absorption event. This is also the momentum structure of the H/He absorption
term in Rosdahl–Teyssier (2015), §2.3.3 Eq. (27).

The covariant construction in (6) follows the general absorption/emission
four-force of Farris et al. (2008), Eq. (30), without adopting its later
grey/Kirchhoff or Eddington assumptions. The present application retains the
given non-LTE atomic rates and energy moments.

**Direction-resolved beam versus the current ring node.** Equations (4)–(7)
use an actual directional ordinate with a unit `e_q`. The current axisymmetric
`mu` node represents an azimuth-averaged ring. For that node the first moment
uses `〈e〉_phi=mu e_z`, while the second moment uses
`〈e^i e^j〉_phi=diag((1-mu^2)/2,(1-mu^2)/2,mu^2)`. Its contribution to (6)
is the azimuth average `(mathcal E_q R_iq/c)(u+mu e_z)`. It is a positive
average of null-photon momenta; the average vector itself is timelike when
`|mu|<1` and nonzero. The unit-direction/null test applies before this average.
The same integrated node count supplies both moments, with no extra angular
weight or `2 pi` factor.

## 3. Case A escape: an explicit positive emission-moment realization

Let the adopted scalar escape power be `mathcal Q_esc >= 0`. Assume its
emissivity is isotropic in the common gas frame. Then its outgoing momentum
source is

\[
\boxed{\mathcal L^a={\mathcal Q_{\rm esc}\over c}u^a,}
\qquad \mathcal Q(\mathcal L)=\mathcal Q_{\rm esc},
\quad h^a{}_b\mathcal L^b=0.
\tag{8}
\]

An explicit realization shows that this is a nonempty closure. Choose any
energy `E_*>0` and six directions `+/- e_1,+/- e_2,+/- e_3` of an orthonormal
gas-rest triad. Emit photons into each direction at the nonnegative rate

\[
\mathcal R^{\rm em}_j={\mathcal Q_{\rm esc}\over
6\epsilon_{\rm eV}E_*}.
\tag{9}
\]

Summing their four-momenta gives (8), and their second angular emission moment
is isotropic. A fully angular-isotropic continuum realization replaces these
six directions by a uniform solid-angle distribution. More generally any
nonnegative spectrum with the same first energy moment realizes (8).
`Q_esc=0` uses zero emissivity and requires no division by that power.

Equation (9) constructs the required emission moments; `E_*` is an arbitrary
realization parameter, not a reconstructed H/He recombination spectrum. The
previous provider supplies RR/DR binding plus captured kinetic power.
Cooling here means those captured-kinetic losses; no extra radiative channel is
introduced. Their scalar sum does not determine a
spectrum or a subsequently propagated escape stress tensor.

If an anisotropic emissivity is supplied later, write instead

\[
\mathcal L^a=(\mathcal Q_{\rm esc}/c)u^a+\ell_{\rm esc}^a,
\quad u_a\ell_{\rm esc}^a=0.
\tag{10}
\]

For a nonnegative photon emissivity, `|ell_esc| <= Q_esc/c`. The present
isotropic closure sets `ell_esc=0`. Isotropic recombination emission having
zero flux-source moment is the corresponding assumption in Rosdahl et al.
(2013), Appendix A Eqs. (A6)–(A8).

## 4. Total local exchange and its energy projection

Let `S^a` denote prescribed external primary-photon injection. Define

\[
G_g^a=\mathcal A^a-\mathcal L^a,\qquad
G_{\gamma,p}^a=-\mathcal A^a+\mathcal S^a,\qquad
G_{\rm esc}^a=\mathcal L^a.
\tag{11}
\]

The local transfer identity is exactly

\[
G_g^a+G_{\gamma,p}^a+G_{\rm esc}^a=\mathcal S^a.
\tag{12}
\]

If the three sectors are transported, their stress divergences take the
corresponding sources (11). The current receiver transports only the selected
primary/gas scalar moments and a cumulative escape-energy counter. Equation
(12) therefore supplies the covariant exchange contract, not an assertion that
an escape transport state is already present.

For the gas under isotropic escape,

\[
\mathcal Q_g=\mathcal Q_{\rm abs}-\mathcal Q_{\rm esc},
\qquad f_g^a=f_{\rm abs}^a.
\tag{13}
\]

CI rearranges energy inside the common gas sector. RR/DR binding and their
captured-kinetic losses contribute to `Q_esc`; the previously adopted event
identity accounts for those transfers and is reused below. In its per-H units,
the fixed provider uses

\[
Q_{\rm esc}^{(H)}=\sum_i(\chi_i\mathcal R_i^{(H)}+K_i^{(H)})
+\chi_1\sum_r\mathcal D_r^{(H)}+\sum_r L_r^{(H)}.
\tag{13a}
\]

Here `R_i^(H)` is the RR event rate; `K_i` and `L_r` are the RR and two DR
captured-kinetic powers, respectively. `L_r` is not an extra line/free-free
cooling channel. Chemical constituents need no independent velocity in this
construction.

## 5. Gas binding energy, pressure and scalar-ledger recovery

Use the previous fractions `v=(x,a_HeII,b_HeIII)` and fixed `f=n_He/n_H`.
For readability the fractions below are written simply `x,a,b`:

\[
e=x+f(a+2b),\quad d=1+f+e,\qquad
w={3k_B\over2\epsilon_{\rm eV}}dT,
\tag{14}
\]

\[
B(v)=\chi_0x+f\chi_1a+f(\chi_1+\chi_2)b,
\quad b_\chi=\nabla_vB.
\tag{15}
\]

The retained ionization energies are `(13.598434599702,24.587389011,54.41776)`
eV; the provider cutoffs `(13.60,24.59,54.42)` eV retain their separate role.
They are inherited inputs, not refitted numbers in this unit.

Take `m_ref=m_HI+f m_HeI`, including the neutral atoms' bound electrons, and
define the nonrelativistic ideal-gas constitutive approximation

\[
\rho_g=n_Hm_{\rm ref}c^2+n_H\epsilon_{\rm eV}[w+B(v)],
\quad p_g=n_Hd k_BT={2\over3}n_H\epsilon_{\rm eV}w,
\tag{16}
\]

\[
T_g^{ab}=\rho_g u^au^b+p_g h^{ab}.
\tag{17}
\]

Using a neutral reference mass makes the positive `B` the increase of
composition rest energy upon ionization. Adding free-electron rest masses once
more to (16) would double-count them.

Metric compatibility, `u.u=-1`, and the product rule give

\[
-c u_b\nabla_a T_g^{ab}=\dot\rho_g+\Theta(\rho_g+p_g),
\tag{18}
\]

\[
h^b{}_d\nabla_a T_g^{ad}=
{\rho_g+p_g\over c^2}a^b+D^bp_g.
\tag{19}
\]

Conservation of H nuclei gives `dot n_H=-Theta n_H`. Substitution of (16)
into (18) cancels every advected reference-mass/binding/thermal-density term:

\[
n_H\epsilon_{\rm eV}(\dot w+\dot B)+\Theta p_g
=\mathcal Q_g.
\tag{20}
\]

The previously proved event identity, with all its captured kinetic moments,
is

\[
Q_{\rm th}^{(H)}+b_\chi^T\mathcal G_{\rm chem}
+Q_{\rm esc}^{(H)}=\sum_{iq}E_q\mathcal P_{iq}.
\tag{21}
\]

Here `dot v=mathcal G_chem`, so `dot B=b_chi^T mathcal G_chem`; the superscript
`(H)` means eV per H per proper second. Equations (5), (13), (20), (21) imply

\[
\boxed{\dot w=Q_{\rm th}^{(H)}-{2\over3}\Theta w.}
\tag{22}
\]

For `Theta=3H`, (22) is `dot w=Q_th^(H)-2H w`. For the proper thermal energy
density `u_th=n_H epsilon_eV w`, the corresponding equation is

\[
\dot u_{\rm th}=-5H u_{\rm th}+\mathcal Q_{\rm th},
\qquad \mathcal Q_{\rm th}=n_H\epsilon_{\rm eV}Q_{\rm th}^{(H)}.
\tag{23}
\]

This is the actual `axisym_coupling.rs` gas equation. The previous
`F_E=F_w+b_chi^T F_v` and finite-step scalar cancellation are reused results;
the new result is their explicit common-frame constitutive/projection map.

The tensor algebra in (18)–(20) is exact for (16)–(17). The gas equation of
state and tabulated atomic coefficients retain their nonrelativistic domain;
this construction does not derive recoil-resolved species distributions or
relativistic atomic rate corrections.

## 6. The spatial equation and the fixed-frame condition

The same gas four-force must satisfy

\[
\boxed{{\rho_g+p_g\over c^2}a^a+D^ap_g
=f_{\rm abs}^a-\ell_{\rm esc}^a.}
\tag{24}
\]

In the selected geodesic, homogeneous-pressure, isotropic-escape application,
`a=0`, `D p_g=0`, `ell_esc=0`. Thus the compatible local sources obey

\[
\sum_{iq}\epsilon_{\rm eV}E_q\mathcal R_{iq}e_q^a=0.
\tag{25}
\]

The companion note constructs and preserves a nonempty antipodal/ring-reflection
family satisfying (25), with nonzero anisotropic stress. If a general permitted
node input has a nonzero right-hand side, (24) gives its required acceleration,
or a separately specified support force can balance it. An energy-only check
does not supply that missing spatial balance.

For an exact paired family both directions have the same `E`, density and
opacity at each stage. This is stronger than simply setting the unweighted
radiation energy flux to zero.

### A spectral counterexample to the weaker flux-only condition

Choose two opposite directions with equal positive energy densities
`U_+=U_-=U_0/2`, different photon energies, and effective absorption opacities
`kappa_+ != kappa_-`. All photon counts remain positive. Then

\[
q^a=c(U_+-U_-)e_z^a=0,
\quad
f_{\rm abs}^a={U_0\over2}(\kappa_+-\kappa_-)e_z^a\ne0.
\tag{26}
\]

For example, `kappa_+=2 kappa`, `kappa_-=kappa>0` yields
`f_abs=(kappa U_0/2)e_z`. This is an exact positive-opacity construction,
not a specified numerical ratio of the FT03 cross sections. With any two
actual energies having unequal `sum_i n_i sigma_i(E)`, the first expression
in (26) supplies the same discriminant. Zero energy flux alone cannot replace
the opacity-weighted condition (25).

This is a bounded counterexample to one proposed simplification, not a new
strong no-go theorem about homogeneous anisotropic radiation.

## 7. Exact local observer projection

Let another unit observer be

\[
n^a=\gamma(u^a+\beta v^a),\quad
u\cdot v=0,\quad v\cdot v=1,\quad
\gamma=(1-\beta^2)^{-1/2},\quad |\beta|<1.
\tag{27}
\]

Holding the already constructed four-force fixed, its measured energy source is

\[
\boxed{\mathcal Q_g(n)=-c n_aG_g^a
=\gamma[\mathcal Q_g(u)-c\beta v_af_g^a].}
\tag{28}
\]

For the emission (8), `Q_L(n)=gamma Q_esc`, and its spatial projection is

\[
h(n)^a{}_b\mathcal L^b=
{\mathcal Q_{\rm esc}\over c}(u^a-\gamma n^a).
\tag{29}
\]

Its magnitude is `gamma |beta| Q_esc/c`. It vanishes for the gas observer or
zero power. Thus isotropic *emission in the gas rest frame* is a covariant
source specification, not an assertion of isotropy in every frame.

Equations (28)–(29) are exact Lorentz projections. The existing atomic rates
are still evaluated from gas-frame energy, density and temperature. A later
moving-gas integrator must transform energies/angles and account consistently
for kinetic energy; replacing the rest-frame source by a lab-frame scalar
without this projection is not the contract established here.

## 8. Primary references and reused project proof

1. Farris et al. (2008), [arXiv:0802.3210](https://arxiv.org/pdf/0802.3210),
   Eqs. (19), (20), (30), with their added closure assumptions kept separate.
2. Barrow–Maartens (1999), [astro-ph/9808268](https://arxiv.org/pdf/astro-ph/9808268),
   exact 1+3 equations (11), (12), for the companion projection.
3. Rosdahl–Teyssier (2015), [1411.6440v2](https://arxiv.org/pdf/1411.6440v2),
   §2.3.3 Eq. (27); their first-order mixed-frame scheme is not used as an
   exact Lorentz transformation formula here.
4. Rosdahl et al. (2013), [1304.7126](https://arxiv.org/pdf/1304.7126),
   Appendix A Eqs. (A6)–(A8), (A15), (A16).
5. BASS_HE [PRIMARY_THEORY_03](https://github.com/cosmosapjw-quantum/BASS_HE/tree/be96b0011772b47af4bd3c8e420f73153a745508/research/rux03_primary_theory_20261012),
   `SHARED_RESIDUAL_AND_PROVIDER.md` and `PHOTON_ELIMINATION.md` for (14),
   (15), (21), density/event normalization and the finite-work identity.
