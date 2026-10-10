# REI Bianchi-I 입력 blocker: 이론 단계 판정과 공급자 계약

작성일: 2026-10-10. 연구 기준: GPT-6 Astra PHYS–MATH harness 4.0.0. 열람한 저장소 기준은 `17bd1cc0`이며, 이 문서는 생산 코드의 실행 결과를 주장하지 않는다. 하네스의 원본 `state/RESEARCH_STATE.md`는 배포용 `NOT_RUN` 템플릿이므로 연구 증거로 상속하지 않았다.

## 판정

원래 blocker에는 서로 다른 두 문제가 섞여 있다. 첫째는 계산에 넣을 수 있는 정규화된 물리 모델 입력이 없다는 문제이고, 둘째는 선택한 입력·closure·유효범위·오차 예산을 본래의 과학 실행에 채택할 수 있는지의 문제다. 전자는 공개된 실제 source table과 명시적으로 선택한 초기값 문제를 결합하여 해소할 수 있다. 후자는 이번 짧은 조건부 계산만으로 해소할 수 없다. 원래 blocker가 관측으로 확정된 Bianchi 우주를 반드시 요구한다는 뜻은 아니다. 이 구분을 지키면 새 임의 함수로 잔차를 맞추는 manufactured solution 없이도 첫 coupled interval을 실행할 수 있다.

추천 후보는 **HM12의 원저자 배포 emissivity를 공급원으로 사용하는, prescribed exact dust+Λ LRS Bianchi-I 배경 위의 조건부 H/He 복사·열 진화**다. `UVB.out`은 최초 시각의 복사 Cauchy 자료로만 사용한다. 이후의 `J_ν(t)` 또는 `Γ(t)`를 해로 강제하지 않는다. 이 입력은 `SOURCE_BACKED_CONDITIONAL_MODEL`이며 `OBSERVATIONAL_UNIVERSE`가 아니다. HM12 emissivity는 관측을 이용한 합성 모델의 출력이지 관측 원자료 자체도 아니다.

**사전 claim ceiling:** 첫 interval에서 공급원이 실제 원저자 table에 연결되었는지, 정규화·보존식·수렴이 닫히는지까지 검증한다. 전 재이온화사, 물리 closure 오차의 인증, Bianchi shear 측정, 관측적 정당화, HM12 원 계산의 재현을 주장하지 않는다. 기존 `PhysicalHistory` admission을 메타데이터가 채워졌다는 이유로 개방하지 않는다.

## 공급원이 실제로 존재하는가

Haardt–Madau 원저자 페이지는 입력 G+Q comoving emissivity와 출력 UVB spectrum을 별도로 제공한다 [S1]. 실제 table header에서 둘 다 `CUBA V6.3 Nov 2011`, redshift 60개가 확인되었다. `emissivity.out`의 단위는 `erg s^-1 Mpc^-3 Hz^-1`, `UVB.out`의 단위는 `erg s^-1 cm^-2 Hz^-1 sr^-1`, 첫 열은 Å 파장이다 [S2,S3]. 따라서 단순 photo-rate table을 공급원으로 오인할 필요가 없다.

다운로드 후 원 bytes의 SHA-256·size·URL·acquired_at을 기록하고 source table을 create-only로 보존한다. 파서가 header와 row shape를 실제 검사해야 한다. 웹 검색의 렌더링이나 이 문서의 숫자는 raw source bytes를 대신하지 않는다. 이 이론 단계 자체에서는 다운로드 완료나 bytes identity를 주장하지 않는다.

HM12의 원 논문은 `(Ω_m,Ω_Λ,Ω_b,h)=(0.3,0.7,0.045,0.7)`를 사용한다 [S4]. 이 값을 **선택한 역사적 baseline의 매개변수**로 가져오며 현재 최선의 우주론 적합값이라고 부르지 않는다. 원 source table의 redshift를 비등방 우주의 방향별 관측 redshift라고 해석하는 것도 금지한다.

## 1. 배경과 시각 좌표 — derived

signature는 `(-,+,+,+)`이고 `t`는 비회전·비경사 comoving gas의 proper seconds다. 코드의 `AxisymmetricPoint`와 같은 convention을 사용한다.

\[
ds^2=-c^2dt^2+a^2(t)e^{-2b(t)}(dx^2+dy^2)+a^2(t)e^{4b(t)}dz^2,
\quad s=\dot b,
\]
\[
H_\perp=H-s,\quad H_\parallel=H+2s,\quad H=\dot a/a,
\quad \theta=3H,\quad \sigma^2\equiv\tfrac12\sigma_{ij}\sigma^{ij}=3s^2.
\]

