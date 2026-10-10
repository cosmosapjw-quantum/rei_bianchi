# REI-PHYS20: Bianchi-I의 방향별 광흡수·광가열과 각도 평균의 약한 전단 응답

작성일: 2026-10-10 KST. 선행 연구: `REI-PHYS19-20261010`.

## 1. 결론과 연구 범위

이번 연구는 **방향별 물리 효과가 선형으로 존재하면서도, 그 효과의 구면 평균은 선형 차수에서 사라질 수 있는 이유**를 실제 `rei_bianchi`의 photon/source measure와 연결한다. 중요한 결과는 다음과 같다.

1. 같은 평균 팽창과 등방 초기·방출 광원에서 trace-free shear가 만드는 최초 응답은 quadrupole이다. 반응함수와 해의 적절한 미분가능성 아래 연속 구면의 scalar gas/photon observables는 전단의 1차 응답이 0이다. 유계 2차 미분까지 있으면 변화는 전단 적분량의 2차부터 시작한다. 이것은 새로운 물리 closure가 아니라 대칭성과 인과 응답의 결과다.
2. **방출 광자 한 개당 흡수 사건률**, **고정 q-bin의 사건률**, **현재 물리적 입체각당 사건률**은 서로 다르다. 마지막 양에는 angular Jacobian에 따른 추가 `−3 Δβ` 항이 있다. 실제 FT03 soft-HI 상수에서는 빠른 축을 따라 첫 번째 흡수 사건률은 증가하고, 세 번째 사건률과 광가열은 감소하는 작은 커널 사례가 나온다.
3. 현재 source Jacobian 자체는 올바른 연속 측도를 나타낸다. 그러나 native midpoint angular rule은 일반 STF tensor의 2차 구면 모멘트를 정확히 재현하지 않는다. 현재 `BI=(1.01,0.99,1)×10⁻¹⁴ s⁻¹`는 x/y 교환대칭 때문에 1차 상쇄를 보존한다. 이 결과를 임의 방향의 shear로 확장할 수는 없다.
4. 현재 8×16 각도 격자는 이 특별한 x/y 전단의 **선두 2차 free-photon mean-energy 계수**를 연속 구면보다 약 0.971% 크게 준다. 이는 해당 정확 benchmark 계수의 오차이며, 실제 온도·광학깊이 예측의 0.971% 오차라는 뜻이 아니다.
5. threshold에 정확히 놓인 monochromatic line에는 `|shear|` cusp가 생길 수 있다. 따라서 trace-free 조건 또는 `ε↔−ε` 대칭만으로 2차 시작을 주장할 수 없다.

범위는 PHYS19 handoff가 지정한 방향별 characteristic, source measure, 약한 전단의 흡수·가열과 작은 검산이다. FT03는 **prescribed constant-H Bianchi-I** 모델이다. 다른 PR의 Einstein dust+Λ/HM12 provider를 가져오지 않았고, PHYS19의 FLRW 수치오차 경계를 Bianchi 오차 경계로 옮기지 않았다. HH/RCT/CR는 OFF다. 새 gas IVP, native history, NCP, 이전 source/time certificate의 재실행은 0회다.

`physical=HOLD`, 기존 `[160,161] FAIL`, `tick160`, `auxiliary escape FAIL`을 그대로 보존한다. 아래 수학 결과와 작은 진단은 이 판정을 해제하지 않는다.

## 2. 기준 source와 실제 구현의 의미

입력은 repository `cosmosapjw-quantum/rei_bianchi`, branch `forward/rust-reion-kernels-20260922`, PR #83의 commit `718468dc75cb81fdfe0f2792aab5c8d0dbc54607`이다. 전체 tree는 `f2538f9b3db885b0342256729415f983fcf290d4`, scientific Rust source subtree는 `cb69b4736dd046e4675557577eb8e0ead037d1f3`이다. 선행 PHYS19의 source subtree와 일치한다. `SOURCE_MANIFEST.json`은 실제 읽은 파일의 blob SHA, SHA-256, 크기와 pinned URL을 연결한다.

