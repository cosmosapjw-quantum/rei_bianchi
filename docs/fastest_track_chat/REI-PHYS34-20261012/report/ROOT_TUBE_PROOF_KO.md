# PHYS34 — 고정 커널의 하단 분지: 유한 폭 근의 존재·유일성·엄격한 순서

**상태: numerically-enclosed + theorem derived. 최종 독립 판정은 별도 대기 중이다.**

이 문서는 실행 전 [하단 유도](../contributions/theory/LOWER_BRANCH_DERIVATION_KO.md)의 충분조건을 실제 [첫 인증서](../evidence/CERTIFICATE_FIRST.json)에 연결한다. [실행 receipt](../evidence/EXECUTION_RECEIPT.json)에 따르면 첫 실행과 [복원 replay](../evidence/CERTIFICATE_REPLAY.json)는 각각 25/25 recorded checks를 통과했고 원시 결과의 byte identity도 일치했다. 작성자는 이론 후보 기여자이며 독립 decision reviewer가 아니다. 이 문서 작성 과정에서 새 kernel·import·main·root·quadrature·산술 검사를 실행하지 않았다.

## 1. 인증한 명제와 정확한 입력

원 source-real 커널과 아래 두 프로파일을 고정하면, 모든

\[
0\le\delta\le0.001\ \mathrm{eV},\qquad
W\in I_W=[\widehat W-0.25,\widehat W+0.25]\ \mathrm{eV}^2
\tag{R34.1}
\]

에서 하단 패킷의 실현가능성이 유지된다. 각 폭에서 두 응답은 같은 정확한 수준

\[
\boxed{A_-=-3.2582515\times10^{-137}\ \mathrm{s}^{-4}}
\tag{R34.2}
\]

을 갖는 근 \(W_{-,u}(\delta),W_{-,p}(\delta)\)를 각각 하나씩 **이 tube 안에** 갖는다. \(\delta=0\)에서는 두 근이 같고, 모든 \(0<\delta\le0.001\) eV에서는 \(W_{-,p}<W_{-,u}\)다. 아래에서 존재·유일성과 엄격한 부등호를 별도로 증명하고, 차이의 전 구간 enclosure를 제시한다.

정확한 기하 상수는

\[
a=13.61,\quad b=24.58,\quad m=18,\quad
L=m-a=4.39,\quad R=b-m=6.58\quad(\mathrm{eV}),
\]
\[
s=-1,\qquad d=0.001\ \mathrm{eV},\qquad
\eta=0.25\ \mathrm{eV}^2.
\tag{R34.3}
\]

\(\widehat W\)는 원 PHYS29 JSON의 `constants.stored_PHYS26_root_strings.lower_root` 전체 문자열이다.

```text
23.42021899235339297211351479315057454874081817054292481189118799276998028222045968598367218051982929113154658725620727981626004744285172054408046783979559490765
```

수준 R34.2의 원 키는 `second_order.jet_chain.lower_root.response_s-4`다. 상단 수준, 별도 scalar 계산의 응답, 저장된 다른 residual 또는 0을 사용하지 않았다. \(\widehat W\)를 정확한 근으로 가정하지 않고 §5에서 실제 잔차를 감쌌다. `lower`는 상속한 극값 분지 이름이다.

커널은

\[
\mathscr D=E\partial_E,\qquad
k(E)=\mathcal P(\mathscr D^2+3\mathscr D)
\{\sigma_{\rm HI}(E)[J_x+J_w(E-\chi)]\},
\]
\[
\mathcal P=\frac{q_{\rm src}N_0c_{\rm light}n_H(1-x_{HII})}{180}
\tag{R34.4}
\]

이다. \(q_{\rm src}\)는 원 정규화 상수이며 아래 혼합확률 \(q\)와 구별한다. 원 binary64 리터럴의 값은 정확한 유리수로, 원 \(J\)의 직렬화 문자열 및 선언한 기하·A는 지정된 정확한 십진 유리수로 해석한다. 그 위의 정확한 실수 함수가 대상이다. 저장 rounded prefactor나 native binary64 산술 순서로 의미를 바꾸지 않는다. \(c_{\rm light}\), proper seconds와 기존 \((-,+,+,+)\) convention을 유지한다. \(k,F,A\)의 단위는 s⁻⁴, \(W\)는 eV²다.

