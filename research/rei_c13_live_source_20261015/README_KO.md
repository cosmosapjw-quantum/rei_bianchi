# REI C13: actual MD14 photon birth + BASS Killing transport + C11 H/He Case A, with source-stress Σ/π diagnostics

**Execution date:** 2026-10-15 KST. **Scope:** short near-̅z=4 cosmological source/transport/chemistry pilot, on a source-locked *prescribed* Bianchi I family. **Science state:** DERIVED, NUMERICALLY_CHECKED, LOCAL_IMPLEMENTATION_VERIFIED in stated scope; **NO full ̅z=20→4 physical reionization history, AX11/AX12 or observer CMB admission.** Initial ̅z≈4 gas deliberately prescribed (x_HII=.4, x_HeII=.5, x_HeIII=.3, Tgas=12000 K), **not** the original ̅z=20 gas evolved self-consistently. Its short interval a=0.1999→0.2 is not a postulated cosmic initial condition.

## Real source identity and implementation map

- Base rei_bianchi parent C12 HEAD `5d940a023507a601c2c8c935bad0b0aea1dcbe9c`. User original active owner `0fcb2dddf5de6b583c2e00f150abff0b2afb6315` is untouched. This is separate opt-in Git branch, no local Codex, native AI subagent not available (NOT_RUN).
- Original real Rust `rei_microphysics::axbi_sources::AxbiSource` exported **without changing its source** through additive `rust/rei_microphysics/examples/rei_c13_native_source.rs`. `SOURCE_ID=MD14_Z002_FESC_BB50K_13P6_100_V1`, original source module SHA256 `606e3c2ec367dd9951ebbf2f53486f2232b49c0218896d66d8dc13dd5ee83bfe`, scenario SHA256 `07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696`.
- Spectral support emitted 13.6–100 eV split at original 13.6/24.59/54.42/100-eV source edges; native spectra 4,8,16,32 cells per threshold segment; native angular Gauss 8 or 16. Native emitted per-H/s validated on **17 original source z=4..20 nodes**, plus proper photon densities and source spectral/solid-angle normalization, no copied/artificial photon-birth amplitude.
- Original `bass` PR157 independently implemented positive `gauss_increment` and `Background(Family(q))`, exact physical elapsed seconds and Δb from bounded `d(ln a)/H`, no subtraction of huge accumulated cosmic times. The same donor is inherited through C12 Git-blob-verified `research/rei_crossrepo_integration_20261015/suppliers/bass/...`.
- Original REI C11 `casea.strang_step` plus `CaseARates` owner Grackle (Rust `igm_rates`, table SHA256 `33396b071c840b40ad79d68ee626de59f12bb2cf0b1df2159627efd7fde42aec`) is ACTUALLY called to evolve H I/H II, He I/II/III, electrons and ideal-gas temperature, plus source photon photoheating and Case-A escape energy. CI/CE/FF/Compton and general dynamic energy stress are not switched on.
- Original `bass_cr` PR71 `PositivePacketOracle/AdaptiveQGrid` is **actually called on propagated C13 native stellar packets at one receiver proper time, same one source-ray label** in `supplier_snapshot.py`, with all six source-gas photoevents/photoheats enclosed. No arbitrary child moments are inferred from parent N/U. Strict `HOLD_PRECISION_TARGET` remains unresolved.
- C13 short-interval H/He source-cohort compression `coalesce.py` preserves per-native-source angular-energy mode N, first/second energy moment and Eμ² by positive two-point energy nodes. Each accepted merge is tested against three true proper neutral gas states (100%,70%,35%) for three H/He reactions and photoelectron heating, then only adopted if explicitly set local thresholds pass; not a global dynamic oracle/certificate. The original packet support is retained on HOLD.
- C13 opt-in `rec_bianchi` HyRec donor **remains DISABLED** at ̅z=20 (never copied as ̅z=4 gas), and source-scoped warm BASS_HE P01 Thomson optical depth **is not** relabeled as this cold astro source's τ. WU088_HH PR85 microscopic screened Coulomb results do **not** provide a production physical `k_HH(T)`; collision/reaction HH stays OFF (original C12 WU guard test still PASS).
- Immutable exact Git blob `c1f8c351a04891085fb6cfdc7fcb2956fa97c8da` is REI PR135 Einstein-Sigma/pi source, and `7abb53320534203715cd65d909cfa3764396e6d0` is REI PR136 original BASS moment hierarchy source. They are actually invoked through `pr136_sigma_interface.py` (case-independent positive radiation/massive seed stress) without conflating them with the ionizing-photon pressure and **without feeding back into the old stress-free metric**.

