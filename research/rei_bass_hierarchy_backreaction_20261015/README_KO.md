# REI ↔ BASS 볼츠만 hierarchy·\(\Sigma\)·\(\pi_{ab}\) backreaction, 2026-10-15

## 이번 루프의 실험적 결과

**실제 Ubuntu에서 코드 작성·실행·검증**, 원래 과학 source/AX08 체크포인트/실행파일 보존. 사용자 요청은 BASS의 기존 Boltzmann hierarchy/dossier와, BASS_HE/WU088_HH/bass_cr/rec_bianchi 발전을 REI에서 작동하게 이식하는 것. 기존 [REI C12 공급자 통합 PR134](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/134) 코드를 그대로 기반으로 삼았다. 기존 공통 source/case를 덮어쓰는 새로운 "합친" dummy physics는 만들지 않았다. 기존 REI \(\Sigma\)-stress [PR133](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/133) 도 읽고 BASS [PR159](https://github.com/cosmosapjw-quantum/bass/pull/159) 독립 Einstein–Vlasov 코드 `fa8c60fba73ce5dd40ce47833749ae70dd0c64d7`를 Git blob/source-lock에 맞춰 직접 호출했다. User \(\Sigma=\sqrt{\sigma_{ab}\sigma^{ab}/2}/H=\sqrt3|s|/H\)와 전단 방향 \(\varepsilon_\sigma\)를 모든 새 물리 output에서 사용한다. 역사적 q_ref는 source-compatible 초기 ref-input 선택에만 있다.

**진행 상태:** source-locked \(\ell_{\max}\le32\) homogeneous LRS Bianchi I **두 원자 radiation 에너지·수 밀도 모멘트 Boltzmann hierarchy**를 Einstein \(\pi_{ab}\)와 결합, 실제 AX08 312238-행 HHe electron density source \(\Gamma_T=c\sigma_T n_e\)에 연결하고, 원래 REI C11의 Grackle Case-A HHe/photons fixed receiver를 실제 실행해 time-dependent \(n_e(t)\) Thomson 및 전단 backreaction를 확인. 나중 단계의 풀 polarization E/B, tilt 및 exact multifrequency/photoionizing pressure stress, LRS 외 Bianchi는 구현됐다고 주장하지 않는다. Source-heavy native AX08 ODE 수정/재실행도 없다.

## BASS PSTF Boltzmann hierarchy의 실제 수치 연결식

사용한 실제 물리 근거: BASS `PLAN-H-boltzmann-hierarchy.md`, `docs/lowell_bianchi/02_multipole_hierarchy_spec.md` T1/T7/T8/T9, `src/pstf/hierarchy.rs` 및 `htt/bass/collision/thomson_pstf.py`. \(k=0\), non-tilted, diagonal LRS \(ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2\)에서 \(\sigma_{\hat i\hat j}=\operatorname{diag}(-s,-s,2s)\), \(s=\dot b\). Current local direction \(\mu=\cos\theta\) evolves \(d\mu/dt=-3s\mu(1-\mu^2)\), photon energy \(d\ln E/dt=-H-s(3\mu^2-1)\). For \(x=\ln(a/a_\mathrm{ref})\), energy-integrated **comoving normalized** intensity \(F_E=a^4 I_E/\rho_{\rm ref}\) and photon number angular density \(F_N\propto a^3 N\) obey

\[
\partial_x F_j
  = \frac{s}{H}\left[3\mu(1-\mu^2)\partial_\mu F_j
                         -n_j(3\mu^2-1)F_j\right]
    +\frac{C_j}{H},\qquad n_E=4,\ n_N=3.
\]

\[
F=\sum_{\ell=0}^L (2\ell+1)F_\ell P_\ell(\mu),\quad
F_\ell=\frac12\int_{-1}^{1}F P_\ell\,d\mu .
\]
구현한 1D projected Gauss–Legendre angular matrix \(A^{(n)}_{\ell m}\)는 원래 BASS 계층의 위 LRS angular sub-block을 source-specific normalization으로 표현한다. 실제 Wolfram symbolic \(L=4\)에서는 \(A^{(4)}_{0,2}=-2,\ A^{(3)}_{0m}=0,\ A^{(4)}_{2,0}=-8/5,\ A^{(3)}_{2,0}=-6/5\)이고 \(\Delta\ell=0,\pm2\)만 존재한다. 따라서
\[
\boxed{\frac{dF_{E,0}}{dx}=-2\frac{s}{H}F_{E,2}},\qquad
\boxed{\frac{dF_{N,0}}{dx}=0}\quad\text{(elastic Thomson)}.
\]
두 관계는 구현에서 즉시 검사하고 실제 모든 결과에서 광자/중성미자 양쪽 모두 \(|N_0-1|\) within rounding.

Elastic unpolarized Thomson은 BASS 원래 \(K_0=0\), \(K_2=-\Gamma_T(9/10)F_2\), \(\ell\ge3:K_\ell=-\Gamma_T F_\ell\) 및 정지 전자/무쌍극자 \(K_1=-\Gamma_T F_1\)으로 둔다. **BASS 원본 polarization source \(K_{I2}=-\Gamma_T[9I_2/10+\sqrt6\,E_2/10]\)의 \(E_2=0\) 절단**을 수행했으므로 complete polarized collision이라고 선언하지 않는다. Full BASS `E/B` tower와 \(\sqrt6\) 혼합, tilt/boost와 Thomson-to-baryon momentum은 이후 DAG에 포함된다.

Einstein source (에너지밀도 SI J m\(^{-3}\)):
\[
\Pi_\mathrm{rad}=\frac{\rho_{\mathrm{crit},0}}{3a^4}
  \left(\Omega_\gamma I_{\gamma,2}+\Omega_\nu I_{\nu,2}\right),\quad
\dot s+3Hs=\frac{8\pi G}{c^2}
  \left(\Pi_\mathrm{rad}+\Pi_\mathrm{matter}\right),
\]
\[
H^2=H_0^2\left[\frac{\Omega_m}{a^3}+\Omega_\Lambda+
\frac{\Omega_\gamma I_{\gamma,0}+\Omega_\nu I_{\nu,0}}{a^4}
+\frac{u_{\rm th}}{\rho_{\mathrm{crit},0}}\right]+s^2 .
\]
\(\Sigma=\sqrt3|s|/H\), sign \(\varepsilon_\sigma\) independent. Optional illustrative *non-causal first-order* matter viscosity \(\Pi_m=-2\eta_m s\), \(\eta_m=\nu_m\rho_\mathrm{dust}/H\) and internal heat \(d u/dt+5Hu=-6s\Pi_m\). 이 \(\nu_m\)는 새 측정치가 아니고 실제 원자/DM 운동론 closure가 아니다.

**물리학적 재수정:** 기존 toy all-\(\Omega_r\) Thomson은 ν에도 충돌을 가하는 upper-envelope이므로 생산용으로 채택하지 않는다. 소스 고정 \(\Omega_r=9.2\times10^{-5}\), \(T_{\mathrm{CMB},0}=2.7255\) K, \(a_R=4\sigma_{\rm SB}/c\)에서
\[
\Omega_\gamma=\frac{a_R T_{\mathrm{CMB},0}^4}{\rho_{\mathrm{crit},0}},\quad
\Omega_\nu=\Omega_r-\Omega_\gamma,\qquad
\Omega_\gamma/\Omega_r=0.5917144338784673,
\]
광자만 \(C_T\)에 결합하고 massless ν는 collisionless, 두 \(\Pi\) 합은 Einstein shear에 결합한다. \(\Omega_r\) 원래 값은 rounded background이며 실제 ν 질량/phase-space 스펙트럼 독립적으로 고정하지 않았다.

BASS PR159 \(W(\mu_{\rm ref})=1+\kappa P_2\), \(|\kappa|\le0.5\), \(I_{\ell=0}=N_0=1,\ I_2=N_2=\kappa/5\), \(\Pi/\rho_{\gamma}=\kappa/15\) at \(b=0\). \(\kappa\)와 초기 \(\Sigma\)는 독립으로 준다. Thomson OFF, \(\kappa_\gamma=\kappa_\nu\), \(\nu_m=0\)에서 두 타워 합은 **원래 PR159 Einstein-Vlasov RHS 및 출력을 실제 실행값으로 재현**한다. 강한 test 사례 \(\Sigma_{\rm ref}=0,\kappa_\gamma=\kappa_\nu=.2\): original BASS \(b_{\rm end}=8.411890570790299\times10^{-5}\), new L8 absolute mismatch \(8.4\times10^{-14}\) 이하 (조건/시계열 정밀도에 따라 차이 다름).

## 실제 실행 결과와 물리 경계

**11 initial envelope hierarchy runs**, actual original full `ZERO_composed_001/history.csv` (312238 rows SHA256 `4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f`)에서 source \(n_e(a)\)를 읽어 Thomson damping에 연결, BASS κ 초기 stress/Einstein shear backreaction의 signed \(\Sigma\), \(I_{E,2}\) 및 \(\Pi_r\)를 계산한다. Electron source는 시간 방향 one-way; 새 metric 때문에 기존 HHe reaction을 재진화하지 않음.

C1 전자밀도 PCHIP 18,368 node를 그대로 DOP853+L cutoff tests에 사용하면 sharp original HII transition 때문에 time adaptivity가 걸리고 error floor가 얽힌다. **실제 source에 양수 C² log-electron interpolation (8193 node)**를 추가하고 312238 original data points에서 관측한 max relative ne difference \(1.9755000594345873\times10^{-4}\), 99.9%-tile \(1.446198064892773\times10^{-4}\)를 별도 기록하였다. 이는 입력 보간의 *표본오차*이고 연속 함숫값의 엄밀 보증이 아니다. Legacy raw full PCHIP / decimated source / C2_8193, C2_16385 4 cases × L4/8/12 × tight 1e-13 ODE convergence를 `opacity_sensitivity.py`에서 실제 반복하며 각 구분된 endpoint 변화를 저장한다. 이 예의 **원천 전자밀도 보간과 ODE 적분오차를 고정하지 않고 hierarchy cutoff만 올려 과학적 정밀도를 주장하지 않는다**. 특히 L8→L12 difference는 C2_8193 tight solver에서 \(1.45717\times10^{-13}\)이나 다른 source interpolation/solver branches에서 큰 차이를 나타낸다. 해당 output은 `HOLD_ERROR_BUDGET`, 전체 HHe/관측 error certified 아님.

**서로 다른 photon + massless ν 타워 실제 물리 계산:** \(\Sigma_{\rm ref}=0,\kappa_\gamma=\kappa_\nu=+.2\)에서
- Thomson OFF: \(\Sigma(\bar z=4)=0.00010207032208826824\), \(I_{\gamma,2}=I_{\nu,2}=0.03986061128530538\).
- Real historic CMB Thomson ON: \(\Sigma=0.0001014917011532296\), photon \(I_{\gamma,2}=0.038729152224152755\), neutrino \(I_{\nu,2}=0.03986083558324631\) (gravitational background 변화의 간접 영향만). Photon and ν both \(N_0=1\).
- κγ=.2, κν=0 initial: \(\Sigma_{\rm end}=5.98189003618\times10^{-5}\); κγ=0,κν=.2: \(\Sigma_{\rm end}=4.16757755370\times10^{-5}\), demonstrating independently sourced radiation stresses.

**실제 C11 Case-A HHe 전자 소스 short receiver:** `receiver_coupled.py`가 원본 `research/source07_c11_casea_20261015/casea.py` 및 Grackle table을 실제 32 steps \(a=.2,\Delta t=10^{12}s\) 실행했다. \(x_\mathrm{HII}=.4\to .7513295747730638\), \(x_\mathrm{HeII}=.5\to .5553540579720488\), gas \(T=12000\to15154.128677066801\,K\). Original photon/chemical/thermal/CaseA escaped-radiation ledger \(\max|E|\approx1.066\times10^{-14}\,\mathrm{eV/H}\), photon + electron conservation residual \(4.44\times10^{-16}\). C11 \(n_e(t)\)가 Thomson \(\Gamma\)를 바꾸고 그 radiation \(I_2\)가 Einstein shear를 바꾸는 short proper-time feedback, measured \(\tau_T=3.4120614\times10^{-7}\), \( \Delta I_2=-1.2240680\times10^{-8}\), \(\Delta\Sigma=-1.9437034\times10^{-16}\). 이 source receiver는 전체 이력 동안 source age/redshift, gas proper densities 및 microscopic recombination rates를 새 metric에서 동적으로 재계산하지 않으며, whole-EoR 연속 방정식 완성이라고 선언할 수 없음.

## 실제 다섯 공급자 재검증과 채택 게이트

[REI PR134](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/134) byte-bound source supplier consumer Python **6/6 PASS**를 해당 새 브랜치에서 다시 수행. Table:

| supplier | 실제 이용한 데이터 / 코딩 | adoption |
|---|---|---|
| BASS PR159 및 위 PSTF hierarchy/dossier | independently computed Einstein–Vlasov with \(\kappa\) → new LRS Legendre \(\Delta\ell=0,\pm2\) energy and number source and gamma/ν gravitational stress | **hierarchy LRS unpolarized sub-block implemented**, BASS full E/B/11 Bianchi typed hierarchies not merged |
| bass_cr PR71 | source-pinned `PositivePacketOracle`, true dyadic source-age bins; actual REI C10 photon packets and six photoevent/heat enclosures | real test PASS but precision gate `HOLD_PRECISION_TARGET`, no unverified source compression in coupling |
| BASS_HE PR64 | source-locked 16-cell warm P01 optical tau full interval, Decimal recheck | valid distinct warm physical source only, not cold REI |
| rec_bianchi PR94 | independent HyRec2012 HHe z20 initial donor `x_e=.000210349192936`, \(T=9.3060424K\) and source alternative instantaneous Thomson +5.1746% | opt-in sensitivity only, not swapped into baseline C11/AX08 |
| WU088_HH PR83/84 | original physical guard called; physical \(k_{\rm HH}(T)\) not admitted | `HOLD`, not invented rate source |

Historical original BASS valid \(\Gamma_T\) in proper time \(c\sigma_Tn_e\), but original kinematic PSTF docs use \(\kappa'\) per conformal time, so \(\partial_x\) rate divides by physical \(H\). This units change is explicitly enacted in new LRS adapter; no double application of \(a\).

## Verification & next DAG

- Native source input 16 original Git blobs PR134 revalidated, 6/6.
- BASS Einstein Vlasov direct code invoked and independently reproduced (all no-thom scenarios), source original first-call and gravity feedback identities checked, positive W. Angular Boltzmann matrix \(A^{(4)}_{02}=-2\) and \(A^{(3)}_{0\ell}=0\) confirmed exact in Wolfram15; actual photon number/E0 conservation checks.
- New `test_hierarchy.py`: **12/12 PASS**, originally a separate actual ne interpolation/time ODE error mixing defect was investigated and corrected using physically explicit C2 donor and tighter tolerance, not arbitrary looser tolerance.
- `test_species.py`: **7/7 PASS**, gamma/neutrino splitting, source Ωr non-doublecounting, source-specific stress, true photons only Thomson, ν collisionless and distinct N0 conserved, plus negative fixture.
- Native original C11 Case-A tests and REI C12 negative source gates can be rerun with the same source; source code paths are inherited in PR134, not recreated with copied equivalent formulas. Local Codex NOT_USED; native subagent NOT_RUN.
- Spectral/time/angle hierarchy convergence is scoped, **not global AX11 physical error bound**. Next substantive node should integrate source-age photon emissions and absorption/redshift into evolving actual HHe gas and Einstein \(\pi_{ab}\) per-step, add BASS documented E/B/Thomson cross-coupled polarization and matter kinetic hierarchy with actual collision terms, then matched AX11 dt/dE/dμ, gas abundance+temperature and observer-side tail. Existing unadmitted HH and donor initial state are explicitly held; preserve actual original native AX08 source and checkpoints, establish new source identity for changed equations.

`results/hierarchy_coupled_results.json`, `results/gamma_neutrino_separate.json`, `results/C11_thomson_receiver_integration.json`, `results/opacity_source_sensitivity.json`, actual 2-D PNG and `NEXT_DAG.json` are machine-readable continuation sources. Source SHA manifest identifies legacy provider and genuine BASS blob identities.

**Scientific status:** BASS↔REI Einstein+massless Boltzmann radiation quadrupoles including separate photon/neutrino backreaction and one-way physical HHe source Thomson **SCOPED_VERIFIED**; full coupled astrophysical HHe/BBN-style \(\Sigma,\pi_{ab}\)-resolved reionization source and polarized observer predictions remain **NOT_ISSUED**.
