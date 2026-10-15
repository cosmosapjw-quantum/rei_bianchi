# HE18 → rei_bianchi: 실제 native 세 수준 수렴성 및 spectral remap 비-semigroup 검증
2026-10-15 KST. 범위: 실제 cold Plancklike_MD14/BB50K LRS Bianchi I의 짧은 상대적 적색편이 구간, 별도 탐색적 실행. 모든 결과는 **NONAUTHORITATIVE_EXPLORATORY**이며 native science admission이 발급된 것은 아니다.

## 1. 실제 source identity와 실험 계약

원래 solver owner: /home/cosmosapjw/Dropbox/bianchi/rei_bianchi, branch `codex/rux-science-delivery-20261014`, HEAD `0fcb2dddf5de6b583c2e00f150abff0b2afb6315`. 이 원본 작업 트리의 추적 파일은 전혀 바꾸지 않았다. 별도 소스 worktree: `/tmp/BASS_HE_REI_ADAPTER_20261015`; 연구 브랜치 `research/bass-he-optical-depth-transfer-20261015`.

- 실제 native binary `rust/rei_microphysics/target/release/examples/axbi_reionization` SHA256 = `32d11e733155d355a1fa748597b48ea1c8196adba3c871722a7a598f0b6cbfca`.
- 모든 실행 source_identity.txt SHA256 = `d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185`.
- 독립 출처에서 읽은 원본 5개 q-부호 이력 중 ZERO, SHEAR_HALF_MINUS, SHEAR_HALF_PLUS를 선택하였다.
- fixed source, original thermodynamics, emissivity, angular quadrature, energy subdivisions, reference proper clock, H/He normal-comoving. 기본 metric signature (-,+,+,+).
- 공통 평균 종점 \(\bar z=19.99\) (\(a=0.04764173415912339\)), 시작 \(\bar z=20\).
- 세 가지 원 adaptive local_target = 1e-5, 3e-6, 1e-6. 각각 ZERO, q=-.005, q=+.005. 총 9개 native **직접 실행**, 전부 EXIT_ZERO / COMPLETE_REPRESENTED_INTERVAL, 각 native scientific_admission=NOT_ISSUED.
- 각 q의 accepted count는 target 순서대로 972 / 1797 / 3706. 두-worker bounded run elapsed wall 113.426 s (첫 6), 160.002 s (추가 3); 각 subprocess max wall 120s; output cap 256 MiB, original owner stage 방해 없음.
- Initial source packet, physical rates, source-grid, geometry reference remain frozen. `spectra_every_accepted=10000`은 출력 빈도만 변경하였다. 처음 기준 실행 CSV는 원래 source 학습 이력의 **처음 973개 line(헤더 포함)**과 바이트 일치했고 이후 마지막 경계 행만 다르다. 이는 byte identity of bounded prefix, not an equivalence of entire files.

## 2. native 상태·목적함수 결과

\[
n_e=n_H[x_{\mathrm{HII}}+f_{\mathrm{He}}(x_{\mathrm{HeII}}+2x_{\mathrm{HeIII}})],\quad f_{\mathrm{He}}=1227/15092,\quad d\tau/dt=c\sigma_Tn_e .
\]
\(\sigma_T=6.6524587321\times10^{-29}\mathrm{m}^2,\ c=299792458\mathrm{m\,s^{-1}}\); proper number density cm^-3 to SI times 10^6. Native proper time is elapsed seconds after mean zbar20. The normal observer for all relative directional redshifts is at the zbar19.99 endpoint, **not z=0**.

LRS metric \(\mathrm{diag}(-c^2,a^2e^{-2b},a^2e^{-2b},a^2e^{4b})\). Directional redshift at fixed observer-local direction cosine mu:
\[
1+z_{\mathrm{rel}}=(a_o/a_e)[(1-\mu_o^2)e^{2(b_e-b_o)}+\mu_o^2e^{-4(b_e-b_o)}]^{1/2}.
\]
Define \(\tau_0=\frac12\int_{-1}^1\tau_{\rm dir}d\mu\),
\(\tau_2=\frac52\int_{-1}^1P_2(\mu)\tau_{\rm dir}d\mu\),
\(E_{\tau_0}=\frac12(\tau_{0,+}+\tau_{0,-})-\tau_{0,0}\),
\(O_{\tau_2}=\frac12(\tau_{2,+}-\tau_{2,-})\).

At relative redshift z_rel=0.0004:

