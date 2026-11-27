# HE-F2C: 명시적 조건부 local RHS 수락

완료 범위는 새 RCT 반환의 입력·영수증 검사와 조건부 local RHS binding이다.
HE-F2 전체/물리 admission/시간 적분기/F09 완료를 선언하지 않는다.
현재 상태의 근거는 `RETURN.json`, `REACTION_BINDING.json`,
`CONSUMER_LEDGER_ACCEPTANCE.json`, `INTAKE_VERIFICATION.json`이다.

## 소스 진술과 전달된 모형

KF96 1e-14 cm3/s, 1000–1e7 K와 GM25 1.70e-13 cm3/s, 200–10000 K는
서로 다른 nominal source다. source code SHA256은 논문 SHA256이 아니다.
KF96 isotope unresolved와 명시적 W82 ground-state 시나리오는 공급자 packet에 보존된다.
KF96 primary는 넓은 호출 구간을 위한 명시적 코드 선택이며 물리적 우월성 판정이 아니다.
두 소스를 합산·자동 전환·clamp·외삽하지 않는다. 공통 비교 구간은 1000–10000 K다.
actual FT03 30000–110000 K에서는 GM25를 거절한다.

## 전달된 유도·명시적 근사

종 순서 HI,HII,HeI,HeII,HeIII,e에 대한 사건 벡터는 (-1,1,0,1,-1,0)이다.
proper density 곱은 소비기에서 한 번 적용하고 직접 자유전자 변화는 0이다.
반응당 광자 birth 1은 primary absorption이 아니다.
조건부 escape closure는 source moment를 사용하지 않고 caller의 유한 양수 Ebar를 요구한다.
Chemical -QR, thermal (Q-Ebar)R, escaped Ebar R의 항등식은 전달된 모형의 ledger다.
열 나머지의 음수도 허용한다. 모든 primary photon이 tracked field 밖으로 escape하므로
tracked injection=0이며 미제공 moment를 0으로 치환한 것이 아니다.
CountOnly 열/광자 에너지/spectrum은 null이다. provider heat/recoil/spectrum도 null이다.
이는 스펙트럼·recoil·흡수 확률·우주론적 역사의 예측이 아니다.

## 실행 증거와 이번 검사

native code 41e4592, 문서 pin 7a15daa, supplier code 21d5b80을 분리한다.
최종 native 116개, E2 12789 assertions/422 calls, E2X 212 assertions/12 calls의
PASS와 독립 POST_FT03_REVIEW confirmed/open0는 이번에 해시로 결속한 기존 증거다.
초기 104개 FINAL_REVIEW는 역사 기록으로 보존하며 FT03 최종 검토 대신 사용하지 않는다.
이번에 실행한 테스트는 손상·잘못된 scope·count/rate 혼동·null 변환 등의 입력 경계 17개다.
Draft202012 스키마 2개, 저장된 입력 15개, 공개 source 8개, supplier core 2개를 검사했다.
원자 suite/native 전체/수치 oracle/감도 campaign의 새 실행은 0회다.

actual ft03_rhs를 합성하는 typed wrapper는 원래 RR/CI/DR을 보존한다.
원래 FT03의 nonzero-product underflow 거절은 RCT increment가 계승하지 않는다.
기존 유한점 검증은 uniform 상대오차나 underflow 인증이 아니다.
Q±1/Q Ebar는 합성 검증 입력이며 원자 스펙트럼 예측이 아니다.
기존 implicit_hhe_step/ft03_implicit_step에 RCT가 연결된 것으로 수락하지 않는다.

## 재개 및 전달

두 baseline RCT는 OFF, source physical HOLD, F04 fullfalse, HE-L1/L2/L3 parked,
Eq55 미승격, HE-FLRW02B mixed-native pending을 유지한다.
다음 소비기 RCT-STEP01은 실제 stepper 결속·affected numerical contract가 필요하다.
HE-F3는 실제 REI-F09 paired 반환을 기다리며 공급자가 별도 campaign을 실행하지 않는다.
변경 입력이 없으면 이 검사를 반복하지 않는다. run_intake.py는 결과를 create-only로 쓴다.
다음 audit는 새 execution 경로에서 새 pin으로 수행해야 한다.

ChatGPT URL의 직접 본문 수신/메시지 전달은 확인하지 못했다.
Git handoff와 `../CHATGPT_SYNC_KO.md`로 전달할 기록을 보존한다.
추정 CSV 경로 HTTP404와 RED 실패 로그는 보존됐으며 실제 CSV는 FETCH_DELTA에 고정했다.
staged diff 검사에서 unittest RED subtest 출력의 trailing space를 발견했다.
FORMATTING_FAILURE에 기록하고 RED.log와 이를 인용하는 두 실패 로그의 whitespace attribute만 제외했다.
실패 증거의 원본 바이트와 SHA256은 유지하며 코드·계약 문서의 diff 검사는 계속 적용한다.
