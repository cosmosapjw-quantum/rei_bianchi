# Finite moving-gas source construction

Unit: HERE_RUX03_MOVING_GAS_SOURCE_05. THEORY R3–R7. Date: 2026-10-13 KST.

This is the author derivation of M01, M02, M04, M05 and M07. The global
constitutive inverse and explicit absorption families are proved in
[PRIMITIVE_RECOVERY_AND_EXAMPLES.md](PRIMITIVE_RECOVERY_AND_EXAMPLES.md).
The adopted input and claim scope are in
[SCIENTIFIC_CONTRACT.md](../dossier/SCIENTIFIC_CONTRACT.md). The independent
review is a separate artifact. Equations below use physical energy unless
an energy is explicitly in eV.

## 1. State, time and energy ownership

Fix a local orthonormal Eulerian tetrad with future unit normal \(n^a\),
signature \((-+++)\), coordinate \(x^0=ct\), and fixed Eulerian spatial
volume. During the homogeneous source substep all spatial derivatives in
this tetrad vanish and photon lab energies and directions are held fixed.
Geometry and spatial transport are handled in their inherited substeps.
The common gas has

\[
u^a=\gamma(n^a+\beta^a),\quad
n_a\beta^a=0,\quad \gamma=(1-|\boldsymbol\beta|^2)^{-1/2},\quad U^a=cu^a.
\tag{S1}
\]

Conservation of H nuclei, \(\nabla_a(cn_Hu^a)=0\), reduces to
\(\partial_t(\gamma n_H)=0\). Thus

\[
D=\gamma n_H>0
\tag{S2}
\]

is fixed through the source substep. It is a number density in the chosen
Eulerian volume. The gas proper density changes as its velocity changes.
Let \(f=n_{\rm He}/n_H\) and use the three independent composition variables

\[
\zeta=(x,fa,fb),\quad e=\zeta_1+\zeta_2+2\zeta_3,\quad d=1+f+e,
\quad B=\chi_0\zeta_1+\chi_1\zeta_2+(\chi_1+\chi_2)\zeta_3.
\tag{S3}
\]

Here \(B,w\) have units eV per H. Write \(\epsilon=\epsilon_{\rm eV}\),
\(\theta=\epsilon w\), \(\kappa=2/3\), \(\Gamma=5/3\), and adopt

\[
r=m_{\rm ref}c^2+\epsilon B>0,\quad
\rho=n_H(r+\theta),\quad p=\kappa n_H\theta,\quad
T={2\epsilon w\over3k_Bd}.
\tag{S4}
\]

The fixed neutral reference mass includes the bound electrons. Ionization
changes \(B\); electron rest mass is not counted again. The gas stress and
its Eulerian energy current are

\[
T_g^{ab}=(\rho+p)u^au^b+pg^{ab},\qquad
\mathcal C^a=-T_g^{ab}n_b=En^a+M^a,
\tag{S5}
\]
\[
E=(\rho+p)\gamma^2-p,\qquad
\mathbf M=(\rho+p)\gamma^2\boldsymbol\beta.
\tag{S6}
\]

\(\mathbf M\) is \(c\) times physical momentum density, so \(E,p,M_i\)
share energy-density units. \(\mathcal C\) is defined with the fixed normal
\(n\); changing the foliation changes that contraction. The finite scheme
below is a scheme on this specified time foliation.

## 2. Doppler map and event normalization — M01

For a directional photon node define

\[
k_q^a=n^a+e_q^a,\quad e_q^2=1,\ n\cdot e_q=0,\quad
p_q^a={\epsilon E_q\over c}k_q^a,
\quad \epsilon E_q=\hbar\omega_q.
\tag{S7}
\]

The Eulerian number density \(N_q\) includes the node's spectral and angular
weights. Its number current is \(j_q^a=cN_q k_q^a\). Direct contraction gives

\[
\boxed{\delta_q=-u\cdot k_q=\gamma(1-\boldsymbol\beta\cdot\mathbf e_q)>0,
\quad E'_q=\delta_q E_q,\quad N'_q=\delta_q N_q.}
\tag{S8}
\]