## Exact physical assumptions and accounting

Default signature (-,+,+,+):
`ds²=-c²dt²+a²(e^-2b(dx²+dy²)+e^4b dz²)`, `s=ẋb`,
`σ^i_j=diag(-s,-s,2s)`, `Σ=|σ|/H=√3|s|/H`, plus independent signed shear orientation. Original `q_ref=s_ref/H_FLRW,ref` is a **historical source-boundary adapter** only, not the new scalar Σ itself. `|Σ_ref|≠|Σ(zbar=4)|`: physically evolved shear varies with a. This distinction was identified by a real failing regression test and corrected.

The positive individual Killing photon propagation is
```
R=sqrt((1-mu²) exp(2 Δb)+mu² exp(-4 Δb)),
E_new=E_old (a_old/a_new) R,  mu_new=mu_old exp(-2 Δb)/R.
```
`N_i/N_H` is conserved along collisionless source-free ray pushforward, without a *second* angular Jacobian. For a homogeneous ideal isotropic nonrelativistic proper gas, n_H∝a^-3, T_ad∝a^-2; all proper reaction number densities in cm^-3, source photon energies eV, elapsed clock SI seconds, c=299792458 m/s (29979245800 cm/s), k_B=8.617333262145×10^-5 eV/K. The source BBN-type H/He state is NOT inferred from photon birth.

The cross-process ledger, per H nucleus, is
```
L_N = N_gamma/N_H + n_e/n_H + N_rec,cumulative/N_H - N_MD14,cumulative/N_H
L_E = U_gamma/N_H + U_thermal/N_H + U_binding/N_H
    + U_recombination_escape/N_H + W_expansion,accum/N_H
    - U_MD14,emitted_cumulative/N_H.
```
Each time step uses BASS direct Gauss4 Δt and Δb, exactly mapped photon momentum and thermal expansion, positive original-source birth at the log-midpoint (two halves), and source C11 Case-A H/He reaction. `W_expansion` is the **measured change** of photon energy and ideal-gas thermal energy due to this separately computed expansion, not a newly calibrated matter closure. `U_binding` tracks H+He ionization thresholds, and native source Case A escapes are recorded as energy, **not invented recombination photons or active Case-B OTS**. This ledger is conservation evidence for this reduced submodel; excluded native collisional source and full energy-momentum exchange need separate physical owners.

Actual ionizing-photon extra pressure anisotropy at the receiver:
```
Pi_ion [Pa] = (1.602176634e-13) nH_cm^-3 ∑_i (N_i/N_H) E_i [eV] P2(mu_i)
Sigma=√3 |s|/H,    orientation=sign(s).
```
The PR136 BASS initially isotropic primordial massless radiation stress `Pi_CMB` and frozen collisionless massive matter tensor are **separate** from this newly emitting UV photon pressure. They are evaluated at the SAME (a,b) to compare, but are **not added to the Einstein shear equation** or to the native chemical source in this run. An independently seeded positive `W=1+A P2` (A_r=.2,A_m=.4) has `Pi_CMB/P_r≠0` even when Σ_ref=0, as true PR136 source implementation predicts. This is not a native AXBI coupled Einstein UV solver.

## Executed source-backed numbers (NOT observational reionization history)

