# REI owner F08: native Rust first-step photoabsorption and photoelectron-energy consequence

Date: 2026-11-01; selected physmath R5–R8 and C5/C6/C9/C10, **one physical bounded unit**; no original production admission.

## 1. Real source, historical Rust recovery and question

The user's original Rust source `rust/rei_microphysics/src/atomic_provider.rs` at historical Git commit `d234243a79e4e8e611aaf4ac61949c5ef9111468` has exact byte SHA256 `b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3`. The copied `src/original_atomic_provider.rs` is byte-identical, not a hand-coded approximation; its `AtomicProvider::cross_section(Absorber::HI,E)` is called by actual standalone native Rust. This is **not** a port of the entire 26-event microphysics/worker. That larger Rust restoration is separately underway in `research/rei-f05-rust-native-restoration-20261101` and must not be overwritten.

Original F08 S0 photon/matter evidence is read directly from user-authorized full BASS #321 source-inclusive backup ZIP SHA256 `530370df21fd40e57165bd0882c17c25f684d571788c5c2db70f2c3105a48cfb`, whose raw members are SHA256-pinned and CRC tested by `source_intake.py`. Two original S0 proper-time histories (Bianchi I and matched FLRW), original photon headers with 8×16 angular `qhat` and 17 energy nodes, actual original H I proper density at the first endpoint, original F08 `gamma_HI_per_s` first result. Native source 256 directional records in `source_inputs/ORIGINAL_REI_F08_S0_FIRSTSTEP_256_RAYS.csv`.

## 2. Equation and exact scope

In the prescribed metric `ds²=-c²dt²+Σ a_i(t)² dx_i²` with fixed `H_i=(1.01,.99,1)×10^-14 s^-1` or isotropic `10^-14 s^-1`, the exact local observer-energy characteristic for the first original proper time interval `Δt=625,000,000 s` is

```
E_q = E_birth * sqrt(sum_i q_i^2 exp(-2 H_i Δt)),  E_birth=13.7 eV
w_minus = (E_plus-E_q)/(E_plus-E_minus), w_plus=1-w_minus
E_minus=13.675 eV, E_plus=13.7 eV.
```

The initial original 0.05 photon/H is isotropic over 128 rays; original continuous source `5e-15 photon/H/s` is injected at the endpoint at 13.7 eV with original `g^-3` direction weighting. Both representations use the **same exact original frozen endpoint** `n_HI=9.99359406501587e-6 cm^-3` and `AtomicProvider` HI Verner96 fit. Original source implicit per-node photoabsorption fraction

```
f(E)=c Δt n_HI σ_HI(E)/(1+c Δt n_HI σ_HI(E)), c=29979245800 cm/s.
N_abs_characteristic/H = sum_q (0.05/128)*f(E_q) + S_q*f(13.7)
N_abs_hat/H = sum_q (0.05/128)*[w_minus*f(13.675)+w_plus*f(13.7)] + S_q*f(13.7)
Q_photoelectron = sum_absorbed_photons [(E-χ_H) eV], χ_H=13.598434599702 eV.
```

`Q_photoelectron` is direct photon **excess-energy transfer under this frozen absorbing model**, not integrated original gas net heating (cooling, OTS, collisions and thermochemistry absent). Original 26-event source/worker, first tick, real observer CMB, Einstein Bianchi evolution and fully coupled 16k F08 IVP are **not** replayed here.

## 3. New actual original-source native Rust physical results

| First original interval | Bianchi I | FLRW |
|---|---:|---:|
| Exact 128-ray spectral minimum [eV] | 13.699913596561121 | 13.699914375267575 |
| Hat forbidden lower-node photon/H before absorption | 1.7124946478630246e-4 | 1.7124946484386753e-4 |
| Characteristic H I absorbed photon/H | 5.8195553751875328e-5 | 5.8195553751875498e-5 |
| Hat H I absorbed photon/H | 5.8195556947896758e-5 | 5.8195556947897118e-5 |
| **hat-minus-characteristic absorbed photon/H** | **+3.1960214300920907e-12** | **+3.196021619827471e-12** |
| **relative event bias** | **+5.49186531280e-8** | **+5.49186563883e-8** |
| Characteristic photoelectron excess [eV/H] | 5.9056720450657647e-6 | 5.9056720450663161e-6 |
| Hat photoelectron excess [eV/H] | 5.9056479548605930e-6 | 5.9056479548589278e-6 |
| **relative excess-energy bias** | **-4.07916406258e-6** | **-4.07916443793e-6** |

The mathematical **continuous-direction** source support floor 13.699913519... eV from BASS #321 is strictly below the **128 finite-ray** minimum, as it should be: do not relabel this angular sampling difference as a source error. The first-step artificial population below the exact energy support is about `1.7125e-4 photon/H`, consistent with original BASS #321. Nonetheless the actual first-step HI event bias is ~`5.5e-8` relative and the excess-energy bias ~`4.1e-6` relative. The previously reported **23.4276% final below-support photon number weight** is NOT a 23% HI rate/heat error, nor is this first-step result a bound on 16k-step cumulative chemical feedback.

