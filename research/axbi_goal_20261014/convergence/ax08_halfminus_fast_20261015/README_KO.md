# AX08 HALF_MINUS 실제 시작과 source-free 복사 모멘트 고속 정확도 검증

2026-10-15 (KST). `physmath-research-loop` 이론·코딩 후속 루프. 원래 사용자 목표는 non-tilted axisymmetric Bianchi I에서 H/He 재이온화 이력과 BBN식 비율 도표를 계산하는 것이다. 새로운 `SHEAR_HALF_MINUS`의 signed 전체 이력 확보와 AX11 수렴성은 해당 목표의 필수 선행 연구다. 이 루프는 오리지널 AX07/AX08 cold MD14+50kK blackbody 조건부 source/Case-A/초기조건/compiled binary를 변경하지 않고 실행되었다.

## 1. 정확한 signed continuation 단 한 번 실행

기존 independent exact science binding review `research/axbi_goal_20261014/driver/full/signed_minus_bindings_review_001/INDEPENDENT_REVIEW.json`: decision `PASS_SCOPED_EXACT_BINDINGS_CONDITIONAL_LAUNCH`, `SHEAR_HALF_MINUS=PASS`; original frozen private binding SHA256 `315986f63370fc20bcd20ee3d45da398d4c9274b53c329dbf4d1850e760d1aa4`. 실제 사용 binary `4243c744af3f3237ad0ca570b14fad8db4344f33be8fc29d8da9cfda8e811c74`. 모든 원래 input SHA가 그대로인지 읽어 검사. 이전 PLUS 중단은 typed `RUNTIME_CLASSIFIER_FALSE_POSITIVE_SOLVER_ABORTED`, HALF_PLUS/MINUS는 각각 자연 종료 및 `COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION`로 판정되어 스케줄러 순서 충족.

새 `launch_001`의 `derive_launcher.py`는 직전 MINUS에서 검증·사용된 single-start launcher를 HALF_MINUS 소유권/경로/SHA/원래 권한에 맞게 기계적으로 변환한다. 출처 계약 `LAUNCH_CONTRACT.json` + `launcher.py` + `controller_release.py`는 다음을 집행한다: 기존 independent scientific binding PASS, previous MINUS terminal digest 및 composition receipt, 중복 출력/예약 거부, 로컬/NCP 실제 worker 확인과 이전 reservation terminal 정리, 단일 CPU0 science, 물리 binary의 hash, wall 10800s, 합계 output 4096 MiB, RSS 2 GiB, 자동 재시도 0. 신규 CPU/physics/solver 구성은 추가하지 않는다.

독립된 *검사 방식*인 AST/hash checker는 `PASS_SCOPED_INDEPENDENT_IMPLEMENTATION_CONTROL`, 사전 로컬 regression `4/4 PASS`를 보였다. 별도 모델·native subagent의 새 심사가 이루어졌다는 뜻은 아니다 (`native_subagent: NOT_RUN`). Actual single fresh controller RELEASE `FRESH_CONTROLLER_RELEASE_ONE_START`, Popen ACK `RELEASED_AND_LAUNCHER_DETACHED`, observed science process PID1433670, wrapper pid1433663, launcher PID1433655, CPU0, full observed cumulative science starts10, history starts13. Runtime files are kept privately in the user's original live checkout; `ACTUAL_LAUNCH_PUBLIC.json` only exposes the scoped SHA-bound audit facts. After launch `launcher.py --preflight` fails closed with `DUPLICATE_OUTPUT_OR_RAW`, as expected. No attempts to restart.

초기 실제 구동증거: source `checkpoint.txt`와 `history.csv`가 생성되고 accepted counter는 원래 200000보다 증가. 종료 `RETURN`은 관찰 시점 아직 없음. 최초 accepted200000의 source checkpoint는 intact하고 끝까지의 도달은 future terminal verification을 기다린다. Full H/He or BBN-like plot completion not claimed.

## 2. 분석적으로 도출된 비등방성 복사 에너지·사중극자 함수

