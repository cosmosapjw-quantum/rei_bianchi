# RCT STEP01 standalone add-on 수신

Supplier3355cd79의 구현된 add-on을 수신했다. 기존 설계를 다시 구현하지 않았다.
수신/byte identity/event arithmetic은 PASS이며 owner dispatcher 및 numerical-budget
채택은 PENDING이다. 원 time_integrator_RCT_binding_accepted=false를 유지한다.

실제 Dropbox 복구 archive SHA256:
`cd204b1533c79a2610b0b923a420d71b3f4816b5a660010333dd0dac5d89e7b9`.
150918bytes/CRC/86payload manifest와 원 addon SOURCE_MANIFEST를 확인했다.
Vendor34파일은 REI41e4592의 실제 Git blob와 일치하며 현재8e8ea0의 FT03/he_rct
blob도 같다. 역사적 lib와 최신 전체 crate는 다르므로 whole-current-crate 수락은 없다.
첫 archive parser의 manifest.files 가정 실패는 MANIFEST_SHAPE_FAILURE.json에 보존했다.
실제 schema의 payloads mapping을 읽어 확인했으며 원 bytes는 바꾸지 않았다.

| 요구사항 | 근거와 확인 범위 |
| --- | --- |
| OFF baseline 위임 | 원 source의 ft03_implicit_step/adaptive_step 직접 호출; sender parity 시험 수신 |
| RR/CI/DR 보존·RCT 별도 | combined_ft03_rhs 호출, 별도 RctIntegral; source/시험/원 실행 identity 대조 |
| accepted half1+half2·transaction | 두 half 장부 합산과 마지막 state/count 동시 commit; sender 성공/rollback 시험 수신 |
| explicit event budget | EventControl에 Default 없음; 고정12개 로그의 실제 API 연산 순서로6수락/6거절 확인 |
| underflow 구별 | nonzero finite product의 zero만 거절; 원0채널은0. Uniform subnormal/rounding proof 아님 |

새 수신 경계10시험 PASS(원8개와 아래 static scope2개). 기존 native15시험과36endpoint/12root 검산은 sender의
기존 실행으로 구분했다. 이 loop의 native0, reference root0, scientific suite replay0.
지정 native 시험의 검사 결과를 현재 전체 crate의 새 PASS로 재집계하지 않는다.

새 exploratory budget은 aJ=1e-14 events/H,rJ=2e-4이며 반드시 caller가 제공한다.
Owner의 production error budget으로 채택하지 않았다. dt1e8/1e9는 수락,
dt1e10/1e11은 기존 state gate를 통과해도 RCT_EVENT_LOCAL_ERROR로 거절된다.
Full/half 사건수 차이는 exact-flow error certificate가 아니다.

Probe는 abs(Jfull-Jhalf)/nH와 곱셈 후 나눗셈을 기록한다. API는 먼저 Jfull/nH와
Jhalf/nH를 구한 뒤 차를 취한다. 두 binary64 연산 순서의 차이를
EVENT_ARITHMETIC.json에 따로 보존했다. 12개 판정은 일치하며 로그를 실제 API의
bitwise event_error로 부르지 않는다. 새 허용오차나 clamp는 도입하지 않았다.

재검사: `python3 -B -W error -m unittest discover -s 이_폴더 -p test_event_receipt.py -v`.
수학/solver 새 구현이 아닌 저장된 입력의 산술·수락 범위 검사다. 전체 실행 패키지는
INPUT_IDENTITY.json의 Dropbox ID/archive hash로 식별하며 binaries/ZIP을 Git에 재배포하지 않았다.

배포 영수증은 당시 tool safety-status로 Git ref 갱신이 차단됐다고 기록한다.
이 원 영수증은 inputs/DELIVERY_RECEIPT.json에 보존한다. 실제 현재 branch에는
3355cd79가 이미 존재함을 read-only로 확인했다. 원 차단 요청은 여기서 재시도하지
않았으며 원 tool의 승인 상태가 해소됐다고 추론하지 않는다.

다음은 owner의 EventControl/underflow 계약 검토와 REI-F08 파일 예약 후 actual
build/dispatcher 연결이다. 이미 구현된 addon의 채택 또는 예약된 원 source로 이동 중
한 경로만 선택한다. Build context가 바뀐 범위에 필요한 시험만 실행한다.
원 runner는 전체 end-to-end 미실행 보고이며 여기서 재실행하지 않았다.
Owner 재현에는 기존 commands의 `RUSTFLAGS=-D warnings`도 명시적으로 유지해야 한다.

RCT OFF, source moments null, HE-F3 empty common domain/F09 대기, physical HOLD,
Eq55 NOT_RUN, legacy PARKED_OPEN 유지. Consumer mutation0; ChatGPT 직접 전송은 미검증이다.

게시 직전8d6da91의 STEP02-STATIC 반환을 non-force fast-forward로 보존했다.
원 addon은 불변이다. 별도 caller의 실행 SHA를 확인하고12static trajectories와
2800accepted macro steps/campaign, continuous reference 오류/refinement는 author 보고로
수신했다. STEP02 전체 ZIP·raw trajectory·reference는 여기서 복구/재실행하지 않았다.
Local estimator 합을 certified flow bound로 승격하는 입력과 직접 전자항0을
보고된 population feedback0으로 바꾸는 입력을 두 추가 시험에서 거부했다.
LATE_STATIC_INTAKE.json은 이 좁은 report scope와 unchanged-source 결속을 보존한다.
새 supplier DELIVERY_RECEIPT는 STEP01의 정상 non-force 게시 복구도 기록한다.
원 과거 safety-status 실패 영수증과 당시 원문은 계속 보존한다.
