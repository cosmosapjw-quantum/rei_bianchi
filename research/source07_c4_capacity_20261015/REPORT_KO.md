# REI SOURCE07 C4: 방향 보존 및 메모리 한계에 근거한 q-수송 실행 구조 선택
2026-10-15 KST, selected C4 execution/resources stage. 실제 repo Rust에 source-bound scoped pilot/test를 작성, 빌드, 실행. 사용자 최종 목표는 non-tilted axisymmetric Bianchi-I + matched FLRW의 H/He abundance와 gas T 이력이다. 원 MD14 source, Case A, proper-clock, signed q_ref와 기존 output·AX07–AX16 scientific admission을 보존한다. C5 생산 이력 구현은 별개로 남는다.

## 1. 두 photon 단일 압축에 대한 새 정리 (exact-real; 범위 명시)
LRS Bianchi I에서 a_perp=a exp(-b), a_parallel=a exp(2b), 0<|mu|<1인 같은 LOCAL 방출 방향 n에 대해, 방출시각 t_j의 공간 공변운동량 k_j=a_j E_j n는
k_z/k_x=exp(3b_j) mu/sqrt(1-mu²)
를 만족한다. 그러므로 b_1 != b_2면 k_1,k_2가 일반적으로 collinear하지 않다. 같은 source angular index는 그 사실을 고치지 못한다. N=N1+N2와 K=N1 k1+N2 k2를 보존하려면 한 packet 평균 kbar=K/N으로 정해진다. 임의의 동일 future geometry에서 photon energy E(k)=||A^{-1} k||_2 (k는 에너지 단위)를 사용하면
N1 E(k1)+N2 E(k2)-N E(kbar) >= 0.
양수 N1,N2에서 실제 손실 없이 등호가 성립하는 것은 두 physical ray momenta가 같은 비음수 방향에 있을 때(또는 하나가 진공/영가중치일 때)다. 정확한 제곱 gap는
(N1 |p1|+N2 |p2|)^2 - |N1 p1+N2 p2|²
=2 N1 N2 (|p1||p2|-p1·p2), p_j=A^{-1}k_j.
근사적으로 b=0 주변 angular derivative dθ/db=3 μ sqrt(1-μ²). 방향별 photon energy의 단일-covariant-vector 압축은 다른 시각 LRS에서 일반적으로 양의 energy deficit을 만든다. 이는 모든 형식의 복사장 압축 자체에 대한 불가능성이 아니라 **단일 양의 질량 없는 q-ray 대표자를 통한 모든 1차 모멘트 동시 보존**의 제약이다.

실제 owner AxbiBackground의 q=[-.01,-.005,0,+.005,+.01]로 z20,z11에 각100eV mu=.5로 방출한 두 광자를 z4에서 비교: q=-.01의 상대 결손 2.8353145e-6, q=+.01의 상대 결손 2.7695335e-6, q=0에서는0. q=+.01의 sin(q direction angle)=0.004935466... (저장된 source input geometry). 이 수치는 제조된 두-광자 observable이지 완성된 abundance 이력의 shear 효과가 아니다.

## 2. 실제 Rust C4 component 구현
새 rust/rei_microphysics/src/axbi_q_capacity.rs, tests/axbi_q_capacity.rs, examples/axbi_q_capacity_pilot.rs 그리고 lib.rs에 모듈 1줄 등록. 기존 axbi_driver.rs, axbi_sources.rs, atomic_provider.rs, bianchi_i.rs 및 STATE bytes는 변경하지 않았다.
TaggedPhoton에는 angular_key와 실제 CovariantPhoton(k_i, N/H)이 들어간다. assess_merge는 ray별 q collinearity, 현재/forecast 에너지 결손, HI/HeI/HeII fit cutoff를 통한 미래 단조 redshift 구간, fixed neutral H/He absorption events/photoheat의 절대 국소 예산을 체크한다. Fail은 reason을 담아 반환하고 원 패킷은 유지한다.
cap_packets은 adjacent-energy candidate를 탐색하며 cap까지 근사 O((N-cap) N logN) 과정을 수행한다. 따라서 이 버전은 production merge 알고리즘이 아니라 source-bound feasibility/reference용이며, N<=65536 입력 guard와 cap 절대 예산, 잘못된 k 입력 검사를 유지한다. max source packet + thermal component가 2GiB 이하라는 전체 프로그램 보장은 아니다.
경계가 겹치지 않는 두 snapshot을 통해 전체 구간 문턱 부재를 보장하려면 photon E(t)의 중간단조성이 추가로 필요하다. 선택된 owner signed |s|/H<=0.01에서는 H_perp=H-s>0,H_parallel=H+2s>0이므로 양의 photon energy가 감소한다. 임의 비단조 외부 background에서는 endpoint만으로 같은 보장이 되지 않는다. 또한 q 벡터 collinearity는 floating sin angle<1e-12 + 양 endpoint E slack<1e-12 상대수치 규칙으로 판별하므로 byte-identical covariant momentum proof라 주장하지 않는다.
현 국소흡수 예산값은 실제 x_HI, n_HeI로 초기 z20 proper gas n을 적용한 절대 허용오차이며, full feedback propagation certificate가 아니다.

