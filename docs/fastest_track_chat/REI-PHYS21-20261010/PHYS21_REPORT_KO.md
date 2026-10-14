# REI-PHYS21 — Scalar shear의 2차 radiation forcing과 인과적 기체 응답

연구일: 2026-10-10. PHYS20의 지정 후속 루프. 근거 상태: **수식은 derived, 명시한 작은 진단은 numerically checked, 실제 Rust 소스는 source-inspected / byte-identity-verified**. 실제 evolving-gas의 2차 계수는 아직 계산하지 않았다. `physical=HOLD`를 유지한다. 별도 최종 판정과 대상 파일의 해시는 `independent/DECISION_REVIEW.json`에 기록한다.

## 1. 이번 루프의 결론과 범위

PHYS20에서 닫힌 continuum scalar first-variation cancellation을 입력으로 받아, 이번에는 **각도 평균 뒤 처음 남는 scalar 2차 항**을 유도했다. 결과는 한 cohort의 endpoint spectral curvature, endpoint–opacity covariance, survival variance, mean second-opacity change의 네 항으로 분해된다. 이 식은 prescribed mean expansion, 물리적으로 등방인 birth source, 매끄러운 scalar opacity에 대한 연속 구면 결과다.

이 분해에서 세 가지 물리적 결론을 얻었다.

1. 자유 광자의 평균 에너지가 shear에 의해 2차에서 증가하더라도, 흡수 사건률이나 primary heating의 평균이 증가한다고 결론낼 수 없다. 같은 매끄러운 감소 opacity에서도 optical depth에 따라 2차 heating의 부호가 바뀌는 정확한 반례를 구성했다.
2. 고정 기체에서 모든 ray가 같은 inverse-cube opacity 구간에 머물면 평균 optical depth는 정확히 보존된다. Jensen inequality에 의해 평균 survival은 증가하고 누적 흡수 확률은 감소하지만, 현재 시각의 흡수 사건률에는 동일한 부호 정리가 없다.
3. 실제 FT03의 coupled scalar response는 새 geometry forcing을 받는 **선형 Volterra 방정식**이다. 온도 계수에는 thermal energy/H의 변화와 총 입자수/H의 변화가 함께 들어간다. radiation memory와 absorber abundance 변분을 포함한 식을 실제 소스의 상태·단위·반응 소유권에 결속했다.

| 결과 | 근거 상태 | 이 결과가 말하지 않는 것 |
|---|---|---|
| 일반 2차 scalar radiation kernel 및 fixed-q 표현과의 일치 | 독립 유도 일치; 새 진단 수치 검산 | native angular/remapping 정확도 |
| inverse-cube cumulative absorption 부등식 | 연속 구면에서 직접 유도 | threshold를 건너는 일반 cross section의 전역 부등식 |
| absorption/heating 부호 반례 | 정확한 유리수 + 유한 진폭 검산 | 실제 evolving FT03 gas의 부호 |
| 실제 HI fit을 쓴 고정 neutral-fraction cohort 계수 | 고정된 입력에서 수치 검산 | source 전체 적분이나 gas 해 |
| FT03 gas response, 온도·전자수 mapping | 소스에 결속한 유도; 국소 Jacobian 검산 | finite-time gas response를 풀었다는 주장 |

이 루프의 과학적 완료 범위는 위의 새 2차 구조와 검산이다. 기존 `[160,161] FAIL`, `tick160`, auxiliary escape `FAIL`, HH/RCT/CR `OFF`, precision atomic `PARKED`를 보존했다. Native history 0회, 새 gas IVP 0회, 닫힌 PHYS19/20 proof 재실행 0회이며 source/default/runtime returns를 변경하지 않았다.

## 2. 입력, 모델, convention

저장소는 `cosmosapjw-quantum/rei_bianchi`, 브랜치는 `forward/rust-reion-kernels-20260922`다. 입력 commit은 `faec51259ed26f660cf14568bcaa3d288e54bf9a`, root tree는 `d4c734ac2047e68966ccecc81da79eb68420f8a1`, scientific Rust src tree는 `cb69b4736dd046e4675557577eb8e0ead037d1f3`다. PHYS20의 report/handoff/result/DAG를 읽고 그때 닫힌 1차 결과를 사용했다. Canonical GPT-6 Astra harness v4.0.0의 SHA256은 `dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7`이다.

Metric signature는 \((-+++ )\), \(t\)는 gas-comoving proper time [s]다. 고정 principal axes에서

\[
ds^2=-c^2dt^2+a^2(t)\sum_i e^{2\epsilon B_i(t)}(dx^i)^2,
\qquad \sum_iB_i(t)=0. \tag{1}
\]

\(a,H,n_H\), scalar initial state 및 source의 scalar amplitude와 birth energy는 \(\epsilon\)에 독립이다. 이 가정은 **prescribed FT03 family**를 정의한다. Einstein 방정식을 함께 풀어 mean expansion의 shear-squared 보정을 구하는 family에서는 같은 차수의 추가 항이 생기므로 이 보고서의 계수를 그대로 전체 backreaction 계수로 사용할 수 없다. Bianchi I의 정확한 광선 운동학과 self-consistent background의 구별은 [L1]의 metric/geodesic 및 background 식과도 일치한다.

