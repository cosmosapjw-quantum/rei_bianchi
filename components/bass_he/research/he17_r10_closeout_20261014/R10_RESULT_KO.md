# BASS_HE HE17 R10: 검증된 첫 셀 결과의 종료·재개와 AXBI 짧은-clock 대안

**일자:** 2026-10-14, KST. **단계:** `$physmath-research-loop` theory **R10**만 수행. 현재 출발점은 BASS_HE draft PR54 `34303765770fb8d35d9ddef92dc9e8949e147dca`이며, 다음 R10 산출물은 새 원본을 덮어쓰지 않는 누적 인계다. AXBI의 연구·계산 lane은 사용자가 병렬로 요청한 별도 보조 과제다. 

## 1. 종료 판정의 경계

**HE17 R1–R10의 지정된 첫 셀 공변 전류·광학 소비기 과제를 `COMPLETE_SCOPED_FIRST_CELL_AND_HANDOFF`로 종료한다.** 이것은 전체 HE/native/global 연구의 완료가 아니다. R9 archive 4,841,475 bytes, SHA256 `fb3850cd844045755e9fcb3c7836b916b4236c9d219351cab4b3817fd05d9f77`의 CRC와 21개 manifest payload를 새 호출에서 검사했다. R9의 read-only `verify_release.py`는 exit 0, 원래 13개 `unittest` 모두 통과했다. 원 R9 consumer 12,645 bytes, SHA256 `7a60a9f3e8e74ce6704268d79b2705e21fdf1bca085cca6b802416fb24016dd0`, Git blob `25824afaa214299f70750919df7d9df34a4adea0`를 변경하지 않았다. 초기 R9 xAct 심볼 파싱 실패와 복구 로그도 그대로 포함했다.

원본의 science scope는 **warm P01** FT03/HM12 Case A, prescribed normal-comoving non-tilted LRS Bianchi I, **0–6,250,000,000 proper seconds의 첫 저장 셀**, photon bins 2904, original input NPZ `3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be`, receiver commit `a5c958c414dea41216b445c05f58df837f05cacb`, fixed Hermite `7a2015398e7857ecb8dccb05482e246d7c412816eace6153f1c47eceb9b983be`다. CR/RCT/HH OFF. Metric(-,+,+,+), x0=ct, u.u=-1, c와 k_B 및 hbar의 차원을 유지한다.

### 재현 가능한 정식 결과

기체 proper 전자밀도는 `n_e=n_H [x_HII+(3/38)(x_HeII+2x_HeIII)]`, source의 n_H는 **proper cm^-3**이고 electron column은 m^-2이다. Photon state의 **reference-volume** stock은 electron proper density와 다른 좌표다. 일반 공변 전류는

\[
 J_e^a=c n_e u^a+j_e^a,\quad u_a j_e^a=0,\quad
 D=-u\cdot k>0,\; A=(c\nabla_a\vartheta)k^a>0,
\]
\[
\mathcal C=\int_{0}^{6.25\cdot10^9s}\frac{cD n_e-k\cdot j_e}{A}\,d\vartheta,
\quad\tau_T=\sigma_T\mathcal C,\quad\sigma_T=6.6524587051\cdot10^{-29}\,\mathrm{m^2}.
\]

Source normal clock has D/A=1, j_e=0. Sigma is applied exactly once. The R7 64-piece bound, consumed by R8/R9, remains `R_C<1585.727990634604 m^-2`. Certified exact-real finite-model first-cell optical depth and scattering-out probability are

\[
\boxed{\tau\in[7.99991934859042930820,\;7.99991934859042951919]10^{-9}},
\]
\[
\boxed{P_{\rm conditional}\in[7.99991931659107460155,\;7.99991931659107481254]10^{-9}}.
\]

The R9 consumer returns these inherited intervals **without source ODE execution**; its added explicit foreground T∈[0,1] readout is a separately conditioned source, default `observer_probability=null`. Synthetic T=1/4 is only a control. `full_history_tau=null`; remaining 15 stored cells are not fine-certified. The complete raw 2904 photon endpoint error is preserved; the four-component `hB error` compression is valid only while B remains the original fixed first-cell matrix. For an actual later cell, use that cell's own reference, domain, A/B/C Jacobian majorants and residual, and the raw incoming gas+2904 photon errors. Existing native CMB Boltzmann/polarization solver not activated; physical atomic calibration, spectral continuum, observer tail and external independent review remain open.

## 2. Actual Codex repo and four completed temperature-table pilot runs

Live authorized worktree read at 2026-10-14T13:50:09Z (22:50:09 KST): HEAD `1583938d663ea90d0688303b28e5e1f49e3aa816`, tracked status clean. AX07 ZERO complete at scoped conditional `zbar20→4`; AX08 signed family IN_PROGRESS with original HALF_MINUS and recovered observer recorded as running; AX11 T1 and AX12 variant configs prepared but runs not started. AX13 interim figure/report scoped completed, AX14–16 pending. `STATE.next_ready_ids=[]`, whole-goal admission NOT_ISSUED. This is the current STATE's report, not an independent process ps measurement; no owner files/processes/queue or solver were modified by this R10.

