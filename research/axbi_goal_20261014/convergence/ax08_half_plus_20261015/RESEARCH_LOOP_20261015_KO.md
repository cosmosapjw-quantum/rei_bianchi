# AX08 직접 이론·코딩 연구 루프, 2026-10-15 KST

## 기준, 물리적 scope, 실행 소유권

원래 frozen `rei_bianchi` AX07/AX08 source/binary/config/physical rates/Case-A/numerical solver/저장 데이터는 불변이다. 별도 local Codex를 호출하지 않고 ChatGPT에서 Desktop Commander를 통하여 Ubuntu 파일·코드·테스트·실제 읽기 계산을 수행했다. 이번 환경에는 native subagent dispatch 도구가 없어 `native_subagent=NOT_RUN`이다. 2-thread Rust 및 NumPy 병렬 프로세싱은 subagent라고 부르지 않는다.

`SHEAR_HALF_PLUS`의 완료된 +0.005 continuation은 앞선 루프에 실측으로 존재한다. `SHEAR_HALF_PLUS_composed_002` full interval은 312,238 states (a=1/21→.2), source-epoch relation은 `REVIEWED_RESOURCE_ONLY`, ledger+census 검증 범위는 이미 별도로 기록됨.

## 새 MINUS 1회 continuation launcher

새 `driver/full/minus_continuation_001/launch_001/launcher.py` / `test_launcher.py`는 기존 frozen private binding, binary, execution authority, independent binding review SHA를 직접 검증한다. 최초 PLUS observer가 `RUNTIME_CLASSIFIER_FALSE_POSITIVE_SOLVER_ABORTED`로 종료된 이력, HALF_PLUS 실제 return exit0/accepted312237/endpoint a=.2, completed-history 312238 rows를 분리하여 검사한다. 아울러 원래 학습 문제였던 `rg`의 파일 경로가 argv에 포함되는 false-positive를 방지하기 위해 **실제 실행 파일 위치**만 science 프로세스로 구분하고, scheduler Python ownership은 이 repo의 AXBI driver 위치로 국한한다. 현재 local preflight PASS, synthetic/real read-only regression 4/4 PASS. CPU0 가용, 당시 memory available 약20 GiB, disk 약276 GiB, local scientific process와 owner 각각 0.

`--launch`에는 신규 독립 launcher changed-surface review와 단 한 번의 fresh controller RELEASE (remote/pending science slot, exact SHA, 최근 관측 시간, 중복 예약 없음)가 필요하다. **이 단계에서는 launch를 호출하지 않았고 새 solver start=0**이다. PASS_PRELAUNCH와 scientific admission은 별개이며 frozen `launch_now=false`도 조용히 무시하지 않았다.

## 구성적 물리 유도와 실제 독립 검사

Axial metric과 자유 shear 정의는

\[
ds^2=-c^2dt^2+a^2 e^{-2b}(dx^2+dy^2)+a^2 e^{4b}dz^2,
\qquad s=\dot b.
\]

처음 등방적인, 충돌 없는 유효 질량 없는 복사장은 현재 국소 방향 \(\mu\)에 대해

\[
T(\mu,a)=\frac{T_0}{a}
\left[(1-\mu^2)e^{-2b}+\mu^2e^{4b}\right]^{-1/2},
\qquad
\rho_{r,\mathrm{iso}}(a)=\frac{3H_0^2c^2\Omega_r}{8\pi G a^4}.
\]

국소 physical-angle 사중극자를 적분하면

\[
\frac{\Delta P_r}{\rho_{r,\mathrm{iso}}}
=\frac12\int_{-1}^{1}
\frac{P_2(\mu)\,d\mu}
{\left[(1-\mu^2)e^{-2b}+\mu^2e^{4b}\right]^2}
=-\frac85b+\frac87b^2-\frac{16}{35}b^3+O(b^4).
\]

