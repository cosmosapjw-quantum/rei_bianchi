# A1b: 여섯 원자 궤도의 Gram 행렬, 채널 사영 및 점근 위상

상태: `DERIVED`; 병렬 수학 작성자의 노트이며 독립 심사자의 승인 문서가 아니다. 아래 결과는 명시한 여섯 궤도 Galerkin 공간의 성질이다. 실제 충돌 단면적의 정확도, 기저 수렴, continuum 완비성, R10R의 수치 상태와의 동일성을 인증하지 않는다. 기존 A1 테스트는 재실행하지 않았다.

## 1. 모형과 명시적 원자 궤도

전자 질량은 \(m=m_e\), \(\kappa_A=e^2/(4\pi\epsilon_0)>0\), \(\kappa_B=2\kappa_A\)이며 핵의 환산질량 보정을 넣지 않는다. \(a=\hbar^2/(m\kappa_A)\), \(E_0=m\kappa_A^2/(2\hbar^2)\)로 둔다. 전자 Hilbert 공간은 \(L^2(\mathbb R^3,d^3r)\), 내적은 첫 인자에 반선형이다. 처방된 핵 궤적 \(X_C(t)\)는 국소적으로 \(C^2\)이고 \(R=|X_B-X_A|>0\)이다. \(v_C=\dot X_C\), \(a_C=\dot v_C\), \(\rho_C=r-X_C\)이며 모든 시간 미분은 lab 좌표 \(r\)를 고정한다.

전자 Hamiltonian은

\[
H(t)=\frac{p^2}{2m}-\frac{\kappa_A}{|r-X_A(t)|}
                    -\frac{\kappa_B}{|r-X_B(t)|},\qquad p=-i\hbar\nabla_r.
\]

핵간 반발 에너지는 이 전자 Hamiltonian에 포함하지 않는다. 회전하는 body 축을 도입하지 않고 \(2p_x,2p_y,2p_z\)를 고정된 lab Cartesian 축으로 정의한다. \(N=(\pi a^3)^{-1/2}\)로 쓰면 실수 정규화 궤도는 다음과 같다.

\[
\begin{aligned}
\phi_{A1s}(\rho)&=N e^{-\rho/a},
&\epsilon_{A1s}&=-E_0,\\
\phi_{B1s}(\rho)&=\sqrt8\,N e^{-2\rho/a},
&\epsilon_{B1s}&=-4E_0,\\
\phi_{B2s}(\rho)&=N(1-\rho/a)e^{-\rho/a},
&\epsilon_{B2s}&=-E_0,\\
\phi_{B2p_i}(\boldsymbol\rho)&=N(\rho_i/a)e^{-\rho/a},
&\epsilon_{B2p_i}&=-E_0\quad(i=x,y,z).
\end{aligned}
\]

여기서 스칼라 \(\rho=|\boldsymbol\rho|\)이다. 따라서 H \(1s\)와 He\(^+\) \(n=2\)는 이 모형에서 정확히 축퇴한다. 에너지 고윳값만으로 원래 핵 중심을 식별할 수 없다. 중심과 전체 \(n=2\) 부분공간을 경계 자료로 지정해야 한다.

유한한 기준 시각 \(t_*\)를 고르고

\[
\begin{aligned}
\chi_{C\nu}(r,t)&=e^{i\Theta_{C\nu}(r,t)/\hbar}\phi_{C\nu}(\rho_C),\\
\Theta_{C\nu}
&=m v_C(t)\cdot\rho_C+
 \frac m2\int_{t_*}^{t}|v_C(s)|^2ds
 -\epsilon_{C\nu}(t-t_*)
 +\int_{t_*}^{t}\frac{\kappa_{\bar C}}{R(s)}ds .
\end{aligned}
\]

이는 유한 \(R\)에서 선택한 명시적 embedding이다. 다른 중심별 공간 위상은 일반적으로 이 여섯 차원 공간 자체를 바꾸므로, 임의의 MO 공간 안에서의 gauge 변경과 동일시하지 않는다. 같은 중심에서는 공간 위상이 공통이고 나머지 위상은 상태별 상수이므로 원자 궤도의 직교성이 유지된다.

이 특정 궤도들은 \(H^2(\mathbb R^3)\)에 속한다. \(s\)-궤도의 cusp는 고전적 미분가능성을 깨지만 약한 2차 미분의 \(1/\rho\) 특이성은 3차원에서 국소 \(L^2\)이다. 유한 속도의 plane wave를 곱해도 \(H^2\)이고, 다른 핵의 \(1/|r-X_{\bar C}|\)를 곱한 결과도 \(L^2\)이다. 따라서 아래의 강한 전자 잔차는 선택한 궤도에 대해 의미가 있다. 일반적인 A1 기저에 대해서까지 \(H^2\)를 가정하는 것은 아니다.