| Native local_target | ZERO x_HII endpoint | ZERO tau0 | E_tau0(+/-0.005) | O_tau2(+/-0.005) |
| --- | ---: | ---: | ---: | ---: |
| 1e-5 | 0.00021578209362370935 | 2.485765180180353e-8 | 1.3740470822680565e-13 | -2.400042360111409e-10 |
| 3e-6 | 0.00021570243360720105 | 2.485183177433566e-8 | 1.3772041770856828e-13 | -2.399862676853289e-10 |
| 1e-6 | 0.00021553672988191408 | 2.484158331120798e-8 | 1.3804325025103512e-13 | -2.399733466069069e-10 |

- Endpoint x_HII difference |level2-level1|=7.96600165e-8; |level3-level2|=1.65703725e-7; attenuation ratio=2.0801367 >1.
- At z_rel=0.0004, corresponding odd τ2 difference attenuation ratio ≈0.7191 but scalar even τ0 ratio ≈1.02256. At z_rel 0.0001 and 0.00025, odd τ2 ratios ≈1.9605 and ≈1.5998. Thus no **uniform contracting three-level Cauchy evidence**, regardless of the small per-goal relative changes.
- Correct classification: observed controlled native numerical differences / NOT_ASYMPTOTICALLY_VERIFIED, **not** generalized mathematical nonconvergence, not known true-error estimate and not failure of the physical equations.
- In the original code `adaptive_step`, one full tentative BE-source/geometry step is compared to two half steps, and the accepted state is the two-half-step result. `error_metric` normalizes gas, thermal and photon component discrepancies. `last_error` is that local control metric, not a global τ goal-error bound, as in Cao & Petzold's distinction.

## 3. Native scalar change versus signed geometry

For each fixed tolerance, q=+0.005 and q=-0.005 have **exactly identical sampled mean-a and proper t arrays**, all rows. For the refined→ultra pair, the maximum shared/even electron-density correction is 2.908746913e-10 proper cm^-3, whereas the odd/antisymmetric correction is only 1.958763691e-21 cm^-3 (ratio 6.734e-12).

A counterfactual adds the **same** measured even electron-density correction to both signed refined histories, while keeping their b(a), a(t), and clock fixed. Recomputed odd directional τ2 changes reproduce the actual refined→ultra Oτ2 shift within ~0.03% at all 3 tested relative redshifts (0.0001,0.00025,0.0004). This is a useful source sensitivity diagnosis, **not** proof that the measured common density correction or a particular numerical operation causally explains the true-error budget.

It is NOT valid to assert that common even electron-density error cancels out of the signed odd τ2; the b-dependent directional emission-time mapping makes common scalar n_e perturbations relevant to the odd τ2 observable.

## 4. Separate native Rust free-streaming semigroup defect

Original code `rust/rei_microphysics/src/axbi_driver.rs`: `Driver::geometry_map` transports each photon stock between geometry snapshots, then **deposits onto the fixed physical-energy nodes after every map**. `Driver::deposit` assigns a packet to the two adjacent energy nodes with linear barycentric weights, preserving number/first energy moment away from boundaries. No aggregate error-control theorem for repeated remapping is provided in original code.

We compiled an independent local Rust probe linking the original `librei_microphysics-2db3552c92b16edc.rlib` (SHA256 `44b7ea58b04b58e521a2db2686a4b248040414a733120c22689e857ed40d2a3f`). It uses the actual public Driver/geometry_map method, no source injection or chemical stage, and starts with exactly one monoenergetic photon at source energy index 5. It varies only the number of remap substeps.

Example, q=0 and zbar20→19.8 (freeflight exact energy remains above the minimum bin):

| property | one geometry map | 4096 geometry maps |
|---|---:|---:|
| initial packet energy [eV] | 16.3651518618212 | same |
| exact final energy [eV] | 16.2092932726610 | same |
| surviving energy variance [eV²] | 0.06839903484297 | 0.09132206997640 |
| variance excess | reference | +33.5137% |
| physically unsupported leaked photon count | 0 | 8.4501581e-6 |

The direct 4096-step result has 6 populated energy bins versus two for the single map. The single-step physical packet is still at E_end=16.2093 eV > E_floor=13.6 eV, so this leakage is a **demonstrated numerical effect in collisionless free flight**, not physical photoabsorption.

