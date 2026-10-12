# PHYS34 — 하단 분지의 유한 폭 패킷과 같은 수준 근 비교

작성 역할: `/root/polynomial_theory`, **NONBLIND 이론 후보 기여자**. GPT-6 Astra를 상속하며 모델을 바꾸지 않았다. 최종 decision reviewer가 아니다. 이 문서는 **derived / conditional theorem / OWNER_SELF_REVIEW** 상태다. 새 물리 커널·부호·잔차·근의 평가, 프로그램 import·main, 일반 산술 기초검사의 반복은 모두 **0회**다. 아래의 수치 상수와 부등식 조건은 검증할 대상을 지정하며, 그 조건을 이번 기여에서 실제로 인증했다는 뜻이 아니다.

## 1. 읽은 근거, 수준과 범위

이번 작업 공간에서 직접 읽은 근거는 다음과 같다.

- `phys33/inputs/PHYS32/contributions/theory/QUANTITATIVE_REMAINDER_KO.md`: T32.3–30의 공통 sign 기하, 실현가능성, 기울기와 이동 경계.
- `phys33/inputs/PHYS32/contributions/numerics/POSITIVE_PEANO_AND_TOY_ORACLES_KO.md`: P32.1–9의 정확한 Peano 항등식과 근 차이 전달.
- `phys33/report/ROOT_TUBE_PROOF_KO.md`: 상단 인증서의 수치값을 제외한 존재·잔차·균일 이동·근 순서의 논증 구조.
- `phys33/inputs/PHYS29_SECOND_ORDER_FIRST.json`: 아래 두 키의 실제 저장 문자열. 이 파일의 과거 커널·도함수 수치값을 새로운 하단 구간 bound로 사용하지 않는다.

선행 PHYS33의 owner 지정 commit은 `06e65fa291685fcec0e012ee84d291b356922748`이다. 이 기여는 별도 원격 조회를 수행하지 않았고, 파일 identity와 새 실행 범위의 고정은 owner의 provenance·실행 계약에 따른다. PHYS33의 exact Fraction 다항식 및 outward interval helper는 owner가 byte identity를 유지하여 재사용한다. 이 문서는 그 helper를 수정하거나 재실행하지 않는다.

정확하게 선언한 에너지·폭·분산 반경은

\[
a=13.61,\quad b=24.58,\quad m=18,\quad
L=m-a=4.39,\quad R=b-m=6.58\quad(\mathrm{eV}),
\]
\[
s=-1,\qquad 0\le\delta\le d=0.001\ \mathrm{eV},
\qquad \eta=0.25\ \mathrm{eV}^2.
\tag{L34.1}
\]

분산 tube는 \(I_W=[\widehat W-\eta,\widehat W+\eta]\)이며, 중심은 `constants.stored_PHYS26_root_strings.lower_root`의 **전체 문자열**을 정확한 십진 유리수로 해석한 값이다.

```text
23.42021899235339297211351479315057454874081817054292481189118799276998028222045968598367218051982929113154658725620727981626004744285172054408046783979559490765
```

이 분지에서 두 프로파일이 공유할 정확한 수준은

\[
\boxed{A_-= -3.2582515\times10^{-137}\ \mathrm{s}^{-4},}
\tag{L34.2}
\]

이며 원 키는 `second_order.jet_chain.lower_root.response_s-4`다. 이를 상단 `upper_root`의 수준, `scalar_bivariate.lower_root`의 값, `stored_PHYS26_response_s-4`, 0 또는 새로 평가한 \(F(0,\widehat W)\)로 바꾸지 않는다. 특히 \(\widehat W\)를 정확한 근으로 가정하지 않는다. `lower`는 상속한 극값 분지 이름이며, 분산의 수치적 크기 순서를 새로 정의하는 이름이 아니다.

같은 고정 source-real 커널을 사용한다.

\[
\mathscr D=E\partial_E,\qquad
k(E)=\mathcal P(\mathscr D^2+3\mathscr D)
\left\{\sigma_{\rm HI}(E)[J_x+J_w(E-\chi)]\right\},
\quad
\mathcal P=\frac{q_{\rm src}N_0c_{\rm light}n_H(1-x_{HII})}{180}.
\tag{L34.3}
\]

