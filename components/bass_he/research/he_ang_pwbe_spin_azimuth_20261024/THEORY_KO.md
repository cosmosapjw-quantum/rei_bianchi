# HE-ANG-PWBE-SPIN-AZIMUTH — 이론과 구현 계약의 기준식

## 1. 목표와 근거 상태
이번 단위는 수소 1s 전자충돌 이온화의 명시적인 plane-wave first-Born exchange(PWBE) 모형에서 spin-averaged joint TDCS와 relative-azimuth conditional law를 구성한다. 원전의 직접/교환 진폭, 독립 spin trace, 정확한 방위각 적분과 양성을 드러내는 계산식을 연결한다. 기존 DDCS20/CCC/TDCS54는 근거와 비용 원장을 재사용하고 재실행하지 않는다.

원전 입력: Weigold, Noble, Hood, Fuss, FIAS-R-39 (June 1978), report p18 Eqs19–20. 실제 PDF SHA256 aaa750d5d5f0652ba7e6090878f938174fc26268265c256022c4d9437c3a96a8. Eq21의 인쇄된 −2DX는 보존하되 unpolarized law로 채택하지 않는다. 본문에서 사용한 전자 spin 평균은 아래 독립 trace로 정의·유도한다. Buică arXiv2306.08573v1 Eq46은 별도 spin-weight 교차 근거이고, 후속2023erratum 본문 미확보 때문에 이 유도의 필수 전제가 아니다. Buică의 Born–Ochkur exchange와 이번 exact-swapped PWBE exchange는 서로 다른 근사이다.

전체 HE-ANG physical provider는 SOURCE_INPUT_PENDING이다. 이번 admission 대상은 명시적 nonrelativistic fixed-center PWBE model과 그 수학·구현이다. 모델의 실제 정확도, finite-mass recoil, full kinetic consumer admission은 별도 열린 의무이다. 새 strong no-go를 주장하지 않는다.

## 2. 모형·단위·정의역
양성자 질량을 무한대로 두고 초기 H(1s)를 정지시킨다. 방출 후 residual-ion/electron-electron Coulomb distortion은 plane-wave final-state 근사에서 빠져 있다. First Born을 사용한다. 입사/초기 bound electron spin은 각각 unpolarized이며 final spin은 분해하지 않는다.

원전의 atomic-unit 변수를 사용하되 의미를 명시한다:
k=p a0/hbar, epsilon=E/Eh, Eh=hbar^2/(m_e a0^2).
결합에너지는 이 수학 모형에서 정확히 1/2 Eh이다. 원전의 반올림된13.6eV를 수학적 exact값으로 혼합하지 않는다.
출력 numerical TDCS K의 물리 단위 복원은 (a0^2/Eh) K이며 measure는 dE_B dOmega_A dOmega_B이다.
Nonrelativistic 물리 적용에는 E0 << m_e c^2가 필요하다. 정확도 수치 인증은 이번 결과에 포함되지 않는다.

epsilon0>1/2,
epsilonA+epsilonB=epsilon0−1/2,
k_i=sqrt(2 epsilon_i), epsilonA,epsilonB>0.                 (1)

A=fast, B=slow의 ordered event convention은 epsilonA>epsilonB를 interior로 한다. Equal-sharing boundary는 pointwise density와 symmetry 검산에 허용한다. 완전 labeled-domain algebra는 별도 diagnostic mode로 표시한다. 입사축은 +z이고 mu_A,mu_B∈[−1,1], phi∈[0,2pi).
dOmega=dmu dvarphi의 양의 측도이며 polar-angle theta 입력으로 바꾸면 각 sin(theta) Jacobian이 필요하다.

k0=(0,0,k0)
kA=(kA sqrt(1−mu_A^2),0,kA mu_A)
kB=(kB sqrt(1−mu_B^2) cos(phi),
    kB sqrt(1−mu_B^2) sin(phi),kB mu_B).                  (2)

q=k0−kA−kB, Delta_A=k0−kA, Delta_B=k0−kB.
q는 fixed-center 모형의 전달 운동량이다. q^2/(2m_p)의 에너지 feedback이나 유한질량 recoil law는 계산하지 않는다.

## 3. Direct amplitude의 구성과 exchange
phi_1s(r)=exp(−r)/sqrt(pi),
phi_tilde(p)=(2pi)^(-3/2) int exp(−ip.r)phi_1s(r)d^3r
            =(2sqrt(2)/pi)/(1+p^2)^2.                  (3)

이는 int exp(−r)exp(−ip.r)d^3r=8pi/(1+p^2)^2에서 따른다.
Projectile perturbation V=1/|r0−r1|−1/r0의 Fourier transform은
(4pi/Delta_A^2)(exp(iDelta_A.r1)−1).
초기/최종 projectile plane-wave normalization (2pi)^−3을 포함하면,

