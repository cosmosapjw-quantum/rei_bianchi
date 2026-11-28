# HARMONIC10 — 새 이론·코딩 단위의 계약

작성 권위: Astra parent, 2026-10-28 KST. 사용자가 AZIMUTH09 종료 뒤 다음 전체
이론 R1–R10과 코딩 C1–C10을 새로 요청했다. 이 계약은 새 단위 하나에 적용하며,
이전 예산을 초기화하거나 남은 reserve를 이전하지 않는다.

## 1. 목표와 기준

고정 선언된 rest-energy A=m_alpha c^2, M=m_d c^2 및 incident energy e=E_gamma,
metric(-,+,+,+), H=A^2+2Ae-4M^2>0에 대해 AZIMUTH09의 같은 사건 두 딸
방향 (F(mu),t), (F(-mu),t+1/2 mod1)과 유한 detector patch 기하를 재사용한다.
t=phi/(2 pi), -1<=mu<=1. 기존 UNIFORM_DECLARED를 명시적
SECOND_HARMONIC_DECLARED 비음수 측도로 확장한다. c,hbar,k_B의 자연단위 설정은
없다. A,M,e는 MeV로 표시된 에너지이며 rest-energy 변수 사용으로 식이 간결하다.

dm = [rho0(mu)+rhoc(mu) cos(4 pi t)+rhos(mu) sin(4 pi t)] dmu dt.

rho_j(mu)=sum_{i=0}^n b_{j,i} B_i^n((mu+1)/2), n<=8. 세 계수 배열의 길이는
같고, 모두 reflection-even b_{j,i}=b_{j,n-i}. 각 i에서 b0_i>=0 및
b0_i^2>=bc_i^2+bs_i^2를 정확한 유리수 비교로 요구한다. bc,bs는 음수를 허용한다.
이는 비음수성의 충분조건이다. cone 밖 전체 양성 다항식까지 판정하는 API는 아니다.
예: b0=(1,0,1),bc=(0,1/2,0),bs=0은 rho0-|rhoc|=(1+3mu^2)/4>0이나
이 계수 cone에는 속하지 않는다. 이 예를 invalid certificate 입력으로 보존한다.

sigma = 2 sum(b0)/(n+1). B0=max b0. 비영 harmonic이 있으면 B=2B0,
uniform이면 B=B0를 density 상한으로 사용한다. 계수별 b0+bc cos+bs sin>=0에서
전체 rho>=0, rho<=2B0가 나온다. sigma=0이면 모든 계수0이고 모든 사건 measure0.
서로 다른 물리적 정규화나 photon flux는 이 계약의 입력에서 주어지지 않았다.

기준 remote P10=307fee38cb65b957deea84c3308f59e972049362,
tree=5bce5ccb7d95721069ae17f791ea37fa6fbd27d5. 원 local D10은
bc08e7d59b67284c45addfe3da89a707f3c18261이며 실행 신원을 원격 신원으로 바꾸지 않는다.
새 branch=research/he-harmonic10-20261028,
새 unit=research/program_expansion_20261025/continuation_harmonic_20261028.
새 local DAG 분모14: 초기9 complete+1 inherited partial+3 physical open+1 pending;
채택 시10 complete+1 inherited partial+3 physical open. 중앙28/88, HE delta0 유지.

## 2. 같은 사건 기하와 적분

AZIMUTH09의 DetectorPatch, FiniteDetector, PhysicalAngularMap, SetBounds를 그대로
import한다. detector당 patch<=8, total<=16, 활성 고유 polar window N<=8.
wrapped/full/empty arc 및 patch overlap은 기존 합집합 의미를 유지한다.
original/halfturn arc endpoint와0,1의 정확 분할에서 선형 strip 수 P<=65다.
strip midpoint는 azimuth membership만 결정한다. mu 적분의 quadrature sample이 아니다.

기존 azimuth_pair_response를 rho0의 BernsteinDensity 및 고정한 delta로 호출해
그 반환 strips/sets/preimages를 재사용할 수 있다. 이 호출은 새 harmonic contract의
기하 의존성을 사용한다. 과거 suite를 재실행하거나 과거 결과를 다시 채택하지 않는다.
그 함수의 uniform 숫자를 새 harmonic 결과로 사용하지 않는다.

각 strip [l,h]에서 사건의 mu inner/outer 집합 E-/E+에 대해 세 다항식의
유리수 primitive를 정확히 계산한다. 부호가 있는 계수도 허용한다.

