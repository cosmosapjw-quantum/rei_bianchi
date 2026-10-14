# 원자 세 스레드의 실제 갱신과 다음 작업

GitHub의 각 research branch, 모든 현재 branch 목록(각 100개 미만), 최근 PR, 최신 commit 변경 파일과 관련 원문을 확인했다. 읽은 원문은 `../survey/atomic/SOURCE_IDENTITY.json`에 바이트·SHA256·Git blob identity로 묶었다. 새 과학 실행은 별도 `../loop1/he_mixed/`의 혼합 H/He native 검사 두 개뿐이다. 나머지 기존 시험 수는 수신 증거이며 재실행 수가 아니다.

| 스레드 | 고정 head / PR | 현재 결과 | 남은 owner 입력 |
|---|---|---|---|
| BASS_HE | 28c3da1455915672ff3e41d8ecd06a6deccb9a78 / 17 | F2C 조건부 local RHS 수락; F2D S0 직접 RCT exposure 상한 완료; 이번 mixed native 2개 PASS | RCT-STEP01 실제 stepper/stage 장부; 공통 source-domain을 가진 F09 입력. 새 mixed 결과의 supplier 수신 ACK |
| bass_cr | 3c7d7d4b811dd5f6eeafe60bafa1308a52dc1cf2 / 23 | F04C 온도의존 4변수 잔차·J/H 유도/구현; 실제 CR-off receiver 증거 없음 | 실제 REI source/loader/callback 관측. F04D를 할 경우 새 parent·두 half 계약 |
| WU088_HH | 3b5e7c3dc151b23db434f0ce60af383bb19dd5e7 / 33 | F07 S0 HH-OFF 결정 수신 완료. Optional HH parked; S0를 막지 않음 | 실제 HH-off runtime 장부. Opt-in 연구 재개 시 새 provider/domain/owner 계약 |

## 동기화에서 제거할 오래된 대기

HE의 `CURRENT_FASTEST_STATE.json`은 이제 local RHS acceptance=true다. 예전 `WAIT_OWNER_OPT_IN_AND_PROVIDER_CONTRACT`를 현재 결과로 반복하지 않는다. F2C isolated exact/BE reference는 실제 native stepper가 아니며, F2D 직접 forcing 상한도 coupled observable 차이 상한이 아니다. F2D는 기존 F04 static 완료를 수신했고 S0 baseline에 새 필수 gate를 추가하지 않는다.

HE-FLRW02B의 actual native test가 소비기 b553698a에는 없었다. 실제 cargo missing-target exit101을 보존하고, 원 supplier ZIP의 새 제안 하나만 byte-identical하게 별도 harness에서 컴파일했다. `AtomicProvider::reference`, `hhe_rhs`, `homogeneous_photo_rates`를 실제 호출한 2개 시험과 274 비교가 통과했다. 상대 최대 오차는 structural 3.4885067388312133e-16, 독립 source anchor 2.809899931685239e-15다. 허용오차 5e-14 relative + 1e-300 absolute는 바꾸지 않았다. 이는 finite mixed native 실행 공백을 메운 결과이며 HE owner ACK나 full history/physical source admission을 대신하지 않는다.

HH의 `fastest_sync_20261004_v1/CURRENT_SYNC_STATE.json`과 canonical TASKS에 남은 `WAITING_ON_REI_DOMAIN/F07`은 이전 checkpoint다. 최신 `f07_owner_return_20261005_v1/OWNER_RETURN_ACK_SUMMARY.json`이 실제 OFF 결정을 받았다. HH optional F1/F2를 S0 prerequisite로 세우지 않는다. OFF는 물리적 무시 가능성 증명도 loader/callback 0 관측도 아니다.

CR `research/fastest_track_20261005/f04c_temperature_residual/LOOP_RETURN.json`의 10 tests/NOT_FROZEN/F04 partial은 그 자체의 오래된 scope다. 이후 `docs/fastest_track_resume_20261005_v1/F04C_TEMPERATURE_COUPLED_RESIDUAL_KO.md`는 23 tests와 4D Jacobian/Hessian 결과를 보고한다. 최신 REI b553698a의 static F04 완료는 별도로 수신해야 한다. 23과 10을 합산하거나 static 인증을 expanding S0로 확대하지 않는다.

## 기존 진행 경로와 충돌하지 않는 병렬 후보

