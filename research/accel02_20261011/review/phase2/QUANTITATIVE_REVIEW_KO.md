# ACCEL02 phase2: 새 시간 refinement의 독립 판정

**PROMOTE_SCOPED_FIXED_GRID_TEMPORAL_REFINEMENT_AND_CONSERVATION**으로 판정한다. 범위는 FLRW,128개 energy×2개 angle node에서 같은 conditional Case-A/HM12 방정식을 z15.9→4까지 적분한 EVENT_COUPLED001/002의 시간 오차 비교와 fine run의 보존 ledger다. N2 전체 DAG 완료, 스펙트럼 연속극한, 비등방 paired history 또는 실제 EoR 관측 해석은 아직 승격하지 않는다.

두 실행은 source/native/base/event-driver identity, IC, geometry, energy·angle grid가 동일하고 rtol만10⁻⁹→10⁻¹¹로 강화했다. 실행 당시 원 driver와 base driver의 보존 파일 해시가 IDENTITY 기록과 일치한다. 같은129개 epoch의 저장값에서9개 field의 오차 요약을 직접 산술 재확인했다. 최대 normalized difference는 photon density의1.423172774×10⁻⁸로 기존2×10⁻⁶ 기준보다 작다. 온도 최대차이는7.76169×10⁻⁵K다. 이는 두 허용오차 설정의 empirical agreement이며 절대적인 연속계 오차 증명이 아니다.

Fine run의 segment endpoint와 common epoch를 모두 포함한 energy residual 최대는 초기 에너지 대비5.248135677×10⁻¹¹, photon-number residual은 초기 H수밀도 대비5.010378246×10⁻¹⁰다. 두 값 모두 원래10⁻⁹ 기준을 통과한다. coarse run의 약4.064×10⁻⁸ photon-number 실패는 그대로 보존되며 판정기준은 완화되지 않았다. 에너지 좌표에서 energy ledger가 선형 불변량이 되는 특성만으로 photon-number 검증을 대체하지 않았다.

P2-01의 endpoint-only 집계 문제는 최종 comparison에서 두 집합의 최대를 사용하여 해결되었다. P2-02는 과거 실행을 소급하여 완전검증으로 바꾸지 않고 정확히 범위를 제한했다. 모든 accepted step의 photon positivity는 기록되어 있지만 gas domain은129개 저장 epoch와 Newton RHS stage에만 근거한다. EVENT002의 all-accepted gas-domain 여부는 NOT_EXPLICITLY_MEASURED로 남는다. 향후 driver에는 accepted gas-state 검사가 추가되었으며 이 추가로 과거 실행을 재표기해서는 안 된다.

첫 broad whole-interval native integration과 시간 refinement는 실제 완료되었다. 다음 판단은 EVENT003의 spectral change 및 angular/shear 증거에 한정하면 된다. RUN002 또는 변경 없는 이전 point suite를 다시 실행할 필요는 없다.
