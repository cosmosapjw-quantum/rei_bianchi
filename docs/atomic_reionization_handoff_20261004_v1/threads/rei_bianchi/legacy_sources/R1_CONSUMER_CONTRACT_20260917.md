# BASS PRESENT R1 — Nonperturbative Multifrequency H/He Reionization Contract

Date: 2026-09-17 Asia/Seoul

## Verdict

`R1 = ANALYTICALLY_CLOSED_NONPERTURBATIVE_MULTIFREQUENCY_HHE_REIONIZATION_CONTRACT`

```text
REPORT_BRANCH                         FROZEN_AT_R5_RC
CR0_REGIME_ATLAS                     COMPLETE
CR1_EXECUTION                         NOT_STARTED / PRESENTATION-DAG PARKED
R1_PHOTON_HHE_CONTRACT                COMPLETE
PRODUCTION_CODE_MUTATION              NO
HISTORICAL_R15P                       HOLD_MISSING_HISTORICAL_AUTHORITY
HISTORICAL/PRODUCTION_D2_AMPLITUDE    NOT_CLAIMED
NEXT                                 R2_NONTILTED_HOMOGENEOUS_SOLVER_REALIZATION
```

This work unit upgrades the original perturbative anisotropic-reionization programme into a nonperturbative, multifrequency, nonequilibrium H/He transport programme. It does not run WU086-CR1 and does not alter the independent CR branch authority. The presentation-integration DAG deliberately closes the photon/H-He receiver solver before coupling cosmic rays to it.

---

## 1. Scientific target

The perturbative report treated anisotropy through logarithmic spectral displacements and response coefficients

\[
\Gamma_s(\Delta)/\Gamma_{s0}
=1+A_s\Delta+\tfrac12 B_s\Delta^2+\cdots.
\]

R1 changes the role of \(A_s,B_s\). They are no longer primary inputs. The nonperturbative solver evolves the radiation field and H/He thermochemistry directly, and the effective coefficients are *measured afterwards* as derivatives of the exact numerical response:

\[
A_s^{\rm eff}=\frac{1}{\Gamma_{s0}}
\left.\frac{\partial\Gamma_s}{\partial\Delta}\right|_0,
\qquad
B_s^{\rm eff}=\frac{1}{\Gamma_{s0}}
\left.\frac{\partial^2\Gamma_s}{\partial\Delta^2}\right|_0.
\]

The central comparison observable becomes

\[
R_{\Gamma,s}
=\frac{\Gamma_s^{\rm exact}-\Gamma_s^{\rm pert}}
{\Gamma_s^{\rm exact}},
\]

with analogous residuals for heating, temperature, and ion fractions.

---

## 2. Geometry and transport authority

### 2.1 Principal first geometry: Bianchi I

Use

\[
ds^2=-c^2dt^2+a_1^2(t)(dx^1)^2+a_2^2(t)(dx^2)^2+a_3^2(t)(dx^3)^2.
\]

Define

\[
H_i=\dot a_i/a_i,\qquad
H=\frac13(H_1+H_2+H_3),\qquad
\sigma^i{}_j=(H_i-H)\delta^i{}_j.
\]

The geometry is prescribed by a validated background interface in R2. Radiation/thermochemistry backreaction on the Einstein equations is outside the first solver.

### 2.2 Exact photon characteristics

For normal-frame photon energy \(E\) and orthonormal direction \(e^i\),

\[
\frac{d\ln E}{dt}
=-\sum_i H_i(e^i)^2
=-H-\sigma_{ij}e^ie^j,
\]

\[
\dot e^i
=\left(\sum_jH_j(e^j)^2-H_i\right)e^i
=-\sigma^i{}_j e^j+\sigma_{kl}e^ke^l e^i.
\]

For an interval \(t_0\to t_1\), let

\[
r_i=a_i(t_0)/a_i(t_1).
\]

Then the exact characteristic map is

\[
\frac{E_1}{E_0}
=G=\left[\sum_i(e_0^i)^2r_i^2\right]^{1/2},
\qquad
 e_1^i=\frac{e_0^i r_i}{G}.
\]

This exact map is the Bianchi-I geometric authority. A numerical angular advection operator must reproduce it, rather than define the physics.

### 2.3 Occupation-number Liouville variable

The principal radiation variable is the dimensionless occupation number

