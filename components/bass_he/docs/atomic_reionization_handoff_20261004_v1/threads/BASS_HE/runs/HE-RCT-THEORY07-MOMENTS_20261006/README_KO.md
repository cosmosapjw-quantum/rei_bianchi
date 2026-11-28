# HE-RCT-THEORY07: 미확정 photon/heat 모멘트의 식별 한계와 허용범위

판정: CONDITIONAL_THEORY_AND_FINITE_CHECKS_PASS__SPECTRAL_VALUES_OPEN. 이 단위는 이론 연구이며 소비기 빌드/복구/채택 검사의 확장이 아니다. 실제 source의 photon/heat/recoil/spectrum 값은 아직 null이다.

## 원전과 현재 계약

West, Lane & Cohen, PRA26,3164–3169(1982), DOI10.1103/PhysRevA.26.3164의 원문 PDF2–4쪽을 읽었다. 3166쪽은 optical-potential loss 방법이 emission spectrum을 결정하지 않고 total transfer cross section을 얻는다고 명시한다. 원전 Eq3/6/12와 아래 직접 유도를 구분한다. PDF는 재배포하지 않는다.

현재 KF96 adapter는 dk/dT=0을 CONSTANT_PRESCRIPTION_ONLY_NOT_PHYSICAL_SLOPE로 명시한다. native closed_events의 Ebar는 caller-supplied이며 physical_closure_admission=false다. 따라서 below constant-rate 예시를 KF96 실제 원자모멘트로 승격하지 않는다.

## 새 유도

공통T Maxwellian,zero drift,fixed initial/final states,단일 spontaneous photon,T-independent nonnegative sigma0(E),필요한 적분가능성을 전제한다. E=mu*v_rel^2/2,beta=1/(kB*T),epsilon=hbar*omega는 pair COM photon energy다. NR Maxwell 평균과 exact relativistic endpoint의 역할을 구분하고 fluid frame thermal boost는 별도다.

S(E,epsilon)=d sigma/d epsilon, sigma_m(E)=integral epsilon^m S d epsilon,
k_m^gamma=C beta^(3/2) integral E sigma_m(E) exp(-beta E)dE,
C=sqrt(8/(pi*mu)), k=k_0^gamma, mean_epsilon=k_1^gamma/k.

Z=integral E sigma0 exp(-beta E)dE와 반응조건부 P(E)=E sigma0 exp(-beta E)/Z에서

    mean_E = kB*T*(3/2 + d ln k/d ln T).
    b=3/2+D ln k, D=T*d/dT.
    mean_E2=(kB*T)^2*(b^2+b+D b).
    Var(E)=(kB*T)^2*(b+D b).

이는 입사 상대운동에너지의 모멘트이며 photon mean이 아니다. 일반 incoming moment rate에는 k_(m+1)^in=kB*T*((3/2)k_m^in+T*d k_m^in/dT)가 성립한다. b>=0,b+Db>=0은 이 sigma 가정의 필요조건이다. constant sigma는 mean_E=2kBT이며, 정확한 constant k에만 mean_E=1.5kBT다. nominal fit의 미분을 실제 slope라고 가정하지 않는다.

에너지보존 Q+E=epsilon+Kproducts, Kproducts>=0에서

    0<=mean_epsilon<=Q+mean_E,
    -mean_E<=mean_qkin=Q-mean_epsilon<=Q,
    mean_epsilon2<=Q^2+2Q*mean_E+mean_E2.

Kproducts에는 pair recoil이 포함된다. chemical=-QR,matter=(Q-mean_epsilon)R,emitted=mean_epsilon*R을 유지하며 recoil을 다시 빼면 잘못된 잔차가 생긴다. matter kinetic을 heat로 읽으려면 국소 열화와 bulk-work 분리 가정이 필요하다. 재흡수는 별도다. 이 상한은 사건평균이며 Maxwell tail의 모든 photon을 잘라내는 cutoff가 아니다.

