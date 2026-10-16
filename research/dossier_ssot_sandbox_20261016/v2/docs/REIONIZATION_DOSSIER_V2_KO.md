# Reionization Dossier II: 물리 정식화에서 Sandbox Rust 개발 SSOT까지

**REI-DOSSIER-SSOT v2.0 | 2026-10-16 KST | 연구/구현 개발 보충본**

> 권위와 범위: 이 문서는 2026-10-14 `Reionization_Standalone_Dossier.pdf`의 대체 출판본이나 모든 절의 새 증명을 주장하지 않는다. 해당 원전을 물리학적 기준으로 삼고, 2026-10-15~16 최신 `rei_bianchi` PR 및 2026-10-16 추가 DAG의 실제 후속 구현 요구사항을 묶은 **개발용 후속 dossier**이다. 우선 대상은 non-tilted homogeneous diagonal/LRS Bianchi I와 matched FLRW이다. 비선형 finite tilt, 11개 Bianchi 종류, full CMB E/B, 공간 patchiness는 별도 조건부 범위다.

## I. 권위, 작업 대상 및 과학적 수용 범위

`rei_bianchi`가 최종적으로 다루려는 계는 Bianchi 시공간에서 photon, H/He 및 trace-isotope 원자 핵수, 전자, 기체 열에너지, 복사/물질 stress를 함께 진화시켜 finite-observer reionization optical depth와 방향 의존 전달량을 생성한다. 방정식의 수학적 정식화, 저장된 실행 증거, 특정 Rust 구현, 그리고 관측적 해석을 각각 독립 기록한다. `PROJECT_STATE.json`의 초기 4-site FLRW 마이크로스텝 인증과 2026-10-16 PR150의 FULL005 원생산 실행은 다른 대상이다.

현재 권위는 `AGENTS.md` 정책, 각 source-owner 실제 커밋, branch별 물리 입력의 immutable identity, 그리고 해당 stage의 raw execution evidence에 있다. `main` SHA `ae3402713c4b6530ab2b27f008f5f5d5c6a999ed`는 과거 소스/compact artifact 기반이며 현대 독립 PR의 선두가 아니다. PR150 current head `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7`와 V11 비교용 frozen native source `6ea2b1b4b3875c9163cafc45efe720afded43fc4`는 정확히 구분한다. PR174의 source-free Python 결과를 current owner Rust 2차 확인으로 승격하지 않는다. 지침의 수치 상한을 유지하고 clipping으로 값을 수선하지 않는다.

증거 상태는 `literature-supported`, `derived`, `numerically checked`, `implementation-verified`, `conjectural`, `unresolved` 중 대상마다 부여한다. 정식화를 완성했다고 해서 production accuracy나 observable fit을 선언하지 않는다. 이번 문서 및 machine contracts가 통과하면 기술적 이행 `DOSSIER-V2 → SYNC-01/FT-B1A/ISO-EOS/RT-R9_R10`로 진행한다. 별도의 신학적/물리학적 novelty 주장은 본 dossier의 목표가 아니다.

## II. 기하, 표기 및 광자 특성선

시그니처는 `(-,+,+,+)`이고 좌표시간은 Bianchi normal의 고유시간 `t`(s)이다. 우선 대각 Bianchi-I:

\[
ds^2=-c^2dt^2+\sum_{i=1}^3a_i(t)^2(dx^i)^2,
\quad a=(a_1a_2a_3)^{1/3},\quad H_i=\dot a_i/a_i,\ H=\tfrac13\sum_iH_i.
\]