모든 coefficient를

\[
F_\epsilon=F_0+\epsilon F_1+\epsilon^2F_2+o(\epsilon^2),
\qquad F_2=\tfrac12\partial_\epsilon^2F|_0 \tag{2}
\]

로 정의한다. 아래의 `2차 계수`는 \(F_2\)이며 둘째 미분 그 자체가 아니다. 에너지는 eV, hazard에는 \(c\), 온도 변환에는 \(k_B\)를 명시적으로 유지한다.

연속 source와 opacity의 에너지 응답은 적용 구간에서 \(C^2\)이고, 시간·각도·birth 적분과 두 번 미분을 교환할 수 있다고 가정한다. Threshold/cutoff를 가로지르는 경로에 이 가정을 자동 적용하지 않는다. PHYS20의 threshold와 finite-grid 한계도 그대로 유지한다. Photon monopole와 shear–quadrupole coupling의 배경은 [L2]를 참고하되, 아래 causal kernel은 이번에 직접 유도한 결과다.

## 3. Physical birth-angle에서 두 번째 에너지 변분

Birth time \(b\), birth energy \(E_b\), 등방인 물리적 birth 방향 \(\boldsymbol m\)을 고정한다. \(|\boldsymbol m|=1\)이며

\[
A_s=B(s)-B(b),\qquad
E_0(s)=E_b\frac{a(b)}{a(s)},\qquad
R_s=\frac{E(s)}{E_0(s)}
=\left(\sum_i m_i^2e^{-2\epsilon(A_s)_i}\right)^{1/2}. \tag{3}
\]

이 변수에서 source 평균은 \(d\Omega_m/(4\pi)\)다. Birth Jacobian을 다시 곱하지 않는다. Scalar cohort count에도 별도 current-angle Jacobian을 덧붙이지 않는다.

\(u_s=\boldsymbol m^TA_s\boldsymbol m\), \(v_s=\boldsymbol m^TA_s^2\boldsymbol m\)라 쓰면

\[
R_s=1-\epsilon u_s+\epsilon^2(v_s-u_s^2/2)+O(\epsilon^3),
\quad
\ln R_s=-\epsilon u_s+\epsilon^2(v_s-u_s^2)+O(\epsilon^3). \tag{4}
\]

\(D=E\partial_E\), \(\delta=\partial_\epsilon|_0\)에 대해

\[
\delta F=-(DF_0)u_s,
\qquad
\delta^2F=2(DF_0)v_s+(D^2F_0-2DF_0)u_s^2. \tag{5}
\]

두 번째 로그 에너지 변분을 포함해야 하는 이유가 식 (5)에 드러난다. 선형 redshift perturbation만 제곱하면 뒤에 나오는 \(+3D\)를 얻지 못한다.

연속 구면 평균은

\[
\langle m_im_j\rangle=\frac{\delta_{ij}}3,
\quad
\langle m_im_jm_km_l\rangle
=\frac{\delta_{ij}\delta_{kl}+\delta_{ik}\delta_{jl}+\delta_{il}\delta_{jk}}{15}. \tag{6}
\]

Trace-free symmetric \(A,M\)에 대해

\[
\langle\boldsymbol m^TA^2\boldsymbol m\rangle=\tfrac13\operatorname{tr}A^2,
\quad
\langle(\boldsymbol m^TA\boldsymbol m)(\boldsymbol m^TM\boldsymbol m)\rangle
=\tfrac2{15}\operatorname{tr}(AM). \tag{7}
\]

따라서

\[
\langle\delta^2F\rangle=\frac2{15}(D^2+3D)F_0\operatorname{tr}A_s^2. \tag{8}
\]

이 단계는 단순한 positive variance 명제보다 강하다. Spectral operator \(\mathscr C=D(D+3)\)가 남으며, \(\mathscr C E^p=p(p+3)E^p\)이므로 국소 평균 곡률은 spectral slope에 따라 양·음·0 모두 가능하다.

## 4. 생존 확률을 포함한 일반 scalar 2차 커널

기체의 기준 trajectory를 고정해

\[
\lambda(s,E)=\sum_j c\,n_j(s)\sigma_j(E),\quad
\Theta(t,b)=\int_b^t\lambda(s,E(s))\,ds,\quad
P=e^{-\Theta},\quad K_\phi=PL_\phi \tag{9}
\]

로 둔다. \(L=1,E,cn_H\sigma_j,\lambda_j,\sum_j\lambda_j(E-\chi_j)\)를 선택하면 각각 count, surviving energy, per-absorber ionization rate, absorption event rate, primary heat를 얻는다.

무차원 opacity memory를

\[
M(t,b,E_b)=\int_b^t(D\lambda_0)(s)A_s\,ds,
\quad
V(t,b,E_b)=\int_b^t[(D^2+3D)\lambda_0](s)\operatorname{tr}A_s^2\,ds \tag{10}
\]