I(E;l,h) = A0(E)(h-l)+Ac(E) C(l,h)+As(E) S(l,h),
A_j(E)=integral_E rho_j(mu)dmu,
C=(sin(4pi h)-sin(4pi l))/(4pi),
S=(cos(4pi l)-cos(4pi h))/(4pi).

비음수 측도이므로 I(E-)<=I(true)<=I(E+). C,S를 인증 interval로 계산하여
lower=sum lower(I(E-)), upper=sum upper(I(E+))를 반환한다. 사건값은
확립된 [0,sigma]와 intersect해도 된다. inner integral의 부호 있는 harmonic 항을
개별 양의 밀도로 오해하거나 component별로 잘못 clip하지 않는다.
중복 set integral은 같은 호출 안에서 cache할 수 있다.

기존 EVENTS와 PARTS를 유지한다. coincidence는
(A_plus AND B_minus) OR (B_plus AND A_minus). inclusive counts, both-detectors-hit,
assignment sum, assignment overlap은 서로 다른 observable이다. 더하는 출력은
interval과 width_bound를 합한다. 조건부 ratio는 denominator.lower>0일 때만
[num.lower/den.upper,min(1,num.upper/den.lower)]를 반환한다. upper0이면 undefined,
lower0<upper면 unresolved/null. 조건부 ratio에는 일괄 epsilon 보장이 없다.

## 3. 유리수 삼각함수 인증

production certificate는 float sin/cos나 black-box interval 라이브러리를 사용하지 않는다.
pi =16 atan(1/5)-4 atan(1/239). atan(x)의 N-term alternating partial sum과 다음
항까지의 합 사이를 enclosure로 삼는다. N5=24,N239=8로 고정하고 pi interval을
2^-96 dyadic grid에 바깥쪽으로 반올림한다. 원 identity는 tan(4atan(1/5)-atan(1/239))=1과
각도 범위로 유도한다. 이는 새로운 물리 정리나 novelty 주장이 아니다.

u=(2t) mod1, q=floor(4u), r=u-q/4 in[0,1/4). x=2pi r의 interval을 만든다.
그 midpoint를2^-96 grid에 내려 반올림한 w를 Taylor 평가점으로 쓴다.
argument_error=max(abs(w-x.lower),abs(x.upper-w)). 0<=w<2.
sin: sum_{k=0}^{19}(-1)^k w^(2k+1)/(2k+1)!, remainder<=2^41/41!.
cos: sum_{k=0}^{19}(-1)^k w^(2k)/(2k)!, remainder<=2^40/40!.
각 remainder에 argument_error를 더한다 (|sin'|,|cos'|<=1).
interval을2^-88 grid 바깥 반올림하고 [-1,1]과 intersect한다.
q=0,1,2,3에 따라 sin/cos를 정확히 교환·부호 변환한다. r=0은 cardinal0,±1을
정확히 반환한다. 재사용 cache는 phase의 정확 유리수 값으로 key한다.

구간 사칙연산으로 C,S를 계산한다. 특히 full/half circle의 endpoint 차0은 exact0.
pi.width<2^-94, phase argument error<2^-94, sine/cosine width<2^-86,
pi>3 및 numerator magnitude<=2에서 C.width,S.width<2^-84라는 보수적 상한을
유도한다. 실제 반환 width도 각각<=2^-84인지 확인한다. tolerance를 통과시키려고
넓히지 않는다. 모든 계산은 고정 유한 series이며 재실행·adaptive trial이 없다.

## 4. 오차 예산과 대칭

각 polar preimage uncertainty<=5delta를 재사용한다. reflected union까지 포함한
모든 Boolean event의 uncertain area a_E<=10Ndelta. rho<=B이므로 polar gap<=B a_E.
실제 산술 오차 상한 a_num은 각 strip의 inner integral interval width와 outer interval
width의 합이다. 실제 width<=B a_E+a_num. |Ac(E)|,|As(E)|<=sigma로부터
a_num<=4 sigma P 2^-84. returned width_bound에는 실제 a_num을 사용한다.
global bound는10NBdelta+4sigma P2^-84 (uniform의 arithmetic term은0).