An independently useful owner-scope check uses actual original first-step `x_HII=0.9000621855333871` and `Δt`: `N_abs_characteristic/((1-x_HII)Δt)=9.3170824777e-13 s^-1`, which differs from original full F08 `gamma_HI_per_s=9.3170783117e-13` by `+4.4714e-7` relative. This is a same-source approximate physical-scale agreement, NOT exact whole-solver parity.

## 4. Execution, hostile referee and decision

- **Rust C5/C6:** `cargo test --offline` 3/3 PASS, `cargo test --offline --release` 3/3 PASS; source-matched 256-row native Rust physics CSV generated, its SHA256 `7b1f9e2a6c99f3c0ec75101eea1e1b47656ac105a499bae640eebf63a3fb25f0`, summary JSON SHA256 `0473007072ea6d908b270a35a89132fb18aea8e5d823ca21c9c1947ef95c6c2e`.
- **R6/C9:** independent same-author pure Python scalar derivation rechecked 256 rows ×13 checks = 3328 physical scalar comparisons, original source and original provider SHA; recorded `results/INDEPENDENT_ORACLE.json` SHA256 `809c3530d8d2bd7f28273879df31aa33b0d9dbb78adf7213ac9b564d5dafee20`.
- Release binary reproduced **all 256 rows with 0.0 maximum absolute reported difference**. Input altered to invalid q fails, source ZIP one-byte tampering fails original SHA. These are actual negative PASS_EXPECTED_REJECT results.
- During independent auditing a few cancellation-sensitive `(13.7-E)/(0.025)` float weights failed naive relative-equality at ~2e-11 relative. Repaired **only numerical readback representation comparison**, keeping source/physics outputs untouched. No change to production tolerances; this is not a formal directed-rounding error certificate.
- Exact historic original Rust `AtomicProvider` Git blob SHA256 equals the source-archive Rust atom source SHA256. Different-author subagent/referee not available: `native_subagent=NOT_RUN`; hostile review is same author independent implementation.

**R8 owner decision:** `PROMOTE_FOR_SPECIFIED_USE` 256-ray ORIGINAL F08 S0 frozen-matter *first-step HI photon event/excess-energy consequence*. `HOLD` original full coupled photon source physical equivalence, V1 F08 scientific admission, original F05 tick161 and production. Original first interval F05 V1 logT sufficient enclosure 2.1245050576e-4 >2e-4 remains historical failure; V2 owner shadow does not automatically accept it. F09 atomic-provider domain remains blocked.

**Drift watchdog:** Physical event/heat consequence from native Rust source = productive. Stop at this one unit. Next material F08 science must propagate support-aware characteristics through original source-matched H/He/thermal feedback and compare admitted observables; parallel higher priority F05 original worker 0→64 parity and V2 versioned admission remains the central 28/88 critical path. No repeated side atlas, no full Rust migration claim.

DAG at R5, R6, R7, R8, C5, C6, C9 and C10: **Central 28/88, Working 33/88, Physical Fast 4/7, canonical delta=0**; no original source or production edits.

Primary physics: Verner et al. 1996, https://doi.org/10.1086/177435 ; original Rust Git source and archived BASS/REI source are the implementation authority, not the paper alone.

## 5. Current owner-level cross-repo intake, not unqualified merging

A second GitHub readback discovered later live REI Draft [#359](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/359) HEAD `ae7c9b5e3176810b08c291871bcabbd35c0eda0e`, a **separate, previously completed Rust characteristic 128-ray support study**, and [#360](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/360) HEAD `b8165987fe1472e6269ac7600c16d17b33067e60`, exact restoration of 117 historical native Rust sources with 262/262 native tests and a source-conditional 46,080-cell F05 Rust EOS evaluation. Their claims are **not** replaced by this unit: #359 support diagnosis is upstream and accepted for bounded F08 source comparison, #360 exact historical Rust preservation is admissible for research-only reuse, not original full 26-event worker parity or production.

Other latest real siblings: BASS_HE #148 PR has theory-only H/He spatial PW19 donor (no newly admitted causal photon field at last readback), rec_bianchi #192 has accepted tick0→160 Thomson material diagnostic (source history, no LoS), bass_cr #160 has conditional intrinsic Lyα Case-B emissivity but no transported 10.2eV line photons, WU088_HH #192 has conditional D/H kinetics but no original REI D photon or full thermochemical owner, and VigilODE #183 remains optional solver/thermal-root shadow. **None is promoted as an original F08 13.7eV photon source replacement or new canonical DAG node.** REI #357's BASS_HE146+REC190 derived F05 consumption remains valid under its old source/clock scope.

This new study contributes the original Rust **HI photoionization and excess-energy consequence** of #359's source-support mechanism, not a competing generalized remapper. It should be reviewed at the F08 project-owner side by direct scientific use, not counted as another independent cosmological epoch.
