# HE-RCT-STEP01-ADDON: 별도 Rust 구현과 고정 입력 검증

판정은 SCOPED_ADDON_NATIVE_PASS__OWNER_ADOPTION_PENDING이다. 기존 설계 C1-C4를 실제 compiled/tested Rust crate bass_he_rct_step_addon으로 구현했다. 원 consumer source/dispatcher는 수정하지 않았다. F08 owner 예약과 원 root/TASKS는 보존하며 global HE-F2, HE-F3, physical admission을 승격하지 않는다.

## 실행 구조

실행 dependency는 REI 41e4592aa494b48929dcd23fc8504c169a98a908의 full crate다. Drive RCT01 ZIP493387bytes/SHA25606252b274959f247ca386b9410e7d28248e7710bc79524bb3d9d586a19525534를 실제 복원하고34vendor파일을 원 manifest와 대조했다. 현재 관측 REI8e8ea0c664e2ba2f2f8560e0c64266d206fbd50f의 ft03_controlled/he_rct blob는 같다. 최신 전체 crate/F08 빌드나 수정은 아니다.

OFF는 기존 ft03_implicit_step/ft03_adaptive_step에 직접 위임한다. 활성 경로는 고정 proper nH,nHe, 단일 k와 명시적 고정 Ebar를 사용한다. 양성 species block에 I_H+=k*nHe*z_guess, HeIII loss+=k*nH*(1-x_guess)를 추가하고 실제 combined_ft03_rhs를 후보 열/escape와 최종 endpoint 잔차에 사용한다. 기존 RR/CI/DR/photo는 보존한다. 최종 endpoint의 RCT는 별도 RctIntegral 장부이며 accepted half1+half2만 합한다. 실패 시 state와 external accumulator 모두 commit하지 않는다.

## 새 사건수 오차 계약

J는 proper cm^-3 사건수다. eJ=abs(Jfull-(Jhalf1+Jhalf2))/nH를 aJ+rJ*max(abs(Jfull),abs(Jhalf1+Jhalf2))/nH와 비교한다. 코드의 실제 계산 순서는 full/half counts를 각각 nH로 나눈 후 차를 취한다. EventControl에는 암묵 default가 없고 이번 exploratory 입력은 aJ=1e-14 events/H,rJ=2e-4다. owner의 production budget 채택은 별도이며 step-doubling은 rigorous exact-flow bound가 아니다. 기존 residual1e-14, strict state error<2e-4, proper floors1e-30과 invariant 기준은 그대로다.

실제 controlled FT03 초기조건, KF96와 합성 Ebar=Q에서 dt1e10s의 상태 차이는9.33461502e-7이라 기존 state gate를 통과하지만 eJ=4.89543404e-14 events/H가 허용1.99302549e-14의2.46배여서 RCT_EVENT_LOCAL_ERROR로 거절된다. dt1e11s도 state7.65501039e-5<2e-4이지만 event budget은39.1배 초과한다. dt1e8/1e9s는 채택된다. 이는 선택한 작은 RCT 사건수의 error control 문제이지 원자율 정확도 또는 관측량 중요도 판정이 아니다.

새 rate/energy/event 경계에서는 비영 finite factor의 곱이0이 되면 RCT_PRODUCT_UNDERFLOW, 원래0채널은0으로 구분한다. 원 provider는 바꾸지 않았으며 모든 subnormal/덧셈소실/균일 rounding 인증을 주장하지 않는다.

## 실제 검증과 실패

8개 API의 stub assertion RED를 확인한 뒤 구현했다. 첫 구현에서dt1e10을 성공으로 예상한 시험은 event gate 때문에 실패했다. 허용오차를 바꾸지 않고 acceptance 예제를dt1e9로 옮기고dt1e10은 explicit rejection regression으로 보존했다. 최종15native tests(2unit+13integration), warnings-as-errors build, rustfmt가 통과했다. 기존 mixed2/274와116/F04/F05과학 suite는 재실행하지 않았다.

12개 implicit scenarios(Ebar Q-1,Q,Q+1와dt4개)의 full/half1/half2 총36끝점과 adaptive6accept/6reject를 기록했다. 별도 Python/mpmath90자리 식 구현으로36endpoint residual과12numerical root를 대조했다. max scaled residual3.944448110974106e-16, max scaled root difference1.196918295633169e-16, max RCT count relative difference1.270024289870378e-15다. 이는 동일 저자의 독립 수치 계산경로이며 independent scientific review=NOT_RUN, interval certificate=false다. isolated BE reference는 이전 HE-F2C rct_reference.py bytes를 그대로6case에 재사용했다.

## 전달과 다음 노드

전체 실행 source/tests/vendor34/oracle/실패 및 성공 로그는 BASS_HE_RCT_STEP01_ADDON_20261005_v1.zip에 있다. Git에는 이 요약, 반환/수치계약, source identity, 입력 pin, 실제 test log와 다음 지침을 게시한다. Git 요약 checkout만으로 실행 가능한 전체 source가 있다고 가정하지 않는다. 정확 ZIP/cloud identity는 DELIVERY_RECEIPT.json을 따른다.

새 패키지 runner는 bash syntax 검증했고 그 구성 명령들은 각각 실제 실행했다. runner 전체의 한 번짜리 end-to-end 재실행은 하지 않았다. Rust1.94.1 archive SHA는 기존 pin과 일치하나 GPG 공개키/서명 검증은 완료하지 못했다. 도구체인/binary bytes는 ZIP에서 제외한다.

다음은 owner가 실행 모듈과 event/underflow 계약을 수락하고 reserved build/dispatcher에 연결하는 일이다. 원 source 수정 또는 중복 구현은 아직 하지 않았다. HE-F2global=false, HE-F3 WAIT_REI_F09_RESULT, baseline RCT OFF, source moments null, physical HOLD, Eq55 NOT_RUN, legacy PARKED_OPEN을 유지한다.
