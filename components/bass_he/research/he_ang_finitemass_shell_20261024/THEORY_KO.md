# HE-ANG-FINITEMASS-SHELL: 유한 질량 shell, 두 근, 위상공간 사상

## 1. 결과와 원전의 역할

이 단위는 비상대론적 e + H -> e_A + e_B + p 과정의 유한 질량 운동학을 완결한다. 실제 유도 대상은 lab/COM/Jacobi 사상, 양의 outgoing radial root 전부, coarea Jacobian, 좌표 fold 처리, 전체 kinematic phase-space volume, 상수 가중치 검산용 moment이다. 이는 새로운 물리적 amplitude나 event 단면적이 아니다. HE-ANG의 physical provider gate는 SOURCE_INPUT_PENDING을 유지한다.

원전: Kadyrov, Bray, Mukhamedzhanov, Stelbovics, Annals of Physics 324 (2009) 1516–1546, DOI 10.1016/j.aop.2009.02.003, §3.1 pp1527–1528, Eqs72–84 및 Eq79 바로 뒤의 번호 없는 energy identity. 실제 author-hosted published PDF SHA256 c7627a718193fc1ab0181d1c7fbabdc334bcf53a28e3a0870c45cd9827da9165. 원전은 arbitrary finite masses의 reduced masses, canonical Jacobi coordinates, COM Hamiltonian과 breakup shell을 준다. 아래 lab specialization, radial classification, volume/moments는 이 단위에서 유도한다. 원전이 lab detector prefactor나 spin/count prescription을 주었다고 쓰지 않는다.

## 2. 정의와 가정

Electron atomic units: hbar=m_e=e=1. 입사 electron의 lab kinetic energy E0>0, momentum P=(0,0,sqrt(2 E0)); target COM은 lab에서 정지한다. 두 outgoing electron 질량은 1, nucleus 질량은 M>0, binding B>0를 별도 입력으로 받는다. 질량합 T=M+2는 비상대론적 Galilean 질량이다. Binding mass defect B/c^2, 상대론, radiation, extra excitation channel은 이 Hamiltonian의 범위 밖이다.

B=1/2는 이전 nominal fixed-center binding을 유지한 비교 입력이다. B=mu/2, mu=M/(M+1)는 finite-mass Coulomb H1s의 별도 모델 입력이며 두 mode를 혼합하지 않는다. 2022 CODATA M=1836.152673426은 NIST 원전의 central value를 고정 fixture로 사용한다. 그 standard uncertainty 0.000000032는 인용하되 이번 수치 결과에 전파하지 않는다. eV 설명에 쓰는 U=27.2 eV는 이전 단위와 동일한 nominal conversion이며 정밀 Hartree 상수가 아니다.

p_A,p_B,Q는 lab momentum이고 Q=P-p_A-p_B이다. 최종상태 label A/B를 유지한 measure를 정의한다:

  dLambda = d^3 p_A d^3 p_B delta(F),
  F = E0-B - p_A^2/2 - p_B^2/2 - Q^2/(2M).

이 식에는 incident flux, amplitude, Fourier-normalization, spin average, detector acceptance 또는 unordered-event 1/2가 없다. 단위는 momentum^6 / energy이다. 따라서 dLambda나 그 적분을 sigma로 표기하지 않는다.

## 3. Lab와 Jacobi 사상, 전체 support

nu=(M+1)/(M+2), mu=M/(M+1)를 정의한다. A spectator / (B,nucleus) pair convention을 명시하여

  q = p_A - P/T,
  k = (M p_B-Q)/(M+1) = p_B + p_A/(M+1) - P/(M+1)

를 택한다. 역변환은

  p_A = q + P/T,
  p_B = k - q/(M+1) + P/T,
  Q = -k - M q/(M+1) + M P/T.

각 Cartesian component에서 (p_A,p_B)->(q,k)의 determinant는 1이므로 6차원 momentum volume도 보존된다. 직접 전개하면

  p_A^2/2 + p_B^2/2 + Q^2/(2M)
    = P^2/(2T) + k^2/(2mu) + q^2/(2nu).

