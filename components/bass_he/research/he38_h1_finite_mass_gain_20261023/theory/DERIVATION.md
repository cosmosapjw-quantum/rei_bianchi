# Finite-mass H1 ionization with source-coordinate Jacobi gain

Workflow1.0.0 / approval0.2. This is a constructive independent derivation for the next HE37 unit. Author: `/root/he38_finite_mass_derivation`. Scientific status of the algebra below: **derived within the stated model**. Numerical/exact-arithmetic checks are separately recorded in CHECKS.json. The source-qualified formula/page record is owned by the source-intake agent; this note does not claim empirical angular calibration.

## 1. Definitions, mass convention and model choice

Use a local orthonormal common-bulk rest frame, metric convention (-,+,+,+), proper time, SI masses/pressures/rates, and θ=k_B T. This is Newtonian collision kinematics with an internal ionization defect I>0. The electron kinetic mass is m, the ion mass is M>0, the neutral kinetic mass is h=M+m, and L=h+m=M+2m. Thus translational kinetic masses are additive. The binding correction I/c_light² is carried as internal energy, not inserted as a rest-mass change in this Newtonian model. Relativistic mass-defect corrections and relativistic tails require a different contract; c_light and ħ are not silently set to one.

Define the dimensionless fractions

\[
\eta=m/L,\qquad\zeta=h/L,\qquad c=M/h,\qquad d=m/h,
\]

so η+ζ=c+d=1, d=η/ζ, c=(ζ−η)/ζ, 0<η<1/2 and ζ>1/2. The symbol c in the four-fraction formulas is a **dimensionless mass fraction**, not the speed of light; implementation names must distinguish it, e.g. `ion_fraction_inner`. When referring to the speed of light write c_light explicitly.

For incoming velocities v_e,v_H define

\[
V=(m v_e+h v_H)/L,\quad g_0=v_e-v_H,\quad
v_e=V+\zeta g_0,\quad v_H=V-\eta g_0,
\]

\[
\mu=mh/L=m\zeta,\qquad E=\mu g_0^2/2.
\tag{1}
\]

The adopted candidate retains the Le–Cambier source-coordinate energy transfer Υ. The final Jacobi velocities are g_1 = scattered electron velocity minus the COM velocity of the ejected-electron/ion pair and g_2 = ejected-electron velocity minus ion velocity:

\[
v_1=V+\zeta g_1,\qquad
v_2=V-\eta g_1+c g_2,\qquad
v_p=V-\eta g_1-d g_2.
\tag{2}
\]

With μ_t=mM/h=mc,

\[
\frac{\mu g_1^2}{2}=E-\Upsilon,
\quad\frac{\mu_t g_2^2}{2}=\Upsilon-I,
\quad I\le\Upsilon\le E,\quad E>I.
\tag{3}
\]

The event cross section and transfer probability are specified functions of relative energy E:

\[
\sigma(E)=4\pi a_0^2I(E-I)/E^2,\quad
p(\Upsilon\mid E)=\frac{IE}{(E-I)\Upsilon^2},
\quad K(E)=\sqrt{2E/\mu}\,\sigma(E).
\tag{4}
\]

σ=0 for E≤I. The conditional p is defined only when an event has nonzero support; its threshold limit is a degenerate distribution. Directions of g_1 and g_2 are independent and uniform on S² in this declared finite-mass continuation. These Jacobi directions, not the final laboratory electron directions, are independently isotropic. Momentum conservation correlates the latter at finite M.

The existing event normalization is preserved analytically: the integral of p from I to E is IE/(E−I)(1/I−1/E)=1, and each angular measure is dΩ/(4π). The two source-coordinate electron labels identify roles within one ionization event; the species moment sums both outgoing electrons. No additional event factor of two or one-half is inserted.

The finite-mass kinematics follows exactly from definitions (1)–(3). Applying the selected energy-sharing/cross-section/isotropic-Jacobi law at finite M is an explicit **model assumption**. It is not a fitted H1 differential provider. A different explored pair-electron/ion microcanonical law would yield a different finite-mass species heat split; it is not adopted here.

At a stationary target, E=ζ E_lab. Therefore this relative-energy model has E_lab,threshold=I/ζ. The energy variable cannot be relabeled as laboratory energy at finite mass.

## 2. Event-level conservation

Substitution of (2) gives

\[
m(v_1+v_2)+Mv_p=LV=mv_e+hv_H.
\tag{5}
\]

The g_1·g_2 cross term in total kinetic energy vanishes because mc=Md. Likewise COM-relative cross terms vanish by total momentum. Thus