선택된 LRS 가변수 `b`와 signed shear rate `s=\dot b`에 대해 `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, 따라서 `H_i=(H-s,H-s,H+2s)`. 대각 직교 tetrad에서 `sigma_ab sigma^ab=6s²`; 이 문서의 정준 양은

\[
|\sigma|=\sqrt{\sigma_{ab}\sigma^{ab}/2}=\sqrt3|s|,\qquad
\Sigma=|\sigma|/H=\sqrt3|s|/H\quad (H>0),\quad r=s/H.
\]

따라서 `r=+0.01`은 `Σ=0.01732…`이고 `sign(s)`를 별도 보존한다. 기존 여러 논문의 `Sigma=|s|/H` 또는 `q_ref`라는 호환 변수는 이 정의와 자동 동치로 사용하지 않는다. 이 두 정의를 혼동하면 shear 민감도뿐 아니라 CMB quadrupole의 정규화가 달라진다. `H=0` turnaround에는 `Σ` 대신 차원 있는 `s, |sigma|`를 보고한다.

Bianchi-I 공간 병진 Killing vector에 의해 `p_i`는 geodesic 상수이다. 정상 관측자 상대 초기 단위 방향 `e_i(t0)`과 에너지 `E0`를 주면

\[
R_i=a_i(t_0)/a_i(t_1),\quad
r_E=\sqrt{\sum_i(e_i(t_0)R_i)^2},\quad
E_1=E_0r_E,\qquad e_i(t_1)=e_i(t_0)R_i/r_E.
\]

이 방향 사상의 입체각 Jacobian은 `J_Ω=(R_1R_2R_3)/r_E³`. 이 식은 기하적 충돌 없는 전달에 **정확**하고 지수 팽창의 Euler 시간적분이 필요 없다. 충돌 없는 scalar 분포함수의 occupation은 characteristic을 따라 보존된다. 반면 packet당 comoving 수, 단위 고유부피에 대한 수밀도, 기체/광자에 전달된 에너지는 동일한 변수가 아니며 `prod a_i`를 통한 부피 변환을 적용한다.

`H_i`를 알고 있어도 source-born photons가 시간마다 서로 다른 Killing constant와 초기 에너지를 가지므로 birth-time 적분을 생략하거나 단일 중간 출생 시간으로 전부 보내면 불연속 문턱값에서 낮은 차수 및 비물리적 가열을 유발한다.

**명시적 물리 영역:** 자유 감쇠 `s∝a^{-3}`와 모든 관측 CMB quadrupole을 해당 모드에 배당하는 가정 아래 CMB 자료가 큰 late-time shear를 제약할 수 있다. 제공된 부가 문서의 `Σ0≲1e-10`은 이 제한된 모델 조건의 규모 추정이지 모든 Bianchi 물리 모델에 대한 보편 theorem이나 재분석된 likelihood가 아니다. 따라서 `r=±0.005`, `±0.01`, `0.1`의 실험은 적어도 해당 자유 감쇠 CMB 적용에서는 `COUNTERFACTUAL`로 라벨링한다. 관측량의 방향 선형항과 평균 스칼라의 대칭성에 따른 2차항을 분리하며 isotropized-H control을 명시한다.

## III. 핵종·전하 상태, 표준화된 밀도, 전자수

원 dossier의 식 (1.15)는 아래 **17상태 기준 벡터**를 사용한다.

`(n, H0, H+, D0, D+, T0, T+, 3He0, 3He+, 3He2+, 4He0, 4He+, 4He2+, 7Li0, 7Li+, 7Li2+, 7Li3+)`.

이 정의는 현재 소스의 모든 확장 상태를 열거하지 않는다. `6Li` charge family, `7Be` 전자포획 및 daughter lithium, 들뜬 준위, 음이온, 분자, 비열 전자 및 광자는 **외부 typed extension**이다. 원 `Y_A=n_A/n_B`는 `n_B` baryon-number density이고 `∑A A Y_A=1`; conditional charge probabilities `P_A(q,α)`의 합은 각 핵종에 대해 1이다. 원자 핵종은 q 전하 상태로 옮겨도 핵수 `n_A=∑_q n_Aq`가 변하지 않는다. 핵반응이 있으면 `∑_A A ν_Ar=0`을 강제한다. **원자 이온화만 있는 RHS와 핵반응 네트워크의 불변량은 다르다.**

`n_B=∑_A A n_A`는 *모든 핵종을 서로 배타적으로 셌을 때* 성립한다. 수소를 `n_H1`로 정의했다면 중수소 2 `n_D`를 추가한다. `n_H`가 모든 수소 동위원소를 포괄한 총 nuclei면 D를 다시 더하면 이중 계수다. helium3와 lithium6/7는 각각 3,6,7을 곱해야 한다. 이 정규화의 소스 필드는 `STATE_VARIABLES.json`과 `PROCESS_OWNER_REGISTRY.json`에서 명시한다.

전하중성이고 반입자/하전 비열 입자에 별도 인벤토리가 없을 때 `n_e=∑_{A,q} q n_Aq`이다. 재이온화 ionized-volume filling factor `Q_V`, HII 분율 `x_HII`, 전자 ratio `n_e/n_H`, mass-weighted `Q_M`는 정의상 서로 다르다. reduced PR104 모형의 `x_e=(1+y_He)Q`는 He singly-ionized sharp-region closure라는 **추가 가정**이 있을 때만 사용한다. 일반 상태는 `x_e=x_HII+y_He(x_HeII+2x_HeIII)`이고 helium charge fractions의 분모를 명시한다. 종속성이 맞지 않는 donor는 저비용 보간으로 고치지 않고 input HOLD로 분류한다.

## IV. 보존적 다중주파수 이온화 복사 및 광자 소유권

기체 common-rest-frame에서 각 absorber `a ∈ {HI,HeI,HeII,D…}`의 proper number density는 `n_a`(m⁻³), 바닥상태 단면적은 `σ_a(E)`(m²), 한 ray/cohort의 optically thin proper-second hazard는

\[
\kappa(t,E,\mathbf e)=c\sum_a n_a(t)\sigma_a(E(t,\mathbf e)),\qquad
\dot N(t)=S(t)-\kappa(t)N(t).
\]

**정확한 source-age Duhamel 해**는

\[
N(t_1)=N(t_0)e^{-\int_{t_0}^{t_1}\kappa dt}
+\int_{t_0}^{t_1}\!S(t_b)\exp\!\left[-\int_{t_b}^{t_1}\!\kappa(t;t_b)dt\right]dt_b.
\]

입자 출생시각 `t_b`의 E/방향도 지오데식 및 원래 source law를 따라 결정한다. `κ`와 `S`를 모두 고정한 국소 제조해는 `h=t1-t0`, `z=-κh`, `φ_1(z)=expm1(z)/z`, `N1=N0 exp(z)+Sh φ_1(z)`이고 흡수수 `A=N0+Sh-N1`. `k→0` 한계는 `N1=N0+Sh`, `A=0`. 큰 optical depth에서는 `φ_1`을 안정적으로 평가해야 하며 negativity를 clipping해서 숨기지 않는다.

각 photon event는 오직 하나의 absorber로 할당된다. `A=∑_a A_a`, `Nold+Nbirth=Nsurv+∑_a A_a`. 에너지 `E≥χ_a`가 **해당 순간**이고 redshift/다른 collision이 없을 때, 흡수는 `−E` radiation, `+χ_a` chemical binding, `+(E−χ_a)` kinetic heat로 배분된다. 따라서 `Δ(E N)+E Nbirth−...` 식의 각 항 표기 부호를 바꾸지 말고 전체 transaction residual로 검증한다. 실제 cosmological transport는 **광자 redshift work**와 thermal/chemical expansion work를 별도 owner로 기록한다. thermalization이 지연되는 경우에는 fast nonthermal electron reservoir를 먼저 거친다.

Case A와 Case B를 같은 recombination event에서 동시에 켜는 것은 에너지/광자 이중 카운트다. Case A의 탈출 광자를 명시 전파하면 Case-B OTS effective opacity/recombination과 XOR로 한다. Grackle rate/thermal 원본의 `CI floor, CE exponential cap, DR structural zero` 등의 함수 분기 부근을 보간하면 의도치 않은 도함수 jump가 생길 수 있으므로 65,537-점 logT rate-table 가속에는 원본 direct fallback guard가 필요하다. 기준 도메인 밖 T는 typed rejection이다.

원 dossier 1.5의 frozen fixed-E/matter absorption reduction은 `u_a(t)=c n_H σ_*∫ r_a dt`, `Ψ(u)=∫ e^{-s(E)·u}dμ0` 및 `α_a=-∂_aΨ`, `β_a=-∂_aΨ_E`로 표현된다. `∇²Ψ`는 비음수 Gram form이다. 단, 이 축약은 source, redshift, 온도, 다른 collision이 동시에 변하는 실제 전체 state의 자동 exact closure가 아니다. 여기서 나온 spectral compression bound는 고정 exposure에서의 error일 뿐 coupled trajectory/output bound를 별도로 전파해야 한다.

## V. 반응 행렬, 열용량, 확장/화학 에너지 방정식

common-rest-frame의 species state `n_s`와 reaction flux `R_r`에 대해

\[
\dot n_s+\Theta n_s=\sum_r \nu_{sr}R_r,
\qquad \Theta=3H\quad(\mathrm{normal,\ homogeneous}).
\]

`w^T ν=0`인 행벡터 `w`는 각 반응의 보존량이다. rest/chemical energy `u_ch=∑ ε_s n_s`의 변화는 `\dot u_ch+Θu_ch=∑_r Δε_rR_r`. 열/화학 합계는

\[
\dot u_{th}+\Theta(u_{th}+p)=Q_{mat}-\sum_r Δε_rR_r.
\]

반응/열 전용 double accounting을 방지하기 위해 `Q_mat`가 어느 photon/escape/nonthermal species의 에너지를 소유하는지 process owner registry에 기록한다. 중복 `RR` 적용 또는 `CMB` 냉각을 별도 두 thermal paths에서 두 번 더하는 것은 수치 정확도 이전의 물리 오류다.

비상대론적 단일 온도 기체의 `u_th=(3/2)n_tot k_B T`, `p=n_tot k_B T`, `n_tot=∑_species n_atoms+ n_e`이고 모든 입자의 통계 가중과 전하상태를 올바르게 세야 한다. derivative를 취하면

\[
\dot T= -\tfrac23\Theta T-\frac{T}{n_{tot}}\frac{D n_{tot}}{Dt}\bigg|_{\mathrm{reactions}}
+\frac{2Q_{th}}{3k_B n_{tot}},
\]

여기서 `D n_tot/Dt|reactions`는 expansion dilution `−Θn_tot`을 제외한 **입자수 변동**이다. 수소만 예로 `n_tot=n_H(1+x)`이면 `−T xdot/(1+x)` 항을 복구한다. D/H thermal CX의 fixed-volume pure pair component가 PASS여도, He spectator heat capacity를 포함한 expanding network EOS가 PASS된 것은 아니다.

새 `ISO-EOS`는 `nuclei_census`, `nonthermal_e`, `thermal_e`, `photon_CMB`, `photon_UV`, `escape`, `gas_work`, `binding`의 단일 소유 권한을 명시한 후 Rust source owner에게 opt-in interface로 전달한다. `AtomicRhs XOR ThermalSubstep`를 어기는 구현은 바로 FAIL이다.

## VI. 빛의 관측: τ, visibility, 방향/관측자 표면

비기울어짐(non-tilted) normal matter에서 Thomson optical depth의 **해당 적분 구간 기여**는

\[
\tau(t_i,t_o)=\int_{t_i}^{t_o} c\,\sigma_T n_e^{rest}(t)dt.
\]

finite tilt가 있다면 normal-time 광선에 대해 `c σ_T n_e^{rest} γ(1−β·e) dt`를 적분한다. electron current `J_e^a=c n_e^{rest} u^a`의 Lorentz contraction은 frame passive invariance를 보장한다. `n_e^{normal}`을 공급하고 `γ`를 또 곱하면 이중계산이다. 원 dossier 1.7의 material age clock `θ`는 proper seconds이고 nontrivial `dθ/dt`; 중성자가 아닌 자유 전자 집단으로 옮긴다고 optical depth 기원이 즉시 discontinuous라 할 수 없다.

`g=dτ/dη * exp(−τ)`는 conformal time 및 적분 방향 convention이 필요하다. bin visibility mass는 `P_bin=e^{-τ_near}−e^{-τ_far}`의 앞뒤 방향을 정확히 정해 비음수를 확인한다. 과거/미래 경계가 unknown일 경우 전체 CMB τ 또는 total visibility probability를 임의로 1로 normalization하지 않고 `null`과 missing-tail budget를 유지한다. PR104 z20→4+ `τ≈0.03744`는 전체 CMB optical depth가 아니다.

고정 observed redshift `1+z_*`의 emission time은 방향 dependent implicit root `G(t_*,Σ,n)=0`이다. derivative에는 `t_*'(Σ)`와 `t_*''(Σ)`가 포함되고, 단순히 fixed-coordinate-time 적분의 응답과 같지 않다. `G_t=0` 인 fold에서는 implicit-function Taylor bound가 통하지 않아 구간 분할/경로 branch를 명시한다. shear signs, source-fluence ages 및 redshift endpoint를 별도 오차 축으로 기록한다.