D = sqrt(2)/pi^3 * d,
X = sqrt(2)/pi^3 * x,
d = alpha(t−h_B), x = beta(t−h_A),
alpha=1/Delta_A^2, beta=1/Delta_B^2,
t=(1+q^2)^−2, h_i=(1+k_i^2)^−2.                         (4)

X(kA,kB)=D(kB,kA). Nuclear subtraction h_B/h_A를 모두 보존한다.
(4)는 FIAS Eqs19–20과 일치한다. Scattering amplitude convention F_D=−(2pi)^2D, F_X=−(2pi)^2X이며 |common factor|=4sqrt(2)/pi이다.

On-shell (1)에서는 k_A,k_B<k0이므로 Delta_i^2>0. 계산에는
Delta_i^2=(k0−k_i)^2+2k0 k_i(1−mu_i)
를 써서 작은 차를 큰 제곱끼리 빼지 않는다.
t−h_i는 필요시 [(1+k_i^2)−(1+q^2)] [(1+k_i^2)+(1+q^2)]
/[(1+q^2)^2(1+k_i^2)^2]로 계산할 수 있다.
노드와 threshold 인근의 relative accuracy는 아래 finite fixture 범위에서만 수치 검증한다.

## 4. Spin trace와 count
두 spin-1/2 공간에서 swap P는 P^2=I4, P^dagger=P, Tr(P)=2이다.
M=D I4−X P, rho_in=I4/4로 두면

Tr(M rho_in M^dagger)
=|D|^2+|X|^2−Re(D X*)                                  (5)
=1/4 |D+X|^2 +3/4 |D−X|^2.

P eigenvalue−1의 singlet는 차원1, +1의 triplet는 차원3이다.
FIAS Eq21의 real bracket D^2+X^2−2DX는 |D−X|^2와 같고,
(5)의 unpolarized average와 일반적으로 다르다.
D=X≠0에서 전자는0, (5)는|D|^2이다. 이는 특정 인쇄식의 양화된 적용 차이이며 새로운 일반 no-go 성과가 아니다. 원전의 의도나1979journalversion의 교정을 추정하지 않는다.

Physical model TDCS는 source transition normalization을 사용하여
K=(2pi)^4 kA kB/k0 [1/4|D+X|^2+3/4|D−X|^2]
 =(32/pi^2) kA kB/k0 w,
w=d^2+x^2−dx = (d−x/2)^2+3x^2/4.                       (6)

Source plane-wave amplitudes는 real이다. 일반 complex spin helper에는 (5)를 사용한다.
Spin weighting은 (6)에서 한 번 적용한다. Pointwise TDCS에 추가2나4를 곱하지 않는다.

Exchange map (EA,OmegaA,OmegaB) -> (EB,OmegaB,OmegaA)는 absolute Jacobian1이며 K invariant다.
전체 labeled energy interval(0,epsilon0−1/2)을 적분하면 동일 unordered event를2번 센다.
따라서 event integral은 strict ordered half-domain에서 factor1, 또는 full labeled domain에서 factor1/2를 사용한다. Equal-energy boundary는 energy measure0이므로 pointwise density에 별도half를 부여하지 않는다.
이 단위에서는 energy/global-angle event integral을 실행하거나 total event sigma로 보고하지 않는다.

## 5. 상대 방위각의 정확한 적분
R_A=kA sqrt(1−mu_A^2), R_B=kB sqrt(1−mu_B^2),
z=k0−kA mu_A−kB mu_B,
a=1+z^2+R_A^2+R_B^2, b=2R_A R_B >=0.
그러면 1+q^2=a+b cos(phi).                              (7)

a−b=1+z^2+(R_A−R_B)^2>0,
a+b=1+z^2+(R_A+R_B)^2.
rho=sqrt((a−b)(a+b))를 이 양의 식으로 계산한다.
I_n=(1/2pi) int_0^(2pi) (a+bcos(phi))^−n dphi,
J_n=(1/2pi) int_0^(2pi) cos(phi)(a+bcos(phi))^−n dphi.

I1=1/rho, I_(n+1)=−(1/n)partial_a I_n이고 따라서
I2=a/rho^3,
I3=(2a^2+b^2)/(2rho^5),
I4=a(2a^2+3b^2)/(2rho^7),
J2=−b/rho^3,
J4=−b(4a^2+b^2)/(2rho^7).                              (8)

J_n=(I_(n−1)−a I_n)/b로 유도하되 구현은 b로 나누지 않는 (8)을 사용한다. b=0에서 I_n=a^−n,J_n=0이다.
I1은 tan(phi/2) substitution으로 얻고, a>|b|가 integrand의 uniformly positive denominator를 주므로 이 유한차수 미분과 적분을 교환할 수 있다.

