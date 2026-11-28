# HE32 최적화 코딩 루프

## C1–C2: 목표와 기존 코드 경로

완료 기준은 이 단원만 복사한 환경에서 입력 준비, 실제 z=20→2 적분,
성분별 응력 sweep, 그림 생성, 저장 결과 재사용을 실행하는 것이다.
직접 baseline은 HE31 `88e415c45d8607c85cd3ab36aabeaed4378820ce`이며,
원 canonical FV, species hierarchy, Legendre source와 HE31 prepared moments의
바이트를 `evidence/BASELINE_MANIFEST.json`으로 고정했다. 원 repo/worktree는 보존했다.

최신 intake는 `evidence/intake/`에 있다. 새 ACCEL03·C21N·D9 근거를 구분해
재사용하며, 그 결과가 없는 전구간 H/He/Li 화학을 완료 상태로 상속하지 않는다.
새 물리 입력과 기존 collisionless donor는 서로 다른 실행 identity를 갖는다.

이 단원의 원자망 범위는 첨부한 원시핵종 그림을 확장한
n, H1, D, T, He3, He4, Li6, Li7와 각각의 원자 전하 0..Z이다.
이 음이온·분자 없는 원자 I–IV 상태 공간을 21 heavy species로 정의한다.
전자 수는 이온 전하의 합에서 계산한다. 원자핵 생성/파괴와 원자 이온화를
별도 소유하며, 반응의 활성 여부와 근사 오차를 다음 물리 루프에서 확정한다.

## C3: 정확한 짝수 부분공간

`J_l=<F P_l>`, `F=sum_l(2l+1)J_l P_l`에서 기존 forward 연산자는

\[
 L_p F=3\mu(1-\mu^2)\partial_\mu F-p(3\mu^2-1)F,
 \qquad p=4\ (energy),\ 3\ (number).
\]

부분적분과 Legendre 미분 항등식으로

\[
 L_p^*P_l=-3l\mu P_{l-1}+3(l+3-p)\mu^2P_l+(p-3)P_l.
\]

따라서 연결은 l−2,l,l+2뿐이다. reflection-even 초기 자료와 Thomson 산란은
짝수 부분공간을 보존한다. 새 코드는 이 항등식을 유리수 계수로 구성한 뒤
binary64로 바꾼다. `N0'=0`, `E0'=-2(s/H)E2`를 정확히 표현한다.
원 4개의 energy/number tower를 전부 보존하고 홀수 모멘트와 항상 0인
gas-energy placeholder만 제거한다. L8에서 40개 상태가 23개로 줄어든다.
이는 closure 차수의 감소가 아니다. 원 full state 복원 함수도 제공한다.

질량 입자의 양의 canonical FV 셀과 HE31 준비 quadrature를 재사용한다.
각 RHS는 FV moment를 한 번 평가하고, 같은 H로 geometry·shear·radiation을
계산한다. 출력용 dictionary는 출력 시점에만 구성한다. 원 reduction order와
유리수 계수의 반올림 차이는 같은 수치 기준 아래 독립 비교한다.

## C4–C5: 구현과 실행 자원

실제 샌드박스는 CPU quota 8, affinity 9, memory.max 8 GiB이다.
계산은 별도 케이스 프로세스와 프로세스당 native thread 1개로 실행한다.
다른 작업의 존재를 중지 조건으로 쓰지 않고 실제 가용 RAM·CPU에 따라 worker
수를 제한한다. 케이스별 content identity와 원자적 저장으로 재개한다.
기존 Fortran/MPI 권고는 현재 사용자가 명시한 portable sandbox 목표에 맞춰
NumPy/SciPy 경로로 적용한다. 컴파일·NCP·인터넷은 배포 후 실행의 필수 조건이 아니다.

수치 적분기는 SciPy 1.17.0의 기존 DOP853 비교와 신규 stiff 원자망용
implicit solver를 사용한다. 새 원자망에서는 종별 abundance 크기가 다른 문제를
각 핵종의 전하 fraction으로 정규화한다. tolerance를 완화해 최적화를
성공시켰다고 기록하지 않는다. source-domain 밖 rate fit은 연결하지 않는다.

## C6–C9: 변경 의존성의 독립 검증

별도 검토자가 원 forward polynomial을 직접 유리수 적분해 새 adjoint와
대조하고, source full RHS·적분과 비교한다. 검사는 행렬, 정확한 영 모드,
proper-time/H 연결, 초기 물리축, 약한/강한 shear 두 궤적에 집중한다.
원본과 새 구현은 같은 L8·quadrature·DOP853 `rtol=3e-11`, `atol=3e-13`을 쓴다.
성능 benchmark나 반복 suite는 실행하지 않는다. 실제 수치와 판정은
`evidence/optimization/`의 실행 기록을 따른다.

## C10: 다음 의존성

최적화 루프가 독립 비교를 통과하면 다음 단계는 P.R1–R10이다.
그 단계는 21상태의 광이온화/재결합, 초기 조성, UV/열 입력,
핵반응 freeze-out 오차와 넓은 물리적 stress 범위를 확정한다.
그 후 F.C1–C10에서 새 화학 결합 IVP와 실제 parameter sweep을 실행한다.
