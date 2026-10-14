# REI SOURCE07 C3: 문턱 통과 보존형 q-수송과 실제 CPU 최적화
2026-10-15 KST. 사용자 요청: 이론 구성과 Ubuntu 로컬 Rust 구현/검산, 경량화·SoA·병렬화를 함께 실행. 선택 단계는 C3 수치 설계이며 구현은 해당 설계를 검증하는 bounded stage-local component다. Full H/He EoR chemistry/full AX08 admission은 미수행·미발급.

## 물리·수치 정의
계량은 (-,+,+,+), x0=ct, a_perp=a exp(-b), a_parallel=a exp(2b). 기존 C2와 동일하게 광자 label k_i=cq_i=a_i E n_i [eV]를 보존한다. C3의 manufactured frozen-neutral background는 구간 동안 세 방향의 H_i >=0 상수다. 이는 실제 AXBI H(a,q) 전체 역사와 동일하지 않다.
E(t)=sqrt(sum_i[(k_i/a_i(0))exp(-H_i t)]²).
lambda_i(t)=c_cm_s n_absorber,i sigma_Verner,i(E(t)).
N(t)=N(0) exp(-integral_0^t sum lambda_i ds).
Species A_i=integral_0^T N(t) lambda_i(t)dt. B=sum A_i I_i and Q=sum integral (E(t)-I_i)dA_i. Source-free geometric work W=integral_0^T N(t)(-E_dot(t))dt >=0, with E_dot=-E sum H_i n_i².
Conservation identities: N(0)=N(T)+sum A_i, N(0)E(0)=N(T)E(T)+B+Q+W. Absorber densities are proper cm^-3 frozen; binding thresholds HHeModel=13.598434599702,24.587389011,54.41776eV, Verner photoionization FIT cutoffs13.60,24.59,54.42eV. Cross sections applied once, c=29979245800 cm/s once; no imposed external UVB Γ.

The code brackets and bisects EVERY active physical threshold-crossing time on monotone E(t), then applies midpoint cross-section/energy and an exactly exponential number-loss fraction within each smooth subinterval. It preserves discrete photon and energy ledgers. This is NOT an exact variable-opacity continuous step; opacity and source/thermal feedback errors remain. A trajectory with any H_i<0 is rejected instead of silently assuming monotonicity. No temporal emission while propagating this cohort.

The integrated time-of-flight threshold function is continuous at the boundary for positive H even though sigma(E) jumps. Thus naive C² global spectral interpolation error statements are invalid across thresholds; the C3 numerical representation splits there explicitly. For smooth subsegments midpoint quadrature is nominal second order as length->0; the non-linear reaction and floating point error are measured, not certified by this statement.

## 실제 구현 및 최적화
Added optional source rust/rei_microphysics/src/axbi_q_advance.rs, new public lib.rs module, test axbi_q_event.rs and release benchmark axbi_q_batch_bench.rs. Existing AXBI driver/scenario/output/checkpoints and previous optional q-reference module unchanged.
- Geometry algebra common-subexpression removal: FLRW uses one exponential, LRS axisymmetry two instead of three; Verner calls skipped when density=0 or local E below FIT cutoff.
- Event-time accurate topology via 64-step bisection, event-split midpoint rates, exact exponential photon depletion per smooth slice.
- Stateless packet batch with std::thread::scope, 1/2/4 worker choices, no global Rayon pool; parallel only when >=512 packets per worker, results returned in original order. Binary64 outputs are bit-identical for serial/parallel in targeted test.
- Optional EnergySoA holds three contiguous k-vector component arrays and precomputes inverse scale factors once; fast sqrt readout for capped <=50keV physically representable photons, separate robust original hypot path preserved. SIMD-friendly layout is not a certificate of actual SIMD machine instructions. Additional 589824 bytes for 24576 packets in measured SoA snapshot.