\[
\frac m2(v_1^2+v_2^2)+\frac M2v_p^2
=\frac L2V^2+\frac\mu2g_1^2+\frac{\mu_t}2g_2^2
=\frac L2V^2+E-I.
\tag{6}
\]

The incoming kinetic energy is LV²/2+E. Hence net kinetic energy is −I **for every event**, in every common Galilean frame, before angular averaging. The internal ionization reservoir receives +I once.

The stoichiometric increments are ΔN_e=+1, ΔN_H=−1, ΔN_p=+1. Translational mass change is m−h+M=0; charge and nuclei also balance. Total thermal particle change equals +1 only if all three species/products are included in the declared thermal inventory.

For completeness the conditional net species momenta, after the stated outgoing angular average but before averaging incoming velocities, are

\[
\langle\Delta p_e\rangle=mV-\mu g_0,\qquad
\langle\Delta p_H\rangle=-hV+\mu g_0,\qquad
\langle\Delta p_p\rangle=MV.
\tag{6a}
\]

Their sum vanishes. The unaveraged increments obtained directly from (2) also sum to zero for every event; the angular average is needed only for the separate-species expressions in (6a).

## 3. Conditional outgoing second moments

Let u(E)=E−barΥ(E), v(E)=barΥ(E)−I, where barΥ is the conditional transfer mean. Angular averaging at fixed V,E eliminates each odd direction and the g_1g_2 cross tensor. Since m/μ=1/ζ and m/μ_t=1/c,

\[
B_e^+=m\langle v_1v_1+v_2v_2\rangle
=2mVV+\frac23[ (1-\eta c)u+c v ]\,\mathbf1,
\tag{7}
\]

\[
B_p^+=M\langle v_pv_p\rangle
=MVV+\frac23[\eta c u+d v]\,\mathbf1.
\tag{8}
\]

Their sum is LVV+(2/3)(E−I)Id. The removed parents give m v_e v_e+h v_H v_H=LVV+μg_0g_0. Thus the angular-averaged total net event pressure tensor is particularly simple:

\[
\boxed{B_{\rm all}^{\rm net}
=\frac23(E-I)\mathbf1-\mu g_0g_0.}
\tag{9}
\]

Its trace is −2I pointwise. The source-specific sharing law affects the species trace allocation in (7)–(8), but not this total tensor or the STF gains generated by COM motion. It also does not determine a nonlinear species-temperature/anisotropy closure.

## 4. Common-temperature Maxwellian reference and Grad first variation

At common temperature T and bulk velocity zero, V and g_0 are independent Gaussians with component variances θ/L and θ/μ. For s=e,H use

\[
f_s=f_{Ms}\left[1+\frac{m_s}{2n_s\theta^2}\pi_s:v_sv_s\right]+O(\pi^2),
\quad\pi_s=\pi_s^T,\quad\operatorname{tr}\pi_s=0.
\tag{10}
\]

This specifies an infinitesimal first variation. It does not require accepting the quadratic polynomial as a positive finite-amplitude PDF. It agrees with the derivative of a positive anisotropic Gaussian family at the isotropic reference.

Write radial averages

\[
\alpha=\langle K\rangle,\quad\beta=\langle EK\rangle,
\quad\gamma=\langle E^2K\rangle,
\quad\kappa_1=\frac{2\beta}{3\theta},\quad
\kappa_2=\frac{4\gamma}{15\theta^2}.
\tag{11}
\]

The rate is r=n_e n_H α. Scalar rate/heat first variations vanish because the angular contraction has tr π_s=0. Species momentum sources vanish at this common-rest reference by parity, including the first variation.

At common boost U, raw momentum sources are m r U, −h r U and M r U. The correct reactive centralization is R_2−UF^T−FU^T+m_s R_n UU^T. Its number-source term is essential; using the elastic fixed-number formula would create a spurious frame dependence.

## 5. Exact sharing-moment compression

Direct integration of (4) gives

\[
\overline\Upsilon(E)=\frac{IE}{E-I}\log(E/I).
\tag{12}
\]

This expression is evaluated with log1p((E−I)/I) near threshold. Let x=I/θ and

\[
C_\mu=4\pi a_0^2I\sqrt{\frac8{\pi\mu}}\theta^{-3/2}.
\]

The weighted Maxwell measure is C_μ(E−I)exp(−E/θ)dE/E. Therefore

\[
\Lambda:=\langle K\overline\Upsilon\rangle
=C_\mu I\int_I^\infty\log(E/I)e^{-E/\theta}dE
=C_\mu I\theta E_1(x).
\tag{13}
\]

