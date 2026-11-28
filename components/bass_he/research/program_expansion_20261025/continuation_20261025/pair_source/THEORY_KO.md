# H–He 실제 수송 입력에서 유한질량 교환 모멘트로

## 결과와 근거 범위

중성 H–He의 고정 수송 적분 공급자에서 \(\overline Q_{11}\) 입력을 받아, 무상대 drift인 두 Maxwell 분포의 열교환과 작은 상대 drift의 운동량 교환을 연결했다. 소스의 \(\overline Q_{11}\)는 이미 각도·속도 적분된 면적이다. 두 식의 의존성은 하나의 동일한 elastic pair law이며, 해당 교환 모멘트는 전체 미분 단면적을 역구성하지 않고도 얻는다. 실제 fit의 새 평가와 과학 수치 캠페인은 수행하지 않았다.

- **literature-supported / source-intaken:** 아래 원본의 H–He 계수 9행과 Bruno2010 정규화.
- **reused:** HE34의 기존 H–He Q11,Q22 계수 및 당시 scoped 점성 검증. 현재 intake는 두 계수의 원본 일치를 확인한다.
- **derived:** 상대 Maxwell 평균, 열교환 \(G_{ab}\), 선형 drag \(K_{ab}\).
- **implementation:** h_he_intake.py는 원본 intake와 별도 공급된 \(\overline Q_{11}\)의 조건부 변환을 구현한다. 테스트·독립 심사는 중앙 continuation 기록에 연결한다.
- **unresolved:** isotope/state mapping의 실제 채택, calibrated source uncertainty, 선택한 온도의 실제 값, 유한 drift·비열분포·비탄성 채널, 전체 물리 공급자 승인.

## 고정 원전과 실제 바이트