## VII. 최신 추가 연구의 수치적 귀결과 수용 경계

**PR174 V11 source-free clock [historical reported; independently read]:** Grackle 3.4.1 original literal rates를 source-free H/He 21-state Python Radau 제조 문제에 고정하고, 41/41 테스트 및 144-row independent benchmark에서 CE-only midpoint가 T error를 97–97.5% 줄였으며 all-process midpoint는 non-stiff smooth 영역에서 대략 2차 정확도를 회복한다. 이것은 **native Rust PR150 driver의 실제 결함 원인이나 전체 source-on 2차 수렴을 입증하지 않는다**. 혼합 θ_j 평가 scheme의 국소 defect는 `h²∑_j (θ_j−1/2) DF_j F +O(h³)`이다. 한 process만 midpoint로 바꾸면 다른 first-order clock은 남는다. 물리적 ledger closure와 방법의 2차 시간 정확도는 서로 별개다.

**PR171/PR173 source-age [historical reported]:** age16→32 survivor N 차이 약 90.13495%, integrated HeI event 차이 약 0.001956%; transport32→64 endpoint HeI Γ 차이 0.081248%, integrated HeI event 차이 0.749735% (frozen target 0.5%). 이 값들은 **인접 격자 차이**이며 continuum error bound가 아니다. source optical variable `z=∫ κ dt`를 쓰면 piecewise affine prescribed opacity의 terminal survivor boundary layer를 높은 정밀도로 적분할 수 있지만, 실제 nonlinear feedback의 native reference로 가져오는 것은 별도 과제다. PR173 21-test/21은 확정된 조건부 oracle이지 production native approval이 아니다.