여기서 \(q_{\rm src}\)는 원 prefactor의 고정 정규화 상수 \(q\)를 구별하여 쓴 표기이며, 아래 두 패킷의 혼합확률 \(q\)와 다르다. 원 binary64 리터럴의 값 자체를 정확한 유리수로 해석하고, 원 \(J\)의 직렬화 문자열과 L34.1–2의 선언값은 각각 지정된 정확한 십진 유리수로 해석한다. 그 위의 정확한 실수 곱과 함수를 대상으로 한다. 저장된 rounded prefactor를 exact product 대신 쓰거나 native binary64 연산 순서를 모사하는 의미로 바꾸지 않는다. \(c_{\rm light}\)와 proper-second 단위를 유지하며 natural units를 도입하지 않는다. \(W\)는 eV², \(k,F,A_-\)는 s⁻⁴, \(k^{(n)}\)는 s⁻⁴ eV⁻ⁿ이다. 기존 metric convention \((-,+,+,+)\)을 바꾸지 않는다.

## 2. 하단 기하에서 실제 분산의 보존

프로파일 변수는 \(z\in[-1,1]\)이고

\[
h_u(z)=\frac12,\qquad
h_p(z)=\frac{35z^4-30z^2+11}{16}
=\frac{1+P_4(z)}2.
\tag{L34.4}
\]

이 두 고정 확률밀도의 정규화, 대칭성, 양성, 공통 \(\mu_2=1/3\)은 선행 정확 대수 결과를 그대로 쓴다. 프로파일 측도 \(d\alpha=h_\alpha(z)dz\)는 \(\delta,W\)와 독립이고, \(\alpha=u,p\)다.

\[
r=R-\delta,\quad V=W-\mu_2\delta^2,\qquad
e_\delta=b-\delta=m+r,\qquad
x_{\delta,W}=m-\frac Vr,
\tag{L34.5}
\]
\[
p=\frac{V}{r^2+V},\qquad q=\frac{r^2}{r^2+V}=1-p.
\tag{L34.6}
\]

중심 확률변수 \(Y\)가 \(e_\delta,x_{\delta,W}\)에 각각 확률 \(p,q\)를 갖게 하고, 독립인 \(Z\sim\alpha\)를 사용해 광자 에너지를 \(E=Y+\delta Z\)로 둔다. 그러면

\[
\mathbb E(Y-m)=pr-q\frac Vr=0,
\]
\[
\mathbb E[(Y-m)^2]
=pr^2+q\frac{V^2}{r^2}
=\frac{Vr^2+V^2}{r^2+V}=V.
\tag{L34.7}
\]

프로파일의 평균이 0이므로 교차항도 0이고,

\[
\boxed{\mathbb E E=m,\qquad
\operatorname{Var}(E)=V+\mu_2\delta^2=W.}
\tag{L34.8}
\]

따라서 \(V\)와 실제 분산 \(W\)를 혼동하지 않는다. 두 프로파일은 공통 \(\mu_2\) 때문에 같은 \(W\)에서 중심과 가중치를 정확히 공유한다. 응답은

\[
\boxed{F_\alpha(\delta,W)
=p\int k(e_\delta+\delta z)d\alpha(z)
+q\int k(x_{\delta,W}+\delta z)d\alpha(z).}
\tag{L34.9}
\]

## 3. 실현가능성과 전체 패킷의 고정 포함구간

직사각형 \([0,d]\times I_W\)에서 확인할 충분조건은

\[
\boxed{d<\min(L,R),\qquad
\mu_2d^2<\widehat W-\eta,\qquad
\widehat W+\eta<(R-d)(L-d).}
\tag{L34.10}
\]

이 조건이 성립하면 모든 허용 \(\delta,W\)에서

\[
0<V\le W\le\widehat W+\eta
<(R-d)(L-d)\le(R-\delta)(L-\delta).
\tag{L34.11}
\]

따라서 \(r>0\), \(p,q>0\)이며

\[
a+\delta<x_{\delta,W}<m<e_\delta=b-\delta.
\tag{L34.12}
\]

두 패킷은 모두 \([a,b]\)에 남는다. 정확한 실현가능 조건에는
\(W\le(R-\delta)(L-\delta)+\mu_2\delta^2\)가 들어가지만, L34.10은 마지막 양의 항을 버린 보수적인 충분조건이다. 충분조건을 필요조건이라고 해석하지 않는다.

전 폭·전 tube에 대한 endpoint 패킷은

\[
e_\delta+\delta z\in[b-2d,b].
\tag{L34.13}
\]

내부 패킷은 \(V\le\widehat W+\eta\), \(V\ge\widehat W-\eta-\mu_2d^2\), \(R-d\le r\le R\)에서

