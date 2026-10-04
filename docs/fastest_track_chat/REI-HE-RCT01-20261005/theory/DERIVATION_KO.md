# REI-HE-RCT01: He RCT 선택·provider·closure의 최소 닫힌 계약

상태: 반응·provider 수치는 문헌/동결 공급 packet 기반(`literature-supported`), 아래 event·에너지·FLRW 식은 `derived`. 실제 Rust 실행 여부는 coding/evidence 기록에서만 판정한다. 대상은 원자율을 새로 계산하는 작업이 아니라 기존 rate provider를 명시적으로 선택하여 소비기에 연결하는 제한된 시작 단계다. 전체 소비기의 기본 설정은 OFF이며 physical source admission은 false다.

## 1. 반응을 먼저 고정한다

선택된 별도 채널은

\[
\mathrm{He}^{2+}+\mathrm H(1s)\longrightarrow
\mathrm{He}^{+}(1s)+\mathrm H^++\gamma.
\tag{R1}
\]

분리된 두 생성 이온과 **일차 광자 한 개**의 spontaneous radiative charge transfer (RCT) 시나리오다. 전자는 HeIII의 포획 bound electron이 되며, 전자 gas에서 전자를 소모하지 않는다. 이는 `HeIII + e -> HeII + gamma` radiative recombination과 다른 반응이다. 역반응·비복사 charge transfer(NRCT)·radiative association(RA)·HeH molecular species는 이 계약에서 제외한다. RA는 생성물이 결합 분자이므로 (R1)의 동일 최종 채널로 더할 수 없다. 별도 excited HeII 생성 채널이나 후속 cascade를 포함하면 에너지와 광자 개수 계약을 다시 작성해야 한다.

반응 identity는 `R_CX:He2+_H1s:He+1s_H+`. 원 자료 연결은 `../sources/snapshots/{KF96_PACKET,GM25_PACKET}.json`과 source ledger를 따른다. KF96의 상세 isotope/state 분해는 자체 원문이 보증하는 정보보다 강하게 주장하지 않는다. packet의 ground-state mapping은 명시적 W82 시나리오다.

| provider | 조건부 상수 k [cm³ s⁻¹] | 동결 수치 window [K] | 해석 |
|---|---:|---:|---|
| KF96_HEIII_HI_RCT_NOMINAL_V1 | 1.00×10⁻¹⁴ | [1000, 10⁷] | nominal compilation prescription; 원문 하한은 약 1000 K |
| GM25_W82_RCX_CONSTANT_200_10000_K_V1 | 1.70×10⁻¹³ | [200, 10000] | Appendix B.3 상수 근사; W82 단면적 재적분은 이번 작업에서 미수행 |

공통 조건은 Maxwell 분포, 공통 T, zero relative drift, 지정된 ground initial state다. 공통 window에서 비율 17은 **미해결 출처 간 차이**이지 검증된 오차막대나 확률분포가 아니다. 두 provider를 더하거나 평균하거나 온도에 따라 자동 전환하지 않는다. hot guard 30,000–110,000 K는 KF96 수치 window에만 속하며 GM25 외삽 근거가 되지 않는다. 상수 근사의 `dk/dT=0`은 실제 산란율 기울기 판정이 아니다. SI 입력을 받을 경우 1 cm³/s = 10⁻⁶ m³/s를 정확히 적용한다.

## 2. 수 밀도·분율과 event ledger

proper 핵 수밀도 n_H, n_He를 cm⁻³, k를 cm³ s⁻¹로 쓴다. 분율은

\[
n_{HI}=n_H(1-x_{HII}),\quad n_{HeIII}=n_{He}x_{HeIII},\quad
n_e=n_Hx_{HII}+n_{He}(x_{HeII}+2x_{HeIII}).
\]

0≤x_HII≤1, 0≤x_HeII, 0≤x_HeIII, x_HeII+x_HeIII≤1. 선택된 율의 proper event density는

\[
R=k(T)n_H(1-x_{HII})n_{He}x_{HeIII},\qquad [R]=\mathrm{cm^{-3}s^{-1}}.
\tag{R2}
\]

서로 다른 두 반응물이라 1/2 조합 인자가 없다. species order `(HI,HII,HeI,HeII,HeIII,e)`에서

\[
\nu=(-1,+1,0,+1,-1,0),\quad \dot n_s|_{RCT}=\nu_sR.
\tag{R3}
\]

