# ISO-COUPLE P4/S3: 실제 retarded photon birth-time, 경로 불투명도와 H/He/D 양의 스펙트럼 참조

2026-10-17 KST. **독립 bounded reference**. 이전 P4/S2 source-native release와 PR #184 HEAD `4e82783f560d26589a646f64473359299ed9f977` 위의 add-only 연구. PR #150 owner `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7`를 포함한 기존 12개 원본 source는 불변. 자연단위계를 적용하지 않고 `c=299792458 m/s`, `k_B`는 original owner, 시간 s, 에너지 eV/J, metric `(-,+,+,+)`. Bianchi-I는 비물리적/물리적 혼동을 피하기 위해 주어진 prescribed off-shell axisymmetric background로 한정.

## R5. Source-age와 네 종 경쟁 흡수에 대한 식

대각 Bianchi-I Killing momenta `P_i=a_i(t_b) E_b n_i(t_b)`에서

\[
E(t;t_b,E_b,\mathbf n_b)=E_b\sqrt{\sum_{i=1}^3n_{b,i}^2\left[\frac{a_i(t_b)}{a_i(t)}\right]^2}.
\]

`N`은 기준 **comoving m³당 광자수**, `j(t_b)`은 동일 부피당 초당 광자 방출, `kappa_i(t)`는 **proper s⁻¹**. 오직 광자 출생 이후만 전파한다.

\[
N(t_1)=N(t_0)\exp\{-\int_{t_0}^{t_1}\kappa(s)\,ds\}
+\int_{t_0}^{t_1}\! j(t_b)\exp\{-\int_{t_b}^{t_1}\kappa(s)\,ds\}\,dt_b,
\quad \kappa=\sum_{i\in\{\mathrm{HI,HeI,HeII,DI}\}}n_i^{\rm proper}(t)c\sigma_i[E(t)].
\]

각 경로에서 원래부터 있는 광자 또는 출생 quadrature node 광자에게 별도로 `N_old exp(-tau_segment)`를 적용한다. Stage path microinterval `[a,b]`의 gas composition은 midpoint 고정하며 `n_i(t)=n_i(t_mid) V(t_mid)/V(t)`를 **화학 변화 없는 gas background**로 사용한다. \(\tau_k=\kappa(t_{k+1/2})\Delta t_k\)에서 정확한 고정계수 흡수 \(A_{ik}=N_k(1-e^{-\tau_k})\kappa_i/\kappa\), 생존 \(N_{k+1}=N_ke^{-\tau_k}\)은 nonnegative. 이를 채널마다 합하면 각 진화구간 `N_begin=N_end+ΣA_i`가 성립한다.

출생 적분은 source-native `AxbiSource::source_births(t_b,dt*w_b)`를 이용한 **positive GL2/GL4**. `birth_time_s`와 그 때의 `birth_geometry`를 cohort에 실제로 보존한다. 원본 source MD14/BB50k, z=4..20, 13.6..100 eV, GL8 각도; 임의 유효 스펙트럼을 새로 추측하지 않는다. Time-varying source를 이용한 독립 512-part Simpson emissivity test를 통과했다.

## R5/R7. D threshold 불연속과 새로운 스펙트럼 선택지

Original `AxbiSource`는 각각 16개의 H/HeI/HeII threshold segment로 48개 number-weighted mean energy cell을 생성한다. D-photo는 정확한 동위원소 단면적이 아니라 **원본 H-equality D model**의 `sigma_HI(E)`를 `E>=chi_D`에서만 사용한다. 여기서 원본 `HHeModel` 결합 경계 \(\chi_H=13.598434599702\,\mathrm{eV}\), 제조된 \(\chi_D=13.602134599702\,\mathrm{eV}\), 원본 Verner H photo-fit threshold \(13.60\,\mathrm{eV}\)는 다른 물리적 source labels다. D 문턱이 original 첫 source spectral cell 내부에 있다.

`positive_spectral::SplitPositiveGauss3`는 그 cell을 \(\chi_D\)에서 별도 분할하고 각 subinterval에서 3점 **양의** Gauss node를 평가한다. 광자 수의 가중치는 원본 blackbody number shape \(E^2/[e^{E/k_BT_{BB}}-1]\), \(T_{BB}=50000\,\mathrm K\)를 사용하고 **각 original cell photon fraction을 정확히 재정규화**한다. 다른 47개 cell에서는 각각 3점 노드, D 첫 셀에는 6점, 총 147 energy nodes×GL8 = 1176 photon quadrature points per birth time. GL4 birth이면 4704 새 cohort per macrostep. `OriginalCellMean`도 비교자로 보존한다. Source continuous spectrum의 absolute physically calibrated inference는 아니다.

**제한:** 이 버전의 path opacity time microsteps는 각 구간 중간 energy와 density를 평가한다. Energy threshold crossing을 root-finding으로 정확 분할한 통합 적분은 **미구현**이므로, 큰 단계·문턱 근처의 error는 HOLD. 다른 온도·원자단면적 모델을 도입하지 않았고, 제조된 \(\chi_D\)를 관측값으로 승격하지 않는다.

## R5. 광자-화학-열 에너지 장부와 검증계층

Absorbed photon energy는 **흡수 시각의 ray energy** \(E(t_{k+1/2})\). 각 species event 수 \(A_i\)에 대해 `thermal=(E-chi_i)A_i*EV_J`, `binding=chi_i*A_i*EV_J`를 원본 P2 microphysics에 한 번만 전달한다. `DAtomicProvider`의 원래 `d_atomic_rhs` signed-source self-check, nuclei positivity, Savin T domain과 final gas ledger를 통과할 때만 state commit. P2의 CI/RR/CX/CE/FF/CMB는 `use_photo=false`로 호출하여 광이온화 이중 계수 없음.

