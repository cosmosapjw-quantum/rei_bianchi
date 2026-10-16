# V11 C5: 독립 원본 rate 기반 CI·CE·FF·CMB 계산 코드

독립 샌드박스 경로 `src/ci_thermal_clock.py`. GitHub에서는 PR #172에 실제로 있는 `v7/reference/radau_casea_reference.py`와 최상위 `rust/rei_microphysics/src/igm_{rates,thermal,state}.rs`의 frozen owner를 사용한다. 로컬 복원 패키지에는 V7 cosmology 참고본과 owner 원본을 그대로 포함한다.

- Input: prescribed FLRW `H(a)`, `nHtotal(a)`, `nHe/nH`, `a0=1/21`, HII/HeII/HeIII fractions `(0.075,0.12,0.03)`, T0=15000 K, X interval normally `1e-5`. No photons, source or opacity.
- State q=(three ion fractions, W[eV/total H]), augmented 12 reaction/cooling reservoirs, four independent RR/DR kinetic radiative cooling reservoirs, gas geometric work. Total nuclei are encoded as complements; electrons are derived algebraically.
- Literal native CI K1,K3,K5 (including 1e-20 floor), RR K2,k4RR,K6 and DR, CEHI, CEHeI metastable (n_e squared, HeII state), CEHeII, free-free, and CMB Thomson coupling. Temperature input validated against original 1..1e6 K owner domain. Original 96-row 17-coefficient table verified with maximal relative difference 2.8410045294244635e-14.
- Eight opt-in modes (owner_like_be, ci_mid, ce_mid, ff_mid, cmb_mid, thermal_mid, chemical_mid, all_mid). Each physical process is evaluated at one state-clock and written to both state and ledger. One coupled scipy.optimize.root solves end-state, accepted final state never projected. Nonconverged or negative states are rejected. Exact half-step adiabatic cooling separately counts geometric work.
- Independent continuous 21-variable SciPy Radau solution used as the benchmark. No actual native Rust driver is executed by this sandbox implementation.
- Initial Tgas point: CI binding ~2.3542324167 eV/H/X, CEHI cooling 155.6319045 eV/H/X, free-free 0.0177379088 eV/H/X, CMB gas input −7.71527165 eV/H/X, versus RR/DR sum ~0.0597 eV/H/X. These are instantaneous X-rates for this particular state, not proven error-budget contributions.
- First native comparison: N=128 BE Tgas sandbox 14988.761135234614 K vs recorded V10 NCP `no_radiation_be` 14988.7611352303 K, absolute 4.315e-9 K (single matching endpoint). Scope-matched numerical parity, NOT full native runtime equivalence.