현재 문서에 지정된 REI-F05/FLRW06, RCT-STEP01, CR-F04D는 owner의 예약된 다음 작업이다. 이 조사만으로 별도 세션이나 host에서 실제 프로세스가 실행 중이라고 관측한 것은 아니다. 같은 구현을 복제하지 않고 owner 경로와 증거 포인터를 먼저 맞춘다.

| 후보 | 병렬 가능 조건 / 소유자 | 산출물과 종료 기준 | 임계 경로 영향 |
|---|---|---|---|
| HE mixed native 반환 수락 | 이번 고정 실행 반환 / HE supplier | source·golden·test·native pin 대조 후 scope ACK; 원자 suite 재실행 없음 | 이번 실행 공백 해소, ACK만 후속 |
| OFF dispatch 관측 | F05의 실제 dispatch 경로가 정해진 뒤 REI owner | CR/HH 각 loader/source/callback zero 관측, 해당 함수/실행 pin, actual skip 분기 테스트 | 생산자 원자계산과 독립; 단순 null을 0으로 쓰지 않음 |
| BASS optical-depth 소비 계약 | expanding state writer와 독립된 BASS owner | proper density/normal-clock stage/grid/observer-tail typed 입력과 source identity; 기존 visibility 연결 사용 | 새로운 원자 provider 필요 없음 |
| F04D original-parent/two-half 표현 | CR 담당; F05와 파일·입력 분리 | mixed parent derivatives 및 half1→half2 의존성. 실제 box 없으면 형식 계약까지 | 보조 인증 lane; S0 baseline에 새 gate 금지 |
| RCT full-response sensitivity 계약 | 실제 admitted baseline Jacobian/stability 정보 확보 후 REI/HE | direct exposure→전체 observable 전파에 필요한 norm/forcing/response 지표의 명시 계약 | 선택 연구; F2D를 재계산하거나 자동 RCT-ON하지 않음 |
| HH optional intake 재개 | 실제 HH opt-in 또는 changed consumer evidence 후 HH | source-domain/distribution/중복 없는 event·heat·binding owner와 cutoff budget | parked; 동일 OFF 상황에서 새 helper/toy를 만들지 않음 |

즉시 새 물리 입력 없이 할 수 있는 최소 원자 gate는 mixed-native 실행이었고 이번에 마쳤다. CR/HH OFF 실증은 receiver 경로가 존재할 때만 의미가 있다. 현재 FT03 온도창 30000..110000 K와 GM25 200..10000 K가 겹치지 않으므로 OFF/KF96 결과를 HE-F3의 paired source campaign 완료로 부르지 않는다. 이 논리적 blocker는 clamp, guard 완화, 자동 provider 교대로 해소할 수 없다.

## 게시 경로와 보존

각 branch에 `docs/atomic_reionization_handoff_20261004_v1/threads/<repo>/consumer_returns/REI-REC-BASS-SYNC01_20261005/`를 additive successor 경로로 쓰는 것이 적절하다. 파일은 `SYNC_STATE.json`, `NEXT_STEP_KO.md`, `SOURCE_BINDING.json`, 필요한 scoped 결과 포인터다. 기존 CURRENT/TASKS/과거 receipt를 덮어쓰지 않고 새 기록이 어떤 오래된 상태를 해당 scope에서 대체하는지 명시한다. 기존 PR17/23/33을 그대로 쓰고 non-force append만 수행한다. 정확한 publication parent는 쓰기 직전에 다시 읽어야 한다.

HE: attached 원자 PDF를 재배포하지 않는다. unchanged source suite를 다시 실행하지 않고 scientific approval과 immutable identity를 구분한다. CR: `docs/READBACK_POLICY.md`의 R1 기본을 사용하고, authority/import/복구 등 R3 trigger가 실제로 있으면 영향 객체에 한정한다. 참조된 `.codex/readback-policy.json`은 이번 pin에서 404였으며 정책 MD는 존재한다. HH: frozen native/reference와 vendor/orchestration bytes·기존 실패·24/289 및 265 unbounded/epsilon null/B22 OPEN을 유지한다. 실제 scientific full49 promotion이나 무거운 재계산을 암시하지 않는다.

직접 ChatGPT 스레드 메시지 전달은 이 조사에서 수행하지 않았다. 각 스레드용 Git handoff를 게시하는 것과 실제 스레드 수신 ACK를 구분한다.
