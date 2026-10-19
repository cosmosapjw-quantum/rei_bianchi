# BR04: BR03 time–age 자료의 독립 재해석

## 실제 재사용한 근거

기존 7개 AP 이력의 raw CSV SHA-256을 BR03 독립 native 감사 기록과 비교해 일치시켰고, 현재 SCIENCE_RESULTS.json의 최종 값과 독립 계산값도 확인했다. 이 분석은 BR03 물리 source나 자료를 변경하지 않았다. 실제 시간 격자와 출생 refinement는 `(16,2), (32,1), (32,2), (32,4), (32,8), (64,2), (128,2)`이다. 이 집합에는 완전한 2×2 time–birth rectangle이 없다.

모든 이력은 동일한 최종 물리시각 T=8e12 s의 SIGNED_MINUS, donor grid 121, 원 spectrum, opacity panel 4, CX rtol=1e-12 및 atol=1e-14 사례다. 원 자료의 mean age와 second age moment는 각각 Σ(N age)/ΣN 및 Σ(N age²)/ΣN으로 다시 계산했다. q2는 원 photon projection의 에너지 가중 P2이다. 비율 관측량의 분자도 별도로 비교하기 위해 raw age moments와 E_gamma*q2를 함께 출력한다.

## 두 독립 축에서 관측된 차이

아래 시간 차수는 N16/32/64 및 N32/64/128의 연속 차분 비에서 계산한 형식적 값이다. 마지막 열은 N32에서 birth r2→r4의 `(fine−coarse)/coarse`다. 부호를 가진 에너지 항의 분모 부호도 유지했다.

| 관측량 | fixed r2 시간 차수 두 값 | fixed N32 birth r2→r4 상대 변화 |
|---|---|---:|
| photons_com3 | 1.005641, 1.064312 | -1.80032133e-08 |
| mean_age_s | -1.376809, -0.795455 | -6.89483170e-04 |
| second_age_s2 | -1.307759, 0.581734 | -8.58402033e-04 |
| q2 | -1.512572, -0.081702 | -7.59259271e-04 |
| DI | 0.656513, 2.010822 | 2.43877361e-12 |
| T_K | 1.818754, 1.894792 | 1.05909280e-13 |
| gas_thermal_com3 | 1.820792, 1.895961 | 1.06121878e-13 |
| thermal_change_com3 | 1.815599, 1.893575 | -1.56484784e-11 |
| geom_work | 1.480866, 1.656885 | -5.85293398e-11 |

평균 연령과 q2의 fixed-r2 시간 차분은 이 네 격자에서 증가하는 구간이 있다. 같은 N32에서 birth r2→r4의 평균 연령 변화는 광자수 변화보다 상대 크기가 훨씬 크다. 따라서 광자수의 빠른 birth 안정화와 age/angular 관측량의 안정화는 각각 평가해야 한다. N32의 r4→r8에서도 평균 연령은 약 6.65e-5, q2는 약 7.46e-5의 상대 변화가 남는다.

## 두 추가 사례가 식별하는 양

h=T/N, epsilon=1/r로 정의한다. 동일 입력을 유지한 네 corner에서 다음 항등식을 계산한다.

D_tr = [F(2N,2r)−F(N,2r)]−[F(2N,r)−F(N,r)]
     = [F(2N,2r)−F(2N,r)]−[F(N,2r)−F(N,r)].

추가 N16r4는 N16→32, r2→4 rectangle을 완성하고, 추가 N64r4는 N32→64, r2→4 rectangle을 완성한다. 두 사례를 얻으면 fixed r4 시간열이 N16/32/64가 되고, 평균 연령과 q2의 시간 차분이 줄어드는지 직접 비교할 수 있다. 분석기는 마지막 시각뿐 아니라 원 자료에 공통으로 존재하는 모든 시간 endpoint에서 D_tr와 각 축 차분을 계산한다. 보간값을 corner로 만들지 않는다.

조건부 오차 전개

F(h,epsilon) = F_star + A h^p + B epsilon^q + C h^p epsilon^q + R

를 가정하면 순수 시간 항과 순수 birth 항은 mixed 차분에서 소거되고,

D_tr = C h^p epsilon^q (2^(-p)−1)(2^(-q)−1) + Delta_t Delta_r R

를 얻는다. 고정 r pair에서 두 연속 rectangle의 D가 같은 부호를 가지면 log2(|D_16,32/D_32,64|)를 혼합 항의 조건부 h 차수로 보고한다. 이는 전체 시간 차수를 자동 결정하지 않는다. D가 0인 additive 식에도 A와 B는 남기 때문에, D의 작은 크기만으로 각 축의 절대 오차를 정하지 않는다.

이 분리에는 비교 격자에서 지배 차수와 계수가 안정적이고, remainder 및 내부 native solver 오차가 차분보다 작다는 조건이 필요하다. epsilon=1/r은 명목 해상도이다. h가 바뀌면 tau=kappa*h와 geometric birth panel의 분할도 달라진다. mean age, second age 및 q2는 비율이므로 분자·분모의 결합만으로도 mixed 차분이 나타날 수 있다. raw moments와 가중 분자의 비교가 이 해석을 보완한다.

## 비용과 다음 식별 단계

실제 BR03 wall time은 N16r2 9.40 s, N32r2 30.74 s, N64r2 90.46 s, N32r4 54.73 s이다. N32 r2→r4의 실측 배율을 옮기면 추가 두 사례는 각각 약 16.7 s와 161.1 s, 합계 약 178 s로 추정된다. 이전 실행의 인접 refinement 배율 범위를 사용하면 약 17–20 s와 161–188 s이다. 이는 이전 worker contention이 포함된 관측적 범위이며 확률적 신뢰구간이 아니다. 신규 native 실행은 부모 연구자가 담당한다.

추가 r8 사례를 N16 또는 N64 중 하나에 두면 두 r pair의 mixed 차분을 비교할 수 있다. N128r4는 더 미세한 시간열에서 같은 검사를 잇는다. 전체 연령–에너지–방향 결합분포에 관한 추가 관측은 현재 CSV의 marginal moment와 q2 외의 입력을 요구한다.

## 구현 검산과 결과 상태

Decimal 60자리로 serialized native 값을 읽어 새 산술 상쇄를 줄이고, derived moment의 네 corner 뺄셈에는 추가 working precision을 쓴다. 이것이 native solver의 roundoff나 discretization 오차를 없애지는 않는다. 7개 독립 algebra test는 additive 소거, 알려진 mixed monomial, 미세한 차분의 보존, 부호 변화/0 차분 분류, 완전한 rectangle 개수, age 정규화, ratio-induced mixed defect를 실제 검증했다.

현재 이 문서는 새 native 사례 전의 재사용 결과다. 두 신규 이력의 완료·실패 및 실제 crossed 결과는 별도 실행 산출물에 기록한다. LONGSPAN_SOLUTION은 원래의 수렴 의무가 완료될 때까지 NOT_ADMITTED 상태를 유지한다.
