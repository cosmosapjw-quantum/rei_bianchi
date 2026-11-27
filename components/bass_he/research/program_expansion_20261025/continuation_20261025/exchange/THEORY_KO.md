# HE 확장: 유한질량 교환과 열·입자수의 단일 소유권

## 결과와 적용 범위

이 단위는 선택된 미분 충돌 공급자를 종별 운동량·운동에너지·STF 모멘트로 연결하는 계산식과, 그 결과를 thermal population에 투영하는 소비자 인터페이스를 구성한다. 식 (1)–(16)은 아래 조건에서 직접 유도한 결과다. `exchange_closure.py`는 해당 대수 사상과 입력 검사를 구현한다. 작성 시점의 새 실행 상태는 **NOT_RUN**이며 실행·독립 검토의 최종 결과는 부모 단위의 검증 기록이 소유한다. 이 문서의 완료를 실제 단면적·공통 온도·물리 production 승인으로 바꾸지 않는다.

국소 정규직교 frame, proper volume와 proper time, signature `(-,+,+,+)`를 사용한다. 질량 kg, 속도 m s⁻¹, 에너지 J, pressure J m⁻³, source W m⁻³, cross section m²다. `c`, `ħ`, `k_B`를 1로 두지 않는다. 충돌 운동학은 비상대론적이고 각 retained species의 kinetic mass가 일정하다. Binding/internal energy는 별도다. Nuclear mass defect 또는 relativistic daughter를 이 운동학에 자동 삽입하지 않는다. Spatial transport를 생략하는 균질 적용에서는 heat-flux divergence가 0이며, 일반 국소 에너지식에는 그 항을 명시적으로 남긴다.

원 HE33의 pressure/thermal equation, HE36의 reactive centralization, HE38의 finite-mass event conservation을 **불변 파일에서 실제로 읽어** 재사용했다. 원 파일의 전체 text와 blob identity는 `source_snapshots/` 및 `PROVENANCE.json`에 보존했다. 기존 실행을 재수행하지 않았다. HE101의 C8 export와 소진 예산은 이 단위에 들어오지 않는다.

## 1. 입자 생성이 있는 raw source와 중심 source

한 종에 대해 number source를 \(\Gamma_s\), mass source를 \(S_s=m_s\Gamma_s\), 보존형 momentum source를 \(\mathbf R_s\), raw translational kinetic-energy source를 \(E_s\)라 하자. 모두 같은 분포의 gain−loss 모멘트다. \(\rho_s=m_sn_s\), 평균속도 \(\mathbf u_s\)일 때

\[
\partial_t\rho_s+\nabla\cdot(\rho_s\mathbf u_s)=S_s,
\qquad
\partial_t(\rho_s\mathbf u_s)+\nabla\cdot(\rho_s\mathbf u_s\mathbf u_s+P_s)=\mathbf R_s.
\tag{1}
\]

Momentum 방정식에 \(\mathbf u_s\)를 곱하고 continuity를 사용하면 bulk kinetic-energy source는

\[
\mathbf u_s\cdot\mathbf R_s-\frac12u_s^2S_s.
\]

따라서 total kinetic energy에서 bulk energy를 빼서 얻는 central heat source는

\[
\boxed{Q_s=E_s-\mathbf u_s\cdot\mathbf R_s+\tfrac12u_s^2S_s.}
\tag{2}
\]

Acceleration/drag source를 \(\mathbf F_s=\mathbf R_s-\mathbf u_sS_s\)로 정의하는 표기에서는 같은 식이

\[
\boxed{Q_s=E_s-\mathbf u_s\cdot\mathbf F_s-\tfrac12u_s^2S_s}
\tag{3}
\]

가 된다. **Raw \(\mathbf R_s\)에는 plus, acceleration \(\mathbf F_s\)에는 minus**다. 서로 다른 momentum source convention을 섞으면 birth/death heat의 부호가 틀린다. HE36 §8의 central second-moment source

\[
C_s=R_{2,s}-\mathbf u_s\mathbf R_s^T-\mathbf R_s\mathbf u_s^T+S_s\mathbf u_s\mathbf u_s^T
\]

에 \(\operatorname{tr}/2\)를 취해도 (2)가 나온다.