\[
f_\gamma(t,\nu,\mathbf e).
\]

In the normal tetrad,

\[
\partial_t f_\gamma
+\dot{\ln\nu}\,\partial_{\ln\nu}f_\gamma
+V^A\nabla_A^{(S^2)}f_\gamma
=C_t[f_\gamma].
\]

There is no explicit collisionless dilution source in the \(f\) equation.

For trace-free diagonal shear the angular flow obeys

\[
\nabla_{S^2}\!\cdot V=3\sigma_{ee}.
\]

Together with \(\dot{\ln\nu}=-H-\sigma_{ee}\), the divergence of the \(\nu^2d\nu\,d\Omega\) momentum measure is exactly \(-3H\). Therefore in the collisionless source-free problem

\[
\frac{d}{dt}\left[a_1a_2a_3\,n_\gamma\right]=0
\]

is a mandatory exact numerical gate.

---

## 3. Matter frame and finite tilt

Let the material congruence be

\[
u^a=\gamma(n^a+\beta^a),\qquad
\gamma=(1-\beta^2)^{-1/2}.
\]

For a normal-frame photon direction \(e^a\), define the exact Doppler factor

\[
D(\mathbf e)=\gamma(1-\beta_a e^a),
\qquad
\nu_u=D\nu_n.
\]

The occupation number is Lorentz invariant. The standard radiation invariants imply

\[
\frac{I_\nu}{\nu^3}=\mathrm{invariant},\qquad
 d\Omega_u=D^{-2}d\Omega_n,\qquad
 d\nu_u=D\,d\nu_n.
\]

Hence the matter-frame photoionization rate per absorber can be evaluated directly on the normal-frame distribution:

\[
\Gamma_s
=\frac{2}{c^2}\int d\Omega_n\int d\nu_n\,
D\,\nu_n^2 f_\gamma
\sigma_s(D\nu_n)
\Theta(Dh\nu_n-\chi_s).
\]

The corresponding photoelectron heating per absorber is

\[
q_s
=\frac{2}{c^2}\int d\Omega_n\int d\nu_n\,
D\,\nu_n^2 f_\gamma\sigma_s(D\nu_n)
(Dh\nu_n-\chi_s)
\Theta(Dh\nu_n-\chi_s).
\]

The normal-frame absorption operator contains the same factor \(D\):

\[
(\partial_t f)_\mathrm{abs}
=-c\,D\,\kappa_u(D\nu_n)f.
\]

This ensures that integrated photon loss per normal four-volume equals the matter-frame primary photoionization event count.

### Tilt staging rule

The first executable R2 lane is \(u^a=n^a\) (non-tilted matter) so that photon, chemistry, and thermal conservation can be closed without an external bulk-kinetic-energy reservoir. The exact finite-tilt adapter above is frozen in R1 and must be activated in a separate R2-T gate after R2-N passes.

For homogeneous tilted chemistry,

\[
u^a\nabla_a x=R_x
\quad\Rightarrow\quad
\gamma\dot x=R_x.
\]

Nuclear-number conservation on a normal slice is naturally written in terms of \(\gamma n_s a_1a_2a_3\).

---

## 4. H/He nonequilibrium state

The minimum matter state is

\[
Y_m=
\{x_{\rm HII},x_{\rm HeII},x_{\rm HeIII},u_{\rm th}\}.
\]

Derived fractions:

\[
x_{\rm HI}=1-x_{\rm HII},
\]

\[
x_{\rm HeI}=1-x_{\rm HeII}-x_{\rm HeIII}.
\]

Electron density:

\[
n_e=n_Hx_{\rm HII}
+n_{He}(x_{\rm HeII}+2x_{\rm HeIII}).
\]

The non-tilted baseline equations are

\[
\dot x_{\rm HII}
=x_{\rm HI}(\Gamma_{\rm HI}+n_e C_{\rm HI})
-x_{\rm HII}n_e\alpha_{\rm HII},
\]

\[
\dot x_{\rm HeII}
=x_{\rm HeI}(\Gamma_{\rm HeI}+n_eC_{\rm HeI})
+x_{\rm HeIII}n_e\alpha_{\rm HeIII}
-x_{\rm HeII}(\Gamma_{\rm HeII}+n_eC_{\rm HeII}+n_e\alpha_{\rm HeII}),
\]