## 2. Gram 양의 정부호성: 수치 관찰이 아닌 증명

\(u=\chi_{A1s}\), \(V=(\chi_{B1s},\chi_{B2s},\chi_{B2p_x},\chi_{B2p_y},\chi_{B2p_z})\), \(X=(u,V)\)라 하자. \(V^\dagger V=I_5\)이고 \(s=V^\dagger u\)이므로

\[
S=X^\dagger X=
\begin{pmatrix}1&s^\dagger\\s&I_5\end{pmatrix},\qquad
\delta=1-s^\dagger s.
\]

**명제.** 유한한 시간의 \(R>0\)와 유한 속도에서 \(S\)는 양의 정부호이다.

증명: H 중심 \(X_A\) 근처에서 \(u\)는 0이 아닌 상수를 \(u_0\)로 하여

\[
u(X_A+\rho)=u_0
\left[1+i\frac m\hbar v_A\cdot\rho-\frac{|\rho|}{a}
  +O(|\rho|^2)\right]
\]

로 전개된다. \(-|\rho|/a\) 항 때문에 \(u\)는 그 점에서 미분가능하지 않다. 반면 모든 He 중심 궤도와 그 ETF는 \(X_A\ne X_B\)의 작은 근방에서 실해석적이다. 만일 \(\alpha u+Vb=0\)가 \(L^2\)에서 성립하면 연속성 때문에 점별로도 성립한다. \(\alpha\ne0\)이면 \(u\)가 해석적 함수들의 선형결합이 되어 모순이다. 따라서 \(\alpha=0\)이고, \(V\)의 직교성으로 \(b=0\)이다. 여섯 열의 선형독립성이 증명된다. 따라서 \(\delta>0\), \(\|s\|<1\)이다.

정확한 고윳값과 역행렬은

\[
\operatorname{spec}S=\{1-\|s\|,1,1,1,1,1+\|s\|\},
\qquad
S^{-1}=\begin{pmatrix}
\delta^{-1}&-\delta^{-1}s^\dagger\\
-\delta^{-1}s&I_5+\delta^{-1}ss^\dagger
\end{pmatrix}.
\]

따라서 \(\kappa_2(S)=(1+\|s\|)/(1-\|s\|)\)이다. 점별 양의 정부호성은 임의의 모든 궤적에서 수치 조건수가 작다는 보장이 아니다. 지정된 유한 시간 구간에서 매개변수가 연속이고 \(R>0\)이면 compactness로 최소 고윳값에 양의 하한이 존재하지만, 실제 하한과 정밀도 선택은 별도 수치 자료를 요구한다.

**합체 극한에 대한 반례.** \(R=0\), 두 중심의 속도가 같은 순간에는 공간 ETF를 공통 인자로 제거할 수 있다. 상태별 상수 위상도 Gram 고윳값을 바꾸지 않는다. 그때

\[
s_{1s}=\frac{16\sqrt2}{27},\quad
s_{2s}=-\frac12,\quad s_{2p_i}=0,
\]

\[
\|s\|^2=\frac{512}{729}+\frac14=\frac{2777}{2916},\qquad
\delta=\frac{139}{2916}>0.
\]

첫 적분은 \(4\pi N^2\sqrt8\int_0^\infty r^2e^{-3r/a}dr\), 두 번째는 H \(1s\) 밀도에 대한 \(\langle1-r/a\rangle=1-3/2\)이다. 따라서 이 여섯 궤도는 동일 중심·동일 속도에서도 종속되지 않는다. 합체 자체가 반드시 Gram 특이성을 만든다는 주장은 잘못이다.

더 일반적으로 합체점에서 상대 속도가 유한해도 선형독립이다. 공통 공간 위상과 \(e^{-r/a}\)를 제거하면, 종속 관계는 상수들을 흡수하여

\[
e^{iq\cdot r}=b_0e^{-r/a}+b_1(1-r/a)+b\cdot r/a,
\quad q=m(v_A-v_B)/\hbar
\]

를 요구한다. 모든 방향 \(r=\lambda n\)에서 좌변은 절댓값 1로 유계이다. 우변의 선형 성장항이 없어야 하므로 \(-b_1+b\cdot n=0\)가 모든 단위 \(n\)에서 성립한다. 따라서 \(b_1=b=0\)이고, 우변은 \(\lambda\to\infty\)에서 0으로 가므로 모순이다. 다만 **선택한 Coulomb 보상 위상 \(\int\kappa_{\bar C}/R\,dt\)는 \(R=0\) 궤적을 본 계약에서 허용하지 않는다.** Gram 문제가 없다는 것과 위상 계약의 유효범위는 다르다.

