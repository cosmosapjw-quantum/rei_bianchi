# BASS_HE: source-qualified He-4 competing photoreactions under KN regeneration (2026-10-31)

**Independent bounded scientific extension, not an activated cosmological source.**
Parent is Draft PR #132 immutable commit `3bf639cc4f8534f9de3986ee9936e26818b42e37` in `cosmosapjw-quantum/BASS_HE`. The two inherited source files in `research/he_dd_flrw_firstcollision_20261031/src` have original SHA-256 `cccdc3eeb3d4495c9648ce02d202af0f1d97bc85015a278b0696400d5ccb0345` and `ee9ec2e9190639dd12831ef9c75df0d9bec463602a9a90150ff2c4470a2483a9` respectively and are included in ZIP for standalone restoration, but **not added again to GitHub**.

## Principal physical result

Published Appendix A fits of Cyburt et al., *Phys. Rev. D* **67** 103521 (2003), items 6,7,9, are added as competing final nuclear channels `He4(gamma,p)T`, `He4(gamma,n)He3`, and `He4(gamma,np)D`. The `He4(gamma,DD)` channel is **kept on the prior Rice2000 energy-bin model** (8.29 nb at 150–190 MeV, 4.34 nb at 190–250 MeV), not overwritten. The Cyburt Appendix A item 8 DD curve is separately compared solely as a **150–250 MeV high-energy extrapolation**. All four nuclear channels are source equations, but none is a new measurement; the three new ones are NOT shown experimentally validated across the full 150–250 MeV domain.

### At one 220 MeV gamma, z=10,000 (static FLRW, full KN photon-only recycling above 150 MeV)

- `P_alpha_to_pT = 2.2516366510e-05`
- `P_alpha_to_nHe3 = 2.2452499197e-05`
- `P_alpha_to_npD = 1.6996576637e-05`
- `P_alpha_to_DD = 2.4797199996e-08`
- `N_D_born = 2 P_DD + P_npD = 1.7046171037e-05` per injected gamma.
- `P_BH_terminal = 0.6897312778`, `P_exit_gamma_below_150 = 0.3102067319`; latter are **not** deposited heat. `P_BW` is exponentially suppressed at this redshift.
- The `npD` channel contributes about **342.71 times as many born deuterons** as the direct `DD` channel for this particular extrapolated model (and is the dominant modeled D-birth channel). This **is not** a physical prediction robust to missing high-energy nuclear experimental information or coupled electron-positron cascade.

The direct DD 2003 fit extrapolated to 220 MeV is `0.00103991568 nb`; Rice-bin 190–250 MeV surrogate is `4.34 nb`, an extrapolation/model difference factor `4173.41528` (independently Wolfram-checked). **Do not interpret this as contradictory measurements of the same energy-resolved cross section.** Rice 1998 and Rice 2000 are a single SAL campaign and Rice source flux/error concerns remain unresolved.

## Physical equations and frame

Metric signature `(-,+,+,+)`, c, hbar and k_B explicitly retained in original physical FLRW constants. `T_gamma=T0(1+z)`, `n_H=n_b(1-Yp)`, `n_alpha=n_b Yp/4`, `n_e=n_b(1-Yp/2)`. The PR132 original Planck-integrated Breit-Wheeler rate is used unchanged. Cold-target free-electron Klein-Nishina and high-energy unscreened H/He Bethe–Heitler Born rates are also unchanged. For nuclear reaction channel c, source fit (all energies in MeV):

`σ_c(E)=A_c mb × (Q_c/E)^{a_c} × (1-Q_c/E)^{b_c} Θ(E-Q_c)`.

| channel c | A (mb) | Q (MeV) | a | b | provenance |
|---|---:|---:|---:|---:|---|
| (gamma,p)T | 19.5 | 19.813852 | 3.5 | 1 | Cyburt 2003 App A #6 |
| (gamma,n)He3 | 17.1 | 20.577615 | 3.5 | 1 | Cyburt 2003 App A #7 |
| (gamma,np)D | 21.7 | 26.071100 | 4 | 3 | Cyburt 2003 App A #9 |
| (gamma,dd) alternative only | 10.7 | 23.846527 | 10.2 | 3.4 | Cyburt 2003 App A #8 |

`Γ_c(E,z)=c n_alpha(z) σ_c(E)`. In 150 <= E < 250 MeV a fixed-z renewal equation over all free-electron Compton orders is solved with terminal exit channels BW, BH, four photodisintegrations, and a *gamma photon* escaping below 150 MeV. Its normalized differential KN photon kernel `K(E'|E)` is derived from `dσ/dΩ=(r_e^2/2) q^2(q+1/q−sin²θ)`, `q=E'/E=[1+(E/m_ec²)(1-cosθ)]^{-1}`. With p_i=Γ_i/Γ_tot, for each exit observable F, `F(E)=F_direct(E)+p_KN(E)∫K(E'|E)F(E')dE'` for `E'≥150 MeV`; all `E'<150` enter an explicit *photon escape* sink. There is no electron-positron regeneration or Hubble evolution during fast cascade. This uses the quasistatic local approximation only; it is not a full Boltzmann coupled cascade.