따라서 internal available energy는 epsilon=nu E0-B이다. 원전의 COM E에 해당하는 것은 epsilon이며 lab E0가 아니다.

epsilon<0이면 support가 비고, epsilon=0이면 세 입자가 공통속도 P/T를 갖는 한 점으로 collapse하며 6D shell measure는 0이다. epsilon>0의 전체 support는

  k=sqrt(2mu epsilon) u, q=sqrt(2nu epsilon) v,
  |u|^2+|v|^2=1

로 매개화된다. 즉 S^5가 전체 label-preserving shell을 덮는다. Lab threshold는 E0=B/nu이다. B=mu/2이면 threshold=M(M+2)/(2(M+1)^2); 이는 이상적인 비상대론적 Coulomb H1s에서만 성립하는 자체 유도 결과이다.

Electron swap은 (p_A,p_B,Q)->(p_B,p_A,Q)이며 에너지와 measure를 보존한다. Jacobi coordinates의 모양은 달라지지만 원래 momentum 사상으로 직접 구현하면 convention 혼동이 없다.

## 4. 한 electron을 고정한 conditional sphere

고정 p_A에 대해 r=P-p_A, alpha=(M+1)/M,

  H=E0-B-p_A^2/2-r^2/[2(M+1)],
  c=r/(M+1), rho^2=2H/alpha

를 정의하면

  F=H-(alpha/2)|p_B-c|^2.

H<0은 empty, H=0은 p_B=c 한 점으로 collapse하고 conditional measure가 0이다. H>0이면 outgoing p_B support는 center c, radius rho의 2-sphere이다. 이는 recoil를 무시한 원점 중심 sphere와 일반적으로 다르다.

Translation 후 radial delta를 적분하면 정확히

  V_B(p_A)=integral d^3p_B delta(F)=4pi rho/alpha.

이 regular coordinate는 lab radial chart의 fold에서 numerical alternative로 사용할 수 있다.

## 5. Lab radial roots와 Jacobian

p_B=p n_B, |n_B|=1, p>0인 detector ray를 택한다. s=r.n_B, beta=s/M,

  gamma=p_A^2/2 + r^2/(2M) - (E0-B)

이면 shell equation은 alpha p^2/2 - beta p + gamma=0이다. D=beta^2-2alpha gamma로 두 대수적 근을 표현한다:

  p_plus=(beta+sqrt(D))/alpha,
  p_minus=(beta-sqrt(D))/alpha.

실수 근 중 p>0만 outgoing interior branch에 포함하고 p=0은 별도 endpoint로 기록한다. 분류:

- D<0: radial support 없음.
- D>0, gamma<0: 정확히 하나의 positive root.
- D>0, gamma>0: beta>0이면 두 positive roots, beta<0이면 없음.
- D>0, gamma=0: zero endpoint와 2beta/alpha; 후자는 beta>0일 때만 positive.
- D=0: beta>0이면 positive double root인 fold; beta=0이면 zero endpoint; beta<0이면 positive support 없음.

Simple root에서 |dF/dp|=|alpha p-beta|=sqrt(D). d^3p_B=p^2 dp dOmega_B 및 d^3p_A=p_A dE_A dOmega_A이므로

  dLambda/(dE_A dOmega_A dOmega_B)
    = p_A sum_positive_roots p_j^2/sqrt(D).

Weighted integrand W(p_A,p_B,Q)가 주어지면 각 branch의 값을 따로 곱해 합산한다. 두 근을 하나의 energy label로 합치거나 한 branch를 자동으로 버리지 않는다. 이 식은 에너지 delta의 Jacobian이며 source-defined TDCS prefactor를 대신하지 않는다.

## 6. Fold와 정확한 구성 예

M=1, B=1/2, E0=1, p_A=P/4라는 합성 stress fixture를 택한다. 이는 proton 질량에 대한 관측값이 아니다. 이때 alpha=2, gamma=1/8, beta=(3sqrt(2)/4)cos(theta_B),

  D=(9/8)cos(theta_B)^2-1/2.

