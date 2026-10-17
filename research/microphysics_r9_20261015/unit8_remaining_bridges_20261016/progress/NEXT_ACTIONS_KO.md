# 다음 실행과 입력 의존성

1. **T4 기존 계산 회수:** PR151의 unit5_t4_resume_20261016/actual_ncp_20261016 기록과 NCP allocation REI-R9-UNIT5-20261016T024854Z_99ca7c에서 zero-H residual 후처리의 종료 receipt/log/result를 읽는다. 원 deadline은 2026-10-16T04:48:54.971486Z다. 현재 프로세스는 이 대화에서 검사하지 않았다. 새 H-action·Lanczos·SCF·FCI나 deadline 재설정 없이 이미 생성된 결과만 회수/검토한다. 128차 checkpoint를 다시 만들지 않는다.

2. **A Li 독립 시간적분:** 원 BDF와 한 번의 dyadic-balanced BDF 모두 u=.567329164975에서 floating-step stall을 보였다. 같은 BDF를 반복하지 않는다. 저장 rate table, Radau 출력, 부분 state, Jacobian과 메시지로 새 수치표현/독립 propagator를 정식화하고 실제 population norm에서 검증한다. 기존 수용 오차를 느슨하게 하여 통과시키지 않는다. 실제 초기 wall은 UNKNOWN이며 보수적 accounting은 receipt에 남겼다.

3. **T3/T6 다음 물리:** LiH 유한 곡선 밖의 short/long-range potential과 formation/collider channel이 있어야 저온 반응률을 정한다. Gamma에서 계산한 전자 운동에너지는 Coulomb/역 Compton 재분배 모듈의 입력이다. 분자 abundance·collisional population·electron thermalization을 주지 않고 실제 우주론적 냉각/가열이라고 부르지 않는다.

4. **T5/T7 불확실성 확장:** D는 small8 모델의 source-native prior64 표본이다. 기존 large59 donor에 같은 covariance를 붙이지 않는다. Large-network 차이와 joint charge history의 공유 parameter 전파가 다음 계산이다. Conditional bare17 출력은 사상 검증이며 물리적 matching surface는 별도다.

5. **외부 T8 중복 방지:** RUN09의 다음 노드는 P4-S4C-SPECTRAL-EDGE-SUPPORT다. Source/driver/inputs가 백업에 있고 birth r4와 H/D 문턱 cell부터 positive spectral refinement를 하는 기존 계약을 재사용할 수 있다. PR192의 native budget policy와 PR193 geometry guard를 동일 source라고 가정하지 않는다. 해당 owner의 최신 상태를 읽고 한 번만 수행한다.

Unit8 portable package와 private full backup에 source·입력·실제 결과를 보존했다. 사용자가 수동으로 파일을 준비할 필요 없이 Codex가 게시된 package를 취득할 수 있다. 자동 재현은 기존 receipt를 덮지 않는 새 명시적 allocation으로 수행한다. 필요한 NCP 회수 prompt는 최종 응답에서 직접 복사할 수 있다.