원 입력 identity와 이 의미는 [고정 계약](../PHYSICS_CONTRACT.json), 인증서의 `source_constants`, `Jx`, `Jw`, `A`, `stored_W` 및 `pinned_source_identities`, `frozen_J_strings`, `same_exact_nonzero_A` 검사에 연결된다. 이 명제는 원 J나 원자 fit의 물리적 불확실성을 감싸는 명제가 아니다.

## 2. 실제 분산과 전 tube의 지원

프로파일은 \([-1,1]\)에서

\[
h_u(z)=\frac12,\qquad
h_p(z)=\frac{35z^4-30z^2+11}{16}
=\frac{1+P_4(z)}2
\tag{R34.5}
\]

이며 정규화된 양의 짝함수다. 공통 이차 모멘트는 \(\mu_2=1/3\)이다. \(d\alpha=h_\alpha(z)dz\)는 폭·분산에서 독립인 고정 확률측도다.

\[
r=R-\delta,\quad V=W-\mu_2\delta^2,\quad
e_\delta=b-\delta=m+r,\quad
x_{\delta,W}=m-\frac Vr,
\]
\[
p=\frac{V}{r^2+V},\qquad q=\frac{r^2}{r^2+V}.
\tag{R34.6}
\]

두 중심의 평균 이동은 \(pr-qV/r=0\), 중심 분산은 \(pr^2+qV^2/r^2=V\)다. 평균 0인 독립 프로파일 변위 \(\delta Z\)를 더하면 전체 평균은 \(m\), 실제 분산은 \(V+\mu_2\delta^2=W\)다. 따라서 같은 W에서 두 프로파일은 같은 중심과 가중치를 사용한다.

\[
F_\alpha(\delta,W)=
p\int k(e_\delta+\delta z)d\alpha(z)
+q\int k(x_{\delta,W}+\delta z)d\alpha(z).
\tag{R34.7}
\]

인증서의 `full_tube_feasibility`는 정확한 유리수 비교로

\[
d<\min(L,R),\qquad
\mu_2d^2<\widehat W-\eta,\qquad
\widehat W+\eta<(R-d)(L-d)
\tag{R34.8}
\]

를 충족했다. 따라서 전 직사각형에서
\(0<V<(R-\delta)(L-\delta)\), \(p,q>0\),
\(a+\delta<x_{\delta,W}<m<e_\delta=b-\delta\)다.

전체 endpoint 패킷은 \([b-2d,b]\), 내부 패킷은

\[
\left[
m-\frac{\widehat W+\eta}{R-d}-d,
\quad
m-\frac{\widehat W-\eta-\mu_2d^2}{R}+d
\right]
\tag{R34.9}
\]

에 포함된다. `packet_and_slope_domain_coverage`는 이 두 패킷의 정확한 유리수 끝점을 보존하고, 둘 다

\[
\boxed{J=[14.35,24.58]\ \mathrm{eV}}
\tag{R34.10}
\]

안에 있음을 확인했다. 같은 z에서 두 패킷 에너지 사이의 모든 점
\((1-t)e_\delta+t x_{\delta,W}+\delta z\)도 J에 속한다. 이는 두 패킷의 같은 z 점을 잇는 볼록 결합이기 때문이다. 아래 기울기 적분과 중심 이동에 쓰는 전체 경로가 이 범위에 들어간다.

## 3. 새 하단 구간 전체의 도함수 enclosure

PHYS33에서 고정한 exact Fraction 표현을 byte identity를 유지하여 재사용했다. 프로파일 변수 z와 구별하여
\(\zeta=\sqrt{E/B_0}\), \(B_0=E_0y_a\)라고 쓰면

\[
k^{(n)}(E)=\frac{C_{\rm pref}}{4(2B_0)^n}
\zeta^{P-11-2n}(1+\zeta)^{-P-2-n}Q_n(\zeta),
\qquad 0\le n\le4,
\tag{R34.11}
\]

