# AX08 SHEAR_MINUS 전체 이력의 실제 결과 및 이론·코딩 연구 루프

2026-10-15 KST · REI-AXBI-GOAL-20261014 · `physmath-research-loop` 이론/코딩 실행, 기존 실험 종료 확인 후 실행.

## 판정

**`SHEAR_MINUS_FULL_HISTORY_COMPOSED_AND_SCIENTIFIC_DIAGNOSTICS_EXECUTED`**, `SCIENTIFIC_ADMISSION_NOT_ISSUED`. 이론식, 데이터 가정, 적분 시간 변수와 physical case의 original source identity를 고정했다. 별도의 local Codex **미사용**. 현재 호스트에 native subagent create/wait 도구가 없어 `native_subagent=NOT_RUN`이며 Rust OS threads와 혼동하지 않는다. 기존 AX07/AX08 cold MD14+BB50K, Case-A source, 원본/continuation 과학 파일, checkpoint, solver executable은 불변이고 재실행된 과학 solver는 이번 루프 0회다. 본 완료 결과는 **직전 승인된 단 1회 SHEAR_MINUS continuation을 자연 종료까지 기다려 회수**한 것이다.

### 실제 독점 solver 종결 → source-relation 보존 이력 결합

- Original `SHEAR_MINUS`: accepted 200000, \(a=0.08873654701704167\), original compiled source `d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185`. 자원 제한 종료이지 수치 실패가 아님.
- 기존 1회 allocation continuation: scientific PID 1099975, 실제 `RETURN.txt` 정상 `COMPLETE_SEGMENT_TO_SELECTED_ENDPOINT`, exit0, `result=Ok(())`, \(a=0.2, \bar z=4\), accepted cumulative 312237; continuation RETURN SHA256 `7149130505022a9edfb478f35a12a6ad8d7d45aa5f25299b303cb0ecd2ec6856`. Compiler epoch `4de69c1e68ebd395fe2d0b5580d901b9a82bde86cadbd11bdd07e5ad2042b4a1`은 기존 독립 검토의 `REVIEWED_RESOURCE_ONLY` (4096MiB output arm, numerical kernels unchanged)와 연결됨. 새로운 solver start, 자동 재시도, background 수정 **없음**.
- 기존의 immutable `compose_signed_history.py`를 frozen private binding/실제 terminal digest로 실행. **Exit0**, wall 148.97s, actual output `research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_MINUS_composed_001`. 전체 입력 약 1.8 GiB. 전체 다섯 CSV 공유 boundary는 정확히 한 번 제거.
- 결합 수량: history312238, H/He/electron abundances1873428, ledger8430426, feedback312238, spectra2040752. 원본 byte, adopted new source epoch, beginning/end checkpoints, source compatibility, accepted step and full chemistry/ledger constraints 검사 `COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION`. 원본 고용량 데이터는 로컬에 보존하되 GitHub에 중복 게시하지 않음. Public evidence `evidence/COMPOSITION_RECEIPT.json`, `evidence/COMPLETED_CASE_INPUT.json`, exact SHA.

## Full H/He/electron physical census

검증된 독립적 [AX08 PR119](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/119) `clock_census.py` (기존 완료 ZERO/HALF_PLUS 소스/기법 불변)를 재사용하여 처음부터 마지막까지 MINUS **312238 time states ×6 = 1873428 실제 abundance 행**을 검사. 현재 원본 species registry: H_I, H_II, He_I, He_II, He_III, electron. 반복 시간, source/mass/charge/temperature 불일치 없이 완료; 최대 species fraction 합 잔차 \(4.5103\times10^{-16}\), 최대 normalized electron/charge residual \(2.4044\times10^{-16}\), \(Y_{\rm baryon}\) mass closure \(3.3307\times10^{-16}\). 중요: baryon number-per-baryon normalization은 \(\sum_i A_i Y_i=1\), He에 \(A=4\) 필요.

실측 final \(\bar z=4\): \(x_{\rm HII}=0.9999973170965605\), \(x_{\rm HeII}=0.9742081090684215\), \(x_{\rm HeIII}=0.025784309740003234\), \(T_{\rm gas}=7900.629307442252\)K, electron/H \(1.0833943516797118\), proper elapsed \(4.279464240897777\times10^{16}\)s. 이는 지정된 conditional original source/model 결과지 관측 우주에 대한 재이온화 이력이 아니다.

