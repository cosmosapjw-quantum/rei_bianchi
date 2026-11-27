# ANGULAR06: 유한질량 각도 사상, 역상 분기와 사건 measure

## 범위와 근거

PHOTON05의 정지 bare alpha + photon -> 두 bare deuteron 운동학을 재사용한다. 이번 결과는 그 운동량을 각도 밀도와 branch별 관측량으로 옮기는 조건부 변환이다. 원 PHOTON05 24/24 및 plot CPU FAIL을 재실행하거나 변경하지 않는다. 원자료의 12개 좌표는 그대로이며 실제 DCS의 particle/event 정규화와 전각 law, flux, named deposition은 열린 입력이다.

직접 유도는 아래 정리 1–4와 `review/INDEPENDENT_DERIVATION_KO.md`에 있다. Wolfram의 derivative, discriminant, transition 차이 검산은 `evidence/WOLFRAM_ANGULAR_IDENTITY.json`에 원 warning과 함께 보존한다. 이 정리들의 문헌 신규성이나 no-go는 주장하지 않는다. Exa/SciSpace 조사에서 Arends et al. PLB62(1976)411–412, DOI10.1016/0370-2693(76)90671-7을 식별했으나 정규화 식을 담은 본문은 확보하지 못했다. Rice et al. PRC61(2000)064612의 다른 에너지 구간·fit을 대신 채택하지 않는다.

## 1. 컨벤션과 전제

계량은 (-,+,+,+), 에너지 단위 사운동량은 q^a=(E,c p)다. A=m_alpha c^2, M=m_d c^2, photon energy e를 같은 MeV 단위로 쓴다. 0<A<2M의 endothermic channel을 택한다. 표적은 lab에서 정지하고 전자·표적운동·실험 응답은 아직 이 모델에 결속되지 않았다.

Delta=2M-A, e_th=Delta+Delta^2/(2A), W=sqrt(A^2+2Ae), E*=W/2,
kappa=sqrt[A(e-e_th)/2], gamma=(A+e)/W, beta=e/(A+e).

이 절부터 e>e_th로 두어 kappa>0이다. CM의 한 labeled daughter 방향을 mu=cos(theta*), phi로 표시하고 photon 방향을 z축으로 둔다. 두 daughter의 교환은 u -> -u, 즉 (mu,phi)->(-mu,phi+pi)다.

## 2. 정리 1: 사상·Jacobian·support

상대론적 boost에서 q_z=gamma*kappa*mu+e/2, |q_perp|=kappa*sqrt(1-mu^2). a=e/(2gamma*kappa), D^2=1-mu^2+gamma^2(mu+a)^2라 두면

    nu=cos(theta_lab)=gamma(mu+a)/D,
    phi_lab=phi,
    dnu/dmu=gamma(1+a*mu)/D^3.

증명은 q_z와 |q|=kappa D의 비를 미분하면 된다. 분자의 미분에서 D^2-(mu+a)[gamma^2(mu+a)-mu]=1+a*mu가 남는다. 따라서 dOmega=dmu dphi의 밀도에 들어가는 절대 Jacobian은 J=|dnu/dmu|다. 부호 있는 미분은 역상 분기의 방향을 기록한다. 동등한 운동량 표현은 J=kappa^2*|gamma*kappa+(e/2)mu|/|q|^3이며 모든 인자는 같은 에너지 단위라 J는 무차원이다.

* 0<=a<1: D>0이고 derivative>0. [-1,1] 전체의 단사 사상이다.
* a=1: mu=-1에서 q=0, 방향 undefined. 나머지는 nu in(0,1]에 단사 대응한다.
* a>1: mu_c=-1/a에서 derivative=0. mu<mu_c에서는 감소, mu>mu_c에서는 증가한다. 모든 lab 방향은 forward이고

    nu_min=gamma sqrt(a^2-1)/sqrt[1+gamma^2(a^2-1)].

nu_min<nu<1에는 두 역상, nu=nu_min에는 합쳐진 한 역상, nu=1에는 양 CM pole이 대응한다. 전각 적분에서 한 분기를 버리거나 signed Jacobian으로 밀도를 나누면 양성성 또는 정규화가 깨진다.

## 3. 정리 2: 정확한 역상과 문턱의 구분

G=gamma^2(1-nu^2), L=G+nu^2, B=L-a^2 G로 두면 원식의 제곱은

    L mu^2+2aG mu+(a^2 G-nu^2)=0

을 준다. 판별식은 4nu^2 B이고 후보는

    mu_±=[-aG ± |nu|sqrt(B)]/L.

B>=0, |mu|<=1, D>0과 원식의 sign(mu+a)=sign(nu)를 다시 적용해야 한다. nu=0은 mu=-a가 허용 domain 안에 있을 때만 대응한다. a<1에서 하나의 유효 root는 [-aG+nu sqrt(B)]/L이다. a=1에서는 quadratic의 stopped root를 제거하여 mu=2nu^2/L-1만 남긴다.

Lab daughter가 정지하는 조건은 (A+e-M)^2-e^2=M^2다. A>M이면

    e_tr=A(2M-A)/[2(A-M)],
    e_tr-e_th=M(2M-A)^2/[2A(A-M)]>0.

