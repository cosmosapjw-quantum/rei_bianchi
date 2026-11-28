# AZIMUTH09 독립 사전 계약 검토 — pass 1

검토자: `/root/he09_science_review`, 부모와 별도 Astra 계열 검토 agent. 방법은 원자료 읽기와 독립 수학 유도다. 이 문서는 실행 결과가 아니다. Science/test/plot/Wolfram 실행은 각각 0회다. 새 코드와 실제 결과는 같은 pass 1의 후속 검토 대상으로 남긴다.

## 판정

**PASS_SCOPED_PRECONTRACT_MATH**. 선언한 축대칭 연속 사건 측도 아래에서 KINEMATIC08의 정확 극각 역상에 유리수 회전각 구간 대수를 결합하는 구성이 성립한다. 실험 각분포나 정규화의 채택은 별개다. 새 불가능성 정리나 문헌 신규성 주장은 없다.

검토한 기존 원자료:

- `BASS_HE/AGENTS.md`
- `BASS_HE/research/program_expansion_20261025/continuation_kinematic_20261028/THEORY_KO.md`
- 같은 단위의 `src/kinematic.py`, `CODING_CONTRACT.md`
- `continuation_aperture_20261027/src/aperture.py`
- `externaldelivery_kinematic08/BASS_HE_KINEMATIC08_HANDOFF_KO_20261028.md`, `CENTRAL_PUBLICATION_RECEIPT.json`

이전 실제 검증 Local S05R `d004212d560907eb4058d9539eec8e9b262ec406`와 게시 same-tree `391f1e4c356082c0b5cc693d49fb2aef873a0f2a`를 계승한다. 기존 14/14 PASS와 plot CPU 7.040661/6 FAIL, workflow PARTIAL, local 8/12 및 central 28/88은 바꾸지 않는다.

## 1. 두 입자의 방위각과 사건 측도

`A=m_alpha c²`, `M=m_d c²`, `e=E_gamma`, `q=c p`, signature `(-,+,+,+)`와 KINEMATIC08의 `s=A²+2Ae`, `H=s−4M²>0`, `G=A+e`, `R=H/s`를 유지한다. `t=phi/(2pi)`는 원주 `T=R/Z`의 좌표다. CM에서

`q_perp,+ = sqrt(H)/2 sqrt(1−mu²) (cos(2pi t), sin(2pi t))`,
`q_perp,− = −q_perp,+`.

z 방향 Lorentz boost는 이 두 transverse 성분을 보존한다. 따라서 lab 방향은 `(F(mu),t)`와 `(F(−mu),t+1/2 mod1)`다. Lab의 두 극각 코사인을 `F(mu),−F(mu)`로 바꾸면 boost 효과를 잃는다. `mu=±1`에서 transverse 방향이 정의되지 않는 점과 stopped endpoint는 현재 연속 측도에서 영측도다.

선언 측도는 `dm=rho(mu)dmu dt`, `sigma=integral rho(mu)dmu`다. 따라서 `dt=dphi/(2pi)`. `rho`는 이 labelled parametrization에서 총질량 sigma를 갖도록 **선언된 사건 측도**다. 외부 `d sigma/dOmega`와의 대응이나 동일입자 convention의 1/2를 여기서 자동 결정하지 않는다. 원 DCS의 정규화는 기존 열린 입력이다.

`rho(mu)=rho(−mu)`이면 label 교환 `J(mu,t)=(−mu,t+1/2)`가 측도를 보존한다. 균일 t는 API에서 `azimuth_law='UNIFORM_DECLARED'`로 명시한다. 이 상태가 실제 편광·빔·검출기 자료에 대해 확인됐다는 주장은 하지 않는다.

## 2. 두 검출기의 사건식

검출기 D를 유한 union `D=union_i W_i x S_i`로 정의하고, `D+`를 +딸입자 방향의 역상, `D−=J(D+)`를 −딸입자 역상으로 둔다. `S_i`는 rational turn arc의 정확 구간 union이다.

서로 다른 두 딸입자가 A/B를 채우는 coincidence는

`C=(A+ intersect B−) union (B+ intersect A−)`.