로 정의한다. \(\operatorname{tr}M=0\)이고 \(\delta\Theta=-\boldsymbol m^TM\boldsymbol m\)이다. 두 번 product rule을 취하면

\[
\delta^2(PL)=P_0\{\delta^2L-2\delta L\delta\Theta
+L_0[(\delta\Theta)^2-\delta^2\Theta]\}. \tag{11}
\]

식 (6)–(8)을 적용한 핵심 결과는

\[
\boxed{
\mathcal K_{\phi,2}
=\frac{P_0}{15}\left[
((D^2+3D)L_{\phi,0})\operatorname{tr}A_t^2
-2(DL_{\phi,0})\operatorname{tr}(A_tM)
+L_{\phi,0}\operatorname{tr}M^2
-L_{\phi,0}V
\right].} \tag{12}
\]

| 항 | 기원 | 부호 |
|---|---|---|
| \((D^2+3D)L_0\operatorname{tr}A_t^2\) | 현재 에너지 분포의 spectral curvature | 일반적으로 미정 |
| \(-2DL_0\operatorname{tr}(A_tM)\) | 현재 응답과 과거 opacity의 covariance | 일반적으로 미정 |
| \(L_0\operatorname{tr}M^2\) | survival의 variance | \(L_0\ge0\)이면 비음수 |
| \(-L_0V\) | 평균 opacity의 두 번째 변화 | 일반적으로 미정 |

\(M,V,A\)는 무차원이고 각 항은 \(L\)과 같은 단위다. \(t=b\) 또는 \(A_s=0\)이면 계수는 0이다. \(\lambda=0,L=E\)에서는 \(4E_0\operatorname{tr}A_t^2/15\)가 남아 PHYS20의 자유 광자 benchmark와 대수적으로 연결된다. 일정한 trace-free \(C\)에 대한 \(B(s)\mapsto B(s)+C\)에도 식 (12)는 불변이다.

\(y_0(s)\)를 고정한다는 것은 \(\epsilon\) 미분 동안 그 trajectory를 바꾸지 않는다는 뜻이다. 일반식에서는 \(y_0(s)\)가 시간에 따라 진화할 수 있다. §7의 특정 진단만 neutral fraction을 시간에 대해서도 상수로 고정한다.

### 4.1 Fixed-q와 physical-birth 표현의 일치

\(C=B(b)\), fixed-q 방향 \(\boldsymbol z\)에 대해

\[
R_s^q=\left[\frac{\boldsymbol z^Te^{-2\epsilon(C+A_s)}\boldsymbol z}
{\boldsymbol z^Te^{-2\epsilon C}\boldsymbol z}\right]^{1/2},
\quad J_b=(\boldsymbol z^Te^{-2\epsilon C}\boldsymbol z)^{-3/2}. \tag{13}
\]

\(X=(DL_0)A_t-L_0M\)라 두면 두 표현의 둘째 미분 차이를 \(P_0\)로 나눈 것은

\[
4\boldsymbol z^TCX\boldsymbol z
-10(\boldsymbol z^TC\boldsymbol z)(\boldsymbol z^TX\boldsymbol z)
+L_0[15(\boldsymbol z^TC\boldsymbol z)^2-6\boldsymbol z^TC^2\boldsymbol z]. \tag{14}
\]

평균은 \((4/3-20/15)\operatorname{tr}CX+L_0(30/15-2)\operatorname{tr}C^2=0\)이다. Coordinate 변화, first-order kernel과 source의 covariance, second-order \(J_b\)를 모두 포함해야 취소된다. 자세한 raywise 유도와 새로운 2차 검산은 `contributions/tensor/TENSOR_SECOND_ORDER_KO.md`에 있다.

## 5. 부호: inverse-cube 법칙이 구분해 주는 두 질문

\(A_s=h_sS\), \(\lambda\propto E^p\), \(L\propto E^r\)이고 \(I_k=\int_b^t\lambda_0h_s^kds\)라 하자. 식 (12)는

\[
\frac{\mathcal K_2}{K_0}
=\frac{\operatorname{tr}S^2}{15}
\left[r(r+3)h_t^2-2rp h_t I_1+p^2I_1^2-p(p+3)I_2\right]. \tag{15}
\]

이는 baseline expansion과 opacity amplitude가 시간에 따라 변해도 성립한다. 부호를 분리하는 analytic diagnostic에서는 \(H=0\), \(t-b=T\), \(h_s=(s-b)/T\), 일정한 \(\lambda_0\), \(\tau=\lambda_0T\)로 두어 \(I_1=\tau/2,I_2=\tau/3\)를 사용했다. 이것은 고정 기체 운동학 진단이며 FT03 실제 history나 Einstein 해가 아니다.

### 5.1 누적 흡수 확률에는 부호가 있다

\(p=-3\)이면 \(\mathscr C\lambda_0=0\)이다. 더 강하게 determinant-one map의 solid-angle Jacobian 항등식에서

\[
\langle R_s^{-3}\rangle=1,
\quad \langle\Theta\rangle=\Theta_0,
\quad \boxed{\langle P\rangle\ge P_0,\qquad
\langle1-P\rangle\le1-P_0}. \tag{16}
\]