| Source | 확인한 의미 |
|---|---|
| `paired_runtime.rs`, `qhat`, 56–61 | 등간격 μ와 φ의 midpoint product rule, 각 기본 weight 동일. Gauss–Legendre가 아니다. |
| 같은 파일, `g_point`, 109–111 | `g(q,t)=sqrt(Σ q_i² exp(−2H_i t))`. |
| 같은 파일, `source_weights`, 118–131 | `J=exp(−ΣH_i t)/g³`, 실제 weight는 `J_d/ΣJ_e`. |
| 같은 파일, 224–225 | `dt×5×10⁻¹⁵ photons/H/s`를 위 weight로 `13.7 eV` birth node에 투입. |
| 같은 파일, 80–93 | 초기 `0.05 photons/H`, isotropic q weights, 초기 fractions `(0.9,0.3,0.6)`, `T=50000 K`. |
| `paired_history.rs`, 98–107 | Nμ=4,8,16 비교와 x/y opposite shear. Hmean은 `10⁻¹⁴ s⁻¹`. |
| `bianchi_i.rs`, 185–208 | exact energy/direction pullback과 `solid_angle_jacobian`. |
| `atomic_provider.rs`, 328–349 | Verner HI cutoff는 `13.60 eV`; thermal ledger의 χHI는 별도로 `13.598434599702 eV`. |

배열의 photon 값은 고정 q-ray와 physical-energy node에 든 **수소 핵당 광자수**다. Occupation이나 현재 입체각당 intensity를 저장한 배열로 해석하면 안 된다. 이 양들을 더하여 scalar 광자수·흡수량을 만들 때 현재 시각의 J를 다시 곱하지 않는다.

## 3. 정확한 characteristic과 세 종류의 방향 측도

### 3.1 정의와 convention

기본 metric signature는 `(-,+,+,+)`이며 t는 gas-comoving 관측자의 proper time이다.

\[
ds^2=-c^2dt^2+\sum_{i=1}^3 a_i^2(t)(dx^i)^2,
\qquad a_i=a e^{\beta_i},\qquad \sum_i\beta_i=0,
\qquad H_i=H+\dot\beta_i .
\tag{1}
\]

고정 principal axes의 diagonal Bianchi-I를 다룬다. 아래 tensor 식의 회전은 고정된 좌표축 회전이며, 시간에 따라 회전하는 eigenframe을 새로 가정하지 않는다. `a_i(0)=1`을 기준 좌표 normalization으로 선택한다.

공간 병진 Killing vector 때문에 covariant momentum q_i는 ray를 따라 보존된다. q_i를 파수 대신 momentum으로 정의하므로

\[
E(t)=c\sqrt{\sum_i q_i^2/a_i^2(t)},\quad
g(t,\hat q)=\sqrt{\sum_i\hat q_i^2/a_i^2(t)},\quad
n_i(t)=\frac{\hat q_i}{a_i(t)g(t,\hat q)}.
\tag{2}
\]

방출시각 b, physical birth energy E_b가 고정된 cohort의 정확한 energy는

\[
E(t;b,E_b,\hat q)=E_b\frac{g(t,\hat q)}{g(b,\hat q)}.
\tag{3}
\]

즉 energy는 birth energy에 결속한다. q의 크기를 모든 birth 방향에 동일하게 놓는 것은 별개의 방출 스펙트럼이다. q_i=ℏk_i로 바꾸면 식 (2)의 우변에 cℏ가 들어간다. 기본 geodesic 법칙은 Fleury–Pitrou–Uzan [L1, (4.1)–(4.5)]의 직접 지지를 받는다.

방향 흐름과 에너지 변화의 부호는

\[
\frac{d\ln E}{dt}=-H_\parallel,
\quad H_\parallel=\sum_i H_i n_i^2,
\quad\dot n_i=(H_\parallel-H_i)n_i.
\tag{4}
\]

빠르게 팽창하는 방향의 광자는 더 빠르게 redshift된다. 방향식은 `d(Σn_i²)/dt=0`을 보존한다. H_i는 s⁻¹, β_i와 angular Jacobian은 무차원이다.

### 3.2 Jacobian 유도와 source ownership

선형사상 p=A⁻¹q, A=diag(a_i)에 대해 `d³p=det(A)⁻¹d³q`이다. 동시에 `|p|=|q|g`, 동일한 ray 방향에서 `d|p|=g d|q|`이므로 radial volume factor는 g³이다. 두 표현을 비교하면

\[
d\Omega_n=J(t,\hat q)d\Omega_q,
\qquad
J=\frac{1}{a_1a_2a_3g^3}.
\tag{5}
\]

`a_i=a exp β_i`를 넣으면 `J=(Σq_i² exp(−2β_i))⁻³/²`로 평균 팽창 a가 소거된다. 연속 구면에서는 `∫J dΩ_q=4π`가 정확하다. 식 (5)는 이 연구의 직접 유도이며, [L1]에 같은 angular Jacobian 식이 실렸다고 주장하지 않는다. Source code `solid_angle_jacobian` 및 `source_weights`가 이 식을 구현한다.

