# REI P01-16 / AX08 병렬 이론·코딩 연구: 물리 모형이 다른 두 opacity history의 소유권 구분

2026-10-15 KST. 사용자 지시: 현재 실행 중인 AX08 `SHEAR_MINUS`를 방해하지 않고 ChatGPT에서 직접 이론 검산 및 로컬 Python 코드 구현·실행; **local Codex 사용하지 않음**. PhysMath research loop 1.3.0의 다음 좁은 연구 노드: source intake/derivation/numerical implementation and test/measurement. 이전 10단계를 형식적으로 반복하지 않음.

## 실제 프로젝트 입력과 권한 경계

독립 worktree `/home/cosmosapjw/rei_worktrees/rei_p01_16cell_bridge_20261015`, 부모 `rei_bianchi` HEAD `0fcb2dddf5de6b583c2e00f150abff0b2afb6315`. Canonical 작업 트리와 해당 과학 실험의 원래 실행 파일/lock/source/gas/checkpoint은 수정하지 않음. 현재 `SHEAR_MINUS` production PID 1099975는 CPU0에서 진행 중이며, 새 프로그램은 CPU2/3에 affinity 및 BLAS 1 thread 사용. 독립 native subagent host tool은 노출되지 않아 NOT_RUN; 데이터 ThreadPool을 native agent로 기록하지 않음.