\[
\boxed{x_{\delta,W}+\delta z\in
\left[
m-\frac{\widehat W+\eta}{R-d}-d,\quad
m-\frac{\widehat W-\eta-\mu_2d^2}{R}+d
\right].}
\tag{L34.14}
\]

새 커널 인증의 후보 containing interval은

\[
J=[14.35,24.58]\ \mathrm{eV}.
\tag{L34.15}
\]

L34.13–14의 두 구간이 \(J\)에 포함되는지는 exact rational 비교로 별도 확인해야 한다. 상단 계산에서 사용한 \([13.61,22]\)의 인증값은 \(24.58\) eV까지의 새로운 하단 bound를 제공하지 않는다.

패킷 포함관계가 성립하면 같은 \(z\)에서

\[
(1-t)e_\delta+t x_{\delta,W}+\delta z
=(1-t)(e_\delta+\delta z)+t(x_{\delta,W}+\delta z)
\in J\quad(0\le t\le1).
\tag{L34.16}
\]

이것이 기울기 적분에 필요한 **선분 전체**의 정의역이다. 기준점 \(\delta=0,W=\widehat W\)와 그 후의 중심 이동 경로도 같은 볼록 구간에 포함된다.

## 4. 역방향 선분에서도 실제 분산 기울기는 양의 평균

\(\delta\)를 고정하고 \(g(y)=\int k(y+\delta z)d\alpha(z)\)로 둔다. 국소적으로 \(e=e_\delta\), \(x=x_{\delta,W}\), \(\mathcal Q=r^2+V\)라고 쓰면

\[
D=x-e=-\frac{\mathcal Q}{r}<0,
\qquad p_W=\frac{r^2}{\mathcal Q^2}=\frac1{D^2},
\qquad x_W=-\frac1r,
\qquad qx_W=Dp_W.
\tag{L34.17}
\]

여기서 \(W\) 미분은 실제 분산 미분이며 \(V_W=1\)이다. L34.9를 직접 미분하여