등방 physical birth source를 `S(b,E_b) db dE_b` photons/H로 정의하면, 고정 q 좌표에서의 birth measure는

\[
dN_b=\frac{S(b,E_b)}{4\pi}J(b,\hat q)\,db\,dE_b\,d\Omega_q.
\tag{6}
\]

따라서 방출 시각의 J_b는 필요하다. 반면 **이미 q-ray별 count로 저장된 광자를 scalar로 합산할 때 J_t를 다시 곱하는 것은 중복 변환**이다. 현재 물리적 입체각당 density를 보고 싶다면 count density를 J_t로 나누고, 그 양을 적분할 때 `dΩ_t=J_t dΩ_q`를 사용한다.

이로부터 세 양을 구분한다.

| 양 | 한 birth cohort에서의 표현 |
|---|---|
| 방출 광자 한 개에 조건부인 response kernel | `Kφ` |
| 고정 q 입체각당 source-bound response | `J_b Kφ/(4π)` |
| 현재 물리적 입체각당 response | `J_b Kφ/(4π J_t)` |

한 cohort의 scalar 적분에는 birth J_b만 남는다. 전체 3차원 q momentum measure를 사용하는 다른 정식화에서는 이미 `det(A)⁻¹`이 있으므로 그곳에도 식 (5)를 중복 삽입하면 안 된다.

## 4. 생존확률·광흡수·primary 가열의 선형 응답

### 4.1 조건과 정확한 kernel

흡수체 j의 proper number density를 n_j(t), photoabsorption cross section을 σ_j(E)라 둔다. 비등방 scattering, tilt, 방향 의존적인 원자단면적은 이번 baseline에 없다.

\[
\lambda_j(t,E)=c n_j(t)\sigma_j(E),\quad
\lambda=\sum_j\lambda_j,\quad
\Theta(t,b,\hat q)=\int_b^t\lambda(s,E(s))ds,
\quad P=e^{-\Theta}.
\tag{7}
\]

`P`는 아직 흡수되지 않은 확률이다. 방출 광자 한 개당 endpoint 흡수 사건률과 primary thermal-energy deposition kernel은

\[
K_{A,j}=P\lambda_j,
\qquad K_{Q,j}=P\lambda_j(E-\chi_j).
\tag{8}
\]

차원은 각각 s⁻¹ 및 energy/s이다. Gas evolution에서 per-H birth measure를 곱하면 사건/H/s, energy/H/s가 된다. Per-absorber ionization rate Γ_j는 흡수체 abundance factor를 제외해 정의하며, 그것도 아래 같은 전개에 포함된다. 식 (8)은 primary-electron energy가 열로 들어가는 현재 closure의 kernel이며, secondary ionization과 여기 손실을 새로 추가하지 않는다.

### 4.2 전단 parameter와 causal opacity memory

`β_i(t)=ε B_i(t)`, `ΣB_i=0`으로 놓고 `δ`는 `∂/∂ε|₀`를 뜻하게 한다. `ΔB_i(s,b)=B_i(s)−B_i(b)`이고 baseline energy는 `E⁰(s)=E_b a(b)/a(s)`이다. 따라서

\[
\delta\ln E(s)=-\sum_i\hat q_i^2\Delta B_i(s,b).
\tag{9}
\]

작은 양은 각 photon age의 **integrated shear** `εΔB_i=∫_b^s σ_i du`다. 현재의 작은 `σ/H`만으로 장시간 저장된 광자의 angular memory가 작다고 결론낼 수 없다.

고정 baseline gas에서 D≡E∂_E를 사용하고

\[
M_i(t,b)=\int_b^t D\lambda^0(s,E^0(s))\,\Delta B_i(s,b)ds
\tag{10}
\]

로 정의하면 `ΣM_i=0`이며

\[
\delta\Theta=-\sum_i\hat q_i^2 M_i,
\qquad \delta\ln P=\sum_i\hat q_i^2M_i.
\tag{11}
\]

현재 local cross section의 변화만으로 endpoint 흡수량을 계산하면 생존확률의 causal memory를 빠뜨린다. 감소하는 σ(E)에 대해 빠른 축은 local absorption을 증가시키지만, 앞서 더 많이 흡수되어 살아남은 광자가 줄어드는 반대 효과도 있다.

일반 terminal scalar weight를 Lφ(t,E)로 두고 `Kφ=P Lφ`라 쓰면

\[
\delta K_\phi=P^0\sum_i\hat q_i^2
\left[-DL_\phi^0\Delta B_i(t,b)+L_\phi^0M_i(t,b)\right].
\tag{12}
\]