Wolfram CAS가 integrand를 \(b=0\)에서 미분한 뒤 각도 적분하여 얻은 정확 계수는 \(\{0,-8/5,16/7,-96/35\}\)이다. 적분 closed form 자체를 \(b=0\)에 치환하면 발생한 removable singularity `Indeterminate`를 실제로 확인했고, 올바른 극한 절차로 교정했다.

생산 코드 `axbi_background::isotropic_initial_radiation_moments`는 initial reference angle에서 composite Simpson 4096 panels를 사용한다. **독립적 좌표 표현**의 새 `verify_radiation_quadrupole.py`는 128-point GL current-local direction에서 처음부터 별도로 적분했고, 저장된 312238 states 각각과 비교했다. 두 source/output SHA를 확인하고 all-row proper clock/scale parity를 검사한 후, \(\max|\Delta P_\mathrm{saved}-\Delta P_\mathrm{GL128}|/\rho_{r,\mathrm{iso}}=2.2985916265\times10^{-15}\)을 얻었다. 저장 endpoint \(-2.0745128731978643\times10^{-13}\) J m\(^{-3}\), GL128 \(-2.0745128731980774\times10^{-13}\) J m\(^{-3}\). ZERO FLRW control은 0. Prescribed effective-radiation stress에는 PASS_SCOPED, backreaction-coupled 진화·full atomic accuracy에는 NOT_ISSUED.

## Original five-case 공통 signed prefix

`signed_prefix_parity.py`는 original five-case each 200001 accepted histories, \(20\ge\bar z\ge10.2693\)를 공통 \(\ln a\) 501점에서 표본화한다. CSV field identity를 header로 검증한다. 각도 모멘트 실수 판별에서 처음 잘못 지정했던 `usecols`를 `(4,9,14,22)`로 고쳐 정확 `(a,x_HII,temperature_K,J2_photon_u_eV_per_H)`를 재실행했다.

\[
O_{\rm even}(q)=\frac{O(+q)+O(-q)}2-O(0),
\qquad
O_{\rm odd}(q)=\frac{O(+q)-O(-q)}2.
\]

| Absolute sampled diagnostic | \(q=.01\) | \(q=.005\) | Consistency only |
|---|---:|---:|---|
| \(x_{\rm HII}\) even | 1.2567578674e-6 | 3.1419528070e-7 | leading \(q^2\) |
| \(T_{\rm gas}\) even [K] | 0.02657831773 | 0.00664466088 | leading \(q^2\) |
| \(J_2\) odd [eV/H] | 2.6671711971e-12 | 1.3335886533e-12 | leading \(q\) |

이를 완전한 q→-q symmetry나 수치검출이라고 주장하지 않는다. scalar monopole 1차 \(q\) 항은 isotropic emissivity, normalized symmetric angle quadrature, tracefree shear 가정 아래 \(\int_{-1}^{1}P_2(\mu)d\mu=0\)으로 제거되며 \(J_2\) 사중극자는 1차 항을 허용한다. 실제 empirical error, interpolation error, source-model error를 아직 분리하지 못했다. Stored `signed_prefix_parity.json`; visualization `signed_prefix_even_odd.png`.

## 실제 로컬 Rust/NumPy 최적화

새 `feedback_fast.rs`: 두 실제 `feedback.csv`, each 312238 accepted states를 buffer-streaming `BufRead`로 읽으면서 Kahan pressure integral과 full delta-s 진단을 한다. 두 파일은 독립적이므로 `std::thread::scope`를 써서 data-level parallelism 2개, per-file constant memory \(O(1)\). UTC/PID magic 또는 solver-state mutation 없음. Exact case name, size, physical pressure ledger, monotone proper time and a, dimension/finite controls, and numerical parity with previously saved Python compensated reference checked.

새 `feedback_numpy.py`: exact input SHA 확인, NumPy `loadtxt` vectorized and optional ThreadPool (2 streams), independent same-data parity. Library NumPy=2.4.2; installed system numexpr/bottleneck ABI incompatibility 때문에 pandas optional dependency를 사용하지 않는다.

