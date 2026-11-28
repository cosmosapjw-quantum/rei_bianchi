# AZIMUTH09 R9 / C9 — 과학 채택

## 결정

**ACCEPT_SCOPED_FINITE_AZIMUTH_REFERENCE**.

Root는 고정 계약, 실제 첫 검증 22/22 PASS, 원 응답을 보존한 Wolfram 109/109
literal-zero residual, 저장값 plot의 CPU/wall PASS, 독립 review pass 1의 정적
12/12 및 실제 결과 14/14 PASS를 근거로 새 유한 방위각 참조 노드를 채택한다.
이론 증명과 실행 근거의 역할을 구분한다. 109개 잔차는 109개 독립 물리 실험이나
22개 Python test method를 대체하는 개수가 아니다.

새 local node `AZIMUTH09-FINITE-SECTOR-PAIR-REFERENCE`는 complete_scoped다.
Local DAG는 **9 complete + 1 partial + 3 physical open / 13**, 즉 **9/13**이다.
이번 새 단위의 workflow는 COMPLETE_SCOPED다. 과거 KINEMATIC08의 scoped science
참조를 재사용하면서도 그 plot 실패와 partial node는 승격하지 않는다. 중앙의
실제 `ed6a899fa87ad42fbbb3569e96779bc3af716620` base에서 count는 **28/88**이고
이번 HE delta는 **0**이다. 중앙 실제 게시 identity는 후속 ACK로만 확정한다.

## 채택한 수학적 결과

정지 bare alpha와 같은 질량의 두 딸, 선언한 정확 scalar rest energies A,M 및
photon energy e, s=A^2+2Ae, H=s-4M^2>0의 범위다. polar direction은 이미 채택한
surds map F로 계산한다. 같은 사건의 두 방향은 `(F(mu),t)`와
`(F(-mu),(t+1/2) mod1)`이다. 두 번째 polar cosine을 `-F(mu)`로 바꾸지 않는다.

측도는 명시적으로 `rho(mu) dmu dt`, t in[0,1), even nonnegative degree<=8
Bernstein density와 `azimuth_law=UNIFORM_DECLARED`다. 각 detector는 유리수
polar-window x azimuth-arc patch의 유한 합집합이다. detector당 patch<=8,
전체 활성 고유 polar window N<=8이다. 원 arc 및 halfturn arc의 모든 끝점에서
방위각을 정확 분할하고, 각 open strip에서 변하지 않는 mask만 midpoint로
선택한다. 이는 mu에 대한 수치 적분법이 아니다.

`Q1=Aplus intersect Bminus`, `Q2=Bplus intersect Aminus`로 두 assignment를 만들고
서로 다른 딸 coincidence `C=Q1 union Q2`를 계산한다. Hit-A와 Hit-B, inclusive
daughter counts, assignment sum 및 overlap, same-event both-hit는 각각 의미가
다르며 모두 반환한다. 같은 detector hit의 곱이나 서로 다른 assignment의 단순
합으로 C를 대체하지 않는다.

원 polar-window당 uncertainty length<=5delta를 반사한 집합까지 합친 U는
length<=10Ndelta다. 모든 event membership은 U x circle 밖에서 확정되므로
actual width<=B*actual uncertainty area<=10NBdelta다. B는 Bernstein
coefficient의 최대값이며 밀도의 실제 attained maximum이라고 주장하지 않는다.
기본 delta=sigma/(10NB*2^40)에서 Boolean event width<=sigma*2^-40다.
zero-density와 빈 detector는 별도로 정확 처리한다. Inclusive 및 assignment
count는 명시한 합산 폭, 2Y와 에너지는 각 scaling을 적용한다.

조건부 C|H는 denominator lower>0일 때만 interval division을 한다. Upper가0이면
undefined, lower=0<upper면 unresolved로 null을 반환한다. Positive lower의 경우
`[L_C/U_H,min(1,U_C/L_H)]`를 사용한다. 기본 event epsilon이 ratio의 일률적
epsilon 보장이 되는 것은 아니다. 수동 delta는 항상 실제 width/width_bound를 쓴다.

Label exchange `J(mu,t)=(-mu,t+1/2)`는 선언 측도와 C를 보존한다. 따라서 C 위의
first mu moment는0이고, selected daughter count=2Y, total pair energy=GY,
각 mathematical label energy=GY/2다. 이 에너지에는 rest energy가 포함된다.
이를 detector별 energy, thermal deposition, heat capacity 또는 비열적 pool의
배정으로 해석하지 않는다.

## 독립 oracle 및 검증의 정확한 범위

