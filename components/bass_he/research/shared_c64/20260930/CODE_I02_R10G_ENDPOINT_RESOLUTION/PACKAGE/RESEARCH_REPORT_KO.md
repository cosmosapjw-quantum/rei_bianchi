# BASS_HE R10G: 저-rho 해상도와 원점에서 유한한 회전 표현

## 1. 판단 요약

R10F_BOUNDARY_SPLIT_GK_UNRESOLVED를 보존한다. 경계 분할이 실패 성분을 49개에서 27개로 줄이고 straight 두 lane을 통과시켰지만, Coulomb 첫 구간 문제를 닫지는 못했다. 따라서 앞선 ‘경계 분할만 하면 해결될 것’이라는 전망은 과도했다.

이번에는 첫 구간만 대상으로 실제 반례를 재현했다. 원점에서 발산하는 물리적 확률을 발견한 것은 아니다. 같은 Coulomb 궤적을 원점에서 유한한 eccentric anomaly로 표현하면 회전 ODE는 매끄럽고, head-on |m| 확률은 identity로 수렴한다. 다만 rho가 Coulomb 길이 a 정도에서 빠르게 변하는 좁은 영역이 있고, u=rho^2의 큰 첫 panel은 이를 충분히 분해하지 못한다.

기존 검증 범위보다 작은 rho에서는 원래 x-표현의 고정 1024-step 정확도가 자동으로 상속되지 않는다는 별도 수치 사례도 확인했다. 새 표현과 첫 구간 전용 적분 코드를 준비했지만, 새 exact-Delta 90성분 실행은 이 응답에서 수행하지 않았다.

## 2. 이번에 실제 확보한 원문

GitHub PR17 basis: 5efe052460e85f7e9785b9391d188ba394efee73.
PR15: b8b2fe47a367459f6faf6796eb2f251feacbbd7c, 변경하지 않았다.

원 archive BASS_HE_R10F_BOUNDARY_SPLIT_GK_UNRESOLVED_20260930T1026KST_v1.zip:
- 3,105,199 bytes
- SHA256 082fd7ec94e2873ee218043828179e3c4db8d9f0d4ce28f9fa29f8c807207578
- 실제 Drive 다운로드의 SHA256, ZIP CRC, manifest payload 2014개를 확인했다.

여기서 exact table은 기존 depth96/panels32 numerical-reference 명칭이며 수학적으로 정확한 해 또는 interval certificate를 뜻하지 않는다.

새로운 연구를 위해 읽은 것이며 과거 backup receipt만 반복 인용한 것은 아니다. 원 archive는 변경하지 않는다. R10F의 exact table SHA256은 a5c2422820b56b0ae6b5cc3857b0d24508452bb274ad40e1818373facb1e8031이다.

R10F archive에는 구간별 high/error는 있지만 모든 node의 원시 integrand array는 없다. 따라서 ‘저장된 255 integrand를 그대로 읽었다’고 주장하지 않는다. 확인에 필요한 첫 frozen-lane 15개 점은 독립된 dependency facade와 변경하지 않은 원 adapter로 재생했다. 첫 구간 high/error의 최대 차이는 각각 1.4432899320127035e-15, 1.0763959168436088e-15였다.

## 3. 동일 Coulomb 궤적의 유한한 매개변수

물리적 Coulomb 길이를 a=kappa/(mu v^2), kappa=Z1 Z2 e^2/(4 pi epsilon_0)로 정의한다. 이후 계산식은 저장소의 원자단위 및 dimensionless angular-momentum convention을 그대로 사용한다. 새로운 SI 변환값을 넣거나 legacy 27.07/1.836153 상수를 바꾸지 않는다.

b=sqrt(a^2+rho^2), a>0에 대해

    R(eta) = a + b cosh(eta),
    phi(eta) = 2 atan[(rho/(a+b)) tanh(eta/2)],
    t(eta) = [a eta + b sinh(eta)]/v

로 놓으면

    dphi/deta = rho/R,
    dt/deta = R/v,
    R(phi) = rho^2/[b cos(phi)-a]

가 정확히 성립한다. 기존 Coulomb adapter와 같은 궤적이고, 기존 핵 궤적 또는 cutoff를 바꾼 것이 아니다.

회전 영역에 들어갈 조건은 a+b<Rcut이고,

    eta_max = acosh[(Rcut-a)/b]

에서 경계가 정해진다. 기존 collision-plane 부호 convention을 유지하면 Eq.(47)은

    i dA/deta = [(epsilon/v) R^3 Lx^2 - (rho/R) Lz] A