별도 std-only Rust streaming reader `abundance_minus_fast.rs`는 이전 PR119 검증된 소스의 case binding만 실제 minus case로 변경한 동일 검증 알고리즘. 실제 accepted312238×6 species 경로 **1.6158 s**, peak RSS 약4MiB; Python full census **14.5292 s**, 약9.0× 성능 향상은 **저장 이력 후처리만** 대상. 서로 다른 구현 잔차는 허용된 2e-15 이하로 확인.

## 고유시간 대 동일 scale factor 분해와 실제 수치 결과

단조 평균 scale \(a\)의 matched \(4097\) \(\ln a\) points:
\[
\Delta X|_t=\left[X_q(t_q(a))-X_0(t_0(a))\right]
+\left[X_0(t_0(a))-X_0(t_q(a))\right].
\]
첫 항 fixed mean scale, 둘째 항 reference background clock drift. 원래 H/He 및 thermal physical-clock t와 별개의 reference clock을 분리했다. No out-of-domain extrapolation.

| Actual ZERO vs \(q=-0.01\), sampled max absolute | Fixed \(a\) | Fixed proper \(t\) |
|---|---:|---:|
| \(x_{\mathrm{HII}}\) | 2.46717511553918e-6 | 1.71026628434934e-5 |
| \(x_{\mathrm{HeII}}\) | 2.30094038866646e-6 | 1.48487276353526e-5 |
| \(T_{\mathrm{gas}}\) [K] | 0.0265783457457 | 0.154065543631 |
| \(J_2\) [eV/H] | 0.01190233753943 | 0.01190233753942 |

\(\max|\Delta t(a)|=2.49032580232\times10^{11}\) s, 별개 proper clocks. Source-minus & +0.005의 q amplitude비는 fixed \(a\)에서 \(x_{\rm HII}\) peak 3.9999791, \(T_{\rm gas}\) peak 3.9999511 (leading \(q^2\)), \(J_2\) peak -2.0006153 (leading odd \(q\)). 두 진폭만으로 추정된 고차항 및 tiny signal은 **AX11 분해능 수렴이 없으므로 미인증**.

새 `minus_milestones.py`는 real full history에서 xHII 0.01,0.1,0.5,0.9,0.99,0.999 *최초 upward crossing*의 정확한 bracketing cell을 찾고 선형 보간한다. Fixed-redshift scalar:
- \(x_{\rm HII}=0.1\): \(\Delta \bar z_{q=-.01}=-3.10977498419\times10^{-5}\) vs \(q=+.005\) \(-7.77460726731\times10^{-6}\), 비 3.9999126.
- \(x_{\rm HII}=0.5\): \(-7.93980347957\times10^{-6}\) vs \(-1.98496630421\times10^{-6}\), 비 3.9999689.
- \(x_{\rm HII}=0.9\): \(-4.45314288022\times10^{-6}\) vs \(-1.11329224595\times10^{-6}\), 비 3.9999766.
Interpretable finite-q exploratory scaling only, no population/likelihood inference and numerical error UNKNOWN.

## 독립 복사압 검산 및 feedback reconstruction

원본 Rust `axbi_background::isotropic_initial_radiation_moments`의 initial-ray Simpson4096 모멘트와 달리, 별도 `verify_radiation_minus.py`는 현재 local angle에서 128점 GL 및 stable quadrature로 실제 312238 full saved rows를 다시 계산. \(\max|\Delta P_{\rm saved}-\Delta P_{\rm GL128}|/\rho_{r,\mathrm{iso}}=2.34664624\times10^{-15}\) (ZERO=0). Saved final minus \(\Delta P=+4.1752491628013586\times10^{-13}\) J/m³ vs GL \(+4.1752491628012874\times10^{-13}\) J/m³, sign/units/covariant direction consistent.

재사용한 기존 Python Kahan compensated time integration과 새 std-only Rust \(O(1)\)-memory streamer의 **312238 per-case saved feedback** 결과 일치:
- MINUS maximum \(|\delta s/H|=1.0210497766172324\times10^{-5}\)
- MINUS endpoint \(\delta s/H=+1.0061705312466439\times10^{-5}\)
- max additional energy fraction \(9.728861296337742\times10^{-8}\)
- Historical ZERO \(|\delta s/H|=3.7765658078038334\times10^{-23}\).
이들은 previously frozen screening ceiling \(10^{-4}\) 이내다. 그러나 **Einstein–radiation backreaction를 self-consistently 켜서 통합한 방정식이 아니다**. 작은 abundance 차이의 solver error bound도 아니다.

## 새로운 exact-Wolfram 수학 검산