Galilean frame change \(\mathbf v'=\mathbf v-\mathbf w\)에는

\[
S_s'=S_s,\quad \mathbf R_s'=\mathbf R_s-\mathbf wS_s,
\quad E_s'=E_s-\mathbf w\cdot\mathbf R_s+\tfrac12w^2S_s.
\tag{4}
\]

\(\mathbf u_s'=\mathbf u_s-\mathbf w\)와 함께 (2)에 넣으면 \(Q_s'=Q_s\)다. 새 입자가 \(\mathbf v_b\)로 태어나면 \(E_s=\tfrac12S_sv_b^2\), \(\mathbf R_s=S_s\mathbf v_b\)이므로 \(Q_s=\tfrac12S_s|\mathbf v_b-\mathbf u_s|^2\)다. 이것은 주어진 kinetic pool의 central energy injection이며, fast population에서 thermal pool로 옮겨지는 시간척도를 정하지 않는다.

Fixed-number elastic pair에서는 \(S_a=S_b=0\), \(\mathbf R_a+\mathbf R_b=0\), \(E_a+E_b=0\)이다. 따라서

\[
Q_a+Q_b+\mathbf u_a\cdot\mathbf R_a+\mathbf u_b\cdot\mathbf R_b=0.
\tag{5}
\]

\(\mathbf R_a=-\xi(\mathbf u_a-\mathbf u_b)\), \(\xi\ge0\)라면 \(Q_a+Q_b=\xi|\mathbf u_a-\mathbf u_b|^2\). 서로 다른 bulk를 갖는 종의 heat source를 단순히 \(Q_a=-Q_b\)로 강제하면 drift thermalization을 지운다.

## 2. 유한질량 탄성 사건의 angular transport

\(M=m_a+m_b\), \(\mu=m_am_b/M\), \(a=m_a/M\), \(b=m_b/M\)라 두고

\[
\mathbf V=a\mathbf v_a+b\mathbf v_b,\quad \mathbf g=\mathbf v_a-\mathbf v_b,
\quad \mathbf v_a=\mathbf V+b\mathbf g,\quad \mathbf v_b=\mathbf V-a\mathbf g.
\]

탄성 두 입자 사건은 \(\mathbf V' =\mathbf V\), \(|\mathbf g'|=|\mathbf g|\)를 만족한다. 그러면

\[
\Delta\mathbf p_a=\mu(\mathbf g'-\mathbf g)=-\Delta\mathbf p_b,
\quad
\Delta K_a=\mathbf V\cdot\Delta\mathbf p_a=-\Delta K_b.
\tag{6}
\]

미분 measure가 incoming \(\mathbf g\) 축에 대해 axisymmetric이고 full COM solid angle을 공급할 때

\[
\sigma_0(g)=\int d\sigma,\qquad
\sigma_l(g)=\int[1-P_l(\cos\chi)]d\sigma\quad(l=1,2)
\tag{7}
\]

를 정의한다. \(\sigma_0\)는 total event cross section이고, 식 (7)의 \(l=0\)을 의미하지 않는다. Azimuth 평균에서 \(\langle\mathbf g'\rangle_\phi=g\cos\chi\hat{\mathbf g}\), \(\langle g'_{\langle i}g'_{j\rangle}\rangle_\phi=P_2(\cos\chi)g_{\langle i}g_{j\rangle}\)이므로

\[
\int\Delta\mathbf p_a\,d\sigma=-\mu\sigma_1\mathbf g,
\quad \int\Delta K_a\,d\sigma=-\mu\sigma_1\mathbf V\cdot\mathbf g.
\tag{8}
\]

Species raw second-moment increment를 \(B_s=m_s(\mathbf v_s'\mathbf v_s'-\mathbf v_s\mathbf v_s)\)로 정의하면

\[
\int B_a\,d\sigma=-\mu\sigma_1(\mathbf V\mathbf g+\mathbf g\mathbf V)-\mu b\sigma_2\mathbf g_{\langle i}\mathbf g_{j\rangle},
\]
\[
\int B_b\,d\sigma=+\mu\sigma_1(\mathbf V\mathbf g+\mathbf g\mathbf V)-\mu a\sigma_2\mathbf g_{\langle i}\mathbf g_{j\rangle}.
\tag{9}
\]

전체 trace는 0이고 전체 STF는 \(-\mu\sigma_2\mathbf g_{\langle i}\mathbf g_{j\rangle}\)다. \(\sigma_1\)과 \(\sigma_2\)는 서로 다른 angular 정보를 측정한다. 예를 들어 정확한 backscatter에서는 \(\sigma_1=2\sigma_0\), \(\sigma_2=0\)이어서 momentum transfer가 있어도 relative quadrupole은 변하지 않는다.

정지 표적 \(\mathbf v_b=0\)에서 \(E_{\rm lab}=m_ag^2/2\)이고

\[
\int\Delta K_b\,d\sigma=\frac{2m_am_b}{M^2}E_{\rm lab}\sigma_1.
\tag{10}
\]

한 사건의 최대 recoil은 \(4m_am_bE_{\rm lab}/M^2\), equal-mass backscatter에서는 incoming kinetic energy 전부다. Heavy target 극한에서 recoil fraction은 \(O(m_a/m_b)\)로 감소한다. Microscopic cross section의 isotope/finite-mass validity는 이 kinematic identity와 별개 입력이다.

실제 volumetric source를 만들려면 (8),(9)에 \(f_a(\mathbf v_a)f_b(\mathbf v_b)|\mathbf g|\,d^3v_a d^3v_b\)를 적분해야 한다. 이 adapter는 그 적분이나 새 분포를 만들지 않는다. External nonthermal distribution/injection/cascade/stopping은 CR, selected thermal coefficient는 해당 source-qualified supplier가 소유한다. Thermal collision integral \(\bar Q^{(l,s)}(T)\)를 \(\sigma_l(E)\) 또는 DCS로 역변환하지 않는다. H–He 실제 \(\bar Q^{(1,1)}\) 입력은 병렬 `pair_source/` 단위의 normalization과 유효범위를 따른다.

Positive angular measure의 두 cosine moment는 \(m_1=1-\sigma_1/\sigma_0\), \(m_2=1-2\sigma_2/(3\sigma_0)\)이고

\[
-1\le m_1\le1,\qquad m_1^2\le m_2\le1.
\tag{11}
\]

코드는 이 유한 moment consistency를 검사한다. 이는 source normalization·spin·exchange·uncertainty 승인과 다른 조건이다. Partial-angle 자료, nonaxisymmetric law, unspecified event/inclusive count는 이 full-angle interface에서 명시적으로 거부한다. Source energy support 밖 평가도 거부한다. Physical evaluation에는 외부 검토가 이미 승인한 source status와 finite-mass validity가 필요하며, 조건부 대수 계산은 `purpose="conditional_algebra"`로 명시한다.

## 3. Thermal number와 heat capacity의 분리

지정된 thermal pool의 상태를 \(n_s,T\), 공급된 count source를 \(\Gamma_s^{\rm th}\)라 한다. 각 molecule은 하나의 translational particle이고 free electron은 별도 particle이다. 원자핵 수나 전하로 thermal particle count를 재구성하지 않는다. WU identity와 CR pool assignment에서 실제 열적 population만 받는다. Nonthermal electron birth는 fast pool에 남고, thermalization transfer가 있을 때만 thermal \(\Gamma_s^{\rm th}\)로 들어온다.

공통 bulk와 공통 temperature가 별도 근거로 채택된 ideal mixture에서

\[
e_{\rm cal}=\sum_s n_s\epsilon_s(T),\qquad
C_V=\left(\frac{\partial e_{\rm cal}}{\partial T}\right)_{\{n_s\}}
=\sum_s n_sc_{V,s}(T),\qquad
Dn_s+\Theta n_s=\Gamma_s^{\rm th}.
\tag{12}
\]

\(e_{\rm cal}\)의 명시적 energy equation은

\[
De_{\rm cal}+\Theta(e_{\rm cal}+p)+\sigma:\pi+\nabla\cdot\mathbf q=Q_{\rm cal}.
\]

Chain rule로 \(De_{\rm cal}=C_VDT+\sum_s\epsilon_s(\Gamma_s^{\rm th}-\Theta n_s)\)를 넣으면

\[
\boxed{C_VDT=Q_{\rm cal}-p\Theta-\sigma:\pi-\nabla\cdot\mathbf q
-\sum_s\epsilon_s(T)\Gamma_s^{\rm th}.}
\tag{13}
\]

마지막 항은 heat-capacity를 채우는 입자수 변화에 대한 chain-rule 항이다. Binding threshold 또는 heat deposition 자체가 아니다. Monatomic translational pool에서는 \(\epsilon_s=3k_BT/2\), \(C_V=3n_{\rm th}k_B/2\). \(\Theta=3H\)를 쓰면 HE33 Eq.(8), HE36 §8과 동일하게

\[
\dot T=-2HT-\frac{T\Gamma_{\rm th}}{n_{\rm th}}
+\frac{2(Q_{\rm cal}-\sigma:\pi-\nabla\cdot\mathbf q)}{3k_Bn_{\rm th}}.
\tag{14}
\]

Energy를 이미 직접 진화시킨 뒤 온도를 복원하는 경로에서는 \(-T\Gamma/n\)를 energy RHS에 다시 넣지 않는다. \(C_V\)와 \(\epsilon_s\)는 caller가 같은 온도·같은 state model에서 공급해야 한다. 코드가 common-T나 rapid thermalization을 선언하지 않는다.

Molecular rotational/vibrational/electronic energy는 다음 중 선택한 하나로 소유한다.

* REC가 level population을 명시적으로 진화: \(e_{\rm int}=\sum_jn_jE_j\)는 별도 population-derived reservoir다. Translational \(C_V\)는 고정 level population에서 계산한다. State transfer의 에너지를 thermal capacity에 추가하지 않는다.
* 검증된 equilibrium reduction: partition function에서 얻는 \(\epsilon_{\rm int}(T),c_{V,\rm int}(T)\)를 (12)에 포함하고 같은 internal component의 독립 reservoir를 제거한다. 필요한 equilibration time 및 observable error gate는 여전히 입력이다.

코드는 internal component ID가 caloric energy와 별도 reservoir에 동시에 있으면 거부한다. 비열적 분포에는 Maxwellian heat capacity를 부여하지 않는다. Nonideal density-dependent caloric laws 또는 time-dependent external internal coordinates에는 (13)에 해당 derivative 항을 추가해야 하며, 이번 ideal-mixture API의 범위 밖이다.

## 4. 단일 energy owner와 population-derived binding

이 단위는 WU의 elementary reaction compiler를 재구현하지 않는다. 이미 공급된 canonical event/transfer의 count·energy receipts만 투영한다. Thermal kinetic, bulk kinetic, nonthermal kinetic, chemical binding, internal excitation, nuclear mass, retained radiation, escaped radiation, neutrino escape, external work는 서로 다른 account다.

각 energy transfer \(k\)는 canonical ID, 하나의 authoritative owner, donor \(d(k)\), receiver \(r(k)\), positive power \(P_k\)를 가진다. 그 두 posting은

\[
\dot e_{d(k)}|_k=-P_k,\qquad \dot e_{r(k)}|_k=+P_k.
\tag{15}
\]

같은 physical component ID의 두 representation과 같은 canonical transfer ID의 재소비를 거부한다. Binding을 population으로부터 계산한다면 그 account에는 **expected derivative witness만** 반환하고 evolved RHS를 만들지 않는다. Caller는 WU stoichiometry로 계산한 \(\sum_s I_s\Gamma_s\)와 이 witness를 비교한다. Explicit binding reservoir를 선택한 경우에는 반대로 population-derived binding energy를 total energy에 또 더하지 않는다. Atomic binding과 nuclear mass-Q의 기준도 WU convention을 받아서 고정하며, 동일 rest/binding defect의 중복 포함 여부를 source review에서 확인한다.

예를 들어 nonthermal→thermal power를 CR가 공급하면 동일 canonical transfer의 두 부호가 각각 reservoir 감소와 thermal 증가다. Birth spectrum만 있을 때 thermal deposition posting을 만들지 않는다. Nuclear Q를 daughter kinetic·photon·neutrino로 분할한 upstream receipt도 그대로 소비하며, 그 합을 thermal heating으로 한 번 더 넣지 않는다. Escaping radiation과 neutrino는 추적된 sink account에 남긴다.

Count receipts에도 `(canonical source ID, population ID)` 중복 검사를 적용한다. 같은 transfer가 fast electron에서 \(-\dot n\), thermal electron으로 \(+\dot n\)를 만드는 것은 두 population에 대한 정당한 두 leg다. Energy만으로 그 particle count를 추정하지 않는다.

## 5. 종 모멘트에서 공통 baryon stress로

\(\rho_b=\sum_s\rho_s>0\), \(\mathbf u_b=\sum_s\rho_s\mathbf u_s/\rho_b\), \(\mathbf w_s=\mathbf u_s-\mathbf u_b\)라 하면 분포의 중심을 바꾸는 항등식으로

\[
P_b=\sum_s[P_s+\rho_s\mathbf w_s\mathbf w_s],
\quad
\pi_b=\sum_s[\pi_s+\rho_s w_{s\langle i}w_{sj\rangle}],
\quad e_{\rm drift}=\frac12\sum_s\rho_sw_s^2.
\tag{16}
\]

`common_bulk_pressure`는 이 항등식만 계산한다. 입력 pressure의 positive moment-cone 승인은 기존 supplier gate를 유지한다. Common bulk를 취했다고 \(\mathbf w_s\)가 0이 되지는 않는다. Drift energy를 별도로 추적하는 representation에서는 이를 thermal caloric energy로 다시 넣지 않는다. Gas→BASS geometry/background/covariant coupling 경계에서는 trace·STF·drift 에너지의 같은 frame/clock을 사용한다.

## 구현 및 검증 인계

식 (2),(4) → `ConservativeSource`; 식 (7)–(11) → `AngularTransport`, `TransportSource`, `elastic_moment_kernel`; 식 (12)–(14) → `CaloricSpecies`, `temperature_rhs`; 식 (15) → `EnergyAccount`, `EnergyTransfer`, `project_energy_transfers`; thermal/fast count projection → `project_population_sources`; 식 (16) → `common_bulk_pressure`다.

`test_exchange_closure.py`의 13개 synthetic control은 reactive boost, drag heating, finite-mass COM/stationary-target/backscatter limits, angular moment cone, source-domain rejection, thermal count, molecular capacity, duplicate ownership, nonthermal pool separation, nuclear daughter partition 및 drift stress를 검사하도록 정의됐다. 기대값은 해당 사건의 직접 보존식과 손계산 가능한 수지에서 정한다. 원 HE33/36/38/101 suite를 import하거나 재실행하지 않는다.

부모 runner의 허용 범위에서 실행할 최소 명령은 다음과 같다.

```bash
python3 -m unittest discover -s research/program_expansion_20261025/continuation_20261025/exchange -p 'test_exchange_closure.py' -v
```

이 명령의 실제 성공 여부는 부모가 결과를 저장한 뒤에만 판단한다. 현재 구현은 공급된 source와 조건 아래의 coefficient/ownership adapter이며, 새로운 IVP·physical coefficient evaluation·HE101 export START는 0이다. 신규 strong no-go는 제안하지 않았으므로 NG1–NG7의 성과 채택은 해당하지 않는다.

### 재사용 원자료

* [HE33 theory](https://github.com/cosmosapjw-quantum/BASS_HE/blob/c456b05e0f1c53faa3ae36720826f43e57c06a91/research/he33_baryon_moment_foundation_20261022/THEORY_KO.md), blob `8b50826120ce34222670d8fd005970c5a6d3e1ab`: pressure moment와 thermal chain rule.
* [HE36 theory](https://github.com/cosmosapjw-quantum/BASS_HE/blob/c456b05e0f1c53faa3ae36720826f43e57c06a91/research/he36_reactive_moment_bridge_20261023/theory/THEORY_KO.md), blob `4ecb6c4defd9718bd2111a206bf131b1192cf43c`: incoming loss와 net source 구분, reactive centralization, 열적 입자수.
* [HE38 derivation](https://github.com/cosmosapjw-quantum/BASS_HE/blob/c456b05e0f1c53faa3ae36720826f43e57c06a91/research/he38_h1_finite_mass_gain_20261023/theory/DERIVATION.md), blob `839e35de2eeb7e13b7cb751063106009d0e51b2e`: finite-mass labelled event conservation와 kinetic/internal defect 분리. 그 문서의 isotropic-Jacobi model을 이 단위의 일반 탄성 source 가정으로 이식하지 않았다.