A2=alpha^2+beta^2−alpha beta,
A1=−2alpha^2h_B−2beta^2h_A+alpha beta(h_A+h_B),
A0=alpha^2 h_B^2+beta^2 h_A^2−alpha beta h_A h_B.
w=A2 t^2+A1 t+A0이므로
M0=<w>_phi=A2 I4+A1 I2+A0,
M1=<w cos(phi)>_phi=A2 J4+A1 J2.                        (9)

### 양성 계산식
m=I2,
v=Var_phi(t)=I4−I2^2
 = a b^2(5a+3rho)/[2rho^7(a+rho)] >=0.
dbar=alpha(m−h_B), xbar=beta(m−h_A).
M0=A2 v+(dbar−xbar/2)^2+3 xbar^2/4.                    (10)

(10)은 polynomial cancellation으로 작은 음의 density를 만드는 위험을 줄인다.
A2=(alpha−beta/2)^2+3beta^2/4>0. Arbitrary epsilon-clipping이나 abs(M0)를 사용하지 않는다. (9)는 독립 대수 교차식으로 보존한다.
M1은 부호를 갖는 moment이므로 (9)를 그대로 사용한다. 매우 작은 M0로 나눈 conditional moment는 conditioning을 함께 보고한다.

## 6. Conditional law와 angular correlation
P0=(32/pi^2) kA kB/k0.
Kbar=P0 M0, Cbar=P0 M1.                                (11)
M0>0인 geometry에서
p(phi|epsilon0,epsilonB,muA,muB)=K(phi)/(2pi Kbar),
int p dphi=1,
E[cos(phi)]=M1/M0, E[sin(phi)]=0,
E[nA.nB]=muA muB+sqrt(1−muA^2)sqrt(1−muB^2) M1/M0.       (12)

M0=0이면 해당 conditional law는 정의되지 않으며 API는 명시적으로 알려야 한다.
전체 두 solid-angle 적분을 향후 수행할 때
int dOmegaA dOmegaB K=(2pi)^2 int_-1^1 dmuA int_-1^1 dmuB Kbar.
여기서 첫2pi는 overall azimuth, 둘째2pi는 relative azimuth average의 복원이다. 이번에는 이 global integral을 수행하지 않는다.

## 7. 검증 계획·범위
독립 R6에서 원전 진폭과 spin/count, (8)–(12)를 검토한다. Wolfram은 finite symbolic identities와 손으로 제시한 oracle를 검산한다. Lower-tier 구현은 새로운 함수와 raw results만 작성한다.

Hand oracle:
- complex d=1+2i,x=3−i: singlet17,triplet13,unpolarized14.
- d=x=2+i: unpolarized5,triplet0.
- a=5,b=3,rho=4: I2=5/64,I4=385/32768,
  J2=−3/64,J4=−327/32768,v=185/32768.
- vectors k0=(0,0,5), kA=(0,0,4), kB=(2,0,2):
  on-shell25=16+8+1, q^2=5, DeltaA^2=1,DeltaB^2=13,
  d=5/324, x=253/135252.
이들은 algebraic fixtures이며 실험 정확도 데이터가 아니다.

새 numerical demonstration은 epsilon0=100,epsilonB=40 및 equal-sharing49.75의 fixed-center high-energy model이다.
고정 geometry는 모두 epsilon0=100에서 다음 여섯 가지다:
G1: epsilonB=40,muA=1,muB=0.2;
G2: epsilonB=40,muA=0.8,muB=0.6;
G3: epsilonB=40,muA=−0.4,muB=0.75;
G4: epsilonB=40,muA=239/(2sqrt(23800)),muB=161/(2sqrt(16000));
G5: epsilonB=49.75,muA=muB=0.5;
G6: epsilonB=49.75,muA=1,muB=−1.
G4는 phi=pi에서 q=0인 triangle이며 a−b=1,b=95.1975이다.
G1/G6은 b=0이고 G5는 exact equal-sharing/equal-polar triplet node이다.
별도 해석적 zero-density 예제 epsilon0=9/14,epsilonA=epsilonB=1/14,
muA=muB=1은 q^2=kA^2=kB^2=1/7이므로 D=X=M0=0이다.
이 예제에서는 conditional law가 정의되지 않는다. Binary64에서 작은 값을 임의의
epsilon으로0에 붙이지 않으며, 정확한 algebraic zero와 finite arithmetic을 구별한다.
Periodic trapezoidal azimuth quadrature N=64,256,1024,2048로 여섯 고정 geometry의 Kbar와 Cbar를 독립적으로 대조하고 마지막 level relative M0 error<=1e−10, |delta(M1/M0)|<=1e−10를 요구한다. 이 finite-case 검증을 전역오차 정리로 확대하지 않는다.
Source table의 relative observations는 미전사·미사용이다. 기존 TDCS54/DDCS20 데이터를 이 모형에 fit하거나 정규화하지 않는다.

Source model의 actual error envelope와 electron-electron/residual-ion final-state dynamics, calibrated full source payload 및 finite-mass consumer 계약은 후속 의무이다.

