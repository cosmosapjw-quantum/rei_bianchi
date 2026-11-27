# HE29: canonical-momentum 재사용과 z=2 continuation의 물리 계약

작성일: 2026-10-21. 직접 읽은 BASS_HE checkout: `048a73de4246f609b1bc14854ea5c48757cb82fd`, `research/he29_rei_pilot_20261021`. 이 작업은 R2–R6 중 기존 모델의 식·단위·보존량 재사용과 필요한 algebra 검산을 담당한다. 원래 ODE pilot 재실행과 성능 benchmark는 수행하지 않았다.

후속 evidence 갱신: 이 유도 뒤 복구된 `REI_UNIFIED_D3_EXECUTION_20261021_20261021T104524Z.tar.gz`에 z=20→2의 237개 완전한 저장 궤적이 이미 존재한다. 아래 continuation 설명은 해당 실행을 해석·검토하는 계약으로 재사용하며 추가 tail IVP를 권고하지 않는다. 새 작업은 저장 결과의 독립 검토와 벡터화된 후처리다. 실제 결과 판정은 `INDEPENDENT_RESULT_REVIEW_KO.md`, 수치·hash 영수증은 `INDEPENDENT_DATA_READBACK.json`을 따른다.

## 1. 선택한 기여와 근거 상태

오늘의 `z=20→2` 목표에는 기존 collisionless canonical massive matter + photon/neutrino hierarchy와 완전한 저장 상태를 보존하는 경로가 직접 기여한다. z=4→2 구간도 D3 복구본에서 완료되었으므로 재실행 없이 사용한다. 고정 phase-space geometry와 weights의 재사용은 동일한 moment 적분을 계산하므로 물리 closure를 바꾸지 않는다. 실제 원자물리 H/He response는 별도 donor가 필요한 결합 항이다.

| 결과 | 근거 상태 | 근거 |
|---|---|---|
| LRS 정규화·signed stress 합산 | derived; implementation-verified by source inspection | `src/coordinates.py`, 아래 §2 |
| canonical weights의 보존과 moment 에너지 항등식 | derived; symbolically checked; numerically checked | 아래 §3, `TOOL_EVIDENCE.json`, `CANONICAL_MOMENT_CHECKS.json` |
| 저장 상태에서의 continuation 조건 | derived; completed D3 execution reviewed separately | 아래 §4; 실제 237개 continuation은 복구된 기존 실행 |
| invariant precomputation 후보 | derived | 아래 §5; 실제 패치·통과 여부는 parent 통합 보고 |
| H/He electron/opacity adapter 관계 | derived, literature-supported | 아래 §6; 현재 pilot에서 native chemistry 실행 없음 |

## 2. tensor, 시간, 단위와 독립된 matter/radiation 좌표

사용하는 signature는 `(-,+,+,+)`이며 proper time t는 초 단위다. 기존 코드의 대칭축은 세 번째 축이다.

\[
ds^2=-c^2dt^2+a^2(t)e^{-2b(t)}(dx^2+dy^2)+a^2(t)e^{4b(t)}dz^2,
\quad H=\dot a/a,\quad s=\dot b.
\]

orthonormal 공간 성분에서

\[
D=\operatorname{diag}(-1,-1,2),\qquad
\sigma_{ab}=sD_{ab},\qquad
\pi^X_{ab}=p_XD_{ab},\qquad X=m,r.
\]

따라서 `Tr(D)=0`, `Tr(D²)=6`, `P_parallel-P_perp=3 p_X`이며

\[
|\sigma|_F=\sqrt6|s|,\quad |\pi_X|_F=\sqrt6|p_X|,
\quad \sigma_{ab}\pi_X^{ab}=6sp_X.
\]

`vendor`의 `Sigma=√3 |s|/H`는 half-contraction norm을 사용한다. 사용자 요청의 Frobenius norm은 `src/coordinates.py`에서 `Sigma_F=√2 Sigma`로 이미 변환한다. plot과 표에는 이 `Sigma_F`를 사용한다.

물리적 stress는 J m^-3이며, proper-time Einstein 결합 계수는

\[
\kappa_t=8\pi G/c^2=c^2\kappa_E,\qquad \kappa_E=8\pi G/c^4.
\]

따라서 dimensionless 좌표는

\[
u=\sqrt6s/H,\qquad v_X=\kappa_t\sqrt6p_X/H^2,
\qquad\Sigma_F=|u|,\quad\Pi_X=|v_X|.
\]

