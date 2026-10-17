# rei_bianchi P4/S10: 내부 CX와 외부 timestep의 공통척도 예산 정책

2026-10-17. Parent PR190 HEAD `512f765fd5d7496381cd4089cea4bd980b06c5f8`. P9 원본 ZIP 식별자 SHA256 `024fcc02b15d53c7816c9d888f98b5ec637fdcb875456028cf9f342c5f696446`는 선행 영수증에서 읽었다. 이번에 ZIP의 바이트를 다시 검사하거나 P9 프로그램을 실행한 것은 아니다. 이번 변경은 새 경로의 독립 정책 프로토타입과 증거만 추가한다. 원래 production PR150, P9 및 이전 source/branch는 변경하지 않는다.

## 결과 상태

**P4/S10 PARTIAL: THEORY_DERIVED_AND_WOLFRAM_CHECKED; RUST_POLICY_AUTHORED_UNCOMPILED.**

container 명령, 진단 echo, Python 및 별도 visible Python 초기화가 모두 실행 전 ServerError를 반환했다. Rust 설치 여부나 컴파일러 버전을 현재 런타임에서 확인하지 못했다. 따라서 이번 native Rust tests/build/Clippy/solver campaign은 NOT_RUN이다. 선행140개 PASS를 이번 테스트 결과로 계승하지 않는다. 네이티브 subagent도 NOT_RUN_UNAVAILABLE이며 Wolfram 계산을 subagent review로 부르지 않는다.

## 1. 선택한 문제

P9 문서와 PR190은 외부 step-doubling 차이와 내부 thermal-CX 정밀도를 분리할 필요를 남겼다. 특히 내부 허용오차를 조이면 final DII가 변하지만 일부 다른 채널은 같은 값일 수 있다. 이번에는 상쇄에 덜 취약한 국소 네 계산 비교를 구성하고, 실제 solver에 연결하기 전에 독립 Rust 정책 커널과20개 회귀 테스트를 작성했다. 물리 적분은 아직 연결하지 않았다.

## 2. 정의와 직접 유도

고정된 초기상태Y, 고유시간 구간[t,t+h], 원자율·기하·광원 및 angular/spectral/birth/opacity quadrature를 사용한다. 내부 CX 허용오차 두 수준을 loose,tight로 두고 각 수준에서 C=한 전체단계, F=두 반단계를 계산한다. 두 번째 반단계는 실제 공통 endpoint에 맞춘다. 예측·거부 경로는 상태와 source/energy/event ledger에 반영하지 않는다.

각 물리 관측투영 Q_i에 공통의 양수 척도 s_i를 고정한다. s_i의 단위는 Q_i와 같다. tolerance/referenced magnitude로 만들더라도 전체 inner ladder 비교 동안 동일 값을 사용해야 한다. 서로 다른 pair마다 denominator를 다시 계산하면 아래 같은 norm의 부등식으로 결합할 수 없다.

C0,F0=loose projections; C1,F1=tight projections로 정의한다.

O_i=abs(C1_i-F1_i)/s_i.
I_i=[abs(C0_i-C1_i)+abs(F0_i-F1_i)]/s_i.

실수 대수에서
(C0-F0)-(C1-F1)=(C0-C1)-(F0-F1),
따라서 abs((C0-F0)-(C1-F1))/s_i <= I_i,
또한 abs(C0-F0)/s_i <= O_i+I_i.

0<beta<1에 대해 모든 성분에서 O_i<=1-beta 및 I_i<=beta를 요구한다. beta=1/4는 이번 정책 대조값이지 물리적으로 최적인 값이나 문헌에서 유도된 값이 아니다. 이는 두 tested precision 사이의 변화와 tight step-doubling defect를 분리하는 정책이다. I_i는 tight inner solution의 참해오차 bound가 아니고 O_i도 전체 수송 참해오차 bound가 아니다. 1/(2^p-1)을 적용하지 않으며 모든 채널에서p=2라고 가정하지 않는다.

## 3. 반례와 검산

단위척도1에서 C0=F0=2, C1=1.3,F1=1.1이면 원 loose defect는0이지만 O=0.2,I=1.6이다. 새 정책은 h를 바꾸기 전에 내부 정밀도를 조이도록 반환한다.

반면 네 값이 모두100이면 O=I=0이어서 정책은 수락한다. 독립 참조값이0인 문제라면 실제 오차100을 탐지하지 못한다. 모든 네 값에 같은 b를 더하는 공통 편향은 차이에 나타나지 않는다. 이 예는 이 특정 diagnostic의 한계이며 모든 수치 방법에 대한 no-go나 학술적 신규성 주장으로 확대하지 않는다.