In the physically ordered short interval `a=0.1999→0.2`, Δt≈3.6136e13 s, q=0, native spectral 8 per threshold segment ×8 directions, 128 proper steps:
- Cumulative stellar photoemission `N_source/H=0.009511928993497785` (independent source a quadrature agrees to near 1e-11 relative); surviving UV source photons/H `0.00033794958635945544`.
- `x_HII=0.40882451599893593`, `x_HeII=0.503626162052235`, `x_HeIII=0.2997996449877433`, `Tgas=12193.495444733417 K`. `τ_Thomson=8.450822111816708e-6` is only a **short post-source proper normal-frame integrated scattering depth**, not to the CMB observer.
- Source emitted energy 0.19286953562051398 eV/H, Case-A escape 0.0021341391598109025 eV/H, adiabatic/Killing cosmic work 0.002466299134594613 eV/H.
- The five signed native original source q cases and independent C11 source/geometry/atomic owner satisfy `|L_N(t)-L_N(0)|≲10^-15`, `|L_E(t)-L_E(0)|≲10^-14 eV/H` on the sampled time history.
- At q=+.01, nsteps32, PR136 actual primitive `Pi_CMB=-4.1402478860969967e-13 Pa`, `Pi_m,collisionless=-5.717336495437477e-24 Pa`, UV source `Pi_ion=-4.3224348841729385e-27 Pa`; q negative gives corresponding reversed sign. The frozen relativistic massless/massive source and UV source are not a single thermodynamic fluid, and no new Einstein RHS evolution is computed.

## Optimization, numerical convergence and exact errors

- Positive source-age cohort memory reduction, original source 8×8/128 steps: **49,152 → 384 stored photon packets**, 128× fewer and 128× lower in **only the photon-cloud E,mu,N array**; *NOT* total program memory. Seven warmed matched whole-C13 source/chemistry BASS geometry trials gave median ~**3.23×** speedup at q0, while retaining the six immediate species reaction observables within given budgets.
- Actual q=0,±.01 paired compressed versus fully uncompressed 128-step trajectories: endpoint `|Δx_HII|≤10^-15`, `|ΔT|≤1.3e-11 K`, UV quadrupole |ΔPi_ion|≈2.5e-31 Pa; 127 compression admissions/0 HOLD in these cases. **This is a finite model test, not a guaranteed global closure error.** Threshold adversarial physical packet passed HOLD (rejected compression).
- Memory-bounded NumPy vectorized Bianchi E/mu advection over 8,192 photons vs scalar independent reference: 34.54× median microkernel speed, ≈4.39e-16 relative agreement. Six-point source/chemistry+geometry signed q batch uses 3-worker vs serial ≈2.19×, exactly same recorded science floats; not native AX08 solver speedup.
- 8/16/32/64/128 temporal refinement (uncompressed 8×8 source) shows self-convergence orders approaching 2: x_HII 1.48→1.76→1.92, gas T 1.80→1.95→1.99, HeII ≈1.92→1.98→1.995, τ only 1.42→1.73→1.91. **Empirical**, not a rigorous time global error enclosure.
- Native spectral refinement 4/8/16/32 cells per threshold segment at fixed 64 steps (q0): gas T `12193.690648925349, 12193.428174167262, 12193.3603104983, 12193.34319804474 K`; the 8→16 and16→32 differences ratio ≈3.9657, consistent with native 2nd order spectral quadrature. Angular nmu8→16 at fixed 8 segments changed these scalar observables only at floating precision in q0,+.01; neither is a universal polarization/shear sky angular convergence certificate.
- Actual `bass_cr` one ray/one receiver time adaptive source after 8 native source steps: 384 true-child packets, 1→8 cells, six reaction bound widths improved [1,3.57,249,765,764,61.7]× but `HOLD_PRECISION_TARGET` persists.
- Compression preserves N, E, E², Eμ² per source mode; it **does not** formally conserve the full dipole, polarization, spin-2 phase or every future stimulated/recombination spectrum. The separate fast momentum quadrupole diagnostic is valid only in this symmetric prescribed radiation source/source mode.

## Exact commands and evidence

