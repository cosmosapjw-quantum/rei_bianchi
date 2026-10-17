# P4 보조 gate: 외부에서 주어진 affine 광원·흡수율

소비 대상은 다음 source-age 공동 시간적분 설계의 독립 기준 계산이다. 이번 구현은 scalar photon count에만 적용된다. H/He/D 종별 사건 배분이나 가스 변화, Bianchi 기하를 호출하지 않는다. 이전의 fixed-geometry cohort 결과를 수정하거나 승격하지 않는다.

## 계약과 구현
고정 proper volume과 광자 에너지에서 j(t), lambda(t)를 구간 양 끝의 비음수 값으로 정의한 affine 함수로 가정한다. 기존 광자 optical depth는 사다리꼴 적분으로 정확히 계산한다. 출생 광자는 두 양의 Gauss 노드에서 주입량과 birth→endpoint optical depth를 계산해 생존·흡수에 같은 가중치를 사용한다. 둘 다 상수인 경우 기존 Phi 정확식을 재사용한다.

변수 계수 경로는 구간 전체 optical depth<=1만 허용한다. 이 조건은 정확도 보증이 아니라 지원 영역이다. 더 큰 구간은 거부하고 호출자가 분할해야 한다. 계수의 endpoint는 외부에서 정한 물리적 함수의 표본이어야 하며, 시작 gas 값을 복사해 물리적으로 정확한 affine history라고 주장하면 안 된다.

정적 검토에서 subnormal rate를 먼저 절반으로 나누면 큰 dt를 곱하기 전에 주입량이 소실되는 문제가 발견됐다. h*j, h*lambda endpoint 적분부터 계산하도록 수정하고 rate/time 재척도화 회귀 검사를 추가했다. 양의 곱이 0으로 underflow하거나 overflow하면 거부한다. 변수 계수 경로의 양의 subnormal endpoint 적분은 지원하지 않으며 fail-closed 한다. 상수 경로는 기존 hardened Phi를 사용한다.

## 실제 검증
- 새 API 부재 RED 보존, 최종 affine Rust 테스트10개 PASS.
- 그 전 단계에서 기존 uniform-birth21개 회귀 검사도 PASS; 마지막 수정은 affine module만 바꾸었다.
- 증가·감소·교차 affine 세 경우와 상수 한 경우를 N=1,2,4,8,16,32로 계산한24행 결과를100자리 mpmath 적분과 비교했다.
- 세 affine 사례의 N32 생존량 절대 차이: 5.2742893e-10, 6.8868776e-10, 5.9945977e-10. N16→32 관측 차수는 각각3.99938,4.00061,4.00053이다. 이는 정확히 affine로 주어진 이 세 함수에 대한 결과다.
- SymPy에서 optical-depth 적분식 및 두 Gauss 가중치의 총 주입량 잔차가0.
- 정상 지원 범위 독립 코드 검토 PASS_SCOPED. Clippy 미실행 유지.

이 방식은 affine 함수가 정확히 주어진 경우에만 위 고차 거동을 보였다. 일반적인 부드러운 함수를 endpoint 선형 보간하면 그 보간 오차 때문에 보통2차로 제한되고, coupled gas의 predictor/splitting 오차는 별도다. 어느 결과도 전체 solver의2차/4차 정확도 승인이 아니다.

## 다음 연결을 막는 핵심 계약
종별 opacity 비율이 시간에 따라 변하면 total absorption을 한 시점의 lambda_i/sum(lambda)로 나누면 안 된다. 각 종은 integral lambda_i(t) N(t) dt의 공동 시간적분이 필요하다. 비율이 구간 내 상수인 제한 경우에만 total absorption의 고정비 배분이 가능하다. 따라서 이번 scalar API는 종별 사건을 출력하지 않는다.

## 누적 비용과 상태
이전 작업20회에서 이어 명령30회, 합 wall26.696080s / child CPU26.817213s. bounded cap300s/600s는 재설정하지 않았다. 전체 프로젝트의 과거·미계측 비용과 잔여 예산은 UNKNOWN이다. 과학 장구간·로컬/NCP·Wolfram 실행은 추가하지 않았다.

DAG: 외부 affine scalar quadrature PASS_SCOPED; 시간 의존 종별 공동 사건·가스·Bianchi 결합 HOLD. 이 보조 gate를 완료한 뒤 필요한 다음 연구는 종별 사건과 생존 photon을 동시에 보존하는 공동 quadrature 계약이다.
