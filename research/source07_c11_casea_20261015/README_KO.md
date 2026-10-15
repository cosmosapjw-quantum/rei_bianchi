# REI SOURCE07 C11: 소스 계수 기반 Case-A 재결합·냉각과 스펙트럼 압축 동적 검증

기준일: **2026-10-15 KST**. Branch `research/rei-source07-casea-thermal-c11-20261015`는 C10 PR #128 head `26177f10d2c3264189980af2de26b3f63a9227fc`에서 분리. USER GOAL은 (z=20\to4) 전체 H/He 이온화/가스온도 이력 완성이지만, **이번 C11은 그 전체 계산이 아니라 고정 수신 셀의 특정 필수 결합 레인을 실제로 구현·검증한 결과**다. 승인 상태: `NUMERICALLY_CHECKED / LOCAL_IMPLEMENTATION_VERIFIED`, cosmological production/AX11 admission `NOT_ISSUED`.

## 원본 공급자와 scope

- HII→HI, HeII→HeI, HeIII→HeII Case-A radiative recombination 및 HeII dielectronic recombination. 직접 원본 호출 `rei_microphysics::igm_rates::igm_rates`; 2026-10-15 source `rust/rei_microphysics/src/igm_rates.rs` SHA256 `310164e620617f3089d488bd1f9668996b4a4cbd191383e45303def176ef81cf`. Source history labels the Grackle 3.4.1 implementation `af7939494ce65007887ada7b98d1813df6843346`. This is a source identity, not a new validation of Grackle theory.
- `rust/rei_microphysics/examples/source07_c11_rates.rs` compiles against **the existing Rust owner** without modifying existing functions. `--loggrid 10000 24000 129` output `owner_grackle_rates_129.csv` SHA256 `33396b071c840b40ad79d68ee626de59f12bb2cf0b1df2159627efd7fde42aec`. Headers: T K, 3 RR cm³/s, HeII DR cm³/s, 3 RR cooling erg cm³/s, HeII DR cooling erg cm³/s.
- One multi-output log-PCHIP strictly within `10000<=T<=24000 K`. Both 5500 K and 0.8*11605 K owner branch transitions are outside this validity window. **No table extrapolation, fallback, artificial floor, or Case-B relabeling.** 121 withheld direct Rust-owner evaluation temperatures: maximum relative interpolation discrepancy `1.2985959796726887e-7`, compared with predeclared 2e-7 acceptance (see `RATE_VALIDATION.json`). Direct table-point parity `7.6e-15`.
- Background reference `(-,+,+,+)`, `ds²=-c²dt²+a²e^{-2b}(dx²+dy²)+a²e^{4b}dz²`, `s=\dot b`. C9 uses full original collisionless fixed-Killing-momentum `q=0,±0.005,±0.01` source-age mapping to **a single static receiver at `a=1/5`**. Receiver photon energy in eV, proper species densities cm⁻³, proper clock s, `c=29979245800 cm/s`, (k_B=8.617333262145\times10^{-5}) eV/K. Radiation consists of one manufactured normalized photon inventory of `1 photon/H` from the original BB50K emissivity kernel or a clearly labeled nonphysical hard `E^{-1.5}` alternative, not the observed continuous source history. During the local 1e12 s absorption/recombination test **cosmological expansion/redshift, ongoing emission, spatial transport, collisions, full cooling, all CMB optical depth and polarization are OFF**.

## Theory and computational update

C10 photo event: `A_j(E)=N_E[-expm1(-dt Σλ)]λ_j/(Σλ)`, `λ_j=c n_j σ_j(E)` for `j=(HI,HeI,HeII)`. Photon survival `N_E exp(-dt Σλ)`, resulting photon energy, binding energy and gas photo-electron heating are ledgered.

New C11 Case A mid-interval operator: let `k_H=n_e α_HII`, `k_2=n_e(α_HeII+α_DR)`, `k_3=n_e α_HeIII`. For rates frozen at internally converged `T_mid,n_e_mid`, update
```
nHII_1 = nHII_0 exp(-k_H dt)
nHeIII_1 = nHeIII_0 exp(-k_3 dt)
nHeII_1 = nHeII_0 exp(-k_2 dt)
         + nHeIII_0 k_3 (exp(-k_3 dt)-exp(-k_2 dt))/(k_2-k_3).
```
The divided exponential is evaluated with `-expm1(-|k2-k3|dt)/|k2-k3| exp(-min(k2,k3)dt)`; at equality the exact continuous limit `dt exp(-k2 dt)` is used. No loss of positivity from an unstable `k2-k3` division. Species and electron counts are *reconstructed by stoichiometry*, not normalized post hoc.

Source-owned RR/DR thermal sink `Q_RR=eV^{-1} dt n_{e,mid}[\bar nHII Λ_HII+\bar nHeII(Λ_HeII+Λ_DR)+\bar nHeIII Λ_HeIII]` comes directly from the Grackle cooling columns (Λ in erg cm³/s). Thermal and electron midpoint conditions are solved simultaneously with finite iteration/rejection guards. The step preserves H/He nuclear inventories, gas simplex and positive gas energy or fails closed; the recombination source does not spuriously insert photon bins.

