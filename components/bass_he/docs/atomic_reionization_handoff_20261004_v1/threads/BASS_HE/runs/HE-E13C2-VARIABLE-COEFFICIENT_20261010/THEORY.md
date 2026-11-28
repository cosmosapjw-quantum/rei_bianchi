# E13C2: 동일한 affine gas path에서 광원·흡수율 freezing 오차

## 상태와 범위

**근거 상태: `derived`; 국소 다항식 검산 결과는 동봉 JSON에 별도 기록한다.** 이 문서는 물리 유도 contributor의 산출물이며 독립 최종 decision review가 아니다.

기준 입력은 `HE-E13C1-PHOTON-PHYSICS_20261010/code/photon_green.py`, 같은 run의 `README_KO.md`, `NEXT_DAG.json`, `INPUT_PIN.json`이다. E13C1의 frozen-segment Green kernel과 검증 완료 상태는 계승하며 재검증하지 않는다. 본 비교에서는 저장된 두 gas endpoint 사이의 affine path, 배경, source closure, energy anchor, spectral node/weight, 사건 경계를 고정한다. 새로운 gas solve, Newton solve, 전체 시간 이력, 원자 데이터 fitting, 실제 RCT 방출 에너지 모멘트에 대한 물리 승격은 포함하지 않는다.

유도의 목적은 **같은 prescribed path에서 계수를 연속 평가한 광자 해와 각 사건구간의 midpoint에 계수를 고정한 해의 차이**를 분리하는 것이다. 그 차이는 원자 fit의 참오차, gas interpolation의 참오차, spectral quadrature의 참오차, 실제 cosmic history의 참오차를 인증하지 않는다. 수치 계산으로 유한 비교를 하더라도 interval enclosure 없이는 uniform certificate가 아니다.

추가 직접 source read 범위는 4 MB archive 내 radiation.rs의 affine stage, event split, source/rates, HI outflow 부분과 event_anchor.rs, e9_common_domain.cfg다. 해당 파일들은 native_candidate/source/research/transport_20261007/short-hhe-midpoint 아래에 있다. 이 source에서 constant rate, affine gas, 사건별 midpoint freezing, HI 경계 outflow를 확인했다. Source/compiler/kernel fidelity에 대한 완료된 전체 감사는 반복하지 않았다.

하네스는 GPT-6 Astra research v4.0.0의 `PROJECT_INSTRUCTIONS.md` 및 phase 6을 적용했다. 배포 템플릿 `state/RESEARCH_STATE.md`는 미실행 공용 양식이므로 프로젝트 상태의 근거로 사용하지 않았다.

## 1. 정의, convention, 단위

우주 팽창 좌표를 \(s=\ln a\), 사건구간의 시작을 \(s_a\), 국소 좌표를 \(u=s-s_a\in[0,h]\), 중점을 \(m=h/2\)로 쓴다. \(s,u,h\)는 무차원이고, prime은 proper time이 아니라 \(d/ds=d/du\)다. 이 lane은 상속된 scalar characteristic \(E(u)=E_a e^{-u}\)를 사용한다. 이 식을 일반 Bianchi 방향 의존 photon redshift로 승격하지 않는다. 관련 spacetime convention은 \((- ,+,+,+)\)이지만 아래 scalar balance 유도는 metric 재유도를 포함하지 않는다.

\(E\)와 고정 binding energy \(\chi_i\)는 eV이며 \(\epsilon=1.602176634\times10^{-12}\,\mathrm{erg/eV}\)를 유지한다. \(c\)도 명시한다. Native 비교에서 binary64 literal의 exact-lift와 SI 정의 상수의 십진 값을 구별하는 기존 규칙을 유지한다. \(P\)는 상속된 spectral quadrature의 photon stock per H이며, quadrature weight 적용 전후를 섞지 않는다.

\[
 P'=q-\Lambda P,\qquad \Lambda=\sum_i\lambda_i,\qquad
 \lambda_i(s)=\frac{c\,n_{\mathrm{target},i}(s)\,\sigma_i(E(s))}{H(s)}.
\]

\(n_{\mathrm{target},i}\)는 proper \(\mathrm{cm^{-3}}\), \(\sigma_i\)는 \(\mathrm{cm^2}\), \(c\)는 \(\mathrm{cm\,s^{-1}}\), \(H>0\)는 \(\mathrm{s^{-1}}\)이므로 \(\lambda_i\)는 \(s\) 좌표당 무차원 optical depth다. \(q\)는 동일 photon/H 정규화에서 \(s\)당 생성수다. 상속된 source band 내부에서는