흡수는 `Lφ=λ_j`, primary heat는 `Lφ=λ_j(E−χ_j)`이다. Lφ가 양수인 곳에서 `αφ=D ln Lφ`로 나눠 쓸 수 있지만, Lφ=0인 문턱에서는 나누지 않은 식을 사용해야 한다.

### 4.3 birth measure와 현재 방향분포

`δJ_b=3Σq_i²B_i(b)`를 식 (12)에 결합하면

\[
\delta(J_bK_\phi)=P^0\sum_i\hat q_i^2
\left[3L_\phi^0 B_i(b)-DL_\phi^0\Delta B_i+L_\phi^0M_i\right].
\tag{13}
\]

현재 물리적 입체각당 response는 J_t로 나누어야 한다. 이에 대한 fractional first variation은

\[
\boxed{\quad
\delta\ln\!\left(\frac{J_bK_\phi}{J_t}\right)
=\sum_i\hat q_i^2\left[-(3+\alpha_\phi)\Delta B_i+M_i\right].
\quad}
\tag{14}
\]

ε=0에서 zeroth-order response가 방향과 무관하므로, q를 고정했을 때와 현재 n을 고정했을 때 식 (14)의 1차 계수는 같다. **추가 3은 원자물리 계수가 아니라 방향 측도의 변화**다.

HI의 local logarithmic slopes는

\[
\alpha_A=D\ln\sigma_{\rm HI},\qquad
\alpha_Q=\alpha_A+\frac{E}{E-\chi_{\rm HI}}.
\tag{15}
\]

threshold 근처에서는 두 번째 항이 커져, 흡수와 가열이 반대 부호의 응답을 낼 수 있다. 실제 Verner fit [L3]의 source-bound 구현을 사용하며, 관측 파라미터의 오차를 추정한 것은 아니다.

## 5. 구면 평균이 선형 차수에서 사라지는 정리

### 5.1 고정 gas의 각도 적분

연속 구면에서는

\[
\langle q_iq_j\rangle=\frac{\delta_{ij}}3,
\quad
\langle q_iq_jq_kq_l\rangle
=\frac{\delta_{ij}\delta_{kl}+\delta_{ik}\delta_{jl}+\delta_{il}\delta_{jk}}{15}.
\tag{16}
\]

식 (13)의 대괄호 tensor는 trace-free이므로

\[
\delta\langle J_bK_\phi\rangle=0
\tag{17}
\]

이다. 모든 birth time과 emitted energy에 대해 이 식이 성립하고 적분·미분의 교환이 정당하면, 임의의 등방 S(b,E_b)를 적분한 full source에도 성립한다. β(0)=0에서 등방 초기 광자 cohort도 포함된다. 이는 유한 radiation moment closure를 요구하지 않는다.

### 5.2 기체와 결합했을 때

다음 조건을 명시한다.

- H와 scalar density normalization을 동일하게 유지한다. 순수 trace-free shear variation이다.
- 초기 gas는 같고 photon/source의 zeroth-order 물리적 방향분포는 등방적이다.
- 초기 photon count와 emitted-energy spectrum, S(b,E_b)의 scalar normalization은 ε에 독립이다. Source가 gas state에 의존하는 경우 그 변화는 식 (18)의 gas feedback에 포함하고 독립적인 O(ε) scalar forcing을 추가하지 않는다.
- 기체 반응률은 scalar gas state와 scalar photon integrals에 의존한다. Baseline에 finite anisotropic source, tilt 또는 방향 의존적인 미시반응이 없다.
- 관련 시간구간에서 source/response map이 Fréchet differentiable이고, 선형화한 gas–radiation/Volterra system에 해의 유일성이 있다. Threshold와 spectral-node crossing에는 별도의 regularity 검사가 필요하다.

Gas first variation z(t)에 대한 선형화는 개략적으로

\[
\dot z=A(t)z+\int_0^t K(t,s)z(s)ds+f_{\rm shear}(t),
\qquad z(0)=0
\tag{18}
\]

형태다. 식 (17)로 explicit scalar forcing `f_shear=0`이며, 유일성 아래 `z≡0`이다. 따라서 ion fractions, thermal energy, 양의 입자수에서 정의한 T, 동일한 proper-time 적분 구간의 scalar electron optical-depth proxy도 1차 변화가 0이다. 다른 lightcone endpoints나 observer redshift를 고정한 양은 추가 endpoint variation이 있으므로 이 문장으로 자동 승인하지 않는다.