원래 Einstein source와 conservation work는 signed `p_m+p_r`로 계산한다.

\[
\dot s+3Hs=\kappa_t(p_m+p_r),\qquad
\Pi_{\mathrm{tot}}=|v_m+v_r|.
\]

`Pi_m+Pi_r`로 total을 대체하면 반대 방향 stress의 cancellation이 소실된다. photon과 massless neutrino는 각각 유지한 뒤 `p_r=p_gamma+p_nu`로 합한다. 기존 canonical pilot의 UV 성분은 0이며 `ne_source=None`이다.

초기 positive angular weight는 `W_m=1+A_m P2(mu)`이다. `P2`의 범위가 `[-1/2,1]`이므로 모든 방향에서 W_m≥0인 정확한 조건은 `-1≤A_m≤2`다. 기존 split mapping은 고정 finite quadrature에서 계산한 `M1=pi_s(A_m=1)`로 `A_m`을 역산한다. 연속 radial 근사로 이 coefficient를 바꾸지 않는다.

## 3. canonical momentum moment와 에너지 항등식

Bianchi I의 공간 translation Killing fields에 대응하는 covariant momenta `k_i`는 collisionless geodesic 위에서 일정하다. 현재 모델은 이 좌표에서 고정된 비음수 cell weights `w_j`를 유지한다. 이 구조의 massless case와 physical momentum 대응은 Dash & Jaiswal, PRD 97, 104005 (2018), §IV–V와 Appendix A에서 확인된다. 특히 식 (19)–(27)은 moments, 식 (32)–(35) 이후의 characteristic solution은 canonical momentum dependence를 제시한다. 논문 convention은 `(+,-,-,-)`와 natural units이므로 여기의 식으로 대응시켰다. [원전](https://arxiv.org/pdf/1711.07130)

기준 epoch `a_ref=1/21`에서

\[
\eta=\ln(a/a_{\rm ref}),\quad r=e^{-\eta},\quad
p_\perp=q_\perp r e^b,\qquad p_\parallel=q_\parallel r e^{-2b},
\]

여기서 moment 코드의 p, q, m은 동일한 고정 reference-energy 단위로 무차원화했다. 물리 단위 복원은 코드의 `rho_crit_J_m3 * mass_pref`가 담당한다. 다시 `T_ref`를 현재 temperature로 바꾸지 않는다. 고정 quadrature normalization N을 사용하면

\[
E_j=(m^2+p_{\perp,j}^2+p_{\parallel,j}^2)^{1/2},
\]
\[
\rho={r^3\over N}\sum_jw_jE_j,\quad
P_\perp={r^3\over N}\sum_j{w_jp_{\perp,j}^2\over2E_j},\quad
P_\parallel={r^3\over N}\sum_j{w_jp_{\parallel,j}^2\over E_j}.
\]

`P_perp`는 두 수직 방향 각각의 압력이다. `pbar=(2 P_perp+P_parallel)/3`, `p_m=(P_parallel-P_perp)/3`다. g=b'(eta)라 놓으면 한 packet에서

\[
{dE_j\over d\eta}=-{p_{\perp,j}^2+p_{\parallel,j}^2\over E_j}
+g{p_{\perp,j}^2-2p_{\parallel,j}^2\over E_j}.
\]

따라서 quadrature 합을 취하기 전부터

\[
\boxed{\rho'+3(\rho+\bar P)+6b'p_m=0},\qquad
\boxed{n(\eta)e^{3\eta}=\mathrm{constant}}
\]

가 성립한다. `b'=s/H`를 대입하면 proper-time matter energy conservation으로 돌아간다. 항등식은 유한 positive quadrature 자체에서도 성립하며 continuum quadrature convergence와는 별도 성질이다.

Wolfram의 한-packet symbolic residual은 정확히 0이었다. 기존 vendor의 mass/Tref=30, A_m=0.5, radial24×angular12, Gauss3에 대해 네 개 `(eta,b,b')` state를 직접 평가했다. `max |energy residual|/(rho+pbar)=8.85e-16` 이하, number relative residual은 `2.23e-16` 이하였다. ODE time stepping은 이 검사에 포함되지 않았다. 두 도구 출력의 provenance는 함께 보존했다.

보조 해석: `b≈constant`, nonrelativistic massive particles에서 `p_m∝a^-5`, massless radiation에서 `p_r∝a^-4`다. matter-dominated `H²∝a^-3` 한계에서는 `Pi_m∝a^-2`, `Pi_r∝a^-1`이 된다. 따라서 같은 크기의 opposite-sign 초기 stress라도 cancellation이 계속 유지될 필요는 없다. 실제 coupled solution은 b와 radiation multipoles의 진화를 포함하므로 이 식은 scaling 진단으로 사용한다.

## 4. z=4→2 continuation의 정확한 입력 계약

기존 source의 `a_end=.2`는 z=4다. 목표 z=2는 `a_end=1/3`, `eta_end=ln(7)`이며 새로운 구간은 `eta∈[ln(4.2),ln(7)]`다. 다음 항목을 보존하면 같은 finite-dimensional IVP의 continuation이다.

- `a_ref`, `H_ref`, `rho_crit`, cosmological density parameters를 보존한다. `a_end`만 확장한다.
- 저장된 `sol_t[-1]`을 새 시작 eta로 쓰고 **40개 전 상태 성분** `sol_y[:, -1]`을 넘긴다. elapsed proper time, b, s/H_ref, thermal slot, photon/neutrino energy와 number multipoles 모두 포함한다.
- `mass_over_Tref`, `mass_fraction`, actual `A_m`, 모든 grid/order, radiation initial amplitudes, Lmax와 closure, solver tolerance를 보존한다.
- canonical weights는 기존 initial-distribution specification으로 재구성하며 현재 epoch를 새 initial epoch로 삼아 reset하지 않는다.
- 오래된 구간의 값·원본 해시는 유지하고 새 구간은 별도 identity와 provenance를 가진다. 접합점 한 행은 plot/table 병합에서 중복을 제거한다.
- 저장된 `(Sigma,Pi_m,Pi_r)`만으로 restart하지 않는다. 이는 sign과 higher multipoles, b, clock을 재구성하기에 불충분한 요약이다.

현재 old source-binding 정책과 new continuation identity를 분리해야 한다. 원래 source manifest를 덮어쓴 뒤 과거 검증을 상속하는 방식은 사용하지 않는다. 새 interval의 Lmax·moment-resolution 오차는 이 문서의 항등식 검사로 인증되지 않는다.

## 5. 물리식을 보존하는 계산 축소

`q²(1-mu²)`, `q² mu²`, `w/N`, cell minimum, number sum, Legendre energy/number matrices와 Thomson diagonal은 시간에 의존하지 않는다. 생성 후 read-only로 보관하고 RHS에서는 `exp(-2eta+2b)`, `exp(-2eta-4b)`, E와 moment reductions만 계산할 수 있다. 이때 floating-point 연산 순서에 따른 최종 ulp 차이는 허용되는 solver error와 분리해 검사한다.

이미 vendor에는 `moment_batch(eta,b,chunk=32)`가 존재한다. 저장된 diagnostic moments를 새로 계산할 때 이 경로를 재사용하고 무제한 case×time×q×mu tensor를 만들지 않는다. 서로 다른 case는 각각 독립한 IVP이므로 case 단위 process 병렬화가 직접적인 방향이다. 각 worker 내부 BLAS/OpenMP thread는 1로 두고 제공된 자원 lease 범위에서 worker 수를 정한다. 실제 speedup 배수는 측정하지 않았다.

외부 방법 대조: Grackle은 `initialize_rates.c`의 `logT_spacing`과 `add_reaction_rate`에서 T-only atomic rates를 초기화 시 tabulate한다. [공식 source](https://github.com/grackle-project/grackle/blob/6d57fe2c3eb07c34dadb0b0e568cdc12f975146d/src/clib/initialize_rates.c). 이 작업에서 채택하는 공통 원리는 불변 계수의 1회 계산이며, 기존 locked H/He rate 값은 바꾸지 않는다. Grackle source는 Enzo Public License의 NCSA/BSD 조건을 사용한다. 이번 subtask에서는 외부 source를 복사하지 않았다.

## 6. helium이 실제로 기여하는 결합 위치

원자 chemistry state가 주어지면 free-electron density는

\[
n_e=n_Hx_{\rm HII}+n_{\rm He}(x_{\rm HeII}+2x_{\rm HeIII}),
\qquad \Gamma_T=c\sigma_Tn_e.
\]

현재 코드에서 donor는 proper `cm^-3`이고 `GAMMA_PER_NE=c_cgs sigma_T_cm2`이므로 Gamma_T는 s^-1다. Gamma_T는 photon collision term만 곱하고 collisionless neutrino term에는 들어가지 않는다. scalar ion fractions만으로 nonbaryonic massive `pi_m`을 생성하거나 대체하지 않는다. native UV photons의 anisotropic stress를 넣으려면 별도 radiation energy/momentum ledger가 필요하다.

고정 T, 외부 photoionization rates, frozen n_e에서 helium fractions X=(x_HeI,x_HeII,x_HeIII)는

\[
\dot X=AX,\quad
A=\begin{pmatrix}-a&b&0\\a&-b-c&d\\0&c&-d\end{pmatrix},
\]

\[
a=\Gamma_{\rm HeI}+n_eC_{\rm HeI},\quad b=n_e\alpha_{\rm HeII},
\quad c=\Gamma_{\rm HeII}+n_eC_{\rm HeII},\quad d=n_e\alpha_{\rm HeIII}.
\]

각 coefficient가 비음수이면 column sum은 0이고 off-diagonal은 비음수다. 따라서 frozen-rate propagator `exp(A dt)`는 helium nuclei와 fractions의 비음수성을 보존한다. 이는 self-consistent n_e와 T를 freeze한 subproblem의 성질이다. 전체 thermochemistry 정확도는 freeze/splitting error를 별도로 갖는다.

`y=(x_HeII,x_HeIII)`, `x_HeI=1-y1-y2`라 놓으면 self-consistent electron Jacobian은

\[
J=\begin{pmatrix}-(a+b+c)&d-a\\c&-d\end{pmatrix}
+\begin{pmatrix}C_1x_0-(\alpha_1+C_2)x_1+\alpha_2x_2\\ C_2x_1-\alpha_2x_2\end{pmatrix}
\begin{pmatrix}n_{\rm He}&2n_{\rm He}\end{pmatrix}.
\]

Wolfram differentiation과 이 표현의 차이는 영행렬이었다. full H/He OTS에서는 helium recombination photons가 H 및 He photoionization source에도 기여하므로 이 3-state block 바깥의 결합을 보존해야 한다. Friedrich et al. (2012), §3.1, Appendices A–B와 G가 그 계약의 직접적인 원전이다. [원전](https://academic.oup.com/mnras/article/421/3/2232/1077406)

HYREC-2는 effective atomic rates와 RT correction을 표로 재사용하는 유용한 선례다. 그러나 해당 Lyman-alpha correction의 calibration 범위는 primordial recombination 및 논문에서 명시한 cosmological domain이다. z20→2 reionization의 새로운 source prescription으로 자동 채택하지 않는다. 이번 확인에서 upstream GitHub license metadata는 null이었으므로 코드 복사도 수행하지 않았다. [논문](https://arxiv.org/abs/2007.14114), [공식 코드](https://github.com/nanoomlee/HYREC-2)

Grackle의 기본 UVB table은 FG2011의 경우 z10.6, HM2012의 경우 z15.13에서 끝난다. 그 위 구간의 equilibrium fallback을 오늘 z20 initial condition에 암묵적으로 대입하지 않는다. rate source를 선택하고 donor epoch 범위를 명시한 뒤 helium opacity coupling을 별도 모델로 이어가는 것이 구현 계약이다. [공식 설정 문서](https://grackle.readthedocs.io/en/latest/Parameters.html)

## 7. 검토 결론과 다음 실제 작업

새 strong no-go는 주장하지 않았다. NG1–NG7은 새 불가능성 성과를 채택하지 않으므로 not_applicable이다. 구성적 검토의 발견은 `(i)` norm의 √2 대응, `(ii)` proper-time κ의 c² 대응, `(iii)` restart clock/metric/multipole state 보존, `(iv)` unchanged rate ownership이었다. 현재 코드의 Frobenius adapter와 κ_t는 이미 올바르게 연결되어 있고 새 continuation 구현은 §4 계약을 따라 검토하면 된다.

이 단위의 산출물은 기존 finite model을 z2까지 확장할 식·불변량·재사용 조건이다. parent의 코드 구현과 새 구간 계산이 끝나면 `Sigma_F(z)`, signed `v_m(z),v_r(z)`, `Pi_m(z),Pi_r(z)` 및 initial-parameter slice plot에 직접 연결한다. 원래의 729-case phenomenological pilot과 40-case canonical model은 source identity와 closure가 다르므로 각각의 결과로 관리한다.
