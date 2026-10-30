# REI F4 | 원본 BASS193 Li I 1s 사건의 조건부 2E1/M1 복사 용량

2026-10-30, 이론 계산 R1–R10 범위. **물리 노드의 일부 구성만 완료**했으며, full REI thermal port, source-qualified spin yields, exact two-photon differential shape, gas reabsorption은 unresolved이다.

## 1. Source identity and scope

Parent REI PR #279 HEAD `46d7d3192c32a069ef2b6d9aa5b7202e9c2bfa78`, parent PR #277 `b9610ccefd8ddddab89c98ccad09152b49ba6762`, native BASS AtomicNetwork owner `cc602e209e7deeb511ab2a1f3b2268d55206c43c`. Immutable source ZIP SHA256 `6e50586131ab6f8f76b72ee8c7125dfd3225211d528609c862e01a305a0ab6d3`, nested PR277 SHA256 `6a5794996b0fe0473558bc07c866f2f3f0315cb72aef9b284e805cd40ba897a8`. Same saved 193 epochs, 71 photon bins and 8,492 Li6I/Li7I 1s event rows; new IVPs zero.

Each original native single-K photoevent rate per baryon and second is

\[r_{ib}(t)=Y_i(t)\sigma_{i,1s}(E_b)\Phi_b(t),\qquad [r]={\rm baryon^{-1}s^{-1}},\]

where photon flux and photo cross section are both original source-owned. No split of the original source `sigma` into invented fine-structure cross sections.

## 2. Source measurements, NOT guessed radiative rates

NIST Li II `1s2s ^3S1` is at `476034.24 cm^-1` (`59.02072367315768 eV`), `1s2s ^1S0` at `491373.58 cm^-1` (`60.92255944755200 eV`). These are below the Li III continuum; follow-up field-free Auger from these residual **bound** states cannot occur. This statement does not prohibit direct double photoionization, shake-off or other doubly-excited Li I continua. The original first active bin at 65.6324218962602 eV only admits the triplet; remaining active bins allow triplet and singlet. NIST reference: https://physics.nist.gov/PhysRefData/Handbook/Tables/lithiumtable6_a.htm