고정 반대 quarter-sector 예는 C=1/2다. 독립 sector 확률식은 1/8, hit marginal의
곱은1/4가 되어 실제 same-event coincidence와 구별된다. Relative orientation을
추가로 균일 평균하면1/8이 되지만 이는 별도 평균이다. 같은 full-circle detector
둘에서는 C=1, assignment count=2, overlap=1이다. 같은 half-circle 둘에서는
C=0이고 both-hit=1이다. Wrapped seam 예도 원의 유리수 합집합으로 정확 처리한다.

A=3,M=2,e=8/3인 mixed polar/quarter-sector oracle에서는 C=11/204,
Hit-A=91/204, Hit-B=11/204, 조건부 oracle11/91 및1, selected count11/102,
pair energy11/36 MeV, label energy11/72 MeV다. 반환 ratio endpoint는 테스트에서
oracle 포함을 확인했지만 plot용 JSON에는 따로 저장하지 않았다. 이미 끝난
검증을 다시 실행하여 이 기록 범위를 확대하지 않는다.

Degree8/N8 사례의 실제 boundary bisection은0, fold bisection392,
comparison48, strips32다. 이는 해당 입력 구성과 guard를 검증한 것으로,
비공허 경계의 worst-case stress라는 주장은 하지 않는다. 최대50회 root bisection
상한은 해석적 bracket/delta 증명과 두 exact integer comparison에 근거한다.
Native 세 사례에는 각각 실제 boundary bisection92회가 관측됐다.

수동 delta1/16 비교의 Hit-A interval은[17/48,19/48], width=bound1/24이며
default width는1/26388279066624다. 이 사례의 C는 둘 다 exact0다. APERTURE07의
수동 delta2^-40 예에도 그 당시 반환된 실제 폭을 계속 사용한다.

## 실행·검토·신원

| 항목 | 실제 source / 결과 |
|---|---|
| 검증 Local S05 | `0529ce44d5fca255befbd6b7e1007b40c768feed` |
| 검증 remote same-tree S05 | `920519403c80285174c8154e92c9ae8a1e82f2cb` |
| 검증 exact tree | `76c88b7feb60d9afe01064a066f41d698f72fd1d` |
| 검증 | 22/22 PASS; whole CPU0.782465/12 s, wall0.8201407000015024/40 s |
| Plot Local S07 | `2fbe4657b480149b393c54cac6009feb4fd05ac6` |
| Plot remote same-tree S07 | `4750c693cfb51433060db10ad81c8732382f3f17` |
| Plot exact tree | `40c6184a0a4cf5ac04c1a2428015659b3709c3f8` |
| Plot | whole CPU2.053974/8 s, wall2.124947346004774/20 s, science calls0 |
| Wolfram | evaluator1, 109 literal integer zeros, bisection comparisons2 True; remote CPU=null |
| 독립 review | pass1, static12/12, actual14/14, preexecution F01 closed1, blocking0 |

검증과 plot은 각각 첫 실행, execution repair0이다. 새 reserve1은 사용하지 않았고
남은 값이 자동 재실행이나 다른 노드의 예산을 허가하지 않는다. F01은 실행 전
periodic atan2 좌표의 동치 표현을 비교하는 assertion의 false-FAIL을 수정한 것이다.
기존 places12, 과학 알고리즘, 모델과 예산을 바꾸지 않았다. 과학 실행 후 실패를
숨기거나 tolerances를 완화한 사건이 아니다.

Whole-process와 outer orchestration 수치는 각각 영수증의 측정 범위로 해석한다.
Plot은 기존 font cache가 있는 환경의 관측이며 cold-start 비교는 하지 않는다.
새 과학·검증·plot·Wolfram 재실행과 추가 review pass는 필요하지 않다.

## 미해결 물리 입력과 에너지 소유권

1. 원 M0475002 정규화, liquid-He electron/target motion/response projection.
2. 완전한 실제 각분포와 photon encounter flux/history.
3. Named nonthermal birth/deposition/thermalization 및 global species binding.

이번 결과는 선언 기하와 선언 측도에 대한 참조다. 실제 parameter 변환 불확실성,
empirical DCS normalization, 실제 물리 사건률을 인증하지 않는다. 입자 수, Cv,
rest/binding energy와 비열적 에너지는 별개다. Binding은
`population_rest_energy_witness`가 한 번만 소유한다. Independent binding RHS,
Gamma_thermal, Cv, species_heating, thermal_deposition은 null이고 birth_pool은
UNASSIGNED다. Global physical completion=null, L4=false,
production=NOT_APPROVED를 보존한다.

이 문서는 S09 채택 시점의 source 기록이다. 최종 source/중앙 게시 및 백업 ACK는
S10 이후 POSTPUBLICATION_EXTERNAL_DELIVERY 문서가 권위 있다.