Thus at fixed spectral resolution,
\[
R(\Delta t_2)R(\Delta t_1)\ne R(\Delta t_1+\Delta t_2)
\]
for the actual discrete remapper. More time steps can increase numerical spectral spreading even though photon-number and integrated energy ledgers remain internally consistent. In the much shorter native zbar20→19.99 segment, energy variance changed ~1.256% between 1 and 4096 maps for the same index, and boundary leak ~3.18e-12, NOT proven dominant for coupled x_HII drift.

**Constructive fix candidate:** preserve individual covariant photon-energy characteristics/cohorts through collisionless transports and perform fixed-grid projection only at controlled physical interaction points, or implement a consistent positivity/number-energy preserving transport operator whose semigroup and discretization error are verified. `axbi_q_reference::CovariantPhoton` is already in the repo as a reference for exact geodesic free flight. Full production physical closure cannot be replaced solely by this diagnostic without validating absorption, emission, group thresholds, energy and momentum ledgers.

## 5. Acceptance and handoff

- All nine original native runs completed, all config/source/binary hashes and original partial-line byte replay checked.
- Python new native 28 tests PASS, plus previous parent adapter 33 and directional module 19 tests. Total 80 tests across three disjoint suites when rechecked.
- Local Rust probe compiled and executed successfully; independent numerical/source artifact (no cargo workspace, no Codex).
- This loop retains two independent failure classes: (i) empirical native tolerance refinement is non-contracting for several observables; (ii) exact collisionless repeated spectral remap has a semigroup defect. **Do not assert** that (ii) causes all of (i) without a controlled same-physics replacement experiment.
- Rerunning the full 5-case z=4 EoR campaign would be premature. The shortest next constructive experiment is a small q=0 and ±0.005 frozen-gas and frozen-photon A/B that isolates energy-grid re-projection while keeping source thermodynamic closure and exact photon event ledgers, followed by two-dimensional convergence in both time tolerance and photon energy-grid resolution. Compare objective τ0, τ2, x_HII and energy/number ledgers at matched mean a and matched clock. Goal admission remains HOLD.

**Background literature:** Cao and Petzold (2004), *A Posteriori Error Estimation and Global Error Control for Ordinary Differential Equations by the Adjoint Method*, SIAM J. Sci. Comput., DOI 10.1137/S1064827503420969; Sandu & Miehe (2010), *Forward, tangent linear, and adjoint Runge–Kutta methods for stiff chemical kinetic simulations*, Int. J. Comput. Math.; Fleury, Pitrou & Uzan (2015), PRD 91 043511 (directional Bianchi I light propagation); Friedrich et al. (2012), MNRAS 421, 2232 (H/He photon-conserving chemistry).

## 6. Source and evidence pointers

- Native plan and 9 run receipts: local archive `~/archives/HE18_AXBI_NATIVE_GOAL_20261015/experiment_001`, `experiment_002`. Each original source output has immutable SHA recorded in receipts.
- Read-only coded research lane and machine-readable results: `research/bass_he16_transfer_20261015/native_goal_convergence_20261015/`.
- The raw science outputs have no claim of a publication-ready or truth-certified observation. Byte identity of source files, summary content identity and scientific equivalence are separate.

## 7. 종료된 중단 실행 및 독립 ledger 재검산

원래 Rust `geometry_map`를 재빌드/재실행한 충돌 없는 48개 시험에서 raw `REMAP_SEMIGROUP_LEDGER.csv`의 앞선 수치 열은 기존 `REMAP_SEMIGROUP.csv`와 byte-level value identity를 유지했다. 각 시험에서는 `source_n=1`, `source_u=E_initial`의 별도 입력 ledger를 등록하고 원본 `Driver::residuals` 함수로 number/energy 잔차를 직접 검사했다. 최대 절대 number 잔차는 3.1086244689504383e-15, 에너지 잔차는 1.4635341549773528e-13 eV/H이며 48개 모두 PASS. 기존 송신부나 보존법칙을 수정한 것이 아니라 같은 native crate의 원 메서드를 그대로 링크한 검증이다.

연속 원형 자유전파의 정확 에너지 이동량이 한 간격당 αΔE, 0<α<1/2인 균일 격자 toy에 대해, 한 번에 2αΔE를 이동하여 projection한 확률질량은 (1-2α,2α,0), 두 번 각각 αΔE를 이동하며 재투영한 확률질량은 ((1-α)^2,2α(1-α),α²)이다. 두 분포 모두 photon number 1과 mean energy shift -2αΔE를 보존한다. 정확한 분산 차이는 `Var(Rα ◦ Rα) - Var(R₂α) = 2α²(ΔE)² > 0`이다.

