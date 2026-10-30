# REI F4 | Li I 1s 실제 준위와 원본 BASS193 사건 장부

**Date** 2026-10-30. **Scope** `REI_BASS_LI1S_AUGER_FLUORESCENCE_AND_THERMAL_PORT_SOURCE_BIND`의 운동학적·원본 사건율 부분만 검증했다. Auger/fluorescence yield, branching 확률, 비즉시 열화 kernel, REI 열원 binding은 아직 source-qualified되지 않았다. 따라서 전체 노드는 `PARTIAL`, canonical DAG 증분은 `0`이다.

## 원본과 데이터 계보

- Immutable PR277: `b9610ccefd8ddddab89c98ccad09152b49ba6762`, parent PR276 `970175ffce1e1139b911a1f45bee9271a69153b9`.
- BASS21 owner: `cc602e209e7deeb511ab2a1f3b2268d55206c43c`, network `baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80`.
- Source-inclusive original PR277 ZIP: `source/PR277_FULL.zip`, 4,888,454 bytes, SHA256 `6a5794996b0fe0473558bc07c866f2f3f0315cb72aef9b284e805cd40ba897a8`.
- Saved trajectory SHA256 `37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086`, original 193 x-grid epochs with saved `H`, `Y`, `UV`, `n_b`, `T`. No new IVP.
- Original network's Li6I (index13) and Li7I (index17) 1s partial cross sections and source photon flux across 71 bins. **22 bins active**; 193×2×22 = **8492 direct original source-grid event rows**. Native `photo_s` H1I/He4I/He4II projected in 193×3=579 shape-only potential rows.
- REI thermal code `rust/rei_microphysics/src/igm_thermal.rs` blob `0648618d9822e169e9672ac3c556f86595c3b0b6` at exact PR277 head. `IgmPhotoInput::heat_erg_per_absorber_s[3]` is actual deposited heat per H I/He I/He II absorber, *not* primary electron energy injected.

## 물리적 준위와 허용 채널

NIST Li II levels in 1/cm above ground: `1s2s ^3S1 = 476034.24`, `1s2s ^1S0 = 491373.58`. Exact SI conversion `hc/(e·cm)` and Li I threshold `5.391714996 eV` give

```
I(Li I)                    = 5.391714996 eV
Li II 1s2s 3S excitation   = 59.0207236731576776 eV
Li II 1s2s 1S excitation   = 60.9225594475520037 eV
Li I single-K 3S threshold = 64.4124386691576776 eV
Li I single-K 1S threshold = 66.3142744435520037 eV
I(Li II)                   = 75.6400970 eV
Li I direct double threshold = I(Li I)+I(Li II) = 81.031811996 eV
```

A simple direct photo-ejection of a neutral Li I 1s electron leaves two-electron Li II(1s2s). Both singlet and triplet levels lie **below Li III + free e** by 14.717538 and 16.619373 eV respectively. Therefore *subsequent field-free Auger autoionization of these two residual levels* is kinematically forbidden. This does **not** rule out direct two-electron photo-ejection, multiply excited resonances, two-electron shake-off, impact ionization, or externally driven processes. It is incorrect to use Auger yields for three-electron Li-like **1s2s²** states as yields for two-electron He-like Li II **1s2s**.

After decay or collision, initial bound excitation may become 2-photon emission (singlet) or weak forbidden radiation/other channels (triplet), whose emitted photons may escape, re-absorb or be delayed. No prompt-fluorescence probability is asserted. Spin branching and cascade lifetimes are **UNBOUND**.

BASS approximates Li 1s ionization at `64.39 eV` with valence threshold `5.392 eV`, so its unresolved core term is fixed to `58.998 eV` per Li 1s event. This is not identical to either NIST excitation. DO NOT add the difference to gas heating; instead regard it as a modeling energy-allocation mismatch requiring an explicit source-model replacement if physical cascade is later installed.

## Original source bin branches