**PR150 FULL005 [historical reported]:** z20→4 FLRW Q512/Q1024 두 history 저장, 기존 그래프·abundances는 재사용. 그 자체로 age/angle/transport spectral/full time convergence는 아니다. 기존 실행을 다시 돌려 증명하지 말고 저장 raw trace와 새 엄격한 axis-separated refinement 결과를 비교하라. source-native Grackle, rec_bianchi, BASS_HE/bass_cr/WU088_HH의 전달 interface는 공급자의 SHA와 적용 범위를 맞춰야 한다.

**PR151 R9 trace elements [historical reported]:** Li/Be 세부 atomic/nuclear branches와 여기에 따른 photon emission/absorption response의 범위가 넓어졌으나, 해당 numerical tests는 independent conditional program의 것. 실제 cosmological irradiation·nonthermal deposition·whole isotope network의 admission에는 사용하지 않는다.

**PR137 unpolarized BASS [historical reported]:** photon/neutrino 분리와 Einstein shear feedback의 finite benchmark가 있으며 Thomson은 photons에만 적용. 이로부터 polarized full E/B collision engine, cosmic global τ 또는 tilt가 자동 구현된 것은 아니다.

## VIII. 샌드박스 중심 개발 전략과 정량 자원 한계

Rust 1.94.1 toolchain이 사용자 제공 tarball로 `/mnt/data/rust-1.94.1-prefix/`에 격리 설치돼 있다. 매 세션 `rustc --version`, `cargo --version`을 확인한다. 기본 `CARGO_BUILD_JOBS=1`, `--offline --locked`, task별 작업 디렉터리, 256MiB(T0)~2GiB(T2) bounded budget를 사용한다. 전체 `RUSTCORE` vendor crate를 무턱대고 다시 compile하지 않는다. 원 코드의 mutable production checkpoint, NCP/로컬 SSH, `main`/기존 PR merge는 수행하지 않는다.

