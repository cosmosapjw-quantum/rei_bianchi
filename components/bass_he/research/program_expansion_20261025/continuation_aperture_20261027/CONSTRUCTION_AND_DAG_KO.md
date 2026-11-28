# 구성 후보와 실행 DAG — R4/C4

## 검토한 표현

| 표현 | 계산식과 사용 조건 | 이번 선택 |
|---|---|---|
| lab density의 branch별 적분 | `Σ ρ(μ_i)/|F'(μ_i)|`를 lab 창에서 적분. Fold에서 적분 가능한 특이성을 적절히 다뤄야 함 | 선행 ANGULAR06 결과로 유지. 이번 구현은 CM 구간을 직접 적분 |
| CM 역상의 정확한 구간 포함 | `I⊆F⁻¹(A)⊆O`, rational root bracket와 양성 polynomial 적분 | 이번 reference 구현과 결정론적 오차 경계 |
| 두 detector의 유한 φ patch | `(μ,φ)→(F(μ),φ)`와 딸입자 `(−μ,φ+π)`에 대한 2차원 사건 indicator | 실제 기하·φ 분포를 결속하는 후속 후보. 이번 annular 범위의 후속 의무 |

단일 사건의 paired map은 `μ→(F(μ),F(−μ))`다. γ=1,a=0,ρ=1/2, A=[1/2,1],B=[−1,−1/2]의 첫 구성 예에서 coincidence=1/2, 각 사건 hit=1/2이므로 hit 곱1/4와 구분된다. 이 예는 상관을 보존하는 최소 판별량이다.

## 새 계산 제품과 의존성

1. `APERTURE07-CERTIFIED-PREIMAGE`: 기존 map/branch에서 rational 부호 판별과 inner/outer 집합을 구성하고 검토한다.
2. `APERTURE07-POSITIVE-PAIR-MEASURE`: 양성 밀도의 정확한 적분·signed 모멘트·공유 사건 집합과 오차 경계를 구성하고 검토한다.
3. `APERTURE07-VALIDATED-REFERENCE`: 위 두 제품을 구현한 실제 실행·수렴·저장 데이터 그림·독립 결과 검토를 완료한다.

기존 완료5개와 열린 물리 입력3개를 그대로 계승한다. 새 제품은 아직 pending이다. 합계11개 중 현재완료5개이며, 중앙28/88에 이 개수를 더하지 않는다.

## 실행과 비용

- 첫 구현 검증은 canonical S05 source를 고정한 뒤 `python -B scripts/run_validation.py`로 수행한다. 기존 wrapper의 누적 CPU4s/wall15s, childCPU3s/wall10s, memory256MiB,1thread를 유지한다. 원인과 남은 자원이 있는 targeted repair만 최대1회다.
- R7은 새 Bernstein/weighted 항등식과 제조 예에 대한 Wolfram symbolic call1회(timeConstraint15s)다. 기존 map 유도나 완료된 과학 suite를 다시 실행하지 않는다.
- C8은 새 검증이 저장한 데이터만 읽는 plot1회다. CPU6s/wall15s/memory512MiB,1thread, scientific calls0으로 제한한다. 과거 PHOTON05 plot을 고치거나 새 plot으로 덮어쓰지 않는다.
- 준비·백업·게시·모델 작업의 자원은 위 실측 envelope 밖이며 UNKNOWN_NOT_ZERO다. 새 CPU 한도는 이전 reserve에서 가져오거나 reset한 값이 아니다.

검토 PASS는 다음 실제 실행으로 연결한다. 실행 결과와 비용을 보존하고, 코드·수학·입력 변경이 없다면 검증을 반복하지 않는다. C10 이후에는 요청한 이 루프를 종료하고 다음 스레드에 정확한 남은 입력과 이어갈 위치를 넘긴다.