\(D=(1-\mu^2)e^{-2b}+\mu^2e^{4b}\)에 대해
\[
\frac{\rho_r}{\rho_{r,\rm iso}}
=\left\langle D^{-2}\right\rangle
=1+\frac85b^2-\frac{16}{21}b^3+\frac8{35}b^4
+\frac{16}{231}b^5+\frac{4528}{32175}b^6+O(b^7),
\]
\[
\frac{\Delta P_r}{\rho_{r,\rm iso}}
=\left\langle P_2(\mu)D^{-2}\right\rangle
=-\frac85b+\frac87b^2-\frac{16}{35}b^3-\frac{40}{231}b^4
-\frac{4528}{10725}b^5+\frac{1328}{2145}b^6+O(b^7).
\]
Local **Wolfram Engine 15, exact rational coefficient sequence exit0** (`ax08_shear_parity.wl` + saved stdout). \(H_{\rm density-fixed}(q)=H(-q)\), \(b(-q)=-b(q)\) 이므로 scalar effective-radiation energy first odd term \(O(q^3)\), signed quadrupole first odd term \(O(q)\). No collision/source/free-streaming identification beyond stated geometry assumptions. Exact null ray geometry background: [Fleury, Pitrou & Uzan, Phys. Rev. D 91 043511 (2015)](https://doi.org/10.1103/PhysRevD.91.043511).

## 실행·검증·코드 최적화

- Original full composer **one validated invocation only**, source-binary fixed, exit0; processed 1.8GiB data, ~149s.
- Python complete H/He chemistry census PASS, Rust native streamer PASS with all 1,873,428 ions. Independent full pressure parity <\(3\times10^{-15}\).
- `minus_full_diagnostic.py`: hash-bound three real completed cases, 4097 logarithmic matched samples, signed unequal-amplitude probe, 2-D H/He/temperature and clock-drift diagrams.
- `minus_milestones.py`: monotone-source first upward crossing + alpha interpolation, actual source rows and per-event bracket widths.
- `feedback_minus_fast.rs`: reuse source identity of previous PR118 streamer, edit only expected ZERO+MINUS case paths, \(O(1)\) per stream, stable Kahan pressure, no new solver.
- `test_minus_full.py`: **7/7 scoped tests PASS**, two initial test-schema KeyErrors diagnosed and repaired within same implementation episode, scientific results unchanged. Python/Rust census crosscheck, actual GL128+feedback scopes, source receipts, synthetic clock and crossing rejection.
- **Do not infer unmeasured solver speedup from Python→Rust science-output postprocessing gains.** BLAS single-thread CPU affinity 2/3 selected; no local Codex.

## 최신 다른 repo의 실질적 사용 범위

- [rei_bianchi PR119](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/119): upstream exact all-species census `clock_census.py` and source-bound paired manifest reused without rewriting physics; base SHA `b0dda3b37e4958cc48af8bbd7bba421075f6424f`.
- [BASS_HE PR64](https://github.com/cosmosapjw-quantum/BASS_HE/pull/64): independent warm P01 16/16 source-scoped Thomson tau, **not** cold AX08 opacity. Separate [REI PR120](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/120) preserved explicit model-contrast opacity/Poisson diagnostics.
- [bass_cr PR71](https://github.com/cosmosapjw-quantum/bass_cr/pull/71): threshold-resolved age-conditioned photon q moments require extra true source child moments; no adoption of unvalidated compression into frozen AX08.
- [Friedrich et al. 2012](https://arxiv.org/abs/1201.0602): H/He photoheating and temperature time-step constraints warn against abundance-only error gates. No directly imported numerical fit/tolerance.
- SciSpace & Exa used for primary method crosscheck; no literature claim that these results establish this project's novelty.

## Next DAG, user-locked acceptance

**Next science execution candidate**: `SHEAR_HALF_MINUS` already has a private frozen independently reviewed binding, but requires separate one-shot launcher, source-locked PLUS/MINUS/HALF_PLUS terminal classifications and fresh local+remote controller slot release. No new science solver started in this loop. `SHEAR_PLUS` has a distinct aborted observer/process classifier recovery and no full endpoint. After both completed, do full signed-five-case parity and **AX11 matched dt/dE/dmu** (especially \(\sim10^{-6}\) fraction and \(\sim0.03\)K Tgas); AX12 source/IC variants, current physical H/He and uncertainty, and observer optical depth remain separate. Existing true `SHEAR_MINUS` completion, original raw preserved, no overwrite.