실제 즉시 개발 가능 단위는 `DOSSIER-V2`의 schema+구현, `RT-R9_R10`의 원본 source/domain 수용, `ISO-EOS`의 stoichiometry+heat-capacity 수식, `SA-03`의 저장 endpoint serializer, `FT-B1A`의 saved PR104 read-only collisionless ray, 그리고 `LRS-V11` frozen owner seam adapter 설계/소형 Rust 비교이다. source-age 32→64/full z20→4 campaign은 현재 샌드박스 예산으로 임의 성공을 주장하지 않고 `HOLD_NEW_MATCHED_INPUT_OR_BUDGET` 유지한다. `DAG_NODE_GUIDE_KO.md`의 각 노드 출력과 실패→최소 수정, PASS→후속 행동을 따른다.

## IX. 오늘 첫 구현 단위: exact source-age transport smoke

이번 dossier package의 독립 Rust 참조 크레이트는 위 IV절 고정 `S,κ,E,χ` 시간 박스에서 `N1, Nbirth, Nabsorbed, Eheat, Ebinding`을 계산한다. 참조 목적은 부호, 단위, 작은/큰 optical depth 및 single-owner event/energy를 실제 compile/test로 고정하는 것이다. 이 크레이트는 `repo Rust driver`, `Grackle`, `HyRec`, `real spectra`, `thermal EOS`를 링크하지 않는다. 그러므로 결론은 **CONDITIONAL_MANUFACTURED_SCOPED_RUST_PASS**이며 production solver 승격은 명시적으로 보류한다.