직교 tetrad의 shear eigenvalue는 `(-s,-s,2s)`다. 좌표 공변 성분에 단순 `a^-3` 법칙을 적용하면 scale factor가 누락되므로, shear 법칙은 이 tetrad 성분에 적용한다. 일반 비경사 perfect-fluid Bianchi-I 해의 구조는 [S6]의 2.3–2.7 및 2.19식과 일치한다.

중력원은 dust와 Λ로 한정한다. 복사와 가스 thermal energy의 metric backreaction은 test-field 근사로 제외한다. 그러면 Einstein constraint와 traceless spatial equation으로

\[
3H^2=8\pi G\rho_m+\Lambda c^2+3s^2,\quad
\dot\rho_m+3H\rho_m=0,\quad \dot s+3Hs=0.
\]

`a_0=1`, `H_fid=70 km s^-1 Mpc^-1`를 정의하고

\[
F(a)=H_{\rm fid}^2(0.3a^{-3}+0.7),\qquad
s(a)=s_0a^{-3},\qquad H(a)=\sqrt{F(a)+s_0^2a^{-6}}.
\]

여기서 `H_fid`는 HM12의 flat baseline scale이며 shear가 있을 때 정확한 현시각 `H(1)`와 동일하지 않다. `H(1)=H_fid`를 강제하려면 `Ω_Λ=1-Ω_m-Ω_σ0`로 다시 정의해야 한다. 두 convention을 섞지 않는다.

최초 `a_i=(1+z_i)^-1`에서 signed ratio `r=s_i/H_i`, `|r|<1`를 직접 입력하면

\[
H_i=\sqrt{F(a_i)/(1-r^2)},\qquad s_0=rH_i a_i^3.
\]

예시 선택 `r=10^-3`은 관측에서 얻은 값이 아니라 이론 모델 매개변수다. 작은 값이므로 비등방성을 버리는 것이 아니라, 비등방 characteristic과 shear work가 실제 0이 아닌지를 검사한다. `b_i=0`은 최초 spatial-coordinate normalization이며 `s_i≠0`인 한 FLRW를 뜻하지 않는다.

시각 사상은

\[
t(a)-t_i=\int_{a_i}^{a}\frac{dA}{AH(A)},\qquad
b(a)-b_i=s_0\int_{a_i}^{a}\frac{dA}{A^4H(A)},\qquad
\frac{dt}{dz_a}=-\frac{1}{(1+z_a)H(a)},\quad z_a=a^{-1}-1.
\]

`z_a`는 volume scale label이고 관측 redshift가 아니다. `a>0,H>0`에서 `t(a)`는 단조로우므로 역함수가 존재한다. 실제 photon의 방향별 redshift는 각 scale factor에서 계산한다.

수치 사상에 독립적인 검산식도 있다. `v=a^3`, `D=0.7H_fid^2`, `B=0.3H_fid^2`, `C=s_0^2`, `ω=3√D`이면

\[
v(t_i+\Delta t)=v_i\cosh(\omega\Delta t)
 +\frac{\sqrt{Dv_i^2+Bv_i+C}}{\sqrt D}\sinh(\omega\Delta t)
 +\frac{B}{2D}[\cosh(\omega\Delta t)-1].
\]

작은 `ωΔt`에서 마지막 차이는 `2sinh²(ωΔt/2)`로 계산해 상쇄를 줄인다. 위 식은 `v''=9Dv+9B/2`와 초기 `v'_i=3√(Dv_i²+Bv_i+C)`에서 직접 유도된다. `s_0→0`이면 dust+Λ FLRW, 모든 시간의 `a_⊥²a_∥=a³`, `s a³=s_0`가 검사값이다.

## 2. 핵종 밀도와 정상화 IC — derived / chosen assumptions

`ρ_b0=Ω_b 3H_fid²/(8πG)`와 chosen hydrogen mass fraction `X_H`를 사용해

\[
n_H(a)=\frac{X_H\rho_{b0}}{m_H}a^{-3},\qquad
n_{He}(a)=\frac{(1-X_H)\rho_{b0}}{m_{He}}a^{-3}.
\]