\[
\dot x_{\rm HeIII}
=x_{\rm HeII}(\Gamma_{\rm HeII}+n_eC_{\rm HeII})
-x_{\rm HeIII}n_e\alpha_{\rm HeIII}.
\]

The coefficients include the standard primordial-gas collisional/recombination channels. Helium dielectronic recombination is folded into the appropriate total coefficient where required by the adopted atomic-data authority.

### Thermal state

Use proper thermal internal-energy density, not temperature, as the primary variable:

\[
u_{\rm th}=\frac32 n_{\rm part}k_BT.
\]

Then

\[
\dot u_{\rm th}+\Theta(u_{\rm th}+p)
=Q_\gamma-\Lambda,
\]

for the non-tilted baseline, with

\[
p=n_{\rm part}k_BT.
\]

This avoids hiding the composition-work term when ionization changes \(n_e\). Temperature is reconstructed from \(u_{\rm th}\) and the instantaneous particle count.

Mandatory cooling/heating families for R2-N:

- H/He photoheating;
- collisional ionization/excitation cooling;
- radiative + dielectronic recombination cooling;
- free-free cooling;
- Compton coupling to the CMB;
- adiabatic expansion.

---

## 5. Absorption and photon/energy ledgers

Bound-free opacity in the matter frame is

\[
\kappa_\nu^{\rm bf}
=n_{\rm HI}\sigma_{\rm HI}(\nu)
+n_{\rm HeI}\sigma_{\rm HeI}(\nu)
+n_{\rm HeII}\sigma_{\rm HeII}(\nu).
\]

The instantaneous physical mean free path is

\[
\lambda_\nu=(\kappa_\nu^{\rm bf})^{-1}
\]

in the homogeneous baseline. No external MFP closure is inserted in R2-N.

For every spectral/angular cell, the discrete absorbed photon count must be partitioned by physical opacity ownership,

\[
w_s=\frac{\kappa_s}{\sum_r\kappa_r},
\qquad
\Delta N_s^{\rm abs}=w_s\Delta N_\gamma^{\rm abs}.
\]

The primary photoionization ledger requires

\[
\sum_s\Delta N_s^{\rm primary}
=\Delta N_\gamma^{\rm abs}
\]

to the declared numerical tolerance.

For the primary-only baseline, absorbed energy is partitioned as threshold work plus photoelectron heat. Hard-photon secondary-electron deposition is a separately labelled MICRO-1 extension and must use an external validated deposition model rather than an ad hoc fraction.

---

## 6. Source contract

The homogeneous source is specified by a matter-frame emissivity

\[
j_\nu^{(u)}(t,\mathbf e)
=\bar j_\nu(t)
\left[1+s_a e^a+s_{ab}e^ae^b+\cdots\right].
\]

Source anisotropy is therefore explicit and can be set to zero for the clean geometry-only control.

Three source families are preregistered conceptually:

1. S0: monochromatic/near-threshold verification sources;
2. S1: stellar/Pop-III-like UV spectrum;
3. S2: hard power-law/X-ray control.

No source family may be tuned after inspecting anisotropy observables.

The finite-tilt source transform must use the Lorentz emissivity invariant \(j_\nu/\nu^2\).

---

## 7. Spectral representation contract

Use logarithmic normal-frame photon energy

\[
y=\ln(h\nu_n/\chi_{\rm HI}).
\]

The spectral partition must contain exact boundaries at

\[
\chi_{\rm HI}=13.598434599702\,\mathrm{eV},
\quad
\chi_{\rm HeI}=24.587389011\,\mathrm{eV},
\quad
\chi_{\rm HeII}=54.417760\,\mathrm{eV}.
\]

A sub-threshold guard interval is mandatory so photons redshifted below H I threshold are not spuriously deleted.

The upper energy boundary is not fixed by convenience. For each source family, \(E_{\max}\) must be chosen *before anisotropy results are inspected* so that omitted source photon number and omitted source energy are each below a frozen tail tolerance.

For finite tilt, a matter-frame threshold appears at normal-frame energy

\[
h\nu_{n,s}=\chi_s/D(\mathbf e).
\]

Therefore collision quadrature must split an energy element at the exact moving threshold whenever it crosses that element. A fixed-bin nearest-threshold approximation is not permitted for the tilt-validation lane.

Photoionization cross sections use the frozen Verner-family H/He fits or an equivalently validated atomic authority; changing cross-section authority is a separate work unit.

