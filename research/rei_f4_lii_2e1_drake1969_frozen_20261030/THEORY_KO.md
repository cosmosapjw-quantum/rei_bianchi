# REI F4 | Li II 2E1 실제 원전 분광률과 원본 BASS193 정적 광흡수

Date 2026-10-30. Parent REI PR282 (`6739f37460caf802f045dcd64e1a3b225e54c4dc`), BASS AtomicNetwork original source owner `cc602e209e7deeb511ab2a1f3b2268d55206c43c`. Node `REI_F4_LII_2E1_SOURCE_SPECTRUM_FROZEN_ABSORPTION_20261030`; scoped auxiliary science, not canonical REI full chemistry, CMB, tau or physical gas heating.

## 1. 원전 및 한계

G.W.F. Drake, G.A. Victor, A. Dalgarno, *Two-Photon Decay of the Singlet and Triplet Metastable States of Helium-like Ions*, Physical Review **180**, 25 (1969), doi:10.1103/PhysRev.180.25, Table II gives a **Li II** singlet 2E1 differential probability versus `y` in `[0,1/2]`, step `1/40`. We transcribed the 21 **Li II column** values (s^-1 per unit y) into `results/LI_2E1_DRAKE_1969_TABLE_21.csv`: `[0,379,1110,1810,2420,2940,3380,3740,4060,4320,4540,4730,4880,5020,5130,5220,5290,5350,5380,5410,5420]`. Available scan: https://uwindsor.scholaris.ca/bitstreams/0cd0ebf7-0164-4c22-9aaa-71af11cfea5f/download. Some scanned extracted glyphs were ambiguous (`V` to `7`, `O` to `0`), **direct visual page readback was blocked**. Accordingly source-translation certainty is **partial**, not an authoritative bit-exact Table II copy. It is checked against the independent Li II rate in Derevianko and Johnson, PRA **56** 1288 (1997), doi:10.1103/PhysRevA.56.1288. The table's piecewise-linear integrated rate is **1945.475 s^-1**, 0.2822165% above the latter's 1940 s^-1. We use its **shape**, with the independent experimentally measured 503±26 μs lifetime only for interpretation, not imposed on this tabular interpolant.

Li II singlet-to-ground transition energy from NIST levels (PR279): `E_s=60.922559447552 eV`, triplet M1 `E_t=59.020723673157676 eV`. Ionization threshold energies `[H I:13.598434599702, He I:24.587389011, He II:54.417765486] eV`.

## 2. 2E1 photon-pair measure and exact integral

Define `A(y)` as the linearly interpolated 1969 tabulated rate, `W = ∫_0^{1/2} A(y)dy`, `p(y)=A(y)/W`; this is the **joint pair** probability density for lower-energy fraction `y`, **not** the probability density for an individually tagged photon over the whole `[0,1]`. Each emitted pair carries photons of energies `E_1=y E_s`, `E_2=(1-y)E_s` and `E_1+E_2=E_s`. For absorber ionization threshold `χ`, the source probability-weighted **number** of potentially ionizing photons per singlet pair is

`N_χ = ∫_0^{1/2} p(y)[1_{E_s y≥χ}+1_{E_s(1−y)≥χ}] dy`.

The integral is evaluated **analytically between the 21 table vertices**. For `0<χ<E_s/2`, `N_χ = 1 + P(y>χ/E_s)`; for `E_s/2<χ<E_s`, `N_χ=P(y<1−χ/E_s)`; equality is a measure-zero endpoint. Independently evaluated in Wolfram Language on the exact piecewise-linear Table II:

- `N_HI = 1.7212750025558112 photons / singlet pair`;
- `N_HeI = 1.2664637647251857 photons / singlet pair`;
- `N_HeII = 0.06661043779514719 photons / singlet pair`.

Thus the high-energy 2E1 photon is **not** automatically above the He II threshold, and the pair photons cannot both ionize He II. No unverified singlet/triplet *photoionization yield* was assumed.

## 3. Conditional emission from original BASS21 event source

Use original native `K(z)=Σ_{6,7Li; 1s,bins} Y_i σ_{i,b}(E_b) Φ_b` in `baryon^-1 s^-1` along exactly 193 originally saved BASS21 epochs, and the triplet-forced subset `K_T(z)` determined by first BASS photon bin lying below `E_s + I(Li I)`. Let `K_S^max(z)=K(z)−K_T(z)≥0`. No unknown spin yield `f_S` is set. Assuming **complete free-space radiative decay** (itself conditional), the number of potentially ionizing photons for each source event is bounded by both the single 59.02 eV M1 photon and the two-photon `N_χ`. Thus:

`K_χ^min = K_T + min(1,N_χ)K_S^max`, `K_χ^max = K_T + max(1,N_χ)K_S^max`.

Time-integration here means frozen-output **postprocessing** `∫ R(x)/H(x) dx` over original `x=ln a` saved grid using Simpson, no new IVP and no physical photon propagation. Reported integrated source events 3.4426556153037163e-11 / baryon, triplet forced 4.27548054648883e-12 / baryon. Results (conditional photons/baryon):

| Absorber threshold | Minimum | Maximum |
|---|---:|---:|
| H I | 3.4426556153037163e-11 | 5.6173773288210785e-11 |
| He I | 3.4426556153037163e-11 | 4.2460725269671736e-11 |
| He II | 6.2838568926355965e-12 | 3.4426556153037163e-11 |

These source counts are not gas ionizations, not photon survival or transferred heat.

## 4. Source-owned frozen short-distance transfer diagnostic

We also compute a **separately labelled conditional model** with every non-triplet-forced event producing a 2E1 singlet pair (`f_S=1`). This is a feasible upper/saturated **scenario**, **not** a bound on every derived absorbed-photon energy or channel fraction. At each original BASS epoch `z`, evaluate the actual archived native 21-ion Verner photoionization cross sections at each photon energy `E`:

`κ(z,E)=n_b(z) Σ_{i=1}^{21} Y_i(z) σ_i(E)` in proper `m^-1`, `τ_frozen(z,E)= c κ(z,E)/H(z)`.

Fixing the entire BASS epoch gas composition during a hypothetical **one proper Hubble length**, the first-photoabsorption probability is `P_abs(z,E)=1−exp[−τ_frozen(z,E)]` and the first-absorber channel share is `P_i= P_abs n_bY_iσ_i/κ` (zero for κ=0). All photon production in the *actual universe* would require an independent radiative transfer equation and boundary/initial conditions: the frozen diagnostic is not that evolution.

The expected **number per singlet 2E1 pair** absorbed in this thought experiment is

`A(z)=∫_0^{1/2}p(y)[P_abs(z,E_s y)+P_abs(z,E_s(1−y))]dy`.

Analogous integrals weighting `E−I_i` and `I_i` yield source-injected primary photoelectron energy and chemical ionization binding energy; the unabsorbed contribution weighs `(1−P_abs)E`. The channel-specific first-event rate is `K_S^max(z) ∫ p(y)[P_i(E_s y)+P_i(E_s(1−y))]dy`.

**Conservation by construction** at fixed `z` and for each `E`: `E = Σ_i P_i(E)[(E−I_i)+I_i] + (1−P_abs(E))E`; therefore per pair `E_s=E_{e,primary}+E_{ion,binding}+E_{photon,escape}`. `E_e,primary` is **not heat**. This model supplies a static diagnostic only; physical thermal deposition and secondary ionization remain UNBOUND.

## 5. Numeric form, accuracy and claim boundary

Use the 21 native BASS ionic threshold energies, all 21 Drake table vertices, and external named thresholds as breakpoints for composite Gauss–Legendre quadrature of 4/8/16 orders. Failing to split **all** native thresholds produced a detected ~2e-5 relative initial quadrature discrepancy; fixed without changing source or tolerance. The source probabilities `N_χ` are evaluated by exact piecewise-linear cumulative arithmetic and independently reproduced in Wolfram. The 193 original row densities `Y,n_b,H` and BASS `photo_cross_sections` are called directly from the source-embedded BASS owner code, cross-check original PR282 M1 opacity and PR280 Li1s 8,492-row source event rates. The saved epoch source grid and all generated CSV/plots are preserved unrounded; original binary ZIPs are byte-locked SHA256.

**Status:** `literature-supported` 1969 Li II table + rate, **source OCR transcription only partially visually verified**; `derived` pair measure/threshold probabilities; `numerically_checked` exact source event/projection and frozen conditional transfer; `implementation-verified` targeted tests; **unresolved** spin/charge branching, 2E1 time/angular correlations, proper cosmological transport, actual secondary electron deposition, common REI17/BASS21 chemistry and clock, observational τ/CMB. `F4=PARTIAL`, `L4_ready=false`, original canonical DAG working33/88 central28/88 F4-fast4/7 unchanged, physical delta0, this auxiliary node 1/1 scoped. No new IVPs, no merge/force/production.