이 유리수 항등식은 Python Fraction 및 Wolfram CAS로 독립 검산했다. 단 이는 가산적 에너지 이동·균일 격자의 국소 toy 증명이며 실제 Bianchi 에너지 이동의 전체 오차 상계나 실험에서 관측된 분산비의 해석식이 아니다.

부모 수치 postprocessor 33개, 방향별 광학깊이 19개, 이번 native 21개, 총 73개 테스트를 각각 Ubuntu에서 재검산한 결과로 판정한다. 전체 9개 native output와 48개 remap 증거 파일 165개의 원본 바이트에 대해 read-only SHA256 manifest를 생성했다. 그 원본은 112156456 bytes이며, 각 run의 binary/config/source/history identity와 native `scientific_admission=NOT_ISSUED`가 변경되지 않았다.

## 8. 실패의 원인 분류와 다음 최소 코드 실험

(1) 국소 BE full-versus-two-half estimator의 full 및 half candidate는 같은 총 구간에서 서로 다른 횟수의 `geometry_map`와 source/thermal stage를 포함한다. (2) `geometry_map`의 고정 physical-energy node reprojection은 이산 semigroup이 아님을 실제 Rust·Wolfram/정확 유리수 toy에서 각각 확인했다. 따라서 local error metric에는 시간 적분 truncation뿐 아니라 photon spectral reprojection difference도 혼합될 수 있다. **그렇다고 이 성분이 관측한 HII 수렴성 drift의 실제 주원인이라고 증명한 것은 아니다.**

실제 다음 연구에서는 native 수렴성 실험과 같은 아주 작은 emission/opacity 구간에서 두 가지 transport lane을 동일한 원자 반응률과 full photon-number/energy/threshold ledger 아래 병렬 비교하는 것이 우선이다. 첫 lane은 원래 per-substep energy-grid reprojection, 두 번째는 `CovariantPhoton`의 continuous characteristic을 보존하고 실제 photon collision/absorption event에서만 projection한다. 원래 solver owner의 frozen production source를 조용히 교체해서는 안 되며, 먼저 별도 experimental driver와 test/native source record를 구축해야 한다.

기존 원본 warm HE18 source certificate를 cold AXBI의 rigorous τ error guarantee로 승격하지 않았다.

## 9. Signed-q covariant characteristic A/B, full-source epoch distinction

An extra standalone Rust program directly links CovariantPhoton::energy_at and original Driver::geometry_map, testing q_ref=-0.005,0,+0.005 for zbar20->19.8. One projection matches the exact characteristic endpoint energy at machine precision, but 4096 projections give surviving-photon relative energy biases 1.40120e-6, 1.37193e-6, and 1.34313e-6 respectively, with photon boundary losses 8.63203e-6, 8.45016e-6, 8.27129e-6. Each source crate number and energy ledger is consistent to <1e-12. See SIGNED_COVARIANT_FREEFLIGHT_RESULT.md and results/REMAP_VS_COVARIANT_CHARACTERISTIC.csv.

Provenance qualification: the standalone remap probes were linked against librei_microphysics-2db3552c92b16edc.rlib, with full compiled source identity fa00a6f73f45e8ac391b5bb723b30d162005bf79750138b1a13e84ec82248f67. That identity is DIFFERENT from the original nine-run frozen binary source epoch d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185. We checked the ten Rust function bodies used for the specific geometry/deposit/freeflight mapping and background calculation, which are byte-for-byte identical across frozen source, linked rlib source, and current source. This **does not certify whole-source or whole-binary identity**. The remapper semigroup counterexample remains source-scoped to these tested functions.

Original 9 native chemistry+photons runs used the exact frozen original binary with SHA256 32d11e733155d355a1fa748597b48ea1c8196adba3c871722a7a598f0b6cbfca. These runs are not relabeled as built with the separate rlib.

The audited original raw evidence consists of 169 files, 112156456 bytes, with individual SHA256 manifest under results/RAW_SOURCE_SHA256_MANIFEST.json. Combined Python suite count after source-surface, signed-freeflight and manifest tests: 33 parent + 19 directional + 28 native = **80 tests** (full final verification evidence retained).

Scientific admission remains HOLD. Next physical change is an explicitly isolated covariant-packet/collision A/B at fixed atomic source and H/He threshold ledger, not an unsupported automatic replacement of production code.