두 assignment를 더한 양은 `K=1_(A+ intersect B−)+1_(B+ intersect A−)`로 0,1,2의 값을 가질 수 있다. Detector overlap을 허용할 때 `integral K`와 `measure(C)`를 구분해야 한다. Assignment overlap O를 두 항의 교집합으로 두면 `integral K=measure(C)+measure(O)`다.

Hit는 `H_A=A+ union A−`, inclusive daughter count는 `I_A=1_A+ +1_A−`다. `H_A intersect H_B`는 한 딸입자가 중첩 검출기를 모두 만족한 사건도 포함한다. 따라서 이것을 distinct-daughter coincidence C로 대체할 수 없다. `C subset H_A intersect H_B`는 성립한다.

J는 C를 보존한다. 짝 rho 아래 `integral_C mu dm=0`이므로 `Y=measure(C)`에 대해 selected daughters `2Y`, pair total energy `G Y`, label별 coincidence energy `G Y/2`가 성립한다. 이것은 임의 검출기별 energy slope를 근사하는 주장이 아니며, rest energy를 포함하는 총에너지를 heating에 넣지 않는다.

## 3. 원주 구간과 strip 적분

`Arc(start,width)`는 `0<=start<1`, `0<=width<=1`로 정의한다. width0은 empty, width1은 full circle이다. 끝점이1을 지나면 두 조각으로 나눈다. 0과1 seam의 단일 점은 영측도이므로 동일한 convention으로 정규화하면 된다.

각 detector의 원래 sector endpoint와 half-turn 이동 endpoint를 모두 모아 `[0,1)`를 정확히 분할한다. 각 열린 strip 안에서는 sector membership가 상수이므로 **t midpoint**로 활성 patch를 찾는 것은 정확하다. μ midpoint로 물리 역상을 대체하는 것은 이 논증에 포함되지 않는다. 활성 polar preimage bounds를 union/intersection하여 strip별 `SetBounds`를 얻고, 각 strip 길이를 정확 Bernstein 적분에 곱하여 더한다. 중복·접촉·중첩 patch는 union으로 정규화하며 그대로 더하지 않는다.

## 4. 포함과 오차의 독립 증명

전체 detector에서 서로 다른 비퇴화 polar window를 `W_1,...,W_N`으로 세고, KINEMATIC08의 `I_i subset P_i subset O_i` 및 `U_i=O_i\I_i`, `length(U_i)<=5 delta`를 재사용한다. 원래 window의 방위각 위치나 여러 patch에서의 재사용 횟수는 N을 늘리지 않는다.

`U=union_i (U_i union reflection(U_i))` 밖에서는 모든 +/− polar membership가 정확히 결정된다. t의 경계들을 제외하면 sector membership도 정확하다. 따라서 정확한 포함 연산으로 만든 Boolean 사건 E의 내·외부 차이는 `U x T` 안에 놓인다. 단조 union/intersection에는 inner끼리/outer끼리를 적용하고, 차집합을 추가한다면 `I_A\O_B`, `O_A\I_B`를 사용해야 한다.

`area(O_E\I_E)<=length(U)<=10N delta`.

`B=max Bernstein coefficients`, `0<=rho<=B`이므로

`0<=U_E−L_E<=B area(O_E\I_E)<=10NB delta`.

`B>0,N>0`이면 `delta=sigma/(10NB 2^40)`로 사건 폭 `<=sigma 2^-40`를 보장한다. 실제 area 기반 width_bound도 반환해야 한다. `N=0` 또는 `B=0`은 정확 영결과로 처리한다. 수동 delta에는 실제 반환 width/width_bound를 적용한다.

degree n<=8에서 `B/sigma <=(n+1)/2<=9/2`. N<=8이면 `delta>=1/(360*2^40)`이고, 초기 길이2인 bracket은 최대 `ceil(log2(720*2^40))=50`번 이분으로 충분하다. **이전의 48회 상계를 그대로 쓰면 안 된다.** 이는 유리수 bit-length에 대한 wall-time 보장이 아니다.

위 10NB delta는 Boolean 사건의 상계다. `2Y`, `G Y`, `G Y/2`에는 해당 계수만큼 폭과 bound를 함께 scale한다. Assignment count와 여러 detector의 count 합은 Boolean 사건으로 취급하지 말고 각 반환 구성에 맞춘 가중 bound를 사용한다.