The external escaping recombination energy reservoir is incremented by `ΔU_escape = χ_H ΔR_H + χ_HeI ΔR_HeII + χ_HeII ΔR_HeIII + Q_RR`. It is an **energy-only Case-A escape ledger**, not a claim that each recombination produces exactly one locally tracked ionizing photon. Combined photo/recombination/photo Strang splitting conserves:
```
N_photon + n_e + N_recomb_cumulative = constant
U_photon + U_thermal + U_binding + U_caseA_escape = constant
nHI+nHII=nH,     nHeI+nHeII+nHeIII=nHe.
U_binding=chi_H nHII+chi_HeI(nHeII+nHeIII)+chi_HeII nHeIII.
```
Wolfram Language exact algebra checks H/He, charge and energy, equal-rate `k2→k3` limit: `{0,0,0,0}`. Independent SciPy matrix exponential verifies the helium chain incl. nearly degenerate cases. H-only manufactured analytic reference `nHII(t)=nHII(0)/(1+alpha nHII(0)t)` (if `n_e=n_HII`) verifies second-order reduction, no hidden electron freeze.

## Actual Ubuntu local results

`source07_c11_casea_20261015/study_results.json` and `CASEA_PHOTO_HHE.png`: BB50K at `nsteps64`, dense 36 source ages: `xHII=.7513257523437779`, `xHeII=.5553539800837982`, `Tgas=15154.088916886623 K`, CaseA escape `9.732420490192359e-5 eV/H`; hard source `xHII=.6693940800304194`, `Tgas=18680.134788794123 K`. Original rate owner, original C9 source-spectrum labels and C10 gas initial state held fixed.

BB50K 11-node positive age compression: max over all 65 saved times `|ΔxHII|=3.69340780182e-10`, `|ΔT|=1.54908557306e-5 K`; hard 12-node compression: `|ΔxHeII|=2.6717667e-9`, `|ΔT|=1.82668332855e-4 K`. Recombination chemistry modifies the orbit but source-specific compressed accuracy remains **numerically checked only on these sampled gas trajectories**. With nsteps 8/16/32/64/128, xHII and T self-convergence orders around `2.00001–2.00065` for both spectra. Ledger errors per H on actual C11 runs below ~1e-14 in the stated energy/electron units.

Speed test, 9 warmed identical 32-step H/He solver integrations of already-constructed photon packets and rate table, BLAS single thread, 36 vs 11 ages: median **2.57625×**, photon packet array memory **1,486,848 / 479,232 bytes (3.10256×)**. Six disjoint q×spectrum jobs, 3-worker versus serial, 3 full-batch repetitions: **2.51045×**, exact floating science field agreement. **No general speedup claim for fully source-coupled AX08 chemistry or its entire RAM**.

`ZERO_RATE_CONTROL.json` uses exactly the **same C11 Strang scheme and source** with a manufactured zero-rate provider. BB50K Case-A minus RR OFF: `ΔxHII=-2.840190166e-6`, `ΔT=+0.0162912645 K`, while `ΔUthermal=-3.24557484e-6 eV/H` and `Δxe=-3.72805506e-6`. Hard-source `ΔT=+0.0240252692 K`. The sign is possible because the electron heat capacity also decreases with recombination: with `D=nH+nHe+ne`, `T∝Uthermal/D`; `T_new-T_old ∝ (U R-D Q)/(D(D-R))` for positive losses `Q=ΔUthermal`, `R=Δne`. Wolfram exact identity `{0,True}`. This sign result is conditional on the ideal-gas and source/thermal subset, **not** a general IGM thermal prediction.

## How to reproduce

From the repo root (Python 3, NumPy, SciPy and matplotlib):
```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export CARGO_TARGET_DIR=/tmp/rei_source07_c11_cargo_target
(cd rust/rei_microphysics && cargo run --offline --release --example source07_c11_rates -- --loggrid 10000 24000 129) > research/source07_c11_casea_20261015/owner_grackle_rates_129.csv
python3 research/source07_c11_casea_20261015/validate_owner.py
python3 -m unittest discover -s research/source07_c11_casea_20261015 -p 'test_*.py' -v
python3 research/source07_c11_casea_20261015/study.py
python3 research/source07_c11_casea_20261015/zero_rate_control.py
```
RATE_VALIDATION, exact-cell helium matrix test, manufactured H-only analytic/convergence, negative temperature guard, matched positive-age H/He photon/energy ledgers, source-specific compression and Strang order tested locally. Pre-existing C9/C10 test suites can be replayed independently; unchanged evidence is not restated as a new full AX08 certification.

Sources: [Smith et al. Grackle methods arXiv:1610.09591](https://arxiv.org/abs/1610.09591), [Pawlik & Schaye multifrequency H/He](https://arxiv.org/abs/1008.1071), [Norman et al. 2015 coupled RT](https://doi.org/10.1088/0067-0049/216/1/16). No claim that these papers previously established this sparse age closure. Nearby user repo `bass_cr` PR #71 provides independent positive sub-bin true-child evidence but must not be conflated with C11's source-age weights; `BASS_HE` PR #64 is a distinct source/thermal universe.

**Stop/next exact scientific step**: select the source-supported continuous emissivity and real cosmic proper clock; include time-dependent photon emission, H/He collisional ionization/CE/FF/Compton, expansion work and true photon transport group-boundary flux, then compare full source-specific uncompressed interval and discretization uncertainty against this surrogate. Explicit Case A recombination photon spectral escape (or independently justified Case-B OTS) is required before transporting recombination radiation; do not relabel this energy-only sink as full RT or `GOAL_DONE`.

`native_subagent=NOT_RUN` (host did not expose native delegation). Numerical multiprocessing is actual CPU parallelism but is not a native AI subagent.

## Preservation

The research repository contains the source, 129-node Grackle table, Rust rates-export example, tests, exact source SHA, small evidence JSON, and plot. User original checkout, private run bindings and other research worktrees were not mutated. For the source+evidence ZIP and independent Google Drive/Dropbox readback checks, use the accompanying `BACKUP_RECEIPT.json` **only after it is generated from actual remote results**. No upload is asserted before a successful remote readback.