핵 보존은 ν_HI+ν_HII=0, ν_HeI+ν_HeII+ν_HeIII=0이고, 전하 보존은 ν_HII+ν_HeII+2ν_HeIII−ν_e=0이다. 따라서 free electron event increment는 정확히 0이다. RCT가 HII를 늘려도 HeIII→HeII 변화가 같은 전하량을 상쇄한다. 원자/이온 수와 전자 수가 모두 같으므로 이 반응만으로 이상 단원자 gas의 총 particle 수는 바뀌지 않는다.

\[
\dot x_{HII}|_{RCT}=k n_{He}(1-x_{HII})x_{HeIII},\quad
\dot x_{HeII}|_{RCT}=+k n_H(1-x_{HII})x_{HeIII},\quad
\dot x_{HeIII}|_{RCT}=-k n_H(1-x_{HII})x_{HeIII}.
\tag{R4}
\]

양의 원소 밀도에서는 R/n_H, ±R/n_He와 같다. 원소 밀도가 0인 경우 그 원소 분율은 물리적으로 정의되지 않는다. 구현이 이 상태를 지원한다면 해당 absent-species derivative=0이라는 명시적 convention을 적용하고 R=0을 보장하거나, 양의 밀도를 요구하여 거절해야 한다. 원소가 없는 상태에서 0/0을 계산해서는 안 된다. n_e rate는 n_H dot x_HII+n_He(dot x_HeII+2 dot x_HeIII)=0이다.

이전 photoionization–recombination ledger의 `n_e + tracked photon number` 항등식에도 새 photon source를 반영해야 한다. RCT는 electron을 바꾸지 않고 photon을 생성하므로, 생성광자의 fraction p_tr가 tracked groups에 들어오면 해당 합의 local RCT source는 p_tr R이다. 전부 escape하는 현재 closure에서는 tracked source=0이고 escaped primary count=R이다. 기존 광자수 보존 항등식을 수정 없이 RCT 포함 네트워크에 적용해 가짜 실패 또는 가짜 보존을 선언하지 않는다.

## 3. 에너지: chemical release와 열은 다르다

중성 ground 원자들을 chemical energy 기준으로 잡으면

\[
U_{ion}=\chi_Hn_{HII}+\chi_{HeI}n_{HeII}
 +(\chi_{HeI}+\chi_{HeII})n_{HeIII}.
\tag{R5}
\]

이 식의 단위는 eV cm⁻³다. 기존 소비기의 threshold convention을 사용하면

\[
\chi_H=13.598434599702\ \mathrm{eV},\quad
\chi_{HeII}=54.41776\ \mathrm{eV},\quad
Q=\chi_{HeII}-\chi_H=40.819325400298\ \mathrm{eV}.
\tag{R6}
\]

(R3)을 (R5)에 대입하면 dot U_ion=−Q R. 이 Q는 **ground channel의 chemical release**이며 개별 방출광자의 에너지라는 뜻은 아니다. 동일 threshold 집합을 주입해야 기존 `hhe_rhs`의 chemical ledger와 닫힌다. threshold를 바꾼 모델에 Q를 하드코딩하면 그 모델의 energy identity가 깨진다.

최초 상대 운동에너지 E, 최종 상대 운동에너지 E′, 방출광자 E_γ에 대해 반동 등을 일관되게 배분한 에너지 보존은 E+Q=E′+E_γ이다. 충돌들의 rate-weighted 일차 광자 평균을 Ebar_γ라 쓰면

\[
\dot u_{RCT}=\epsilon_{eV}(Q-\bar E_\gamma)R,\qquad
\dot U_{\gamma,em}=\epsilon_{eV}\bar E_\gamma R,
\quad \epsilon_{eV}=1.602176634\times10^{-12}\ \mathrm{erg/eV},
\tag{R7}
\]

따라서 dot u+ε_eV dot U_ion+dot U_γ,em=0. 양의 Q라고 열항이 반드시 양수는 아니다. Ebar<Q이면 gas heating, Ebar>Q이면 gas cooling, Ebar=Q이면 이 근사에서 열 변화 0이다. 세 경우는 closure fixture일 뿐 실제 스펙트럼의 예측이 아니다. Ebar의 임의 양의 값이 해당 온도에서 실제 가능하거나 동역학적으로 정확하다는 보증도 하지 않는다. 유한 step에서 u≥0 보장은 별도 positivity/stepper 과제다.

일반적인 Maxwell 평균 rate는

\[
k(T)=\sqrt{\frac{8}{\pi\mu}}(k_BT)^{-3/2}
\int_0^\infty E\sigma_{RCT}(E)e^{-E/(k_BT)}\,dE.
\tag{R8}
\]