---

## 8. Numerical architecture authorized for R2

The continuum contract does not force a production implementation, but it freezes these numerical requirements:

### Geometry step

Use the exact Bianchi-I characteristic map as the reference. Any remap onto a numerical angular-energy representation must be conservative and positivity preserving.

### Local stiff step

The coupled local state

\[
Y=\{f_{gq},x_{\rm HII},x_{\rm HeII},x_{\rm HeIII},u_{\rm th}\}
\]

is advanced with a block-implicit residual or an equivalent stiff-stable method. The chemistry/thermal solver may use Newton/JVP/AD machinery, borrowing the BASS monolithic-residual methodology, but may not alter the physical equations to improve convergence.

### Temporal composition

The geometry and local stiff operators must be composed with a globally second-order method for smooth tests. A Strang-style exact-geometry / local-stiff / exact-geometry composition is the reference architecture unless R2 demonstrates a stricter alternative before physical output is examined.

### Principal angular state

A positivity-preserving directional representation is required. Harmonic/Fourier reconstructions may be retained as diagnostics, but the WU13 strict-coherency experience prohibits treating a non-positive spectral reconstruction as unquestioned physical state authority.

---

## 9. Exact and asymptotic gates

### G0 — FLRW collisionless

For \(a_1=a_2=a_3=a\),

\[
E\propto a^{-1},\qquad \dot{\mathbf e}=0,
\]

and collisionless comoving photon number is constant.

### G1 — Bianchi-I exact geodesic

The numerical transport must reproduce the exact characteristic map for arbitrary prescribed \(a_i(t)\).

### G2 — angular norm

\[
e_ie^i=1
\]

must be preserved by the geometric update.

### G3 — photon number

Source-free/absorption-free:

\[
a_1a_2a_3 n_\gamma=\mathrm{const}.
\]

### G4 — nuclei

\[
x_{\rm HI}+x_{\rm HII}=1,
\qquad
x_{\rm HeI}+x_{\rm HeII}+x_{\rm HeIII}=1.
\]

### G5 — photon-ionization ownership

Integrated primary photoionizations equal integrated bound-free photon absorption species-by-species.

### G6 — positivity

\[
f_\gamma\ge0,\quad
0\le x_i\le1,\quad
u_{\rm th}\ge0.
\]

### G7 — weak-shear limit

With isotropic uncorrelated source/opacity weighting, the exact solver must recover

\[
\langle\Delta_\sigma\rangle=0,
\qquad
\langle\Delta_\sigma^2\rangle=\frac{2}{15}S_{ab}S^{ab},
\]

and hence

\[
\left\langle\frac{\delta\Gamma_s}{\Gamma_{s0}}\right\rangle_\sigma
=\frac{B_s}{15}S_{ab}S^{ab}+O(S^3).
\]

### G8 — weak-tilt adapter

The finite boost must recover

\[
\ln D=-\beta\mu+\frac12\beta^2(1-\mu^2)+O(\beta^3),
\]

\[
\left\langle\frac{\delta\Gamma_s}{\Gamma_{s0}}\right\rangle_\beta
=\left(\frac{A_s}{3}+\frac{B_s}{6}\right)\beta^2+O(\beta^3).
\]

### G9 — correlation restoration

A preregistered anisotropic source/opacity test must demonstrate that a nonzero correlated moment such as

\[
\langle\delta\kappa(\mathbf e)\sigma_{ab}e^ae^b\rangle
\]

can restore a linear scalar response. The sign is not preregistered.

### G10 — microphysics reference

At \(\sigma=\beta=0\), one-zone ionization/heating benchmarks must agree with a validated H/He reference implementation or published equilibrium/test solution using the same rates and source spectrum.

---

## 10. Frozen numerical acceptance policy for R2

The exact ladder values are to be preregistered in the first R2 implementation receipt before production-like results are viewed. The following gates are frozen now:

- smooth global temporal order: >= 1.8;
- smooth spectral/angular refinement must demonstrate convergence rather than a single-resolution pass;
- closed-form collisionless characteristic relative error: <= 1e-10 where machine precision permits;
- nuclei-sum defects: <= 1e-10 in unit tests and <= 1e-8 in long coupled runs;
- cumulative photon-primary-ionization ledger defect: <= 1e-8;
- negative physical-state values larger than 1e-12 in normalized units: FAIL, not clipped silently;
- weak-anisotropy derivative/parity regression: relative discrepancy <= 1e-3 at preregistered sufficiently small amplitudes;
- no post-hoc change of thresholds, source SED, angular grid, energy grid, tolerances, or microphysical rates based on desired physical signal.

