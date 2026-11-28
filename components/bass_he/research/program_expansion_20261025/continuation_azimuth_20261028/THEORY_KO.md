# AZIMUTH09 이론 — 유한 방위각에서 정확 포함과 공유 사건

## 1. 정의와 물리 사상

정지 bare alpha의 두 동일질량 daughter 모형에 KINEMATIC08의 convention을 고정한다. `A=m_alpha c²`, `M=m_d c²`, `e=E_gamma`이며 모두 선언된 정확 유리수 rest/incident energy(MeV)다. `s=A²+2Ae`, `H=s−4M²>0`, `G=A+e`, `R=H/s`, `r=√R`다. 0<A<2M, e>0인 open channel에서 q=cp의 transverse components와 lab polar cosine은

\[
\mathbf q_{\perp,+}=\frac{\sqrt H}{2}\sqrt{1-\mu^2}
(\cos2\pi t,\sin2\pi t),\qquad
\mathbf q_{\perp,-}=-\mathbf q_{\perp,+},
\]
\[
F(\mu)=\frac{e+Gr\mu}{\sqrt{(e+Gr\mu)^2+H(1-\mu^2)}}.
\]

Metric signature는(-,+,+,+). z boost는 두 transverse 성분을 바꾸지 않는다. 따라서 실험실 방향 사상은

\[
\Psi_+(\mu,t)=(F(\mu),t),\qquad
\Psi_-(\mu,t)=(F(-\mu),t+\tfrac12\pmod1).
\]

μ는[-1,1], t는 원주 R/Z다. Stopped endpoint와 p_perp=0의 방향은 전체 연속 측도에서 영집합이며 public polar comparator의 stopped rejection은 그대로 둔다. 원자형 threshold measure는 기존 H=0 rejection을 유지한다. Lab에서 두 polarcos가 서로 음수인 관계는 사용하지 않는다.

ρ(μ)는 degree n≤8의 비음수 Bernstein polynomial, x=(μ+1)/2에 대해

\[
\rho(\mu)=\sum_{k=0}^n b_k{n\choose k}x^k(1-x)^{n-k},\quad
b_k\ge0,\quad b_k=b_{n-k}.
\]

선언 사건 측도 `dm=ρ(μ)dμdt`의 총량은 `σ=2Σb_k/(n+1)`이고 `0≤ρ≤B=max b_k`. `UNIFORM_DECLARED`는 입력 가정이다. dt=dφ/(2π)이므로 선언 측도의 dΩ 밀도는ρ/(2π)이다. 이 식은 원 empirical DCS의 particle/event convention을 선택하는 식이 아니다.

## 2. Detector와 label 교환

유리수 turn arc S(a,w)는 `0≤a<1,0≤w≤1`이며 `[a,a+w)`를 mod1로 사상한 집합이다. w0/1은 empty/full을 구별하고 crossing은[0,a+w−1)∪[a,1)이다. Detector D는 최대8개 `W_i×S_i`의 union이다. Polar window W_i는[-1,1]의 유리수 닫힌 구간이며 singleton은 영측도로 처리한다. 경계 inclusion 선택은 현재 연속 측도에서 결과에 영향을 주지 않는다.

`J(μ,t)=(−μ,t+1/2 mod1)`는 J²=id인 measure-preserving involution이다. J의 측도 보존은 ρ의 짝대칭과 uniform t에서 온다. D+=Ψ+^-1(D), D−=Ψ−^-1(D)=J(D+)로 둔다. A/B 겹침을 허용해도 이 정의가 유지된다.

서로 다른 두 딸입자가 A/B를 채우는 coincidence C, detector hit H, assignment overlap O는

\[
Q_1=A_+\cap B_-,\quad Q_2=B_+\cap A_-,\quad
C=Q_1\cup Q_2,\quad O=Q_1\cap Q_2,
\]
\[
H_A=A_+\cup A_-,\quad D_A=A_+\cap A_-,\quad
I_A=\mathbf1_{A_+}+\mathbf1_{A_-}.
\]

Pointwise `I_A=1_HA+1_DA`와 `1_Q1+1_Q2=1_C+1_O`가 성립한다. 또한 C⊂H_A∩H_B이지만 이 포함은 일반적으로 진포함이다. 이 세 관계가 event, selected particle count, assignment count를 분리한다. 중첩된 patches는 내부에서도 union 처리한다.

## 3. 정확한 방위각 strip 환원

모든 S_i endpoint와 S_i−1/2의 endpoint, 0과1을 모아 정렬한다. 각 열린 strip T_j=(t_j,t_{j+1}) 안에서는 모든 sector membership가 상수다. 따라서 rational midpoint로 활성 patches를 결정하는 행위는 정확한 Boolean 선택이다. Polar 함수에 대한 midpoint quadrature는 수행하지 않는다.

서로 다른 활성 polar window W_i(i=1,…,N,N≤8)에 대해 검증된 KINEMATIC08 역상 enclosure `I_i⊂P_i=F^-1(W_i)⊂O_i`를 한 번씩 계산한다. T_j에서 A+는 활성 A창들의 P_i union, A−는 t+1/2에서 활성 A창의 reflected P_i union이다. 동일하게 B±와 C,H,D,O를 합성한다. Inner/outer union/intersection의 단조성에 의해 각 strip에서 `I_E,j⊂E_j⊂O_E,j`를 얻는다.

Bernstein polynomial의 exact rational primitive를 쓰면

\[
L_E=\sum_j|T_j|\int_{I_{E,j}}\rho\,d\mu,
\qquad U_E=\sum_j|T_j|\int_{O_{E,j}}\rho\,d\mu
\]