## 3. 계수 노름과 물리 사영 확률

계수를 \(c=(\alpha,b)^T\), 파동함수를 \(\psi=Xc\)라 하면

\[
\|\psi\|^2=c^\dagger Sc
=|\alpha|^2+\|b\|^2+2\operatorname{Re}(\alpha^*s^\dagger b)
=\delta|\alpha|^2+\|b+s\alpha\|^2.
\]

\(w=u-Vs=(I-VV^\dagger)u\)이면 \(\|w\|^2=\delta\)이고 전체 선택 공간의 직교 사영은

\[
P=X S^{-1}X^\dagger
=VV^\dagger+\frac{|w\rangle\langle w|}{\delta}.
\]

그러나 원래 H 및 He 원자 채널 사영은 각각

\[
\Pi_A=|u\rangle\langle u|,\qquad \Pi_B=VV^\dagger
\]

이며 유한 \(R\)에서는 서로 직교하지 않는다. 정규화된 \(\psi=Xc\)에 대해

\[
p_A=\langle\psi,\Pi_A\psi\rangle=|\alpha+s^\dagger b|^2,
\quad
p_B=\langle\psi,\Pi_B\psi\rangle=\|b+s\alpha\|^2.
\]

He의 \(1s\) 또는 \(n=2\) 블록만 고르면 \(p_{B,n}=\|b_n+s_n\alpha\|^2\)이다. He 내부 블록끼리는 직교하므로 \(p_B=p_{B,1s}+p_{B,n=2}\)이다. 일반적으로 \(p_A+p_B\ne1\)이고, 단순 계수 제곱 \(\|b\|^2\)도 유한 시각의 He 사영 확률이 아니다. 각 \(\Pi\)는 진짜 직교 사영이므로 정규화된 상태에 대해 개별 \(p\)는 0과 1 사이이다.

\(P=\Pi_B+|w\rangle\langle w|/\delta\)는 선택 공간 안의 직교 분할이지만 두 번째 항은 원래 H \(1s\) 사영을 바꾼 것이다. 이를 별도 선언 없이 물리적인 H/He의 배타적 유한 시간 분할로 사용할 수 없다. 마찬가지로 Löwdin 계수 \(z=S^{1/2}c\)의 성분 제곱은 혼합된 직교 기저의 확률이며, 원래 중심별 원자 사영과 자동으로 같지 않다.

선택 공간 바깥의 임의의 상태 \(\Psi\)에 대해 \(f=X^\dagger\Psi\)이면 그 직교 사영의 계수는 \(c_P=S^{-1}f\), 노름은 \(\|P\Psi\|^2=f^\dagger S^{-1}f\)이다. 이 사영 노름과 Galerkin 시간발전의 보존 노름을 혼동하지 않는다.

## 4. 위상의 부호와 정확한 강한 잔차

고정 lab 좌표에서

\[
\partial_t\Theta_{C\nu}
=m a_C\cdot\rho_C-\frac m2|v_C|^2
-\epsilon_{C\nu}+\frac{\kappa_{\bar C}}R .
\]

원자 고유방정식과 \(p\,e^{i m v_C\cdot\rho_C/\hbar}
=e^{i m v_C\cdot\rho_C/\hbar}(p+m v_C)\)를 직접 적용하면

\[
\boxed{(H-i\hbar\partial_t)\chi_{C\nu}
=\left[V_{\bar C}(r,t)+\frac{\kappa_{\bar C}}R
              +m a_C\cdot\rho_C\right]\chi_{C\nu}},
\qquad V_{\bar C}=-\frac{\kappa_{\bar C}}{|r-X_{\bar C}|}.
\]

속도 교차항 \(v_C\cdot p\), 원자 에너지 및 \(m v_C^2/2\) 항은 정확히 상쇄된다. 잔차는 에너지 차원의 곱셈 연산자이다. \(a_C=0\)이고 다른 핵의 장을 정확히 monopole \(-\kappa_{\bar C}/R\)로 대체하면 잔차는 0이다. 정적인 중심에서 \(v_C=a_C=0\)이어도 실제 다른 핵의 비균일 장은 남으므로 해당 잔차가 0이라고 할 수 없다.

\(D_C=X_{\bar C}-X_C=R n_C\)이면 국소 전개는