이고 \(C_{\rm pref}>0\), \(\deg Q_n\le8+n\le12\)다. 비다항식 인자는 양수이며 다항식 계수는 정확한 유리수다.

인증서 `certificate.covering.z_domain`의 두 outward sqrt 끝점을 정확한 유리수 \(\zeta_-,\zeta_+\)로 해석하고, 각 차수에서 32개 exact cell

\[
\left[\zeta_-+\frac i{32}(\zeta_+-\zeta_-),
\zeta_-+\frac{i+1}{32}(\zeta_+-\zeta_-)\right],
\qquad i=0,\ldots,31
\tag{R34.12}
\]

을 사용했다. 각 cell의 Bernstein 계수 최소·최대가 다항식의 연속 범위를 덮고, 별도의 outward Decimal 인자 enclosure와 곱하여 R34.11을 감쌌다. 각 record는 `exact_rational_cell`을 저장한다. 표시·prefactor용으로 다시 확장한 `z_interval`과 이 exact cell은 같은 개념이 아니다. 다항식 bound는 exact cell에, 외부 인자 bound는 이를 포함하는 표시 구간에 적용한다.

`complete_grid_domain_and_cutoff_containment`는 실제 grid가 J를 덮고, 에너지 역상의 양 끝이 H I cutoff \(\operatorname{real64}(13.60)\)보다 크며 He I cutoff \(\operatorname{real64}(24.59)\)보다 작음을 확인했다. 느슨한 \([1,4/3]\) 상자는 포함관계 확인용이다. \(\chi=\operatorname{real64}(13.598434599702)\)는 가열 offset이고 cutoff와 구별한다.

계산은 계약의 90자리 directed Decimal 산술과 ln·exp·sqrt의 outward 확장 의미를 따른다. 비정수 거듭제곱은 exp/log의 enclosure로 구성한다. 따라서 이것은 지정한 Decimal/libmpdec 의미에 조건부인 계산 증명이며 형식증명기에서 산술 구현 자체를 검증했다는 주장은 아니다.

새 인증서의 전 구간 도함수 상·하한을 짧게 바깥쪽으로 단순화하면

| 인증 상수 | 보수적 표시 경계 | 단위 |
|---|---:|---|
| \(m_2\), \(k''\)의 공통 하한 | \(m_2\ge1.14150\times10^{-66}>0\) | s⁻⁴ eV⁻² |
| \(M_2\), \(k''\)의 공통 상한 | \(M_2\le4.49452\times10^{-65}\) | s⁻⁴ eV⁻² |
| \(m_4\), \(k^{(4)}\)의 공통 하한 | \(m_4\ge1.28077\times10^{-67}>0\) | s⁻⁴ eV⁻⁴ |
| \(M_4\), \(k^{(4)}\)의 공통 상한 | \(M_4\le8.10157\times10^{-66}\) | s⁻⁴ eV⁻⁴ |