질량 `m_He=4m_H`를 사용하는 경우 이를 mass-number approximation으로 기록한다. `X_H=0.76` 같은 값도 source/assumption ledger에서 선택값으로 분리한다. 모든 H/He charge state의 합은 각각 위 density와 정확히 같고, 전하중성으로 `n_e=n_H x_HII+n_He(x_HeII+2x_HeIII)`다.

기존 FT03 admissible temperature는 30000–110000 K다. 표준 mean-density reionization IGM의 `T~10^4 K`를 넣으면서 guard를 낮추거나 clamp하면 안 된다. 이번 bounded reduced-model 후보의 `T_i=50000 K`는 **warm homogeneous parcel의 선택한 thermal IC**이며, 관측된 평균 IGM temperature라는 주장은 하지 않는다. 별도의 차가운 우주론 IC를 요구하면 low-temperature atomic-provider validation이 실제 선행조건이다. 이것은 데이터의 부재와 별개의 provider-domain blocker다.

최초 ion fractions는 임의 숫자 복사가 아니라 선택한 `T_i`, `n_H,n_He`, 초기 spectrum이 주는 `Γ`에 대한 ionization equilibrium으로 고정할 수 있다. 이는 최초 Cauchy state를 정의하는 모델 선택이며 thermal equilibrium도, 이후의 equilibrium evolution도 뜻하지 않는다. 

\[
A_H=\Gamma_H+\beta_H n_e,\quad R_H=\alpha_H n_e,
\quad x_{HII}=A_H/(A_H+R_H).
\]

He의 `A_1=Γ_HeI+β_HeI n_e`, `A_2=Γ_HeII+β_HeII n_e`, `R_1=(α_HeII+α_DR)n_e`, `R_2=α_HeIII n_e`를 정의하면 division overflow를 피하는 형식은

\[
W_0=R_1R_2,\quad W_1=A_1R_2,\quad W_2=A_1A_2,
\quad (x_{HeI},x_{HeII},x_{HeIII})=\frac{(W_0,W_1,W_2)}{W_0+W_1+W_2}.
\]

전자밀도는 `0≤n_e≤n_H+2n_He` 안에서 charge-neutrality residual의 root를 구한다. 실제 적분 spectrum과 동일 cross-section provider로 `Γ`를 계산한다. 이 식이 FT03와 연결될 때 `α_DR`는 HeII→HeI dielectronic branches의 합이다. Root residual, 모든 species 합, nonnegativity를 출력한다. 실제 숫자는 코딩 단계에서만 `numerically checked`로 승격한다.

양의 photoionization rates와 양의 recombination coefficients에서는 root의 유일성도 보일 수 있다. H의 `x_HII(n_e)`는 `dx/dn_e=-Γ_H α_H/[Γ_H+(β_H+α_H)n_e]^2<0`다. He의 ratio `r_1=A_1/R_1`, `r_2=A_2/R_2`는 둘 다 전자밀도에 대해 감소하고 평균 전하는 `q=(r_1+2r_1r_2)/(1+r_1+r_1r_2)`다. 이 함수는 각각의 ratio에 대해 증가한다: `∂q/∂r_1=(1+2r_2)/(1+r_1+r_1r_2)^2>0`, `∂q/∂r_2=r_1(2+r_1)/(1+r_1+r_1r_2)^2>0`. 따라서 `n_e-[n_H x_HII(n_e)+n_He q(n_e)]`는 엄격히 증가한다. `n_e→0+`와 `n_H+2n_He`에서 부호가 반대이므로 유일한 interior root가 존재한다. 이 유일성의 조건인 양의 세 `Γ`는 채택한 finite band quadrature가 실제 만족하는지 검사해야 한다.

총 thermal energy는 `u_th=(3/2) k_B T(n_H+n_He+n_e)`. 전자밀도를 빼거나 ionization threshold energy를 여기에 넣지 않는다. 후자는 별도 internal/binding ledger다. 모든 다른 핵종은 baseline에서 명시적으로 OFF이다.

## 3. 원 table에서 photon IC와 source로의 변환 — derived

`E=hν`, `ℓ=ln E`, `h=2πℏ`를 사용한다. Photon spectral density를 `n_ℓΩ` = proper volume·log-energy·solid-angle당 photon number로 정의한다. Isotropic intensity에서

\[
u_{\nu\Omega}=J_\nu/c,\qquad
n_{\nu\Omega}=J_\nu/(ch\nu),\qquad
n_{\ell\Omega}=J_\nu/(ch).
\]