**Baryon and charge:** A nucleus A=4, Z=2 produces `P_npD+2P_DD` D, `P_pT` T, `P_nHe3` He3, etc. Exact modeled bookkeeping: `N_p+N_n+2N_D+3N_T+3N_He3=4P_alpha`, `N_p+N_D+N_T+2N_He3=2P_alpha`.

**Projectile-energy ledger:** partition each test gamma's incident energy into terminal BW/BH channel energy, all nuclear outgoing kinetic and nuclear Q, escaped gamma energy, and KN-recoil electron energy. This tests the energy of the *injected test photon* only, ignoring the extra thermal CMB energy absorbed in BW and subsequent medium state; it does not prove a global coupled-thermal-plasma energy ledger or net heat. Nuclear kinetic energy of (gamma,np)D is summed for the *three particles*, not all assigned to the D.

## Evidence and scope

Generated: 12 source-formula-energy rows, 18 local seven-channel hazard rows, 36 static KN-recycled seven-channel rows, and 18 derived Rice-vs-2003-DD comparative rows: **84 model/output rows (66 underlying model evaluations + 18 derived comparisons), 0 new measured rows**, plus three original figures in PNG and SVG.

Executed: 15/15 `unittest` normal, 15/15 Python optimized, inherited PR132 19/19 unchanged, prior local restricted extension 14/14 unchanged. Worst over all 36 model rows: probability residual `8.281e-12`, **projectile** energy relative residual `8.274e-12`, KN kernel quadrature residual `2.070e-11`. Independent Wolfram 220 MeV `npD=2931.33863521385 nb`, 2003-DD `0.00103991568197743 nb`, Rice/2003=4173.4153. Real independent-author blind R6 and C9 **NOT_RUN**, native subagents **NOT_RUN**.

**Missing:** BASS- or REI-owned local 150–250 MeV gamma phase-space emissivity `q_gamma(E,z,x,n)`; verified high-energy source-resolved (gamma,pT), (gamma,nHe3), (gamma,npD) experimental cross sections and covariances; complete BW/BH pair spectra and inverse-Compton/gamma-gamma return; photons from 2.2 to 150 MeV, gamma-e triplet, nonthermal light nuclear network, D-fast ion+nuclear stopping, deposition/escape, true anisotropic Boltzmann equation. No net `heat_rate` or absolute `R_event`.

Central DAG **28/88**, HE Physical **14/18**, canonical delta **0**. New local bounded α-competition micro **1/1 scoped implementation**; not a canonical physical node completion. `kappa=null; R_event=null; heat_rate=null; L4=false; PRODUCTION=HOLD; NO_MERGE=true; NO_FORCE_PUSH=true; AUTO_NEXT_NODE=false`.

## Reproduction

```bash
python -m pip install numpy scipy matplotlib
cd research/he_dd_alpha_competition_20261031
bash REPRODUCE.sh
python verify_manifest.py
```

The ZIP contains the two **unmodified** inherited source files in their original tree locations. The GitHub proposal adds only `research/he_dd_alpha_competition_20261031/*` to parent PR132 HEAD and does not rewrite or merge it. `verify_manifest.py` checks all source/data/evidence files in the restored snapshot and source identity. Stage-specific notes R01–R10/C01–C10 are included in the same archive and mirrored individually where uploads are supported.

## Bibliography and data access

- Cyburt, R. H., Ellis, J., Fields, B. D., and Olive, K. A. (2003), *Updated Nucleosynthesis Constraints on Unstable Relic Particles*, Phys. Rev. D 67, 103521. DOI: https://doi.org/10.1103/PhysRevD.67.103521; text: https://arxiv.org/abs/astro-ph/0211258 (Appendix A items 6–9).
- Rice, B. J., et al. (2000), *Two-deuteron photodisintegration of 4He at Eγ=150–250 MeV*, Phys. Rev. C 61, 064612. DOI https://doi.org/10.1103/PhysRevC.61.064612. Source bins are **150–190** and **190–250 MeV**, not independent monochromatic measurements.
- Jedamzik, K. (2006), Phys. Rev. D 74, 103509. DOI https://doi.org/10.1103/PhysRevD.74.103509, Table I and Appendix D.
- Poulin, V. and Serpico, P. D. (2015), Phys. Rev. D 91, 103007. DOI https://doi.org/10.1103/PhysRevD.91.103007, Eqs (2)–(11).
- Depta, P. F., Hufnagel, M., Schmidt-Hoberg, K. (2020/2021), *ACROPOLIS* https://arxiv.org/abs/2011.06518; code https://github.com/hep-mh/acropolis (GPL3). **Code consulted as a reference, not installed or executed** in this work. Native sandbox DNS cannot resolve github.com, and there is no certified full cascade run.
- High-energy exclusive photoabsorption raw data: IAEA EXFOR https://www-nds.iaea.org/exfor/exfor.htm or JCPRG https://nds.sci.hokudai.ac.jp/exfor/. Query target `4-He`, projectile `g`, emission `p+t`, `n+3He`, `n+p+d`, energy 150–250 MeV; require cross section **and** covariance/acceptance/source dataset identity. Original laboratory source rather than low-energy fit extrapolation is needed for a canonical promotion.