Previous HE electron-floor correction and combined HH source-pair/CR union-knot comparator are **already present and hash-confirmed**. Do not apply the R8/R9 supplier patch again. HH69's T1 source relation remains scoped to three output-resource edits and a changed numerical target, not trajectory identity. CR62's exact union-knot PL norm is a reconstruction norm, not true-IVP error. HH/CR atomic/kinetic numerical bounds are not imported into the cold IGM/MD14 AXBI source.

The owner **independently completed** four `zbar20→19.8` temperature-table short-pilot runs. Read the actual `INDEPENDENT_PILOT_REVIEW.json`, `TRAJECTORY_COMPARISON.json`, `PERFORMANCE_RECEIPT.json` and `PILOT_RECEIPT.json`:

| Case | Direct process wall | Table process wall | Accepted / RHS / rate calls |
|---|---:|---:|---:|
| ZERO | 89.55 s | 90.05 s | 2547 / 53889 / 130863 |
| PLUS q=+.01 | 118.35 s | 119.71 s | 2547 / 53889 / 130863 |

All four exits 0; corresponding trajectories passed scoped pairwise short-history numerical checks, with normalized photon number L1 max `7.460637988537529e-17`, photon energy L1 max `6.102780225992955e-17`. But the observed table-to-direct time ratios **1.00558347 / 1.01149134** indicate **no measured short-history speedup**. One ordered sample each, table load ~0.57s, no 64-core/long-history performance admission, no new physical result or signed-shear detection. Owner's independent review says retain direct default; table opt-in only for tested conditions. Do not reflexively rerun pilots or launch new ones.

## 3. Constructive nonduplicating REI support: cancellation-stable local time increment

The original `axbi_driver.rs` computes `dt = point_at_scale(to).time_s - point_at_scale(old.a).time_s`. `BACKGROUND_TABLE_001` documented a short-step subtraction discrepancy near Δln a=1e-10 (frozen 1e-8 local relative comparison limit); `Table::increment` already exists as a **validated diagnostic** but its production table integration remains HOLD. The following new small standalone **independent candidate** derives a broader source-specific analytic bound. This is not a replacement in the owner driver, not a new blocking precondition and not a claim of exclusive novelty.

Set `x=ln a`, `a_ref=1/21` and

\[
 F(x)=\Omega_\Lambda+\Omega_m e^{-3x}+\Omega_r e^{-4x}
 +q^2 F_\mathrm{FLRW}(x_{\rm ref})e^{-6(x-x_{\rm ref})},
 \qquad f(x)=(H_0\sqrt{F(x)})^{-1}.
\]

For SameHDiagnostic omit the q² term. Coefficients are nonnegative, q∈{0,±.005,±.01}, all initial/source/cosmological constants are unchanged. Then dt=∫_x0^x1 f(x) dx, and the **local Simpson candidate** is

\[
S_2=\frac{h}{6}\left[f(x_0)+4f(x_0+h/2)+f(x_1)\right],\quad
h=\ln(a_1/a_0)>0.
\]

Let `p_n=c_n e^{-nx}/F`, n∈{0,3,4,6}, and `m_k=Σ p_n n^k`, so `0≤m_k≤6^k`. Symbolic calculation with actual Wolfram verifies

\[
\frac{f^{(4)}}{f}=\frac{105}{16}m_1^4-\frac{45}{4}m_1^2m_2
+\frac94m_2^2+3m_1m_3-\frac12m_4.
\]

Triangle bound yields `|f''''|/f ≤ 30537`. Since f'/f=m1/2≤3, `f(x1)/f(x0)≤exp(3h)`. The standard Simpson remainder \(|S_2-\int f|\le h^5\|f^{(4)}\|_\infty/2880\) therefore gives the **rigorous exact-real quadrature-truncation bound**

\[
 \boxed{\frac{|S_2-\Delta t|}{\Delta t}\le\frac{30537}{2880}\,h^4 e^{3h}},
\quad \text{for positive coefficients and exact function evaluations.}
\]

For `h≤0.005` the right side is **≤6.727106695783466e-9**. This bound deliberately does **NOT** include binary64 formation of endpoints, `log1p`, `exp`, `sqrt/hypot`, H/source coefficient evaluation, summation, native adaptive steps or physical background model error; a production claim needs those controls and actual driver parity separately. All quoted units: h dimensionless, dt seconds, H s^-1.