(R8)에서 μ를 g, E와 k_B T를 erg, σ를 cm²로 일관되게 쓰면 k의 단위는 cm³/s다.

이 **사건 수 모멘트 하나**로는 photon differential cross section이나 Ebar를 결정할 수 없다. 에너지 모멘트에는 추가로 적분 내부의 사건별 Eγ 가중치가 필요하다. scalar k에서 missing energy를 0 또는 Q로 채우는 것은 별도 물리 가정의 몰래 도입이다. 현재 두 packet 모두 photon/heat/recoil/inverse moment=null을 보존한다.

HeII excited level의 에너지 E_exc>0까지 확장하면 prompt release는 Q_exc=Q−E_exc이고 이후 cascade energy와 photon count를 별도 기록해야 한다. 이를 ground 단일-photon 계약에 섞지 않는다. NRCT의 경우 Eγ=0인 별도 nonradiative channel과 해당 branch energy가 필요하며 RCT scalar율을 재사용하여 두 번 세지 않는다.

## 4. 선택한 최소 closure와 소비기 연결

코딩 시작 scope는 아래 두 개이며 provider 선택과 closure 선택은 독립 필드다.

1. **CountOnly**: (R2)–(R4), primary photons produced=R, chemical release=Q R만 반환한다. thermal rate·escaped energy·group spectrum은 `None/null`; thermal solver에 합성하지 않는다. 생산된 primary count는 provenance count이며 기존 tracked photon group에 자동 더하지 않는다.
2. **EscapedMeanEnergy(Ebar)**: 외부에서 명시한 유한 양의 Ebar를 받아 (R7)을 적용한다. 모든 RCT photon은 tracked ionizing field 바깥으로 즉시 escape한다고 선언한다. 기존 photon group derivative에 RCT source를 넣지 않으며 escaped photon count=R, escaped energy=ε_eV Ebar R을 기록한다. 이는 조건부 opt-in model이며 우주론적 광학적 두께에서 보편적으로 타당하다는 주장과 다르다.

`hhe_rhs`와 합성하는 wrapper는 enabled일 때 둘째 closure만 허용하고, 첫째 상태의 total thermal derivative를 숫자 0으로 대체하지 않는다. 기존 `hhe_rhs`는 그대로 두며 OFF는 기존 결과와 같아야 한다. provider 이름, source identity, T window, conflict acknowledgement, reaction identity와 closure 종류를 결과에서 추적할 수 있어야 한다. Numeric API는 양의 Ebar와 `CALLER_SUPPLIED_NO_ATOMIC_MOMENT` 분류를 노출하며 자유형 origin 문자열을 타입 안에 요구하지 않는다. 정확한 입력 Ebar의 값·근거·선택 목적은 외부 run manifest가 보존한다. 예를 들어 E2의 Q−1/Q/Q+1 선택은 synthetic validation scenario이고 문헌 spectrum에서 얻은 값이 아니다. 이 API 분류 자체는 실제 photon moment의 출처를 제공하지 않는다. payload 검증 실패·범위 밖·nonfinite·미지원 distribution/drift는 명시적 error이고 k=0으로 감추지 않는다.

외부 Ebar 입력은 scalar 에너지 수지를 닫을 뿐 photon spectrum, 각분포, recoil/momentum-transfer tensor를 정하지 않는다. 따라서 Bianchi의 방향 의존 radiation force·tilt 교환항이나 production admission을 이 closure에서 추론하지 않는다.

현재 합성 wrapper는 local RHS의 조건부 보존을 보이는 단계다. production microstep, implicit Jacobian, step integrated event ledger, positivity 및 thermal endpoint는 미연결이다. 따라서 wrapper가 계산 가능하다는 사실을 production source admission과 혼동하지 않는다.

## 5. Multigroup/OTS는 왜 별도인가

추후 photon distribution p(Eγ)를 도입하면 그룹 사건당 광자수 p_g=∫_g p(E)dE와 그룹 에너지 모멘트 m_g=∫_g E p(E)dE가 서로 다른 입력이다. 단일 primary photon이면 tracked+escaped+below-grid의 모든 경로에 대해 Σ p_route=1이고 Σ m_route=Ebar가 성립해야 한다. group centre에 모든 광자를 놓는 것은 별도 근사이며 scalar k로부터 유도되지 않는다. 평균 photon energy 하나도 그룹별 p_g를 결정하지 않는다. 입력 평균이 H/He threshold 위인 사실만으로 모든 photon의 흡수 채널을 알 수 없다.

