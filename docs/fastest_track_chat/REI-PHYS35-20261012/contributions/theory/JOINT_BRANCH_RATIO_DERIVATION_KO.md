# PHYS35: 두 고정 수준에서의 프로파일 근 이동 비교 유도

## 0. 기여의 지위와 비교 대상

이 문서는 `JOINT_BRANCH_PROFILE_DISPLACEMENT_COMPARISON`의 **이론 기여**다. PHYS33·PHYS34가 이미 인증한 커널 구간과 근 존재 정리를 재사용하여, 두 프로파일 근 이동의 차이를 인증하기에 충분한 정확한 부등식을 유도한다. 작성자는 후보 유도에 참여했으며 최종 독립 판정자가 아니다. 이 문서 작성 작업에는 과학 모듈 import, 커널·도함수 평가, 새 Bernstein 계산, 초월함수 평가, 수치 후보 생성, quadrature, 근 탐색, main 또는 과거 기초검사의 실행이 없다. 이 기여 시점의 새 상대 부호는 **NOT_RUN / NOT_CERTIFIED**이며, 이후 고정 계약에 따른 실행 증거와 별도 최종 결정이 그 상태를 정한다.

연속성의 기준은 [PHYS35 인계](../../intake/prior_PHYS34/next/PHYS35_NEXT_HANDOFF_KO.md), 보존한 [상단 최종 상태](../../inputs/PHYS33/state/FINAL_STATE.md), [하단 최종 상태](../../inputs/PHYS34/state/FINAL_STATE.md), 그리고 [입력 manifest](../../SOURCE_MANIFEST.json)다. 개별 분지의 과거 승인을 새 비교 부호의 승인으로 옮겨 적지 않는다. 과거 raw의 `claim_ceiling`은 해당 실행 전 계약의 불변 snapshot이며, 당시 실제 결과와 채택 여부는 checks·certificate·FINAL_STATE·별도 decision에서 읽는다.

| 분지 \(s\) | \(R_s\), eV | \(e_{s,0}\), eV | 정확한 \(A_s\), s⁻⁴ | 저장 \(\widehat W_s\) 키 |
|---|---:|---:|---:|---|
| 상단 \(s=+1\) | 4.39 | 13.61 | −2.2748589E−137 | `constants.stored_PHYS26_root_strings.upper_root` |
| 하단 \(s=-1\) | 6.58 | 24.58 | −3.2582515E−137 | `constants.stored_PHYS26_root_strings.lower_root` |

수준의 원 키는 각각 `second_order.jet_chain.upper_root.response_s-4`와 `second_order.jet_chain.lower_root.response_s-4`이며, 입력은 [PHYS29 원 JSON](../../inputs/PHYS29_SECOND_ORDER_FIRST.json)이다. \(\widehat W_s\)는 해당 저장 문자열 **전체**를 정확한 십진 유리수로 읽는다. 저장 중심을 정확한 근으로 가정하지 않는다.

비교량은

\[
G_\alpha(\delta;A_-,A_+)
=W_{-,\alpha}(\delta;A_-)-W_{+,\alpha}(\delta;A_+),
\qquad \alpha\in\{u,p\}.
\tag{T35.1}
\]

이는 지정한 **서로 다른 두 수준에서의 root separation**이다. 공통 \(A\)에서 두 분지를 비교하는 명제로 바꾸지 않는다. 같은 분지의 두 프로파일 차이를 취할 때에만 그 분지의 \(A_s\)가 소거된다. 이하

\[
a=13.61,\quad b=24.58,\quad m=18,\quad
d=0.001\ {\rm eV},\quad \eta=0.25\ {\rm eV}^2,
\]
\[
0\le\delta\le d,\qquad
W\in\mathcal T_s=[\widehat W_s-\eta,\widehat W_s+\eta],
\qquad \mu_2=\frac13
\tag{T35.2}
\]

를 유지한다. 상단·하단의 기존 보간 에너지 영역은 각각

\[
J_+=[13.61,22],\qquad J_-=[14.35,24.58]\quad({\rm eV})
\tag{T35.3}
\]