\[
 q(s)=\frac{R(s)}{C_E E(s) H(s)},\qquad
 C_E=\frac1{E_{\min}}-\frac1{E_{\max}}.
\]

Source-band 외부는 \(q=0\)이다. 실제 archive source에서 확인한 본 E13C2의 계약은 \(R=10^{-15}\,\mathrm{photons/H/s}\) 상수이며 **별도 RCT emission source를 주입하지 않는다.** 아래 일반 \(R(s)\) 도함수 식은 확장 가능한 유도 형태일 뿐 이 입력을 변경하지 않는다. \(R\)를 affine gas에 따라 다시 평가하는 것은 다른 source model이므로 이 비교에 혼합하지 않는다.

누적량은 각 구간에서 증가분으로 정의한다.

\[
 A_i'=\lambda_iP,\qquad
 B_i'=\epsilon E\lambda_iP,\qquad
 Z'=\epsilon EP,\qquad U=\epsilon EP.
\]

\(A_i\)는 흡수수/H, \(B_i\)는 흡수 에너지 erg/H, \(Z\)는 적색편이 손실 erg/H다. 종별 photoelectron heat를 고정 binding energy로 계산하는 이 closure에서

\[
 Q_i=B_i-\epsilon\chi_iA_i.
\]

흡수 에너지와 heat는 같은 양이 아니다. E13C1의 Verner cutoff \((13.6,24.59,54.42)\,\mathrm{eV}\), 물질 EOS의 binding energy, 별도 35 eV RCT 연구 closure를 서로 대체하지 않는다.

## 2. 연속 해와 frozen 해

구간 내부에서 \(q,\lambda_i\)가 적분 가능하고 \(q,\lambda_i\ge0\)라고 한다. 다음 Green 함수는 smoothness 없이도 정의된다.

\[
 G(u,v)=\exp\!\left[-\int_v^u\Lambda(w)\,dw\right],\qquad 0\le v\le u\le h.
\]

연속 계수 해는

\[
 P(u)=G(u,0)P_a+\int_0^uG(u,v)q(v)\,dv.
\]

Midpoint-frozen 해를 \(\widehat P\)로 표시한다.

\[
 \widehat P'=q_m-\Lambda_m\widehat P,\qquad
 \widehat A_i'=\lambda_{i,m}\widehat P,\qquad
 \widehat B_i'=\epsilon E(u)\lambda_{i,m}\widehat P,\qquad
 \widehat Z'=\epsilon E(u)\widehat P.
\]

여기서는 **에너지 \(E(u)\)를 고정하지 않는다.** 상속된 kernel처럼 \(E\)의 지수 감소는 계속 유지하고 \(q,\lambda_i\)만 고정한다. 이 차이를 생략하면 아래 heat 및 energy bias의 leading term이 달라진다.

## 3. 정확한 signed defect identity

부호 convention을

\[
 e=P-\widehat P,\quad \delta q=q-q_m,\quad
 \delta\lambda_i=\lambda_i-\lambda_{i,m},\quad
 \delta\Lambda=\sum_i\delta\lambda_i
\]

로 고정한다. 두 photon 방정식을 빼면

\[
 e'+\Lambda e=r,\qquad
 r(u)=\delta q(u)-\delta\Lambda(u)\widehat P(u).
\]

따라서 다음은 perturbation order에 대한 가정이 없는 정확한 항등식이다.

\[
 \boxed{e(u)=G(u,0)e_a+
 \int_0^uG(u,v)[\delta q(v)-\delta\Lambda(v)\widehat P(v)]\,dv.}
 \tag{1}
\]

특히 광원의 직접 차이와 photon depletion을 만드는 총 opacity 차이를 signed integrand로 분리할 수 있다. 식 (1)의 feedback에는 연속 Green 함수가 들어간다. 이것을 frozen exponential로 바꾸려면 defect 오른쪽의 \(\widehat P\)도 \(P\)로 바꾼 다른 정확한 표현을 써야 한다.

\[
 e(u)=e^{-\Lambda_mu}e_a+
 \int_0^u e^{-\Lambda_m(u-v)}[\delta q(v)-\delta\Lambda(v)P(v)]\,dv.
 \tag{2}
\]

