# HE-ANG-FINITEMASS-CBA: finite-mass Jacobi direct Coulomb–Born model

## 1. 결과와 근거 상태

이 단위는 PR99의 finite-M shell과 PR100의 Coulomb overlap을 공통 Jacobi Hamiltonian으로 연결한다. 새 결과는 두 recoil Fourier phase, reduced-mass bound/continuum, invariant cross-section weight, Jacobi와 lab detector density, amplitude-weighted two-root fold 적분의 연결이다. 이는 아래에 명시한 labelled direct C1 Born channel model에서의 유도이며 전체 HE-ANG physical provider의 validity/exchange/uncertainty 채택은 별도 열린 의무다.

Literature-supported: Kadyrov–Bray–Mukhamedzhanov–Stelbovics, Ann.Phys.324(2009)1516–1546, DOI10.1016/j.aop.2009.02.003, §3.1 pp1527–28 Eqs72–84의 arbitrary-mass Jacobi Hamiltonian과 channel coordinates. 실제 원전 PDF448174bytes SHA256c7627a718193fc1ab0181d1c7fbabdc334bcf53a28e3a0870c45cd9827da9165를 재취득했고 pp1527–28 이미지를 읽었다. 해당 원전의 exact scattering theory가 아래 C1 closure를 물리적으로 승인했다는 뜻은 아니다.
Reused derived/checked: PR99 Dbec636ffa3014035292c1078a758c7aa1827174d의 shell.py와 THEORY_KO.md; PR100 D8e0fb28fea520364d8794bac32840621dd150f95의 cba.py와 THEORY_KO.md. 모든 기존 실행·실패·unknown은 그대로 보존한다.
Literature-supported/source correspondence: Attaourti–Taj–Manaut, physics/0411013v2, related DOI10.1103/PhysRevA.71.062705. 실제 PDF326595bytes SHA256b14f054de037722bb21ab8911b0b3917f0978b18dab9c916427d02115ccceda1. Fixed-centre source의 Coulomb convention은 PR100에서 유도·검토한 K를 재사용한다. 그 Eq16/18의1/r 차이, Eq28 J 구별, reference16=Massey–Mohr1933, appendix sign 기록도 유지한다.
Derived here: 아래 finite-M channel 구성과 계수. Numerically checked/implementation-verified의 범위는 실행 뒤 RESULTS_KO와 원장에 별도로 기록한다.

## 2. 단위, 좌표와 정확한 kinetic separation

g=e²/(4*pi*epsilon0), a0=hbar²/(m_e*g), p0=hbar/a0, E_h=hbar²/(m_e*a0²).
Nucleus physical mass는 M*m_e이고 M>0이다. 이하 좌표는 a0, 운동량은 p0, 에너지는 E_h로 나눈 무차원 변수다. 이 명시적 변환을 통해 내부식에서 hbar=m_e=g=1을 사용한다. TDCS physical unit는 a0²/E_h, invariant weight W의 단위는 a0²*E_h/p0^6, conditional slice는 a0²/p0^3다. 비상대론 근사 E << m_e*c², Galilean mass addition을 사용하며 binding mass defect와 radiation을 포함하지 않는다.

x_A는 projectile electron, x_B는 target electron, x_N는 nucleus다.
T=M+2, a=mu=M/(M+1), b=1/(M+1), nu=(M+1)/(M+2), a+b=1.
X=(x_A+x_B+M*x_N)/T,
r=x_B-x_N,
R=x_A-(x_B+M*x_N)/(M+1).

역좌표:
x_A=X+nu*R,
x_B=X-R/T+a*r,
x_N=X-R/T-b*r.
Canonical momenta:
p_A=P/T+q,
p_B=P/T-b*q+k,
P_N=M*P/T-a*q-k.                                      (1)

각 Cartesian component에서 coordinate와 momentum 변환의 determinant는1이다. 따라서 d³p_A d³p_B=d³q d³k at fixed total P.
직접 전개하면
p_A²/2+p_B²/2+P_N²/(2M)=P²/(2T)+q²/(2nu)+k²/(2mu).      (2)

실제 단위의 internal Hamiltonian은
H_int,phys=-hbar²/(2m_e*nu) Laplacian_R
           -hbar²/(2m_e*mu) Laplacian_r
           -g/r +g/|R-a*r|-g/|R+b*r|.
차원 변수에 대한 Laplacian/거리로 읽는다. 무차원 channel 분해는
H0=qhat²/(2nu)+h_r,
h_r=khat²/(2mu)-1/r,
V=1/|R-a*r|-1/|R+b*r|.                                 (3)

이 h_r의1s는 phi=(mu³/pi)^(1/2)exp(-mu*r), binding B=mu/2다. 즉 lambda=mu이며 continuum Sommerfeld parameter eta=mu/k이다. 임의 fixed B=.5를 이 finite-M Coulomb state와 혼합하지 않는다.

## 3. Initial/final channel과 recoil phases

