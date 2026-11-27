# BASS_HE | PR131 physical opacity + electron drag | handoff

```makefile
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
READ_LIVE_HEAD_FIRST=true
PARENT_PR=130
IMMUTABLE_PARENT_HEAD=39177b446df601e3103cdb1e4d39ac51ad31086a
CURRENT_UNIT=BBN_PLANCK_CMB_BREIT_WHEELER_OPACITY_X_FASTD_ELECTRON_DRAG
NEW_MICRO=2/2_SOURCE_BASED_MODEL_CONDITIONAL
CENTRAL_DAG=28/88
HE_PHYSICAL_DAG=14/18
CANONICAL_PHYSICAL_DELTA=0
R_EVENT=null
HEAT_RATE=null
KAPPA=null
L4=false
PRODUCTION=HOLD
AUTO_NEXT_NODE=false
NO_MERGE=true
NO_FORCE_PUSH=true
NATIVE_SUBAGENT=NOT_RUN
DISTINCT_AUTHOR_R06=NOT_RUN
DISTINCT_AUTHOR_C09=NOT_RUN
NEXT_OBJECTIVE=REAL_HE_REST_150_250_MEV_PHOTON_INJECTION_FROM_BASS_SOURCE_AND_BPS_JEDAMZIK_FASTD_NUCLEAR_TRANSPORT
```

## Actual science now

- 55 physical derived `gamma-gamma_CMB->e+e-` opacity cells for E=150,170,190,220,250 MeV across 11 actual-source-based Planck/PDG FLRW redshifts z=1e4 to 2e7; no MeV emission model.
- 55 weakly-coupled fully ionized H/He Maxwellian-electron `D_fast` drag cells E_D=50,75,100,125,150 MeV. Leading-log electron loss, not complete plasma stopping or heat.
- 22 first-interaction `He4(gamma,dd)` vs `gamma-gamma` cells using Rice2000 two-bin *model* sigma 8.29/4.34 nb; real published data but pointwise sigma energy dependence not observed. 15 exact numerical `Gamma_gg/H` crossing redshifts and six nominal two-body daughter energy-pair examples. 4 plots PNG+SVG. All rows reproduce with `bash REPRODUCE.sh`.
- At z=1e6 and Eγ=220 MeV: Γgg=39714.748 s^-1, Γdd=2.002632e-12 s^-1, P(first dd of two channels)=5.04254e-17; no absolute cosmic event rate due no source normalization.
- At z=1e6, Kd=100 MeV, electron-only dynamic-screening Coulomb rate |dK/dt|=0.241438 MeV/s, instantaneous loss/Hubble=8.697e-6. NOT heat.
- Independent Wolfram BW beta0.7 sigma/sigmaT=0.255636746421, Eγ220, mu0.5 gives K+=(114.9484964713), K-=(81.2050253287) MeV.

## Source identity and unresolved blockers

User Rice_1998(2).pdf SHA256 `87fe939659151b09a1653467f1ac2098d971048fa4cf3611b447fce8cc976336` = earlier PR130 Rice 139-page **partial** original. Table5.2 from PR127 separately. Do not request again. Original detailed experiment high flux ratio (`1.546` printed vs `1.2575051` reconstructed) and low-bin last statistical sigma (`0.122` printed vs `0.14042136` direct) are still CONCERN and not retrocorrected.

To progress actual canonical HE physical DAG, require: target-epoch nonthermal `f_gamma^(alpha)(E,Omega,x,t)` with direct injection/transport and observer frame from BASS, true individual energy-dependent exclusive He-dd cross section covariance or model family, real `n_alpha,U_alpha`, complete BPS/Jedamzik ion/electron/nuclear/escape/secondary energy deposition. An established CMB is the *target* for gamma-gamma pair absorption, not a source of injected MeV photons. Modelled fast-D electron drag is a controlled input but does not itself produce an event heat rate.

Open access: Gould & Schreder 1967 https://doi.org/10.1103/PhysRev.155.1404 ; PDG constants https://pdg.lbl.gov/2025/reviews/rpp2024-rev-astrophysical-constants.pdf ; BPS https://arxiv.org/abs/physics/0501084 ; Jedamzik https://arxiv.org/abs/hep-ph/0604251 ; Poulin & Serpico https://arxiv.org/abs/1502.01250 ; Rice 1998 complete online PDF https://nucldata.tunl.duke.edu/nucldata/Theses/PhD/Rice_1998.pdf if needed (TUNL, public access; local upload 139 pages). These references do not require reconstructing private experiment code.

`R_event=null;heat_rate=null;kappa=null;L4=false;PRODUCTION=HOLD` remains strict; do not read these output tables as cosmic gamma injection normalization, complete optical depth, or thermal heat.