Let original source `Y_i(z)=n_i/n_b`, `Phi_b(z)` [photons/m²/s in integrated bin], `sigma_i,1s(E_b)` [m²]. For Li6I and Li7I,

\[
 r_{ib}(z)=Y_i(z)\sigma_{i,1s}(E_b)\Phi_b(z)
 \quad [\mathrm{events\ baryon^{-1}s^{-1}}].
\]

For a conditional final state `c∈{3S,1S}`, define energy allocation per counted single-K event:

\[
 E_b=I_{\mathrm{LiI}}+E_{\mathrm{exc},c}+K_{e,b,c},\qquad K_{e,b,c}\ge0.
\]

For each bin define allowed set `A_b={3S if E_b≥64.4124 eV, 1S if E_b≥66.3143 eV}`. Since `p_{b,3S},p_{b,1S}` are **unknown**, only bounds are admissible: `K_min=E-I-E_exc,max`, `K_max=E-I-E_exc,min`; excitation bounds reverse. The first BASS active 1s bin at **65.6324218962602 eV** admits **only triplet**. There is **one** triplet-only active bin. The original photo-rate has not been repartitioned into invented state-resolved cross sections.

Source-saved integrated quantities (Simpson postprocessing only with the existing `dx/dt=H` clock):

| Diagnostic | eV/baryon or events/baryon |
|---|---:|
| Original Li single-K events | `3.4426556153037163e-11` events |
| Triplet-only kinematic events | `4.27548054648883e-12` events (12.4191%) |
| Original **single-K** events whose photon has enough energy for a *separate* direct double process | `1.6077289839884362e-11` events (46.7003%); **not** double photoionization events |
| Absorbed | `2.9564236527996403e-09` eV |
| NIST valence ionization baseline | `1.8561817907096648e-10` eV |
| Conditional NIST bound-excitation energy | `[2.031880257726855e-09, 2.089222651951853e-09]` eV |
| Conditional prompt primary-e energy | `[6.81582821776819e-10, 7.389252160018209e-10]` eV |
| Original BASS unresolved-core energy | `2.0310979599168842e-09` eV |
| Original BASS primary-electron energy | `7.39697702105577e-10` eV |

Both extremal allocations conserve exactly the same original Li1s absorbed photon energy. These quantities are **injected/potential** energy, not automatically deposited gas heat. Li1s primary energy bound is less than `2.61e-11` of original all-species primary energy exposure `28.3186248272491 eV/baryon`. That extreme smallness is source-trajectory specific, not a general Li atomic-physics insignificance theorem.

## 비즉시 열화 구조 및 REI port 경계

Let `S_e(E,t)` denote an **independently source-qualified** electron kinetic-energy injection distribution per baryon per second per eV, with required sources: BASS primary spectrum, state-resolved Li shell branching and additional Auger/shake-off/double-ionization channels if present. Let `K_heat(t,t';E,X)` [s^-1] be a causal fractional-energy deposition response conditioned on the whole gas/radiation history `X`, allowing energy exchange into secondary ionization, excitation, escaping photons, thermal electrons and cosmological dilution. Then a formal delayed heat source per baryon is

\[
 {\dot{Q}_{\rm heat}(t)\over n_b(t)}
 = {\rm eV\to erg}\int_{-\infty}^{t}dt'\int dE\;E S_e(E,t') K_{\rm heat}(t,t';E,X),\qquad K_{\rm heat}=0\;(t<t').
\]

This formal convolution assumes comoving baryon-number conservation so that injection per baryon can be transported; additional expansion redshifting and escape belong to the kernel/kinetic equation. It is **not** a calibrated deposition operator. In general thermal/ionization/excitation fractions depend on primary-electron energy and gas ionization; e.g. Shull & van Steenberg (1985), Furlanetto & Stoever (2010). Setting `K_heat=δ(t-t')`, `f_heat=1` would be unjustified and is **not done**.