마지막 부등식은 \(e^{-x}\)의 convexity에 따른다. 적용되는 모든 ray와 시각이 동일한 inverse-cube 구간에 머물고 기체가 \(\epsilon\)에 독립이어야 한다. 이 조건하의 식 (16)은 perturbative 결과를 넘는 연속 구면 부등식이다. 유한 각도 rule에서 전 진폭을 정확히 적분했다는 인증은 아니다.

### 5.2 현재 흡수율과 가열률에는 보편적인 부호가 없다

\(S=\operatorname{diag}(1,-1,0)\)일 때 현재 흡수 사건률은

\[
c_A(\tau)\equiv\frac{\mathcal K_{A,2}}{K_{A,0}}
=\frac3{10}\tau(\tau-4). \tag{17}
\]

\(0<\tau<4\)에서는 음수, \(\tau>4\)에서는 양수다. Survival의 크기 순서가 그 시간 미분의 크기 순서까지 고정하지는 않으므로 식 (16)과 모순되지 않는다.

Primary heat \(L=\lambda(E-\chi)\), \(\chi/E_0=1/2\)에는

\[
c_Q(\tau)\equiv\frac{\mathcal K_{Q,2}}{K_{Q,0}}
=\frac3{10}\tau^2-\frac25\tau-\frac8{15}. \tag{18}
\]

양의 영점은 \(2(1+\sqrt5)/3\simeq2.157\)이다. 충분히 작은 \(|\epsilon|<\ln2\)에서 \(E>\chi\)이므로 이 부호 변화는 threshold cusp에 의한 것이 아니다. 일반 \(\eta_\chi=\chi/E_0<1\)에서는

\[
\frac{\mathcal K_{Q,2}}{K_{Q,0}}
=\frac{\operatorname{tr}S^2}{15(1-\eta_\chi)}
\left[-2+(-6+9\eta_\chi)\tau+\frac94(1-\eta_\chi)\tau^2\right]. \tag{19}
\]

| 매끄러운 diagnostic | \(\tau\) | 정확한 상대 \(\epsilon^2\) 계수 |
|---|---:|---:|
| 현재 흡수 사건률 | \(1/4\) | \(-9/32\) |
| 현재 흡수 사건률 | \(8\) | \(48/5\) |
| Primary heat, \(E_b=2\chi\) | \(1/4\) | \(-59/96\) |
| Primary heat, \(E_b=2\chi\) | \(4\) | \(8/3\) |

`figures/PHYS21_scalar_signs.png`와 PDF는 식 (17)–(18)의 계수 곡선이다. 임의의 유한 \(\epsilon\)에서 실제 fractional change를 그린 그림이 아니다.

## 6. 독립 tensor 계산의 검증 범위

기여자는 owner 코드를 import하지 않고 ray별 \(\epsilon^2\) polynomial을 `Fraction`으로 전개하고 시간 적분한 결과를 trace formula와 비교했다. 6개 axis ray와 8개 cube ray로 이루어진 Q2/Q4-exact 14-ray rule을 사용했다. 대각 행렬에서는 네 direction-square class로 묶을 수 있다. 유한 진폭에서 이 rule이 모든 높은 angular moment까지 정확하다는 뜻은 아니다.

별도로 원래 exponential energy와 survival을 Decimal80으로 계산하고 \(\epsilon=10^{-4},5\times10^{-5}\)의 centered coefficient를 Richardson 외삽했다. Physical-birth와 fixed-q+\(J_b\) 표현 모두에서 비교했다. Composite Boole의 8/16 blocks 변화도 확인했다. 네 부호 사례 외에 \(A_s=xS+x^2T\), \(T=\operatorname{diag}(1/3,1/6,-1/2)\), 시간가변 opacity 및 혼합 endpoint spectrum을 사용한 사례를 포함했다. 그 마지막 정확한 상대 계수는 \(8050541/57348000\)이다.

- 실제 **44/44 PASS, exit 0**.
- 외삽 계수 최대 절대차: \(1.03446306758096\times10^{-15}\).
- Boole resolution 변경의 최대 계수 차이: \(7.65321756814567\times10^{-19}\).
- 수치 허용 절대차: \(10^{-12}\). 엄밀한 quadrature enclosure는 아니다.
- 검사 수의 구성은 moment 10, exact kernel 5, source covariance 5, finite amplitude/resolution 20, 정확한 sign value 4다. 이는 44개의 서로 다른 물리 정리라는 뜻이 아니다.

근거: `contributions/tensor/second_order_results_v1.json`, `EXECUTION.json`, `verify_second_order.py`.

## 7. 실제 HI fit에 결속한 고정 neutral-fraction 수치 결과

실제 입력의 \(H=10^{-14}\ {m s}^{-1}\), shear magnitude \(\varsigma\simeq10^{-16}\ {m s}^{-1}\), \(B(t)=\varsigma t\operatorname{diag}(1,-1,0)\), \(n_H(0)=10^{-4}\ {m cm}^{-3}\), \(x_{\rm HI}=1-0.9\), \(E_b=13.7\) eV를 사용했다. 각 decimal literal은 해당 binary64 값을 exact real로 해석해 Decimal60으로 계산했다. \(x_{\rm HI}\)만 시간에 대해 고정하고 \(n_H(t)=n_H(0)e^{-3Ht}\)는 유지했다. He opacity는 이 soft-energy support에서 inactive다.