Li II singlet `1s2s ^1S0` decays by two E1 photons and measured lifetime is `503±26 microseconds` (Prior & Shugart, PRL 27, 902 (1971), https://doi.org/10.1103/PhysRevLett.27.902). Li II triplet `1s2s ^3S1` decays by M1 single photon, measured `52.2±5.0 s` (Saghiri et al., PRA 60 R3350 (1999), https://doi.org/10.1103/PhysRevA.60.R3350). Separate experimental check Knight & Prior, PRA 21, 179 (1980): `58.6±12.9 s` 95% CI, https://doi.org/10.1103/PhysRevA.21.179. Measurements do not calibrate isotope-specific spin branching. Numerically, A1~1988.07157 s^-1 and A3~0.0191570881 s^-1, but rates are for an **isolated radiative level** in vacuum, not full gas cascade probabilities.

## 3. Radiative count and energy map

Let `p_ib` be the unknown probability that a source-counted *single-K* event produces the triplet, and `1-p_ib` the singlet for bins with both channels allowed. At the lowest active bin `p_ib=1` follows from energy threshold (not statistical spin assumptions). The outgoing bound-state excitation and prompt electron kinetic energy obey

\[ E_b=I_{\rm LiI}+K_{ib,c}+E_c,\qquad
E_{3S}=59.020723673\,\mathrm{eV},\;E_{1S}=60.922559448\,\mathrm{eV}. \]

Under collisionless *complete* radiative decay, triplet emits one M1 photon at `E3S`, singlet emits a two-photon pair with total energy `E1S`. The pair has unknown energy-sharing distribution `g(y)`, `y∈(0,1)`; individual photons carry `y E1S` and `(1-y) E1S`. Consequently

\[\dot N_\gamma^{vac}(t)=\sum_{ib} r_{ib}(2-p_{ib}),\qquad \dot Q_\gamma^{vac}(t)=\sum_{ib}r_{ib}[p_{ib}E_{3S}+(1-p_{ib})E_{1S}].\]

The photon energy is **radiation**, not `photo.heat_erg_per_absorber_s`. Production rates in a real gas also require radiative versus collisional-quenching yields. With unknown `p` and `g`, only conditional envelopes are claimable.

For ionization threshold `chi`, let `N_chi(e1,e2)=1[e1>chi]+1[e2>chi]`, `e1+e2=E1S` with both energies nonnegative. Its sharp (achievable or limiting) bounds are:

- `E1S≤chi`: `(min,max)=(0,0)`.
- `chi<E1S≤2chi`: `(0,1)`.
- `E1S>2chi`: `(1,2)`.

Triplet M1 yields `1[E3S>chi]`. Unknown spin branching extends per-bin bounds to the min/max over the permitted states. The three thresholds (NIST ASD eV) are `H I:13.598434599702`, `He I:24.587389011`, `He II:54.417765486`. Both H I and He I: each event yields 1..2 potentially ionizing photons. For He II: forced-triplet first-active-bin event yields exactly 1, all other events yield 0..1. Total 2E1 sum exceeds the He II threshold but is less than twice this threshold; a He II-capable 2E1 photon requires its partner energy below `60.922559447552−54.417765486=6.504793961552 eV`. No probability is assigned to this narrow kinematic support.

For each target `j` the source conditional count power is

\[\dot N_{\gamma,j}^{\mathrm{cap},\min/\max}(t) = \sum_{ib} r_{ib}(t)\,N^{\min/\max}_{j,ib}.\]

These values are potential **photon counts above an atomic ionization threshold**, NOT actual number of photoabsorptions, electron-ionizations, REI heat, or cosmological optical depth. Without radiative branching, a real medium has no positive unconditional photon-emission lower bound.

## 4. Measured lifetime / Hubble ratio

At every original frozen epoch one may calculate `H(z) tau_c` using the saved, source-owned `H`. Maximum over 193 is `6.177923233737762e-15` (triplet nominal), `5.953056296111291e-20` (singlet nominal); including reported additive uncertainty maxima: `6.769678332754789e-15` and `6.260768947600145e-20`. Thus atomic vacuum decay times are tiny compared with the Hubble time *for these saved epochs*. This does not independently establish gas optical depths, collision rates, thermalization times or the adiabaticity of a rapidly varying radiation pulse. A future causal radiative kernel would have `G_c(t,t')=Theta(t-t') exp[-(t-t')/tau_c]/tau_c` if isolated decay and source history were justified. This kernel is NOT propagated as a new IVP in this run.

## 5. Reproduced numerical saved-grid diagnostics (NOT NEW IVP)

Original Li single-K events `3.442655615303716e-11 /baryon`, first-bin forced-triplet events `4.27548054648883e-12 /baryon`. Possible number of radiative photons `3.442655615303716e-11` to `6.457763175958553e-11 /baryon`. HI and HeI threshold-capable counts have same range. HeII threshold-capable counts `4.27548054648883e-12` to `3.442655615303716e-11 /baryon`. Source primary electron energy and excitation bounds from PR279 are unchanged; conditional radiation energy lies `[2.031880257726855e-9, 2.089222651951853e-9] eV/baryon`. Source absorbed is `2.95642365279964e-9 eV/baryon`, valence ionization `1.856181790709665e-10 eV/baryon`, kinetic e− paired bounds `[6.81582821776819e-10,7.389252160018209e-10]`; lower radiation energy matches upper prompt kinetic energy and conversely. Source saved `dx/dt=H` and existing Simpson integration only. Full 8492-row and 193-row CSV are in `results/`.

## 6. Obligations and claim gate

- **Established/literature-supported:** NIST bound levels, source-measured 2E1/M1 lifetimes, physical atom/ionization thresholds, source owner identities.
- **Derived and numerically checked:** sharp threshold photon count bounds and conservation identities; 193-epoch source-rate aggregation; Wolfram exact energy residuals zero and threshold inequalities true.
- **Not admitted:** `p_ib` spin yields, double photoionization, full differential two-photon spectrum, collisional-quenching or opacity, secondary-electron energy deposition, BASS↔REI17 whole chemistry and clock, actual REI `IgmPhotoInput::heat_erg_per_absorber_s`, observational tau/CMB. Original 40/40 and 17/17 remain historical scoped evidence. New targeted 28/28 and clean restore are recorded separately.

Working DAG **33/88**, central **28/88**, F4 fast DAG **4/7**, canonical physical increment **0**, auxiliary radiative-capacity node **1/1 scoped only**, full F4 still PARTIAL and L4 false. `NO_MORE_IVPS`, `NO_MERGE`, `NO_FORCE_PUSH` remain true; `AUTO_NEXT_NODE=false`; `PRODUCTION=HOLD`. R6/C9 genuinely different-author reviewers NOT_RUN; available native subagent tools NOT_RUN.