따라서 cgs 표를 사용할 때 `n_ℓΩ=J_ν/(c_cgs h_cgs)`는 `cm^-3 sr^-1`이고 SI에는 `10^6`을 곱한다. `4π`를 IC에 두 번 넣지 않는다. 각 quadrature packet의 proper number는 `n_ℓΩ Δℓ ΔΩ`, absolute-comoving count는 여기에 `a_i³`을 곱한 것이다. 실제 구현은 초기 proper volume에 대한 `N_rel=a_rel³ n`을 사용하므로 `N_abs=a_i³ N_rel`이며, 두 정규화를 섞지 않는다.

표의 isotropic, angle-integrated comoving emissivity를 `ε_ν^com`라고 하면

\[
q_{\ell\Omega}(t,E)=
\frac{\epsilon_\nu^{com}(z_a)}{4\pi h\,a^3\,{\rm Mpc}_{cm}^{3}}
\quad[{\rm cm}^{-3}{\rm s}^{-1}{\rm sr}^{-1}].
\]

`q`에 여분의 `c`를 곱하지 않는다. 원 intensity transport 식의 `cε/(4π)`를 `ch`로 나눈 결과이기 때문이다. Å→frequency 변환은 `ν=c/(10^-8 λ_Å)` in cgs, energy는 `E_eV=hν/eV_erg`다. 입력 spectrum이 `ε_ν`이지 `ε_λ`가 아니므로 λ-coordinate table이라고 추가 Jacobian을 intensity 값에 곱하지 않는다. 적분에서만 `dlnν=-dlnλ`를 사용한다.

권장 첫 시각은 source·UVB 두 table의 native column `z_i=5.807`. 이 선택은 interpolation을 줄이며 HM12 model상 H overlap 이후다. 그 뒤 짧은 interval에서 `ε_ν(z_a(t))`만 평가한다. 연속 table interpolation은 log-frequency/선택한 redshift 좌표·zero 처리·domain 밖 fail closed를 contract에 고정한다. 높은 에너지·낮은 에너지 band와 angular quadrature를 기록하고 packet/grid refinement를 비교한다.

전체 원 spectrum 대신 유한 band를 쓸 경우 `BAND_LIMITED_HM12`라고 명시한다. 원 model과의 차이는 적분된 누락 photon number·energy·photoionization/heating tails로 계량한다. 고에너지 boundary inflow를 implicit zero로 버리지 않는다: 밖의 spectrum을 포함한 packets를 운반하거나, 닫힌 truncated model 및 그 유효범위를 선언한다. 고에너지 광자의 secondary ionization을 OFF로 둔 결과는 complete atomic transport가 아니다.

## 4. 비등방 수송, source-opacity 일관성, closure — derived / selected

동일한 geometry의 orthonormal ray에 대해

\[
\frac{d\ln E}{dt}=-H-s(3\mu^2-1),\qquad
\dot\mu=-3s\mu(1-\mu^2).
\]

`s>0`이면 longitudinal direction의 photon이 더 빠르게 redshift한다. `μ=0,±1`은 고정 direction이고 `μ→-μ` reflection symmetry는 유지된다. 각 packet의 comoving spatial covector를 보존해 정확히 transport할 수 있다. Collisionless comoving total photon number는 constant다. proper radiation energy는

\[
\dot u_\gamma+4Hu_\gamma+\sigma_{ij}\pi_\gamma^{ij}=S_\gamma,
\qquad \sigma_{ij}\pi_\gamma^{ij}=2s(p_\parallel-p_\perp).
\]

Source로 최초 `ε`를 사용하면서 evolving opacity는 **같은 evolving H/He state**의 `κ_E=Σ_a n_a σ_a(E)`로 계산한다. 적분 photoionization event는 radiation photon sink, ionic source, `χ_a` binding increase, `(E-χ_a)` heating에 한 번씩만 들어간다. `Γ_a=c∫σ_a n_ℓΩ dℓdΩ`는 결과다. HM12의 `Γ` table을 별도 forcing으로 동시에 넣지 않는다.

실제 coding candidate는 최초 frame의 comoving momentum을 고정 quadrature node로 사용한다. `r=E(t)/E_i`, `a_rel=a/a_i`라 두면 `d³p=a_rel^-3 d³q`에서 `dln E dΩ=a_rel^-3 r^-3 dln q dΩ_i`가 따른다. 초기 proper volume을 기준으로 한 count `N=a_rel³ n`의 source는 따라서 `q_proper/r³`다. 이 Jacobian을 생략하면 비등방적 momentum 격자에서 isotropic physical emissivity를 잘못 정규화한다. 이번 band `10..200 eV`는 최초 `q`의 support이며, 이후 physical energy support는 direction별 characteristic을 따라 변한다. 전 방향을 이미 적분한 `n_log` API에는 angular average weight `dμ/2`를 사용한다.

