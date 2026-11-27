# BASS_HE RUX03 | Native REI tick160 H/He proper photo-opacity + exact spectral-hardening witness

2026-11-01 | Theory R1–R10 scoped stage | Source-conditional single physics unit | Owner BASS_HE; receiver REI IGM.

## R1–R3 Physical target, source authority and non-identities
Reconstruct the original **accepted** REI F05 46,080-node H/He five-population intervals at tick160 from the original immutable `REIADP1` state, divide by the **original** positive proper cell volumes at source z=5.95, and combine their **actual** local neutral density with already source-locked PW19 spectral H/He photoionization microphysics. Produce physically sourced local frequency-band opacity and full-frequency-versus-grey spectral-hardening diagnostics, *not* a synthetic sky or local photon current. No new time integration.

Immutable parent BASS_HE PR147 HEAD `c7ea4b30c25e177014d59a755621760323578cd9`, prior PR146 BASS_HE HE energy and REI PR357 original-owner conditional consumer. Local original source ZIP `REC191_ORIGINAL_F05_NATIVE_THOMSON_MEDIUM_SOURCE_FULL_20261101.zip` SHA256 `3f6772f54822274bf6228dac1ec629a9d0b0cde9d2a0adbaa08d59a1ac352d0e`. Nested original REI F05 source TAR SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`, state `LOCAL_NEUTRAL_HAZARD_PRIMARY.state` accepted tick160 SHA256 `74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6`. Original `initial_material_state_z6.npz` SHA256 `7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d`, original first-interval source clock 17/17 z_mid=5.95 SHA256 `9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268`.

BASS_HE PR147 (not the native REI photon owner) supplies published PW19/Verner energy source donor ZIP SHA256 `afd470b9fd934234e7f6e815d6887814a2ff8767e61f0d2a8e6187efde8d0d55`. Its original exact spectral source data and same-PW19 rates remain unchanged. Source donor group CSV SHA256 `080fb36c9bf4a161f58dcf23c11765bf6eeeaeb537c2fab3fd2b51304d09240b`. The PW19 average background is **not** the local REI causal transport field or a photon emission history. It is a conditional external isotropic test intensity.

## R4–R5 Constructive local absorption and energy ledger
Use (-,+,+,+), comoving gas tetrad, c=2.99792458e10 cm/s, k_B explicitly for any later thermal RHS. Original cell proper volume `V_i=W_node_i (3.085677581491367e24 cm)^3 / (1+5.95)^3`. Exact source population interval `N_{s,i}∈[N^-_{s,i},N^+_{s,i}]`, native proper absorber `n_{s,i}∈[N^-_{s,i}/V_i,N^+_{s,i}/V_i]` for s={HI,HeI,HeII}. H nuclei and He nuclei are separately conserved. All 46080 REIADP1 source state values must be included and parent original nuclei values must fall in corresponding conserved intervals.

Let `Phi_g = ∫_g [I(E)/(epsilon_eV E)] dln E` [photons cm^-2 s^-1], `w_g(E)=Phi(E)/Phi_g` photon-number normalized, `mu_s,g=∫w_g sigma_s(E)dlnE`, `K_st,g=∫w_g sigma_s(E)sigma_t(E)dlnE`; σ in cm². The same 3 physically supported spectral intervals are A=[13.60,24.59], B=[24.59,54.42], C=[54.42,50000] eV, **not** original REI four photon groups. Species inactive below their fitted threshold have identically zero cross-section.

The source-conditional local attenuation coefficient is
`kappa_g,i = sum_s n_s,i mu_s,g` [cm^-1], with interval `sum_s n_s^± mu_s,g` and local `ell_g,i = 1/kappa_g,i` [cm]. The source-conditional ionizations per unit proper volume satisfy
`R_g,i = c*n_gamma_g*kappa_g,i = sum_s n_s,i Gamma_s,g`, where `n_gamma_g=Phi_g/c` [cm^-3] and `Gamma_s,g=Phi_g mu_s,g` [s^-1]. The local *photo-only* thermal excess source is `Q_photo_g,i=sum_s n_s,i H_s,g` [erg cm^-3 s^-1], while binding-energy increase is `Bdot_g,i=sum_s chi_s epsilon_eV n_s,i Gamma_s,g`. Exact energy:
`Q_photo+Bdot= c*n_gamma * sum_s n_s <sigma_s E> *epsilon_eV`. **Net thermal RHS, OTS/recombination and photons leaking from the original box are not specified by these terms.**

## R5 finite spectral-hardening theorem
For a homogeneous proper path of length L with *frozen* local native density, full frequency-resolved transmission is
`T_g(L) = ∫w_g(E)exp[-kappa(E)L]dlnE`,
`kappa(E)=sum_s n_s sigma_s(E)`.
The single-group frozen grey closure gives `Tgrey_g(L)=exp[-L kappa_g]`.
Since exp is convex: **T_g(L)≥Tgrey_g(L)** for L≥0, equality only for a constant κ(E) almost everywhere in the photon-number measure or L=0. Also
`d ln T/dL=-<kappa>_surviving`,
`d² ln T/dL²=Var_surviving(kappa)≥0`.
At L=0, the physically sourced variance is `Var_g(kappa)=sum_st n_s (K_st,g - mu_s,g mu_t,g) n_t ≥0`. The true frequency-resolved opacity decreases along the path because spectral hardening preferentially removes higher-κ photons. Therefore a fixed grey `kappa_g` may be a correct **instantaneous local rate** but cannot claim an exact finite-column transport law. This is a physical distinction, not numerical error.

Report `CV²=Var_g(kappa)/kappa_g²` for original accepted cell midpoint states as a **diagnostic**, NOT an interval certificate. The only single-path comparison uses L=1/kappa_g derived from the same cell (one *diagnostic mean free path*); it is never called a cosmological ray distance or observed optical depth. Use representative actual native cells, not invented gas composition.

## R6–R10 Evidence gates, host claims, next action
One bounded same-author hostile review checks original state parser, conservation, signed groups, exact energy, κ and µ positivity, source SHA, grey Jensen inequality and equality limits. Source interval endpoints are inherited IEEE 754 and source-native validated scopes, **NOT complete MPFI/MPFR proof**. No original REI worker, MAIN, source spectrum, stage history, tolerance or IVP mutation. Numerical tests of a generated CSV are not independent physical source verification unless full original ZIP is read back.

RUX02: published conditional PW19 spectral donor exists; RUX03: **native local material opacity operator computed if source checks pass**, local causal incident flux/transport source remains UNBOUND; RUX04: NOT_ADMITTED. No artificial G3 photon current, no P19-D1-rate substitution, no new photon spectra. REI central **28/88_REPORTED**, REI working **33/88_REPORTED**, PhysicalFast **4/7_REPORTED**, BASS_HE Physical **14/18_REPORTED**, canonical delta 0. PRODUCTION HOLD.

Next central path: use a genuine REI-owned causal/local Jnu(t,x,n) and boundary emission history + opacity operator + OTS/cooling/Einstein geometry to evaluate matched FLRW/finite-shear Bianchi physical histories. Independently REI owner must decide original tick161 V2 runtime/0→64 parity. Do not spin a new frozen-medium source atlas once this unit is published.