계량(-,+,+,+):
\[
ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2 .
\]
초기 방향 \(\mu_0\)에서 자유전파 massless radiation의 \(S=(1-\mu_0^2)e^{2\Delta b}+\mu_0^2e^{-4\Delta b}\), \(\Delta b=b-b_{\rm ref}\). \(\mu_{\rm local}^2=\mu_0^2e^{-4\Delta b}/S\). 이때 source-free 초기 등방 복사의 정규화 모멘트
\[
M_0=\int_0^1\sqrt{S}\,d\mu_0,\qquad
M_2=\int_0^1\sqrt{S}\,P_2(\mu_{\rm local})\,d\mu_0.
\]
\(\rho_{\mathrm r}=\rho_{\mathrm{iso}} M_0\), \(\Delta P_{\mathrm r}=\rho_{\mathrm{iso}} M_2\), \(\rho_{\mathrm{iso}}=\rho_{\mathrm{ref}}(a_{\rm ref}/a)^4\).

\(\delta=e^{-6\Delta b}-1\)로 쓰면
\[
M_0=e^{\Delta b}\sum_{n\ge0}\binom{1/2}{n}\frac{\delta^n}{2n+1},\qquad
M_2=\frac{e^{\Delta b}}2
\left[3e^{-6\Delta b}\sum_{n\ge0}\binom{-1/2}{n}\frac{\delta^n}{2n+3}
-\sum_{n\ge0}\binom{1/2}{n}\frac{\delta^n}{2n+1}\right].
\]
Wolfram에서 이 두 식의 **0차부터 14차까지의 모든 정확 유리수 계수**를 얻어 검산했다. 따라서 고속 후보는
\(M_0-1=(\Delta b)^2\operatorname{Horner}_{2:14}(\Delta b)\),
\(M_2=\Delta b\operatorname{Horner}_{1:14}(\Delta b)\)로 계산한다. \(\Delta b\to0\)에서도 energy correction의 \(1-1\) cancellation을 유발하지 않는다.

**분석적인 절단 오차 상계.** 복소 \(z\)에서 \(|z|=R=0.4\), \(\exp(-6z)\)의 회전각은 \(|\arg|\le6R<\pi\)이며
\[
|(1-\mu^2)+\mu^2e^{-6z}|
\ge \cos(3R)e^{-6R}>0.
\]
따라서 해당 원판에서 일관된 square-root analytic branch가 존재한다. \(|M_0|\le e^{4R}\),
\[
|M_2|\le \frac{e^R}{2}\left[\frac{e^{9R}}{\sqrt{\cos(3R)}}+e^{3R}\right].
\]
Cauchy geometric bound로 \(|\Delta b|\le0.025\), \(\eta=0.025/R=1/16\)이면 14차 절단 나머지는 위 각 경계의 \(M\eta^{15}/(1-\eta)\) 이하. Rust에서
\[
|R_{0,14}|<6\times10^{-18},\qquad
|R_{2,14}|<5\times10^{-17}
\]
의 **순수 분석적 truncation bound**를 검증했다. 이는 finite-precision arithmetic, source/absorption, chemistry, Einstein dynamics, observation/AX11 continuum error를 포함하지 않는다. 제한을 벗어난 \(|\Delta b|>0.025\)에서는 새 함수가 결과를 반환하지 않고 원래 높은 분해능 계산으로 fallback해야 한다.

## 3. 실제 Ubuntu 로컬 구현·실행 및 성능

신규 C5/C6/C8 구현: `fast_moments.rs` (독립 O(1) 14차 Horner 함수와 Cauchy bound), `rust/rei_microphysics/tests/axbi_fast_small_shear_candidate.rs` (실제 production 4096-panel Simpson과 match, FLRW, signed, arbitrary b_ref 및 invalid domain). Actual `cargo test --locked --offline --test axbi_fast_small_shear_candidate`: **4/4 PASS**.

