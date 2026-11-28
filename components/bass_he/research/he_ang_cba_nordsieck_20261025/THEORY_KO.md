# HE-ANG-CBA-NORDSIECK: Coulomb–1s overlap와 direct Born 정규화

## 결과, 적용 모형과 단위

이 단위는 고정핵, 비상대론적 직접 Coulomb–Born 근사에서 수소 1s의 연속상태 전이 form factor를 구성한다. 원전의 Coulomb 적분을 독립적으로 유도하고 감쇠상수 미분으로 올바른 1s overlap을 얻는다. 같은 Coulomb 전하에서는 직교성을 드러내는 소거 없는 식으로 계산한다. Delta-normalized 전자 상태에서 직접 채널 TDCS의 절대 계수를 유도한다. 이는 새 구현의 수학적 모형이며, HE-ANG physical provider의 채택은 별도 source validity·exchange·count·finite-mass 의무를 갖는다.

물리 척도는 a0=4*pi*epsilon0*hbar^2/(m_e*e^2), p0=hbar/a0, E_h=hbar^2/(m_e*a0^2)다. 아래 r,p,lambda,E는 각각 r_phys/a0, p_phys/p0, lambda_phys*a0, E_phys/E_h이다. 이 명시적 변수변환 안에서 m_e=hbar=e^2/(4*pi*epsilon0)=1을 사용한다. TDCS의 물리 단위는 a0^2/E_h이다. 온도·곡률·상대론 보정은 모형에 없다. 비상대론적 적용 조건은 운동에너지가 m_e*c^2보다 충분히 작다는 조건을 포함한다. 그림의 eV 변환 U=27.2 eV/E_h는 기존 nominal 입력이며 정밀 Hartree 상수를 주장하지 않는다.

수학 적분에서 lambda>0, p=|pvec|>0, eta>=0, qvec는 실수 3벡터이다. lambda와 eta는 독립 입력이다. 물리 수소 채널에서는 lambda=1, eta=1/p, binding B=1/2를 적용한다. 표적핵은 정지한 무한질량 중심이고 projectile은 입·출사 평면파, 방출전자는 attractive Coulomb 연속파다. 전자교환·postcollision projectile distortion은 이 직접 근사에 포함하지 않는다.

## R1–R3: 근거와 정의

기준은 PR99 D=bec636ffa3014035292c1078a758c7aa1827174d, 중앙 E=9600a605f6380bc2262d0cfce5ff00290e594a5a다. AGENTS 두 blob과 실제 backup metadata를 확인했다. PR94–99, HE-X1/HE-ANG-CONTRACT/HE38/Hex/D10의 완료 결과·비용·실패·unknown을 재사용한다. PR99 finite-M shell과 이번 fixed-centre amplitude를 곱하는 source-consistency 주장은 하지 않는다.

1차 근거는 Attaourti–Taj–Manaut, arXiv:physics/0411013v2, 관련 DOI10.1103/PhysRevA.71.062705다. 실제 author PDF SHA256 b14f054de037722bb21ab8911b0b3917f0978b18dab9c916427d02115ccceda1, 326595 bytes. Eq19/A9가 아래 I를 제공한다. Eqs13–17의 bra는 Gamma(1-i*eta), M(i*eta;1;i[p*r+pvec.rvec]), exp(-i*pvec.rvec)이다. Eq16의 bound-state integral에는 별도의 1/r가 없고 Eq18에는 문자 그대로 추가되어 있다. 여기서는 Eq16의 정의에서 출발한다. 출판본과의 등가성·erratum은 확인하지 않았다. 원전의 Eq28 J는 다른 hypergeometric integral이므로 아래 overlap은 K로 부른다.

Eq19의 실제 reference16은 Massey–Mohr, Proc.Roy.Soc.A140,613(1933)이다. Nordsieck1954 DOI10.1103/PhysRev.93.785는 관련 integral 계보의 서지 자료이며 이번 식의 직접 인용원으로 삼지 않는다. 원전 appendix의 Q 부호 중간식에는 불일치가 있어 아래 q convention으로 유도한다. 연구 단위 이름 Nordsieck은 integral 계열의 관용적 표지이며 새 적분 정리나 최초성 주장이 아니다.

M(a;b;z)={}_1F_1(a;b;z), A=q^2+lambda^2, Bc=A+2*qvec.pvec-2*i*lambda*p로 둔다. binding B와 혼동하지 않도록 본문에서는 복소 분모를 Bc라 부른다.

I(lambda,qvec,pvec;eta)=integral d^3r exp(-lambda*r+i*qvec.rvec) M(i*eta;1;i[p*r+pvec.rvec])/r.

K(lambda,qvec,pvec;eta)=integral d^3r exp(-lambda*r+i*qvec.rvec) M(i*eta;1;i[p*r+pvec.rvec]).

## R4–R5: parabolic 적분과 미분