\[
V_{\bar C}+\frac{\kappa_{\bar C}}R
=-\frac{\kappa_{\bar C}}{R^2}n_C\cdot\rho_C
-\frac{\kappa_{\bar C}}{2R^3}
 \left[3(n_C\cdot\rho_C)^2-\rho_C^2\right]+\cdots .
\]

이는 전 공간에서 균등한 점별 전개가 아니므로 적분에 그대로 무제한 대입하지 않는다. 실제 궤도에 작용한 \(L^2\) 잔차에는 다음 경계가 성립한다.

\[
\left\|\left(\frac1{|D_C-\rho|}-\frac1R\right)\phi_{C\nu}\right\|_2
\le \frac{C_{C\nu}}{R^2}\quad(R\ge R_0),
\]

\[
\|(H-i\hbar\partial_t)\chi_{C\nu}\|_2
\le m|a_C|\|\rho\phi_{C\nu}\|_2+
\frac{\kappa_{\bar C} C_{C\nu}}{R^2}.
\]

경계의 이유: \(\rho\le R/2\)에서는 평균값 정리로 차이가 \(4\rho/R^2\) 이하이다. 외곽에서는 원자 궤도의 지수 꼬리를 쓰고 다른 핵 주변의 작은 공에서는 \(\int_{|z|<\ell}|z|^{-2}d^3z=4\pi\ell\)의 유한성을 쓴다. 나머지 외곽은 두 핵과 떨어져 있어 지수 꼬리로 제어된다. 따라서 다른 핵의 Coulomb 특이점 때문에 \(L^2\) 추정이 실패하지 않는다.

## 5. 장거리 한계: 보상 위상과 유한 차원 산란

다음은 충분조건이지 모든 핵 궤적에 대한 주장도, 궤적 방정식의 해도 아니다. 양쪽 꼬리에서

\[
R(t)\ge c|t|,\quad |v_C(t)|\le C_v,\quad
|a_C(t)|=O(|t|^{-2})\qquad(|t|\to\infty)
\]

를 가정한다. 잔차 \(L^2\) 노름은 \(O(|t|^{-2})\)이므로 시간 적분 가능하다. \(\int\kappa_{\bar C}/R\,dt\) 자체는 일반적으로 로그 발산한다. 따라서 위상의 기준 시각을 \(t_*=\infty\)라고 두어 적분이 유한하다고 가정하면 안 된다. 유한 \(t_*\)의 위상 함수로 장거리 \(1/R\) 항을 제거하고, 그 위상까지 포함한 비교 상태와 계수의 극한을 취한다. 이 구조를 여기서는 Coulomb monopole 보상 또는 Dollard형 비교 위상이라고 부른다. 일반적인 다입자 Dollard 정리 전체를 증명했다는 뜻은 아니다.

보상 항이 없으면 \(H-i\hbar\partial_t\)의 대각 monopole이 \(-\kappa_{\bar C}/R\)로 남아 시간 적분 불가능하다. 이 사실은 보상하지 않은 복소 진폭의 극한 문제이며, 확률의 극한도 무조건 존재하지 않는다는 뜻은 아니다.

원자 궤도의 지수 감소로 임의의 \(0<\beta<1/a\)에 대해

\[
|s_j(t)|\le C_{\beta,j}e^{-\beta R(t)}.
\]

증명은 \(R\le|r-X_A|+|r-X_B|\)와 두 궤도에 각각 가중치 \(e^{\beta|\rho_C|}\)를 준 Cauchy–Schwarz 부등식으로 충분하다. ETF의 공간 위상은 절댓값 1이므로 이 경계를 바꾸지 않는다. 시간 미분에는 위치·속도·가속도 및 에너지에 의한 유한 차수 가중 인자만 추가된다. 위 꼬리 가정에서 \(\dot s\) 역시 지수 인자에 다항식이 곱해진 경계를 가지므로 시간 적분 가능하다. 따라서 \(S\to I_6\), \(\dot S\)는 꼬리에서 적분 가능하다.

전체 기저로부터

\[
h=X^\dagger HX,\quad D=X^\dagger\dot X,\quad
M=h-i\hbar D=X^\dagger(HX-i\hbar\dot X)
\]

를 한번 계산한다. \(M\)은 일반적으로 Hermitian이 아니며

\[
M-M^\dagger=-i\hbar\dot S,\qquad
i\hbar S\dot c=Mc.
\]

\(W=S^{-1/2}\), \(c=Wz\)이면

\[
K=WMW-i\hbar W S\dot W,
\qquad K=K^\dagger,\qquad i\hbar\dot z=Kz.
\]