Forward cone cos(theta_B)>2/3 안에는 두 positive roots가 있다. theta_c=arccos(2/3)에서 두 근이 p*=sqrt(2)/4로 합쳐진다. theta=0의 근은 (3sqrt(2) +- sqrt(10))/8이다. theta_c보다 큰 forward angle에는 radial support가 없다.

원점이 sphere 밖인 일반 fold에서 c0=|c|>rho, t=n_B.c/c0, t_c=sqrt(1-rho^2/c0^2)>0로 쓰면 p_+-=c0 t +- h, h=sqrt(rho^2-c0^2+c0^2 t^2)이다. D=alpha^2 h^2이므로 radial weight는 h^-1로 발산하지만

  dt = h/[c0 sqrt(h^2+c0^2-rho^2)] dh

를 적용한 branch-summed angular integral은

  2pi integral_0^rho (p_plus^2+p_minus^2)
       /[alpha c0 sqrt(h^2+c0^2-rho^2)] dh
    = 4pi rho/alpha

가 된다. 적분구간 h의 upper endpoint는 t=1에서 h=rho이다. Fold는 이 chart의 projection singularity이고 underlying sphere는 regular하다. 여기서 amplitude가 fold에 추가 singularity를 갖지 않는다는 조건 없이 일반 weighted integral의 유한성을 주장하지 않는다.

## 7. 전체 phase-space volume과 양의 fixture

3절의 6D rescaling Jacobian은 8(mu nu)^(3/2)이다. Unit S^5 area는 pi^3이고 integral r^5 dr delta(epsilon-r^2)=epsilon^2/2이다. 따라서

  Phi(E0,B,M)=4pi^3 (mu nu)^(3/2) epsilon^2
             =4pi^3 [M/(M+2)]^(3/2) (nu E0-B)^2

for epsilon>0, otherwise 0. 독립적인 1D 적분형은

  Phi=16pi^2 mu sqrt(2mu) integral_0^sqrt(2nu epsilon)
                    q^2 sqrt(epsilon-q^2/(2nu)) dq.

u=q^2/(2nu epsilon)의 정규화 density는 (8/pi)sqrt(u(1-u)), 0<u<1이다. 이는 W=1인 kinematic fixture에서만 Beta(3/2,3/2) law이다.

S^5의 deterministic 76-node positive quadrature를 moment fixture로 쓴다. 12 axis nodes +-e_i 각각 weight 1/48, 64 hypercube nodes (signs)/sqrt(6) 각각 weight 3/256이다. 총 weight 1, second moments delta_ij/6, fourth moments (delta_ij delta_kl + delta_ik delta_jl + delta_il delta_jk)/48이며 모든 odd moments가 0이다. 따라서 degree<=4 polynomial에 대해 sphere average와 일치한다. 전 구면에서 임의 amplitude를 적분하는 cubature의 정확성을 주장하지 않는다.

## 8. 상수 가중치 fixture의 정확한 lab moments

이 절의 average는 dLambda/Phi 및 W=1에 대한 것이다. 물리적 cross-section-weighted recoil law와 구별한다. S^5 symmetry에서 <k>=<q>=0, <k^2>=mu epsilon, <q^2>=nu epsilon이다. 그러므로

  <p_A>=<p_B>=P/T, <Q>=M P/T,
  <E_A>=<E_B>=P^2/(2T^2)+(M+1)epsilon/(2T),
  <E_R>=M P^2/(2T^2)+epsilon/T,
  2<E_A>+<E_R>=E0-B.

Q=a+Z, a=M P/T, L L^T=c_* I, c_*=4M epsilon/T, Z=L(u,v)로 놓으면 <Z^2>=c_*/2, <(Z^2)^2>=5 c_*^2/16, <(a.Z)^2>=a^2 c_*/6이다. 따라서

  Var(E_R)=2 M P^2 epsilon/(3T^3)+epsilon^2/(4T^2).

76-node rule은 이 mean/variance를 독립적으로 검사할 수 있다. Constant W는 검산 fixture로 명시되며 H ionization dynamics로 선택하지 않는다.