The gas-frame direction is \(e_q^{\prime a}=k_q^a/\delta_q-u^a\).
It satisfies \(u\cdot e'_q=0\), \((e'_q)^2=1\), and
\(p_q^a=(\epsilon E'_q/c)(u^a+e_q^{\prime a})\). These identities follow
from \(k_q^2=0\), \(u^2=-1\), \(u\cdot k_q=-\delta_q\), and were also
canonicalized with actual xTensor/xPerm.

For an absorber with proper density \(n_i'=n_Hy_i=D y_i/\gamma\), the gas
provider supplies \(\sigma_i(E'_q)\). Its proper event rate is

\[
R'_{iq}=c n'_i\sigma_i(E'_q)N'_q=\lambda_{iq}N_q,
\quad
\boxed{\lambda_{iq}=cD y_i(1-\boldsymbol\beta\cdot\mathbf e_q)
\sigma_i(\delta_qE_q).}
\tag{S9}
\]

Equivalently \(\lambda=c n'_i\sigma_i(E'_q)\delta_q\). The extra angular
factor is essential even after evaluating the cross section at shifted
energy. The three photoabsorber abundances per H are
\(y_{\rm HI}=1-x\), \(y_{\rm HeI}=f-\zeta_2-\zeta_3\),
\(y_{\rm HeII}=\zeta_2\).

An event count in a small four-volume is
\(d\mathcal N=R'\,dV'\,dt'=R'\,dV\,dt\), since the product of spatial
volume and time is the invariant four-volume divided by \(c\). Thus the
lab event count per lab volume over the endpoint step is \(hR'\).
The species continuity equation independently gives
\(\partial_t(D\zeta)=\sum_c\nu_c R'_c\). In per-H proper-clock units
\(G^{(H)}=\sum_c\nu_cR'_c/n_H\), this becomes
\(\partial_t\zeta=G^{(H)}/\gamma\). These are two equivalent
normalizations of the same events.

This agrees with the invariant opacity \(\nu\alpha_\nu\) in Younsi,
Wu and Fuerst (2012), eqs. (9)–(17): in the present convention
\(\alpha_{\rm lab}=\delta\alpha'\). The project's per-H normalization
is the current derivation applying that invariant to its H/He event ledger.

## 3. One common endpoint for every channel — M02

Let \(h=\Delta t\ge0\). All densities, fractions, velocities, cross sections,
CI/RR/DR rates, and thermal/escape rates on a right-hand side below use one
candidate endpoint \(X_+=(\zeta_+,w_+,\boldsymbol\beta_+)\). Let \(S_q\ge0\)
be the externally specified photon source in lab number density per lab time.
Define

\[
\Lambda_q(X_+)=\sum_i\lambda_{iq}(X_+),\qquad
\boxed{N_q^+={N_q^-+hS_q\over1+h\Lambda_q(X_+)}},\qquad
A_{iq}=h\lambda_{iq}(X_+)N_q^+.
\tag{S10}
\]

The photon equation is exactly
\(N_q^+-N_q^-=hS_q-\sum_iA_{iq}\). Its solution is unique and nonnegative
for every physical candidate, every \(h\ge0\), and nonnegative initial data
and source. It removes all photon nodes from the nonlinear unknown list.
It also implies \(\sum_i A_{iq}\le N_q^-+hS_q\).

For each non-photo channel \(c\), let \(A_c=hR'_c(X_+)\), with the inherited
CI, RR and two DR channels and their proper-volume rate normalization.
The species equations are

\[
\boxed{D(\zeta_+-\zeta_-)=\sum_c\nu_c A_c.}
\tag{S11}
\]

HI ionization has \(\nu=(1,0,0)\), HeI ionization \((0,1,0)\), and
HeII ionization \((0,-1,1)\); recombination has the reverse stoichiometry.
These stoichiometries preserve the nuclei totals. Their positive source
and sink rates are taken from the adopted atomic model.

Let \(Q'_{\rm esc}\) be physical escaped energy per proper volume per proper
time: inherited RR/DR binding plus captured-kinetic radiation. Case A escape
is comoving-isotropic. Set \(L=hQ'_{\rm esc}(X_+)\). Its Eulerian energy and
scaled momentum increments are \(\gamma_+L\) and
\(\gamma_+L\boldsymbol\beta_+\). The gas equations are

\[
\boxed{E_+-E_-=
\sum_{iq}\epsilon E_q A_{iq}-\gamma_+L,}
\tag{S12}
\]
\[
\boxed{\mathbf M_+-\mathbf M_-=
\sum_{iq}\epsilon E_q A_{iq}\mathbf e_q
-\gamma_+L\boldsymbol\beta_+.}
\tag{S13}
\]

Collision ionization is internal redistribution in the gas's total energy;
the changed binding energy is already in \(r(\zeta_+)\). RR/DR leave through
the specified escape current. Primary absorption deposits the full incoming
lab photon energy and momentum. This is the same covariant event ownership
as THEORY04, now placed at a common finite endpoint.

Accumulating the escape current and using (S10) yields the exact identities

\[
\boxed{\Delta\left(E+\sum_q\epsilon E_qN_q+E_{\rm esc}\right)
=h\sum_q\epsilon E_qS_q,}
\tag{S14}
\]
\[
\boxed{\Delta\left(\mathbf M+\sum_q\epsilon E_qN_q\mathbf e_q
+\mathbf M_{\rm esc}\right)
=h\sum_q\epsilon E_qS_q\mathbf e_q.}
\tag{S15}
\]

The proof is termwise cancellation of the same \(A_{iq}\) and escape
increments. No cancellation between unrelated estimates is required.
Sądowski et al. (2013), eqs. (54)–(56), give the established conservative
implicit matter/radiation source structure. The present construction supplies
the specific H/He event normalization, photon elimination and thermal
projection needed by this project.

## 4. Primitive recovery and the seven-dimensional residual — M03/M05

At a candidate composition, let \(a_r=Dr>0\), \(s=|\mathbf M|^2\).
The constitutive inverse reduces to

\[
E=\mathscr E(C)={3C^2+2a_r C+5s\over5\sqrt{C^2+s}},\quad C\ge a_r,
\qquad \mathscr E'(C)={3C^3+Cs+2a_rs\over5(C^2+s)^{3/2}}>0.
\tag{S16}
\]

It maps \([a_r,\infty)\) onto \([\sqrt{a_r^2+s},\infty)\). Consequently
\(E>\sqrt{(Dr)^2+|\mathbf M|^2}\) is necessary and sufficient for the unique
positive thermal primitive of the gamma-law EOS at fixed composition.
Set \(W=\sqrt{C^2+s}\); then

\[
\gamma=W/C,\quad \boldsymbol\beta=\mathbf M/W,\quad
n_H=DC/W,\quad w={3(C-a_r)\over5D\epsilon},\quad
p={2C(C-a_r)\over5W}.
\tag{S17}
\]

The companion proof supplies stable positive-term evaluation, a finite
bracket and the exact warm-temperature subdomain. This is a specialized
rederivation of the standard gamma-law admissibility result in Wu and Tang
(2015), Lemma 2.1, with their mass-energy density mapped to \(Dr\).

Smoothness also holds at \(\mathbf M=0\): use \(s=\mathbf M\cdot\mathbf M\)
in the scalar implicit function and (S17), which contains no division by
\(|\mathbf M|\). For an independent differential check, put
\(\alpha=\Gamma/\kappa=5/2\), \(W=a_r\gamma+\alpha p\gamma^2\).
In coordinates \((p,\beta_1,\beta_2,\beta_3)\), direct differentiation gives

\[
\det{\partial(E,\mathbf M)\over\partial(p,\boldsymbol\beta)}
=W^2\left[a_r(\alpha-1)\gamma^3+
\alpha p\{(\alpha-2)\gamma^4+\gamma^2\}\right]>0.
\tag{S18}
\]

The first term is strictly positive. The change to \(w\) multiplies the
determinant by \(\partial p/\partial w|_\beta=\kappa D\epsilon/\gamma>0\).

Use conservative/composition variables \(Y=(\zeta,E,\mathbf M)\), seven
components, and eliminate photons by (S10). Primitive recovery is a smooth
map \(\Phi(Y)\). Dividing (S11) by \(D\), equations (S11)–(S13) become

\[
F(Y,h)=Y-Y_- -h\mathcal S_h(Y)=0.
\tag{S19}
\]

Here the right-hand side is explicitly the inherited proper atomic rates
and the lab energy/momentum rates of (S12)–(S13), evaluated at \(\Phi(Y)\)
and \(N_h(Y)\). At \(h=0\), \(F(Y_-,0)=0\) and \(D_YF(Y_-,0)=I\).

**Local physical-branch theorem.** Suppose the initial state is in the
strict H/He simplex, has \(D,r>0\), satisfies the strict primitive cone and
the strict warm domain \(30000<T<110000\) K. Require a neighborhood in which
the adopted rates and the specified source are \(C^1\), with every active
gas-frame photon energy inside \(0<E'_q<50000\) eV and away from the
provider's piecewise cutoffs. Then there is \(h_0>0\) and a unique local
\(C^1\) solution branch through \(Y_-\) for \(0\le h<h_0\). It stays in
those physical domains; its photons are nonnegative; and (S14)–(S15) hold.

**Proof.** Equations (S16)–(S18) give a smooth primitive inverse; (S10) has
a nonzero denominator in a neighborhood of \(h=0\). The assumed rate
regularity makes \(F\) continuously differentiable. The identity Jacobian
at \(h=0\) is invertible, so the implicit function theorem gives the unique
local branch. Openness and continuity preserve every strict state-domain
condition after decreasing \(h_0\). Photon positivity follows separately
from (S10). Finite conservation follows from the exact residual equations.

**Constructive sufficient step bound.** Fix positive scales for the seven
coordinates and use the associated dimensionless norm. Choose a closed
convex ball \(\mathcal B_r(Y_-)\) lying in the smooth physical domain. On
\(\mathcal B_r\times[0,\bar h]\), define finite bounds

\[
M_0=\sup\|\mathcal S_h(Y)\|,\qquad
L_0=\sup\|D_Y\mathcal S_h(Y)\|.
\tag{S20}
\]

Whenever \(0\le h\le\bar h\), \(hM_0\le r\), and \(hL_0<1\), the map
\(T_h(Y)=Y_-+h\mathcal S_h(Y)\) maps the ball into itself and is a
contraction. Iteration \(Y_{k+1}=T_h(Y_k)\), \(Y_0=Y_-\), constructs its
unique endpoint, with

\[
\|Y_k-Y_*\|\le{(hL_0)^k\over1-hL_0}\|Y_1-Y_0\|.
\tag{S21}
\]

This follows from the mean-value bound and the geometric tail of the
successive increments. It gives a concrete sufficient criterion in terms
of the supplied rates on a chosen compact domain. Numerical values of
\(M_0,L_0\), a production solver and large-step continuation are coding or
subsequent continuation obligations; they were not executed in this unit.

## 5. Exact finite thermal correction — M04

The gas projection at one state satisfies

\[
E-\boldsymbol\beta\cdot\mathbf M=\rho,\qquad
-u\cdot\mathcal C=\gamma\rho.
\tag{S22}
\]

Use the **endpoint** gas velocity to project the finite difference in the
Eulerian energy current. Introduce the relative Lorentz factor

\[
\gamma_{\rm rel}=-u_+\cdot u_-
=\gamma_+\gamma_-(1-\boldsymbol\beta_+\cdot\boldsymbol\beta_-).
\tag{S23}
\]

The old current's projection is

\[
-u_+\cdot\mathcal C_-
=\gamma_-(\rho_-+p_-)\gamma_{\rm rel}-\gamma_+p_-.
\tag{S24}
\]

Projecting (S12)–(S13) therefore gives

\[
\gamma_+\rho_+-\gamma_-(\rho_-+p_-)\gamma_{\rm rel}+\gamma_+p_-
=\sum_{iq}\epsilon E'_{q,+}A_{iq}-L.
\tag{S25}
\]

An absorbed photon contributes its endpoint rest-frame energy because
\(-u_+\cdot k_q=\delta_{q,+}\); endpoint-isotropic escape contributes
exactly \(L\), since \(-u_+^2=1\). Both contractions were checked in xAct.

Insert (S2) and (S4) into (S25). The left side becomes
\(D\epsilon(\Delta w+\Delta B)-\mathcal K_\gamma\), where

\[
\boxed{\mathcal K_\gamma=D\left[
(r_-+\Gamma\epsilon w_-)(\gamma_{\rm rel}-1)
-\kappa\epsilon w_-\left({\gamma_+\over\gamma_-}-1\right)\right].}
\tag{S26}
\]

The inherited chemical event identity, evaluated at this same endpoint
and multiplied by \(h\), is

\[
D\epsilon\Delta B+hQ'_{\rm esc}+hQ'_{\rm th}
=\sum_{iq}\epsilon E'_{q,+}A_{iq},\qquad
Q'_{\rm th}=n_{H,+}\epsilon Q_{\rm th}^{(H)}.
\tag{S27}
\]

The first equality uses (S11) and the binding coefficients in (S3). It
includes photo excess energy, CI binding transfer, and inherited RR/DR
escape and captured kinetic loss. Subtracting it from (S25) yields

\[
\boxed{w_+-w_-={h\over\gamma_+}Q_{\rm th}^{(H)}(X_+,N'_+)
+{\mathcal K_\gamma\over D\epsilon}.}
\tag{S28}
\]

This is the finite thermal equation equivalent to the common conservative
stage. It supplies the velocity correction that must accompany the scalar
H/He thermal provider. Every binding or kinetic term appears once.

### 5.1 Continuous limit and pressure work

On a smooth trajectory with \(\boldsymbol\beta_+-\boldsymbol\beta_-=O(h)\),
normalization of \(u\) gives \(\gamma_{\rm rel}-1=O(h^2)\). Hence

\[
{\mathcal K_\gamma\over D\epsilon}
=-\kappa w_-\Delta\log\gamma+O(h^2).
\tag{S29}
\]

The fixed-volume homogeneous kinematics give
\(\Theta=c\nabla_a u^a=\partial_t\gamma\) and the gas-clock derivative
\(\dot w=cu^a\nabla_aw=\gamma\partial_tw\). Dividing (S28) by \(h\)
and taking its smooth limit gives

\[
\partial_tw={Q_{\rm th}^{(H)}\over\gamma}
-\kappa w\partial_t\log\gamma,
\qquad
\dot w=Q_{\rm th}^{(H)}-\kappa\Theta w.
\tag{S30}
\]

This is precisely the accepted covariant thermal law. Its pressure work
occurs even though the fixed Eulerian spatial volume is constant, because
\(n_H=D/\gamma\) changes.

There is a related kinematic detail: for an Eulerian-homogeneous pressure
\(p(t)\), the rest-space pressure gradient is
\(D_u^ap=(\partial_tp/c)(\gamma u^a-n^a)\). It can be nonzero when the
gas moves. Thus comoving-isotropic heating by itself does not imply a
constant lab velocity in this source split. Actual xAct checks verify
this projected gradient, the gas clock and the expansion identity.

## 6. Nonempty constructions and the rest-paired limit — M06

For initially resting gas and lab nodes in equal opposite pairs with equal
energies, number densities and sources, \(\boldsymbol\beta_+=0\) makes the
paired absorption momentum cancel. Escape momentum also vanishes.
The residual is invariant under reflection of the gas velocity and the
paired nodes. The unique local branch from §4 consequently has
\(\boldsymbol\beta_+=0\), \(\gamma_+=\gamma_-=\gamma_{\rm rel}=1\),
\(\mathcal K_\gamma=0\), and \(n_H=D\). Equations (S10), (S11) and (S28)
reduce to the inherited scalar source stage with geometry held fixed.

The companion derivation constructs an explicit, positive, warm HI-only
23 eV absorption family for one beam and for an opposite pair. It supplies
finite event counts, changed binding, photon initial data, and a positive
step chosen to satisfy (S10) exactly. The one-beam family has nonzero recoil;
its gas endpoint is verified against the full energy/momentum EOS. The
reference temperature starts at 50000 K and remains in the adopted warm
interval for the proved small positive parameter range. These are
channel-isolated analytical fixtures. The full retained CI/RR/DR/photo
model has the local branch proved in §4, rather than an assumed cancellation
of its nonzero collisional or recombination rates in those fixtures.

## 7. Angular and source adapters — M07

For a full directional node set, use (S8)–(S10) for arbitrary gas velocity.
For an inherited azimuth-averaged ring with direction
\(\mathbf e(\phi)\) and \(\mu=e_z\), an axial velocity gives
\(\delta=\gamma(1-\beta_z\mu)\), independent of \(\phi\). The existing
ring weights and first/second angular moments can then be retained.

For transverse velocity, \(\delta(\phi)\) varies within the ring. The exact
construction is a positive resolved azimuth quadrature or the integral
of the pointwise update

\[
N_+(\phi)={N_-(\phi)+hS(\phi)\over1+h\Lambda(X_+,\phi)}.
\tag{S31}
\]

The resulting endpoint generally has azimuth dependence. Evaluate cross
sections at each actual Doppler energy before integration. A cross section
at an averaged direction need not equal the average cross section, and the
finite denominator in (S31) is also nonlinear. Geometry, source birth and
angular moments retain their own measure/ownership adapters.

The current receiver stores \(N_{\rm ref}=a_{\rm rel}^3n_\gamma\) and has no
gas velocity or conservative gas energy/momentum. The coding contract must
therefore provide an explicit fixed-volume conversion, a gas-primitive
adapter and lab-normalized source. It must evaluate the energy guard
\(0\le E'_q\le50000\) eV **after** Doppler transformation. The existing
atomic fit cutoffs (13.60, 24.59, 54.42 eV) and the distinct adopted binding
energies remain separate inputs.

## 8. Evidence and remaining mathematical obligation

The scalar inverse, local-branch proof, finite balances and thermal
projection are direct arguments in this unit. Actual Wolfram algebra and
xAct tensor calculations check their vulnerable transitions; the execution
record preserves exact inputs and all observed failures/corrections.
The independent decision determines adoption after reviewing those files.

The next theoretical obligation is a quantitative continuation/admissibility
certificate for the full rate-dependent finite stage up to the adopted warm
and energy-domain boundaries. Its concrete first task is to bound
\(M_0,L_0\) and/or the residual Jacobian on a specified physical box, then
identify whether the continued branch reaches a domain boundary or loses
invertibility. The present unit establishes a constructive local endpoint
and a global constitutive inverse at each fixed composition. It does not
use an unproved global source-stage assertion.

## Primary sources

1. Z. Younsi, K. Wu, S. Fuerst, *General relativistic radiative transfer:
   formulation and emission from structured tori around black holes* (2012),
   [arXiv:1207.4234](https://arxiv.org/abs/1207.4234), eqs. (9)–(17).
2. A. Sądowski et al., *Semi-implicit scheme for treating radiation under M1
   closure in general relativistic conservative fluid dynamics codes* (2013),
   [arXiv:1212.5050](https://arxiv.org/abs/1212.5050),
   §3.3–3.4, eqs. (54)–(56).
3. K. Wu, H. Tang, *High-order accurate physical-constraints-preserving
   finite difference WENO schemes for special relativistic hydrodynamics*
   (2015), [arXiv:1504.07707](https://arxiv.org/abs/1504.07707), Lemma 2.1.

Precise readings, source locations, scope mapping and search accounting are
in [LITERATURE_MAP.md](../review/LITERATURE_MAP.md). The established
conservative-source and primitive-admissibility structures are credited
there; the project-specific construction is (S8)–(S31) with the retained
H/He event/provider ownership.