Exact COM kinematics에서는 C_f=M_f*c^2, S=Q+E, g(S)=S*(2C_f+S)/(2(C_f+S))가 photon endpoint다. g''=-C_f^2/(C_f+S)^3<0이므로 mean_epsilon<=mean_g<=g(Q+mean_E). E를 NR Maxwell 변수로 평균한 예시는 그 근사 수준을 넘어선 SR 인증이 아니다.

## 동일한 모든 총반응률로도 가열 부호는 정해지지 않는다

S_a(E,epsilon)=sigma0(E)*delta(epsilon-a*g(Q+E)),0<a<1은 모든 a에서 같은 sigma0와 모든 T의 k(T)를 갖지만 서로 다른 photon mean을 준다. 좁은 smooth 양의 분포로도 근사할 수 있다. 이는 normalization/positivity/kinematics 반례이며 실제 He dipole spectrum 계산이 아니다.

정확한 constant-rate surrogate(sigma proportional1/v), T50000K,Q token40.819325400298eV와 설명용 C_f=5e9eV에서:

| a | photon mean eV | mean matter heating eV/event |
|---:|---:|---:|
| .50 |23.64116256028018|+17.17816284001782|
| .95 |44.91820886453235|-4.09888346423435|

따라서 total sigma를 완전히 복원해도 광자평균/가열부호가 유일하게 결정되지 않는다. optical loss에 A(R)*DeltaE(R)를 붙여 정확한 first moment라고 부르려면 별도 spectral/local-emission 근사 유도와 오차가 필요하다.

## rate 미분 없이 쓰는 경계

동일 실제 sigma의 T+>T에서 a=1/(kBT)-1/(kBT+)이면

    mean_E<=ln[(T+/T)^(3/2)*k(T+)/k(T)]/a.

T-<T,b=1/(kBT-)-1/(kBT)에서 mean_E>=max(0,-ln[(T-/T)^(3/2)*k(T-)/k(T)]/b). 이는 exponential moment와 Jensen으로 얻는다. 실제 enclosures k(T)>=L0>0,k(T±)<=U±가 있다면 ratio의 k(T±)/k(T)를 U±/L0로 바꾼 보수적 경계가 된다. 서로 다른 KF96/GM25를 한 함수의 표본으로 혼합하지 않는다. 현재 source uncertainty는 null이므로 이 actual physical bound의 숫자 승인은 없다.

회전불변·무 drift ensemble에서는 평균 photon momentum0, covariance=delta_ij*mean_epsilon_fluid2/(3c^2)다. 대칭이 tensor 형태를 정해도 scalar moment는 미정이다. 정의된 event moment와 kinetic stress tensor의 위상공간 가중치를 혼동하지 않는다.

## 계산과 종료 지점

새 python -B -W error research/verify_moments.py는 exit0. SymPy12identities,4synthetic kernels x3temperatures=12cases를60/85dps에서 direct quadrature와 rate-derivative로 대조했다. 고정밀 최대 상대잔차2.17e-45,동일-rate 반대부호2counterexamples와3invalid inputs를 확인했다. 소수값은 illustrative rounding이며 outward interval certificate가 아니다. Tests-after 이론검산이며 RED/GREEN이나 independent scientific review가 아니다. native/history/actual atomic sigma/consumer mutation0이다.

원자 평균값을 닫으려면 same-channel k_1^gamma(T) 또는 sigma_1(E)가 필요하다. recoil에는 k_2^gamma, 그룹 source에는 spectral/group integrals,종별 partition에는 최종운동량 상관이 필요하다. 다음 이론 노드 HE-RCT-THEORY08_SPECTRAL_FIRST_MOMENT_OPERATOR는 initial/final continuum Hamiltonian과 dipole에서 first-moment operator를 정식화한다. 수치 potential/dipole가 없으면 형식 유도와 actual evaluation을 분리한다.

원 source moments null,baselineRCTOFF,HE-F2globalfalse,HE-F3/F09blocked,physicalHOLD를 유지한다. 기존 addon의 owner 채택에는 새 과학선행조건을 추가하지 않는다. Git은 이 리뷰/계약/입력/실행 identity를, immutable ZIP은 전체 유도와 실행 verifier/개별 결과를 보존한다. archive/cloud identity는 DELIVERY_RECEIPT.json을 따른다.