## 3. 실제 계산 결과
Physical MD14 z20의 48 energy cells per source angular bin ×8 directions =384 TaggedPacket을 cap256으로 줄였다. 128 merges. TaggedPhoton size40 B. Tag payload은 15,360 B ->10,240 B (33.3% 감소)이며 실제 Vec capacity, temporary bank 및 source caches 등은 별도다.
Source count 4.29803611476420e-10 photons/H, source energy 8.7149539291624e-9 eV/H는 source initial metric에서 비트 출력의 반올림 내 유지.
Frozen proper absorber, dt=1e8s: 기존 HI event baseline6.56465982707e-12 photons/H, 압축 후 delta -5.22967303405e-14 photons/H => -0.79664%. HeI baseline1.96625860209e-13, delta-1.9426756338e-16 => -0.09880%. Baseline photoheat2.49894654214e-11eV/H, delta +3.19413216993e-13eV/H => +1.27819%. HeII 초기 density0으로 event0. 이 absolute local budget은 cap policy HI1e-13/HeI1e-13/HeII1e-13 photons/H, heat1e-11eV/H를 통과하지만 **엄밀한 반응 정확도 조건이나 전체 우주론 source-history 수렴성을 통과했다는 뜻은 아니다**.
Release cap의 독립 실행3회 중앙값: q=-.01 25.433802ms, q0 24.750803ms, q=+.01 24.726267ms per one384->256 contraction. 이 알고리즘을 매 EoR step 호출하는 것은 비용과 오류축 측면에서 아직 바람직하지 않다. 전체 200000step raw source cohort 384*200000*32=2.288818GiB는 2GiB budget을 초과하며 (추가 Vec/source/solver/output 제외), 성공적으로 cap된 256 TaggedPacket state payload은10KiB이다. 다만 다른 emission epoch의 실제 LRS 방향별 병합이 거절되므로 전체 역사에서 256을 항상 달성한다고 주장하지 않는다.

## 4. 채택한 C4 자원 선택
우선 fixed covariant-q **energy × angular** grid, 대표 coarse N_E64 N_mu8, pilot128×16, reference256×32, refinement512×32. 예를 들어 four binary64 arrays를 가정한 raw state 크기(방출/absorption/heat/trace arrays의 의도만 지정, 아직 실제 구현 아님):
64×8×4×8 B=0.015625MiB,
128×16×4×8=0.0625MiB,
256×32×4×8=0.25MiB,
512×32×4×8=0.5MiB.
이 수치는 solver, cache, interpolation, quadrature, checkpoint 등 전체 RAM이 아니고 source representation의 예산 초안이다. 실제 production source reference-energy support E*∈[13.6,432.2293723205]eV, E_t=R E*, eta_ref=R J_Ω eta_t(E_t), phi(E_t) positive, and moving HI/HeI/HeII thresholds must be handled in quadrature/coupled time steps. Angular quadrature directions are truly fixed q, not "same local mu each injection" rays.
Explicit state-space compression, directional q moment invariant and threshold tube error/budget requires distinct C5 work; bass_cr PR66 has scalar-energy frozen-neutral bound only and was NOT copied as universal q certification. Existing C2 per-cohort q benchmark remains the independent sparse oracle.

## 5. Verification, other-repo reuse and next
New C4 Rust 7 focus tests PASS incl exact FLRW-same-direction merge, actual signed b-family cross-time HOLD, fit threshold-tube HOLD, cap below 3 partitions transaction HOLD, source384->256 count/E, and new RED→GREEN invalid NaN packet even when under cap. Real prior C3 and owner tests check via fresh cargo test and all-targets command. Wolfram15.0.0 xAct1.3.0/xCoba0.8.6 returned 19 scalar zeros and5 tensor zeros after adding explicit *real* assumptions to a square-root triangle identity; first RawJSON attempt failed with complex-branch un-simplified radical, preserved separately. This is self-consistent same-author independent code paths, not external peer review.
Read actual bass_cr PR66 head 0a43dcb... (v2), which accepts actual owner q energies up to50keV but is not a vector-q angular certificate. BASS_HE PR58 is warm P01 second-cell, BASS PR152 angular-cap C6 and WU088_HH PR73 atomic radial certificates; no source constants or error-radius transplantation.
Next **C5** should directly implement actual fixed q grid with R J source pushforward and source/H/He moment quadrature, windowed event-aware absorption, versioned checkpoints, and a short same-source/frozen-gas+matched FLRW/LRS comparison. Full signed AX08 retained source and scientific admission NOT_ISSUED; no old campaign replay, scheduler changes, or forced production migration.

Native subagents: NOT_RUN, current host has no spawn/delegate; implemented directly via ChatGPT remote Ubuntu.