## 독립 수치 정확도
Single HeII-only manufactured case: initial 54.9eV, H_i=1e-16 s^-1, n_HeII=1e-10cm^-3, duration1e15 s. Exact cutoff crossing time log(54.9/54.42)/H = 87816151603846.19 s. Independent SciPy DOP853 integrating Verner HeII gives absorbed0.0004128992999639923 photons/H; direct heating0.00009949266237910015 eV/H. Rust event-aware midpoint, 256 requested nominal slices, gives absorbed0.0004128992824797633, heating0.00009949324513704671; differences -1.748422896264215e-11 photons/H and +5.827579465538836e-10 eV/H. The fixed midpoint nstep distribution adjusts to event-split intervals (hence labels do not always correspond to equal total substeps). No error enclosure for a general coupled gas state.

## 성능: 실제 Ryzen 5900X; matched accuracy
3 external fresh release benchmark invocations, each with 3 measured inner repetitions, medians (seconds in BENCHMARK_ANALYSIS.json). Same 24576 independent packets, 8 nominal slices, same sources, gas and H for each serial/parallel comparison. FLRW serial 36.407 ms vs 2-worker22.851 ms vs 4-worker14.962 ms (speedup 2.43x). LRS axisym serial38.983 vs 2-worker23.199 vs 4-worker14.379 ms (2.71x). All final per-packet output bits agree between serial and parallel for the fixed bench physics; CPU frequency scheduling can vary across repetitions, no unconditional speedup claim.
48 repeated full-array energy-only readouts: original AoS hypot21.556 ms vs contiguous SoA sqrt3.738 ms (5.77x), matching physics energies to the documented relative bound. The SoA input buffer uses589824 extra bytes. This comparison benefits from one shared geometry validation and explicit capped moderate energy range; does not show SIMD instructions or overall source+chemistry acceleration.

Memory risk: CovariantPhoton32 B, EvolvingPacket96 B. Naive 384 source cohorts per accepted step across200000 accepted steps uses 2,457,600,000 bytes=2.288818GiB just for live packet base state, already above 2GiB lane cap, before allocations/chemistry. Do NOT enable cohort accumulation as the full driver. This C3 batch code uses bounded transient 24,576 packets for measurement only.

## 다른 repo 실제 결과 반영
bass_cr PR65 implemented a separate threshold-aware energy remapper and showed redshift/absorption noncommutation; PR66 implemented budgeted source energy-cohort compression 48->32, 240->32 after four toy emissions, with only local frozen-neutral floating-evaluated budget certificates. These were READ; not copied or relabeled as a direction-preserving full Bianchi q compressor. For a q+angular design, any merge must preserve directional momentum and forecast threshold tube, not only scalar mean energy. BASS_HE PR57 warm P01 Jacobian work is a different proper/comoving density and 2904-bin source. BASS PR151 cap+RK4 and rec_bianchi PR85 clock techniques are methodology comparisons, not imported physics constraints. Primary references include Mellema et al. 2006 C2Ray astro-ph/0508416; Mirocha et al. 2012 arXiv1204.1944; Pawlik & Schaye 2011 arXiv1008.1071; Fleury/Pitrou/Uzan 2015 arXiv1410.8473.

## 검증/수용
Targeted RED observed missing module and then repaired test-input densities to avoid saturated tau; GREEN accepted only after measured native checks. Current 6 targeted tests pass (including independent DOP853 calibrated numbers, free-flight ledger, error rejection, serial/parallel binary64 identity and SoA consistency); full crate Cargo tests and all-targets check separate fresh receipts. Actual local Wolfram Engine15.0.0 xAct/xTensor1.3.0/xCoba0.8.6 returned scalar14 and tensor5 zero identities after FullSimplify fixed a first RawJSON failure; original source identities unchanged except additive lib.rs module declaration.
This is an optional research reference. Status C3_SCOPED_NUMERICAL_DESIGN_AND_NATIVE_REFERENCE = COMPLETED_SCOPED; production AXBI EoR is still IN_PROGRESS/NOT_ISSUED. Native subagents NOT_RUN (no spawn/delegate exposed).

## C4 next
Do a bounded q-transport representation/memory allocation DAG: choose fixed q energy/angular grid vs compressed directional cohorts, source R*J quadrature at all emission times (E* support to432.2293723205eV), exact threshold transport substeps, time-varying proper gas and heating feedback, and independent verification against current historical 49-node/guard51-node with identical source/IC/clock. Define physical variant/versioned checkpoint before running full EoR or claiming matched shear.