REI native proper-time `IgmPhotoInput` requires gas heat power *per H I, He I, He II absorber* and a gamma matching each absorber. Original BASS `photo_s` and energy-weighted ejection moment for those three species are recorded as `HHE_193x3_SOURCE_ELECTRON_INPUT_NOT_HEAT.csv` to show the **shape** of an input; they are not deposited heat and are **not provided to REI**. The original REI17 and BASS21 have different isotope inventory, rate coefficients, photon-bath owner, and clock. No common-source owner exists yet to derive a consistent `REI heat_erg_per_absorber_s`. Thus `photo.heat_erg_per_absorber_s` remains `UNBOUND` and `F4/L4/PRODUCTION` stay on hold.

## Test evidence and validity

Local source-owner calculation generated 8492 Li isotope-bin rows, 193 epoch summaries and 579 HHe potential rows. Test `bash VERIFY.sh` from this package uses original source-inclusive ZIP and passes **17/17** tests including source SHA negative control, original BASS event and core recovery, atomic level order, per-bin energy identity, HHe native rates, saved-clock Simpson identity, `NO_IVP` and no heat-port promotion. Wolfram independently evaluated both symbolic energy identities to exact **0 residual**, not independent different-author R6 or C9 review. The original PR277 `bash VERIFY.sh` previously passed **40/40** clean. The uncertainty in physical spin-yield, double process partial sigma, radiative time/transport and collisional deposition is **UNRESOLVED**, not zero.

## Source pointers

1. NIST Atomic Spectra Database, Li II lower levels: https://physics.nist.gov/PhysRefData/Handbook/Tables/lithiumtable6_a.htm
2. NIST ASD Li successive ionization: https://physics.nist.gov/cgi-bin/ASD/ie.pl
3. R. Wehlitz et al., *Single and double photoionization of lithium*, PRA 59 (1999) 3397, https://doi.org/10.1103/PhysRevA.59.3397 . This is external evidence of distinct Li+ and Li2+ yields, **not an input yield for BASS**.
4. K. A. Berrington & S. Nakazaki (1998), *Direct and indirect ionization processes near the Li hollow-atom threshold*, https://doi.org/10.1088/0953-4075/31/2/013 . Distinct multiply excited channels.
5. J. M. Shull & M. E. van Steenberg (1985), https://doi.org/10.1086/163605 . Energy partition in ionized/neutral gas.
6. S. R. Furlanetto & S. J. Stoever (2010), https://doi.org/10.1111/j.1365-2966.2010.16401.x . Nonthermal electron excitation/secondary ionization/heat partition.
7. Exact REI source code: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/b9610ccefd8ddddab89c98ccad09152b49ba6762/rust/rei_microphysics/src/igm_thermal.rs

## DAG and next actionable owner

- Working: **33/88**, central **28/88**, F4 fast **4/7**. New canonical physical delta **0**. Additional Li1s conditional diagnostic **1/1 scoped only**, not a completed canonical stage or full thermo closure. Prior auxiliary data `3/3` unchanged.
- Previous R/C per-unit `18/20` preserved (not newly rerun). Independent distinct-author R6/C9 `NOT_RUN`; native subagent `NOT_RUN`. New local regression tests do not convert these into PASS.
- `F4=PARTIAL`, `L4_ready=false`, `NO_MORE_IVPs=true`, `NO_MERGE=true`, `NO_FORCE_PUSH=true`, `AUTO_NEXT_NODE=false`, `PRODUCTION=HOLD`.
- **Next**: obtain source-identified state-resolved partial cross sections/yields and radiative rates for Li I single/double shells (with valid energy domain and species definition); explicitly decide whether BASS single-K source is replaced rather than silently split. Obtain a source-owned kinetic electron deposition operator and original REI17 full H/D/T/He/Li chemistry, photon/temperature state, and clock. Only then derive a true common-source REI thermal-port quantity. No IVPs or observed τ/CMB promotion.