즉 threshold와 stopped-direction transition은 서로 다르다. M<A<2M에서 e_th<e<e_tr는 fold, e>e_tr는 한 분기다. A<=M에는 유한한 transition이 없고 모든 e>e_th가 fold regime다.

정확 e=e_th에서는 kappa=0이고 두 daughter q=(e/2)n이다. 방향 measure는 nu=1의 원자로 붕괴하므로 연속 밀도로 나누지 않는다. a=1의 stopped daughter에 원자 질량이 놓이면 zero-momentum atom을 별도로 보존해야 하며 임의 방향을 붙일 수 없다.

## 4. 정리 3: 밀도와 관측량의 pushforward

명시적으로 주어진 CM density f(mu,phi)에 대해 regular lab 방향의 밀도는

    g(nu,phi)=sum_i f(mu_i,phi)/J(mu_i).

이는 test function psi에 대한 integral psi(F(mu),phi) f dmu dphi를 단조 branch별로 변수변환하면 얻는다. 원자의 pushforward는 별도 합으로 처리한다. azimuth에 대한 평균은 이 식에 포함되지 않는다.

fold에서 nu''_c=gamma*a/D_c^3>0이다. delta_nu=nu-nu_min이 양으로 작을 때 mu_±=mu_c ±sqrt(2delta_nu/nu''_c)+O(delta_nu). f가 연속이고 f(mu_c)!=0이면

    g ~ sqrt(2) f(mu_c,phi)/sqrt(nu''_c delta_nu).

따라서 pointwise density는 발산하지만 finite angular bin mass는 O(sqrt(delta_nu))로 유한하다. 구현은 fold의 density를 None으로 반환하고 유한값을 제조하지 않는다. f가 fold에서 소거되면 실제 limit는 별도 regularity에 의존한다.

관측량 W를 함께 운반할 때 필요한 식은

    g_W(nu,phi)=sum_i f(mu_i,phi) W(mu_i,phi)/J(mu_i).

같은 nu라도 두 branch의 E=gamma E*+gamma beta kappa mu는 다르다. g만 보관하고 하나의 E를 붙이면 energy/stress를 일반적으로 잃는다. 구현의 weighted_density는 각 branch의 mu, J, f, W와 기여를 함께 반환한다. Pair stress는 PHOTON05의 q_i q_j/E를 그대로 가중하며, rest/binding 소유권을 다시 배정하지 않는다.

## 5. 정리 4: 동일입자 정규화

물리적인 unordered event orientation은 S^2/{u~-u}다. 전체 구면에 대칭적으로 lift한 event density f를 integral f=Sigma_event로 정규화한다. Inclusive daughter density h=2f는 integral h=2Sigma_event를 만족한다. B를 단일 daughter 관측량, F=B(q_+)+B(q_-)를 pair 관측량이라 하면

    integral f F = (1/2) integral h F = integral h B(q_+).

마지막 등식은 u->-u 교환과 f의 evenness에서 따른다. 한 hemisphere에 대표를 하나씩 두는 density H는 그 domain에서 h와 같고 integral H=Sigma_event다. Hemisphere에서 single contribution만 적분하면 다른 daughter를 잃으므로 반드시 pair를 더한다. Equator atom에는 별도 deterministic 대표 선택이 필요하다.

코드는 세 convention을 문자열로 요구하며 알 수 없는 convention을 거부한다. M0475002의 DATA-CM convention은 확인되지 않았으므로 그 숫자에 자동 1/2 또는 2를 적용하지 않는다. Event count, material nuclear count, 열용량과 열화 에너지는 각자 다른 양이다.

## 6. 계산 계약과 검증 경계

계산은 Decimal80 중간 연산과 binary64 입출력을 사용한다. 질량 domain·threshold·transition admission은 Fraction.from_float의 정확한 유리수에서 비교한다. 반환 threshold의 반올림 값을 물리 admission에 쓰지 않는다. 정규 방향의 역상은 cancellation을 줄인 quadratic pivot 및 root product로 구성한 뒤 원식 부호를 확인한다. 결과는 interval certificate가 아니다.

일반 map의 구현 domain은 1<=gamma<=10^6, 0<=a<=10^6이다. 수학적으로 유효해도 fold cone·root가 binary64로 분해되지 않으면 AngularResolutionError를 낸다. fold_mu/nu_min의 binary64 좌표는 명시적인 API boundary sentinel이다. 이 저장 좌표를 정확한 실수 fold와 동일하다고 주장하지 않는다.

검증은 기존 저장된 12개 사건의 q에서 직접 얻은 lab cosine, 별도 Decimal vector 미분·bracketed inverse, finite-bin 질량, 두 branch의 서로 다른 energy, discrete quotient 정규화, invalid input 및 극한으로 수행한다. 새 plot은 이 검증이 저장한 각도/Jacobian/branch 데이터만 읽는다. PHOTON05의 운동학 suite나 그림을 다시 실행하지 않는다.

PHOTON05의 세 physical-input 의무, HE101 C8 PARTIAL_EXPORT19/20·reserve0·PASS/FAIL/FAIL과 모든 caloric/thermal null port는 유지한다. Local conditional DAG와 중앙27/88, global physical completion null은 서로 다른 집계다.