On-the-spot closure는 어떤 원자 species가 어떤 energy에서 얼마를 흡수하는지의 branching/opacity 또는 transport 근거를 필요로 한다. effective local photoionization을 이미 event에 더했다면 같은 photon을 explicit source로 다시 주입하지 않아야 한다. RCT는 recombination Case-A/B label을 붙이는 것만으로 OTS가 닫히지 않는다. secondary ionization과 excitation·heat 분할을 포함하면 그 closure도 별도다.

## 6. Isolated fixed-density 해석해: 독립 검산용

다른 반응·흐름·팽창이 없고 k가 상수일 때 A=n_HI(0), B=n_HeIII(0), proper progress ξ(0)=0를 두면

\[
\dot\xi=k(A-\xi)(B-\xi),\quad0\le\xi\le\min(A,B).
\tag{R9}
\]

A=B>0이면 ξ=k A²t/(1+kAt). A≠B이면 D=B−A, z=exp(−Dkt)에 대하여

\[
\xi(t)=\frac{AB(1-z)}{B-Az}.
\tag{R10}
\]

초기 기울기는 kAB, t→∞에서 min(A,B), A→B에서 위 equal-density 해로 수렴한다. A=0 또는 B=0이면 ξ=0이다. (R10)을 binary64로 그대로 쓰면 D≈0에서 cancellation이나 큰 음의 D에서 exponent overflow가 생길 수 있으므로 equal-limit/expm1 또는 reservoir-order 교환이 필요하다. 이 문서는 고정밀 fixture로만 사용하며 새 production time stepper를 도입하지 않는다.

상수 Ebar의 escaped closure에서 누적된 chemical/thermal/escaped 변화는 각각 −Qξ, (Q−Ebar)ξ, Ebarξ이고 합은 0이다. emitted primary photon 수밀도는 ξ. 결과는 fractional progress를 넘는 새로운 ionization front나 filling-factor 해가 아니다.

## 7. FLRW normalization과 극한

공통 flow의 homogeneous FLRW, 원소 보존, proper time t, dimensionless a(t)에서

\[
\dot n_s+3Hn_s=\nu_sR,\quad
\dot n_H+3Hn_H=\dot n_{He}+3Hn_{He}=0.
\tag{R11}
\]

n_s/n_element를 미분하면 3H가 상쇄되어 (R4)가 그대로 성립한다. free-electron RCT collision source=0이므로 RCT만 켰을 때 dot n_e+3H n_e=0이지 dot n_e=0은 아니다. comoving count N_s=a³ n_s에는 dot N_s=ν_s a³R이며 −3H N_s를 다시 넣지 않는다.

A_c,B_c를 초기 comoving reactant 수밀도, Ξ를 comoving progress라 두면

\[
\dot\Xi=k(t)a^{-3}(A_c-\Xi)(B_c-\Xi),\quad
\tau(t)=\int_0^t k(t')a(t')^{-3}dt'.
\tag{R12}
\]

(R10)의 kt를 τ로 치환하면 해석해를 얻는다. k,H 상수이고 a=a0 exp(Ht)이면 τ=k a0⁻³[1−exp(−3Ht)]/(3H), H→0에서 k a0⁻³t. dilution으로 finite integrated collision exposure가 남기 때문에 H>0에서 항상 substrate가 완전히 소모되는 것은 아니다. 여기서 thermal gas의 adiabatic work와 transported radiation redshift는 별도 evolution 항이며 local event energy cancellation만으로 우주론적 총에너지 보존식을 주장하지 않는다.

## 8. 검증과 종료 기준

실제 supplier packet을 통한 rate unit/domain identity, ν 핵·전하·electron null space, density-normalized fraction increments, CountOnly의 missing thermal 거절, explicit mean-energy ledger, OFF baseline identity를 독립 검사한다. provider 두 개의 17배 차이를 상쇄하거나 fit uncertainty로 덮지 않는다. boundary·비유한 입력·과충전 He fractions·source 자동 전환을 negative control로 다룬다. analytic vectors는 출처 fit 재검증과 구별한다.

이 작업의 종료점은 **typed 선택·count ledger·조건부 escaped closure와 local RHS 합성의 구현 검증**이다. spectra/heat moment의 물리 보정, GM25–KF96 불일치 해결, 새 원자 산란, full transport·production thermal stepper·F04·실제 EoR history는 이 완료 판정에 포함하지 않는다.
