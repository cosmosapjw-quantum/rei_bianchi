# CMB 물리적 감쇠 + 비열적 deuteron 전자 감속: 유도, 계산식, 판정

## R1–R3: 목적·근거·모형 정의

원래 목표는 `f_gamma^(alpha)(x,p)`와 비열적 D plasma deposition을 연결하는 것. 그 중 코스몰로지 소스의 **주입강도**가 없더라도 이미 측정·정립된 CMB 열광자와 QED에서 직접 계산되는 `Gamma_gamma-gamma`, 그리고 출판된 플라스마 이론의 leading-log 전자 Coulomb drag를 구할 수 있다. 실제 BASS_HE nonthermal gamma emission source를 만들었다고 주장하지 않는다.

- Metric `(-,+,+,+)`; photon and nuclei measured in local, comoving alpha rest frame; `E` is photon energy there. `c`, `hbar`, `k_B` are explicitly retained in formulas.
- Model: Planck 2018 flat FLRW 6-parameter reference, `h=0.674`, `Omega_m=0.315`, `T_CMB0=2.7255 K`, `N_eff=3.046`, PDG `n_b,0=2.515e-7 cm^-3`, `Yp=0.2448`. This is a reference background, NOT user BASS native anisotropic dynamic solution.
- Redshift range `1e4..2e7`, CMB blackbody, fully ionized nondegenerate H/He composition; equilibrium e± assumed negligible at these temperatures. Neutrino background enters only `H(z)`.
- Gamma test energy 150,170,190,220,250 MeV; daughter D test kinetic energy 50,75,100,125,150 MeV. No injected-photon **number** or energy density is assumed.

## R4–R5: exact thermal Breit–Wheeler opacity (established QED + derived integral)

From Gould & Schréder, Phys. Rev. 155, 1404 (1967):

```
beta^2 = 1 - 4 (m_e c^2)^2 / s,
    s = 2 E eps (1 - cos theta) = 4 E eps u,
    u = (1 - cos theta)/2, 0<=u<=1,
sigma_BW(beta) = (3 sigma_T/16) (1-beta^2)
  [ (3-beta^4) log((1+beta)/(1-beta)) - 2 beta (2-beta^2) ]
```

`sigma_BW = 0` below `E eps u < (m_e c^2)^2`; `eps` is CMB photon energy. `n_BB(eps) d eps = eps^2 d eps/[pi^2(hbar c)^3 (exp(eps/k_B T_gamma)-1)]` counts two polarizations, `cm^-3`. The local test-photon interaction frequency is:

```
Gamma_gg(E,z) = c int d eps n_BB(eps,z) int_0^1 du 2u sigma_BW(E,eps,u)
```

The numerical code applies `x=eps/(k_B T)`, `x_min=(m_e c^2)^2/(E k_B T)`, uses Gauss–Legendre integration for `x in [x_min,x_min+65]` and `u in [x_min/x,1]`; an independent `scipy.integrate.quad` uses direct linear `u`. The original small cross section is not approximated as a constant. All `Gamma_gg` units `s^-1`; `Gamma_gg/H` dimensionless, `H(z)^2=H0^2 [Omega_r(1+z)^4+Omega_m(1+z)^3+Omega_L]` with `Omega_r=Omega_gamma*(1+0.2271 N_eff)` and `Omega_gamma*h^2=2.473e-5`.

Source-calibrated data outcome: 

- E=150/170/190/220/250 MeV local `Gamma_gg/H=1` redshifts approximately `227186 / 201223 / 180655 / 156724 / 138463`. Above this, pair-interaction timescale shorter than Hubble time; no assertion of globally sharp observed cutoff.
- At z=1e6, E=220 MeV: `Gamma_gg=3.9714748013e4 s^-1`, `Gamma_gg/H=1.8913866593e12`.

## R4–R5: locally competing exclusive He-dd hazard (source-conditional)

For source-qualified Rice 2000 final `P0+P2` constrained bin fits reused from PR128 (8.29 nb for 150–190 MeV, 4.34 nb for 190–250 MeV), **no pointwise excitation measurement is claimed**. Treat each bin number as a piecewise-constant model value solely for a local diagnostic.

```
Gamma_dd_given_gamma(E,z) = c n_He4(z) sigma_dd,event^bin(E),
P_dd_first_twochannel = Gamma_dd/(Gamma_dd + Gamma_gg),
n_He4(z) = (Yp/4) n_b0 (1+z)^3,
E[D daughters produced in dd event] = 2.
```