## 9. Infinite-mass 한계와 적용 위치

고정 B와 E0>B에서 M->infinity이면 mu,nu,alpha->1, beta->0, gamma->E_A-(E0-B), epsilon->E0-B이다. Interior allowed EA에서 하나의 positive p_B=sqrt(2(E0-B-E_A))를 얻고 radial weight는 p_A p_B가 된다. Phi->4pi^3(E0-B)^2이고 <E_R>, Var(E_R)->0이다. Recoil momentum Q가 0으로 수렴한다는 뜻은 아니다.

고정 B volume ratio는

  Phi_M/Phi_inf=[M/(M+2)]^(3/2)
          [(nu E0-B)/(E0-B)]^2

이다. Threshold 근처 및 D=0 근처에는 이 점별 한계를 uniform error certificate로 쓰지 않는다. 이미 검증된 PWBE/TDCS413의 fixed-center dynamics에 finite-M shell만 꽂아 source-consistent finite-M amplitude라고 부르지 않는다.

전체 label domain에서 symmetric W를 사용할 때 unordered event integral은 정확히 1/2 labelled integral이다(중복의 measure-zero diagonal 제외). Energy-order half-domain으로 제한했다면 추가 1/2를 넣지 않는다. 특정 detector A/B value에도 자동 2 또는 1/2를 넣지 않는다. Spin trace 및 exchange interference는 기존 HE-ANG-CONTRACT/PR97의 논리를 참조하되 실제 amplitude convention을 동반해야 한다.

## 10. 구현 계약과 판별 검증

Primary binary64 solver는 cancellation-avoiding quadratic roots를 사용한다: h=beta+copysign(sqrt(D),beta), roots h/alpha and 2gamma/h. Positive roots를 정렬하되 임의 merge/cutoff를 두지 않는다. D의 raw value와 scale을 보존한다. |D| <= 64 eps_machine (beta^2+|2alpha gamma|)이면 NEAR_CAUSTIC_UNRESOLVED로 돌려 실수해 부재나 finite weight를 단정하지 않는다. Exact synthetic coefficient tests와 80-digit independent reference는 그 제한을 판별한다. D=0을 rounding-tolerance로 만들어 regularization하지 않는다.

Directions는 finite nonzero vectors만 허용하고 명시적인 normalization helper를 거친다. API 결과에 입력 norm과 normalization 여부를 기록한다. 무효 M/B/E0, nonfinite, 잘못된 vector dimension을 거부한다. 숫자 fallback으로 physical scope를 바꾸지 않는다.

판별 항목: Jacobi energy/momentum/determinant; swap symmetry; complete roots including two positive and zero/negative/complex branches; sphere vs radial identity; exact folded cone angular integral; full volume independent 1D quadrature; 76-node moments through degree4; finite-M fixtures at nominal20/54.4/413.6eV; fixed-B and reduced-mass-binding modes separated; infinite-M trend; binary64 vs80digits. Plot은 저장한 결과만 읽어 two-root fold 및 finite-mass volume ratio를 표시한다. 이전 완료 suite는 실행하지 않는다.

## 11. Claim gate 및 다음 의무

완료 후 허용: finite-M kinematic support/branches/coarea mapping, exact constant-weight phase-space formulas, tested implementation under frozen assumptions. 다음 입력: source-consistent joint amplitude 또는 numerical event payload의 flux/Fourier normalization, spin/exchange, count, support, lab/COM convention, finite-M consistency 및 uncertainty/validity. 이 입력과 새 shell이 결합되어야 physical weighted recoil distribution 및 full event sigma를 평가할 수 있다.

DDCS20 marginal 결과를 event law로 확대하지 않는다. HE-X1 empirical angular correction, physical provider admission, integration activation, merge는 false이다. C9-NB-01 future partial mu-window metadata 의무, 중앙 C23E, 다른 owner의 scoped results와 OPEN, 모든 역사적 비용/실패/unknown을 유지한다. 새로운 strong no-go 주장은 없다.