실제 Wolfram Language 실행: [-1,1]의1/4간격9개 값에서 네 endpoint의6561개 유리수 조합을 검사했다. Triangle, mixed-difference 및 수락=>loose_defect<=1 검사가 모두True였다.239개 조합을 수락했고, loose_defect<=1이지만 새 정책이 거부한 조합은4702개였다. 이 숫자들은 실제H/He/D 사례나 통계적 성능지표가 아니라 정확한 유리수 정책 테스트의 개수다. 실제 호출 코드와 결과는 verify_policy.wl 및 VALIDATION.json에 보존했다.

## 4. 작성한 Rust 커널

budget_kernel.rs는 공통 initial/source/projection identity, 정확한 endpoint bits, 두 내부 tolerance의 엄격한 감소, label/unit 일치, 중복·누락 label, 유한값 및 양수 척도를 검사한다. 순서가 다른 label 목록은 이름으로 정렬해 비교하고 coarse/fine cohort index를 맞추지 않는다. 정규화 중 양의 차이가0으로 underflow하면 성공으로 만들지 않고 오류를 반환한다. 이 처리는 directed-rounding interval certificate가 아니다.

내부 budget초과 -> 같은구간에서 tighter pair 계산; 내부통과/외부실패 -> 외부h감소; 모두통과 -> F_tight만 commit; 더 조일수없음 -> StopInnerUnresolved; 작업예산없음 -> StopWorkLimit. 같은구간에서 다음 refinement시 이전tight pair를 새loose pair로 재사용하면 추가pair1회가 필요하다. Native CX ratecall/work limit은 별도로 유지해야 한다.

이 커널은 평가나 상태변경을 수행하지 않는다. plan_next는 순수 decision을 반환한다. 실제 P9 adapter가 각 pair를 동일초기상태에서 실행하고, 각 halfstep의 사건밀도를 자기중간부피로 변환한 뒤 반환해야 한다. 이 adapter는 아직 작성·연결·검증하지 않았다. 기존 adaptive_step API를 읽지 않고 존재하지 않는 method명을 추정하지 않았다.

## 5. 테스트와 정확한 재개점

budget_tests.rs의20개 test는 작성됐으나 Rust로 실행되지 않았다. Wolfram6561검사를 Rust tests PASS로 대체하지 않는다. 런타임 복구 후 첫 명령:

rustc --edition=2021 --test budget_tests.rs -o budget_tests
./budget_tests

그다음 P9 원본을 검증해 실제 projection adapter를 연결하고, 동일 시간구간에서4corner의 HI/HeI/HeII/DI/thermal/photon/source labels 및 units를 비교한다. 허용오차 ladder는 기존1e-8,1e-10,1e-12,1e-14와 normalized atol=rtol*1e-3를 시작 후보로 삼되 실제 측정 전 성능·물리 수락으로 승인하지 않는다. 고정격자 replay와 독립 tighter reference로 local decisions를 검사한다. CI/RR/CX/CMB/광원과 각 단계의source ownership은그대로유지한다. 실패한native kernel/ledger/source/work오류는 단순 정확도거부로 감추지 않는다.

## 6. 문헌과 구분

SUNDIALS CVODE Mathematical Considerations §3.2의 nonlinear/linear iteration error를 local integration error보다 작게 제어하는 설계는 배경 근거다. CVODE의 nonlinear solve와 우리의 CX subflow는 다른 연산이며 그0.1/0.05계수를 물리적 기준으로 복사하지 않았다. 공식문서 확인: https://sundials.readthedocs.io/en/v7.8.0/cvode/Mathematics_link.html
Lee,Mellema,Lundqvist의photoheating adaptive timestep논문은 열과이온화의시간해상도요구가다를수있다는배경이다: arXiv1511.01040, DOI10.1093/mnras/stv2556. SciSpace에서multiscale/dual-weighted-residual 연구도찾았지만이번정책의errorcertificate로사용하지않는다.

## DAG

P4/S9의기존scoped상태는변경하지않는다. P4/S10은PARTIAL_NATIVE_EXECUTION_BLOCKED. FullP4 PARTIAL; SA01/02,FLRW-CONV,BI-SIGNED,FULL_EOR HOLD. BASSon-shell/물리초기조건/전체age·angular·spectral참해보장은미수행. 런타임장애가닫히면이S10의native검증과adapter부터재개하고,자동으로다음연구루프를시작하지않는다.
