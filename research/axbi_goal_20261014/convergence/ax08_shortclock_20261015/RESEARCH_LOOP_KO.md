# AX08 짧은 고유시간 증분·signed shear 검증 및 H/He 재이온화 후속 연구

2026-10-15 KST. 기준 Git commit `7ac15b6078666d61c023103f79bfd47a033de41f` ([rei_bianchi PR125](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/125)). 다른 작업의 실제 code/결과와 연결하면서 **원본 사용자-owned 실행 checkout은 source/config/checkpoint를 변경하지 않았다**. 분석은 격리된 worktree `research/ax08-shortclock-20261015`에서 CPU2/3만 사용. Local Codex NOT_USED, native subagent NOT_RUN (host에 spawn/delegate tool 없음). 과학 모델: non-tilted LRS Bianchi I, metric \((-+++)\), density-fixed \(H=\sqrt{H_\mathrm{FLRW}^2+s^2}\), signed \(q_\mathrm{ref}=0,\pm0.005,\pm0.01\), \(s=q_\mathrm{ref} H_\mathrm{FLRW}(a_\mathrm{ref})(a_\mathrm{ref}/a)^3\), original MD14/BB50K H/He cold/Case-A source, \(a_\mathrm{ref}=1/21\), \(a_\mathrm{end}=1/5\). 다른 source/epoch를 동일시하지 않는다.

## 새로운 근거: 실제 모든 저장 state의 clock error

[AX03 C8 PR123](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/123) head SHA `602f9726858b8a183c259ac7eae9fc11d1d7fb99`에서 다음 파일을 **원본 바이트와 동일하게** 채택했다:
`vendor/rei_axbi_shortstep_20261015/shortstep.py`,
`vendor/bass_20261015/axbi_provider.py`,
`vendor/bass_20261015/source/REI_BACKGROUND_FAMILY_LOCK.json`.
마지막 lock SHA `46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0` 확인. 이는 standalone source-gradient clock 공급자이며 원래 science ODE를 수정하지 않았다.

**현재 원래 저장소의 실제 입력:** completed ZERO, SHEAR_HALF_PLUS, SHEAR_MINUS 각 312,238 accepted time states; original partial SHEAR_HALF_PLUS 및 SHEAR_HALF_MINUS 각 200,001 states. `history.csv` 전체 SHA256은 `COMPOSITION_RECEIPT.json` 또는 original frozen source/typed accepted=200000 terminal과 일치. 총 1,336,716 소비 saved rows (같은 source epoch의 plus 원본 prefix는 complete plus에도 포함돼 있지만 독립적인 identity/prefix 검사 목적이며 독립된 측정으로 중복 계수하지 않는다).

두 실제 binary64 mean-scale endpoints \(a_i<a_{i+1}\)의
\[
\Delta x_i=\log\!\left(1+\frac{a_{i+1}-a_i}{a_i}\right),\qquad
\Delta t_i=\int_{x_i}^{x_{i+1}}\frac{dx}{H(a(x))},\quad
\Delta b_i=\int_{x_i}^{x_{i+1}}\frac{s(a(x))}{H(a(x))}\,dx .
\]
GL4와 GL8의 독립 local source integral은 모든 sampled actual intervals에서 최대 relative dt difference \(7.470\times10^{-16}\) 이내. `np.diff(saved proper time)`와 **source-frozen GL4**의 최대 상대 차이는 \(5.63886684\times10^{-7}\), 원래 accepted row index 15→16에서 발생했다. 99th percentile은 \(\sim6\times10^{-10}\), median \(\sim9.9\times10^{-11}\)이다. 이 차이는 *국소 저장 timestamp의 수치 오차*이지 전체 H/He ODE solver의 AX11 error certificate가 아니다. Source independent DOP853의 전체 누적 t(a)와 frozen saved background 차이는 최대 \(2.67\times10^5\) s, 하지만 \(t\sim4.28\times10^{16}\) s의 절대 clock 비교이며 **동일 물리모형에서의 엄밀 오차 상계가 아니다**.

관측된 실제 주범의 정량 예:
\[
a_{15}=0.04761904789152601,\qquad
a_{16}=0.04761904790969124 .
\]
기존 ZERO \(\Delta t_\mathrm{saved}=3223208.118472241\) s, independent exact-source GL4 \(\Delta t_\mathrm{GL4}=3223206.3009491283\) s, 차이 \(+1.8175231125\) s. 원래 legacy \(\log(a_i/a_\mathrm{ref})\) 차분은 국소 \(\log1p((a_{i+1}-a_i)/a_i)\)에 비해 상대 오차를 유발한다. 이 로그 차이에 \(1/H(a_{\mathrm{mid}})\)를 곱한 독립 예측 오차 \(1.81752309138\) s와의 차이는 \(2.11\times10^{-8}\) s이다. 따라서 이 특정 witness의 오차는 사실상 **서로 거의 같은 로그값을 빼는 cancellation**으로 재현된다. 다만 이를 전체 저장 이력이나 전체 coupled solver의 유일한 오차 원인이라고 일반화하지 않는다.