꼬리에서 \(S^{-1}\)의 노름은 유계이고 \(\|M\|\)은 궤도 잔차 노름의 합으로 제어된다. 양의 스펙트럼으로부터 \(S^{-1/2}\)의 Fréchet 미분이 유계이므로 \(\|\dot W\|\le C\|\dot S\|\)이다. 따라서 \(\int_{\text{tail}}\|K(t)\|dt<\infty\). 고정된 유한 기준 시각에서 시작한 유한 차원 unitary propagator는 양쪽 꼬리에서 연산자 노름 극한을 가지며, 이 모형의 산란 행렬을 정의할 수 있다. 같은 이유로 \(c(t)\)도 유한한 극한을 가진다. \(S\to I\)이므로 양쪽 극한에서 \(z\)와 \(c\)는 일치하고

\[
p_{B,n}(+\infty)=\sum_{\nu\in B,n}|c_\nu(+\infty)|^2.
\]

이 unitary 성질은 **선택한 여섯 채널 안의 Galerkin 모형**에 대한 것이다. 선택되지 않은 bound state나 ionization으로의 정확한 확률 유출을 0이라고 입증하는 결과가 아니다.

추가로 정확한 전자 Hamiltonian의 unitary propagator \(U(t,s)\)가 존재한다고 가정하면 비교 상태에 대해서

\[
\left\|U(t_*,t_2)\chi(t_2)-U(t_*,t_1)\chi(t_1)\right\|_2
\le\frac1\hbar\int_{t_1}^{t_2}
\|(i\hbar\partial_t-H)\chi(t)\|_2dt
\]

이므로 위 잔차 추정은 비교 상태의 파동 연산자형 극한도 보장한다. 여기서 정확한 전자 propagator의 존재 가정과, 여섯 채널 투영 모형의 unitary 극한 증명을 구별한다. 이 결과만으로 전체 산란 채널의 점근 완비성을 주장할 수 없다.

유한 \(-T\)에서 \(c=(1,0,0,0,0,0)^T\)로 두는 것은 정확히 순수한 \(u(-T)\) 상태를 뜻한다. 그 시각에는 \(p_B=\|s\|^2\)의 overlap이 남는다. 이를 임의로 빼거나 He에 직교하도록 H 상태를 바꾸지 않는다. 실제 incoming 경계는 \(c(-\infty)=e_A\)이며, 유한 \(-T\) 시작의 오차는 적분 가능한 꼬리 생성자의 적분으로 별도 제어해야 한다. 이 문서에서는 그 오차의 수치값을 산출하지 않는다.

핵간 반발 \(V_{NN}=2\kappa_A/R\)를 전자 모형에 공통 c-number로 나중에 더하면 공통 핵 위상 \(\exp[-(i/\hbar)\int V_{NN}dt]\)가 붙는다. 전자 채널 위상의 \(\kappa_{\bar C}\)와 결합하면 입사 H+He\(^{2+}\)의 monopole은 0, 출사 H\(^+\)+He\(^+\)의 monopole은 \(+\kappa_A/R\)가 된다. 이는 전하에 대한 일관성 점검이다. 공통 위상은 여기서 정의한 전자 채널 사영 확률을 바꾸지 않으며, 핵의 양자 산란이나 recoil을 도입한 것은 아니다.

## 6. 경계와 남은 해석적·물리적 공백

이 후보는 기저·ETF·미분 좌표·Gram·잔차·점근 사영을 명시하며, \(R>0\)에서 그 Gram 비특이성을 증명한다. 궤적 꼬리의 충분조건 아래 비교 계수의 극한을 정의한다. 다음 사항은 이 유도에서 해결되지 않았다.

- R10R의 \(g,b,\sigma\) 상태와 이 원자 부분공간 사이의 실제 상태·중첩 자료를 통한 동일성 또는 변환 행렬.
- 여섯 bound 궤도만으로 충돌 observable을 정확히 계산할 수 있는지와, 누락 공간 잔차의 실제 크기.
- 채널 확대, continuum, 핵 궤적 선택·recoil·환산질량 변경 및 단면적 적분.
- CPC body 축의 각속도 부호와 기존 active 회전 convention 사이의 출처에 근거한 매핑.
- 실제 경로에서 Gram 조건수, 유한 시간 경계 오차 및 수치 단위계 구현.

따라서 명시적 embedding의 존재와 정확한 비교 채널 정의는 유도되었지만, 이 노트만으로 A1 전체의 기존 상태 매핑 공백 또는 생산용 충돌 계산 승인을 닫지 않는다. `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED`를 유지한다.