선택 closure는 기존 reduced microphysics에 맞추어 `CASE_A_ESCAPE_PRIMARY_ONLY`, `C=1`, homogeneous gas, one temperature, charge neutrality, no tilt, no diffuse reabsorption으로 명시한다. RR/DR가 방출하는 총 energy는 escape ledger에 기록하고 active ionizing field에 다시 주입하지 않는다. 방출 photon의 수·스펙트럼은 이 모델에서 결정하지 않으며 active-photon number ledger에 포함하지 않는다. 재결합 사건수와 방출 광자수를 동일시하지 않는다. `CaseAExplicitDiffuse` 또는 `FullCoupledOts`라는 기존 enum 이름으로 이 선택을 대체하면 물리적으로 다른 closure를 승인한 셈이다. 새로운 scoped enum/contract가 필요할 수 있다. 전체 우주에 escape되는 diffuse photon을 영구히 제거하는 근사는 보편적으로 정확한 closure가 아니므로 global history admission은 여전히 닫아야 한다.

기존 prescribed-background 근사에서 gas의 nonrelativistic thermal equation은

\[
\dot u_{th}+5Hu_{th}=\mathcal H-\mathcal C,\qquad
\dot T=-2HT+\frac{2(\mathcal H-\mathcal C)}{3k_B n_{tot}}
-T\frac{\dot n_{tot}|_{chem}}{n_{tot}}.
\]

추가 electron이 생길 때 고정 `u_th`의 temperature가 내려가는 항이 마지막 항이다. Ionization energy, radiation energy, escaping energy를 합한 ledger에는 반응별 net creation이 없어야 한다. Expansion work와 외부 stellar/AGN injection은 닫힌 반응계 ledger와 별도로 측정한다.

## 중요한 반례: UVB 전체 history를 강제하면 무엇이 잘못되는가

원저자 Puchwein et al. (2019) §2.2는 HM12의 사전 emissivity·opacity와 그것을 넣은 시뮬레이션의 ionization history가 일치하지 않을 수 있음을 설명한다 [S5]. 따라서 published `J_ν(z)`를 매번 덮어쓰고, 동시에 새 `κ(n_a)`로 photon absorption을 빼는 방법은 동일한 radiative transfer problem의 forward solve가 아니다. `J_ν(t_i)`만 IC로 사용하면 이후 transient는 새 초기값 문제의 정당한 예측이며 residual을 source에 되먹여 해를 만들어내지 않는다.

또한 HM12 emissivity를 `z_a`에 붙이는 것은 관측적으로 isotropic cosmology에서 추론한 source population을 Bianchi test geometry로 이식하는 **phenomenological assumption**이다. 이를 exact Bianchi galaxy formation 모델이라고 부를 수 없다.

## 코딩 acceptance와 남은 gate

1. 원 bytes two tables가 immutable source manifest에 고정되고 source/IC 단위 변환 테스트가 닫힌다. Table 내용을 임의 analytic spectrum으로 대체하지 않는다.
2. Einstein Hamiltonian, `s a³`, volume, monotone time map이 independent residual로 닫힌다. 단순 constant-H background는 이 후보의 physical background가 아니다.
3. IC species normalization, charge root, chosen temperature, source-backed photon normalization을 출력한다. Warm IC 선택과 exact background assumption을 machine-readable로 보존한다.
4. 첫 실제 coupled interval에서 geometry·source·absorption·ionization·thermal energy가 같은 states에 연결되고, source/radiation data 변경에 출력이 반응한다. Metadata-only pass는 불가하다.
5. step refinement, photon quadrature refinement, 반응별 photon/binding/thermal/escape ledger를 검사한다. 통과 범위는 bounded reduced model이다. 검증 도구 부재는 runtime blocker이지 이론 실패가 아니다.
6. 낮은 온도 또는 diffuse/OTS의 full physical history로 진행하려면 provider domain 확장, physical closure error, source mapping uncertainty, spectral-tail/secondary effects를 별도 gate로 다룬다. 이를 이번 first interval이 자동 충족한다고 상속하지 않는다.

## Source ledger (원문 열람 범위)