Run at the C13 repository root, with Python 3, NumPy, SciPy, matplotlib; original source and C11 rate table already tracked:
```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export CARGO_TARGET_DIR=/tmp/rei_c13_native_source_target
# Source native from exact committed Rust owner:
cargo run --offline --manifest-path rust/rei_microphysics/Cargo.toml --release \
   --example rei_c13_native_source -- 8 8 1.8981984507140269e-07 \
   > research/rei_c13_live_source_20261015/NATIVE_SOURCE_8X8.csv
python3 -m unittest discover -s research/rei_c13_live_source_20261015 -p 'test_*.py' -v
python3 research/rei_c13_live_source_20261015/study.py
python3 research/rei_c13_live_source_20261015/supplier_snapshot.py
python3 research/rei_c13_live_source_20261015/pr136_sigma_interface.py
# Independently replay C9-C12 legacy and original native tests.
python3 -m unittest discover -s research/rei_crossrepo_integration_20261015 -p 'test_*.py' -v
python3 -m unittest discover -s research/source07_c11_casea_20261015 -p 'test_*.py' -v
python3 -m unittest discover -s research/source07_c10_dynamic_20261015 -p 'test_*.py' -v
python3 -m unittest discover -s research/source07_c9_heii_vector_20261015 -p 'test_*.py' -v
cargo test --offline --manifest-path rust/rei_microphysics/Cargo.toml --test axbi_sources
cargo test --offline --manifest-path rust/rei_microphysics/Cargo.toml --test axbi_background
cargo test --offline --manifest-path rust/rei_microphysics/Cargo.toml --test igm_rates
cargo test --offline --manifest-path rust/rei_microphysics/Cargo.toml --test igm_thermal
```

Actual fresh targeted C13 tests **16/16 PASS** after source32 and PR136 diagnostics; inherited C12 6/6, C11 8/8, C10 8/8, C9 5/5; native original Rust source2/2, background6/6, igm_rates4/4, igm_thermal11/11. PR136 provider executed; initial versus endpoint Σ reference error and near-zero numerical pressure exact0 tests were diagnosed and repaired. CAS direct Wolfram exact Killing characteristics returned three zero identities. Source SHA lock and test receipts under `verification/`; model numerical evidence in `C13_STUDY_RESULTS.json`, source age `BASSCR_C13_SOURCE_BOUND.json`, PR136 `PR136_HIERARCHY_COUPLING.json`; plotted near-z4 source and abundance history `LIVE_SOURCE_ABUNDANCE_HISTORY.png` and machine readable CSV.

## Next physically necessary integration, without legacy claim promotion

1. Extend from near z4 to all zbar20→4 with **real z20 source gas/photons** and full H/He chemical/cooling provider. Current native Grackle provider table 10,000–24,000 K cannot be extrapolated into the cold initial z20 baseline 8 K. Respect original low-T allowed rates and energy/heat owner before attempting full history.
2. Joint Einstein Σ and π sourced geometry: include injected UV photon π, original independent BASS massless+massive stress and chemistry/gas collision pressure changes, while satisfying Hamiltonian, Raychaudhuri, emission/absorption momentum Q_a. Do not reload old stress-free checkpoint into changed source.
3. Native rei_bianchi production bin mapping and continuous source source-age spectral/angle support, adaptive true-child q moments, recombination photon escape or authorized Case-B OTS and photon group-boundary flux. Accurately certify self-convergence AX11 at matched source/clock and ensure observer τ source/sky parity AX12.
4. Source-matched isolated rec_bianchi HyRec ̅z20 initial-state counterfactual only, while original conditional baseline preserved. WU088_HH effective production rate `k_HH(T)` remains absent even after PR85 micro-scattering mathematical progress; keep OFF. BASS_HE warm P01 source-specific τ is a separate control only.

**Files/backup:** Source and numerical outputs are committed and archived separately with SHA-256 and tested restorable ZIP. Their precise remote paths and two-cloud readback belong exclusively to `BACKUP_RECEIPT.json` after successful uploads. A successful archive CRC alone is not an independent scientific validation or a cloud backup acknowledgement.