Source의 Verner HI fit [L3; pinned `atomic_provider.rs`]에서 \(z=E/0.4298\), \(v=\sqrt{z/32.88}\), \(p_V=2.963\)라 하면

\[
\alpha_\sigma=D\ln\sigma
=\frac{2z}{z-1}+\frac{p_V}2-5.5-\frac{p_V}2\frac{v}{1+v},
\quad
D\alpha_\sigma=-\frac{2z}{(z-1)^2}-\frac{p_V}4\frac{v}{(1+v)^2}. \tag{20}
\]

따라서 \(D^2\sigma=\sigma(\alpha_\sigma^2+D\alpha_\sigma)\)다. Heat에서는 \(\sigma(E)(E-\chi)\) 전체를 미분했다. Thermal threshold \(\chi=13.598434599702\) eV와 opacity cutoff 13.60 eV를 구분했다.

Endpoint \(t=1.25\times10^9\) s, birth \(b=0,t/2\)의 두 cohort를 조사했다. 아래 표는 \(b=0\)의 \(\mathcal K_2/K_0\)다.

| Cohort observable | 상대 \(\epsilon^2\) 계수 |
|---|---:|
| Survival \(P\) | \(+1.78390360948\times10^{-18}\) |
| Absorption event rate \(P\lambda_{\rm HI}\) | \(-2.30206280810\times10^{-15}\) |
| Primary heat \(P\lambda_{\rm HI}(E-\chi)\) | \(-3.88272869428\times10^{-13}\) |
| Surviving energy \(PE\) | \(+8.34817904512\times10^{-15}\) |

위 숫자는 이 특정 cohort의 계수다. 기체 온도 변화나 최종 이온화율 변화로 해석하지 않는다.

기준 \(E_0=13.6998287510703073\) eV, \(\Theta_0=0.002331838935105933\), \(\alpha_\sigma=-2.688723241255\), \(D\alpha_\sigma=-0.252051964061\), \(\mathscr C\sigma/\sigma=-1.088989019761\)다. \(|\epsilon|\le1\)에서 최소 에너지도 13.699827 eV보다 커 cutoff와 떨어져 있다.

Primary heat의 네 상대 계수 항은 차례로

\[
-3.90004374544\times10^{-13},\quad
+1.72972121207\times10^{-15},\quad
+2.04732999282\times10^{-20},\quad
+1.76343030955\times10^{-18}. \tag{21}
\]

이 진단에서는 endpoint spectral curvature가 음의 합을 지배한다. \(E-\chi\)가 작은 상태의 상대 heating 계수이므로, 단순히 cross section의 기울기만으로 크기를 예상해서는 안 된다. 이 숫자를 source 전체 적분, evolving-gas forcing, 실제 \(T_2\)에 대입하지 않았다.

### 7.1 실제 실행과 오차의 성격

`code/second_order_hi_kernel.py`는 time Gauss–Legendre 16/32와 angular GL4×phi8 / GL6×phi12를 사용한다. 이는 연구용 적분 rule이며 native midpoint grid를 바꾸거나 인증한 것이 아니다. \(h=1,1/16,1/32\)에서 ray별로

\[
\frac{K(+h)+K(-h)-2K_0}{2h^2} \tag{22}
\]

를 Decimal 안에서 먼저 계산한 뒤 평균해 cancellation을 처리했다. 새 \(D\sigma,D^2\sigma\)는 log-energy centered difference와 Richardson으로 확인했다.

실제 **39/39 PASS, exit 0**이었다. 계수의 최대 상대차는 \(1.63411907076\times10^{-13}\), time rule 변경의 최대 상대차는 \(6.50657569297\times10^{-16}\), spectral derivative 비교의 최대 상대차는 \(6.84193890230\times10^{-22}\)다. 각각의 허용 상대차는 \(5\times10^{-11},2\times10^{-13},5\times10^{-19}\)였다. 이는 명시한 점과 적분법에서의 수치 일치이며 rigorously enclosed error bar가 아니다.

결과 JSON SHA256은 `ed41b97cfd65ffeb4e21efb6fab672488cc0a9495f28f439e08f0840ee2f0a5b`다. 실제 command/exit와 script SHA는 `evidence/OWNER_EXECUTION.json`에 있다. Owner kernel 실행의 총 wall time은 별도로 측정하지 않았으므로 tool polling 시간을 계산 시간으로 기록하지 않았다.

## 8. 실제 FT03 source와 기체 상태

PHYS20에 있던 Rust source/example/test 8개 blob이 현재 입력 tree와 동일함을 확인했다. 추가로 `ft03_controlled.rs`, `hhe_events.rs`를 읽고 remote Git blob과 저장 bytes의 일치를 확인했다. 전체 identity 및 source-reading evidence는 `contributions/source_gas/SOURCE_BINDING.json`, `REMOTE_SOURCE_READ.json`에 있다.