The boundary term in integration by parts vanishes both at E=I and infinity. Using E_2(x)=e^(−x)−xE_1(x) and the existing same-kernel moments α=C_μθE_2(x), β=C_μθ²e^(−x),

\[
\boxed{\Lambda=\beta-\theta\alpha,\qquad
U_1:=\langle K(E-\Upsilon)\rangle=\theta\alpha,\qquad
U_2:=\langle K(\Upsilon-I)\rangle=\beta-(I+\theta)\alpha.}
\tag{14}
\]

The transferred-energy moment adds no independent radial moment to the production calculation. This is a consequence of the selected cross section and transfer law together; it is not a generic identity for arbitrary CI models.

For a positive numerical oracle define

\[
F(x)=e^xE_2(x)=\int_0^\infty\frac{t}{x+t}e^{-t}dt.
\]

Differentiation of this positive integral and the E_n recurrence gives

\[
H(x):=1-(x+1)F(x)=-xF'(x)
=x\int_0^\infty\frac{t}{(x+t)^2}e^{-t}dt>0,
\]

\[
U_2=C_\mu\theta^2e^{-x}H(x).
\tag{15}
\]

The ratio U_2/(θα)=H/F is a positive weighted mean of x/(x+t), so 0<U_2<θα. Consequently I+θ<β/α<I+2θ. The positive integral is a useful independent control; the production species heat formulas below avoid constructing a small U_2 by subtraction. The exact existing provider kernel is reused with the scaling α_μ,β_μ,γ_μ,δ_μ = sqrt(m/μ) times the HE37 moments because only the relative-speed prefactor changed. Identity, source threshold, constants and support remain explicit.

## 6. Species kinetic-energy source and total heat

The gain energies, after averaging COM motion, are

\[
Q_e^+/(n_en_H)=3\eta\theta\alpha+(1-\eta c)U_1+cU_2,
\]

\[
Q_p^+/(n_en_H)=\tfrac32(\zeta-\eta)\theta\alpha+\eta cU_1+dU_2.
\tag{16}
\]

Reuse the HE36 incoming-loss result with (m_A,m_B)=(m,h):

\[
Q_e^-/(n_en_H)=-\tfrac32\eta\theta\alpha-\zeta\beta,
\quad Q_H^-/(n_en_H)=-\tfrac32\zeta\theta\alpha-\eta\beta.
\tag{17}
\]

Substitute (14) and d=η/ζ to obtain computational forms:

\[
\boxed{Q_e/(n_en_H)=
\eta\left[\left(\tfrac32+2d\right)\theta\alpha-d\beta\right]-cI\alpha,}
\]

\[
\boxed{Q_H/(n_en_H)=-\tfrac32\zeta\theta\alpha-\eta\beta,}
\]

\[
\boxed{Q_p/(n_en_H)=
\left[\tfrac32(\zeta-\eta)-2\eta d\right]\theta\alpha+d\beta-dI\alpha.}
\tag{18}
\]

Their sum is exactly −Iα. The heavy combined source should be calculated directly when its small value is required:

\[
(Q_H+Q_p)/(n_en_H)
=-\eta(\tfrac32+2d)\theta\alpha+\eta d\beta-dI\alpha.
\tag{19}
\]

Subtracting two individually large H-removal/proton-birth terms can lose relative precision in this small combined quantity. Equations (18)–(19) and Q_total=−Ir are independently owned outputs with consistency checks, rather than reconstructed by subtracting almost equal floating-point quantities.

For an explicitly all-retained common thermal pool, R_part=r and

\[
\dot T_{\rm reaction}=-\frac r{n_{\rm part}}
\left(T+\frac{2I}{3k_B}\right).
\tag{20}
\]

This temperature expression follows from the energy-to-temperature chain rule and the chosen inventory. The kinetic source does not establish rapid thermalization, common T/u or electron-to-total-gas stress closure.

## 7. Full species STF map

Let t=θ/L and Z be any STF tensor. Wick contraction yields

\[
\langle VV K[Z:(V+\lambda g_0)(V+\lambda g_0)]\rangle_{\rm STF}
=2t^2\alpha Z.
\tag{21}
\]

The λ² g_0g_0 term has a scalar angular average proportional to tr Z and the mixed term is odd in V. Thus isotropic internal Jacobi energy contributes zero to the STF gain, while COM motion contributes

\[
J_e^+=2\alpha[n_H\eta^2\pi_e+n_e\eta\zeta\pi_H],
\]

\[
J_p^+=\alpha[n_H\eta(\zeta-\eta)\pi_e+
n_e\zeta(\zeta-\eta)\pi_H].
\tag{22}
\]

Reuse the HE36 incoming pair coefficients