원본 \(\pm0.005\) **두 200,001-step accepted prefixes의 same-a timestep과 \(b\)**는 보관된 binary64 배경에서 **bitwise** \(t_+(a)=t_-(a)\), \(b_+(a)=-b_-(a)\)로 정확히 일치했다. 독립 GL4 역시 \(\Delta t(q)=\Delta t(-q)\), \(\Delta b(q)=-\Delta b(-q)\) exact numeric symmetry를 확인했다. 이 사실은 source parity를 검증하지만, 실제 scalar ionization/thermal rates가 정확히 q-even이라는 증명은 아니다.

새 native std-only Rust helper `clock_increment_gl4.rs`는 원본 scientific input을 건드리지 않고 source H(a),s(a)와 `ln_1p`를 사용한 positive local \((\Delta t,\Delta b)\) 계산기를 구현했다. `rust/rei_microphysics/tests/axbi_clock_increment_gl4.rs`: **4/4 PASS**, 실제 AX08 witness와 원래 `AxbiBackground::point_at_scale` 둘을 함께 검사하여 오차 확인, signed q parity, nextfloat interval dt 양수, 불법 source/clock 거부. 이 helper는 **opt-in 후속 solver callsite 개선 후보**일 뿐 현재 runtime binary에 merge/연결하지 않았다.

## 수치 최적화, 병렬 실행 비교

실제 SHEAR_MINUS source-locked 완료 이력에서 8,007개 국소 간격을 뽑아, 같은 Gauss4 물리 적분을 독립 Python scalar vs NumPy grouped vector vs 2-thread 진행:
- Scalar median \(0.356205\) s.
- Vector single worker median \(0.00248641\) s (**143.26×** scalar 대비).
- Vector two workers median \(0.00217911\) s (**1.141×** single grouped 대비).
- 같은 수치값의 상대 차이 \(\Delta t\le2.55\times10^{-16}\), \(\Delta b\le2.23\times10^{-16}\); 5회 동일 하드웨어 측정, CPU2/3 및 BLAS single thread. Total wall includes test/plot/source load and is not identical to this hot-kernel timing.

이는 **clock source subproblem** 성능일 뿐 AX08 전체 coupled chemistry/photoionization/RT ODE solver에 대한 속도 향상, 시간 적분 수렴성 또는 물리 모델 변경이 아니다.

## Wolfram 이론 검산: signed q perturbative clock

\(F(a)=H_\mathrm{FLRW}(a)\), \(\lambda(a)=H_\mathrm{FLRW}(a_\mathrm{ref})(a_\mathrm{ref}/a)^3/F(a)\)일 때
\[
\frac{1}{H(a,q)}=\frac{1}{F(a)}\Big[1-\tfrac12 q^2\lambda^2+
\tfrac38q^4\lambda^4-\tfrac5{16}q^6\lambda^6+\cdots\Big],
\]
\[
\frac{db}{d\ln a}=\frac{q\lambda}{\sqrt{1+q^2\lambda^2}}
=q\lambda-\tfrac12q^3\lambda^3+\tfrac38q^5\lambda^5
-\tfrac5{16}q^7\lambda^7+\cdots .
\]
Wolfram exact-q symbolic identity: 1/H exact q-even, db/dx exact q-odd, rational coefficients PASS. Actual frozen physical source integrals Gauss16 versus Gauss32 agree numerically in `results/perturbative_clock.json`. Alternating-series remainder inequality for \(0\le q^2\lambda^2\le10^{-4}\) is analytic; its **numerically integrated coefficient** remains a quadrature estimate, not a rigorously rounded interval.

At \(a=0.2\):
- q=+.005: actual saved FLRW clock shift \(-62,259,465,536\) s; q-Taylor6 source prediction differs **48.09336 s**, relative \(7.7247\times10^{-10}\). Analytic remainder integral estimate for true Taylor truncation \(\approx8.612\times10^{-5}\) s.
- q=-.01: actual saved FLRW clock shift \(-249,032,580,232\) s; q-Taylor6 source prediction differs **28.87238 s**, relative \(1.1594\times10^{-10}\). Analytic remainder integral estimate \(\approx0.0220471\) s.
- Thus measured difference includes finite precision and independent saved-clock errors beyond analytic Taylor truncation. This compares geometry clocks only; no unearned full AX11/chemical error claim.

## 다른 연구 결과 적용 범위