If (and only if) the *first* interaction is limited to two irreversible channels, `P_dd_first_twochannel` is the probability of dd at that event. Other photon interactions and regeneration are not included, so it is **not** a full-cascade `P_dd`, an observed source rate, or a rigorous global bound. A ±1 sigma *normalization-only* sensitivity for the Rice source is given, using 7.1% or 13% by energy bin; no unprovided covariance or energy-shape error is inferred.

At z=1e6, E=220 MeV `Gamma_dd=2.002632e-12 s^-1` vs `Gamma_gg=39714.748 s^-1`, two-channel first dd fraction `5.04254e-17`. This is a nontrivial physical source-calibrated competition result, but no high-energy injection has been specified and therefore no volumetric `R_event` can be reported.

## R4–R5: electron-only fast-D Coulomb stopping benchmark (modelled)

Under a weakly coupled Maxwellian fully ionized plasma and a heavy deuteron projectile:

```
v_d/c = sqrt(1-[m_d c^2/(m_d c^2 + K_d)]^2),
F(X) = erf(X) - (2X/sqrt(pi)) exp(-X^2), X=v_d/sqrt(2k_B T_e/m_e),
-(dK_d/dt)_e = [4pi n_e Z_d^2 (e^2/4pi eps_0)^2/(m_e v_d)]
  * ln Lambda * F(X)
```

The cgs/SI conversions are explicitly implemented. Electrons only: ion-drag, hard nuclear reactions, recoil photon transfer, nonthermal secondaries, pitch-angle and longitudinal diffusion, finite BPS next-to-leading Coulomb-log constant and actual heat partition are not included. `lnLambda_static = ln(lambda_D/b_min)` and `lnLambda_dynamic = ln(max(lambda_D,v_d/omega_pe)/b_min)` are separately reported *screening-choice sensitivity variants*, not an experimental confidence interval. `b_min = max(Z_d (e^2/4pi eps_0)/(m_e v_d^2),hbar/(2m_e v_d))`, `lambda_D^2=eps_0 k_B T_e/(n_e e^2)`, `omega_pe^2=n_e e^2/(eps_0 m_e)`.

At z=1e6, K_d=100 MeV, `|dK/dt|_{e,dynamic}=0.241438 MeV/s` and characteristic *instantaneous* loss time `K_d/|dK/dt|` divided by Hubble time is `8.69693e-6`. The instantaneous loss time is not the fully integrated stopping time and the electron energy transfer is NOT guaranteed to become local plasma heat. Fully quantitative BPS next-order and Jedamzik nuclear-survival physics remain next-step obligations.

## R6–R8: verified checks and claim admission

- 23/23 Python tests in current root: original user PDF byte lock, radiation blackbody number density ~410.7 cm^-3 at z0, electron charge neutrality, exact two-body energy conservation and identical-D exchange, energy and redshift positivity/monotonicity, thermally corrected drag with weak coupling, and two-channel probability. Independent adaptive quadrature vs Gauss integration relative mismatch below 2e-5 on four representative cells. Additional high-order quadrature convergence <4e-5.
- Independent Wolfram on 2026-10-31: `sigma_BW(beta=0.7)/sigma_T=0.25563674642071383`, and at E_gamma=220 MeV muCM=0.5, `K_+=114.9484964712988`, `K_-=81.20502532870111` MeV; Python agrees.
- Source PDF is not reconstructed nor re-posted. User copy has SHA `87fe939...`; thesis printed SAL Table5.1 final error and Appendix-A.1 flux inconsistency from PR130 remain unchanged, and PR130 prior final published 2000 results are not silently modified.
- Physical status: valid standalone *conditional FLRW thermal-opacity and leading-log electron-drag benchmark*. It is not source-owned astrophysical 150–250 MeV emission and it does not close HE physical DAG. Exact central=28/88, HE=14/18; scoped science micro 2/2.

## R9–R10: computational interface and positive next action

The next non-cosmetic physical computation is source-owned actual `n_gamma^(alpha)(t,x,E,Omega)` from a well-defined source emissivity and a complete full-energy cascade; it may use `Gamma_gg(E,z)` here as a rigorous loss term only in the adopted homogeneous thermal context. Obtain an upstream actual BASS snapshot with frame/epoch, `n_alpha`, `u_alpha`, `T_e`, `n_e`, radiation field and model injection; integrate BPS/Jedamzik ion/electron drag and nuclear survival to produce `F_d` and the full thermal deposition Green function. Do not substitute previous SAL laboratory bremsstrahlung or REI 13.7–100 eV photons.