The new read-only `supplier/src/axbi_short_clock.py` uses the exact original source H(a) formula, a `log1p` of the actual stored binary64 endpoint difference, three H evaluations and `math.fsum`. In30 high-precision actual-path probes (five log-interval widths×six signed family choices), exact-real quadrature remainder stayed inside the derived analytic bound. Largest **observed binary64 candidate versus 80-digit integration** relative discrepancy was 1.080549907801215e-12; not a certified binary64 supremum. At the actual held benchmark endpoint bits `4587023449039406616` and `4587023449040092879`, the independently computed q=0 candidate is `844944.38036397 s`, compared with the 80-digit integral `844944.380363970140013608858049 s`, relative discrepancy `2.2818326147941e-16`. q=+.01 yields `844902.1363132355 s` against `844902.136313235670593282960609 s`. The owner's previous direct cumulative subtraction exhibited ~2.08e-7 relative discrepancy on this q=0 held row; the existing Table.increment diagnostic already avoided it. No native runtime speedup or identical source-code binary64 arithmetic is claimed.

**Actionable positive transition:** This supplier is `READY_FOR_OWNER_THEORY_CONSIDERATION` only. If owner needs to address the independent short-clock table HOLD, compare this option against its existing stable Table.increment and immutable source/cumulative time authority using one bounded driver parity/roundoff test under a separate approved task. Do not change clocks, output histories or performance source while the active Codex run proceeds; production READY has not been earned. The four completed T_TABLE pilots already show no short-history speedup, so prioritizing long-run abundance delivery is more valuable than repeatedly optimizing that table without whole-driver evidence.

## 4. R10 executed checks, limitations and backups

This R10 ran read-only R9 verify_release exit0 and13 Python consumer tests exit0 without original ODE/chemistry/photoionization calls. Separate supplier tests observed expected RED for missing implementation then GREEN:5test methods,0failures. 30 independent 80-digit mpmath real quadratures plus2 actual held intervals passed exact-real analytic remainder crosschecks; these are local postprocessing calculations, not native tests. Actual Wolfram15.0.1 returned five scalar zero groups plus four xAct/xTensor1.3.0 zero tensor projections after pinned archive/file SHA verification. An unrelated `Symbol::undefined2` advisory referred to symbolic A,B; all requested residuals returned exactly zero. The Wolfram script is reconstructed local source, CAS observation a transcription, not raw transport byte identity. External independent scientific reviewer and native subagents NOT_RUN; serial fallback used. SciSpace and Exa primary source discovery support standard quadrature theory, not the frozen AXBI numeric inputs.

The original R9 ZIP and 21 files are embedded unchanged; the new R10 ZIP is manifest-verified and can be extracted anywhere. `python verify_resume.py` validates both manifests and uses the unchanged original R9 consumer to check the exact source-bound first-cell result, with no network or science producer. `supplier/check_mp.py` is optional: it runs numerical quadrature diagnostics and is **not** called by `verify_resume.py`.

Storage: new R10 full and small supplier archives are intended for additive create-only Drive/Dropbox backup, with actual provider outcomes recorded separately from local evidence. Backup acknowledgement does not mean independently tested remote restoration. No owner REI mutation, shared slot change, old source promotion, solver launch, main merge, or production switch.

## 5. Exact resume and future research boundary

Extract `BASS_HE_HE17_R10_CLOSEOUT_20261014_v1.zip`, change directory to `HE17_R10_20261014`, read `READ_FIRST_KO.md` and `RESUME.json`, and run `python verify_resume.py`. To examine the independent AXBI short-clock alternative run `python -m unittest discover -s supplier/tests -p 'test_*.py' -v` and optionally `python supplier/check_mp.py`.

**R10 ends HE17's scoped R1–R10 loop.** Do not automatically begin a new cycle. For a future user-requested full warm P01 continuation, the next physically distinct node is `HE18_WARM_SECOND_SAVED_CELL_SOURCE_CERTIFICATE`, which requires a source-matched next reference, gas/photon domain, actual A/B/C, whole-cell residual, binary/provider evaluation budget, original 4gas+2904photon error packet and a separate native receiver check. This node is `PROPOSED_NOT_EXECUTED`. AXBI AX08/11/12 and source/IC robustness remain separate user-prioritized scientific goals; optical depth stays optional/nonblocking for the BBN-style abundance plots.

### Primary methodological literature

- Talvila & Wiersma, *Simple derivation of basic quadrature formulas*, arXiv:1202.0249. Standard Simpson fourth-derivative error proof.
- Younsi, Wu & Fuerst, *General relativistic radiative transfer: formulation and emission from structured tori around black holes*, A&A 2012. Covariant optical depth and comoving opacity.
- Kehlet & Logg, *A posteriori error analysis of round-off errors in the numerical solution of ordinary differential equations*, Numerical Algorithms, DOI:10.1007/s11075-016-0250-4. Distinguish state/discretization/roundoff.
- Owned code: `rei_bianchi/rust/rei_microphysics/src/axbi_background.rs` and `axbi_driver.rs`, at latest observed head `1583938d663ea90d0688303b28e5e1f49e3aa816`, and reviewed BACKGROUND_TABLE_001 short-step HOLD. All source-specific numerical evidence is from user-owned repo or current calculated local pilot, not literature calibration.
