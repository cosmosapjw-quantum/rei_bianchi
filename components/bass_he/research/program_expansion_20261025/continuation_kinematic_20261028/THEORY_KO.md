# KINEMATIC08 — 질량·에너지에서 직접 구성하는 정확 수용각 경계

## 1. 대상, convention과 선행 결과

정지 bare alpha와 광자의 반응 gamma+alpha→d+d를 같은 질량 M의 두 딸입자에 대한 조건부 두 물체 운동학으로 다룬다. Metric=(-,+,+,+), A=m_alpha c², M=m_d c², e=E_gamma, q=c p이며 에너지 및 q의 수치 단위는 MeV다. A,M,e는 입력한 정확 유리수이다. 0<A<2M, e>0을 요구하고 s=A²+2Ae, H=s−4M²>0, G=A+e, R=H/s, r=√R로 정의한다. 따라서 0<R<1이다. e_th=(4M²−A²)/(2A)>0이고 H>0⇔e>e_th다. H=0은 별도 threshold atom, H<0은 closed channel이다.

APERTURE07의 Bernstein 양성 밀도 적분, SetBounds의 집합 연산, 동일 사건에 속한 두 딸입자 관측을 재사용한다. 기존 source/test/plot은 그대로 보존한다. 이번 유도는 저장 gamma/a가 만들어지기 전의 A,M,e에서 시작하므로 그 중간 변수의 반올림에 의존하지 않는다. 실제 질량·beam uncertainty box, target motion, 전자 screening은 입력되지 않은 별도 물리 의무다.

## 2. 4-운동량에서 한 개의 제곱근으로 환원

CM에서 E*=√s/2, κ=c p*=√H/2이다. Lab boost는 β=e/G, γ=G/√s이고 γβ=e/√s다. μ=cos(theta*)인 +딸입자의 에너지와 운동량은

\[
E_+=\frac{G+er\mu}{2},\qquad
2q_{z,+}=L=e+Gr\mu,\qquad
4q_{\perp,+}^2=T=H(1-\mu^2).
\]

−딸입자는 μ→−μ, 반대 transverse 방향이다. E_++E_−=G, q_z,+ +q_z,−=e, transverse 합=0이다. G²−e²=s와 sR=H를 사용하면

\[
4(E_+^2-q_{z,+}^2-q_{\perp,+}^2)
=s-H=4M^2.
\]

E±>(G−e)/2=A/2>0이고 mass shell과 결합하면 E±≥M이다. 별도 recoil/binding energy를 추가하지 않아도 이 식이 전체 에너지 보존을 포함한다. 관측 방향은 정지점 밖에서

\[
F(\mu)=\frac{L}{\sqrt{L^2+T}}.
\]

L의 단위는 MeV, T는 MeV²이므로 F는 무차원이다. 기존 γ(μ+a) 식에는 a=e/(Gr)를 넣으면 같은 사상을 얻는다.

## 3. 정확 대수적 부호 판별

유리수 p,q와 R≥0에 대해 p+q√R의 부호는 제곱근을 근사하지 않고 결정할 수 있다. p와 q의 부호가 같으면 그 공통 부호다. 서로 반대이고 둘 다0이 아니면

\[
\operatorname{sgn}(p+q\sqrt R)
=\operatorname{sgn}(p)\operatorname{sgn}(p^2-q^2R).
\]

여기서 R≥0만 요구하며 p,q는 임의 부호다. R=0 또는 q=0이면 sign(p), p=0이면 sign(q)로 처리한다. p²=q²R인 정확 상쇄는0이다. 반대 부호인 두 항의 크기를 비교한 것이므로 제곱으로 원래 부호 조건을 잃지 않는다.

ν∈[−1,1]과 F를 비교할 때 먼저 L=e+Gμ√R와 ν의 부호를 비교한다. 부호가 다르면 그 결과로 끝난다. 같은 비영 부호이면 L²−ν²(L²+T)의 부호에 sign(L)을 곱한다. 이 다항식은

\[
P+Q\sqrt R,\quad
P=(1-\nu^2)(e^2+G^2\mu^2R)-\nu^2H(1-\mu^2),\quad
Q=2eG\mu(1-\nu^2)
\]

이므로 모든 계산은 유리수 연산과 정확 순서 비교다. 제곱근·초월 함수·부동소수점 tolerance가 인증 경로에 들어가지 않는다. L=T=0인 정지점은 방향을 정의하지 않는다.

## 4. 분기 위상과 무리수 fold

K=e²−G²R의 정확 부호가 a−1의 부호와 같다. K<0이면 F는 전체 구간에서 증가한다. K=0이면 μ=−1이 정지점이고 내부에서 증가하며 오른쪽 방향 극한은0이다. Public API는 정지 방향을 거절하고, 경계 탐색만 그 극한0을 보조값으로 사용한다. K>0이면

\[
\mu_c=-\frac{G\sqrt R}{e}\in(-1,0)
\]

에서 fold를 갖는다. 미분의 부호는 1+aμ이므로 [−1,μ_c]에서 감소, [μ_c,1]에서 증가한다. μ_c를 rational float로 대체하면 APERTURE07의 단조 구간 전제가 깨질 수 있다.

sign(μ+(G/e)√R)를 이용해 μ_c를 J=[j_l,j_u], |J|≤δ로 감싼다. 정확 rational root를 만나면 J의 폭을0으로 만든다. J 밖의 두 구간 [−1,j_l], [j_u,1]에서 각각 감소/증가하는 사상의 창 경계를 이분법으로 감싼다. 각 endpoint bracket의 폭은δ 이하다. Fold strip J는 inner에 넣지 않고 outer에만 넣는다.

