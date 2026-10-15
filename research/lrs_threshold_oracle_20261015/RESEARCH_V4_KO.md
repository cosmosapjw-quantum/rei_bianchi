# REI-LRS V4: 동적 H/He 재결합·열역학 reference 및 NCP handoff

**연구 기준일:** 2026-10-16 (KST). **범위:** 독립적인 수학·수치 기준 계산. 재이온화 production 결과가 아니다.

## 1. 최신 소스 및 작업 경계

- `rei_bianchi` PR #152: 정확한 LRS Bianchi I photon 특성곡선, Verner 1996 원본 H/He 단면적, angular ionization threshold cut.
- `rei_bianchi` PR #153: H/He **photoionization-only** 양의 짝반응, photon/electron/energy ledger, SciPy Radau validation, 대칭성 회복.
- PR #154: 별도 C16B source-aware photo-reaction reference가 등장했으므로 이 작업은 중복 photo-reaction 개발 대신 **재결합·gas thermal**의 추가 보존법칙과 오차 분석에 집중한다.
- PR #150: 별도 FLRW native production solver. 이 작업은 PR #150/v3/rux/NCP 기존 프로세스, H/He owner 소스 또는 체크포인트를 **수정하지 않는다**.
- 이번 구현의 기준: PR #153 source HEAD `e98d30efb5e725a79743d3a8ff61ee7e5169b498`; 상속 기준 PR #152 HEAD `bbbd18b5c16eff70bc32ba4296360dceb9060ec4`.
- 사용자의 Ubuntu 원격 명령은 Desktop Commander 월간 quota로 차단되었다. 연결을 다시 시도하지 않았다. Ubuntu 원본 `rei_bianchi` 체크아웃 및 이전 미추적 `dynamic_chemistry.py`는 보존할 것.

## 2. 연속계 계약: 정의·물리 가정·단위

시공간 부호 `(-,+,+,+)`. 비틸트, 축대칭 Bianchi I:

\[
 ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2,
\quad X=\ln(a/a_0),\quad b=(s/H)X.
\]

`H>0`, signed `-1/2<s/H<1`, `Σ=√3|s|/H`. 광자 방향 초기 `μ0`, 에너지 `E0>0`에서

\[
 E_r(X)=E_{r0}e^{-X}\sqrt{(1-\mu_0^2)e^{2b}+\mu_0^2e^{-4b}}.
\]

원본 donor Verner et al. (1996), ApJ 465, 487, Eq.(1), Table 1. 원자 단면적 `σ_i(E)`는 Mb (`1 Mb=10^-22 m²`), 에너지는 eV, 시간은 `X` (dimensionless)이다. 입자수와 광자수는 초기 comoving 부피당 기준 밀도 `n★`로 나눈 무차원 stock. 처음에 이미 이온화된 종도 chemical energy로 계상한다.

`g=(M_HI,M_HII,M_HeI,M_HeII,M_HeIII)`. `n_e=M_HII+M_HeII+2M_HeIII`. 광이온화 채널 순서 HI, HeI, HeII; 재결합은 HII→HI, HeII→HeI, HeIII→HeII. 소스 없는 직접 광자 소모:

\[
 P_{ri}=\frac{c n_\star 10^{-22}\mathrm{m}^2}{H_0}\frac{e^{-3X}}{H(X)/H_0}\sigma_i(E_r)N_r M_{\mathrm{target}(i)}
\]

(
`sigma_i`를 Mb로 평가). 광자수 `N'_r=-Σ_i P_ri`, 원자 stock은 각 반응 stoichiometry로 진화한다. 재결합:

\[
 R_i=\frac{\alpha_i(T_\mathrm{ref}) n_\star}{H_0}
\frac{e^{-3X}}{H(X)/H_0}
\left(\frac{T}{T_\mathrm{ref}}\right)^{-\beta_i}
 M_{\mathrm{ion}(i)} n_e.
\]

