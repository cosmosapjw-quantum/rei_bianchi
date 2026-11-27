# E13C3: frozen damping을 보존하는 1차 coefficient-variation 보정

## 범위와 근거

**근거 상태: `derived`; 새 exact-algebra 검산 범위는 `implementation-verified`.** 이 문서는 이론 contributor 산출물이다. 후보의 최종 독립 decision review나 물리 승격을 수행하지 않는다.

현재 기준은 `BASS_HE_E13C2_VARIABLE_COEFFICIENT_20261010_v1/THEORY.md` 전체, 특히 §3.0의 식 (2a)–(2c), §6–8의 사건·ledger·bound와 같은 packet의 `NEXT_DAG.json`에 있는 `E13C3_EXPONENTIAL_DEFECT_CORRECTION_ON_FIXED_GAS_PATH`다. 해당 `state/RESEARCH_STATE.md`도 읽었다. GPT-6 Astra research harness v4.0.0의 `PROJECT_INSTRUCTIONS.md`, phase 6, evidence policy를 적용했다. Harness의 자체 `state/RESEARCH_STATE.md`는 미실행 템플릿이므로 프로젝트 근거로 쓰지 않았다.

이번 새 작업은 **endpoint와 count/energy moments를 한 차원 quadrature로 평가하는 공식, 초기 stock의 전파, 정확한 1차 ledger, 원래 연속 방정식의 잔차, 그리고 incoming uncertainty를 포함한 조건부 bound**다. E13C2의 17개 Taylor-jet 검산과 저장된 연속 reference는 다시 실행하지 않았다. 새로운 native/gas/Newton 계산, full campaign, source/threshold/anchor 변경은 포함하지 않는다.

유한한 여섯 local 및 현재 first2 path에서의 정량 성능은 owner의 별도 구현 결과로 판단한다. 여기의 algebra 검산은 그 물리 입력의 enclosure 또는 정확도 판정이 아니다.

## 1. 정의와 현재 입력 계약

사건 하나의 열린 내부에서 국소 좌표를 \(u=s-s_a\in[0,h]\), \(s=\ln a\), midpoint를 \(m=h/2\)로 둔다. \(u,h\)는 무차원이다. Prime은 \(d/du\)다. 에너지는 같은 inherited characteristic

\[
 E(u)=E_0e^{-u},\qquad E_h=E_0e^{-h}
 \tag{1}
\]

를 유지한다. \(E\)와 binding energy \(\chi_i\)는 eV이며 \(\epsilon=1.602176634\times10^{-12}\,\mathrm{erg/eV}\)로 에너지를 변환한다. Binary64 입력의 exact lift와 십진 상수의 정의를 혼합하지 않는다. \(P\)는 inherited spectral node의 photon stock 정규화이며 spectral quadrature weight를 중복 적용하지 않는다. Metric convention은 \((- ,+,+,+)\)이고, 이 scalar characteristic을 일반적인 방향 의존 Bianchi redshift로 확장하지 않는다.

같은 affine gas path와 배경에서

\[
 P'=q-\Lambda P,\qquad
 \Lambda=\sum_i\lambda_i,\qquad
 \lambda_i=\frac{c n_{{\rm target},i}\sigma_i(E)}{H},
 \tag{2}
\]

이며 \(H>0\), \(q\ge0\), \(\lambda_i\ge0\)를 가정한다. \(q,\lambda_i\)와 아래 integrand는 사건별로 적분 가능하고 유한하다. 도함수의 존재는 (3)–(22)의 적분식에 필요하지 않다. Source-band 내부의 현재 source law는

\[
 q=\frac{R}{C_E E H},\qquad C_E=E_{\min}^{-1}-E_{\max}^{-1},
 \qquad R=10^{-15}\,\mathrm{photons/H/s},
\]

이며 source mask 바깥에서는 \(q=0\)이다. 위 숫자는 상속 입력의 표기이며 새로운 값으로 재정의하지 않는다. \(R\)는 이 lane에서 상수다. \(q\)가 \(E,H\) 때문에 변하는 것은 별도 RCT emission source를 넣는 것과 다르다.