이다. 실제 covering은 이 선언 영역을 덮는, 원 sqrt 구간 끝점에서 정한 정확한 유리수 grid다.

## 1. 원 커널과 재사용의 조건

대상은 전작과 같은 source-real 커널

\[
\mathscr D=E\partial_E,\qquad
k(E)=\mathcal P(\mathscr D^2+3\mathscr D)
\{\sigma_{\rm HI}(E)[J_x+J_w(E-\chi)]\},
\]
\[
\mathcal P=\frac{q_{\rm src}N_0c_{\rm light}n_H(1-x_{HII})}{180}.
\tag{T35.4}
\]

source binary64 리터럴은 그 binary64 값을 나타내는 정확한 유리수로, 직렬화된 \(J\), 선언 기하 및 \(A_s\)는 지정한 정확한 십진 유리수로 해석한다. 그 위의 정확한 실수 함수를 다룬다. 저장 rounded prefactor나 native 연산 순서로 의미를 변경하지 않는다. \(c_{\rm light}\), proper seconds와 기존 \((-,+,+,+)\) convention도 보존한다. \(q_{\rm src}\)는 아래 혼합확률 \(q_s\)와 다르다. [상단 계약](../../inputs/PHYS33/PHYSICS_CONTRACT.json)과 [하단 증명](../../inputs/PHYS34/report/ROOT_TUBE_PROOF_KO.md)에 이 의미가 고정되어 있다.

H I cutoff \(\operatorname{real64}(13.60)\), He I cutoff \(\operatorname{real64}(24.59)\), 가열 offset \(\chi=\operatorname{real64}(13.598434599702)\)는 서로 다른 상수다. old covering의 에너지 역상과 실제 패킷이 해당 cutoff 사이에 있다는 전작의 의무를 유지한다. 느슨한 유리수 \(\zeta\) containing box 전체에 커널 식을 물리적으로 연장하지 않는다.

재사용하는 수치 증거는 [PHYS33 raw](../../inputs/PHYS33/evidence/CERTIFICATE_FIRST.json)와 [PHYS34 raw](../../inputs/PHYS34/evidence/CERTIFICATE_FIRST.json)의 **저장된 outward enclosure**다. 두 입력의 커널·\(J\)·상수 identity가 동일해야 한다. source identity가 달라지면 이 증거를 새 커널에 사용할 수 없다.

전작에서 다음을 이미 확보했다.

1. 각 \(s,\alpha\)와 모든 \(\delta\in[0,d]\)에서 \(F_{s,\alpha}(\delta,W)=A_s\)의 근이 \(\mathcal T_s\) 안에 유일하게 존재한다.
2. 전 tube의 실제 패킷 및 필요한 보간 선분이 \(J_s\) 안에 있다.
3. \(J_s\)를 덮는 covering에서 \(k''>0\), \(k^{(4)}>0\)와 \(k^{(3)}\)를 포함한 저장 도함수 범위가 있다.
4. 양의 폭에서 각 분지 안의 \(W_{s,p}<W_{s,u}\)가 성립한다.

근거는 [상단 근 tube 증명](../../inputs/PHYS33/report/ROOT_TUBE_PROOF_KO.md), [하단 근 tube 증명](../../inputs/PHYS34/report/ROOT_TUBE_PROOF_KO.md) 및 각 final decision이다. 이번 비교는 이 고정 범위를 재사용한다. 원 residual·근 탐색·전역 도함수 검사를 반복할 필요가 없다.

## 2. 실제 \(W\)와 공통 부호 패킷 기하

프로파일은 \([-1,1]\)에서

\[
h_u(z)=\frac12,\qquad
h_p(z)=\frac{35z^4-30z^2+11}{16}.
\tag{T35.5}
\]

두 확률측도 \(d\alpha=h_\alpha(z)dz\)는 모두 짝함수이며 평균 0, 두 번째 모멘트 \(\mu_2=1/3\)을 갖는다. 공통 \(\mu_2\) 때문에 아래 중심·확률은 두 프로파일에서 동일한 실제 분산 \(W\)에 대응한다.