기본 delta=sigma/(20NB2^40); N0 또는 density0은 exact shortcut(delta1).
이때 Boolean width<=sigma(2^-41+260*2^-84)<sigma2^-40.
단, 수동delta에는 실제 반환 width/width_bound만 적용한다. count/energy scaling에는
그 factor를 곱한다. 선택된 기본delta>=1/(1440*2^40)이므로 길이2에서 시작하는
root bisection 횟수는 최대52; fold는 길이1. 실제 관측 iteration 수는 별도 기록한다.
입력 유리수 bit length 전체에 대한 wall-time universal 보장은 하지 않는다.

J(mu,t)=(-mu,t+1/2)에서 짝대칭 rho_j와 주파수4pi로 rho와 coincidence가 불변이다.
E_plus/minus=(G +/- e sqrt(R)mu)/2, G=A+e, R=H/(A^2+2Ae).
integral_C mu dm=0. 따라서 selected daughter count=2Y, pair total energy=GY,
각 mathematical label energy=GY/2. 이 에너지는 rest energy를 포함한다.

geometry를 a turns 회전하면 effective coefficients는
bc'=bc cos(4pi a)+bs sin(4pi a), bs'=-bc sin(4pi a)+bs cos(4pi a).
특히 a=1/8이면 (bc',bs')=(bs,-bc), 정확 유리수 rotation covariance 검사가 가능하다.
geometry와 beam law를 함께 같은 각도로 돌릴 때는 반대 coefficient transform을 적용한다.

## 5. 독립 기준 사례

1. rho=(1/2)[1+lambda cos4pi t+kappa sin4pi t], lambda^2+kappa^2<=1.
   full polar A=arc(a,w), B=arc(a+1/2,w), 0<=w<=1/2이면
   Y=2w+lambda[sin4pi(a+w)-sin4pi a]/(2pi)
      +kappa[cos4pi a-cos4pi(a+w)]/(2pi).
   w=1/8이면 Y=1/4+[(lambda+kappa)cos4pi a+(kappa-lambda)sin4pi a]/(2pi).
   lambda=3/5,kappa=4/5로 coefficient cone의 경계를 실제 사용한다.
   a=0,1/8,1/4,3/8과 0..1의17-point rotation을 같은 검증 실행에서 저장한다.
2. full A=B: Y=sigma, assignments=2sigma, overlap=sigma, daughters=2sigma.
   동일한 half-circle A=B에서는 Y=0, both-detectors-hit=sigma.
3. nonseparable rho0=1/2, rhoc=mu^2/2, rhos=0:
   b0=(1/2,1/2,1/2), bc=(1/2,-1/2,1/2),bs0.
   fullpolar a0,w1/8: Y=1/4+1/(6pi).
   model A3,M2,e8/3에서 k=40/51, forward A [0,1]xarc(0,1/8),
   backward B [-1,0]xarc(1/2,1/8):
   Y=(1-k)/8+(1-k^3)/(12pi), H_A=(1+k)/8+(1+k^3)/(12pi), H_B=Y.
   conditional_A=Y/H_A, conditional_B=1. 평균 harmonic1/3로 대체한 값과 차이가 난다.
   global angular marginal을 separable law로 대입한 잘못된 값도 diagnostic으로 저장한다.
4. uniform bc=bs=0은 동일 explicit delta에서 기존 AZIMUTH09 enclosure와 정확히 같다.
5. degree8/N8 stress: b0 모두1/2, bc_i=(-1)^i/2,bs0 (rhoc=mu^8/2),
   increasing model A3,M2,e8/3; windows=(-4/5+i/5,-7/10+i/5), i0..7,
   arcs=(i/64,1/8), A first4/B last4. 실제 nonzero boundary bisections를 요구한다.
   이는 이 specific case의 finite stress이지 모든 worst-case runtime 검증이 아니다.
6. Native stored masses NIST alpha3727.3794118, deuteron1875.61294500MeV,
   e=213,258,330, b0=(0,3/2,0),bc=(0,9/10,0),bs=(0,6/5,0),
   A polar[-1,-1/2]arc(0,1/8),B polar[1/2,1]arc(1/2,1/8).
   manufactured angular law, exact stored mass values; measurement uncertainty 미포함.

그 밖의 최소 검사는 invalid types/degree/cone/evenness/law/delta, zero density/empty geometry,
wrap/overlap semantics, cardinal sin/cos와 independent high precision analytic oracle,
reflection/rotation, fold/stopped/increasing geometry 연결, conditional unresolved,
manual-delta 실제 폭/기본 폭 차이, linear count-energy scaling과 resource evidence다.
테스트 수를 미리 PASS로 기록하지 않는다. 실제 unique method count와 결과를 기록한다.