가 된다. 원래 rotating frame에서 직접 적분하므로 기존 x-gauge의 endpoint 변환을 이 식에 다시 곱하지 않는다. 이 점은 이중 frame 변환을 피하기 위한 필수 조건이다.

rho -> 0에서 R -> a(1+cosh eta), Lz 결합 -> 0이고, Rcut>2a이면 eta 구간은 유한하다. 이때 propagator는 Lx 고유기저에서 phase만 주므로 collapsed |m| transition matrix는 identity다. Rcut<=2a에서는 애초에 해당 회전 영역에 들어가지 않는다.

rho의 부호 반전은 Lx 주위 pi 회전으로 Lz의 부호를 바꾸는 대칭과 관련된다. 따라서 이 모델에서 확률은 국소적으로 rho에 대해 even이고 off-diagonal 회전 확률은 O(rho^2)다. 전체 충돌확률이 반드시 0이라는 뜻은 아니다. Hidden crossing은 별도다.

이 유도는 고정 a>0의 국소 regularity를 설명한다. a->0과 rho->0의 극한을 임의로 교환하거나 전 rho 영역의 수렴률을 보증하지 않는다.

## 4. actual numerical diagnostics

검사 환경: Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0. 이전 실행 호스트의 Python 3.12.3 환경과 다르므로 새 supporting research evidence로 기록한다.

### 4.1 원래 표현의 새로운 작은-rho 영역

2개 energy, 2개 block (N,l)=(2,1),(3,2), 8개 rho/a 값 0.01,0.05,0.1,0.25,0.5,1,2,4의 32점을 조사했다. Author cutoff를 썼다. 원 adapter의 Git blob 543ff5e5c20ff2969547f03410cd30353998348c는 그대로 유지했다.

원 x-Magnus1024와 새 anomaly full-matrix DOP853 사이 최대 확률 차이는 1.2967683316045253e-7였다. 위치는 5 keV/u, (3,2), rho=0.0033837499999999996, rho/a=0.5다. 이 점은 R10E에서 수렴을 검사한 105-node 범위보다 더 안쪽이다.

이는 원래 R10E gate가 잘못됐다는 뜻이 아니다. 그 gate가 검사하지 않은 더 작은 rho에 자동 적용되지 않는다는 뜻이다. 경계 분할을 추가하며 이 점들을 새로 요청한다면 회전 query 정확도도 함께 점검해야 한다.

### 4.2 anomaly Magnus prototype

동일 32점에서 anomaly-parity Magnus4 64/128/256을 검사했다.
- max128->256: 6.2129560385315585e-9
- max256 vs full-matrix DOP853: 4.1454906174465123e-10
- max unitarity defect: 1.192379528447418e-13

이후 배포용 구현을 테스트와 함께 별도로 작성했다. 원 R10F 첫 panel의 15개 기존 점, 12개 block/energy/cutoff 조합에서 원 x-Magnus1024와 새 eta-Magnus256의 최대 확률 차이는 2.295188983314489e-9였다. 새 표현은 원본과 다른 물리모델을 만드는 것이 아니라 같은 ODE를 더 안정적인 독립변수로 적분하는 후보라는 수치 근거다.

서로 다른 integrator가 같은 방정식에 동의하는 것은 독립적인 물리 증명이나 blind review가 아니다.

## 5. 적분 변수와 bounded pilot

a_ref는 두 energy 중 가장 작은 Coulomb 길이, 즉 E=5 keV/u의 a로 선택한다. 데이터 fitting으로 고른 상수가 아니다.

    rho = a_ref sinh(q),
    2 pi rho d rho = pi a_ref^2 sinh(2q) d q.

q=0이 rho=0이다. 첫 구간 밖의 16개 high/error vector는 R10F의 동일 원문 값을 재사용한다. 본 연구 pilot에서는 fresh Delta를 구하지 않고 정확히 COUL_AUTHOR_FROZEN lane의 저장 Delta(0)만 사용했다. 이 lane에서도 첫 구간 실패가 재현되므로, variable Delta(rho) interpolation error 없이도 남는 적분 난점을 분리할 수 있다.

다음 표는 두 energy 총 18성분에 대한 최악의 global normalized embedded diagnostic이다. 전체 five-lane 결과가 아니다.