\[
r_s=R_s-\delta,\qquad V=W-\mu_2\delta^2,
\]
\[
e_s=m-sr_s=e_{s,0}+s\delta,\qquad
x_s=m+s\frac{V}{r_s},
\]
\[
p_s=\frac{V}{r_s^2+V},\qquad
q_s=1-p_s=\frac{r_s^2}{r_s^2+V}.
\tag{T35.6}
\]

\(r_s>0,V>0\)는 기존 feasible tube의 조건이다. 두 중심의 혼합평균은 \(m\), 중심 사이의 분산은 \(V\), 패킷 내부의 분산은 \(\mu_2\delta^2\)이므로 전체 분산은 정확히 \(W\)다.

\[
F_{s,\alpha}(\delta,W)
=p_s\int k(e_s+\delta z)\,d\alpha(z)
 +q_s\int k(x_s+\delta z)\,d\alpha(z).
\tag{T35.7}
\]

다음은 이후 모든 bound에 사용할 단순한 정확 유리수 상자다.

\[
W_s^L=\widehat W_s-\eta,\quad W_s^U=\widehat W_s+\eta,
\qquad V_s^L=W_s^L-\mu_2d^2.
\tag{T35.8}
\]

중심 구간 \([x_s^L,x_s^U]\)를

\[
[x_+^L,x_+^U]
=\left[m+\frac{V_+^L}{R_+},\;
         m+\frac{W_+^U}{R_+-d}\right],
\]
\[
[x_-^L,x_-^U]
=\left[m-\frac{W_-^U}{R_--d},\;
         m-\frac{V_-^L}{R_-}\right]
\tag{T35.9}
\]

로 잡으면 실제 \(x_s(\delta,W)\)를 포함한다. 이 상자는 \(\delta,W\)의 상관을 버리는 대신 기존 feasible tube 조건만으로 성립한다. 전체 패킷의 에너지 구간은

\[
I_{e,+}=[a,a+2d],\qquad I_{e,-}=[b-2d,b],\qquad
I_{x,s}=[x_s^L-d,x_s^U+d]
\tag{T35.10}
\]

로 잡을 수 있다. 이는 프로파일 \(u,p\)뿐 아니라 §3의 Peano 확률측도 지원도 덮는다.

\(V/(r^2+V)\)는 \(r>0\)에 관해 감소하고 \(V>0\)에 관해 증가하므로

\[
p_s^L=\frac{V_s^L}{R_s^2+V_s^L},\qquad
p_s^U=\frac{W_s^U}{(R_s-d)^2+W_s^U},\qquad
p_s\in[p_s^L,p_s^U]\subset(0,1).
\tag{T35.11}
\]

이 식은 \(p_s\)의 \(\delta\) 단조성을 새로 가정하지 않는다. 더 좁은 단조성 경계를 사용한다면 그 추가 부호 조건과 선택을 계약에서 따로 고정해야 한다.

## 3. exact Peano 식과 근 이동의 정확한 비율

\[
Q(z)=(1-z^2)^4,\qquad
h_p-h_u=\frac{Q^{(4)}(z)}{768},\qquad
d\pi(z)=\frac{315}{256}Q(z)\,dz.
\tag{T35.12}
\]

\(\pi\)는 \([-1,1]\)의 확률측도다. \(Q,Q',Q'',Q'''\)가 양 끝에서 모두 0이므로 네 번 부분적분하면, 패킷 지원에서 \(k\in C^4\)일 때

\[
\int k(y+\delta z)[h_p(z)-h_u(z)]\,dz
=\frac{\delta^4}{945}\int k^{(4)}(y+\delta z)\,d\pi(z).
\tag{T35.13}
\]

편의상

\[
A_{e,s}=\int k^{(4)}(e_s+\delta z)\,d\pi(z),\qquad
A_{x,s}=\int k^{(4)}(x_s+\delta z)\,d\pi(z),
\]
\[
\mathcal S_s(\delta,W)=p_sA_{e,s}+(1-p_s)A_{x,s}
\tag{T35.14}
\]