pvec 방향을 z로 잡고 xi=r+z, zeta=r-z, rho=sqrt(xi*zeta)를 쓴다. xi,zeta>=0이고 d^3r/r=(1/2)d xi d zeta d phi다. qz=qvec.pvec/p, qperp^2=q^2-qz^2, a=(lambda-i*qz)/2, b=(lambda+i*qz)/2, d=qperp^2/4로 놓으면 azimuth 적분 뒤

I=pi integral_0^infty dxi dzeta exp(-a*xi-b*zeta) J0(qperp*sqrt(xi*zeta)) M(i*eta;1;i*p*xi).

Re(b)>0에서 zeta 적분은 b^-1 exp(-d*xi/b)이고 s=a+d/b=A/[2*(lambda+i*qz)]이다. Re(s)>0, Re(s-i*p)>0다. Laplace 적분을 적용하면

integral_0^infty exp(-s*xi) M(i*eta;1;i*p*xi) dxi = s^-1 (1-i*p/s)^(-i*eta).

급수 합으로 성립하는 영역에서 유도한 뒤 Re(s)>0 영역으로 해석적 연속한다. 1-i*p/s=Bc/A이고 pi/(b*s)=4*pi/A다. 실제 q,lambda,p에서는 Im(Bc)=-2*lambda*p<0이므로 주값 Log(Bc)의 Arg는 (-pi,0)에 있고 가지절단을 지나지 않는다. 따라서

C=exp(i*eta*(log(A)-Log(Bc))),  I=4*pi*C/A.                         (1)

이 branch를 전역 구현 규칙으로 고정한다. |C|^2=exp(2*eta*Arg(Bc))다. 임의 principal power의 곱 법칙에 의존하지 않는다.

lambda>=lambda_min>0의 compact 구간에서 hypergeometric 함수의 positive-imaginary-ray asymptotic은 다항 차수의 envelope를 갖고 exp(-lambda_min*r)가 r의 유한차수 인자와 함께 적분가능하다. 이에 따라 적분 아래 lambda 미분이 가능하다. **미분할 때 eta,pvec,qvec는 고정한다.**

K=-partial_lambda I = 2*I*[(1-i*eta)*lambda/A+i*eta*(lambda-i*p)/Bc].  (2)

eta=lambda/p 대입 후 전체 미분을 취하면 eta의 부당한 미분항이 추가된다. 같은 Coulomb 문제는 (2)를 얻은 뒤 대입한다.

### 직교성과 소거 없는 matched 식

qvec=-pvec이면 A0=p^2+lambda^2, Bc0=(lambda-i*p)^2이며

K(lambda,-pvec,pvec;eta)=2*I0*(lambda-eta*p)/A0.                    (3)

따라서 bound 지수 lambda와 continuum 전하 eta*p가 같은 경우 nuclear overlap은 정확히 0이다. 이는 동일한 Coulomb 해밀토니언 bound–continuum 직교성의 적분 표현이다. eta=0이면 독립적으로

I=4*pi/A, K=8*pi*lambda/A^2.                                    (4)

이 plane-wave control에서는 K(-pvec)가 0이 아니므로 projectile–nucleus subtraction을 유지한다.

Delta=qvec+pvec로 두고 eta=lambda/p를 (2)에 대입한다. 공통분모의 numerator는

N=(1-i*eta)*lambda*Bc+i*eta*(lambda-i*p)*A
 =2*lambda*[Delta^2-(1+i*eta)*Delta.pvec].

따라서 matched 계산의 주식은

K_match=16*pi*lambda*C*[Delta^2-(1+i*eta)*Delta.pvec]/(A^2*Bc),     (5)
A=|Delta-pvec|^2+lambda^2, Bc=Delta^2+(lambda-i*p)^2.

Delta=0에서 (5)는 정확히 0을 반환한다. 작은 Delta에서 (2)의 두 큰 항을 빼는 방식에 비해 소거를 피한다. Delta=t*n, |n|=1이면 일반 방향 K=O(t), n.pvec=0이면 K=O(t^2)다. 상수항과 slope는 (5)에서 직접 얻는다. 실제 양의 ionization energy transfer가 있는 운동학에서는 Delta=0이 도달 가능한 입출사 사건이 아니다. 이 작은 t 검사는 kernel conditioning fixture이다.

### 독립 수치 적분 식

원래 K의 volume element에 r=(xi+zeta)/2를 삽입하고 zeta Laplace 적분을 수행하면

K=pi/(2*b) integral_0^infty exp(-s*xi) M(i*eta;1;i*p*xi)
       *[xi+1/b-d*xi/b^2] dxi.                                (6)

여기서 integral zeta exp(-b*zeta) J0(...) dzeta
 =exp(-d*xi/b)*(b^-2-d*xi*b^-3)를 썼다. (6)은 (1)의 수치 미분이 아닌 원적분의 별도 1차원 quadrature이다. 유한한 moderate oscillation 입력4개에서50자리 quadrature로 (2)/(5)를 확인한다. 전체 정의역의 수치오차 상한 주장은 없다.

