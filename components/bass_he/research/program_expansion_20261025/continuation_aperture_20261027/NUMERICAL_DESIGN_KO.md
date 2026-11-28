# 주장·전제와 수치 설계 — R3/C3

## 근거의 구분

| 대상 | 현재 근거 | 이번 단위의 사용 |
|---|---|---|
| ANGULAR06 lab map, 단조 branch, 동일 입자 measure | 선행 직접 유도·26/26 검증·독립 검토, 동일 tree 게시 | 정의·scope·저장 입력을 확인하여 재사용 |
| Rice 유한 기하와 `σ_event=2πA0` | 원전 §3.6·§5.4 시각 판독 | 해당 실험 convention의 예; M0475 정규화와 분리 |
| rational predicate·역상 bracket·signed moment 경계 | 이번 구성적 유도의 대상 | R5 원문과 R6 검토 후 채택 |
| 제조 map·양성 polynomial density | 명시적인 수학 입력 | 일반 알고리즘을 판별하는 제어 예 |
| native12의 저장 γ,a | byte-locked 선행 입력 | 새 창 적분에서만 사용; DCS/error 열은 사용하지 않음 |
| 실제 incident flux·thermal deposition | 결속되지 않음 | 물리 노드 3개를 열린 상태로 유지 |

γ=1,a=5/4 fold 예는 정확한 manufactured map control이다. 특정 질량·입사 에너지 조합에서 나온 실제 γ+α 사건으로 해석하지 않는다. 실제 γ,a의 연결은 저장된 native12 parameter를 사용한 별도 조건부 경로에서 확인한다.

## 수치 경로

1. 유한 int/string/Fraction 또는 저장 binary64 값을 정확한 유리수로 읽는다. bool·비유한 값은 거절한다.
2. 부호를 보존한 rational 비교로 lab 경계와 F(μ)의 순서를 정한다. a>1의 critical μ는 정확히 −1/a다.
3. 각 단조 branch에서 root bracket을 이분하고, 내부·외부 구간 합집합을 생성한다. public stopped 방향은 오류이며 boundary finder만 보조 극한 0을 사용한다.
4. Bernstein 다항식과 선형 weight를 rational antiderivative로 적분한다. 부호가 있는 weight는 불확실 영역에서 정확한 root로 나눈다.
5. 두 딸입자에 대해 같은 μ와 −μ의 집합을 결합한다. pair energy는 관측함수를 먼저 합쳐 2E0Y로 감싼다.

degree≤8에서 `σ=2Σb/(n+1)`, `M=max b`, `ε=σ2^-40`, `δ=ε/(16M)`이다. 경계당 최대48회의 이분법이면 충분하며, 실제 반환 interval 폭을 별도로 기록한다. 일반 preimage API는 `2^-80≤δ≤1`을 받는다. 영밀도는 입력 검사를 거쳐 적분값0을 반환하며 기하학적 역상이 빈 집합이라고 주장하지 않는다.

## 오차와 재현성

| 항목 | 처리 |
|---|---|
| 고정 다항식의 절단·구간 적분 오차 | 없음: 선언된 유한 다항식을 정확한 rational 연산으로 적분 |
| inverse root solver 오차 | 명시적인 bracket으로 포함, 질량 폭은 ≤16Mδ |
| roundoff | 인증 경로는 rational; 최종 그림의 float 변환은 표시 전용 |
| angular interpolation | 수행하지 않음. native DCS 점을 quadrature weight로 바꾸지 않음 |
| physical angular-law approximation | 선언된 supplied density 밖의 실제 분포 오차는 미결속 |
| 질량·에너지→γ,a 변환 및 parameter uncertainty | 이번 certificate에 포함되지 않음; 0으로 보고하지 않음 |
| 계산 비용 | 동결된 제어 예에 대한 실제 비용을 계측. 모든 가능한 입력 길이에 대한 시간 정리는 아님 |

수렴성은 8/16/24/40-bit CM bracket의 포함 관계와 폭 감소, 정확히 알려진 fold 질량 `sqrt(7)/5`의 제곱 판별로 확인한다. 과거 운동학 suite를 새 이름으로 다시 실행하지 않는다. 과학 결과의 채택은 source identity, 실제 출력·자원, 독립 검토와 각각 결속한다.