Target COM은 lab 정지, beam +z, incoming lab momentum P=(0,0,sqrt(2E0)). Incoming relative momentum qi=nu*P, incident relative speed vi=qi/nu=|P|. Internal excess energy는
epsilon=nu*E0-mu/2.                                    (4)
epsilon>0이며 0<Er<epsilon에서 k=sqrt(2mu*Er), q=sqrt(2nu*(epsilon-Er)).
여기서 Er는 (B,N) pair 상대운동 에너지이고 lab electron energy EB가 아니다. 상대 lab threshold는 E0>mu/(2nu).

Approximation/closure: initial projectile is plane wave in R, target is exact finite-mass Coulomb1s; final state is plane wave in R times the attractive (B,N) Coulomb continuum in r. V is treated once. Projectile final distortions, postcollision A-B correlation beyond this Born matrix, and antisymmetrization are not included. This fixes a specific C1 direct channel model, not a claim of exact three-body Coulomb asymptotics.

Let Delta=qi-q. By (1), Delta=P-p_A exactly.
Use exp(+i Delta.R) in the projectile integral. A screened Coulomb g*exp(-epsilon_s*u)/u gives 4*pi/(Delta²+epsilon_s²); shift R'=R-a*r and R''=R+b*r first. For nonzero Delta take epsilon_s->0:
integral d³R exp(i Delta.R) V
 =4*pi/Delta² [exp(i*a*Delta.r)-exp(-i*b*Delta.r)].       (5)

Both phases are required at finite mass. The second is not a constant1 and its continuum overlap is generally nonzero. In the infinite-M limit a->1,b->0,lambda->1; bound–continuum orthogonality then removes that term exactly as in PR100.

## 4. Reusing the Coulomb overlap without cancellation

Let L_lambda(s,kvec)=K(lambda,s-kvec,kvec;eta=lambda/k) be PR100's matched overlap:
A_s=|s-kvec|²+lambda²,
B_s=s²+(lambda-i*k)²,
C_s=exp(i*eta*[log(A_s)-Log(B_s)]),
L_lambda(s,kvec)=16*pi*lambda*C_s
 [s²-(1+i*eta)*s.kvec]/(A_s²*B_s).                      (6)

Im(B_s)=-2lambda*k<0 fixes the same principal log branch. L(0)=0 exactly. The eta-fixed differentiation used to derive K is reused unchanged; reduced-mass matching is substituted afterwards.

The finite-M overlap difference is
D_M=L_mu(a*Delta,kvec)-L_mu(-b*Delta,kvec).              (7)
It is evaluated using the two stable small-s overlaps, rather than generic subtraction of O(1) terms. For diagnostic derivations define G_s=C_s/(A_s² B_s); then
D_M=16*pi*mu {
 Delta²[a²G_a-b²G_-b]
 -(1+i*eta)(Delta.kvec)[aG_a+bG_-b]}.                    (8)

For Delta=t*n, the generic leading term has a+b=1; transverse leading coefficient has a²-b²=(M-1)/(M+1). At M=1 and Delta.kvec=0, G_a=G_-b and D_M=0 for all Delta. This exact synthetic symmetry case uses absolute error. Near cancellation zeros we do not claim a uniform relative error bound.

Nc=(2*pi)^(-3/2) exp(pi*eta/2)Gamma(1-i*eta),
F_M=Nc*sqrt(mu³/pi)*D_M.                                (9)

Reuse PR100 complex loggamma normalizer and stable matched overlap without changing their bytes. Full source-independent numerical check uses PR100's original-integral parabolic quadrature for the two shifted q values. It does not use the closed expression as its integrand.

## 5. Flux, delta-state amplitude and both detector measures

Projectile delta-state normalization yields
T_delta=(4*pi/Delta²)/(2*pi)^3 *F_M.
Golden rule and incoming relative flux give the invariant differential measure
d sigma_D=(2*pi)^4/vi *|T_delta|² d³q d³k delta(epsilon-q²/(2nu)-k²/(2mu))
         =W_M dLambda,
W_M=4*nu/qi *|F_M|²/Delta^4
   =4/|P| *|F_M|²/Delta^4.                              (10)

Here dLambda is exactly PR99's labelled shell measure, now weighted by the finite-M Hamiltonian-derived amplitude. The box-volume derivation gives the same result: T_box scales V^-3/2, two final state densities give V²/(2*pi)^6, flux vi/V cancels the remaining V. The direct spin-diagonal average1/4 and finalsum4 give factor1. No unordered1/2 or exchange interference is inserted.

In Jacobi variables d³k=mu*k dEr dOmega_k and after integrating q's energy delta d³q gives nu*q dOmega_q:
J_D=d³sigma_D/(dEr dOmega_k dOmega_q)
 =4*mu*nu²*(q*k/qi)*|F_M|²/Delta^4
 =mu*nu*q*k*W_M.                                      (11)