로 쓰면 정확히

\[
F_{s,p}(\delta,W)-F_{s,u}(\delta,W)
=\frac{\delta^4}{945}\mathcal S_s(\delta,W).
\tag{T35.15}
\]

기존 근 존재를 사용하여

\[
\Delta W_s=W_{s,p}-W_{s,u},\qquad
\overline C_{s,p}
=\int_0^1 F_{s,p,W}
(\delta,W_{s,u}+\theta\Delta W_s)\,d\theta
\tag{T35.16}
\]

로 두면 같은 \(A_s\)에서

\[
\boxed{\displaystyle
\Delta W_s=-\frac{\delta^4}{945}
\frac{\mathcal S_s(\delta,W_{s,u})}{\overline C_{s,p}}.}
\tag{T35.17}
\]

두 근을 잇는 \(W\) 선분은 기존 tube 안에 있다. 따라서 \(\mathcal S_s\)와 \(F_{s,p,W}\)의 **전 tube 경계**만으로 비율을 감쌀 수 있다. 새 근 좌표를 계산할 필요가 없다.

## 4. 역방향 선분을 포함하는 기울기 항등식

\[
g_{\alpha,\delta}(y)=\int k(y+\delta z)\,d\alpha(z),\qquad
D_s=x_s-e_s=s\frac{r_s^2+V}{r_s}.
\tag{T35.18}
\]

고정 \(\delta\)에서 \(p_{s,W}=1/D_s^2\), \(q_sx_{s,W}=D_sp_{s,W}\)다. 그러므로