두 표현에서 Green 함수와 photon factor를 교차 혼용하는 것은 정확한 항등식이 아니다.

### 3.0 Optical depth를 전개하지 않는 선형 response

식 (1)과는 별도로, frozen damping을 정확히 유지한 1차 계수-variation response를

\[
 e_1(u)=\int_0^u e^{-\Lambda_m(u-v)}r(v)\,dv
\]

로 정의한다. 이 식은 \(e_a=0\)에서 정의했으며 \(\Lambda_mh\)를 전개하지 않는다. 식 (2)에서 \(P=\widehat P+e\)를 대입하면 정확한 remainder가 나온다.

\[
 \boxed{e(u)-e_1(u)=-\int_0^u
 e^{-\Lambda_m(u-v)}\delta\Lambda(v)e(v)\,dv.}
 \tag{2a}
\]

\(D_\Lambda=\int_0^h|\delta\Lambda|\,dv\),
\(B_r=\int_0^h(|\delta q|+|\delta\Lambda|\widehat P)\,dv\)라고 하면 true 및 frozen opacity가 비음수인 조건에서

\[
 \sup|e|\le B_r,\qquad
 \sup|e-e_1|\le D_\Lambda B_r.
 \tag{2b}
\]

따라서 \(\delta q,\delta\Lambda\)를 같은 작은 parameter로 변화시키면 remainder는 그 parameter의 2차다. 충분히 작은 **opacity variation의 적분**이 perturbative 기준이며, \(h\Lambda_m\)가 작아야 한다는 요구는 없다. 수치 sampling으로 \(D_\Lambda,B_r\)를 계산한 값은 rigorous enclosure가 아니다.

일반 누적량에 대해서는

\[
 \Delta J^{(1)}_{w,i}=\int_0^h w\delta\lambda_i\widehat P\,du+
 \int_0^h w\lambda_{i,m}e_1\,du,
\]

\[
 \boxed{\Delta J_{w,i}-\Delta J^{(1)}_{w,i}=
 \int_0^h w[\lambda_{i,m}(e-e_1)+\delta\lambda_i e]\,du.}
 \tag{2c}
\]

이 remainder 역시 계수 variation의 2차이고 \(E(u)\) damping은 그대로 유지된다. 큰 base opacity와 작은 coefficient variation을 구별하는 데에는 이 표현이 단순 \(h^3\) 전개보다 적합하다.

Taylor coefficient를 exponential weight와 결합하고 싶다면

\[
 I_n=\int_0^h e^{-\Lambda_m(h-v)}(v-h/2)^n\,dv,\qquad
 C_n=\int_0^h e^{-\Lambda_m(h-v)}(v-h/2)^n\widehat P(v)\,dv
\]

를 써서

\[
 e_1(h)=q'I_1-\Lambda'C_1+\frac12(q''I_2-\Lambda''C_2)
 +\text{계수 Taylor remainder}
\]

로 쓸 수 있다. 이는 \(\Lambda_mh\)를 전개한 식 (7)과 다르다. \(\Lambda_m=0\)에서 문제가 생기는 \(q_m/\Lambda_m\) 형태보다 이 적분 정의 또는 entire-function 표현을 사용한다.

### 3.1 흡수수·흡수 에너지·heat의 직접 항과 feedback 항

\(J_{w,i}=\int_0^h w(u)\lambda_i(u)P(u)\,du\)와 그 frozen 값 사이의 차이는

\[
 \boxed{\Delta J_{w,i}=
 \underbrace{\int_0^h w\,\delta\lambda_i\,\widehat P\,du}_{D_{w,i}:\,\text{직접 종별 opacity 차이}}+
 \underbrace{\int_0^h w\,\lambda_i e\,du}_{F_{w,i}:\,\text{photon field feedback}}.}
 \tag{3}
\]

\(w=1,\epsilon E,\epsilon(E-\chi_i)\)를 각각 넣으면 \(\Delta A_i,\Delta B_i,\Delta Q_i\)다. 선택한 분해는 \(\widehat P\)를 직접 항의 기준으로 사용한다. 다른 대수적 분해도 가능하므로 문서나 구현에서 분해 convention을 바꾸지 않는다.

\[
 K_{w,i}(v)=\int_v^h w(u)\lambda_i(u)G(u,v)\,du
\]