| 첫 구간 변수 | equal subpanels | max normalized embedded | fail components |
|---|---:|---:|---:|
| u=rho^2 | 1 | 21.39289515 | 9 |
| u=rho^2 | 2 | 7.70462983 | 8 |
| u=rho^2 | 4 | 2.77765982 | 5 |
| u=rho^2 | 8 | 1.82468726 | 2 |
| q=asinh(rho/a_ref) | 1 | 6.86176893 | 6 |
| q=asinh(rho/a_ref) | 2 | 0.08472925 | 0 |
| q=asinh(rho/a_ref) | 4 | 0.00061648 | 0 |
| q=asinh(rho/a_ref) | 8 | 6.99765e-7 | 0 |

q=2->4 panels의 high-estimate 변화는 허용치로 정규화하면 최대 3.86162e-7이었다. 따라서 high/low 우연한 동의만 보는 것보다 독립 grid 변화도 함께 확인했다. 최종 제공하는 worst-first bounded 코드의 pilot은 2개 panel의 첫 PASS 후 한 panel을 더 분할해 3개 leaf/60개 rotation query에서 재확인했다. 연속 두 estimator PASS와 high-change <=0.25*tolerance를 만족했다.

이 pilot은 설계 전에 결과를 보았으므로 outcome-informed다. Dynamic Delta의 90성분 수치 실행이 성공할 것이라고 단정하지 않는다.

## 6. 다음 실행: 새 R10G 계약

기존 모든 R10F cutpoint와 원본 결과를 변경하지 않고, 첫 interval의 적분 표현만 교체한다.
- 첫 구간 [0,B], B hex=0x1.05bbc59d8ffb1p-1.
- q scale hex=0x1.bb83cf2cf95d4p-8, 원래 legacy physical parameters로 생성.
- 2개 q-panel로 시작, 가장 큰 component-normalized error panel만 이분.
- 최대 8 leaf, 최대 210회 rho 평가, 최대 1050회 신규 Delta call.
- 다른 16구간의 exact high/error는 그대로 재사용.
- 각 새 q batch의 eta128/256 확률 gate와 worst-point full-matrix DOP853 audit를 geometry 계산 전에 검사.
- 허용치 unchanged: probability1e-7, DOP1e-8, unitary/stochasticity5e-13.
- exact geometry는 원래 bass_he.geometry.contour_geometry, depth96/panels32. 다른 sturm 경로로 바꾸지 않는다.
- 적분 gate는 기존 component-wise atol1e-10+rtol2e-4*abs(total).
- 연속 두 complete-grid estimator PASS 및 high-estimate 변화 <=0.25*tolerance가 필요.
- budget, source/environment mismatch 또는 새 회전/geometry 실패가 있으면 명시적으로 중단. 같은 실행에서 budget/tolerance를 늘리지 않는다.

R10F의 ‘refinement=0’ 계약을 몰래 바꾼 것이 아니다. 이 문서는 실패를 보존한 뒤 새로 정의한 R10G local-adaptivity 계약이다. 새로운 query authority가 필요하므로 global closure를 자동 상속하지 않는다.

## 7. 실행한 구현 검증

- 새 core helper의 behavioral RED: 12 failed, collection error 없음.
- 최소 구현 후 GREEN: 12 passed.
- source/lane/archive boundary 검사를 추가한 focused final: 16 passed.
- archive-only CLI dry run: exit0, PREPARED_NOT_EXECUTED.
- compileall: exit0.
- 원 source/frozen first interval 재현: high/error 약1e-15 일치.
- real dynamic Delta execution: NOT_RUN.

Runner는 원래 R10F source digest와 Python3.12.3/NumPy2.3.5를 요구한다. 다른 환경에서 이를 우회하거나 과거 캐시를 자동 import하지 않는다. 동시 실행은 출력 directory lock으로 거부한다. 결과/cache는 atomic write+fsync를 사용하며, 매 Delta 결과를 기록한다.

## 8. claim gate

CODE_I02_CLOSED=true; full_certificate_fail_closed=true.
scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN.
R10F_BOUNDARY_SPLIT_GK_UNRESOLVED는 history로 유지.
R10G는 RESEARCH_CODE_PREPARED_AND_BOUNDED_DIAGNOSTIC_CHECKED.
새 five-lane Delta/transport 적분, 효과 분해와 Appendix-A 결론은 NOT_RUN이다.

## 9. source references

현재 GitHub source/보고서의 고정 commit은 5efe052460e85f7e9785b9391d188ba394efee73이다. Source URLs와 외부 문헌은 LITERATURE_AND_WOLFRAM.md에 둔다. 원문 PDF와 author FORTRAN은 이 패키지에 없다.