## 5. 포함과 오차 정리

고정된 lab polar window W=[ν_l,ν_u], 연속 CM measure를 가정한다. 단조 branch의 실제 CM 하단과 상단이 [l0,u0],[l1,u1]에 있으면 inner=[u0,l1], outer=[l0,u1]를 사용하고 역전 inner는 공집합이다. 단조 branch마다 이 포함이 성립하고, fold strip은 외부 포함으로 보충하므로

\[
I_W\subseteq F^{-1}(W)\subseteq O_W
\]

가 measure-zero endpoint를 제외하고 성립한다. Branch가 최대2개이고 경계가 각각2개이므로 경계 불확실 길이는4δ 이하이다. Fold strip의 추가 길이δ를 더해 |O_W\I_W|≤5δ를 얻는다. J와 boundary bracket이 겹쳐도 합의 상계는 유효하다. Singleton window는 이 비상수 연속 방향 사상에서 measure0이고, full[-1,1]은 정지 endpoint를 제외한 exact FULL로 처리할 수 있다.

두 disjoint lab 창 A,B의 공유 사건 C=(P_A∩reflection(P_B))∪(P_B∩reflection(P_A))를 만든다. Indicator가 불확실한 점은 PA,PB 및 각각의 반사 중 적어도 하나의 불확실 영역에 있다. 합집합 상계로 |O_C\I_C|≤20δ다. 교집합/합집합의 inner는 inner끼리, outer는 outer끼리 조합하고, 차집합은 I_A\O_B 및 O_A\I_B를 사용한다.

ρ(μ)=Σb_k B_k^n((μ+1)/2), b_k≥0, n≤8, B=max b_k라 두면 0≤ρ≤B와 σ=2Σb_k/(n+1)이므로

\[
0\le U_Y-L_Y\le20B\delta.
\]

δ=σ/(20B2^40)로 선택하면 width≤σ2^-40이다. B=0은 exact0을 반환한다. B/σ≤(n+1)/2≤9/2이므로 δ≥2^-40/90이고 길이≤2인 bracket에는 최대 ceil(log2(180·2^40))=48번의 이분이 충분하다. 수동 δ는 반환된 실제 width와 width_bound로 판단한다.

## 6. 사건 수와 에너지 관측

ρ가 짝함수이면 두 딸입자의 label 교환과 C의 반사 대칭 때문에 ∫_C μρdμ=0이다. 따라서

\[
Y=\int_C\rho d\mu,\quad N_{\rm selected}=2Y,\quad
\mathcal E_{\rm pair}=G Y,\quad
\mathcal E_{+,C}=\mathcal E_{-,C}=\frac G2Y.
\]

이때 label별 에너지는 coincidence에 선택된 전체 사건에 대한 값이다. 특정 한 검출기가 받은 임의 daughter-energy 모멘트는 E1=(e/2)√R의 outward 처리가 추가로 필요하다. E1을 finite float로 대체해 exact physical moment로 표기하지 않는다. Single-window generic w0+w1μ 적분은 명시된 rational observable에 대해 기존 signed-bound 정리를 재사용한다.

pair_energy는 에너지×사건 measure의 차원을 갖는다. 실제 photon encounter flux/history와 전체 DCS normalization이 주어지지 않았으므로 물리적 시간당 반응률이나 heating으로 변환하지 않는다. Rest/binding 소유권은 population_rest_energy_witness에 한 번만 남긴다.

## 7. 판별 예와 구현 수용 기준

A=3,M=2일 때 e_th=7/6이다. e=3/2에서는 R=1/9, K=0, μ=−1의 daughter가 정확히 정지한다. e=6/5에서는 R=1/81, μ_c=−7/18로 rational fold를 얻는다. e=5/4에서는 R=1/33, μ_c=−17/(5√33)로 irrational fold 처리를 실제 시험한다. e=8/3에서는 s=25,R=9/25,γ=17/15,a=40/51로 기존 fixed-rational map과 exact 동등성이 있는 독립 연결 예를 얻는다.

기존 NIST2022 bare-nuclear rest energies와 native photon energies213/258/330MeV는 새 physical-input 경로의 예로 사용한다. 12개 원 DCS 점을 적분하거나 새 각분포로 변환하지 않는다. 테스트 density는 제조된 positive/even Bernstein 입력이고 실험 DCS는 아니다. Decimal80 four-vector boost는 방향 판별의 별도 수치 cross-check이며 정확 부호 정리의 증명과 구분한다.

입력 scalar의 common positive scaling에서 F, topology와 Y는 불변이며 pair energy는 같은 비율로 증가한다. 이 scale check, mass shell, conservation, stopped endpoint, sign loss, fold omission, factor2 및 marginal-product control을 실제 코드 검증으로 연결한다. 새 proof의 symbolic residual과 새로운 구현 실행·plot 근거의 상태는 별도 evidence에 기록한다.

## 8. 문헌과 주장 상태

위 식·포함 경계·오차 정리는 명시한 두 물체 운동학과 연속 measure 가정에서 직접 유도했다. 문헌 신규성/strong no-go를 주장하지 않는다. Arends1976 DOI10.1016/0370-2693(76)90671-7와 Rice2000 DOI10.1103/PhysRevC.61.064612는 실험 맥락을 제공한다. 원 M0475002 normalization, liquid-He electron/target-motion response, complete physical angular law/flux, named nonthermal/thermalization/global-species binding은 현재 외부 입력 의무를 유지한다. 과학·수치·구현·게시의 완료 상태는 각 실제 근거와 별개다.