Frozen 계수 \(q_f,\lambda_{if}\)는 **저장된 native midpoint 계수를 binary64에서 정확히 올린 값**으로 정의하고, \(L=\sum_i\lambda_{if}\ge0\)로 쓴다. 연속 함수를 수학적 midpoint에서 다시 평가한 \(q(m),\lambda_i(m)\)와는 inherited realification 반올림 차이가 있을 수 있다. 그 차이도 아래 \(\delta q,\delta\lambda_i\)에 포함한다. 정확한 실수 midpoint 값과 같다고 가정하지 않는다. 따라서

\[
 P_f'=q_f-LP_f,\qquad P_f(0)=P_{fa},\qquad
 \delta q=q-q_f,\quad\delta\lambda_i=\lambda_i-\lambda_{if},
 \quad\delta\Lambda=\sum_i\delta\lambda_i
 \tag{3}
\]

로 둔다. \(P_{fa}\ge0\)이면 \(P_f\ge0\)다. 전체 defect 부호는 \(e=P-P_f\)이며, true incoming defect는 \(e_a=P(0)-P_{fa}\)다.

Source mask, 종별 cutoff, macro endpoint, source branch와 energy event anchor는 현재 packet과 동일하게 유지한다. 사건을 가로질러 midpoint 계수를 만들거나 fit의 비활성 영역에 log derivative를 외삽하지 않는다. E13C2의 도함수 식을 부가적으로 사용할 때만 그 절의 event-free smoothness와 유한한 active-domain 조건이 적용된다. 이 보정에는 numerical derivative 또는 \(r_i'/r_i\)가 필요하지 않다.

## 2. 한 번의 quadrature로 계산하는 endpoint와 두 moment

다음 entire response function을 정의한다.

\[
 \mathcal J_a(z)=\int_0^a e^{-zt}\,dt
 =\begin{cases}-\operatorname{expm1}(-za)/z,&z\ne0,\\a,&z=0.\end{cases}
 \tag{4}
\]

\(\mathcal J(z)\)처럼 하첨자를 생략하면 \(a=h\)다. Frozen stock은

\[
 P_f(u)=P_{fa}e^{-Lu}+q_f\mathcal J_u(L).
 \tag{5}
\]

1차 coefficient-variation response는

\[
 e_1'+Le_1=r,\qquad r(u)=\delta q(u)-\delta\Lambda(u)P_f(u),
 \qquad e_1(0)=e_a
 \tag{6}
\]

로 정의한다. 따라서

\[
 e_1(u)=e^{-Lu}e_a+
 \int_0^u e^{-L(u-v)}r(v)\,dv.
 \tag{7}
\]

\(Lh\)를 전개하지 않았다. Source 변화와 photon depletion의 부호를 보존한 \(r\)를 적분하며, 양의 항별 크기를 더한 bound를 실제 signed correction 대신 쓰지 않는다.

필요한 세 kernel은

\[
 W_h(v)=e^{-L(h-v)},\qquad
 K_0(v)=\mathcal J_{h-v}(L),\qquad
 K_E(v)=E(v)\mathcal J_{h-v}(L+1).
 \tag{8}
\]

Moment를 \(J_0=\int_0^h e_1(u)\,du\), \(J_E=\int_0^h E(u)e_1(u)\,du\)로 두면

\[
 \boxed{e_1(h)=e^{-Lh}e_a+\int_0^h W_h(v)r(v)\,dv,}
 \tag{9}
\]

\[
 \boxed{J_0=e_a\mathcal J_h(L)+\int_0^h K_0(v)r(v)\,dv,}
 \tag{10}
\]

\[
 \boxed{J_E=E_0e_a\mathcal J_h(L+1)+\int_0^h K_E(v)r(v)\,dv.}
 \tag{11}
\]

식 (10)–(11)은 (7)을 적분하고 적분 순서를 교환해서 얻는다. 예를 들어

\[
 \int_v^h E_0e^{-u}e^{-L(u-v)}\,du
 =E_0e^{-v}\int_0^{h-v}e^{-(L+1)t}\,dt=K_E(v).
\]

즉 energy kernel에는 \(E(h)\)나 \(E(m)\)가 아니라 **forcing 시점의 \(E(v)\)**가 들어간다. 식 (9)의 초기 stock term만 넣고 식 (10)–(11)의 초기 moment term을 빠뜨리면 일반 incoming defect의 ledger가 닫히지 않는다.

이 표현은 계수 평가 하나의 공통 quadrature grid에서 \(r,\delta\lambda_iP_f,E\delta\lambda_iP_f\)를 모두 계산할 수 있게 한다. 각 내부 quadrature node에서 다시 (7)의 convolution을 계산할 필요가 없다. 비용 감소 정도는 실제 구현 측정 사항이며 이 유도만으로 정하지 않는다.

## 3. 종별 direct/response moment와 정확한 1차 ledger

Frozen 누적량과 연속 누적량의 차이에 대한 1차 근사를

\[
 D_i=\int_0^h\delta\lambda_iP_f\,du,\qquad
 D_{E,i}=\int_0^h E\delta\lambda_iP_f\,du,
\]

\[
 \boxed{\Delta A_i^{(1)}=D_i+\lambda_{if}J_0,\qquad
 \Delta B_i^{(1)}=\epsilon[D_{E,i}+\lambda_{if}J_E],}
 \tag{12}
\]

\[
 \boxed{\Delta Z^{(1)}=\epsilon J_E,\qquad
 \Delta Q_i^{(1)}=\Delta B_i^{(1)}-\epsilon\chi_i\Delta A_i^{(1)}}
 \tag{13}
\]

로 둔다. \(D_i,D_{E,i}\)는 종별 opacity 변화의 직접 항이고 \(\lambda_{if}J_0,\epsilon\lambda_{if}J_E\)는 photon field response다. 해당 분해 convention을 유지한다. \(Q_i\)는 photoelectron heat이며 absorption energy \(B_i\)와 다르다.

Kernel은 다음 adjoint 관계와 terminal condition을 만족한다.

\[
 -K_0'+LK_0=1,\quad -K_E'+LK_E=E(v),\quad
 K_0(h)=K_E(h)=0.
\]

특히 모든 \(v\in[0,h]\)에서

\[
 \boxed{W_h+LK_0=1,\qquad E_hW_h+(L+1)K_E=E(v).}
 \tag{14}
\]

식 (9)–(11)에 (14)를 적용하고 \(r=\delta q-\delta\Lambda P_f\), \(\sum_i\lambda_{if}=L\)를 쓰면

\[
 \boxed{e_1(h)+\sum_i\Delta A_i^{(1)}
 =e_a+\int_0^h\delta q\,du,}
 \tag{15}
\]

\[
 \boxed{\epsilon E_he_1(h)+\sum_i\Delta B_i^{(1)}+\Delta Z^{(1)}
 =\epsilon E_0e_a+\int_0^h\epsilon E\delta q\,du.}
 \tag{16}
\]

이것은 coefficient-variation 순서를 맞춘 누적량의 **정확한 대수 항등식**이다. \(e_1\) 자체가 true defect와 정확히 같다는 뜻은 아니다. Source injection 차이를 우변에서 빼거나 생략하면 다른 ledger가 된다.

같은 quadrature nodes/weights로 세 response와 direct/source 적분을 평가하면 (14)의 pointwise 성질 때문에 해당 quadrature의 ledger도 exact arithmetic에서 닫힌다. 실제 arithmetic에서는 kernel evaluation, 종별 sum, 누적, baseline representation과 seam 오차가 남는다. Ledger를 강제로 0으로 맞추어 moment를 재정의하지 않고 독립적으로 계산한 항을 합해 residual을 기록한다. Quadrature order 변화에 대한 안정성은 추가 numerical evidence이며 이 대수 성질의 대체물이 아니다.

## 4. 원래 연속 계수 방정식에 남는 항

\(P_c=P_f+e_1\)라고 하면

\[
 P_c'=q-LP_c-\delta\Lambda P_f
\]

이므로 원래 식 (2)에 대한 differential residual은

\[
 \boxed{P_c'+\Lambda P_c-q=\delta\Lambda e_1.}
 \tag{17}
\]

에너지는 \((EP_c)'=EP_c'-EP_c\)이므로

\[
 \boxed{(\epsilon EP_c)'+\epsilon E\Lambda P_c+\epsilon EP_c-\epsilon Eq
 =\epsilon E\delta\Lambda e_1.}
 \tag{18}
\]

따라서 \(P_c\)에 원래 full coefficient \(\lambda_i\)를 곱해 흡수를 적분하면, endpoint와 source의 ledger residual은 각각

\[
 \int_0^h\delta\Lambda e_1\,du,
 \qquad \epsilon\int_0^h E\delta\Lambda e_1\,du
 \tag{19}
\]

다. 반면 식 (12)는 \(\delta\lambda_i e_1\)를 제외한 일관된 1차 bookkeeping을 사용한다. 그 ledger의 정확한 closure를 **원래 variable-coefficient 모델의 exact conservation 또는 exact photon solution**으로 승격하지 않는다.

더 강한 주의점은 \(\delta\Lambda=0\)이어도 종별 \(\delta\lambda_i\)는 0이 아닐 수 있다는 것이다. 총 opacity가 일정하면 (7)은 임의의 적분 가능한 source variation에 대해 photon defect를 정확히 준다. 그러나 source 변화로 \(e_1\ne0\)이고 두 종의 opacity 변화가 상쇄되는 경우 각 종의 full moment에는 \(\int w\delta\lambda_i e_1\)가 남는다. 이 항들은 종별로 0이 아닐 수 있으면서 합에서는 소거된다. 따라서 aggregate ledger closure만으로 종별 count나 heat의 정확도를 판단하지 않는다.

## 5. 원래 해와 보정 사이의 bound: 정확한 incoming defect

\(e=P-P_f\)의 exact 방정식은

\[
 e'+\Lambda e=r,
\]

이며 true Green 함수는 \(G(u,v)=\exp[-\int_v^u\Lambda]\le1\)다. 다음 양을 정의한다.

\[
 D_L=\int_0^h|\delta\Lambda|\,du,\qquad
 B_r=\int_0^h\bigl(|\delta q|+|\delta\Lambda|P_f\bigr)\,du,
 \qquad S=|e_a|+B_r.
 \tag{20}
\]

\(D_L\)는 무차원 optical variation이고 \(B_r,S\)는 photon stock 정규화의 양이다. \(P_f\ge0\)를 사용했으며 그렇지 않은 형식적 algebra에서는 \(P_f\)를 \(|P_f|\)로 바꿔야 한다. Nonnegative true opacity로부터 \(\|e\|_\infty\le S\)다. \(R=e-e_1\)라 두면

\[
 R(u)=-\int_0^u e^{-L(u-v)}\delta\Lambda(v)e(v)\,dv,
 \tag{21}
\]

이므로 nonnegative frozen opacity 아래에서

\[
 \boxed{\|R\|_\infty\le D_LS.}
 \tag{22}
\]

Endpoint와 moments에는 더 구체적인 kernel bound를 쓸 수 있다.

\[
 H_h=\int_0^h W_h|\delta\Lambda|\,dv,\quad
 H_0=\int_0^h K_0|\delta\Lambda|\,dv,\quad
 H_E=\int_0^h K_E|\delta\Lambda|\,dv.
\]

\[
 \boxed{|R(h)|\le SH_h,\qquad
 \left|\int_0^hR\,du\right|\le SH_0,\qquad
 \left|\int_0^h ER\,du\right|\le SH_E.}
 \tag{23}
\]

\(K_0,K_E\ge0\)라서 Fubini와 절댓값 부등식으로 바로 얻는다. 또한 \(H_h\le D_L\), \(LH_0\le D_L\), \((L+1)H_E\le E_0D_L\)다. 이 형태는 단순히 \(hL\)를 곱하는 bound보다 큰 frozen opacity를 더 잘 보존한다.

종별 moment의 exact remainder는

\[
 \Delta A_i-\Delta A_i^{(1)}
 =\lambda_{if}\int R\,du+\int\delta\lambda_i e\,du,
\]

\[
 \frac{\Delta B_i-\Delta B_i^{(1)}}\epsilon
 =\lambda_{if}\int ER\,du+\int E\delta\lambda_i e\,du.
 \tag{24}
\]

\(V_i=\int|\delta\lambda_i|\,du\), \(V_{E,i}=\int E|\delta\lambda_i|\,du\)라 쓰면

\[
 |\Delta A_i-\Delta A_i^{(1)}|\le S(\lambda_{if}H_0+V_i),
\]

\[
 |\Delta B_i-\Delta B_i^{(1)}|\le\epsilon S(\lambda_{if}H_E+V_{E,i}),
 \qquad |\Delta Z-\Delta Z^{(1)}|\le\epsilon SH_E.
 \tag{25}
\]

총 opacity의 cancellation은 \(D_L\)를 작게 만들 수 있지만 개별 \(V_i\)를 작게 만들지는 않는다. 따라서 종별 정확도를 위한 bound에는 개별 variation도 필요하다.

일반적인 \(\chi_i\ge0\)에 대해 heat remainder는 (25)의 energy bound와 \(\epsilon\chi_i\)배 count bound의 합으로 제한된다. 더 날카로운 표현은 weight \(w_i=E-\chi_i\)를 유지하는 것이다. 해당 종의 구간 전체에서 \(E\ge\chi_i\)라면 \(K_{Q,i}=K_E-\chi_iK_0\ge0\)이고, (23)–(25)에서 energy weight를 \(w_i\)로 바꾸어 같은 방식의 bound를 얻는다. 이 부호 조건이 확인되지 않은 구간에는 signed heat kernel을 절댓값 bound처럼 쓰지 않는다.

식 (20)–(25)의 값이 **엄밀한 수치 bound**가 되려면 전체 구간의 입력/적분 enclosure가 필요하다. Quadrature sampling으로 추정한 \(D_L,B_r,H_0,H_E,V_i\)는 진단 추정치다. 현재 새 symbolic 계산은 그러한 enclosure를 제공하지 않는다.

## 6. 근사 incoming defect와 그 불확실성

실제 path 전파에서 이전 구간의 보정을 \(\widetilde e_a\)로 가져오고 true incoming과의 차이에 대해

\[
 |e_a-\widetilde e_a|\le\eta_a
\]

만 아는 경우, 식 (9)–(13)에는 \(\widetilde e_a\)를 사용한다. \(\widetilde e_1(0)=\widetilde e_a\), \(R=e-\widetilde e_1\), \(S_*=|\widetilde e_a|+\eta_a+B_r\)라고 쓰면

\[
 R(u)=e^{-Lu}(e_a-\widetilde e_a)
 -\int_0^u e^{-L(u-v)}\delta\Lambda(v)e(v)\,dv.
 \tag{26}
\]

따라서

\[
 |R(h)|\le e^{-Lh}\eta_a+S_*H_h,
\]

\[
 \left|\int R\right|\le\eta_a\mathcal J_h(L)+S_*H_0,
 \qquad
 \left|\int ER\right|\le E_0\eta_a\mathcal J_h(L+1)+S_*H_E.
 \tag{27}
\]

식 (24)의 moment remainder는 그대로 성립한다. 예를 들어 count bound는

\[
 |\Delta A_i-\Delta A_i^{(1)}|
 \le\lambda_{if}[\eta_a\mathcal J_h(L)+S_*H_0]+S_*V_i,
\]

energy bound는 \(\epsilon\{\lambda_{if}[E_0\eta_a\mathcal J_h(L+1)+S_*H_E]+S_*V_{E,i}\}\)다.

동일한 remainder에 대한 다른 정확한 방정식은

\[
 R'+\Lambda R=-\delta\Lambda\widetilde e_1,
 \qquad R(0)=e_a-\widetilde e_a.
\]

True opacity의 nonnegativity와 \(\|\widetilde e_1\|_\infty\le|\widetilde e_a|+B_r\)를 사용하면 다음 sup bound도 얻는다.

\[
 \boxed{\|R\|_\infty\le\eta_a+D_L(|\widetilde e_a|+B_r).}
 \tag{28}
\]

이는 \(\eta_a+D_LS_*\)보다 날카롭지만 (27)의 frozen weighted kernel 정보를 그대로 포함하지는 않는다. 두 식을 혼합해 각자가 제공하지 않는 damping factor를 주장하지 않는다.

중요한 두 경우는 다음과 같다.

- True incoming이 정확히 주어지면 \(\eta_a=0\)이며 (22)의 \(D_L(|e_a|+B_r)\)를 회복한다.
- Incoming \(e_a\) 자체가 이전 구간에서 생긴 1차 defect라면 그것을 매 구간 0으로 reset하지 않는다. 오차 \(\eta_a\)도 다음 구간으로 운반해야 누적 path의 bound가 된다. 여섯 개 독립 local control의 \(e_a=0\) bound를 그대로 full path에 붙일 수 없다.

## 7. 근사 순서, stiffness, 선택적인 두 번째 response

작은 parameter를 \(\eta\)라 하고 fixed finite 구간에서 \(\delta q=O(\eta)\), 각 \(\delta\lambda_i=O(\eta)\)를 필요한 weighted \(L^1\) norm으로 가정하면 \(D_L,B_r,V_i=O(\eta)\)다. 정확히 일치하는 incoming 또는 \(e_a=O(\eta)\)이면 (22), (25)의 remainder는 \(O(\eta^2)\)다. 그러나 \(e_a=O(1)\)를 독립적으로 고정하면 \(D_L|e_a|\)가 남으므로 모든 결과를 2차라고 부를 수 없다. Incoming uncertainty가 있으면 \(\eta_a\)의 순서도 별도로 제한해야 한다.

이 기준은 \(Lh\ll1\)을 요구하지 않는다. \(Lh\)가 커도 frozen damping을 정확히 유지하고 coefficient variation이 작으면 보정이 유효할 수 있다. 반대로 \(h\)의 십진 숫자가 작다는 사실만으로 optical variation이나 truncation error가 작다고 판단하지 않는다. 도함수가 cell refinement에 독립인 Lipschitz bound를 가질 때에는 \(D_L\le\|\Lambda'\|_\infty h^2/4+h|\Lambda(m)-L|\)처럼 연결할 수 있다. 두 번째 항은 captured frozen 값과 수학적 midpoint의 차이다. 정확한 midpoint freezing이면 그 항이 사라진다. Finite current input에서 이 도함수 enclosure를 새로 얻었다고 주장하지 않는다.

전체 field remainder만을 보는 더 날카로운 operator measure는

\[
 \rho_f=\sup_{0\le u\le h}\int_0^u e^{-L(u-v)}|\delta\Lambda(v)|\,dv\le D_L.
\]

\(|\delta\Lambda|\le\theta L\), \(L>0\)가 구간 전체에서 성립하면 \(\rho_f\le\theta(1-e^{-Lh})\le\theta\)다. 따라서 전체 optical depth가 커도 상대적 coefficient variation이 작은 조건에서는 stiff 구간의 response를 제한할 수 있다. 이는 추가 bound 가정이며 sampled ratio의 관찰과 구별한다.

설명용으로 \((Tf)(u)=\int_0^u e^{-L(u-v)}\delta\Lambda(v)f(v)\,dv\)라 쓰면, 정확한 incoming에서 \(e=e_1-Te\)다. \(\rho_f<1\)이면 contraction argument가 가능하여

\[
 \|e-e_1\|_\infty\le\frac{\rho_f}{1-\rho_f}\|e_1\|_\infty.
\]

선택적인 다음 response는 \(e_2=-Te_1\)이고

\[
 e-e_1-e_2=T^2e,\qquad
 \|e-e_1-e_2\|_\infty\le\frac{D_L^2}{2}(|e_a|+B_r).
\]

마지막 \(1/2\)는 ordered integration triangle에서 나온다. Nonnegative frozen damping과 적분 가능한 \(|\delta\Lambda|\) 아래에서 Volterra 반복은 일반적으로 \(\|T^n\|\le D_L^n/n!\)를 가지므로 수렴 자체에 \(D_L<1\)이 필수는 아니다. 그러나 큰 \(D_L\)에서 **첫 항 하나의 정확성**이 보장되지는 않는다. 이 절은 선택적 후속 유도이며 이번 packet에서 2차 numerical candidate를 구현하거나 추가 campaign을 실행하지 않는다.

## 8. 극한, 수치 구현 및 event ledger

\(L=0\)에서는

\[
 P_f=P_{fa}+q_fu,\quad W_h=1,\quad K_0=h-v,\quad
 K_E=E(v)-E_h,
\]

이며 모든 식이 유한하다. \(h=0\)에서는 \(e_1(h)=e_a\), \(J_0=J_E=0\)다. \(\delta q=\delta\lambda_i=0\)인 구간은 들어온 stock 차이를 \(e^{-Lu}e_a\)로 전파하고 count/energy의 incoming response를 정확히 반영한다. Source variation만 있고 **모든 종별 opacity가 일정**하면 이 field와 모든 moments는 정확하다. 총 opacity만 일정한 경우의 종별 예외는 §4와 같다.

수치 구현의 구체적인 주의점은 다음과 같다.

- \(1-e^{-x}\)를 작은 \(x\)에서 직접 빼지 않고 `-expm1(-x)`를 사용한다. \(q_f/L\) 형태로 \(L=0\) singularity를 만들지 않는다.
- \(W_h\)는 `exp(-L*(h-v))`로 평가한다. `exp(-L*h)*exp(L*v)`로 인수분해하면 stiff 구간에서 불필요한 overflow와 `0*inf`를 만들 수 있다.
- \(K_E\)는 forcing 시점 \(E(v)\), 감쇠율 \(L+1\), 그리고 현재 anchor를 사용한다. Energy를 midpoint에서 다시 freeze하지 않는다.
- Signed \(r\), direct 항과 field response가 크게 상쇄될 수 있다. 가까운 두 큰 총량의 차이만으로 defect를 만들지 않고 명시적인 차이 적분을 유지한다. 작은 defect나 heat에는 declared absolute arithmetic floor를 먼저 적용한다.
- GL interior nodes는 event branch를 가로지르지 않는다. \(q\), \(\lambda_i\)의 mask는 기존 사건 분할이 정한 구간의 branch를 유지한다. Quadrature node나 추가 subdivision을 새로운 physical event로 취급하지 않는다.
- Symbolic ledger closure는 quadrature accuracy를 보증하지 않는다. Endpoint, species counts, heat, source, redshift, seam을 저장된 reference와 각각 비교한다.
- \(P\)와 \(P_f\)의 positivity 정리는 \(P_f+e_1\)의 positivity를 자동 보장하지 않는다. Corrected endpoint의 positivity는 별도 candidate diagnostic이며, endpoint 양성만으로 내부의 모든 stock 또는 species increment 양성을 증명하지 않는다.

Finite rate-switch 사건에서 stock correction은 연속으로 넘긴다. 한 segment에서의 energy 식은 정확하지만, inherited eventwise energy anchor가 미세하게 재설정되면 macro energy ledger에는 그 representation seam이 들어간다. 두 모델이 같은 anchor를 쓸 때 correction의 seam 항은 각 seam에서

\[
 \Delta J_{{\rm anchor},k}^{(1)}
 =\epsilon(E_{{\rm next},0}-E_{{\rm prev},h})e_{1,k}
\]

다. 실제 endpoint export convention에 따른 추가 mismatch도 해당 계약대로 따로 기록한다. 이 항을 opacity-freezing의 물리오차로 합치지 않는다.

HI cutoff에서 stock을 outflow로 이동하는 경우 correction도 live와 outflow 사이에서 동일하게 분배한다. Macro number/energy ledger에는 live, outflow, absorbed, source, redshift와 anchor 항을 포함한다. 현재 first2 zero-outflow 계약 밖의 nonzero outflow 입력이 나타나면 이 공식만으로 silently 지원 범위를 넓히지 않고 scoped stop으로 기록한다.

마지막으로 total discrepancy는 coefficient truncation, quadrature error, incoming uncertainty 및 inherited representation/seam error를 포함한다. 식 (22)만으로 이 모두를 한 번에 인증하지 않는다.

## 9. 실제 새 검산과 claim ceiling

`check_theory_e13c3.py`는 Python 표준 라이브러리의 `Fraction`을 사용한다. 항은

\[
 c\,u^n a^i b^j\exp(\alpha u+\beta)
\]

꼴이며 \(c,\alpha,\beta\)는 exact rational이다. \(a,b\)는 true/approximate incoming defect를 나타내는 **형식적 미지수**다. 미분과 적분을 exact finite exponential-polynomial 대수로 수행하므로 arbitrary incoming dependence를 numerical sampling으로 대체하지 않는다. \(L\)과 \(h\)는 유한 rational controls이며, 이 검산은 모든 coefficient function에 대한 theorem prover가 아니다. 일반식의 정당화는 위 직접 유도에 있다.

새 검산은 \(L=0,1/3,1,7,10^6\), \(h=0,3/7\)에서 response equation, adjoint kernels, terminal values, pointwise count/energy identities, 한 번의 적분으로 계산한 endpoint/두 moments, arbitrary incoming terms, first-order ledger, heat kernel, full-coefficient residual, incoming uncertainty equation과 moment를 확인한다. \(Lh>10^5\) case는 formal exponential algebra control이며 floating-point stiff performance 시험이 아니다. 별도 constant-offset control은 정확한 연속 해를 닫힌형식으로 만들기 위한 algebraic control이고 midpoint 물리 샘플로 취급하지 않는다.

추가로 총 opacity의 상쇄 속에 남는 종별 moment remainder와 \(\mathcal J\)의 zero-rate entire-series 계수를 검사한다. E13C2의 \(h,u\) 총차수 3 Taylor jet 또는 기존 17-check suite를 재사용하지 않았다. 실행 command, Python/platform, script SHA-256, 항목별 판정은 `THEORY_CHECKS.json`과 `THEORY_CHECKS_RUN.json`에 기록한다. 이 contributor가 만든 검산 설계는 독립 final review로 표시하지 않는다.

| Claim | 상태 | 범위 또는 한계 |
|---|---|---|
| Endpoint와 두 moments의 1차원 response 공식 | derived; implementation-verified | 적분 가능한 유한 사건구간; 유한 exact algebra controls |
| 일관된 1차 count/energy ledger | derived; implementation-verified | full-coefficient solution/conservation 판정과 구별 |
| 원래 식의 잔차 \(\delta\Lambda e_1\) | derived; implementation-verified | correction field에 원래 계수를 적용한 residual |
| Incoming uncertainty 및 weighted moment bound | derived | Numerical interval enclosure는 이번 작업에 없음 |
| 여섯 local/full first2 candidate의 실제 정확도·비용 | 별도 owner evidence 필요 | 이 문서의 algebra check로 대신하지 않음 |
| Uniform continuum 또는 physical certificate | NOT_ESTABLISHED | 실제 budget과 outward enclosure가 별도 필요 |

`NEXT_DAG.json`의 최대 1% local total-heat defect 기준은 **사전 선언된 candidate approximation diagnostic**이다. 이를 physical/continuum tolerance로 바꾸지 않는다. 기존 gas algebraic `TOL`도 그 용도로 대체하지 않는다.

보호 상태는 그대로다: baseline RCT **OFF**, actual atomic photon/heat/recoil moments **null**, physical/production **HOLD**, HE-F2/F09 **OPEN**, legacy \(\Gamma=3.543295\) alias **FAIL**, receiver adoption **SEPARATE**. 이 문서는 source, gas path, spectral input 또는 이 상태를 변경하지 않는다.