## Delta-normalization, 직접 Born amplitude와 TDCS

bound 상태 phi_1s=(lambda^3/pi)^(1/2) exp(-lambda*r), continuum bra의 delta-normalized prefactor는

Nc(eta)=(2*pi)^(-3/2) exp(pi*eta/2) Gamma(1-i*eta).

F_D(Delta,pvec)=Nc(eta)*(lambda^3/pi)^(1/2)
              *[K(lambda,Delta-pvec,pvec;eta)-K(lambda,-pvec,pvec;eta)]. (7)

수소 matched 채널은 lambda=1,eta=1/p이고 두 번째 항은 (3)에 의해 0이다. plane-wave direct control은 lambda=1,eta=0이며 두 항을 모두 유지한다. logGamma를 사용한 complex Nc와 아래 양성 정규화의 일치를 검증한다.

S(eta)=exp(pi*eta)|Gamma(1-i*eta)|^2=2*pi*eta/(1-exp(-2*pi*eta)),
S(0)=1, |Nc|^2=S/(2*pi)^3.                                    (8)

작은 eta에는 expm1을 사용하고 eta=0은 연속 극한으로 처리한다. 큰 eta 전역 accuracy나 underflow-free 관측 범위는 이번 유한 검증에서 주장하지 않는다.

단위 volume V의 projectile 입·출사 평면파와 방출전자 연속파를 쓰면 direct interaction V_d=1/r12-1/r1의 projectile 적분은 4*pi*(exp(i*Delta.r)-1)/Delta^2이다. Box matrix element는

T_box=V^(-3/2)*(4*pi/Delta^2)*(lambda^3/pi)^(1/2)
       *exp(pi*eta/2)*Gamma(1-i*eta)*K_difference.

황금률 2*pi*|T_box|^2 delta(Ef+EB+B-Ei), 두 final state density V^2/(2*pi)^6, incident flux pi_momentum/V를 결합하면 V가 소거된다. d^3pf=pf*dEf*dOmega_f, d^3p=p*dEB*dOmega_B이고 Ef delta를 적분하므로

d^3sigma_direct/(dEB dOmega_B dOmega_f)
 =4*(pf*p/pi_momentum)*|F_D|^2/Delta^4
 =(pf*p/pi_momentum)*|f_D|^2,   f_D=2*F_D/Delta^2.               (9)

여기서 pi_momentum=|p_i|이며 원주율 pi와 구분한다. 동등한 delta-state T는 T_delta=(4*pi/Delta^2)/(2*pi)^3*F_D이고 (2*pi)^4*(pf*p/pi_momentum)*|T_delta|^2가 (9)다. spin-diagonal direct 채널의 incident/target spin 평균1/4와 final 합4는1이다. Identical-electron exchange amplitude 및 event count factor는 이 labelled direct 결과를 자동 승격하지 않고 별도 구성한다.

수소 운동학 E_i>B+E_B> B, p_i=sqrt(2E_i), p=sqrt(2E_B), p_f=sqrt(2[E_i-B-E_B]), Delta=p_i*n_i-p_f*n_f를 사용한다. E_B>0, E_f>0를 요구하고 zero transfer·threshold endpoint는 이 API에서 거절한다. 출력은 a0^2/E_h 단위이며 eV당 값은 U로 나눈다. F_phys=p0^(-3/2)*F_dimensionless이다. source Eq27의 spinor/c 계수를 그대로 대입하지 않고 위 정규화를 직접 유도했다.

## 판별 계획과 claim boundary

R6은 독립 Astra의 (1)–(9), source correspondence, branch, differentiation order, flux/count·단위 검토다. R7은 한 번의 Wolfram algebra 확인이다. 새 local science는 targeted tests, mp50/80 및 독립 quadrature 분석, 저장 결과의 그림3 children으로 한정한다. 예상 핵심 판별은 generic K와 stable K의 일치, (3)/(4), 작은 transfer conditioning, (6), normalized form factor와 (8)/(9)이다.

250 eV incident,5 eV ejected,3degree scattered는 읽은 preprint가 사용하는 asymmetric geometry의 illustrative calculation이다. Oriented coplanar angle -180..180degree step5의73개 direct CBA/plane-wave 값을 계산하며 적분·data fit·benchmark 성공률로 해석하지 않는다. 20/54.4/413.6eV의 기존 marginal/relative data는 재계산·재적합하지 않는다.

새 단위의 완료는 이 analytic fixed-centre direct model의 명시적 식·구현·유한 검증·전달까지다. 전체 HE-ANG은 SOURCE_INPUT_PENDING, physical_provider_admitted=false다. 다음 입력은 calibrated source-consistent joint amplitude/event law, spin/exchange/count, full-support applicability, finite-M frame/recoil 및 uncertainty다. C9-NB-01 미래 partial mu_window theta metadata, C23E와 다른 owner의 scoped/OPEN 상태를 유지한다. NG1–NG7을 적용할 새 strong no-go 또는 문헌 최초성 주장은 없다.