기체 상태를 \(y=(x,h_1,h_2,w)=(x_{\rm HII},x_{\rm HeII},x_{\rm HeIII},w_{\rm eV/H})\)라 쓰자. He fractions는 He nucleus당 비율이며 \(f=n_{\rm He}/n_H=0.083\)이다.

\[
X_e=x+f(h_1+2h_2),\quad \Pi=1+f+X_e,\quad n_e=n_HX_e,
\quad T=\frac{2e_{\rm V}}{3k_B}\frac w\Pi. \tag{23}
\]

여기서 \(e_{\rm V}=1.602176634\times10^{-12}\) erg/eV, \(k_B=1.380649\times10^{-16}\) erg/K다. 실제 paired initial은 \((x,h_1,h_2,T)=(0.9,0.3,0.6,50000\ {m K})\), 초기 photons/H는 0.05, birth energy는 13.7 eV, 연속 source는 \(S=5\times10^{-15}\) photons/H/s다. 별도의 generic FT03 fixture [20,35,70] eV를 이 source 대신 사용하지 않았다.

연속 birth measure는

\[
d\mu(b,E_b)=0.05\delta_0(db)\delta_{13.7}(dE_b)
+S\,db\,\delta_{13.7}(dE_b),\quad 0\le b\le t. \tag{24}
\]

단위는 photons/H다. Per-H photon count에는 별도 \(-3HN\)을 추가하지 않고, proper photon density는 \(n_HN\)으로 얻는다. `coupled_primary::raw`는 `photon_cm3=[0,0,0]`으로 nonphoto FT03 RHS를 호출한 뒤 packet primary absorption/heat를 한 번 추가한다. RR/DR emission은 Case-A escaped-energy ledger에 들어간다.

Lower/upper populations/H를

\[
\ell=(1-x,f(1-h_1-h_2),fh_1),\qquad
u=(x,fh_1,fh_2) \tag{25}
\]

로 두면 CI/RR/two-DR event/H/s는 \(C_j=\ell_jn_e\beta_j(T)\), \(R_j=u_jn_e\alpha_j(T)\), \(D_k=u_1n_ed_k(T)\)다. \(\nu=(C_0-R_0+A_0,C_1-R_1-\sum D_k+A_1,C_2-R_2+A_2)\)에 대해

\[
\dot x=\nu_0,\quad \dot h_1=(\nu_1-\nu_2)/f,\quad \dot h_2=\nu_2/f,
\quad \dot w=-2Hw-\mathcal C+Q. \tag{26}
\]

\(\mathcal C=\sum\chi_jC_j+\sum u_jn_e\kappa_j+\sum e_k^{\rm DR}D_k\), \(\kappa_j=(k_BT/e_{\rm V})\alpha_j(3/2+g_j)\), \(g_j=d\ln\alpha_j/d\ln T\)다. 실제 source에 없는 shear-viscous heating을 추가하지 않았다. 모든 local JVP와 \(\kappa_j'\)의 \(g_j'\) 항은 source/gas 부록 SG17–SG22에 명시했다.

## 9. Geometry forcing에서 coupled gas response로

관측량 functional을

\[
R_\phi(t;y,\epsilon)=\int d\mu\,\langle P L_\phi\rangle,
\quad
y_\epsilon=y_0+\epsilon^2\eta+o(\epsilon^2),
\quad r_\phi(t)=\int d\mu\,\mathcal K_{\phi,2}[y_0] \tag{27}
\]

로 둔다. PHYS20의 조건하에 \(y_1=0\)이므로

\[
R_{\phi,2}=r_\phi+D_yR_\phi[y_0](\eta), \tag{28}
\]

\[
\boxed{
D_yR_\phi[\eta](t)=\int d\mu\,P_0(t,b)
\left[L_{\phi,y,0}(t)\eta(t)
-L_{\phi,0}(t)\int_b^t\lambda_{y,0}(s)\eta(s)\,ds\right].} \tag{29}
\]

첫 항은 현재 absorber abundance, 둘째는 과거 전체의 opacity feedback이다. Source cross section의 직접 온도 의존성이 없으므로

\[
\lambda_y=cn_H(-\sigma_{\rm HI},\ f(\sigma_{\rm HeII}-\sigma_{\rm HeI}),\ -f\sigma_{\rm HeI},\ 0). \tag{30}
\]

\(N,U_\gamma,\Gamma_j\)는 \(L_y=0\), \(A_j,Q\)에는 local abundance 항이 있다. \(A_j=\ell_j\Gamma_j\)이므로 \(A\) functional에 다시 abundance 변분을 더하면 이중 계산이다. \(\Gamma\)를 사용할 때에는 \(A_{j,2}=\ell_{j,0}\Gamma_{j,2}+\ell_{j,2}\Gamma_{j,0}\)가 필요하다.

\(\mathbf R=(A_{\rm HI},A_{\rm HeI},A_{\rm HeII},Q)^T\) 및

\[
\mathsf B=\begin{pmatrix}
1&0&0&0\\0&1/f&-1/f&0\\0&0&1/f&0\\0&0&0&1
\end{pmatrix} \tag{31}
\]