가 모두 유리수이고 `L_E≤m(E)≤U_E`다. 적분은 이미 검증된 APERTURE07 루틴을 그대로 호출한다. 같은 창이 여러 patch에 나와도 preimage cache key는 정확 유리수 window identity이며 임의 반올림 key를 만들지 않는다.

## 4. 포함 폭 정리와 계산량

**정리.** 위 정의역과 density/geometry 조건에서, 모든 Boolean event E에 대해 실제 반환 width와 area bound가

\[
0\le U_E-L_E\le B\sum_j|T_j|\,|O_{E,j}\setminus I_{E,j}|
\le10NB\delta
\]

를 만족한다.

**증명.** 선행 polar solver는 `U_i=O_i\I_i`의 길이를5δ 이하로 감싼다. 공통 불확실 집합 `U=∪_i(U_i∪(−U_i))`의 길이는 합집합의 subadditivity로10Nδ 이하이다. μ∉U이면 모든 polar window와 reflection membership가 확정된다. t의 유한한 경계점을 제외한 각 strip에서 방위각 membership도 확정되므로 모든 Boolean expression의 inner/outer membership가 일치한다. 따라서 `O_E,j\I_E,j⊂U`. Strip 길이의 합은1이고 ρ≤B이므로 위 경계가 성립한다. ∎

N>0,B>0에서 default `δ=σ/(10NB2^40)`을 택하면 `U_E−L_E≤σ2^-40`. B/σ≤(n+1)/2≤9/2,N≤8이므로 `δ≥1/(360·2^40)`. 초기 polar bracket 길이≤2에서 필요한 이분 횟수는 최대 `ceil(log2(720·2^40))=50`. 이 상계는 각 root의 횟수이며 arbitrary rational bit-length에 관한 CPU/wall 정리가 아니다. Arc endpoint는 최대4×16+2개이므로 strip 수도 유한하다.

N=0 또는 B=0의 measure는 shortcut으로 정확0이다. Manualδ는 기존[2^-80,1] 정의역이며 실제 반환 폭을 쓴다. Inclusive/assignment sum은 Boolean output 두 개의 합이므로 각 component bound의 합을 사용한다. 2Y,GY 등의 bound도 해당 계수만큼 scale한다. 모든 output에 같은 epsilon을 일괄 부여하지 않는다.

## 5. 조건부 확률과 에너지

C⊂H인 hit event에서 L_H>0이면 양의 분모가 인증되고

\[
\frac{L_C}{U_H}\le P(C\mid H)\le\min\left(1,\frac{U_C}{L_H}\right).
\]

이는 양의 interval에 대한 단조 division과 subset probability≤1로부터 온다. U_H=0이면 conditional probability undefined, L_H=0<U_H이면 현재 enclosure로 denominator positivity unresolved다. 두 상태는 null bound와 서로 다른 status를 반환한다. 상대적으로 작은 H에서 ratio conditioning이 나빠질 수 있으므로 eventε를 ratioε로 바꾸지 않는다.

J는 Q1/Q2를 교환하여 C를 보존한다. ρ는 짝이고 t는 uniform이므로 `∫_C μdm=−∫_C μdm=0`. `E±=(G±erμ)/2`를 적분하면

\[
N_{\rm selected}=2Y,\qquad
\mathcal E_{\rm pair}=GY,\qquad
\mathcal E_+=\mathcal E_-=\frac G2Y,\quad Y=m(C).
\]

이 에너지는 rest energy를 포함한 total-energy observable이고 detector-specific energy나 thermal deposition이 아니다. Physical number density, heat capacity, binding RHS와 이 observable을 별도 port로 유지한다.

## 6. 독립 해석 예와 판별량

ρ=1/2,fullpolar에서 A=[0,1/4),B=[1/2,3/4)는 각 assignment의 φ길이1/4이고 서로 겹치지 않아 Y=1/2다. Marginal acceptance의 독립 곱 2(1/4)^2=1/8과 hitA×hitB=1/4는 다른 양이다. 같은 fullsphere detector A=B이면 Y1,assignment2,overlap1,선택daughter2다. 같은 halfcircle A=B이면 C0이지만 H_A∩H_B는1이다.

반대 quarter detector의 위치를 shift d∈[0,1]만큼 움직일 때 fullpolar coincidence는 원주에서 대응 arc의 삼각형 overlap law다. 모든 끝점이 유리수인17점으로 이 exact reference와 반환값을 비교하고 그림으로 표시한다. 이 값은 생산 적분기를 재호출해 expected를 만들지 않는다.

비자명한 운동학 예: A3,M2,e8/3이면 s25,r3/5,G17/3,`k=e/(Gr)=40/51`. Forward polar A=[0,1]×quarter, backward B=[−1,0]×oppositequarter에서 μ coincidence구간은[k,1]과[−1,−k], φ길이는각1/4이다. 따라서 Y11/204,hitA91/204,hitB11/204,conditional11/91와1,2Y11/102,GY11/36MeV,각label11/72MeV다. 참조값이 API의 enclosure에 들어가야 하며 bisection endpoint의 부동수치 일치를 요구하지 않는다.

반례들은 각각 특정 잘못된 연산의 진단 예다. 새로운 물리적 strong no-go 또는 문헌 신규성 성과로 채택하지 않는다. 독립 사전 검토는 review/PRECONTRACT_REVIEW_KO.md, 실제 code/결과의 근거는 해당 static/final review와 실행 receipt에서 연결한다.