## 5. 조건부 비율

`C subset H_A`와 `L_H>0`이 인증되면

`L_C/U_H <= P(C|H_A) <= min(1,U_C/L_H)`.

`U_H=0`은 영분모이며 조건부 확률은 정의되지 않는다. `L_H=0<U_H`에서는 현재 enclosure만으로 양의 분모가 인증되지 않았다. 두 경우에 서로 다른 상태와 null bounds를 반환하는 계약이 적절하다. 기본 사건 폭이 작은 것만으로 조건부 비율에 같은 epsilon을 보장할 수 없다.

## 6. 독립 정확 기준값과 판별력

아래는 코드 실행이 아닌 해석적 기준값이다. 별도 표시가 없으면 full polar acceptance와 constant `rho=1/2`, `sigma=1`이다.

| 입력 | 정확 결과 | 구별하는 오류 |
|---|---|---|
| A turn `[0,1/4)`, B `[1/2,3/4)` | Y=1/2, hitA=hitB=1/2, inclusiveA=inclusiveB=1/2 | 두 label 방위각 독립화: `2f_A f_B=1/8`, hit marginal 곱=1/4 |
| A=B=full sphere | Y=1, assignments=2, overlap=1, daughters=2, hitA=1, inclusiveA=2 | OR를 단순 합으로 대체 |
| A=B same half-turn `[0,1/2)` | Y=0, both-detectors-hit=1 | 같은 딸입자의 중첩 hit를 두 딸입자 coincidence로 오인 |
| A arc(7/8,1/4), B `[3/8,5/8)` | Y=1/2 | periodic seam과 half-turn wrap |
| A sectors `[0,1/3)` union `[1/6,1/2)`, B `[1/2,1)` | Y=1, inclusiveA=1 | 겹친 patch의 중복 적분 |
| 위 모든 검출기를 공통 rational turn만큼 회전 | 모든 measure 불변 | uniform t의 정확 회전 대칭 |

물리 map을 사용하는 비자명한 기준값: `A=3,M=2,e=8/3`이면 `r=3/5`, `G=17/3`, `k=e/(Gr)=40/51`. A는 forward polar `[0,1]`와 turn `[0,1/4)`, B는 backward polar `[-1,0]`와 turn `[1/2,3/4)`다. μ의 두 coincidence 조각은 `[k,1]`, `[-1,−k]`이며 각 azimuth 길이는1/4다. 따라서

- `Y=11/204`
- `hitA=91/204`, `hitB=11/204`
- `P(C|hitA)=11/91`, `P(C|hitB)=1`
- selected daughter measure `2Y=11/102`
- pair energy `G Y=11/36 MeV`, label별 energy `11/72 MeV`

구현의 유리수 bracket이 정확 endpoint를 직접 반환하지 않아도 이 값을 내·외부 bound가 포함해야 한다. 이 예는 `F(−mu)`를 `−F(mu)`로 잘못 바꾸는 오류도 구별한다.

## 7. 후속 코드·실제 결과 검토 범위

Root가 고정한 입력 제한은 detector별 최대8patch/전체16patch, 서로 다른 nonempty polar window N<=8, 명시적 `UNIFORM_DECLARED`, 짝 Bernstein rho다. 테스트는 기존 suite를 재실행하지 않고 새 azimuth/domain/set/event/ratio 연결만 판별해야 한다. Root의 새 단위 예산은 validation CPU12s/wall40s/512MiB, initial scientific suite1회+진단된 repair reserve1, saved-only plot CPU8s/wall20s/512MiB/1회다. 이 예산을 이전 KINEMATIC08 7.040661/6 FAIL의 재판정에 적용하지 않는다.

정적 후속 검토에서 arc 입력검사, exact half-turn, endpoint sweep, 중복 patch 정규화, inherited preimage 호출 identity, event/count 해석, N 계산, actual area width_bound와 ratio의 영분모 처리를 확인한다. 실제 결과 후속에서는 source pin, 실행 횟수, 원로그, budget 판정, 저장 plot input과 실제 그림의 의미를 확인한다. 이 단계에서는 해당 구현·실행 판정을 아직 내리지 않는다.