**C¹ regularity는 first derivative=0, 즉 o(ε)를 보장한다. 유계 C² regularity가 있어야 O(ε²) 경계를 주장할 수 있다.** 여기서는 global Bianchi gas error certificate나 leading 2차 온도계수를 계산하지 않았다. [L2, (70)–(72)]의 spectral monopole이 `σ^{ab}F_ab`와 결합한다는 exact identity와 일치한다. Baseline quadrupole가 0이면 생성된 quadrupole는 O(ε), 그 scalar feedback은 smooth regime에서 O(ε²)다.

### 5.3 무엇이 상쇄를 깨는가

기존 O(1) source/initial quadrupole, 방향 선택·mask, shear와 함께 바뀐 평균 expansion 또는 source normalization, 잘못된 angular measure, moment 조건을 못 맞춘 유한 구적, 반응함수의 비미분가능성은 가정을 벗어난다. 이 원인들은 물리적 비등방성과 수치적 anisotropy를 구분해 검사해야 한다.

특히 고정 q에서 source를 uniform하게 놓아도 isotropic ε=0 baseline의 **연속 구면 scalar 1차항은 여전히 사라진다**. Jacobian 누락의 주요 손상은 1차 directional source와 일반적으로 2차 scalar response에 있다. J를 빼먹으면 반드시 1차 monopole가 생긴다고 주장하는 것은 부정확하다.

## 6. 현재 angular quadrature의 정확한 한계

N=Nμ, M=Nφ라 하고 `μ_j=−1+(2j+1)/N`을 사용한다. M≥3이면 midpoint azimuth rule은 degree-2 Fourier moments를 정확히 적분한다. 따라서 실제 기본 quadrature의 second moment는 정확히

\[
Q_N=\operatorname{diag}\left(
\frac13+\frac{1}{6N^2},\quad
\frac13+\frac{1}{6N^2},\quad
\frac13-\frac{1}{3N^2}\right).
\tag{19}
\]

임의 STF tensor B에 대해

\[
B:Q_N=-\frac{B_{zz}}{2N^2}.
\tag{20}
\]

가중치 총합=1과 antipodal symmetry는 이 문제를 없애지 못한다. 모든 STF direction의 1차 상쇄에는 `Q=I/3`가 필요하다.

실제 source weights가 `w_d∝J_b(q_d)`로 normalize되므로 그 미분은

\[
\delta w_d=3w_d^0[B(b):(q_dq_d-Q_N)].
\tag{21}
\]

따라서 `Σδw_d=0`이고 source-only zeroth moment는 보존한다. 하지만 K⁰가 방향에 무관한 상황에서도 kernel energy derivative에 남은 `Q_N:I_STF`를 제거하지는 못한다. 구체적으로

\[
\delta\sum_d w_dK_{\phi,d}
=P^0[-DL_\phi^0\Delta B+L_\phi^0M]:Q_N.
\tag{22}
\]

현재 선택된 `B∝diag(1,−1,0)`에서는 이 값이 0이다. Mφ가 4의 배수인 현재 grids는 x/y 교환으로 `ε→−ε`를 구현하므로, scalar 각도합이 이상적 exact arithmetic에서 even function이다. 부동소수점 합의 순서 효과나 spectral-map smoothness까지 이 대칭만으로 검증한 것은 아니다.

반면 `B∝diag(−1/2,−1/2,1)`이면 free-photon mean energy에 spurious linear term `+σΔt/(2N²)`가 남는다. N=8, σΔt=1.25×10⁻⁷의 예에서는 `9.765625×10⁻¹⁰`이다. Continuum의 순수 shear energy correction은 이 정도 전단에서 10⁻¹⁴ 수준이므로, generic-shear 해석에서 해당 artifact를 무시할 수 없다. 이것을 기존 `[160,161]` 실패의 원인이라고 판정하지는 않았다.

위 axisymmetric tensor는 현재 xy tensor와 eigenvalues가 다르다. 같은 eigenvalues를 보존한 고정 회전의 반례로 `diag(1,0,−1)`을 선택해도 spurious term `−σΔt/(2N²)`가 생긴다. 따라서 이 문제는 서로 다른 전단 크기·유형을 비교했기 때문에 생긴 현상이 아니라 angular rule의 방향 의존성이다.

### 6.1 선두 2차 scalar 효과도 별도 구적 조건이 필요하다

Physical birth angle에서 isotropic free-photon cohort를 잡고 `u=σ(t−b)`, `D=diag(1,−1,0)`를 놓는다. 정확한 energy ratio는

\[
r=\frac{E}{E_{\rm FLRW}}
=\sqrt{n_x^2e^{-2u}+n_y^2e^{2u}+n_z^2}.
\]

