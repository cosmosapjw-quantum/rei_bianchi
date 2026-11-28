# BASS_HE: PR132 / cosmological first-collision transfer Green kernel (2026-10-31)

Parent: immutable Draft PR131 at `cb6cdb0165782ee3e164b33055e4b7deeaa5156e`.
This calculation delivers **41 new physically computed but model-conditional rows** and 4 scientific plots, not new measurements or a fully normalized cosmological source history. It is not final D deposition, not the full electromagnetic cascade, and is not suitable for production.

## Results and provenance

- `data/CROSS_SECTIONS_MODEL_5.csv`: 5 energy rows of QED free-e KN, unscreened high-energy bare-ion BH on H & He, and Rice2000 fitted-bin piecewise source model. Not measured per-energy sigma.
- `data/LOCAL_FOUR_CHANNEL_HAZARDS_18.csv`: 18 local cosmic FLRW rate rows (6 injection z x 3 E) and H(z); 4 channels: background-photon Breit-Wheeler, electron Klein-Nishina, bare-ion Bethe-Heitler, helium exclusive dd.
- `data/COSMIC_FIRST_COLLISION_18.csv`: 18 **integrated, energy-redshifting** first-collision Green-function rows, with P_BW, P_KN, P_BH, P_dd, surviving-at-150 vs unresolved tail, two daughters/event and first-event birth K per unit injected photon.
- 4 original PNG + 4 SVG figures plot probabilities versus z at injection energies 170/220/249 MeV.
- Exact conserved physics background source `src/physics_pr131.py` copied unchanged from PR131: SHA256 `cccdc3eeb3d4495c9648ce02d202af0f1d97bc85015a278b0696400d5ccb0345`. No re-analysis of prior original studies.
- Source Rice1998 `Rice_1998(2).pdf` 139 pages exact SHA256 `87fe939659151b09a1653467f1ac2098d971048fa4cf3611b447fce8cc976336`. Same source as PR130, NOT added to public Git or public source ZIP. 1998/2000 are same SAL experiment, no double-counting. Asbury1965, CEA1966 original sources remain prior PR129.

## Physical model and equations

Metric (-,+,+,+). CMB Planck blackbody, homogeneous fully-ionized H/He Planck/PDG reference flat FLRW (NOT BASS-native anisotropy), local comoving target alpha rest, T_gamma=T0(1+z). Photon initial E_i (MeV), injected at z_i, normalization **exactly one photon per scenario**; source amplitude, physical injection rate and angular anisotropy are not assumed. Cosmological free propagation redshifts E(u)=E_i exp(-u), u=ln[(1+z_i)/(1+z)], and dt/du=1/H(z).

`Gamma_j(E,z)=c n_target(z) sigma_j(E)` for KN e, BH ion H+He, Rice dd; `Gamma_BW` is exact thermal CMB angular/energy convolution from PR131 (Gould & Schréder 1967). Total sigma KN is exact tree-level on an e at rest. BH uses *unscreened high-energy point-nucleus Born* `alpha Z^2 r_e^2 [(28/9)ln(2E/(m_e c^2)) - 218/27]`, H/He Z=1/2 only. This is not neutral atomic XCOM and not NLO medium cross section.

At first collision `Gamma_total=Gamma_BW+Gamma_KN+Gamma_BH+Gamma_dd`, `tau(u)=integral_0^u (Gamma_total/H)du`, survival `S=exp(-tau)`. The probability of the *first* collision being channel j: `P_j=integral_0^tau_end exp(-tau)Gamma_j/Gamma_total d tau`; integrated numerically in optical-depth variable, not stiff time t. At 150 MeV the modeled DD excitation interval ends. If tau reaches 65 first, the unresolved probability is at most exp(-65) ~ 5.90e-29; no unsupported extrapolation below E=150.

`N_D_first per source photon=2 P_dd`. Per injected photon *born* total daughter kinetic energy is `integral exp(-tau) [Gamma_dd/Gamma_total] [E_gamma(tau)-Q] d tau`, with `Q=(2m_D-m_alpha)c^2`, **not deposited heat**. Example E_i=220 MeV,z_i=1e4: P_KN=0.3363152365, P_BH=0.6636691980, P_dd=2.3840471609e-8, reach-150 survival=1.55417246e-5; born K_D pair per injected gamma=4.52050839e-6 MeV. E_i=220MeV,z_i=1e6: P_dd=5.04253980e-17, first collision dominated by BW.

## Claim boundary

1. **Measured**: zero new experiment data; Rice2000 is input *bin-integrated fitted* total with explicit piecewise-constant pointwise SURROGATE, not an excitation-function measurement.
2. **Derived/implementation-verified**: 41 model-conditional numbers, first-collision identity, 4 plots, Python 19/19 PASS (python -m unittest discover -s tests -v); Wolfram independent KN/BH checked at E=220MeV; KN total versus differential-angle quadrature relative <2.1e-11; u-coordinate independent integration low-z P_dd relative <=1.3e-6; rtol tightening P_dd rel <=1e-8 in checked cases.
3. **Unresolved**: Other nuclear photodisintegration (gamma+He->pT/nHe3/...); photon-on-e triplet pair; electron thermal velocity; Compton scattered photon redistribution; regenerated inverse Compton / secondary photons; full BH cascade; D nuclear reactions, ion drag, heat/escape, energy-dependent *measured* sigma and covariance, non-FLRW background, actual n_gamma source emissivity. Therefore P_dd is not a global branching ratio, a strict full-cascade upper bound, or a measured cosmic event fraction.
4. **Governance**: Central 28/88, HE physical 14/18, delta 0, source-model micro 2/2 scoped; R_event=null, heat_rate=null, kappa=null, L4=false, PRODUCTION=HOLD, NO_MERGE and NO_FORCE_PUSH.

## Reproduce

```bash
python -m pip install -r requirements.txt
bash REPRODUCE.sh
```

This reconstructs all CSV/JSON, 4 PNG+SVG plots, executes tests (19/19) and compiles Python. Output archive and dual backups are separate from public Git. See `notes/THEORY_KO.md`, `notes/BLIND_REFEREE_KO.md` and `notes/HANDOFF_NEXT_THREAD_KO.md`.

## Original published sources

- Gould, R. J. & Schréder, G. P. (1967), *Physical Review* 155, 1404. https://doi.org/10.1103/PhysRev.155.1404
- Klein & Nishina (1929); NIST NBS29 total Compton, Eq. (2-8): https://srd.nist.gov/NSRDS/NSRDS-NBS29.pdf
- Bethe & Heitler (1934); high-energy bare nucleus asymptotic Racah form: see [Geant4 electromagnetic gamma conversion](https://geant4.web.cern.ch/documentation/pipelines/master/prm_html/PhysicsReferenceManual/electromagnetic/gamma_incident/gammaconversion/conv.html)
- Rice et al. (2000), *Phys. Rev. C* 61, 064612. https://doi.org/10.1103/PhysRevC.61.064612
- Planck Collaboration (2020), *A&A* 641 A6. https://doi.org/10.1051/0004-6361/201833910
- Poulin & Serpico (2015), *Phys. Rev. D* 91 103007. https://doi.org/10.1103/PhysRevD.91.103007
- Jedamzik (2006), *Phys. Rev. D* 74 103509. https://doi.org/10.1103/PhysRevD.74.103509
