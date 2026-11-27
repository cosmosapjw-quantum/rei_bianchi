# HE-DD ANGULAR MOMENT ENCLOSURE: source-conditional two-deuteron variance

2026-10-29 · Parent BASS_HE Draft PR108, HEAD `e1587adb8fc515384014dd0838b93e5961308bfd`

## 1. 출처와 주장 범위

현재 자료는 IAEA-NDS `exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871`,
`exforall/M04/M0475.x4`, EXFOR Git blob `c49433293921dbb012d7f1b0387745732a598efa`,
원본 SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`.
PR105의 source-verified 330 MeV 네 행을 **전사하여 재사용**하였고, 이번 세션의
로컬에서 원자료 3,349바이트 전체를 다시 해시했다는 주장은 하지 않는다.
Arends et al., *Phys. Lett. B* 62 (1976) 411–412, DOI 10.1016/0370-2693(76)90671-7.
Silverman et al., *Phys. Rev. C* 29 (1984) 35, DOI 10.1103/PhysRevC.29.35.
두 실험의 원문 detector efficiency·event/particle normalization 및 polarization은
이번 추가 탐색에서도 source-qualified되지 않았다.

중심 물리 질문은 **사건당 두 D의 평균 운동에너지는 각분포와 무관하지만,
그 단일 입자 분산과 비선형 stopping/deposition은 얼마만큼 제한할 수 있는가**이다.

## 2. 가정과 정확 함수족

metric (-,+,+,+), c 유지. PR104의 rest-energy 관례
M=M_alpha c²=3727.3794118 MeV, m=m_d c²=1875.61294500 MeV.
정지 알파 표적에서 E_gamma=330 MeV, s=M²+2ME,
K±=K0±Delta μ, K0=(M+E-2m)/2, Delta²=E²(s-4m²)/(4s),
μ=cos(theta_CM). θ는 degree 단위 0..90, 적분 삼각함수는 radian으로 변환.

PR105에서 선언한 (측정되지 않은) global Lipschitz L [nb/sr/degree], 비음수,
θ↔180°−θ의 동일-D exchange symmetry, azimuthally averaged angular
density f(θ)를 가정한다. 330 MeV M0475002 행은
46°: 0.14±0.03, 61°:0.16±0.05, 73°:0.07±0.05,
87°:0.19±0.05 [nb/sr]. `ERR-S`는 좌표별 통계오차이며
[DA−ERR-S, DA+ERR-S]는 **동시 신뢰구간이 아닌 sensitivity box**이다.
전역 함수족이 공집합이 아니려면 L≥Lmin=1/700 [nb/sr/degree]가 필요하고 충분하다.

각 행 (θ_i, l_i, u_i)에서 두 점별 envelope:
f_-(θ)=max(0, max_i{l_i−L|θ−θ_i|}),
f_+(θ)=min_i{u_i+L|θ−θ_i|}.
두 envelope는 그 자체가 source boxes에 들어가는 L-Lipschitz 양의 함수로
실현 가능하며 모든 허용 f에 f_-≤f≤f_+다.

**중요:** f의 전역 physical event/particle 정규화가 일정한 양의
상수 κ의 곱인 경우에 한하여 아래 비율에서 소거된다. 각도 의존 detector
acceptance, polarization response, beam smearing, data correlations가
같은 상수로 소거된다는 뜻은 아니다. 따라서 이 수치를 실측 각분포의
확정 분산이나 실제 반응률로 쓰지 않는다. κ=1/2 선택하지 않는다.

## 3. 정리: 정규화된 2차 각도 모멘트의 유효한 외측 경계

표기 z=πθ/180, w(z)=sin(z), v(z)=cos²(z), 0≤z≤π/2.
D(f)=∫ f(z)w(z)dz>0, N(f)=∫ v(z) f(z)w(z)dz,
b(f)=N(f)/D(f)∈[0,1]. 이 정의는 full-sphere 공통 상수 4π와
고정 multiplicity κ를 소거한다.

0≤t≤1에서 sign-split 함수
L(t)=∫_{v≥t}(v−t)w f_- dz − ∫_{v<t}(t−v)w f_+ dz,
U(t)=∫_{v≥t}(v−t)w f_+ dz − ∫_{v<t}(t−v)w f_- dz
를 정의한다.

모든 허용 f에 L(t)≤N(f)−tD(f)≤U(t). 실제 증명은 양의
계수에서는 f_-≤f≤f_+를 그대로, 음의 계수에서는 부등식 방향을
반대로 적용하고 적분한다. 함수 L,U는 연속 감소하며 L(0)>0,
L(1)<0, U(0)>0, U(1)<0이다. 따라서 각 함수의 유일 영점
t_L,t_U가 존재하여

        t_L ≤ b(f) ≤ t_U

가 성립한다. t_L에서는 N−t_L D≥L(t_L)=0,
t_U에서는 N−t_U D≤U(t_U)=0이다.

**Sharpness 상한 금지.** L(t),U(t)의 정의에서 양/음 구간별로 서로
다른 envelope를 택하는 패치는 일반적으로 Lipschitz 정칙성을
위반할 수 있다. 그러므로 이 부등식은 *유효한 외측 경계*이고
무조건 sharp optimum은 아니다. f_- 및 f_+를 그대로 적분하여 얻는
b(f_-), b(f_+)는 feasible **내측 증인**이다. 이 두 종류를
동일한 confidence interval이나 물리적 measured errorbar로 혼합하지 않는다.

양의 모멘트의 계산 형태는 각 piecewise affine 구간
f(z)=A+Bz에 대해 다음의 정확 원시함수를 사용한다:

∫f(z)sin z dz = −A cos z + B(−z cos z+sin z);
∫f(z)cos²z sin z dz =
    −A cos³z/3+B(−z cos³z/3+sin z/3−sin³z/9).

θ_t=acos(sqrt(t))에서 부호를 분할한 뒤 별개의 envelope를
각 구간에서 적분한다. θ breakpoints/계수는 Fraction exact,
π 및 삼각적분은 mpmath 고정밀 비인증 근사다.

## 4. 조건부 수치 결과: 330 MeV

| L [nb/(sr deg)] | b outer lower | b outer upper | b(f_-) | b(f_+) |
|---|---:|---:|---:|---:|
| 1/700 | 0.279238681235 | 0.386397436244 | 0.282995665573 | 0.378877871746 |
| 1/200 | 0.186315404014 | 0.472747698143 | 0.223067503898 | 0.401728534255 |
| 1/100 | 0.133108297140 | 0.573194162276 | 0.203508829274 | 0.418894056093 |

Delta²(330)=3798.601445517089853824 MeV².
Var(K_D)=Delta² b, so outer numerical intervals in MeV²:
L=1/700: [1060.71645818465,1467.76985986180];
L=1/200: [707.73796300803,1795.78008953035];
L=1/100: [505.62536992449,2177.33617338273].
These are NOT outward-rounded certified numerical intervals.
At L=1/200 the historical PR105 total angular enclosure is reproduced:
I_fullsphere∈[1.0068860482429433,2.423539172537024] nb (source-conditional).
No physical event σ, rate or posterior is issued.

## 5. 정리: 비선형 stopping/deposition의 조건부 곡률 예산

h(K) [MeV]가 특정 medium/rest frame, 명시한 시간 창, secondary
routing을 포함하여 *사건 출생 하나의 D가 열 또는 지정된 채널로
남기는 에너지*라는 가상 공급자라고 하자. h∈C² on
[K0−Delta,K0+Delta]이고 |h''(K)|≤H [MeV^-1]라 가정하면

 | E_P[h(K_+)+h(K_-)]−2h(K0) | ≤ H Delta² b ≤ H Delta² t_U.

증명: 두 Taylor remainder의 1차 홀수항이 exact pair에서
상쇄되고, 이중 적분 표현
h(K0+d)+h(K0−d)−2h(K0)
=d²∫_{−1}^{1}(1−|x|)h''(K0+xd)dx를 적용한다.
일방향 convex h''≥0이면 왼쪽의 평균은 2h(K0) 이상이다.
h(K)=K²/Kstar, Kstar≥K0+Delta의 manufactured case에서는
평균=2[K0²+Delta² b]/Kstar로 bound의 dependence가
실제로 나타난다. 이 h는 실물리 stopping model이 아니다.

**중요한 반례/경계:** K_+ + K_- invariant만으로 h(K+)+h(K-)
또는 thermal deposition의 고정값은 나오지 않는다.
C_V, energy redistribution, escaping secondaries와 photon/target
history 부재에서 material temperature/rate claim을 하지 않는다.

## 6. 검증/실패/물리 gate

- Wolfram exact 원시함수 및 pair identity 4개 0, symbolic conditional.
- Python 신규 unittest 21/21 PASS; 8개 SciPy 독립 구간 quadrature 비교
  오차 <2×10^-12; PR105 I bounds 회복; L-family monotonicity;
  feasible envelopes/continuity, angular-dependent acceptance negative control.
- 별도 C++20 long double Simpson + bisection (원뿔 envelope를
  원 코드의 piecewise segments 없이 평가) 3L×2 roots PASS;
  최대 관측 오차 약 8.28×10^-10.
- 초기 Python Fraction/mpmath 혼용 2 FAIL, 정확 형변환 교정;
  초기 figure mathtext escape FAIL, label을 일반 문자열로 교정.
  로그에는 최종 PASS만 아니라 실패 유형도 보존한다.
- `native_distinct_author_R6_C9=NOT_RUN`, old IVPs/science suites NOT_RUN.
- Numeric transcendental outward error bound NOT_RUN.
- Source all-bytes readback THIS_TURN NOT_RUN; historical immutable Git
  blob identity 확인 및 PR105 source-row transcription only.

`kappa=null`, `R_event=null`, `heat_rate=null`,
`physical_activation=false`, `L4=false`, `production=HOLD`.

## 7. 권장 다음 물리 노드

1. 원 논문 Arends1976/Silverman1984 raw detector efficiency/acceptance,
   angular/polarization·event/particle normalization, paired same-s DA를
   물리 소스와 연결한다.
2. 실제 330 MeV total event σ와 high-energy photon number density history,
   alpha target proper density/distribution을 동일 frame에서 받는다.
3. medium-specific nonthermal D stopping redistribution operator h 또는
   \dot K_stop(K,t), secondary/escape router, C_V owner를 확보한다.
4. h의 H bound가 실제 source-qualified일 때 conditional error budget을
   평가하고, 그때만 physical event rate/thermal power admission을
   별도 검토한다.

R6/C9 비저자 독립심사는 현 도구에 native delegation 없음으로 NOT_RUN.
Central 28/88, HE14/18, inherited PR105 2/2, PR106 1/2,
reciprocity1/2, birth-ledger1/2. New conditional-scoped
moment DAG=1/2; physical DAG delta 0.