`P₂=n_x²−n_y²`, `R=n_x²+n_y²`로 쓰면

\[
r=1-uP_2+u^2(R-P_2^2/2)+O(u^3),
\qquad \langle r\rangle=1+\frac{8}{15}u^2+O(u^4).
\tag{23}
\]

일반 diagonal integrated shear Δβ의 2차 항은 `(4/15) tr[(Δβ)²]`이다. 이 계수는 energy weighting과 shear가 유도한 방향분포가 결합한 결과다. Grid가 first-order cancellation을 통과해도 이 계수가 정확하다는 뜻은 아니다.

Mφ≥5이면 현재 midpoint rule은

\[
\langle P_2^2\rangle_N=\frac4{15}+\frac7{30N^4},\qquad
C_N=\frac8{15}+\frac1{3N^2}-\frac7{60N^4}
\tag{24}
\]

를 준다. C_N은 b=0, fixed-q initial isotropic cohort의 `u²` 계수다. N=4,8,16의 정확한 Fraction 값과 독립 검사 결과는 `independent/angular_moments_results.json`에 남긴다. 이 지점은 **초기 radiation quadrupole의 수치적 잔여분과 fourth-moment 오차**를 분리해서 보는 계기가 된다.

| Nμ × Nφ | C_N의 정확값 | 연속값 8/15에 대한 계수 bias |
|---|---:|---:|
| 4 × 8 | `567/1024` | `+3.82080078125%` |
| 8 × 16 | `8823/16384` | `+0.971221923828125%` |
| 16 × 32 | `140151/262144` | `+0.2438068389892578125%` |

이 exact moment들은 Fraction의 직접 유한합으로 검산했다. 별도 Decimal80 characteristic evaluation의 coefficient discrepancy는 `2.681×10⁻¹³` 이하였고, source-formula의 Python binary64 재구성에서 Q와 P₂²의 discrepancy는 각각 `5.56×10⁻¹⁷`, `1.67×10⁻¹⁶` 이하였다. Rust 실행 또는 bitwise parity를 주장하지 않는다.

### 6.2 Birth-time source Jacobian의 2차 효과

Constant H_i의 free-energy benchmark에서 continuum isotropic physical source의 mean ratio는 photon age Δ=t−b만으로 정해진다. q-source를 uniform하게 놓으면 absolute birth time b에 의존하는 잘못된 항이 생긴다.

\[
\langle r\rangle_{\rm uniform\ q}-\langle J_b r\rangle_{\rm physical}
=\frac45\sigma^2b\Delta+O(\sigma^4)
\tag{25}
\]

여기서 x/y 교환대칭을 사용했으며 b와 Δ는 고정된 finite times다. General STF 표기로는 leading difference가 `(2/5) tr[β(b)Δβ]`이다. Physical-angle source는 이 가짜 시간원점 의존성을 **연속 구면에서** 제거한다.

유한 midpoint rule에서는 normalized J_b가 continuum처럼 완전한 각도 변환을 수행하지 못한다. 올바르게 J_b-weighted한 finite-grid mean에도 `σ² bΔ[2/(3N²)−7/(6N⁴)]`가 남는다. Uniform-q와 이 finite-grid source의 차이는 `σ²bΔ[4/5+7/(10N⁴)]`다. 이는 source Jacobian의 물리식 오류가 아니라 angular quadrature 잔여오차다.

## 7. 실제 FT03 상수에 결속한 작은 방향 kernel 검산

`code/directional_kernel.py`는 gas IVP를 풀지 않는다. H, directional shear, E_b, HI Verner fit, density normalization, χHI는 pinned code의 binary64 literals를 exact-real inputs로 읽고, **neutral fraction만 초기값 `1−xHII(0)`에 고정**한다. `n_H(t)=10⁻⁴ exp(−3Ht) cm⁻³`의 dilution은 유지한다. 따라서 evolving FT03 gas 또는 physical source history의 새 해가 아니다.

입력은 `t=1.25×10⁹ s`, births `b=0,t/2`, x/y/z축과 `(3/5,4/5,0)` 방향이다. Decimal 60자리에서 exact characteristic을 평가하고, survival optical depth는 Gauss–Legendre 24점으로 계산하여 48점 및 composite Simpson 128구간과 교차 비교했다. Time quadrature는 rigorous enclosure가 아니다.

최초 cohort b=0의 x축에서 다음 relative changes를 얻었다. 모든 수는 **이 frozen-neutral-fraction kernel과 실제 지정 shear amplitude에 한정**된다.