\[
F_{\alpha,W}
=p_W[g(e)-g(x)]+qx_Wg'(x)
=\frac{g(e)-g(x)+Dg'(x)}{D^2}
\tag{L34.18}
\]

를 얻는다. 임의의 \(D\ne0\)에 대해 부분적분하면

\[
\int_0^1t\,g''(e+tD)dt
=\frac{g'(x)}D-\frac{g(x)-g(e)}{D^2}
=\frac{g(e)-g(x)+Dg'(x)}{D^2}.
\tag{L34.19}
\]

따라서 하단에서 \(D<0\)인 사실은 추가 음의 부호를 만들지 않는다. \(k''\)가 콤팩트 구간에서 연속·유계라는 조건으로 적분 아래 미분을 정당화하면

\[
\boxed{F_{\alpha,W}(\delta,W)
=\int_0^1t\int
k''((1-t)e_\delta+t x_{\delta,W}+\delta z)
\,d\alpha(z)dt.}
\tag{L34.20}
\]

새 구간 \(J\)에서 실제로

\[
0<m_2\le k''(E)\le M_2\qquad(E\in J)
\tag{L34.21}
\]

가 인증되면, 확률측도의 비음성과 \(\int_0^1t\,dt=1/2\)로

\[
\boxed{0<\kappa:=\frac{m_2}{2}
\le F_{\alpha,W}\le K:=\frac{M_2}{2}.}
\tag{L34.22}
\]

이는 모든 \(\delta,W,\alpha\)에 공통인 전체 tube bound다. \(k'''<0\)를 새 전제로 추가할 필요가 없다. 이 국소 근 비교 정리는 모든 가능한 광자 분포에서의 전역 극값 성질을 별도로 증명하지 않는다.

## 5. 정확한 lower 수준에 대한 잔차와 균일 이동 상계

기준 \(W=\widehat W\), \(\delta=0\)에서

\[
x_0=m-\frac{\widehat W}{R},\qquad
p_0=\frac{\widehat W}{R^2+\widehat W},\qquad
q_0=\frac{R^2}{R^2+\widehat W},
\quad F_0(\widehat W)=p_0k(b)+q_0k(x_0).
\tag{L34.23}
\]

\(x_0\)는 저장된 \(\widehat W\) 전체 문자열에서 정확히 재구성해야 한다. 과거 80자리 `energy_nodes_eV.u_zero`를 대신 넣으면, 같은 수학적 점에서의 residual enclosure라는 의미가 달라질 수 있다. 필요한 새 잔차 인증은

\[
F_0(\widehat W)-A_-\in[r_-,r_+],\qquad
\epsilon_r=\max(|r_-|,|r_+|).
\tag{L34.24}
\]

그 잔차가 작더라도 0으로 자르지 않는다. \(\widehat W\)를 exact root로 먼저 가정하고 이동을 평가하면 L34.24의 의무가 사라지는 것이 아니라 숨겨진다.

이 절에서 \(p_\delta=p_{\delta,\widehat W}\), \(q_\delta=1-p_\delta\), \(x_\delta=x_{\delta,\widehat W}\)다. 직접 미분하면

\[
\frac{dp_\delta}{d\delta}
=\frac{2(R-\delta)(\widehat W-\mu_2R\delta)}
{[(R-\delta)^2+\widehat W-\mu_2\delta^2]^2}.
\tag{L34.25}
\]

따라서 아래 **추가 조건**을 exact 비교해야 한다.

\[
\boxed{\widehat W>\mu_2Rd.}
\tag{L34.26}
\]

이때 \(p_0\le p_\delta\le p_d\), \(q_\delta\le q_0\)다. L34.26을 확인하지 않은 채 \(p_d-p_0\)를 \(|p_\delta-p_0|\)의 균일 상계로 사용할 수는 없다. L34.10의 \(\mu_2d^2<\widehat W-\eta\)와 L34.26은 구별한다.

하단 중심 이동의 정확한 부호 있는 식은

\[
x_\delta-x_0
=-\frac{\widehat W\delta/R-\mu_2\delta^2}{R-\delta}.
\tag{L34.27}
\]

부호를 쓰지 않고 삼각부등식과 \(R-\delta\ge R-d\)를 적용해

\[
|x_\delta-x_0|\le
D_x:=\frac{\widehat Wd}{R(R-d)}+
\frac{\mu_2d^2}{R-d}
\tag{L34.28}
\]

를 얻는다. \(e_\delta-b=-\delta\)여서 endpoint 이동 크기는 \(\delta\)다. 두 중심이 움직이는 방향과 무관하게 아래 절댓값 경계가 성립한다.

\(M_1\ge\sup_J|k'|\)라 두고, L34.21을 사용한다. 평균 0인 프로파일에 일차 Taylor 적분 나머지를 적용하면

\[
\left|\int k(y+\delta z)d\alpha(z)-k(y)\right|
\le\frac{\mu_2M_2\delta^2}{2}.
\tag{L34.29}
\]

중심 응답의 이동은 정확하게

\[
\begin{aligned}
&p_\delta k(e_\delta)+q_\delta k(x_\delta)
-p_0k(b)-q_0k(x_0)\\
&=(p_\delta-p_0)[k(b)-k(x_0)]
+p_\delta[k(e_\delta)-k(b)]
+q_\delta[k(x_\delta)-k(x_0)]
\end{aligned}
\tag{L34.30}
\]

로 분리된다. \(O_0\ge|k(b)-k(x_0)|\)의 새 outward 상계를 사용하면 L34.25–30으로

\[
\boxed{
B_{\rm disp}=(p_d-p_0)O_0
+M_1[p_d d+q_0D_x]+\frac{\mu_2M_2d^2}{2},
}
\tag{L34.31}
\]
\[
\boxed{|F_\alpha(\delta,\widehat W)-F_0(\widehat W)|
\le B_{\rm disp}\quad(0\le\delta\le d,\ \alpha=u,p).}
\tag{L34.32}
\]

평활화 오차는 \(p_\delta+q_\delta=1\)이므로 두 번 더하지 않는다. L34.31의 모든 항은 s⁻⁴이며, \(D_x\)는 eV다. 이는 \(\delta=d\)에서의 실제 응답 차이를 다른 폭에 외삽한 식이 아니라, 각 항의 균일 상계로 구성한 전 구간 결과다.

## 6. 근을 찾지 않고 증명하는 존재와 유일성

L34.22, L34.24, L34.32를 확보한 뒤 마지막 tube 조건으로

\[
\boxed{\mathcal M:=\kappa\eta-(B_{\rm disp}+\epsilon_r)>0}
\tag{L34.33}
\]

를 인증한다. 그러면 모든 허용 \(\delta\)와 두 프로파일에 대해

\[
F_\alpha(\delta,\widehat W-\eta)-A_-
\le B_{\rm disp}+\epsilon_r-\kappa\eta<0,
\]
\[
F_\alpha(\delta,\widehat W+\eta)-A_-
\ge-(B_{\rm disp}+\epsilon_r)+\kappa\eta>0.
\tag{L34.34}
\]

연속성과 W에 대한 엄격한 단조성으로 정확히 하나의

\[
W_{-,\alpha}(\delta)\in(\widehat W-\eta,\widehat W+\eta),
\qquad F_\alpha(\delta,W_{-,\alpha}(\delta))=A_-
\tag{L34.35}
\]

가 존재한다. 기울기 하한을 다시 적분하여

\[
|W_{-,\alpha}(\delta)-\widehat W|
\le\frac{B_{\rm disp}+\epsilon_r}{\kappa}<\eta,
\qquad
|W_{-,\alpha}(0)-\widehat W|
\le\frac{\epsilon_r}{\kappa}
\tag{L34.36}
\]

를 얻는다. 이 증명에는 새 root iteration 또는 유한 폭 quadrature를 전제하지 않는다. L34.33이 실패하면 이 충분조건이 근 존재를 인증하지 못한 것이며, 실제 근이 없다고 단정할 수도 없다.

## 7. 유한 폭의 정확한 Peano 항등식과 하단 근 순서

\(Q(z)=(1-z^2)^4\)에 대해 직접 미분하면

\[
Q^{(4)}(z)=48(35z^4-30z^2+3),\qquad
h_p-h_u=\frac{Q^{(4)}}{768}.
\tag{L34.37}
\]

\(Q,Q',Q'',Q'''\)의 두 끝점 값이 0이므로 네 번 부분적분의 경계항이 모두 사라진다. \(\partial_z^4k(y+\delta z)=\delta^4k^{(4)}(y+\delta z)\)이고 네 번의 부호 반전은 양수다. 또한 정확 다항식 원시함수에서

\[
\int_{-1}^1Q(z)dz=\frac{256}{315},\qquad
d\pi(z)=\frac{315}{256}(1-z^2)^4dz
\tag{L34.38}
\]

는 확률측도이므로, \(k\in C^4(J)\)와 패킷 포함관계 아래 정확히

\[
\boxed{\int k(y+\delta z)(h_p-h_u)(z)dz
=\frac{\delta^4}{945}\int k^{(4)}(y+\delta z)d\pi(z).}
\tag{L34.39}
\]

작은 폭의 leading Taylor 항을 남긴 근사가 아니다. \(s=-1\)은 중심 \(y\)의 위치에 들어가며, 이 고정 \(\delta,W\)에서의 프로파일 항등식에 새로운 음의 부호를 만들지 않는다.

두 프로파일의 중심·가중치가 공통이므로

\[
F_p(\delta,W)-F_u(\delta,W)
=\frac{\delta^4}{945}\mathcal S_-(\delta,W),
\tag{L34.40}
\]
\[
\mathcal S_-
=p\int k^{(4)}(e_\delta+\delta z)d\pi(z)
+q\int k^{(4)}(x_{\delta,W}+\delta z)d\pi(z).
\tag{L34.41}
\]

새 하단 패킷 전체를 포함하는 \(J\)에서 실제로

\[
0<m_4\le k^{(4)}(E)\le M_4\qquad(E\in J)
\tag{L34.42}
\]

를 인증하면 \(m_4\le\mathcal S_-\le M_4\)다. 두 근의 존재를 L34.35에서 먼저 확보한 뒤
\(\Delta W_-=W_{-,p}-W_{-,u}\)와

\[
\overline C_p=\int_0^1F_{p,W}
(\delta,W_{-,u}+t\Delta W_-)dt
\tag{L34.43}
\]

를 정의한다. 두 근 사이가 같은 tube 안에 있으므로 \(\kappa\le\overline C_p\le K\)다. 같은 정확한 \(A_-\)에서

\[
0=\overline C_p\Delta W_-
+F_p(\delta,W_{-,u})-F_u(\delta,W_{-,u})
\]

이므로

\[
\boxed{\Delta W_-=-\frac{\delta^4}{945}
\frac{\mathcal S_-(\delta,W_{-,u})}{\overline C_p}.}
\tag{L34.44}
\]

따라서 조건들이 모두 인증되었을 때에만

\[
\boxed{-\frac{M_4}{945\kappa}\delta^4
\le W_{-,p}(\delta)-W_{-,u}(\delta)
\le-\frac{m_4}{945K}\delta^4<0,
\quad 0<\delta\le d}
\tag{L34.45}
\]

를 결론낸다. 계수는 eV⁻²이고 전체 차이는 eV²다. \(\delta=0\)에서는 두 응답이 같고 유일근도 같으며 엄격한 부등호를 적용하지 않는다. \(k^{(4)}\ge0\)만 확보하면 비엄격한 순서만 따라온다. 부호가 미인증이거나 변화하면 L34.45를 주장하지 않는다.

## 8. 구간 인증 연결과 남은 조건

PHYS33에서 유도·구현한 \(\zeta=\sqrt{E/B}\), \(B=E_0y_a\) 표현을 그대로 사용한다. 프로파일 변수 \(z\)와 이 sqrt 좌표 \(\zeta\)는 서로 다르다. exact Fraction 다항식의 Bernstein 계수 enclosure와 양의 외부 거듭제곱 인자에 대한 outward enclosure를 곱해 **새 에너지 구간**의 \(k',k'',k^{(4)}\) 경계를 얻는 역할은 owner의 새 실행에 있다. 이전 일반 다항식·산술 기초검사를 여기서 반복하지 않는다.

\(J\)의 양 끝 에너지에서 얻은 outward sqrt 끝점을 정확한 유리수로 해석한 grid가 실제 polynomial cell을 정의해야 한다. 다시 Decimal로 확장한 표시·prefactor 구간을 exact polynomial cell과 동일시하지 않는다. 외부 인자를 더 넓은 구간에서 덮는 것은 가능하지만, Bernstein 다항식 bound가 증명하는 대상은 원 exact cell이다.

실제 sqrt-grid 역상의 두 끝점은 H I cutoff \(\operatorname{real64}(13.60)\)보다 크고 He I cutoff \(\operatorname{real64}(24.59)\)보다 작음을 별도 exact 비교한다. \(\chi=\operatorname{real64}(13.598434599702)\)는 가열 에너지 offset이며 cutoff와 같지 않다. 이 구별을 생략하고 piecewise provider 경계를 건너 미분 부호를 연장하면 논증의 대상이 바뀐다.

| 의무 | 이론식 | 이번 이론 기여의 실행 상태 |
|---|---|---|
| lower A와 전체 \(\widehat W\) 원 키 | L34.2, L34.23–24 | 원 문자열 읽음; 새 잔차 미평가 |
| 실제 분산·mean 보존 | L34.7–8 | 직접 유도 |
| 전 tube feasibility·패킷·cutoff 포함 | L34.10–16, §8 | 조건 유도; 수치 판정 미평가 |
| 새 영역 \(m_2>0,M_1,M_2\) | L34.21–22 | 미평가 |
| 확률 단조성과 uniform Bdisp | L34.25–32 | 직접 유도; 상수 판정 미평가 |
| lower residual과 tube margin | L34.24, L34.33 | 미평가 |
| 새 영역 \(m_4>0,M_4\) | L34.42 | 미평가 |
| 유일근 및 엄격한 하단 프로파일 순서 | L34.35, L34.45 | 위 조건들에 대한 조건부 정리 |

문서를 정적으로 다시 읽으며 하단 \(x_W=-1/r\), \(D<0\), \(qx_W=Dp_W\), 적분의 \(t\) 가중치와 \(1/2\), \(x_\delta-x_0\)의 부호, \(p_\delta\) 단조성의 추가 조건, Peano의 \(1/945\), 음수 quotient의 부등호 방향을 확인했다. 이는 작성자 자신의 **OWNER_SELF_REVIEW**이고 과학 프로그램 실행이나 독립 최종 심사가 아니다.

두 분지 간 gap 부호 또는 그 프로파일 변화는 이 하단 단독 정리에 포함하지 않는다. 예컨대 \(G_\alpha=W_{-,\alpha}-W_{+,\alpha}\)를 별도 정의하더라도
\(G_p-G_u=\Delta W_- -\Delta W_+\)이므로 두 \(\Delta W\)가 각각 음수라는 사실만으로 그 차이의 부호를 알 수 없다. 또한 상단과 하단의 저장 수준 \(A_+,A_-\)는 서로 다르다. 각 분지에서 같은 수준을 유지한 결과를 두 분지가 같은 A를 쓴 결과로 바꿔 해석할 수 없다. 별도 gap 계약·상계 없이 **gap 미인증**을 유지한다.

원 \(J\)와 원자 fit의 불확실성, 관측·기체 입력의 적합성, 전체 coupled history는 이번 조건부 수학적 명제 밖에 있다. `Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0`을 유지한다. 실제 부호·margin이 실패하면 원 실패를 보존하며, 새 수치 결과 없이 PASS·PROMOTE를 선언하지 않는다.