For lab p_A fixed and detector direction n_B, use unchanged PR99 solve_radial with B=mu/2. Its alpha=(M+1)/M, beta=(P-p_A).n_B/M, discriminant Droot, and all positive simple roots p_j give
L_D=d³sigma_D/(dEA dOmega_A dOmega_B)
 =p_A sum_j [p_j²/sqrt(Droot)] W_M(p_A,p_j*n_B).         (12)

The amplitude must be evaluated separately on each branch. If shell.py returns NEAR_CAUSTIC_UNRESOLVED the wrapper propagates it with density=None; it does not clip Droot or infer a finite weight. Empty support has density0. k=0 and the endpoint Er=0 are separate excluded continuum endpoints, with an explicit status if encountered in the lab wrapper. Delta0 is rejected for TDCS APIs. Model and chart metadata accompany outputs.

Equation(12) uses p_A>0. At p_A=0 the lab energy-angle chart has no defined A direction; lab_tdcs returns LAB_A_ZERO_ENDPOINT with density=None. The invariant weight itself remains defined at p_A=0 when its other interior conditions hold. This endpoint distinction is fixed before any numerical execution and is recorded in CONTRACT_ADDENDUM_01.json.

## 6. Amplitude-weighted fold bridge

For fixed p_A define r0=P-p_A=Delta, c=r0/(M+1), alpha=1/mu and radius rho>0 from PR99 conditional_sphere(E0,mu/2,M,p_A). Then k=p_B-c and
integral d³p_B delta(F) W_M =mu*rho integral dOmega_k W_M. (13)

The W in (10) depends only on |Delta|,rho,Delta.k and constants in this isotropic1s direct model. Align z with c. If c0=|c|>rho, the lab detector forward cone has two roots. Set h=sqrt(rho²-c0²+c0²*t²), t=cos(theta_B), p_±=c0*t±h:
I_slice=2*pi integral_0^rho
 [p_+²W_+ +p_-²W_-]/[alpha*c0*sqrt(h²+c0²-rho²)] dh
 =2*pi*mu*rho integral_-1^1 W(k=rho*n(u)) du.             (14)

The second form is regular on the pair sphere, and the first resolves the fold by h. They sample the same amplitude on different points/charts. For the finite-M model fixture M=1,E0=1,B=1/4,p_A=P/10,

For fixed M>0,rho>0 and |Delta|>0, every A_s>=mu² and |B_s|>=2*mu*rho. Nc(mu/rho) is finite and the principal-log branch is continuous. Therefore W_M is smooth and bounded on the compact pair sphere, which justifies both finite weighted integrals and the change of variables in(14). This argument does not include rho=0 continuum endpoints.
c0=9sqrt(2)/20, rho²=67/200, c0²-rho²=7/100>0.
Thus two positive lab roots exist within the cone. This synthetic mass fixture tests branch weighting. The slice is a model cross-section density per d³p_A (a0²/p0³), not a total event sigma or a calibrated physical recoil law.

## 7. Limits and controls

At fixed E0,Er and Jacobi directions in the open interior, M->infinity gives mu,nu,a->1,b->0, B->.5, qi->P. Equations(7),(9),(11) approach PR100 exactly. Compare at fixed Jacobi variables; finite-M Er/angles must not be relabelled as detector EB/angles.
Omitting the second term of(7) is a deliberately incomplete control. At finite M it generally differs; this tests the derived recoil phase obligation.
The M=1 transverse zero follows from parity of(5) and azimuthally symmetric continuum factor. It is a model identity, not a physical no-go.
The small-Delta limit diagnoses kernel conditioning; positive binding excludes Delta=0 ionization events.
The former PR99 W=1 phase-space moments remain kinematic fixtures. No unchanged old suite is rerun.

## 8. Frozen numerical plan and claims

Targeted new tests cover masses/binding, shifted potential geometry, both phases, charge-matched endpoint, mass normalization, flux and chart coefficients, lab positive branches, near-caustic propagation, finite-domain rejection, infinite-M link and input identity.
Analysis uses12generic kernels at4masses×3geometries, mp50/mp80;3independent two-term original-integral quadratures;12tiny cases; finite-M physical-model kinematics; weighted fold at Gauss orders24/48/96;73Jacobi-angle samples atM2/proton/infinite and a mass trend. Exact fixture definitions/tolerances are in FROZEN_CONTRACT.json before execution.
PNG/SVG are produced from saved JSON only. Root and separate reviewer inspect scope/axis units/legibility using the supplied figure criteria.

Permitted completed claims: derived finite-M direct-CBA channel model, both recoil phases, normalized invariant/Jacobi/lab densities, tested weighted two-root chart bridge and finite tested limits. Full HE-ANG remains SOURCE_INPUT_PENDING, physical_provider_admitted=false,event_sigma=false,physical_recoil_distribution=false,HE_X1_empirical_correction=false,globalcompletion=null. Exchange-complete joint payload, calibrated applicability/support/uncertainty and consumer qualification remain OPEN. C9-NB-01,C23E and otherownerOPEN are preserved. No new strong no-go or novelty theorem is claimed.