BASS_HE 출처: [PR64](https://github.com/cosmosapjw-quantum/BASS_HE/pull/64) `b0af50b052862320896085fac70250f51c077944`, originally frozen `rei_bianchi a5c958c414dea41216b445c05f58df837f05cacb`. **Warm HM12/FT03 Case-A source-scoped 16/16 original saved cells, \(0\le t\le10^{11}\,\mathrm{s}\)**. 이전의 7-cell result와 새 9-cell chain complete, gas4 + photon2904 component radii checked conditionally on original source/primitive. Private source NPZ/full radiation modes **읽기/복제/게시하지 않음**. 공개 CSV, RESULT_STATUS, PERFORMANCE crosscheck만 GitHub pinned HEAD에서 byte-for-byte 내려받음.

- Public 16-row input CSV SHA256: `46b4b3ef86e9a69d8fe5d6ac585bc9c145e2fde99f61a8acf3675b4491b86a40`.
- Source-scoped status SHA256: `c2bc5cda5f4c1db55fd1166d4aa86cf88d4b17dc3e574be1e5277fa49a493374`.
- CSV 16/16 strict `cell`, proper clock step \(6.25\times10^9\) s, positive outward tau bounds, SHA, original commit, claim ceiling guard PASS.

**BASS_HE scientific admission boundary:** `SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES`, full original ODE not rerun, not native binary64/provider rounding proof, not observed CMB optical depth, not physical EoR ion abundances.

## (A) 이론 R5/R7: 16-cell 산란 횟수·유한 구간 kernel

\[
\tau_{\rm warm}\in[1.279983109176429360327345119834258225,\,
1.279983109176430675377905063299454235]\times10^{-7}.
\]

동질·정지 normal gas, 독립 Thomson 산란 optical hazard \(\lambda(t)=\sigma_T c n_e(t)\) 조건에서, 비균질 Poisson 산란 횟수 \(N\)의 \(k\)-회 확률과 3회 이상 꼬리는

\[
P_k=e^{-\tau}\frac{\tau^k}{k!},\quad
R_{\ge3}=1-e^{-\tau}\left(1+\tau+\frac{\tau^2}{2}\right)
=e^{-\tau}\sum_{k=3}^\infty\frac{\tau^k}{k!},\quad
R_{\ge3}'=\tfrac12 e^{-\tau}\tau^2\ge0.
\]

따라서 실제 \([\tau_l,\tau_u]\)를 단조식에 대입하면 **source-scoped** 확률의 enclosure가 얻어짐. 90-digit Decimal에서 직접 `1-exp` 빼기 대신 positive series(3–20회, 검증된 잔여 bound)를 사용. Wolfram exact-rational 변환/미분에서 \(R'_{\ge3}-e^{-\tau}\tau^2/2=0\) 확인, endpoint numeric independent agreement.

16th-cell 결과:
- \(P(N=1)\in[1.2799829453407638679758860,1.2799829453407651830261093]\times10^{-7}\).
- \(P(N=2)\approx8.19178275035038\times10^{-15}\).
- \(P(N\ge3)\in[3.4951146300059622556532423,3.4951146300059730282617351]\times10^{-22}\).
- \(1-e^{-\tau_{16}}\) midpoint \(1.27998302725859552411944\times10^{-7}\). BASS_HE의 "first-collision" 표기는 \(P(N\ge1)\), \(P(N=1)\)과 구별됨. 차이는 \(P(N\ge2)\) 약 \(8.19\times10^{-15}\).

엄밀한 느슨한 상계 \(R_{\ge3}\le\tau^3/6\)도 별도 보존. **이 숫자는 scalar scattering event count의 tail이지, E/B/Stokes·thermal gas coupled Boltzmann operator의 norm error bound가 아니다.**

16-cell 범위 내 마지막 산란 \(\tau_i\)의 discrete cell probability:

\[
w_i=e^{-\tau_{16}}\left(e^{\tau_i}-e^{\tau_{i-1}}\right)>0,\qquad
\sum_{i=1}^{16}w_i=1-e^{-\tau_{16}}.
\]

누적 \(\tau_i\)의 조건부 interval들에서 monotone interval endpoints를 사용하여 \(w_i\)를 상·하계화했고, 모든 16개 cell이 양수이며 중간값 망원합을 Decimal90으로 검증. 이는 **주어진 warm P01의 0..1e11초 유한 source window**에 대한 \(w_i\)이고 observer visibility는 아니다. `certified16.py`, `finite_visibility.py`, `results/certified_poisson.json`, `warm_P01_finite_visibility.json`.

## (B) 코딩 C5–C8: 진짜 AX08 cold 5-case early history 독립 재계산

대조 대상은 다른 원본 physics identity `d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185`. ZERO, SHEAR_MINUS, SHEAR_HALF_MINUS, SHEAR_HALF_PLUS, SHEAR_PLUS **다섯 원본** 200,001-step checkpoints의 `history.csv`, `config.cfg`, `source_identity.txt`, `RETURN.txt`를 읽되, \(t=10^{11}\,\mathrm{s}\) 다음 단일 한계 행에서 중단. 각 source initial condition에서 elapsed proper clock 765행만 사용한다. 진행 중인 MINUS continuation output은 **읽지 않았고** solver process/RAM/lock을 건드리지 않음. 원본 데이터 물리 방정식을 변경하지 않음.

Read-only independent diagnostic:

\[
\tau_{\mathrm{cold}}(t)=c\,\sigma_T\int_{0}^t n_e(t')\,dt',
\quad \sigma_T=6.6524587051\times10^{-25}\,\mathrm{cm^2},
\quad c=2.99792458\times10^{10}\,\mathrm{cm\,s^{-1}}.
\]

\(\sigma_T\)는 현재 cold repository의 `rust/rei_microphysics/src/igm_thermal.rs`와 같다. `n_e\)는 원래 `history.csv`의 proper cm\(^{-3}\), 셀별 이온 charge closure \(n_e=n_H[x_{\rm HII}+\frac{Y}{4(1-Y)}(x_{\rm HeII}+2x_{\rm HeIII})]\)를 모든 소비 행에서 검증했으며 \(Y=0.2454\). 시간축은 **각 source 첫 순간부터 경과한 고유시간을 맞춘 것일 뿐, warm/AX08가 동일 cosmological epoch나 동일 microphysics 라는 뜻은 아님**.

Saved piecewise linear \(n_e(t)\), vectorized 16-boundary integral and independent scalar-Kahan reference PASS:

| source | \(\tau_{\mathrm T}(t=10^{11}\mathrm s)\) |
|---|---:|
| BASS_HE warm P01 certified midpoint | \(1.2799831091764300\times10^{-7}\) |
| AX08 ZERO cold | \(7.017871650713276\times10^{-10}\) |
| AX08 \(\pm0.005\) cold | \(7.017871649204325\times10^{-10}\) |
| AX08 \(\pm0.01\) cold | \(7.017871644677877\times10^{-10}\) |

Ratio \(\tau_{\rm BASS}/\tau_{\rm AX08,ZERO}=182.38907362\) at the **same elapsed time, different physical model**. This difference is a source/electron-background contrast, not a cosmological shear signal and not evidence for an observation. The tiny finite-q differences in AX08 on this short window are not scientifically resolved: saved-row stride-8 interpolation perturbation \(\approx1.12\times10^{-17}\), larger than the apparent \(\sim6.0\times10^{-19}\) q-even signal. That perturbation itself is a diagnostic, not a full ODE error bound.

All 16 warm source times paired with all five cold source cases in `results/ax08_cold_vs_p01_warm.csv`, full numeric/source identity in `results/ax08_cold_vs_p01_warm.json`, 2-D measured plots `warm_p01_vs_cold_ax08_tau.png` and `warm_p01_last_scatter_cells.png`.

## (C) 계산/자원 최적화와 부정적 병렬성 결과

- Cold per-source CSV reading is **prefix streaming and early stop**: 765 rows of the original 200001 accepted rows (~0.38%). No need to load full 5 histories or ongoing MINUS output.
- NumPy bulk integration with one searchsorted, cumulative integration and 16 endpoint interpolation yields **13–22x kernel speed** vs scalar Python compensated summation on the same saved physical values, with observed numerical agreement to within \(10^{-24}\) in \(\tau\) (binary64 summation). Benchmark includes only postprocessing, not source CPU or ODE.
- **Direct 24 warm repeats across all five already loaded cases:** 1-process serial med 0.000166665s, 2-thread med 0.000252889s, speedup 0.659x (parallel slower). Therefore choose **serial vectorized** for this tiny subtask; no nested threading or oversubscription. Source-coupled larger problems require fresh matched-error benchmarks, not a claimed parallel gain.
- Original warm per-cell source midpoint/whole process wall ~12.84s, assembly ~15.10s mean on its own BASS_HE run. This experiment did **not** re-execute those private source processes.

## 실제 검증과 수정 이력

Focused `python3 research/rei_p01_ax08_bridge_20261015/tests/test_bridge.py`: **15/15 PASS** with source bytes, clock and scientific claim invariants, 16 Poisson normalization and positive last-scatter enclosure, independent scalar-vs-vectorized cold actual data and negative tampering fixtures.

Initial 13 tests exposed three local test-assumption mistakes. Recorded and corrected rather than diluting physics targets: (i) early-prefix rows actually 765, not arbitrarily >1000; (ii) 28-digit default Decimal arithmetic can lose 90-digit cancellation accuracy when forming \(1-P_0\), so enforce 90-digit context in the test; (iii) two valid binary64 summation orders differ \(2.07\times10^{-25}\) in \(\tau\simeq7\times10^{-10}\), so the numerical reference tolerance was set to \(10^{-24}\), about \(1.4\times10^{-15}\) *relative*, while the physical scientific tolerance stays unaffected. All 15 real/negative tests then PASS.

Independent high-precision Wolfram exact rational \(R'_{\ge3}\) and 45-digit endpoint values match the local Decimal90 tail bounds. xAct not used here because no new tensor identity was required, and a Wolfram verification is not an independent numerical backend proof for earlier BASS_HE interval certificates.

## 문헌과 후속 DAG

- Friedrich et al. 2012, [C2-Ray H/He multifrequency and thermal timestep accuracy](https://arxiv.org/abs/1201.0602): temperature convergence can require smaller steps than abundance convergence. AX11 must gate Tgas separately.
- Pawlik & Schaye 2011, [TRAPHIC photon-conserving multifrequency thermal H/He transport](https://arxiv.org/abs/1008.1071): non-grey photoheating, normalization and spectral hardening.
- Fleury, Pitrou & Uzan 2015, [Bianchi I null light propagation](https://arxiv.org/abs/1410.8473): exact ray/redshift geometry in its own assumptions.
- [BASS_HE PR64](https://github.com/cosmosapjw-quantum/BASS_HE/pull/64): all16 saved-source warm P01 optical-depth certificates, original per-photon error components private.
- [bass_cr PR71](https://github.com/cosmosapjw-quantum/bass_cr/pull/71): source-conditioned bounded q/adaptive bins require true child photon moments, not derivable from pooled N,U alone.
- [rec_bianchi PR89](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/89): Bianchi I phase-volume number/Jacobian verification with explicit convention conversion.

**DAG status:** BASS_HE P01 all16 SOURCE_SCOPED_COMPLETE. This parallel REI-P01 bridge is IMPLEMENTED_TESTED_SOURCE_BOUNDED and does not change old owner acceptance. AX08 signed MINUS running at source readback, with independent final owner/observer release/scheduling; no second solver launch here. On natural MINUS terminal, original+continuation composition only after real RETURN/state/source identity, then half-minus allocation, plus interruption recovery. AX11 time/energy/angular source convergence and independent Tgas/ions errors remain necessary for BBN-style full reionization history scientific admission.