**중요:** `alpha_i(T_ref)*n★/H0`의 세 값과 `β_i`는 이번 **조건부 toy input**이며 검증된 Case-B 실제 atom rate provider가 아니다. 실험값 `K_photo=2`, `K_rec=(0.32,0.15,0.12)`, `β=(0.7,0.7,0.7)`, `T_ref=10000 K`.

물리적 thermal energy `U_th=(3/2)k_B T (M_H+M_He+n_e)/eV`, 에너지 단위는 `eV per n★ initial comoving volume`. 결합에너지 저장량은

\[
 B=E_{\rm HI}M_{\rm HII}
  +E_{\rm HeI}(M_{\rm HeII}+M_{\rm HeIII})
  +E_{\rm HeII}M_{\rm HeIII}.
\]

재결합으로 방출되는 복사의 유효 escape energy를 한 event당 `E_i+(3/2)k_B T`로 정의한다. **이는 열전자 평균 kinetic energy를 제거하는 단순 closure**다. 실제 Case-B cascade photon transport, He branching, 계수 테이블, excitation/collisional cooling, 비열 변화 외 추가 과정은 포함하지 않는다. 재결합 photon을 다시 흡수하는 비국소 수송을 이 계산에서 수행하지 않는다.

따라서 

\[
 U'_{\rm th}=-2U_{\rm th}+
 \sum_{ri}P_{ri}(E_r-E_i)-\sum_i R_i\frac{3}{2}k_BT,
\]
\[
 E'_{\rm esc}=\sum_i R_i(E_i+\frac32 k_BT),\quad
 W'_{\rm th}=2U_{\rm th},\quad
 W'_{\gamma}=\sum_r N_r E_r\left[1+\frac{s}{H}(3\mu_r^2-1)\right].
\]

원자핵수/광자-전자 반응과 에너지 항등식:

\[
 M_H = \mathrm{const},\qquad M_{He}=\mathrm{const},\qquad
 \Delta n_e=\sum_{ri}\mathcal A_{ri}-\sum_i\mathcal R_i,
\]
\[
 \boxed{U_{\gamma,0}+U_{{\rm th},0}+B_0
 =U_\gamma+U_{\rm th}+B+E_{\rm esc}+W_\gamma+W_{\rm th}.}
\]

**Wolfram Language 기호 검사:** 이상의 개별 연속 미분 항들을 합한 에너지 잔차가 정확히 `0`. 각 재결합 소단계에서 `U_th`와 gas total particle count가 같은 비율로 감소하므로 고립 재결합 소단계에서는 온도 `T`가 일정함을 보이는 비율 항등식도 `0`.

## 3. 알고리즘·수치 검증

`recomb_thermal.py`는 정확한 단일 photon-target pair-reaction positive map과 그 역방향(recombination) ion-electron pair map을 사용한다. 두 단계 photo-recomb-photo symmetric Strang composition, 원본 threshold event split, 원래 ray 에너지 특성곡선의 정확한 양쪽 half-drift, 별도 gas adiabatic half-drift를 사용한다. 동일 energy/mirror ray의 group 동등성을 사용해 FLRW 및 LRS 반사대칭을 보호한다.

**주의:** discrete energy residual이 부동소수점 오차 수준인 것은 합성법에서 회계를 정확히 마무리하기 때문이다. 연속 물리 방정식 정확도는 별도의 SciPy Radau RHS와 step refinement로 검증해야 한다.

2026-10-16 ChatGPT sandbox Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, pytest 9.0.2:

- 이전 V2/V3 80개 + 새 thermal/recombination 18개 = **98/98 PASS**.
- 새 18개는 exact thermal/no reaction limit, electron+nuclear census, nonnegative case, reciprocal recombination photo flow, Ray mirror and FLRW isotropy, energy residual, stiff positivity, 독립 Radau 수렴 등을 포함한다.
- `X_end=.65`, 처음 `Tgas=8000 K`, baseline gas `(HI,HII,HeI,HeII,HeIII)=(.37,.03,.085,.012,.003)`. photon spectrum 110eV(.12), 72eV(.08), 43eV(.06), 초기 각도 GL8.
- `H/H0=1`, signed `s/H=-.04,0,+.04`. `max_step=.005` 결과:
  - s/H -0.04: ne=0.07491382090756712, Tgas=6368.972438456518 K, Radau max abs difference 4.27488e-6.
  - s/H 0: ne=0.07491323590241768, Tgas=6369.3891643102625 K, Radau max abs difference 4.51001e-6.
  - s/H +0.04: ne=0.0749137414064937, Tgas=6368.947746792671 K, Radau max abs difference 4.30703e-6.
- number/electron invariant residual은 대개 ~1e-16, 전체 에너지 잔차는 ~1e-14 eV/n★. `ΔX_max=.08,.04,.02,.01,.005`에서 대체로 2차 감소. 이 기준값은 3회 signed shear를 비교한 **toy validation**, 관측값이 아니다.

기계 가독성 산출물: `evidence/v4_recomb_thermal/convergence.json`, `temperature_ion_history.csv`, HI/HeII/HeIII/Tgas PNG 네 장, `evidence/v4_full_test_results.txt`.

## 4. 원격 실행 상태와 NCP 계약

이 환경에서는 사용자 Ubuntu Desktop Commander 월간 호출 한도를 소진하여 원격 셸 실행을 재시도하지 않았다. **이번 새 V4 코드는 아직 사용자 Ubuntu 또는 64-vCPU NCP에서 실행되지 않았다.** NCP 접근 명령은 사용자 제공의 `ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22`; 앞선 턴에서 NCP `rustc 1.99.0` 설치를 확인했으며, 이번 새로운 benchmark는 Python/SciPy 기반이다. NCP에 Rust를 사용해야 한다는 이유만으로 새 물리 solver를 번역하거나 동일성을 주장하지 않는다.

`NCP_RUN_V4.sh`: source checksums, 98 tests, Radau benchmark, 동일 smoke 12건의 single-/4-worker byte identity, 이어서 독립 816건(17 signed shear × 4 photo strengths × 4 recomb strengths × 3 T0) 2-resolution high-throughput sweep. 기본 12 worker, 16 worker 상한, timeout 900s, existing NCP jobs 및 임의 다른 파일 변경 없음. `ncp_recomb_sweep_v4.py`의 self-resolution error는 **Radau 독립오차가 아니며**, 816건 결과의 과학 admission을 자동 부여하지 않는다. NCP 실행 후 정확한 sha/timing/실행환경/실패 원인을 현재 branch에서 체크포인트하고 외부 감사로 회신해야 한다.

배포 보조파일: `NCP_RUN_V4.sh`, `V4_INPUT_SHA256SUMS.txt`, `CODEX_NCP_HANDOFF_20261016.md`. 입출력 계약, stop conditions, GH branch, 원본 dirty workspace 무변경, 양쪽 클라우드 create-only 저장을 손으로 또는 별도 Codex 실행기로 수행한다.

## 5. 후속 조건

이 작업의 다음 과학적 확장(독립 연구)에는 certified actual `alpha_B(T)` species fits, 진짜 recombination cooling, HeII cascade/OTS 재방출과 상호 이온화, Planck/CF4 native background, PR150 transport-chemistry mapping이 필요하다. 해당 소스의 정확한 repo SHA/physics clock/units를 비교하기 전까지 production 결과, 실제 gas-temperature history 또는 관측적 claim으로 올리지 않는다.

**Literature:** Verner et al. 1996 ApJ 465, 487 (`https://arxiv.org/abs/astro-ph/9601009`); Pawlik & Schaye 2011 (`https://arxiv.org/abs/1008.1071`); Friedrich et al. 2012 (`https://arxiv.org/abs/1201.0602`).