실제 immutable `SHEAR_MINUS_composed_001/history.csv` SHA-pinned saved 312238 histories 가운데 39행 간격으로 **8007개 genuine \(b(t)\)** 추출, \(\max|b|=0.00589287855\). 표본 조건에서 old actual-code-equivalent Simpson4096 대 new Taylor14 모두 f64 SIMD/native 최적화, CPU2, 각 7 inner warm iterations, 3 fresh process repetitions:
- 최고 관측 정규화 energy 차이 \(6.43929354283\times10^{-15}\)
- 최고 관측 정규화 quadrupole 차이 \(1.94289029309\times10^{-15}\)
- independent **current observer local-angle** GL128의 energy correction 및 quadrupole 검사: max differences \(3.10481620882\times10^{-16}\) and \(6.69256317032\times10^{-15}\), respectively.
- 3 fresh 반복의 전체 kernel speedup 각각 약 **2018×, 2058×, 2045×**, median 약 **2045×**. 이는 Simpson4096 대 14차 단일 모멘트 kernel이다. 전체 AX08 source, H/He chemistry, Jacobian, I/O, ODE solver의 가속이라고 해석하지 않는다. 별도 원래 science binary는 유지하고 optimized candidate를 production driver에 연결하지 않았다.

실행:
```bash
CARGO_TARGET_DIR="$PWD/.ax08_halfminus_target" CARGO_BUILD_JOBS=2 \
  taskset -c 2,3 cargo test --locked --offline \
  --manifest-path rust/rei_microphysics/Cargo.toml --test axbi_fast_small_shear_candidate

rustc -O -C target-cpu=native --edition=2021 \
  research/axbi_goal_20261014/convergence/ax08_halfminus_fast_20261015/bench_fast_moments.rs \
  -o /tmp/rei_ax08_bench_moments14_20261015

OPENBLAS_NUM_THREADS=1 taskset -c 3 python3 \
  research/axbi_goal_20261014/convergence/ax08_halfminus_fast_20261015/independent_local_gl128.py \
  --owner-root /home/cosmosapjw/Dropbox/bianchi/rei_bianchi
```

**제한:** Section 2의 source-free radiation moment들은 소스 ionizing photons(다중 에너지, H/He species photoheating), Thomson polarization 및 일반 anisotropic Boltzmann collision operator를 적분한 것이 아니다. `bass_cr` [PR71](https://github.com/cosmosapjw-quantum/bass_cr/pull/71)의 true child photon moments/cold error envelope는 다른 method이며, `BASS_HE` [PR64](https://github.com/cosmosapjw-quantum/BASS_HE/pull/64)의 source-scoped 16-cell warm P01는 지금 cold AX08와 물리모형이 달라 직접 대입하지 않았다. 같은 저장소 [AX03 공급자 PR121](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/121)의 Bianchi-I clock/Killing tables는 향후 exact-geometric crosscheck 후보, [PR122](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/122)는 completed MINUS source/census anchor다.

문헌: Fleury, Pitrou & Uzan (2015), *Phys. Rev. D* 91, 043511, DOI 10.1103/PhysRevD.91.043511 (Bianchi I null geometry); Friedrich et al. (2012), MNRAS 421, 2232, https://arxiv.org/abs/1201.0602 (helium+thermal timestep errors), Pawlik & Schaye (2011), https://arxiv.org/abs/1008.1071 (multifrequency thermal H/He). 독립적인 신규 observational conclusion 또는 publication novelty는 주장하지 않는다.

## 다음 진행 DAG

SHEAR_HALF_MINUS actual scientific run continues under its own single-start launcher. On natural terminal: verify actual `RETURN.txt`, launcher exit, selected endpoint \(a=0.2\), accepted counts, frozen SHA; **then** compose from the true predecessor with `compose_signed_history.py` by exact segment RETURN digest, complete H/He charge/material and signed fixed-a/fixed-proper-time comparisons including ±.005. Existing historical `SHEAR_PLUS` false classifier abort needs independent actual recovery. Only after full five-case signed family do AX11 matched \(\Delta t/\Delta E/\Delta\mu\) scientific convergence and a meaningful temperature error floor, then AX12 source/IC variants. No new full-history science admission, no convergence/observer visibility inference in this loop.