를 쓰면

\[
\boxed{\dot\eta=J_{\rm np}\eta+\mathsf B D_y\mathbf R[\eta]+\mathsf B\mathbf r,
\qquad\eta(0)=0.} \tag{32}
\]

여기서 \(J_{\rm np}\)는 source-defined nonphoto RHS의 baseline Jacobian이다. \(D_y^2F[y_1,y_1]=0\)이므로 이 차수에서 gas Hessian을 따로 더하지 않는다. 식 (32)는

\[
\dot\eta(t)=A_g(t)\eta(t)+\int_0^tK_g(t,s)\eta(s)ds+f_2(t), \tag{33}
\]

\[
\begin{aligned}
A_g(t)&=J_{\rm np}(t)+\mathsf B\int_{b\le t}d\mu\,P_0(t,b)\mathbf L_{y,0}(t,b),\\
K_g(t,s)&=-\mathsf B\int_{b\le s}d\mu\,P_0(t,b)\mathbf L_0(t,b)\otimes\lambda_{y,0}(s,b),\\
f_2(t)&=\mathsf B\mathbf r(t)
\end{aligned} \tag{34}
\]

의 선형 Volterra 식이다. 유한 구간에서 적절히 연속·유계인 coefficients와 미분 가능한 baseline이라는 가정하에 인과적 응답을 정의한다. 이번 루프에서는 이 식을 수치적으로 풀지 않았다.

온도 계수는

\[
\boxed{\eta_T=T_0\left[\frac{\eta_w}{w_0}
-\frac{\eta_x+f(\eta_{h_1}+2\eta_{h_2})}{\Pi_0}\right].} \tag{35}
\]

따라서 \(\eta_w\)만으로 \(\eta_T\)의 부호를 정할 수 없다. He photo channels가 현재 soft support에서 inactive이어도 \(T,n_e\)와 CI/RR/DR를 통한 He response는 남는다. 고정 proper-time scalar Thomson integral을 정의한다면 \(\tau_{e,2}=c\sigma_T\int n_H[\eta_x+f(\eta_{h_1}+2\eta_{h_2})]ds\)다. Photon optical depth \(\Theta\)나 observer lightcone optical depth와 같은 양으로 취급하지 않는다.

### 9.1 국소 derivative 검산과 보존식

세 개의 명시적 smooth fixture에서 local nonphoto Jacobian 48개와 온도·입자수 gradient 12개를 analytic JVP와 complex-step으로 비교했다. 실제 **60/60 PASS, exit 0**, 최대 상대차 \(1.12876091033\times10^{-15}\), step \(10^{-24}\), 허용 상대차 \(2\times10^{-12}\)였다. 이 fixture들은 trajectory가 아니다. 수동 Python transcription의 국소 미분 일치이며 native machine-code equivalence나 radiation memory solution의 검산은 아니다.

초기 v1도 60/60 PASS, exit 0이었다. 이후 DR Kelvin constants를 합산 후 곱하던 transcription을 source와 같이 각각 곱한 뒤 합하도록 수정했다. 초기 code/results/receipt/logs를 보존했고 step/tolerance를 바꾸지 않은 수정본도 60/60 통과했다. 분류는 **diagnostic implementation/transcription correction**이며 물리 failure나 runtime failure가 아니다. 같은 전사를 공유한 두 미분 계산의 일치만으로 source identity까지 증명할 수 없다는 구체적인 주의점이다.