를 정의하고 식 (1)을 식 (3)에 넣어 적분 순서를 바꾸면

\[
 \boxed{
 \Delta J_{w,i}=D_{w,i}+K_{w,i}(0)e_a+
 \int_0^h K_{w,i}(v)\delta q(v)\,dv-
 \sum_j\int_0^h K_{w,i}(v)\delta\lambda_j(v)\widehat P(v)\,dv.}
 \tag{4}
\]

이는 동일한 prescribed path에서 source variation, 자기 종의 opacity variation, 다른 absorber와의 경쟁을 구별하는 정확한 retarded response 식이다. 예를 들어 \(w\ge0\)일 때 양의 \(\delta\lambda_j\)는 feedback 항에서 음의 부호를 가진다. 그러나 \(\delta\lambda_j\)는 구간 안에서 부호가 바뀔 수 있고 자신의 직접 항과 경쟁하므로 전체 종별 오차의 부호를 이 관찰만으로 정할 수 없다.

\[
 \Delta Z=\int_0^h\epsilon E(u)e(u)\,du.
 \tag{5}
\]

흡수 평균 에너지 \(\bar E_i=B_i/(\epsilon A_i)\)를 비교할 때는 \(A_i>0\)인 경우에만

\[
 \bar E_i-\widehat{\bar E}_i=
 \frac{\Delta B_i/\epsilon-\widehat{\bar E}_i\Delta A_i}{A_i}.
 \tag{6}
\]

따라서 count bias와 energy-timing bias가 함께 들어간다. \(A_i\)가 매우 작거나 heat가 거의 0인 경우 작은 분모로 만든 상대오차를 단독 acceptance criterion으로 쓰지 않는다.

## 4. Smooth event-free 구간의 midpoint local bias

이 절에서는 \(q,\lambda_i\)가 한 사건구간 내부에서 세 번 연속 미분 가능하고 관련 도함수가 유계라고 가정한다. \(h\to0\)에서 같은 prescribed gas path 및 계수 함수를 유지한다. Incoming photon stock은 동일하여 \(e_a=0\)이고, \(p=\widehat P(m)\), \(f=q_m-\Lambda_mp\), \(d=q'_m-\Lambda'_mp\)로 쓴다. 모든 생략된 계수와 도함수는 midpoint에서 평가한다.

\(\tau=u-h/2\)라 하면

\[
 \widehat P(u)=p+f\tau+O(h^2),
\]

\[
 r(u)=d\tau+
 \left[\frac{q''-\Lambda''p}{2}-\Lambda'f\right]\tau^2+O(h^3).
\]

\(G(h,u)=1-\Lambda(h/2-\tau)+O(h^2)\),
\(\int_{-h/2}^{h/2}\tau\,d\tau=0\),
\(\int_{-h/2}^{h/2}\tau^2d\tau=h^3/12\)를 식 (1)에 대입하면

\[
 \boxed{
 \Delta P_h=\frac{h^3}{24}
 [q''-\Lambda''p+2\Lambda q'-2\Lambda'q]+O(h^4).}
 \tag{7}
\]

동일한 leading coefficient에서 \(p\)를 시작 stock \(P_a\)로 대체해도 차이는 \(O(h^4)\)다. 이 치환은 leading cubic coefficient의 기호 검산에 사용한다. Homogeneous \(q=0\)일 때 scalar \(\Lambda'\) 항이 소거되는 것은 \(P_h=P_a\exp[-\int_0^h\Lambda]\)와 일치한다. 광원과 opacity의 시간순서 때문에 \(2\Lambda q'-2\Lambda'q\)가 남는다.

구간 내부 photon error는

\[
 e(u)=\frac d2\left[(u-h/2)^2-h^2/4\right]+O(h^3).
 \tag{8}
\]

즉 interior error가 \(O(h^2)\)여도 endpoint error는 midpoint의 홀수항 소거로 \(O(h^3)\)다. 이를 같은 정확도로 혼동하지 않는다.

일반 smooth weight \(w\)에 대해 직접 항과 feedback 항의 leading coefficient는

\[
 D_{w,i}=\frac{h^3}{24}
 [w\lambda_i''p+2\lambda_i'(w'p+wf)]+O(h^4),
\]

\[
 F_{w,i}=-\frac{h^3}{12}w\lambda_i d+O(h^4).
\]

따라서

\[
 \boxed{\Delta J_{w,i}=\frac{h^3}{24}
 [w\lambda_i''p+2\lambda_i'(w'p+wf)-2w\lambda_i d]+O(h^4).}
 \tag{9}
\]