\[
F_{s,\alpha,W}
=\frac{g_{\alpha,\delta}(e_s)-g_{\alpha,\delta}(x_s)
       +D_sg'_{\alpha,\delta}(x_s)}{D_s^2}
\]
\[
\boxed{\displaystyle
F_{s,\alpha,W}
=\int_0^1t\int
k''((1-t)e_s+tx_s+\delta z)\,d\alpha(z)\,dt.}
\tag{T35.19}
\]

두 번째 등식은 \(g(e_s)\)를 \(x_s\)에서 적분 나머지가 있는 Taylor 식으로 전개한 것이다. 하단에서는 \(D_s<0\)이지만 \(D_s^2\)와 양의 가중치 \(t\)가 남는다. 선분 방향 때문에 기울기에 음수를 추가하지 않는다. \(m_{2,s}\le k''\le M_{2,s}\)라면 기존 \(\kappa_s=m_{2,s}/2\), \(K_s=M_{2,s}/2\)가 따른다. 이번에는 그 검사를 다시 실행하지 않고 저장 결과를 재사용한다.

## 5. 저장 점 세 개로 만드는 기준 기울기

각 분지의 retained node를 \(x_s^{\rm ref}\)라 하자. 상단은 원 `v_star`, 하단은 원 `u_zero`다. 선택한 point record의 정확한 `energy_eV` 값을 읽어 고정한다. 기준 끝점은 \(e_{s,0}\)이며

\[
D_s^{\rm ref}=x_s^{\rm ref}-e_{s,0}\ne0,
\]
\[
C_s^{\rm ref}
=\frac{k(e_{s,0})-k(x_s^{\rm ref})
       +D_s^{\rm ref}k'(x_s^{\rm ref})}{(D_s^{\rm ref})^2}
=\int_0^1t\,k''((1-t)e_{s,0}+tx_s^{\rm ref})\,dt.
\tag{T35.20}
\]

이 항등식에는 \(x_s^{\rm ref}=x_s(0,\widehat W_s)\)라는 가정이 **필요하지 않다**. retained node는 전체 저장 \(\widehat W_s\)에서 재구성한 중심과 자릿수 끝에서 다를 수 있다. 그 불일치는 다음 절의 정확한 거리 \(H_{c,s}\)가 포함한다.

입력 endpoint enclosure를

\[
k(e_{s,0})\in[K_e^L,K_e^U],\quad
k(x_s^{\rm ref})\in[K_x^L,K_x^U],\quad
k'(x_s^{\rm ref})\in[K_1^L,K_1^U]
\]

라 쓰고 \(D=D_s^{\rm ref}\)로 약기하면

\[
N^L=K_e^L-K_x^U+\min(DK_1^L,DK_1^U),\qquad
N^U=K_e^U-K_x^L+\max(DK_1^L,DK_1^U),
\]
\[
C_s^{{\rm ref},L}=\frac{N^L}{D^2},\qquad
C_s^{{\rm ref},U}=\frac{N^U}{D^2}.
\tag{T35.21}
\]

이 일반식은 하단 \(D<0\)의 구간 곱 순서를 처리한다. point record의 `primary` outward enclosure를 일관되게 선택하면 새 커널 평가가 없다.

**점 identity 의무:** `zero_width_residual.kc`가 exact \(\widehat W_s\)에서 재구성한 중심의 값이라면 retained node의 \(k'\)와 같은 점의 자료로 혼용할 수 없다. 우선 경로는 원 `independent_expression_comparisons`의 동일한 `energy_eV`에서 얻은 order 0과 order 1 `primary` 값을 함께 읽는 것이다. 서로 다른 점을 섞으려면 별도의 명시적 Lipschitz bridge가 필요하며 이번 경로에는 불필요하다.

## 6. 전 tube의 기울기를 감싸는 개선된 오차식

중심 상자 (T35.9)에서

\[
H_{c,s}=\max\{|x_s^L-x_s^{\rm ref}|,\,
                 |x_s^U-x_s^{\rm ref}|\}
\tag{T35.22}
\]

를 정의한다. 이는 **패킷 중심의 거리**다. 패킷 반폭 \(d\)를 여기에 다시 더하지 않는다. 내부 프로파일 이동은 짝함수 Taylor 항이 별도로 처리한다.

전작 저장 범위에서

\[
M_{3,s}\ge\sup_{J_s}|k^{(3)}|,\qquad
M_{4,s}\ge\sup_{J_s}|k^{(4)}|
\tag{T35.23}
\]

를 취한다. 필요하면 저장 전체 grid의 더 넓은 유효 영역에 대한 같은 bound를 써도 된다. 실제 패킷, 기준점, 두 선분의 convex hull이 그 유효 영역 안에 있어야 한다.

\(y=(1-t)e_s+tx_s\), \(y_0=(1-t)e_{s,0}+tx_s^{\rm ref}\)라 하면

\[
|y-y_0|\le(1-t)\delta+tH_{c,s}.
\]

평균값 정리와 \(\int_0^1t(1-t)dt=1/6\), \(\int_0^1t^2dt=1/3\)에 의해

\[
\left|\int_0^1t[k''(y)-k''(y_0)]\,dt\right|
\le M_{3,s}\left(\frac d6+\frac{H_{c,s}}3\right).
\tag{T35.24}
\]

다음으로 \(k''(y+\delta z)\)를 \(y\)에서 2차 적분 나머지까지 전개한다. \(\int z\,d\alpha=0\) 때문에 1차 항은 사라지고

\[
\left|\int k''(y+\delta z)\,d\alpha-k''(y)\right|
\le\frac{M_{4,s}\mu_2\delta^2}{2}.
\]

\(\int_0^1t\,dt=1/2\)를 적용하면

\[
\boxed{\displaystyle
|F_{s,\alpha,W}(\delta,W)-C_s^{\rm ref}|
\le\mathcal E_s
:=
M_{3,s}\left(\frac d6+\frac{H_{c,s}}3\right)
+\frac{\mu_2M_{4,s}d^2}{4}.}
\tag{T35.25}
\]

이는 \(u,p\) 모두에, 기존 **전체** \(\delta,W\) tube에서 균일하다. \(k^{(5)}\)가 필요하지 않다. 양의 가중치와 절댓값을 사용하므로 상단·하단 방향 차이도 없다. 근 사이 평균 \(\overline C_{s,p}\)에도 같은 구간이 적용된다.

따라서

\[
C_s^L=C_s^{{\rm ref},L}-\mathcal E_s,\qquad
C_s^U=C_s^{{\rm ref},U}+\mathcal E_s
\tag{T35.26}
\]

가 유효하다. 계약에서 선택했다면 기존 양의 구간과 교차하여

\[
C_s^L\leftarrow\max(C_s^L,\kappa_s),\qquad
C_s^U\leftarrow\min(C_s^U,K_s)
\tag{T35.27}
\]

로 좁혀도 된다. 비율 계산에는 \(0<C_s^L\le C_s^U\)가 필요하다. 새 산출값 및 gap margin은 여기서 평가하지 않는다.

## 7. 기존 cell을 패킷에 맞춰 재사용하는 \(k^{(4)}\) 경계

전작 좌표를 \(\zeta=\sqrt{E/B}\), \(B=E_0y_a>0\)로 쓰자. \(\zeta\)는 프로파일 좌표 \(z\in[-1,1]\)와 다르다. \(B\)는 원 source-real 두 상수의 정확한 유리수 곱이다.

PHYS33 원 `certify_upper_branch.py`의 grid 생성은 다음의 정확한 식이다.

\[
\zeta_L=\operatorname{Fraction}({\tt covering.z\_domain.lower}),\quad
\zeta_U=\operatorname{Fraction}({\tt covering.z\_domain.upper}),\quad
n={\tt covering.cells\_per\_order},
\]
\[
\ell_i=\zeta_L+(\zeta_U-\zeta_L)\frac{i}{n},\qquad
u_i=\zeta_L+(\zeta_U-\zeta_L)\frac{i+1}{n},\quad 0\le i<n.
\tag{T35.28}
\]

이 식의 `lower/upper`는 저장 JSON 키다. 원 실행 중 Interval 객체의 `.lo/.hi`와 구별한다. 원 코드는 \(n=32\)인 고정 protocol을 사용했다. PHYS34도 같은 분할 관계를 사용하며 각 record에 `exact_rational_cell`을 보존한다. 새 입력 identity에 원 algorithm identity를 포함하고 PHYS33의 재구성 cell과 label/order 대응을 확인한다. PHYS34는 재구성 값과 기록된 exact cell을 대조할 수 있다.

기존 record의 `z_interval`은 prefactor 계산용 outward Decimal 상자일 수 있다. Bernstein polynomial bound가 증명된 정확한 cell보다 소폭 넓을 수 있으므로 **그 표시 상자만으로 cell의 물리 지원을 확대하지 않는다**. 선택에 사용하는 에너지 cell은

\[
E_i=[B\ell_i^2,Bu_i^2].
\tag{T35.29}
\]

새 sqrt는 필요하지 않다. 각 패킷 구간 \(I=[I^L,I^U]\)에 대해 order 4의 cell 중

\[
B\ell_i^2\le I^U,\qquad Bu_i^2\ge I^L
\tag{T35.30}
\]

를 만족하는 모든 cell을 선택한다. 끝점 접촉도 포함한다. 선택 집합이 비어 있지 않고 그 합집합이 \(I\)를 완전히 덮는다는 의무를 명시한다. 저장 `enclosure`가 \([K_{4,i}^L,K_{4,i}^U]\)이면

\[
k^{(4)}(I)\subseteq
\left[\min_{i\ {\rm selected}}K_{4,i}^L,\,
      \max_{i\ {\rm selected}}K_{4,i}^U\right].
\tag{T35.31}
\]

이 방식으로 각각

\[
k^{(4)}(I_{e,s})\subseteq[\ell_{e,s},u_{e,s}],\qquad
k^{(4)}(I_{x,s})\subseteq[\ell_{x,s},u_{x,s}]
\tag{T35.32}
\]

를 얻는다. \(\pi\)가 양의 확률측도이므로 (T35.14)의 \(A_{e,s},A_{x,s}\)도 같은 구간에 있다.

**point \(k^{(4)}\)만의 한계:** point record는 그 정확한 에너지의 값만 감싼다. 이를 주변 packet 전체의 값으로 간주할 수 없다. point 값에 거리만 곱해 안전한 변동폭을 붙이려면 \(k^{(5)}\) 경계 등 추가 연속성 정보가 필요하다. 기존 order 0–4 증거만 재사용하는 이번 경로는 이미 구간 전체에서 증명된 order 4 cell enclosure를 사용한다. point 자료는 기준점·입력 identity 확인에 유용하지만 새로운 국소 구간 증명을 대신하지 않는다.

## 8. \(q=1-p\)를 보존하는 분자 경계

분자에는 두 패킷의 실제 혼합확률을 유지한다. \(p,q\)를 독립 구간으로 취급하지 않는다. (T35.11), (T35.32)로

\[
\mathcal S_s^L
=\min_{p\in\{p_s^L,p_s^U\}}
\{p\ell_{e,s}+(1-p)\ell_{x,s}\},
\]
\[
\mathcal S_s^U
=\max_{p\in\{p_s^L,p_s^U\}}
\{pu_{e,s}+(1-p)u_{x,s}\}
\tag{T35.33}
\]

를 정의하면

\[
0<\mathcal S_s^L\le\mathcal S_s(\delta,W)\le\mathcal S_s^U.
\tag{T35.34}
\]

양 끝만 검사하면 되는 이유는 \(p\)에 관한 식이 affine이기 때문이다. 실제 \(p\)와 패킷 평균의 상관은 상자화했으므로 보수적이지만 총 혼합질량 \(p+q=1\)은 정확히 보존한다. positivity는 재사용 cell 하한이 양수이고 \(0<p_s^L\le p_s^U<1\)일 때 따른다.

## 9. gap 부호를 닫기에 충분한 정확한 부등식

양의 분지별 변위 계수를

\[
\Gamma_s(\delta)=
\frac{\mathcal S_s(\delta,W_{s,u})}{945\,\overline C_{s,p}}
\tag{T35.35}
\]

로 정의한다. 단위는 eV⁻²이며 \(\Delta W_s=-\delta^4\Gamma_s\)다. (T35.26) 또는 계약에서 고정한 (T35.27), 그리고 (T35.33)으로

\[
L_s=\frac{\mathcal S_s^L}{945C_s^U},\qquad
U_s=\frac{\mathcal S_s^U}{945C_s^L},\qquad
0<L_s\le\Gamma_s\le U_s.
\tag{T35.36}
\]

정확한 gap 식은

\[
G_p-G_u=\Delta W_- -\Delta W_+
=\delta^4(\Gamma_+-\Gamma_-),
\tag{T35.37}
\]

이고 균일한 계수 범위는

\[
\boxed{\displaystyle
L_G=L_+-U_-,\qquad U_G=U_+-L_-,\qquad
L_G\delta^4\le G_p-G_u\le U_G\delta^4.}
\tag{T35.38}
\]

모든 비율에는 \(945\)를 **한 번만** 포함한다. 양의 부호를 인증하기에는

\[
L_G>0
\quad\Longleftrightarrow\quad
\mathcal S_+^LC_-^L-\mathcal S_-^UC_+^U>0
\tag{T35.39}
\]

이면 충분하고, 음의 부호를 인증하기에는

\[
U_G<0
\quad\Longleftrightarrow\quad
\mathcal S_+^UC_-^U-\mathcal S_-^LC_+^L<0
\tag{T35.40}
\]

이면 충분하다. cross-product 식은 양의 분모가 확보된 뒤의 정확한 동치다. 어떤 검사를 목표로 할지는 새 계약에서 고정한다.

성공하면 strict order는 \(0<\delta\le d\) 전체에서 성립한다. \(\delta=0\)에서는 두 프로파일이 같은 점 혼합이므로 \(G_p-G_u=0\)이다. 범위가 겹치면 이 방법으로 부호를 결정하지 못한 것이며 실제 부호가 0이라는 뜻이 아니다. 개별 \(\Delta W_s<0\)만으로 (T35.39)나 (T35.40)가 성립하지는 않는다.

## 10. 정확 유리수 조합으로 가능한 새 인증의 최소 의무

유한 십진수인 기존 enclosure 끝점을 `Fraction`으로 읽으면 다음의 정확한 대수만으로 새 계산을 구성할 수 있다. 정수·유리수 사칙연산, 순서 비교, 제곱, finite min/max 외의 새 물리 평가가 필요하지 않다.

| 의무 | 증거 또는 계산 | 논리적 역할 |
|---|---|---|
| 두 원 \(A_s\), 전체 \(\widehat W_s\), source/J 일치 | 고정 입력 키·manifest·기존 certificate | 두 수준과 원 커널 보존 |
| 기존 근 존재·유일성·tube 지원 적용 | 기존 최종 결정과 근 tube 정리 | 두 근 및 그 사이 선분 재사용 |
| 정확한 cell 역상과 packet 포함 | (T35.8)–(T35.11), (T35.28)–(T35.30) | 저장 enclosure의 지원 보존 |
| \(C^{\rm ref}\)의 동일 점 자료 | point `energy_eV`, order 0/1, (T35.21) | retained 중심과 exact 저장 중심 구별 |
| 기준·이동·smoothing 경로의 도함수 영역 포함 | packet/center bounds와 \(J_s\) | \(M_3,M_4\)의 적용 정당화 |
| 전 tube 기울기 구간과 양의 분모 | (T35.22)–(T35.27) | root segment 평균 기울기 enclosure |
| 국소 \(k^{(4)}\) 및 양의 Peano 평균 | 저장 선택 cell, (T35.31)–(T35.34) | 패킷 위치를 보존한 분자 범위 |
| 분지별 및 gap 계수 | (T35.36)–(T35.40) | 새 균일 범위와 상대 부호 판정 |

**저장 JSON의 내용·키·hash를 읽는 것**은 read-only metadata 작업이다. 그러나 packet 경계, cell 선택·hull, \(C^{\rm ref}\), \(\mathcal E_s\), \(\mathcal S_s\), ratio 및 gap margin의 새 산출은 **새 인증 계산**이다. 이를 metadata parsing으로 표기하여 계약 전 수치 preview를 허용하지 않는다. parent가 동결한 새 main·복원 replay 예산에서만 실행한다. PHYS33·PHYS34의 소진된 슬롯은 되살리지 않는다.

모든 새 과학 경계를 정확 유리수로 유지하면 계산 과정에 Decimal interval helper, `rational_kernel`, Bernstein/jet 및 과학 모듈 import가 필요 없다. 사람이 읽는 십진 표시는 최종 유리수를 정한 뒤 FLOOR/CEILING으로 바깥쪽 반올림한다. 이 표시는 인증의 입력이나 재계산 기준이 아니다. raw 정확 유리수 및 원 outward enclosure에 의존하는 증명 구조를 보존한다. 짧은 표시값에서 새 margin을 재계산하지 않는다.

이 유도는 point ratio의 수치상 분리, 새로운 gap 계수 또는 새 수치 통과를 미리 주장하지 않는다. 성공 여부는 고정한 exact-rational 실행이 (T35.39) 또는 (T35.40)를 실제 충족하는지에 달렸다. 실패하면 원 결과를 보존하며 수준·domain·분할·정밀도·예산을 묵시적으로 바꾸지 않는다.

## 11. 범위와 보호 상태

조건부 명제의 범위는 **같은 고정 source-real 커널, 지정한 두 서로 다른 \(A_s\), 기존 두 tube, \(0\le\delta\le0.001\) eV, 지정 uniform/P4 프로파일**이다. 개별 분지의 근 존재는 이미 닫혔지만 새 상대 부호는 이 문서에서 인증하지 않았다. 원 \(J\), 원자 fit 불확실성 또는 coupled history가 해소되었다고 해석할 수 없다.

보호 상태는 `Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0`다. 향후 gap 비교가 인증되어도 physical admission과 공통 \(A\)의 두 분지 비교는 별도 의무다. 최종 채택 여부는 이론 기여와 실행 후보를 만들지 않은 별도 reviewer의 실제 decision에 맡긴다.