- [AX03 PR123](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/123): source-locked short proper-step, GL4 Hermite, exact source files reused; **actual original AX08 saved accepted steps** independently tested above.
- [SOURCE07 PR124](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/124): H/HeII age-conditioned spectral threshold compression; cold BB50K 36→11 with finite frozen-gas state holdout error \(\le1.71\times10^{-11}\), alternative spectrum changes error substantially. Not inserted into this frozen AX08 photon/chemistry source; current stellar-like BB50K source still separate.
- [BASS_HE PR64](https://github.com/cosmosapjw-quantum/BASS_HE/pull/64): completed 16-cell *warm* P01 source-scoped tau; cannot act as observational EoR optical depth or cold source.
- [Fleury, Pitrou & Uzan (2015)](https://doi.org/10.1103/PhysRevD.91.043511) Bianchi I conserved spatial Killing momenta/energy/redshift, independent primary geometry.
- [Friedrich et al. (2012)](https://arxiv.org/abs/1201.0602) C2-Ray multifrequency helium and stricter thermal step requirements. Therefore real temperature and electron rate error must have its own matched AX11 experiment.

## 실시간 과학 결과와 다음 DAG

The already-authorized ONE `SHEAR_HALF_MINUS` continuation (binding `315986f63370fc20bcd20ee3d45da398d4c9274b53c329dbf4d1850e760d1aa4`, no automatic retries) naturally reached exit0/Ok(()), cumulative accepted312237, \(a=0.2\) at 2026-10-15 15:40 KST. Its `RETURN.txt` SHA `513a4338a00a4b421aea2a000d0d7b5ddbedf72c5542f8078ab37a000e41385c`. The original, now-completed independent composer was launched with the exact RETURN SHA and the original frozen `EXECUTION.binding` to `SHEAR_HALF_MINUS_composed_001`. The composer and science data remain on original local Ubuntu; source and raw/dynamic outputs are NOT uploaded in this research branch. This source scope is distinct from the warm BASS_HE lane.

**Full signed parity** requires the actual composer terminal `COMPOSITION_RECEIPT.json` status, SHA, boundary row counts, and full H/He/electron ledger; only once present run the prepared `halfminus_full_parity.py` for four completed ZERO,+.005,-.005,-.01 cases. This is finite-grid exploratory measurement, not matched AX11 numerical truncation and not scientific admission. PLUS case requires separate typed runtime-classifier recovery. Until that and matched \(\Delta t,\Delta E,\Delta\mu\) error floor, true five-case full signed detection is NOT_ISSUED.


## 실제 HALF_MINUS terminal composition 및 네 사례 과학 분석 완료

2026-10-15 15:40 KST, HALF_MINUS actual `RETURN.txt` `status=COMPLETE_SEGMENT_TO_SELECTED_ENDPOINT`, `result=Ok(())`, \(a=0.2\), cumulative accepted312237, launcher `TERMINAL_RECEIPT.json` exit0 / stop_reason null, SHA256 `513a4338a00a4b421aea2a000d0d7b5ddbedf72c5542f8078ab37a000e41385c`. 기존 freeze된 private `EXECUTION.binding` SHA256 `315986f63370fc20bcd20ee3d45da398d4c9274b53c329dbf4d1850e760d1aa4`와 RETURN digest만 입력받는 *기존 immutable* `compose_signed_history.py`를 CPU2로 **실제 실행 exit0, 156.04 s**, 생성된 원본+segment 결합 `SHEAR_HALF_MINUS_composed_001` 약 1.8GiB를 소유자 원본 Ubuntu에 안전하게 보존했다.

직접 실제 수량:
- history312238, abundances1873428, ledgers8430426, feedback312238, spectra2040752.
- Shared first segment boundary exactly one discard per role, source identity and accepted/attempt/RHS/checkpoint exact verification, final `COMPOSITION_RECEIPT.json` status `COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION`. 원본 raw, private frozen bindings and production code untouched.
- New read-only `halfminus_full_parity.py` confirmed source-hash-bound real FOUR cases ZERO,+.005,-.005,-.01 each 312238 history rows; all four at \(a=0.2\). Full 1,873,428 rows of HALF_MINUS H/He/electron abundance charge/baryon/H/He ledger passed using proven PR119/PR122 Python implementation (full 6-species), and separate scoped std-only Rust streamer PASS **1.3993s, peak RSS4060KiB**, max normalized electron-charge discrepancy \(\sim2.4045\times10^{-16}\).
- \(q=\pm0.005\) complete cases' **all 312238 saved binary64 rows**, not just common samples: \(a_+(t)=a_-(t)\) exact, \(t_+(a)=t_-(a)\) exact, \(b_+(a)=-b_-(a)\) exact. This is background-only symmetry; no ion-rate parity assumption.

### 실제 full ±.005 even/odd 분해

공통 4097 \(\ln a\) samples에서 \(E_X=(X_{+.005}+X_{-.005})/2-X_0\), \(O_X=(X_{+.005}-X_{-.005})/2\). Max norm quantities:

| Source observable | max \(|E_X|\) | max \(|O_X|\) |
|---|---:|---:|
| \(x_{\mathrm{HII}}\) | \(6.1679700103\times10^{-7}\) | \(2.4980018054\times10^{-15}\) |
| \(x_{\mathrm{HeII}}\) | \(5.7523951003\times10^{-7}\) | \(1.4543921623\times10^{-14}\) |
| \(x_{\mathrm{HeIII}}\) | \(6.4057330464\times10^{-9}\) | \(6.4011296264\times10^{-16}\) |
| \(T_\mathrm{gas}\) K | 0.00664466772514 | \(1.6298145056\times10^{-9}\) |
| \(J_2\) eV/H | \(6.1580089037\times10^{-7}\) | 0.00594995421902 |

스칼라 even 우세, 광자 quadrupole signed odd 우세가 수치적으로 확인된다. No numerical AX11 error floor yet, thus tiny scalar odd terms are not physical detections. The magnitude is **finite historical full output** of the one frozen conditional source, not an observation.

실제 full species endpoints (\(\bar z=4\)): \(x_{\rm HII}(q=-.005)=0.999997317098235\), \(x_{\rm HeII}=0.9742081031950096\), \(x_{\rm HeIII}=0.025784315615955587\), \(T_{\rm gas}=7900.623351185612\) K. Source q=+.005 uses the same mean-geometry time, but the thermal end difference is \(\sim3.26\times10^{-9}\) K. All 4 actual cases plotted with 5 elemental ionic fractions \(x_{\rm HI},x_{\rm HII},x_{\rm HeI},x_{\rm HeII},x_{\rm HeIII}\) against both actual **elapsed proper time and chronological saved \(T_{\rm gas}\)** (T need not be monotonic); `results/full_halfminus_parity_002/four_HHe_BBNstyle_time_temperature.png`. Additional real 2-D signed-parity and 4-case time curves in same directory. These are BBN-*style* diagnostic presentations of conditional EoR 4-case histories, not a completed five-case source-calibrated EoR observational study.

Validation: `test_full_parity.py` **6/6 PASS**, independent `test_actual_clock.py` 8/8 PASS, new source-locked native `axbi_clock_increment_gl4` 4/4 PASS. No native subagent/other model independent review, no local Codex or new solver starts this turn. Total scientific admission remains `NOT_ISSUED`; still need PLUS actual runtime incident recovery, fifth full scenario, AX11 \(dt/dE/d\mu\) and source/photoheat/thermal convergence checks, AX12 variants and observer optical-depth tail. Preserve original current + halfminus published source-identical results and their SHA registry.


### 핵심 재현 실행 명령

다음 명령은 변경하지 않은 원본 Ubuntu checkout의 실제 science CSV와 공개 source lock을 **읽기만** 하며, 이 대화에서 만든 독립 작업트리의 코드를 실행한다. 기존 결과 폴더가 있으면 새로운 `--output` 폴더명을 지정한다.

```bash
R="$HOME/Dropbox/bianchi/rei_bianchi"
D=research/axbi_goal_20261014/convergence/ax08_shortclock_20261015
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1

taskset -c 2 python3 "$D/actual_clock_gl4.py" --owner-root "$R" --stride 1     --output "$D/results/actual_clock_allrows_fresh.json"
taskset -c 2,3 python3 "$D/benchmark_clock.py" --owner-root "$R"
taskset -c 2 python3 "$D/perturbative_clock.py" --owner-root "$R"
taskset -c 2 python3 "$D/halfminus_full_parity.py" --owner-root "$R"     --output "$D/results/full_halfminus_parity_fresh"
taskset -c 2 python3 "$D/test_actual_clock.py"
taskset -c 2 python3 "$D/test_full_parity.py"

CARGO_TARGET_DIR="$PWD/.ax08_clock_target" CARGO_BUILD_JOBS=2  taskset -c 2,3 cargo test --locked --offline  --manifest-path rust/rei_microphysics/Cargo.toml  --test axbi_clock_increment_gl4 -- --nocapture
```

SOURCE07, BASS_HE와 현재 cold-IGM 조건을 동일 물리 source라고 가정하지 않는다. `results/RESULT_STATUS.json`, `SOURCE_MANIFEST.json`, 실제 PNG, source-dependent JSON은 공용 provenance를 위해 이 브랜치에 공개되지만 원래 1.8GiB science CSV와 private signed execution binding은 절대 복제·게시하지 않는다.