종별 count, absorption energy, redshift는 다음과 같다.

\[
 \boxed{\Delta A_i=\frac{h^3}{24}
 [\lambda_i''p+2\lambda_i'f-2\lambda_i d]+O(h^4).}
 \tag{10}
\]

\[
 \boxed{\Delta B_i=\frac{\epsilon E_mh^3}{24}
 [\lambda_i''p+2\lambda_i'(f-p)-2\lambda_i d]+O(h^4).}
 \tag{11}
\]

\[
 \boxed{\Delta Z=-\frac{\epsilon E_mh^3}{12}d+O(h^4).}
 \tag{12}
\]

Energy bias와 count bias의 차이에 있는 \(-2\lambda_i'p\)가 absorption chronology를 반영한다. Heat는 별도로 가정하지 않고 정확한 선형 결합을 취한다.

\[
 \boxed{\Delta Q_i=\frac{\epsilon h^3}{24}
 \left\{(E_m-\chi_i)
 [\lambda_i''p+2\lambda_i'f-2\lambda_i d]
 -2E_m\lambda_i'p\right\}+O(h^4).}
 \tag{13}
\]

이 leading term의 부호나 상대적 크기는 입력에 따라 달라진다. \(\Lambda\)가 큰 stiff 구간에서 \(h\Lambda\ll1\)가 확보되지 않으면 고정 계수 크기를 전제로 한 위 전개를 uniform stiff error estimate로 쓰지 않는다. 정확한 식 (1)–(5)는 해당 제한을 받지 않는다.

실제 bounded 입력에 대해 owner가 확인한 full macro 폭은 약 \(5.20833333\times10^{-7}\)이고 최대 \(\Lambda h\)는 약 0.64056757이다. 따라서 숫자 \(h\)가 작다는 이유만으로 cubic expansion의 remainder가 작다고 인증할 수 없다. 이번 full6 비교의 정량 판단에는 연속 ODE/retarded 적분 및 numerical refinement를 사용하고, 위 cubic 항은 bias의 성분과 부호를 이해하는 이론식으로 제한한다. Optical depth를 정확히 유지하는 식 (2a)–(2c)가 별도의 stiffness-aware diagnostic을 제공한다.

### 4.1 국소·전역 차이와 source midpoint quadrature

Source injection 차이는

\[
 \Delta N_{\rm src}=\int_0^h\delta q\,du=\frac{h^3}{24}q''+O(h^4),
\]

\[
 \Delta U_{\rm src}=\int_0^h\epsilon E\delta q\,du
 =\frac{\epsilon E_mh^3}{24}(q''-2q')+O(h^4).
 \tag{14}
\]

특히 source가 일정하다는 말은 \(R\) 일정인지 \(q\) 일정인지 구별해야 한다. \(R\)가 일정해도 \(E,H\)가 변하면 \(q\)는 일정하지 않다.

고정된 유한 길이의 path를 사건 경계에서 정확히 나누고 \(h_{\max}\to0\)로 세분화하면, 계수 및 smoothness bound가 그 세분화와 독립이고 안정성이 유지되는 범위에서 \(O(h^3)\) local defect의 누적은 \(O(h_{\max}^2)\)다. 두 macro 사이에서 photon stock을 native endpoint로 다시 reset하면 누적 field feedback을 지워 버리므로 이 전역 비교가 아니다. 반대로 각 frozen 구간을 시작할 때 의도적으로 같은 stock으로 시작하는 실험은 local defect 실험이라고 표시한다.

## 5. Affine gas path에서 도함수의 계산식

Gas fractions를 \(x=x_{\rm HII},y=x_{\rm HeII},z=x_{\rm HeIII}\)로 두면

\[
 r_{\rm HI}=1-x,\qquad r_{\rm HeI}=1-y-z,\qquad r_{\rm HeII}=y.
\]

저장된 macro endpoints 사이에서 \(x,y,z\)가 \(s\)에 affine이면 각 \(r_i''=0\)이다. 조성 simplex는 convex이므로 두 endpoints가 물리 영역이면 affine interior도 \(0\le x\le1\), \(y,z\ge0\), \(y+z\le1\)를 만족한다. 이 사실은 해당 path가 실제 coupled ODE 해임을 보증하지 않는다.

\[
 k_i=\frac{c n_{\rm element(i)}\sigma_i(E)}{H},\qquad
 \lambda_i=k_ir_i,\quad \zeta_H=(\ln H)',\quad
 \alpha_i=\frac{d\ln\sigma_i}{d\ln E},\quad
 \beta_i=\frac{d\alpha_i}{d\ln E}.
\]

상속된 number density가 \(n\propto a^{-3}\)인 경우

\[
 \kappa_i=(\ln k_i)'=-3-\alpha_i-\zeta_H,
 \qquad \kappa_i'=\beta_i-\zeta_H'.
\]

수치적으로 안전한 형태는

\[
 \boxed{\lambda_i'=k_i(r_i'+\kappa_i r_i),\qquad
 \lambda_i''=k_i[2\kappa_i r_i'+(\kappa_i^2+\beta_i-\zeta_H')r_i].}
 \tag{15}
\]

이 표현은 \(r_i=0\)에서도 \(r_i'/r_i\)를 만들지 않는다. \(n\propto a^{-3}\)가 입력 배경의 규칙이 아니면 \(-3\)을 \((\ln n)'\)로, \(\kappa_i'\)를 \((\ln n)''+\beta_i-\zeta_H'\)로 대체한다. Native background가 주어지기 전에 임의의 Friedmann parameter 값을 넣지 않는다.

Source는 \(F=(C_E E H)^{-1}\), \(v=1-\zeta_H\)로 쓰면

\[
 \boxed{q'=F(R'+vR),\qquad
 q''=F[R''+2vR'+(v^2-\zeta_H')R].}
 \tag{16}
\]

Macro-constant \(R\)이면 \(q'/q=1-\zeta_H\),
\(q''/q=(1-\zeta_H)^2-\zeta_H'\)다. \(q=0\)이거나 \(r_i=0\)인 지점에서 logarithmic derivative로 나눌 필요가 없다.

### 5.1 상속된 Verner log-expression의 미분

아래는 `photon_green.py`의 주어진 fit 식 자체를 미분한 결과이며 fit의 물리 정확도를 새로 검증한 결과가 아니다. Active cutoff 내부에서

\[
 t=E/E_0,\quad x=t-y_0,\quad y=\sqrt{x^2+y_1^2},\quad
 D=(x-1)^2+y_w^2,\quad v_\sigma=\sqrt{y/y_a},\quad
 \rho=\frac{v_\sigma}{1+v_\sigma},\quad C=p_{\rm V}/2-5.5-p_{\rm V}\rho/2.
\]

여기서 \(p_{\rm V}\)는 Verner exponent이며 photon midpoint stock \(p\)와 다르다. 그러면

\[
 F_\sigma=\frac{2(x-1)}D+C\frac{x}{y^2},
 \qquad \alpha=tF_\sigma,
\]

\[
 \frac{dF_\sigma}{dx}=
 \frac{2[y_w^2-(x-1)^2]}{D^2}
 +C\frac{y_1^2-x^2}{y^4}
 -\frac{p_{\rm V}\rho(1-\rho)x^2}{4y^4},
\]

\[
 \boxed{\beta=\alpha+t^2\frac{dF_\sigma}{dx}.}
 \tag{17}
\]

Cutoff 바깥의 한 열린 구간에서는 \(\sigma=\lambda=0\)이고 그 구간 내 도함수는 0이다. Cutoff 자체에서는 이 log derivative를 정의하지 않는다. Active domain에서 \(D,y\)가 0인지 여부는 입력 fit과 에너지 domain으로 판단하며 cutoff 아래의 형식적 singular point까지 외삽하지 않는다.

## 6. 사건 경계와 positivity

Source \(E_{\min},E_{\max}\) 통과, 종별 threshold/cutoff 통과, gas macro endpoint, source-rate branch가 바뀌는 곳을 정확히 분리한다. 식 (1)–(5)는 piecewise integrable 계수에도 성립하지만 식 (7)–(17)의 smooth Taylor 전개는 사건을 가로질러 적용하지 않는다. Discontinuity를 한 midpoint cell로 덮으면 일반적으로 local \(O(h^3)\) cancellation이 사라진다.

상속된 사건이 단순한 유한 rate switch라면 \(P,A_i,B_i,Z\)는 사건에서 연속이고 별도 impulsive jump를 넣지 않는다. 사건값 한 점의 계수 선택은 exact integral에 영향을 주지 않지만 endpoint를 직접 찍는 수치 quadrature에는 잘못된 branch를 넣을 수 있다. One-sided convention과 원래 event anchoring을 유지해야 한다.

HI cutoff는 별도의 computational domain 종료도 겸한다. Radiation source는 HI cutoff에 도달한 stock을 다음 live photon state에 남기지 않고 outn과 oute로 옮긴다. 이 경계 이동은 실제 photon destruction이 아니므로 아래 macro ledger에서 outflow를 포함해야 한다. 또한 원 binary64 event anchor는 endpoint 곱셈을 cutoff에 맞추며 adjacent segment energy continuity를 허용오차로 확인한다. 식 (19)는 정확히 이어진 analytic \(E\) 또는 한 segment에서의 항등식이다. Eventwise lifted anchor가 만드는 유한 정밀도 reset이 있다면 macro energy ledger에는 그 boundary mismatch를 representation error로 따로 기록해야 하며 opacity freezing 물리오차로 합치지 않는다.

\(P_a\ge0,q\ge0,\lambda_i\ge0\)이면 Green 표현에서 \(P\ge0\)이고 frozen 해도 동일하게 양수다. 따라서 \(A_i,B_i,Z\)의 증가분은 음수가 아니다. Heat 증가분은 추가로 \(\lambda_i>0\)인 곳에서 \(E\ge\chi_i\)라는 조건 아래 음수가 아니다. \(e,\Delta A_i,\Delta B_i,\Delta Q_i\)는 두 양수 해의 차이이므로 부호 제약이 없다.

## 7. Number 및 energy ledger

각 모델 자체는

\[
 P_h+\sum_i A_i=P_a+N_{\rm src},\qquad
 N_{\rm src}=\int_0^hq\,du,
\]

\[
 U_h+\sum_iB_i+Z=U_a+U_{\rm src},\qquad
 U_{\rm src}=\int_0^h\epsilon E q\,du
\]

를 만족한다. 두 모델을 빼면

\[
 \boxed{e_h+\sum_i\Delta A_i=e_a+\Delta N_{\rm src},}
 \tag{18}
\]

\[
 \boxed{\epsilon E_h e_h+\sum_i\Delta B_i+\Delta Z
 =\epsilon E_a e_a+\Delta U_{\rm src}.}
 \tag{19}
\]

따라서 source coefficient를 연속 평가하면서 생긴 injection 차이를 오른쪽에서 빼지 않은 비교는 freezing bias의 number/energy closure가 아니다. 식 (7), (10)–(12)를 합하면 leading order에서 각각 식 (14)의 \(q''h^3/24\), \(\epsilon E_m(q''-2q')h^3/24\)가 재현된다. Ledger가 닫혀도 종별 흡수 시점, 종별 heat, 혹은 실제 물리 모델의 정확도는 별도 질문이다.

HI cutoff를 포함하는 **macro aggregate**에서는 식 (18)–(19)의 endpoint stock을 live와 outflow의 합으로 바꾼다.

\[
 \boxed{\Delta N_{\rm live}+\Delta N_{\rm out}+\sum_i\Delta A_i
 =\Delta N_{\rm in}+\Delta N_{\rm src},}
 \tag{19a}
\]

\[
 \boxed{\Delta U_{\rm live}+\Delta U_{\rm out}+\sum_i\Delta B_i+\Delta Z
 =\Delta U_{\rm in}+\Delta U_{\rm src}+\Delta J_{\rm anchor}.}
 \tag{19b}
\]

이상적인 연속 energy path에서 \(J_{\rm anchor}=0\)이다. Native의 eventwise energy reset을 그대로 보존하는 표현에서는 \(J_{\rm anchor}\)를 각 경계의 \(\epsilon(E_{\rm next,start}-E_{\rm prev,end})P\) 및 cutoff export mismatch의 합으로 정의할 수 있다. Energy/source residual에서 outflow를 누락하는 것은 물리 보존 실패가 아니라 ledger assembly 오류다. Actual first2 bounded captures에 outflow가 없다는 사실이 source inspection으로 확인되면 해당 계산에서 outflow 항은 0이며, 그 밖의 입력은 별도 domain contract가 필요하다.

## 8. 실제 error bound와 finite diagnostic의 구별

\(G\le1\)이므로 식 (1)에서

\[
 |e(u)|\le |e_a|+\int_0^u
 (|\delta q|+\sum_i|\delta\lambda_i|\widehat P)\,dv.
 \tag{20}
\]

만약 구간 전체에 대해 \(\Lambda\ge\Lambda_{\min}\ge0\), \(|\delta q|\le D_q\), \(|\delta\Lambda|\le D_\Lambda\), \(\widehat P\le P_{\max}\)라는 **enclosure**가 있으면

\[
 |e(u)|\le e^{-\Lambda_{\min}u}|e_a|
 +(D_q+D_\Lambda P_{\max})
 \begin{cases}
 (1-e^{-\Lambda_{\min}u})/\Lambda_{\min},&\Lambda_{\min}>0,\\
 u,&\Lambda_{\min}=0.
 \end{cases}
 \tag{21}
\]

또한

\[
 |\Delta J_{w,i}|\le\int_0^h|w|
 (|\delta\lambda_i|\widehat P+\lambda_i|e|)\,du.
 \tag{22}
\]

\(\Lambda_m>0\)일 때 frozen \(P_{\max}=\max(P_a,q_m/\Lambda_m)\)를 쓸 수 있고, \(\Lambda_m=0\)이면 \(P_a+q_mh\)가 상계다. 단순 절댓값 bound는 midpoint cancellation을 버리므로 국소 endpoint의 \(O(h^3)\)를 날카롭게 인증하지 못할 수 있다.

Sampled maximum, 두 numerical solver의 일치, step-halving ratio, 높은 working precision은 해당 enclosure 자체가 아니다. 이 E13C2에서 수치 산출물을 보고할 때는 `numerically checked` 또는 `implementation-verified`의 유한 범위를 사용하고, `uniform certificate`, `continuous full gas error PASS`, `atomic physical accuracy PASS`로 바꾸지 않는다.

기존 `TOL=[1e-14,1e-14,1e-14,1e-26]`은 gas algebraic residual의 solve tolerance이며 continuum transport truncation의 acceptance budget이 아니다. \(\Delta A_i,\Delta B_i\)를 같은 네 gas residual과 TOL로 투영하면 frozen forcing을 교체했을 때 그 저장 endpoint가 받는 민감도를 측정한다. 그 ratio가 1을 넘는다는 사실은 원 solver tolerance에 비해 변화가 크다는 뜻이며, 별도의 사전 continuum budget 없이 physical accuracy FAIL 또는 acceptable error PASS를 판정하는 기준이 되지 않는다.

## 9. 검산·실패 상태와 다음 계산의 최소 계약

`e13c2_symbolic_check.py`는 외부 symbolic package 없이 exact rational sparse polynomial을 사용하여 smooth Taylor jet를 직접 Picard 적분한다. 실수 sampling이 아니라 \(h,u\) 총차수 3의 formal coefficient 비교다. Endpoint, 일반 weight 흡수, count, energy, redshift, source injection, number/energy ledger를 검사한다. Formal Taylor identity의 구현 검산 범위이며 실제 fit parameter 전역 검증이나 numerical ODE 결과가 아니다.

첫 환경 점검에서 기본 Python과 primary-runtime Python 모두 `ModuleNotFoundError: No module named 'sympy'`였다. 이는 `runtime/environment` 미설치 상태이며 물리·수학 실패가 아니다. 패키지를 설치하거나 network route를 바꾸지 않았고 표준 라이브러리의 가벼운 대수 검산으로 대체했다.

다음 finite numerical 비교는 같은 source authority와 gas path를 유지한 채 photon stock을 연속 전파하고, \(P,A_i,B_i,Z,N_{\rm src},U_{\rm src}\) 및 식 (3)의 직접/feedback 분해를 기록하면 된다. 원 입력에서 source rate가 stage 상수인지 path 함수인지 먼저 명시하고, event-free subsegments만 refine한다. Source/threshold/tolerance/default와 RCT 35 eV closure는 변경하지 않는다. baseline RCT OFF, actual atomic moments null, physical/production HOLD, HE-F2/F09 OPEN, owner adoption 별도라는 상속된 claim ceiling을 유지한다.