3 warm process measurements (whole process median, identical two stored files):
- Python reference: 4.242715562 s.
- Rust sequential: 0.264627584 s.
- Rust 2-thread: 0.151321890 s.
- **Rust parallel / Python wall-speedup: 28.0377×**, Rust parallel / sequential 1.74877×.
- 1 별도 GNU `time -v` 관측 peak RSS: Rust parallel 3816 KiB, Rust sequential 3428 KiB, NumPy parallel 88692 KiB, Python reference 17572 KiB. NumPy real parallel check wall1.68s and scientific parity PASS; 3회 median으로 측정하지 않았다.
- Performance numbers are saved-data postprocessing only, **NOT** the AX08 integration solver speedup.
- Actual raw timing files `raw/{rust_parallel,rust_serial,numpy_parallel,python_reference}.time` and measured `feedback_benchmark.json` are preserved. `quadrupole_crosscheck.json` and `signed_prefix_parity.json` are experimental physical evidence.

Compilation/replay from original repo root:

```bash
rustc -O -C target-cpu=native --edition=2021 research/axbi_goal_20261014/convergence/ax08_half_plus_20261015/feedback_fast.rs -o /tmp/rei_ax08_feedback_fast_20261015
/tmp/rei_ax08_feedback_fast_20261015 "$PWD"
python3 research/axbi_goal_20261014/convergence/ax08_half_plus_20261015/benchmark_feedback.py
python3 research/axbi_goal_20261014/convergence/ax08_half_plus_20261015/verify_radiation_quadrupole.py
python3 research/axbi_goal_20261014/convergence/ax08_half_plus_20261015/signed_prefix_parity.py
python3 research/axbi_goal_20261014/driver/full/minus_continuation_001/launch_001/test_launcher.py
```

## Cross-repo read-only intake, 2026-10-15

- `bass_cr` [PR70](https://github.com/cosmosapjw-quantum/bass_cr/pull/70) head `6898f3dd0ab5acff066fb0239339ec44c8d70398`: shape-free photo-event H/He moment error envelopes. Later source07 age-closure bridge candidate; no error number adopted for production AX08.
- `bass` [PR154](https://github.com/cosmosapjw-quantum/bass/pull/154) head `6812bac3148afa292189f0bdec3e5994a5b892b0`: polarized real-ray quadrature, not active scalar cold-model replacement.
- `BASS_HE` [PR62](https://github.com/cosmosapjw-quantum/BASS_HE/pull/62) head `490ac4a980b582d983f15975dc813ef5457efa02`: warm P01 source-cell certification. Different thermal source/epoch from cold AX08.
- `WU088_HH` [PR77](https://github.com/cosmosapjw-quantum/WU088_HH/pull/77) head `dda5057a3a1af2b97465006163df0c7c3443c6b9`: cusp-shell radial certificate; not directly transportable to HI/He opacity.
- `rec_bianchi` [PR90](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/90) head `99dbd883042bb60734f92cd424f2f91826d1ea48`: HyRec-2/RECFAST matched validation; no implicit replacement of original declared AX08 z=20 approximate gas IC.

SOURCE07 C7 already physically measured ~\(-0.0044125483\) relative HI absorption bias when two separated emission epochs are merged into one N/U fixed-q bin at nE=256. This is a specific **experimental alternate spectral closure**, not a measured physical error of the existing AX08 production physical-energy integration. Respect this distinction when transferring BASS_CR cohorts or SOURCE07 compression.

## Stop condition / next exact action

This loop has no new AX08 science solver start. The original MINUS one-start binding remains unused. Next authorized step requires a fresh independent review of `minus_continuation_001/launch_001/launcher.py` and fixture, followed by current NCP/pending slot/owner readback, one controller release and **exactly one** signed MINUS execution using already frozen original binding, no automatic restart. HALF_MINUS may follow only after actual MINUS classification. PLUS runtime abort recovery needs separate typed authority. AX11 and AX12 downstream scientific admission remains pending full signed-family history and relevant convergence.