\[
A=\eta^2\alpha+2\eta\zeta\kappa_1+\zeta^2\kappa_2,
\quad B=\zeta^2\alpha+2\eta\zeta\kappa_1+\eta^2\kappa_2,
\quad C=\eta\zeta(\alpha-2\kappa_1+\kappa_2).
\tag{23}
\]

Then the complete source map is

\[
\boxed{
\begin{pmatrix}J_e\\J_H\\J_p\end{pmatrix}
=
\begin{pmatrix}
n_H(2\eta^2\alpha-A)&n_e(2\eta\zeta\alpha-C)\\
-n_HC&-n_eB\\
n_H\eta(\zeta-\eta)\alpha&n_e\zeta(\zeta-\eta)\alpha
\end{pmatrix}
\begin{pmatrix}\pi_e\\\pi_H\end{pmatrix}.}
\tag{24}
\]

Each scalar coefficient acts on every independent STF component. A preexisting proton stress does not enter the forward CI operator because protons are not incoming reactants. This does not remove proton stress from other collisions or the total inventory.

Summing (24), every α and κ_1 term cancels:

\[
\boxed{J_{\rm total}=-\kappa_2[n_H\zeta\pi_e+n_e\eta\pi_H].}
\tag{25}
\]

The same formula follows directly from event tensor (9): only the μg_0g_0 term carries STF, and the relative-velocity quadrupole in the two Grad perturbations has the weights ζ and η. This is an independent route to the summed species result. It is not generally a scalar multiple of π_e+π_H+π_p: the species partition remains an input. Do not infer a general entropy theorem or full reactive relaxation spectrum from the incoming-loss matrix alone.

## 8. Limits, dimensions and implementation consequences

All Q have units J m^-3 s^-1=Pa/s, all J have units Pa/s, α/κ_i have units m³/s, β has J m³/s and γ has J² m³/s. R_e=R_p=−R_H has units m^-3 s^-1. The total event-pressure trace check gives tr S_total/2=Q_total; S_s=J_s+(2Q_s/3)Id.

As M/m→∞, η,d→0, ζ,c→1, μ→m:

* Q_e→−Ir and Q_H+Q_p→0. Individual H/proton thermal-removal/birth terms cancel in their sum.
* J_e→−n_Hκ_2π_e, J_H→−n_eαπ_H, J_p→+n_eαπ_H; total J reproduces HE37.
* The original source-coordinate energies become the HE37 outgoing electron energies E−Υ and Υ−I. At the common-rest Maxwellian reference, V variance vanishes and the adopted angular law becomes the HE37 independent isotropic outgoing directions. This is a differential-law continuation, unlike the discarded microcanonical alternative.

For π_H=0, the total STF coefficient relative to HE37 at the same T and electron stress is ζκ_2,μ/κ_2,m=√ζ. The event-rate ratio is α_μ/α_m=1/√ζ. These distinct factors follow from reduced mass plus relative-stress weighting; applying only the rate scaling to STF would miss one factor of ζ.

At absent reactant density, physical source is zero and nonzero stress of the absent species is inadmissible. A coefficient/Jacobian evaluated as a boundary derivative may remain nonzero and must be labeled separately. For tiny traceless tensors, compute J directly; recovering it by subtracting a large isotropic trace from S can erase it. Keep the signed net source without covariance clipping.

The production implementation needs only the unchanged HE37 α,β,γ (and δ if a derivative is requested), a reduced-mass prefactor, mass fractions and exact species maps (18)/(24). New differential-event reconstruction and sharing controls validate this new finite-mass dependence. No existing HE37 suite or IVP is replayed for this derivation.

## 9. Provenance and review boundary

Reused files: HE36 `theory/independent_DERIVATION.md` Eqs.(4)–(6),(10), its executed incoming-loss implementation, and HE37 `theory/DERIVATION.md` Eqs.(10)–(14). Their file identities are recorded by PROVENANCE.json. This unit derives the finite-mass outgoing gain and combined species map; source qualification and independent nonauthor final review remain separate records owned by root. The claims are constructive and conditional; no new strong no-go or global novelty claim is made.

The independent author controls in CHECKS.json passed in 2.539 seconds. They cover 108 exact-rational event reconstructions over three finite mass ratios, all five incoming STF directions for each of two parent species at each mass ratio (30 directions and 90 species tensors), exact scalar-partition checks, and six new high-precision transferred-energy/partition controls. Exact algebra residuals are zero; the largest reported 65-digit partition-identity relative discrepancy is 1.90×10^−65. These are checks of the declared model, not empirical evidence for its angular law. No old scientific suite, IVP, benchmark or render was replayed.