- S1: Haardt–Madau CUBA original-author downloads page, https://www.ucolick.org/~pmadau/CUBA/DOWNLOADS.html . 공급원/출력 파일 분리 확인. `supports`.
- S2: Original `emissivity.out`, https://www.ucolick.org/~pmadau/CUBA/Media/emissivity.out . Header와 native redshift labels 확인; 모든 spectrum의 물리 정확성을 감사한 것은 아님. `supports` units/provenance.
- S3: Original `UVB.out`, https://www.ucolick.org/~pmadau/CUBA/Media/UVB.out . Header와 native redshift labels 확인. `supports` IC conversion only.
- S4: Haardt & Madau, ApJ 746 (2012) 125; arXiv:1105.2039v3, https://arxiv.org/pdf/1105.2039 . pp.1–3, cosmology line and Eqs.(1)–(4) 읽음. `supports` historical model / RT definitions; does not establish Bianchi source history.
- S5: Puchwein et al., MNRAS 485 (2019) 47, https://academic.oup.com/mnras/article/485/1/47/5298898 . §2.1–2.2, Eqs.(1)–(7) 및 source-opacity warning 읽음. `limits` HM12-as-global-evolution; motivates same-state opacity.
- S6: Caceres, Castaneda & Tejeiro, arXiv:1003.3491, https://arxiv.org/pdf/1003.3491 . §2.1, Eqs.(2.3)–(2.19) 읽음. `supports` perfect-fluid Bianchi-I scale/shear structure, not the chosen astrophysical IC.

이 문서의 유도는 위 convention과 선택한 초기값 문제에 대한 직접 유도다. 아래에 추가한 배경 수치 검산을 제외한 production implementation verification와 독립 승격 판정은 코딩·review 단계의 실제 evidence와 연결하기 전에는 `NOT_RUN`이다.

## 배경 구현 후 검산 추가 기록

`research/physical_provider_20261010/background.py`를 이론 lane에서 구현하고 실제 실행했다. `BianchiBackground(r=0.001).at(t)`의 반환은 `a_rel,b,H,s,z,nH,nHe`이고 `nH,nHe`는 proper cm^-3, `H,s`는 s^-1이다. 추가 반환 `scale_rel`은 초기 spatial axes에 대한 세 scale factors라서 conserved comoving momentum에 직접 사용할 수 있다. 초기 `b_i`와 absolute mean scale을 혼동하지 않는다.

`background_validation.json`에서 volume, shear constant, Friedmann constraint, conserved nuclei, null-ray covector, FLRW analytic limit, 독립 DOP853 배경 ODE를 확인했다. 최대 정규화 차이는 약 `1.13×10^-15`다. 초기 핵 밀도는 `nH=5.935621973155476×10^-5`, `nHe=4.686017347228008×10^-6 cm^-3`, 초기 `H=2.2148406706029966×10^-17 s^-1`다. 핵 질량은 `m_H=m_proton,m_He=4m_proton` 근사이며 코드·evidence에 명시했다.

`1e11 s` interval의 redshift 역변환 round trip은 최대 약 `6.87 s`이고, double precision으로 `z~5.8`의 매우 작은 변화를 저장하는 조건수 한계에 따른다. 계산한 input-rounding bound는 `23.57 s`이며 geometry identity tolerance와 이 absolute-time representation bound는 구분되어 보고된다. 실제 coupled integrator는 elapsed proper time을 직접 입력하므로 redshift 역변환을 사용하지 않는다. 검산 결과 JSON의 numpy boolean serialization에서 발생한 첫 실패는 물리 실패와 구분해 `background_execution_notes.json`에 보존했고, Python bool 변환으로 수정 후 동일 검산을 다시 실행했다.


## D01: spectral domain correction after first execution

원래 initial-momentum band10–200 eV의 결과를 보존했다. 원자료 적분에서 이 band가 초기 HeII 광이온화의8.576%와 primary heating의53.945%를 native-supported50keV 영역 안에서 누락함을 확인해, active candidate를10–50000eV로 확장했다. 이 변경은 closure나 tolerance 완화가 아니며 원 source의 지지영역을 더 많이 계산하는 변경이다. 상한은 원 단면적 provider의50keV implementation guard다. 그 위의 반응율, secondary/Compton 및 diffuse-photon 오차는 계속 미해결이다. 정확한 수치와 실행 결과는 evidence/VALIDATION.json, extended*.json, input_audit.json을 따른다.