## X. 관측량별 claim과 release admission

- `abundance vs elapsed proper t and actual Tgas`: 저장한 source/IC/model domain과 시간 수렴을 기록한다. 단순 Euler toy를 native physical history로 바꾸지 않는다.
- `directional I_E and I20/I00`: collisionless Killing 경로와 same-H isotropic comparison을 먼저 검증한다. 전자 이력과의 직접 coupling은 Thompson operator 활성 뒤 주장한다.
- `τ, Δτ, visibility`: 실제 n_e rest-current와 관측자 경로 및 tail known 구간만. 시간/밀도/항산화 근사 오차, atomic/source/closure/geometry 오차는 분리한다.
- `sign(s)`-dependent shear response: `Sigma` magnitude와 sign을 함께 보고하고 parameter identification/no-go는 nuisance/likelihood/finite resolution을 포함하기 전 `unresolved`로 둔다.
- `all Bianchi families / finite tilt / nonthermal/nuclear`: 각각 source and closure contract를 충족한 scoped lane만 release.

릴리스 게이트는 `CLAIM_MATRIX.json`의 항목별로 평가하고 한 실험의 PASS를 26개 DAG 전체의 PASS로 승격하지 않는다. 사용자 제공 추가 DAG는 총 **21개의 실명 노드**를 열거하지만 제목에는 18개라고 적혀 있다(Track 0=2, B=6, A=3, C=3, D=3, E=4). 전부 보존하며 새 문서화 1개와 fast-track 4개를 추가한 machine DAG는 **26개**이다.

## XI. 원전·provenance·재개 지점

원 dossier §1.3 Eq(1.15), §1.5 Eq(1.31–1.43), §1.7 Eq(1.49–1.56), §1.9 Eq(1.63–1.75), §2.8 Eq(2.60–2.66)을 사용했다. 정확한 기술 문헌 참조: Verner et al. 1996 ApJ 465 487 DOI 10.1086/177435 (https://www.pa.uky.edu/~verner/photo.html); Smith et al. 2017 Grackle DOI 10.1093/mnras/stw3291 (https://github.com/grackle-project/grackle); Mackey 2012 A&A 539 A147 arXiv:1201.5651; HYREC-2 Lee & Ali-Haimoud 2020 PRD 102 083517 (https://github.com/nanoomlee/HYREC-2). 다른 요소로 Friedrich et al.의 물리 표를 쓰려면 실제 Appendix G pinned source의 정확한 개정·단위·He 태그를 다시 확인할 것. 모든 문헌 참고가 자동 model validation은 아니다.

중요 대조 연결은 `SOURCE_REGISTRY.json`의 PR104/137/150/151/171/173/174, `DAG_CROSSWALK.json`의 기존 `CURRENT_PLAN` 및 `FLRW NEXT_DAG` 매핑에 있다. 다음 작업은 기존 Rust source authority를 정확히 선택한 `SYNC-01`, read-only PR104 curves를 확보한 `FT-B1A`, `ISO-EOS`의 실제 stoichiometric+thermal Rust kernel을 이 순서로 수행한다. 각 턴 말미에 로컬 SHA/패키지 → 별도 GitHub branch/PR → Google Drive와 Library 백업 → Dropbox 가능 시 fileParam 백업을 시도하며 **각 서비스 응답과 실제 재다운로드**를 서로 다른 수준으로 기록한다.