Photon-redshift work per cohort는 계산상 `W_gamma,ledger=(N_final E_final-N_initial E_initial+Σ A_k E_mid)*EV_J`, 즉 광자 에너지 identity로 정의된다. 이것 **자체**를 독립 에너지 검증 증거라고 주장하지 않는다. 별도로 `W_gamma,ind ≈ Σ N_k phi(tau_k) [E(t_{k+1})-E(t_k)] EV_J` 경로 적분을 수행하여 교차 비교하고, zero-opacity Killing limit에선 원래 exact ray를 이용해 독립 검산한다. Gas는 여전히 midpoint에 에너지를 넣고 반step adiabatic drift를 하므로 결합 시스템의 전역 시간차수는 일반적으로 1차. Photon birth와 opacity에만 새 세분화를 적용하여 **full coupling precision**을 보증하지 않는다.

## R7/C6-C8. 실제 검증 증거와 error axes

- Rust 1.94.1 offline/locked; inherited P3/P4S2 75 tests + new P4S3 9 tests = **84/84 PASS**, Clippy `-D warnings` PASS. 원본 12 files SHA-256 byte identical. Rustfmt는 새 source/tests/examples만 검사.
- 실제 Rust native owner 경로: FLRW + BI shear+ 각각 4/8/16 macrosteps × P4S2 phi, retarded GL2/m2, GL4/m4, D-edge-split GL2/m4, D-edge-split GL4/m8 = 30행. 추가 matched full source time/opacity axes와 N32/N64 partial total 41 unique rows. Completion count와 HOLD는 `evidence/NATIVE_SCIENCE_ANALYSIS.json`을 참조.
- Manufactured \(j=1.7(1+0.25t^2)\), \(\kappa=0.3+1.1t+0.7t^2\), \(0\le t\le1\), \(N_0=2.3\)의 독립 SciPy quad reference survival `1.77194797016994`. N64, GL4, opacity m8 상대오차 `1.45675e-7`에 도달하고 마지막 관측 수렴차수 `1.995`. 이 수치는 **scalar manufactured**에만 적용됨.
- Actual HHeD FLRW N16, **동일 GL4/m8 opacity**에서 original 48-cell mean과 D-edge-split spectrum의 DI cumulative relative difference = `-3.717052668887888e-4` (= −0.0371705%). N16 H photon events relative difference = `-1.3885e-5`, remaining photons `+2.05199e-4`. Opacity m4↔m8 DI relative `-4.30e-11`, 따라서 현재 scope에서 spectral contrast와 temporal-opacity discretization을 분리함. 이는 절대 오차나 continuum convergence를 증명하지 않음.
- 모든 실제 native complete rows에서 maximum photon number ledger relative = `5.348168609880589e-15`, total-energy step max relative = `5.786284392383937e-16`. Independent geometric-work comparison max relative to cumulative emitted energy `2.660843557518173e-8` (coarser N4/GL2/m2), 감소 양상은 실험 설정에 종속.
- Observed native coupled survivor time difference orders: P4S2 `(N16,32,64) p≈0.996`; retarded GL4/m4 `(N16,32,64) p≈1.072`, retarded D-split GL4/m8 `(N8,16,32) p≈1.127` (N64 retarded-split failed runtime budget). Full 2nd order **NOT ADMITTED**.
- N64 native D-split GL4/m8 timed out in bounded extra campaign; 5 previously completed rows retained, missing sixth explicitly `RUNTIME_TIMEOUT_NOT_RUN_TO_COMPLETION`. Source photo-advection integration is \(O(N_t^2 \times N_{birth}\times N_{spectral}\times N_{opacity})\) due retaining and replaying every age cohort; real production cost blocker for large N. Do not impute this row or mark convergence PASS.

## R8/R9/C10. 단계 판정 및 다음 일

`P4/S3: PASS_SCOPED_BIRTH_TIME_PATHWISE_OPACITY_AND_D_THRESHOLD_REFERENCE` if all fresh verification commands pass. Full P4 `PARTIAL`, SA-01/02 `HOLD`, FLRW-CONV `HOLD`, BI-SIGNED `HOLD`, FULL_EOR `HOLD`. No on-shell Einstein shear/tilt, no real reionization observable \(\tau_T\) admission. Next DAG P4/S4: threshold-crossing root- or event-aware time quadrature, source-age compression avoiding \(N_t^2\) cost while preserving positive multichannel photo owner; separately bind on-shell BASS source histories and independently converge age/time/spectrum/angle before publishing science claims.

## Original literature used for method comparison, not code correctness proofs

1. Abel, Norman & Madau (1999), [Photon-conserving cosmological ray transfer](https://arxiv.org/abs/astro-ph/9812151). Photon-number-conserving source/sink algorithm.
2. Mellema et al. (2006), [C²-Ray](https://arxiv.org/abs/astro-ph/0508416), DOI 10.1016/j.newast.2005.09.004. Photon event budget and analytic relaxation for ionization fronts.
3. Mackey (2012), [Accuracy and efficiency of raytracing photoionisation algorithms](https://www.aanda.org/articles/aa/full_html/2012/03/aa17984-11/aa17984-11.html). First- versus second-order photoionization schemes and multi-frequency limitations.
4. Verner et al. (1996), [photoionization fit source](https://www.pa.uky.edu/~verner/photo.html), DOI 10.1086/177435. Original source fits already present in immutable PR150 owner.