---

## 11. Microphysics staging

### MICRO-0 — mandatory first solver

- H I / He I / He II photoionization;
- H/He collisional ionization;
- radiative + dielectronic recombination;
- primary photoheating;
- standard primordial cooling;
- Compton + adiabatic terms.

### MICRO-1 — hard-photon extension

- fast-electron secondary ionization of H/He;
- excitation;
- heat deposition fractions from a validated external calculation.

Required before claiming a hard-X-ray source result.

### MICRO-2 — explicit recombination radiation

The baseline may use a coupled on-the-spot closure for verification, but explicit diffuse recombination radiation is a separate sensitivity lane because anisotropic transport can make an isotropic local OTS assumption physically nontrivial.

---

## 12. Observable registry

Primary physical outputs:

\[
\Gamma_{\rm HI},\ \Gamma_{\rm HeI},\ \Gamma_{\rm HeII},
\]

\[
Q_{\rm HI},\ Q_{\rm HeI},\ Q_{\rm HeII},
\]

\[
T_K,\ x_e,\ x_{\rm HII},\ x_{\rm HeII},\ x_{\rm HeIII},
\]

\[
\lambda_\nu=(\kappa_\nu^{\rm bf})^{-1}.
\]

Grey-rejecting threshold diagnostics:

\[
D^\gamma_{\rm HeI/HI}
=\delta\ln\Gamma_{\rm HeI}-\delta\ln\Gamma_{\rm HI},
\]

\[
D^\gamma_{\rm HeII/HI}
=\delta\ln\Gamma_{\rm HeII}-\delta\ln\Gamma_{\rm HI}.
\]

Angular diagnostics:

- dipole/quadrupole and higher multipoles of \(\Gamma_s(\mathbf e)\);
- scalar angular means;
- cross-correlation with source/opacity anisotropy.

Method diagnostics are kept separate from physical outputs.

---

## 13. Literature-controlled choices

The adopted physical/numerical architecture is consistent with:

- C2-Ray: explicit photon conservation and non-equilibrium ionization;
- Friedrich et al. 2012: helium, multifrequency heating, coupled OTS, secondary ionization, temperature sensitivity;
- TRAPHIC multifrequency work: simultaneous H/He + thermal/ionization evolution and failure modes of grey heating;
- fully coupled reionization methods: radiation, thermal, ionization and dynamics evolved in a single coupled calculation rather than post-processed response coefficients;
- Verner et al.: analytic H/He photoionization cross-section fits;
- Furlanetto & Stoever: fast-electron energy deposition for the later hard-photon/CR interface.

These papers do not prove any BASS-specific anisotropic implementation. They define the microphysical/numerical comparison envelope only.

---

## 14. Dependency decision for the presentation programme

Independent CR branch state remains:

`WU085-CR0 COMPLETE -> WU086-CR1 HANDOFF READY`.

The presentation programme intentionally inserts the photon/H-He solver dependency:

```text
R1 contract (this work unit)
  -> R2-N non-tilted homogeneous solver
  -> R2-T finite-tilt nonlinear solver
  -> R3 source/opacity-correlated H/He model
  -> R4 spatial/source-native anisotropic reionization
  -> CR1 covariant charged-particle + Maxwell operator
  -> CR3 joint photon+CR H/He thermochemistry
```

This reordering does not invalidate the CR branch. It only prevents the CR thermochemistry extension from being coupled to a perturbative placeholder H/He receiver.

---

## 15. Next canonical work unit

`BASS_PRESENT_R2_NONTILTED_HOMOGENEOUS_MULTIFREQUENCY_HHE_SOLVER_REALIZATION`

First action:

1. freeze exact atomic-rate source identities and source SED fixtures;
2. preregister spectral/angular/time refinement ladders;
3. implement only the non-tilted homogeneous Bianchi-I lane;
4. run G0–G7 and G10 before any finite-tilt or source-correlation result;
5. do not start CR1 inside the presentation branch until R2-N has a durable PASS or a scientifically interpretable blocker.