독립 oracle의 pi decimal lower는
3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679,
upper는 여기에10^-100을 더한 값이다. 정확 분수 endpoint 또는 Decimal80 이상으로
독립 closed-form oracle을 계산하라. 이 decimal interval도 단일 Wolfram 검산에 포함한다.
oracle 비교는 production 내부 trig helper를 기대값 계산에 사용하지 않는다.

## 6. 구현·실행·검토 계약

Lower-tier가 src/harmonic.py, tests/test_harmonic.py, bounded runner, saved-only plotter,
결과 직렬화와 mechanical packaging을 담당한다. Astra parent가 이 계약/유도/판정을 담당하고,
별도 Astra reviewer가 같은 한 pass 안에서 static와 actual result/원 plot을 읽는다.
결함이 있으면 구체적인 수정 범위가 lower-tier로 돌아간다. 재귀 reviewer를 만들지 않는다.

새 validation cumulative cap: CPU20s, wall60s, address space512MiB/process, threads1.
initial scientific suite1회, 새 진단에 따른 targeted repair reserve1회가 같은 cumulative cap 안에 있다.
이전 HE09 reserve1과 무관하다. 실행 전 source commit을 고정하고 원 결과/log를 보존한다.
기존 measure_execution/run_bounded를 새 unit 경로로 최소 이식한다. measured whole process CPU는
inner runner startup 및 waited children을 포함하며 outer orchestration CPU는 따로 적는다.
모든 descendant에 대한 strict aggregate preemptive resource enforcement로 확대하지 않는다.

새 plot cap: first attempt1, CPU10s, wall30s, AS512MiB/process, threads1.
검증 중 저장한 JSON만 읽어 PNG/SVG 4panel을 만든다: orientation curve, nonseparable
oracle-vs-naive, native energy row results, actual polar/arithmetic widths. 과학 import/call0.
재렌더 없이 원 PNG를 parent/reviewer가 읽는다. cold/warm font cache 상태를 기록한다.
도표 출력 시간도 whole CPU에 포함한다. old failed plots를 다시 만들지 않는다.

Wolfram evaluator는 별도15s timeConstraint로1회 예정: Machin identity, derivative primitives,
Bernstein integrals/symmetry, cone examples, rotation/analytic oracles, width inequalities.
원 raw response와 code를 보존한다. remote CPU가 없으면 null. contextlookup은 evaluator와 구분.

## 7. 단계별 산출과 게시

S01=R1/C1 연구범위/복원기준/DAG; S02=R2/C2 조사·문헌·식-코드 대응;
S03=R3/C3 명제·signed measure·primitive 설계; S04=R4/C4 후보 선택·유도·독립 oracle/예산;
S05=R5/C5 구현·static same-pass review; S06=R6/C6 실제 suite·independent comparison;
S07=R7/C7 단일CAS·과학 결과 연결; S08=R8/C8 saved-only plot·오차/자원 판정;
S09=R9/C9 최종 independent result review·scoped adoption;
S10=R10/C10 종료·인계. 각 stage actual source publication 및 Drive/Dropbox ACK 뒤 다음 진행.
Source Git은 creation-time PREPUBLICATION snapshot이고 외부 stage ACK는 actual이다.
local execution commit과 remote publication commit은 구별하고 full tree equality를 기록한다.
Central은 마지막에 fresh HEAD/AGENTS, HE 허용9경로만 반영, expected SHA/force=false와 actualreadback.
Final external metadata_scope=POSTPUBLICATION_EXTERNAL_DELIVERY.

세 physical inputs와 population_rest_energy_witness 단일 binding ownership를 보존한다.
Independent binding RHS/Gamma_thermal/Cv/species_heating/thermal_deposition=null,
birth_pool=UNASSIGNED, global physical completion=null,L4=false,production=NOT_APPROVED.
KINEMATIC08 plot7.040661/6FAIL/workflowPARTIAL, PHOTON05plot4.40726504/4FAIL,
APERTURE07plot4.489548029/6PASS, HE101C8PARTIAL_EXPORT19/20/원PASS-FAIL-FAIL를 보존한다.
HARMONIC10 종료 뒤 새 지시 전에는 정지한다.