| 양 | `(Bianchi−FLRW)/FLRW` |
|---|---:|
| 도착 energy E | `−1.24999992×10⁻⁷` |
| 생존 광자의 instantaneous absorption hazard λ | `+3.36090460×10⁻⁷` |
| 방출 광자 한 개당 endpoint event kernel Pλ | `+3.35698605×10⁻⁷` |
| 방출 광자 한 개당 primary heat Pλ(E−χ) | `−1.65536292×10⁻⁵` |
| 현재 physical-angle event density J_bPλ/J_t | `−3.93014503×10⁻⁸` |
| 현재 physical-angle primary heat density | `−1.69286229×10⁻⁵` |

Baseline endpoint `E=13.6998287511 eV`, `Θ=0.00233183894`, `αA=−2.68872324`, `αQ=132.42586242`다. E−χ가 약 0.1014 eV로 작아서 작은 redshift의 relative heating effect가 absorption effect보다 훨씬 크다. 이 예가 주는 결론은 **흡수 증가로부터 가열 증가를 추론할 수 없고, 어떤 angular measure의 사건률을 보고 있는지 먼저 정해야 한다**는 것이다.

실제 first-macro의 fastest-axis minimum energy는 `13.6998270386 eV`로, provider cutoff `13.60 eV`보다 높다. 최소 log-margin은 `0.00731341509`이고 integrated shear는 `1.25×10⁻⁷`이다. 그러므로 이 작은 계산에서 threshold crossing은 없다. χHI와 fit cutoff를 하나의 수로 몰래 통합하지 않았다.

현재 정식 결과는 `evidence/directional_kernel_v2.json`이다. 64개의 analytic-vs-central first-derivative 비교, 16개의 quadrature 대조, 1개의 cutoff check를 실제 실행하여 81/81을 통과했다. 최대 derivative absolute discrepancy는 `2.42×10⁻²⁴`, time-integral 대조의 최대 relative discrepancy는 약 `4.34×10⁻¹⁷`이다. 이것은 **그 비교에서 관측한 수치차**이며 전체 truncation error를 증명한 값이 아니다.

v1에서는 module initialization 중 neutral fraction의 Decimal subtraction이 기본 28자리 context를 거쳤다. exact-input 설명과 일치시키기 위해 초기화부터 60자리 context를 사용하도록 바로잡고 v2를 실행했다. 원 v1 JSON과 수정 이유를 보존했다. 이 수정은 표에 보고한 유효숫자의 물리 결론을 바꾸지 않았다.

## 8. 비미분가능한 문턱 반례와 유효범위

Trace-free shear의 scalar cancellation은 무조건적인 법칙이 아니다. 분리된 반례로 FLRW 도착 에너지가 정확히 E_th인 isotropic monochromatic line을 생각하고, response를 `W(E)=(E−E_th)_+`로 정의하자. Actual FT03 line이나 cutoff를 이렇게 변경한 것이 아니다.

\[
E/E_{\rm th}=1-u(n_x^2-n_y^2)+O(u^2),\qquad
\langle W\rangle
=\frac{2E_{\rm th}}{3\pi}|u|+O(u^2).
\tag{26}
\]

유도는 `⟨|n_x²−n_y²|⟩=⟨sin²θ⟩⟨|cos2φ|⟩=4/(3π)`와 분포의 부호대칭을 사용한다. 양의 부분 평균은 절대값 평균의 절반이다. 따라서 `ε↔−ε`에 대해 even이면서도 leading response가 quadratic이 아닌 cusp가 존재한다.

추가로 positive-energy 영역의 φ 경계를 정확히 나누어 작은 cubature를 실행했다. `|u|=10⁻²,…,5×10⁻⁶`에서 one-sided coefficient가 `2/(3π)`로 수렴했고, 마지막 두 점의 linear extrapolation과 정확계수의 차이는 `6.32×10⁻¹²`였다. `evidence/threshold_cusp.json`에 2개의 성공한 진단 검사를 보존했다. 이것도 rigorous remainder enclosure는 아니다.

Discontinuous cross section과 문턱에 놓인 δ-line은 흡수율 자체의 불연속도 만들 수 있다. 매끄러운 emitted spectrum을 threshold의 moving boundary까지 함께 적분하면 그 경계항도 STF tensor와 결합하여 first derivative가 상쇄될 수 있으나, bounded second derivative는 별도로 확인해야 한다. Energy-bin remapping의 artificial node crossing과 물리적 δ-line은 서로 다른 문제다.