Photon count와 source가 같은 의미로 정의되면 \(N_2'=-\sum A_{j,2}\), \(N_2(0)=0\)이다. \(I=\chi_{\rm HI}x+f[\chi_{\rm HeI}h_1+(\chi_{\rm HeI}+\chi_{\rm HeII})h_2]\)와 escaped/radiation energy를 포함한 동일 ledger에서는

\[
\frac d{dt}(w_2+I_2+U_{{\rm esc},2}+U_{\gamma,2})
=-2Hw_2-\dot W_{{\rm redshift},2}. \tag{36}
\]

Source의 2차 변분은 0이다. 식 (36)은 같은 source/event 소유권에 따른 유도된 일관성 조건이며, 이번에 ledger history를 실행해 검사했다는 뜻은 아니다.

## 10. 남은 수치 문제와 다음 루프

실제 finite-time \(\eta(t)\)를 계산하려면 같은 continuous constant-S 모델의 \(y_0(s)\), cohort별 \(P_0(t,b)\), spectral curvature와 opacity memory를 평가할 수 있어야 한다. PHYS19의 derivative upper bounds와 terminal error intervals만으로 그 시간 함수를 유일하게 복원할 수는 없다. 이번에 읽은 PHYS19/BRIDGE13 자료는 모델과 조건부 증명의 범위를 제공했으나 callable dense baseline을 materialize하지 않았다. PHYS19 ZIP 전체 bytes를 이번에 복원하지 않았고, 제한된 두 번의 title 검색이 resolve되지 않았다는 사실을 archive 부재나 프로젝트 전체 blocker로 해석하지 않았다.

현재 해결되지 않은 것은 **실제 evolving-gas의 finite-time quadratic coefficient와 그 부호**다. 일반 kernel, source mapping, causal operator는 이 누락 때문에 미완료가 되지 않는다. 수치 해를 요청할 경우 필요한 자료는 baseline values/enclosure, cohort survival 또는 그 적분 evaluator, baseline·source·time integration 오차, cutoff margin이다.

다음 루프는 **REI-PHYS22_INITIAL_TIME_COUPLED_SHEAR_RESPONSE**로 지정한다. 실제 paired initial state와 이 보고서의 식 (12), (32), (35)를 사용해, gas IVP 없이 coupled scalar response의 초기시간 전개를 유도한다. 검증할 출발 가설은 initial cohort의 직접 기하학적 forcing이 \(O(\varsigma^2t^2)\), 이에 의한 gas response가 \(O(\varsigma^2t^3)\)이며 continuous-birth contribution은 한 차수 늦게 나타난다는 것이다. 이는 PHYS21에서 계산한 확정 계수가 아니라 PHYS22가 확인할 대상이다. 목표는 실제 초기 \(x_{\rm HII},T\) 계수와 He의 간접 응답 차수를 particle count와 보존식까지 포함해 구하는 것이다.

PHYS22는 첫 local nonzero coefficient와 출처·단위·부호를 닫는 데서 멈춘다. Finite-time gas IVP, native history, 첫 macro 8/16/32 campaign, full raw/NCP, 과거 proof 재실행이나 다른 atomic lane을 자동으로 여는 handoff가 아니다.

## 11. 재현과 근거 파일

- `PHYSICS_CONTRACT.json`: 입력·범위·convention·보존 상태.
- `RESULTS_SUMMARY.json`, `RESEARCH_DAG.json`, `state/RESEARCH_STATE.md`, `state/NEGATIVE_RESULTS.md`: 주장별 근거 상태와 다음 단계.
- `code/second_order_hi_kernel.py`, `evidence/second_order_hi_v1.json`, `evidence/OWNER_EXECUTION.json`: HI cohort 진단과 실제 실행.
- `contributions/tensor/`: 독립 유도, exact rational/finite-amplitude 검산, 실제 실행.
- `contributions/source_gas/`: pinned source bytes와 identity, local response 유도, derivative 검산과 보존된 v1 correction.
- `independent/DECISION_REVIEW_KO.md`, `independent/DECISION_REVIEW.json`: 후보·검산 설계에 참여하지 않은 별도 검토자의 판정.
- `reproduce.py`, `MANIFEST.json`, `SOURCE_MANIFEST.json`: 새 출력 디렉터리에서 이번의 작은 진단 세 개를 재현하거나 bytes만 검사하는 도구.
- `NEXT_HANDOFF_KO.md`: 다음 연구자의 최소 실행 입력.

Portable replay는 기존 PHYS21 진단의 이식성 검사다. 새 과학 가설의 수를 늘리지 않는다. ZIP의 fresh local restore 검사와 remote Git readback은 별도 evidence로 기록하며, local 복원을 remote restore라고 부르지 않는다. Publication commit과 archive hash를 모두 넣는 detached receipt를 사용해 archive self-hash 또는 미래 commit을 archive 안에 넣는 순환을 피한다.

## 참고문헌과 소스

**[L1]** P. Fleury, C. Pitrou, J.-P. Uzan, *Light propagation in a homogeneous and anisotropic universe*, Phys. Rev. D 91, 043511 (2015), [arXiv:1410.8473](https://arxiv.org/abs/1410.8473), [PDF](https://arxiv.org/pdf/1410.8473). Bianchi I metric, geodesic/redshift 및 background 범위를 확인했다. 이번 kernel의 출처로 오인하지 않는다.

**[L2]** R. Maartens, T. Gebbie, G. F. R. Ellis, *Cosmic microwave background anisotropies: nonlinear dynamics*, Phys. Rev. D 59, 083506 (1999), [arXiv:astro-ph/9808163](https://arxiv.org/abs/astro-ph/9808163), [PDF](https://arxiv.org/pdf/astro-ph/9808163). Spectral/multipole transport의 문헌 배경이다.

**[L3]** D. A. Verner, G. J. Ferland, K. T. Korista, D. G. Yakovlev, *Atomic Data for Astrophysics. II. New Analytic Fits for Photoionization Cross Sections of Atoms and Ions*, Astrophys. J. 465, 487 (1996), [arXiv:astro-ph/9601009](https://arxiv.org/abs/astro-ph/9601009), [PDF](https://arxiv.org/pdf/astro-ph/9601009). Fit의 구조는 문헌과 비교했고 수치 constants와 cutoff의 실제 소유권은 pinned source로 고정했다.

**[S1]** [입력 commit](https://github.com/cosmosapjw-quantum/rei_bianchi/commit/faec51259ed26f660cf14568bcaa3d288e54bf9a), [기존 draft PR83](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/83). 이번 결과의 source identity는 `SOURCE_MANIFEST.json`과 contributor source binding에 기록한다. Publication 이후의 commit은 별도 receipt를 따른다.