[Bruno et al., Physics of Plasmas 17,112315 (2010)](https://doi.org/10.1063/1.3495980)의 Eq.(1),(2),(11), Table I와 §II.A.2를 사용한다. 이번 세션에서 읽은 [원 논문의 공개 텍스트 사본](https://www.academia.edu/47044258/Transport_properties_of_high_temperature_Jupiter_atmosphere_components)은 정규화·범위·상호작용 출처를 제공한다. 논문 PDF는 재배포하지 않는다.

실제 입력은 공식 [Mutation++ collision database](https://github.com/mutationpp/Mutationpp/blob/58678c0e038eb2f078fed3b45640741fdaf167dc/data/transport/collisions.xml)의 명시적 H–He pair다. CapitelliIntegrals.h의 setFactor(PI), setUnits("Å-Å") 및 CapitelliIntegrals.cpp의 BrunoEq11ColInt::compute_를 함께 읽었다. 원본 코드와 LGPL 고지는 upstream/에 보존하며 데이터 원본은 공동 intake의 ../sources/raw/를 사용한다.

| 대상 | 실제 identity |
|---|---|
| collisions.xml | 155227 B; blob d86bf74e05e6bcac9db67cfc03055621ebed2f8c; SHA256 25e0ac6affa33361e9652d3fd3f43760f40f1a500c0a4993b1ace82c5ce501c2 |
| 기존 HE34 subset | 1840 B; blob 9415f2504660da610793f063c52a2c46c7447395; SHA256 699114aa23d13d38bd1d67fd74358fb52d06c25e8d3c87aa8d282de82dc26542 |
| H–He 명시적 행 | Q11,Q12,Q13,Q14,Q15,Q22,Q23,Q24,Q33 |
| 기존 검증 재사용 행 | Q11,Q22 |
| source label | H, He; isotope index·internal state의 새 채택 없음 |
| 온도 범위 | 50–50000 K, 경계 포함; 외삽 없음 |

[기존 HE34 입력](https://github.com/cosmosapjw-quantum/BASS_HE/blob/c456b05e0f1c53faa3ae36720826f43e57c06a91/research/he34_sandbox_certified_relaxation_20261022/data/NEUTRAL_H_HE_TRANSPORT_SUBSET.json)과 [기존 유도](https://github.com/cosmosapjw-quantum/BASS_HE/blob/c456b05e0f1c53faa3ae36720826f43e57c06a91/research/he34_sandbox_certified_relaxation_20261022/theory/NEUTRAL_TRANSPORT_KO.md)는 변경하지 않는다. D/T 또는 He3로의 질량 대체는 source calibration을 새로 제공하지 않으므로 WU identity·source 근거의 별도 입력으로 다룬다.

## 정규화

상대속도 \(\mathbf g=\mathbf v_a-\mathbf v_b\), COM 산란각 \(\chi\), 미분 단면적 \(d\sigma/d\Omega\)를 쓴다. 비상대론적 \(v_a,v_b\ll c\), \(\mu=m_am_b/(m_a+m_b)\)다. 다음 각도 모멘트의 차원은 \({\rm m^2}\)다.

\[
\sigma_1(g)=\int(1-\cos\chi)d\sigma,\qquad
Q_{\rm cos}^{(\ell)}(g)=\int[1-\cos^\ell\chi]d\sigma.
\]

source의 Eq.(1),(2)는 \(\gamma^2=\mu g^2/(2k_BT)\)에 대해

\[
\overline Q^{(\ell,s)}(T)=
\frac{4(\ell+1)}{(s+1)![2\ell+1-(-1)^\ell]}
\int_0^\infty e^{-\gamma^2}\gamma^{2s+3}
Q_{\rm cos}^{(\ell)}(g)d\gamma.
\]

따라서

\[
\boxed{\overline Q_{11}(T)=\int_0^\infty
e^{-\gamma^2}\gamma^5\sigma_1(g)d\gamma}.
\tag{1}
\]

\(x=\gamma^2\)에서는 \(\overline Q_{11}=\frac12\int_0^\infty e^{-x}x^2\sigma_1(x)dx\)다. \(1-P_2(\cos\chi)=\frac32(1-\cos^2\chi)\)이므로

\[
\overline Q_{22}(T)=\frac12\int e^{-\gamma^2}\gamma^7Q_{\rm cos}^{(2)}d\gamma
=\frac13\int e^{-\gamma^2}\gamma^7\sigma_{2,\mathrm{Legendre}}d\gamma.
\tag{2}
\]

즉 source의 \(\overline Q_{22}(T)\), 고정 에너지의 \(\sigma_2(g)\), transient quadrupole 이완률은 서로 다른 입력이다. 이번 열·선형 운동량 교환은 식(1)을 사용한다.

Bruno Eq.(11)의 계수를 \(a_i\), \(z=\ln T\)로 쓰면

\[
F(T)=(a_1+a_2z)\operatorname{expit}[2(z-a_3)/a_4]
+a_5\operatorname{expit}[2(z-a_6)/a_7],\qquad
\overline Q(T)=\pi\,10^{-20}F(T)\ {\rm m^2}.
\tag{3}
\]

\(F\)는 source-native \({\rm \mathring A^2}\) 계수식이다. \(\pi\)와 면적 변환은 upstream에서 직접 확인했다. adapter는 식(3)을 실행하지 않고 decimal coefficient token을 보존한다.

## 두 Maxwell 분포

서로 구별되는 두 종은 독립적 고전 Maxwell 분포, 수밀도 \(n_a,n_b\), 온도 \(T_a,T_b>0\)를 가지며 우선 평균속도를 0으로 둔다. 정의

\[
M=m_a+m_b,\quad
\mathbf V=\frac{m_a\mathbf v_a+m_b\mathbf v_b}{M},\quad
T_*=\mu(T_a/m_a+T_b/m_b)
=\frac{m_bT_a+m_aT_b}{M}
\tag{4}
\]

에서 \(\langle g_i g_j\rangle=(k_BT_*/\mu)\delta_{ij}\),
\(\langle V_i g_j\rangle=k_B(T_a-T_b)\delta_{ij}/M\)다. 공동 Gaussian의 조건부 평균은

\[
\mathbb E[\mathbf V\mid\mathbf g]
=\frac{\mu(T_a-T_b)}{M T_*}\mathbf g .
\tag{5}
\]

source의 온도 인자는 개별 \(T_a,T_b\)가 아닌 \(T_*\)다. 따라서 범위 판정은 \(T_*\in[50,50000]\ {\rm K}\)에 적용한다. Elastic 상태를 유지하지 않는 internal excitation·반응은 별도 채널이다.

\(g_0=\sqrt{2k_BT_*/\mu}\)와 \(\overline g=2g_0/\sqrt\pi\)를 쓰면

\[
\langle g^3\sigma_1(g)\rangle
=\frac{4g_0^3}{\sqrt\pi}\int_0^\infty
 e^{-\gamma^2}\gamma^5\sigma_1(g)d\gamma
=\frac{4k_BT_*}{\mu}\,\overline g\,\overline Q_{11}(T_*).
\tag{6}
\]

## 유한질량 열교환

한 elastic 사건에서 \(\mathbf V'=\mathbf V\), \(g'^2=g^2\)이며

\[
\Delta\mathbf p_a=\mu(\mathbf g'-\mathbf g),\qquad
\Delta E_a=\mathbf V\cdot\Delta\mathbf p_a,\qquad
\Delta\mathbf p_b=-\Delta\mathbf p_a,\quad
\Delta E_b=-\Delta E_a.
\tag{7}
\]

방위각 평균은 \(\int(\mathbf g'-\mathbf g)d\sigma=-\sigma_1(g)\mathbf g\)다.
구별되는 두 종의 충돌률 측도는 \(n_an_bf_af_b\,g\,d\sigma\,d^3v_a d^3v_b\)이며 동일종 pair-counting의 \(1/2\)를 넣지 않는다. 식(5)–(7)로부터

\[
Q_a=-n_an_b\mu\langle g\sigma_1\,\mathbf V\cdot\mathbf g\rangle
=-n_an_b\frac{\mu^2(T_a-T_b)}{MT_*}\langle g^3\sigma_1\rangle,
\]

\[
\boxed{Q_a=G_{ab}(T_b-T_a),\quad Q_b=-Q_a,\quad
G_{ab}=4k_Bn_an_b\frac{\mu}{M}\,
\overline g\,\overline Q_{11}(T_*)}.
\tag{8}
\]

\([G_{ab}]={\rm W\,m^{-3}\,K^{-1}}\), \([Q_a]={\rm W\,m^{-3}}\)다. 유한질량 인자 \(\mu/M=m_am_b/M^2\)가 열교환 효율을 정한다. 고정된 단원자 종은 \(C_{V,a}=\frac32n_ak_B\)이므로, 교환만 남긴 경우

\[
\dot T_a=Q_a/C_{V,a},\qquad
\frac{d(T_a-T_b)}{dt}
=-G_{ab}(C_{V,a}^{-1}+C_{V,b}^{-1})(T_a-T_b).
\tag{9}
\]

선형 열화 시간은 우변 계수를 평형에서 평가하여 정의한다. 입자 생성·소멸, 분자 내부준위, 팽창 항은 각각 별도 온도방정식 항이 필요하다.

## 작은 drift의 운동량 교환

\(\mathbf U=\mathbf u_a-\mathbf u_b\)가 열속도보다 작으면
\(\partial f_g/\partial U_j|_0=\mu g_jf_g/(k_BT_*)\)와 등방성을 이용하여

\[
\mathbf R_a=-n_an_b\mu\langle g\sigma_1(g)\mathbf g\rangle
=-K_{ab}\mathbf U+O(|\mathbf U|^3),
\]
\[
\boxed{K_{ab}=\frac43n_an_b\mu\overline g\,\overline Q_{11}(T_*),
\qquad\mathbf R_b=-\mathbf R_a.}
\tag{10}
\]

\([K_{ab}]={\rm kg\,m^{-3}\,s^{-1}}\)이다. 식(8)은 무 drift 열원, 식(10)은 drift 1차 힘이다. 이를 \(O(U^2)\)까지 결합할 때 총 frictional heating \(K_{ab}U^2\)와 그 종별 분배를 같은 사건법칙에서 포함해야 한다.

## 부호·극한·소유권

\(T_a=T_b\)이면 \(Q_a=Q_b=0\), 한 밀도가 0이면 교환계수는 0이다. \(T_a>T_b\)이면 \(Q_a<0\)이며

\[
\dot s_{\rm pair}=Q_a/T_a+Q_b/T_b
=\frac{G_{ab}(T_a-T_b)^2}{T_aT_b}\ge0.
\]

무한 target mass 극한에서 \(\mu/M\to0\)이므로 열교환은 사라지지만 \(K_{ab}\)는 유한할 수 있다. 방향 산란과 에너지 열화가 다른 과정임을 확인하는 극한이다.

현재 elastic 채널은 species 수·전하·bound/internal energy를 바꾸지 않는다. Thermal owner는 \(Q_a,-Q_a\) 두 부호를 가진 하나의 pair exchange다. Nonthermal birth energy, chemical binding, nuclear \(Q\), photon absorption은 이 값에 추가하지 않는다. Source-calibrated uncertainty는 입력이 없어 null이다.

## 코드와 다음 입력

load_h_he_fit_input()은 source 바이트, 명시적 한 pair, 아홉 종류와 기존 두 행의 decimal equality를 확인한다. SELECTED_H_HE_SOURCE.json은 그 실제 산출물이다.

conditional_h_he_moments()는 정확히 같은 \(T_*\)의 별도 \(Q_{11}\) 값, evidence locator, mass-binding evidence를 받아 식(8),(10)을 반환한다. 함수는 source uncertainty나 physical provider approval을 생성하지 않는다.

다음 입력은 WU isotope/state/mass의 source mapping, 선택된 \(T_*\)의 실제 \(Q_{11}\) 값·불확실성이다. 그 입력과 별도 수치 allowance가 확보되면 한 pair만 평가해 HE-EXCHANGE/HE-CLOSURE에 전달한다. 전종 campaign이나 HE101의 C8 export는 이 선택 채널의 선행조건이 아니다.