본 first-macro source-bound 진단은 cutoff margin으로 smooth regime에 속한다. 더 늦은 cutoff epoch, 실제 native energy remapping의 모든 branch, full observer optical depth, gas의 leading second-order shift는 이번 계산으로 닫히지 않는다.

## 9. 증거 상태와 다음 연구

| 주장 | 상태 | 직접 근거 |
|---|---|---|
| Exact E/n characteristic | literature-supported, derived; pinned source inspected | [L1], 식 (2)–(4), `bianchi_i.rs` |
| Birth/current angular Jacobian ownership | derived; implementation source inspected | 식 (5)–(6), `source_weights`; 원 Rust 실행은 하지 않음 |
| Directional absorption/heating causal response | derived, numerically checked | 식 (7)–(15), Decimal kernel JSON |
| Smooth coupled scalar first variation=0 | derived, conditional | 식 (16)–(18), [L2]와 일관됨; global gas certificate 아님 |
| Generic-shear midpoint leakage | derived, exact-arithmetic checked | 식 (19)–(22), independent Fraction evidence |
| Leading scalar energy coefficient and birth measure artifact | derived, numerically checked in free-energy benchmark | 식 (23)–(25), independent report |
| Threshold cusp | derived; focused numerical diagnostic | 식 (26), counterexample evidence |
| Full Bianchi ionization/temperature/τ predictions | unresolved / physical HOLD | 이번 loop에서 새 gas evolution 없음 |

최종 독립 decision-review의 구체적 판정은 `independent/DECISION_REVIEW.json`에 기록한다. Reviewer는 이 candidate와 verification design의 생성에 참여하지 않은 별도 실행자다. 해석상 승격은 이 연구 결과를 다음 이론 단계에 사용하는 범위로 한정하며, production/scientific admission과 구별한다.

다음 문제는 **PHYS21_SECOND_ORDER_SCALAR_SHEAR_RESPONSE**다. PHYS20의 tensor response와 정확한 2차·4차 angular moment 조건을 입력으로, 현재 prescribed FT03 gas에서 quadratic scalar forcing과 인과 gas feedback을 분리해야 한다. 현재 source를 변경하지 않은 상태에서 이론 functional과 small benchmark를 먼저 닫고, 실제 coupled coefficient가 필요할 때만 기존 continuous-gas evidence에 결속한다. 이미 완료한 FLRW source/time certificate를 다시 줄이는 반복은 만들지 않는다.

### 문헌 및 원격 source

- **[L1]** P. Fleury, C. Pitrou, J.-P. Uzan, *Light propagation in a homogeneous and anisotropic universe*, Phys. Rev. D 91, 043511 (2015), arXiv:1410.8473v3. 실제 확인: PDF p.2 (2.1)–(2.5), p.4 (4.1)–(4.5). https://arxiv.org/pdf/1410.8473v3
- **[L2]** R. Maartens, T. Gebbie, G. F. R. Ellis, *Cosmic microwave background anisotropies: Nonlinear dynamics*, Phys. Rev. D 59, 083506 (1999), astro-ph/9808163v2. 실제 확인: PDF pp.13–14 (70)–(72), exact spectral hierarchy와 shear–quadrupole monopole term. https://arxiv.org/pdf/astro-ph/9808163v2
- **[L3]** D. A. Verner, G. J. Ferland, K. T. Korista, D. G. Yakovlev, *Atomic Data for Astrophysics. II. New Analytic Fits for Photoionization Cross Sections of Atoms and Ions*, Astrophys. J. 465, 487 (1996), astro-ph/9601009v2. Fit form의 원전이며 실제 계산의 상수·cutoff authority는 pinned `atomic_provider.rs`다. https://arxiv.org/pdf/astro-ph/9601009
- **[S1]** PHYS19의 다음 물리 문제 계약: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/718468dc75cb81fdfe0f2792aab5c8d0dbc54607/docs/fastest_track_chat/REI-PHYS19-20261010/NEXT_HANDOFF_KO.md
- **[S2]** 실제 qhat/source weights: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/718468dc75cb81fdfe0f2792aab5c8d0dbc54607/rust/rei_microphysics/src/paired_runtime.rs
- **[S3]** 실제 cross sections: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/718468dc75cb81fdfe0f2792aab5c8d0dbc54607/rust/rei_microphysics/src/atomic_provider.rs

문헌은 geodesic/transport 기본식과 fit의 출처를 제공한다. 새로운 directional kernel의 정확한 수치, angular-grid defect, threshold 반례와 본 연구의 조건부 정리는 이번 직접 유도·검산의 결과이며 문헌의 관측결론으로 포장하지 않는다.