여기서 \(m_2\le k''\le M_2\), \(m_4\le k^{(4)}\le M_4\)가 J의 모든 점에서 성립한다. \(M_1\)은 `certificate.root_tube.M1`의 원 90자리 \(\sup_J|k'|\) 상계다. 상단 구간의 수치 상수를 복사한 결과가 아니다.

이 문서의 짧은 숫자는 **각 원시 interval을 독립적으로 바깥쪽으로 단순화한 표시값**이다. 이후 margin·근 이탈·근 차이 계수도 원 90자리 계산 결과를 각각 단순화한다. 이 표의 짧은 m₂, M₂ 등을 다시 조합해 재계산한 값으로 읽으면 안 된다.

## 4. 하단의 역방향 기하와 양의 기울기

폭을 고정하고 \(g(y)=\int k(y+\delta z)d\alpha(z)\), \(e=e_\delta\), \(x=x_{\delta,W}\)로 두자. 하단에서

\[
D=x-e=-\frac{r^2+V}{r}<0,\qquad
p_W=\frac1{D^2},\qquad x_W=-\frac1r,\qquad
qx_W=Dp_W.
\tag{R34.13}
\]

R34.7을 실제 W에 대해 미분하고, \(D\ne0\)인 선분의 적분 항등식을 적용하면

\[
F_{\alpha,W}
=\frac{g(e)-g(x)+Dg'(x)}{D^2}
=\int_0^1t\,g''(e+tD)dt
\]
\[
\boxed{F_{\alpha,W}(\delta,W)
=\int_0^1t\int
k''((1-t)e_\delta+t x_{\delta,W}+\delta z)
\,d\alpha(z)dt.}
\tag{R34.14}
\]

역방향의 \(D<0\)가 추가 음의 부호를 만들지 않는다. 적분 가중치 t는 비음수이고 \(\int_0^1t\,dt=1/2\)이므로 전 tube에서

\[
\boxed{0<\kappa:=m_2/2\le F_{\alpha,W}\le K:=M_2/2,}
\tag{R34.15}
\]
\[
\kappa\ge5.70750\times10^{-67},\qquad
K\le2.24726\times10^{-65}
\quad(\mathrm{s}^{-4}\mathrm{eV}^{-2}).
\tag{R34.16}
\]

따라서 모든 허용 폭에서 각 응답은 W에 대해 엄격히 증가한다. 이 bound는 root 근방의 표본 기울기나 방향 부호의 추정에 의존하지 않는다.

## 5. 정확한 A 잔차, 균일 이동, 유일근 존재

정확한 저장 중심에서

\[
x_0=m-\frac{\widehat W}{R},\quad
p_0=\frac{\widehat W}{R^2+\widehat W},\quad
q_0=\frac{R^2}{R^2+\widehat W},\quad
F_0(\widehat W)=p_0k(b)+q_0k(x_0).
\tag{R34.17}
\]

인증서는 이 \(x_0,p_0,q_0\)를 정확한 유리수로 저장한다. 과거 rounded `u_zero`는 별도 표현 대조의 보존 노드로만 쓰며, 이 정확한 잔차의 중심을 대체하지 않았다. 원 `zero_width_residual.residual_s-4`는

\[
\boxed{F_0(\widehat W)-A_-\in
[-1.396128542248\times10^{-142},
 -1.396128540852\times10^{-142}]\ \mathrm{s}^{-4}.}
\tag{R34.18}
\]

즉 작은 음의 잔차를 그대로 보존했다. 원 상계는
\(\epsilon_r=1.396128542248\times10^{-142}\) s⁻⁴이며, 짧게는 \(\epsilon_r\le1.39613\times10^{-142}\) s⁻⁴다.

W를 \(\widehat W\)에 고정하면

\[
p_\delta'=
\frac{2(R-\delta)(\widehat W-\mu_2R\delta)}
{[(R-\delta)^2+\widehat W-\mu_2\delta^2]^2}.
\tag{R34.19}
\]

`profile_probability_monotonicity`는 \(\widehat W>\mu_2Rd\)를 확인했다. 따라서 \(p_0\le p_\delta\le p_d\), \(q_\delta\le q_0\)다. 중심 이동은

\[
x_\delta-x_0
=-\frac{\widehat W\delta/R-\mu_2\delta^2}{R-\delta},\qquad
|x_\delta-x_0|\le D_x:=
\frac{\widehat Wd}{R(R-d)}+\frac{\mu_2d^2}{R-d}.
\tag{R34.20}
\]

평균 0인 프로파일의 평활화 오차는 \(\mu_2M_2\delta^2/2\) 이하이고, 가중치·중심 이동을 분리하면 두 프로파일에 공통으로

\[
|F_\alpha(\delta,\widehat W)-F_0(\widehat W)|\le B_{\rm disp},
\]
\[
\boxed{B_{\rm disp}=(p_d-p_0)|k(b)-k(x_0)|
+M_1[p_dd+q_0D_x]+\frac{\mu_2M_2d^2}{2}.}
\tag{R34.21}
\]

계산에서는 \(|k(b)-k(x_0)|\)도 원 outward enclosure로 덮었다. 각 항의 전 폭 상계를 사용하므로 이는 \(0\le\delta\le d\) 전체에 대한 부등식이다. 프로파일 오차는 \(p+q=1\)이므로 두 배 하지 않는다.

실제 `root_tube` 결과에서

\[
B_{\rm disp}\le9.73485\times10^{-68}\ \mathrm{s}^{-4},
\]
\[
\boxed{\mathcal M:=\kappa\eta-(B_{\rm disp}+\epsilon_r)
\ge4.53392\times10^{-68}\ \mathrm{s}^{-4}>0.}
\tag{R34.22}
\]

margin은 원 90자리 경계로 계산한 값의 독립적인 바깥 표시다. 표시용 짧은 \(\kappa\)와 \(B_{\rm disp}\)를 다시 빼서 R34.22를 만든 것이 아니다.

R34.15, R34.18, R34.21–22를 결합하면

\[
F_\alpha(\delta,\widehat W-\eta)-A_-
\le B_{\rm disp}+\epsilon_r-\kappa\eta<0,
\]
\[
F_\alpha(\delta,\widehat W+\eta)-A_-
\ge-(B_{\rm disp}+\epsilon_r)+\kappa\eta>0.
\tag{R34.23}
\]

연속성과 엄격한 단조성에서 모든 \(\delta\in[0,d]\), 두 프로파일 각각에 대해 tube 내부의 유일근이 존재한다. 원 `rho_all_widths_eV2`와 `root_error_at_zero_eV2`를 바깥으로 표시하면

\[
\boxed{|W_{-,\alpha}(\delta)-\widehat W|
\le0.170563\ \mathrm{eV}^2<\eta,}
\tag{R34.24}
\]
\[
\boxed{|W_{-,\alpha}(0)-\widehat W|
\le2.44613\times10^{-76}\ \mathrm{eV}^2.}
\tag{R34.25}
\]

이 값들은 고정된 수학적 입력과 정확한 A에 대한 거리 경계다. 입력 원자물리의 오차 수준이나 관측적 정밀도를 나타내지 않는다. 근 탐색 없이 잔차, 기울기, 균일 이동 bound로 얻은 결과다.

## 6. 정확한 Peano 표현과 엄격한 하단 근 순서

\(Q(z)=(1-z^2)^4\)라 두면
\(h_p-h_u=Q^{(4)}/768\)이고, \(Q\)의 0–3차 도함수는 두 끝점에서 0이다. 네 번 부분적분과
\(\int_{-1}^1Qdz=256/315\)에서

\[
d\pi(z)=\frac{315}{256}(1-z^2)^4dz,\qquad
\int d\pi=1,
\]
\[
\boxed{\int k(y+\delta z)(h_p-h_u)(z)dz
=\frac{\delta^4}{945}\int k^{(4)}(y+\delta z)d\pi(z).}
\tag{R34.26}
\]

이는 모든 허용 유한 폭에서 정확한 등식이다. Taylor leading term만 남긴 근사가 아니며, 하단 sign은 네 번 부분적분의 부호를 바꾸지 않는다. 공통 중심과 가중치로 두 패킷을 합하면

\[
F_p-F_u=\frac{\delta^4}{945}\mathcal S_-(\delta,W),\qquad
m_4\le\mathcal S_-\le M_4.
\tag{R34.27}
\]

이미 존재하는 두 근의 차이 \(\Delta W_-=W_{-,p}-W_{-,u}\)에 대해

\[
\overline C_p=\int_0^1F_{p,W}
(\delta,W_{-,u}+t\Delta W_-)dt,\qquad
\kappa\le\overline C_p\le K
\]

이며 같은 정확한 A를 빼면

\[
\boxed{\Delta W_-=-\frac{\delta^4}{945}
\frac{\mathcal S_-(\delta,W_{-,u})}{\overline C_p}.}
\tag{R34.28}
\]

따라서 전체 폭 구간에서

\[
-\frac{M_4}{945\kappa}\delta^4
\le\Delta W_-
\le-\frac{m_4}{945K}\delta^4<0
\qquad(0<\delta\le d).
\tag{R34.29}
\]

실제 원 90자리 결과 `root_tube.C_small_eV-2.lower`와 `root_tube.C_large_eV-2.upper`는 각각 다음과 같다.

```text
C_small lower = 0.00000603100414910888806864116549414496748781073892734106621135499565605159662653190320249946372
C_large upper = 0.0150207115379994898192777529771811420932273191675592128119683619930760157671092136945503380
```

\(C_{\rm small}=m_4/(945K)\)의 하한을 더 작게, \(C_{\rm large}=M_4/(945\kappa)\)의 상한을 더 크게 단순화하여 얻는 보수적 표시가

\[
\boxed{-0.0150208\,\delta^4
\le W_{-,p}(\delta)-W_{-,u}(\delta)
\le-0.00000603100\,\delta^4<0,
\quad0<\delta\le0.001\ \mathrm{eV}.}
\tag{R34.30}
\]

이다. **두 짧은 계수는 원 `C_small/C_large` interval을 바깥으로 단순화한 값이며, §3–4의 짧게 표시한 m₂·M₂·m₄·M₄·κ·K로 다시 계산한 값이 아니다.** 두 계수의 단위는 eV⁻², \(\delta\)는 eV다. 특히 \(\delta=0.001\) eV에서

\[
\boxed{-1.50208\times10^{-14}
\le W_{-,p}-W_{-,u}
\le-6.03100\times10^{-18}\quad\mathrm{eV}^2.}
\tag{R34.31}
\]

이 구간은 실제 차이를 포함하는 보수적인 범위이며 여러 유효숫자를 갖는 점 예측값이 아니다. \(\delta=0\)에서는 두 프로파일 응답이 동일하므로 유일근도 일치한다.

## 7. 실행 근거와 해석 경계

원시 인증서는 새로운 하단 구간의 연속 부호, 전 tube feasibility·coverage, 확률 단조성, 잔차, root margin, 엄격한 근 순서 조건을 충족했다. 보존 b·u_zero 두 노드에서 ordinary-energy Taylor 표현과 0·1·2·4차의 8개 enclosure를 대조했다. 이 점별 대조는 구현 오류 탐지용이며 Bernstein에 의한 연속 구간 증명을 대신하지 않는다.

[복원 receipt](../evidence/RESTORATION_RECEIPT.json)는 별도 디렉터리로 풀어 frozen hash를 확인한 과정을 보존한다. 실행 receipt는 첫 실행과 replay의 25/25 결과, 실제 종료코드 0, 원시 결과 SHA256 `9b576de7e6079b5a9a3352f6049f550fde13646dda8a1d36022febcf6e11ccf4`의 일치를 기록한다. 각 실행은 Bernstein/prefactor 상자 170개, 독립 표현 joint jet 2개, zero-width residual 1개를 사용했다. physical root search·finite-width quadrature·과거 과학 main·일반 산술 검사 반복·NCP 실행은 0이다. 첫 실행 1회와 복원 replay 1회의 허용 예산은 소진했으며, 이 보고서가 추가 실행을 만들지 않았다.

같은 호스트·같은 Decimal backend에서의 replay와 표현 대조는 독립 물리 데이터 또는 별도 산술 backend 검증이 아니다. 원시 JSON의 `claim_ceiling.lower_branch=TARGET_NOT_YET_EVALUATED`는 immutable pre-run 계약 snapshot의 복사다. 실제 실행 결과는 별도 `status`, `checks`, `certificate` 및 실행 receipt에 기록되어 있다. 원시 계약·결과를 사후 수정하지 않고 이 의미를 구별한다. 후속 독립 decision과 최종 상태 문서가 판정 상태를 별도로 기록한다. 이 문서는 그 독립 판정을 선점하지 않는다.

인증 범위는 **고정 source-real 커널, 지정 하단 tube, 지정 프로파일 쌍과 정확한 하단 A**다. 원 J·원자 fit의 불확실성은 unresolved이며 physical admission은 **HOLD**다. 상단 결과를 재실행하지 않았고, 두 분지 gap은 **NOT_CERTIFIED**다. 개별 근 이동이 모두 음수라고 해도 그 차이의 부호는 결정되지 않는다. 상단과 하단의 보존 A가 서로 다르므로 이번 결과를 같은 A에서의 분지 간 비교로 바꿀 수도 없다.

`Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0`을 유지한다. 이 제한된 수학적 근 정리는 전체 coupled history나 물리 데이터의 승격을 뜻하지 않는다.
