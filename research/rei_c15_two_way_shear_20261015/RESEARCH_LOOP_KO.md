# REI C15: native MD14/Case-A H/He ↔ Einstein–Boltzmann shear short-window feedback

2026-10-15 KST. 실제 Ubuntu에서 물리/코딩 루프 C5–C8 시행. 사용자 baseline은 [REI C14 PR139](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/139) exact HEAD 1ca73d64d3aaf7ea3ed4b7265522bbfdfae7e228. 새로운 격리 worktree research/rei-c15-two-way-shear-20261015; original owner checkout와 C13/C14 원본 physics, original AX08 4개의 full signed histories, private source bindings, native binary는 변경하지 않았다. Local Codex NOT_USED. Native AI subagent NOT_RUN (호스트에 dispatch가 없음).

## 직접 실행한 original sources

[REI C13 PR138](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/138)의 native AxbiSource stellar MD14_Z002_FESC_BB50K_13P6_100_V1에서 생성된 NATIVE_SOURCE_8X8.csv original 원본을 입력한다. NativeStellarSource.load, PhotonCloud.drift, emit_half, reaction_step, SourceState, positive original coalesce.reduce_age_cohorts을 재사용. C13의 original C11 Grackle Case-A H/He recombination 및 photoionization/heating/escaped energy owner도 변경하지 않는다.

[REI C14 PR139](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/139)의 실제 [BASS PR159](https://github.com/cosmosapjw-quantum/bass/pull/159) PSTF unpolarized homogeneous Liouville+Thomson gamma/nu source가 동일 Git blob identity e15e1875fba7fcc4a42e257e291c54d9b540a3f0에 pinned되어 있다. C14 _cached_source_angular_operators(L), omega_gamma_fraction, validate_source_sha를 직접 호출, gamma-only Thomson 및 massless-neutrino collisionless stress를 Einstein에 합산한다.

[BASS PR160](https://github.com/cosmosapjw-quantum/bass/pull/160) / [REI PR140](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/140) 실제 finite-mass FD96 radial J_i kinetic π_m is separately examined. 바리온과 중복될 수 있는 Omega_m을 임의로 분배하지 않고 아직 C15에는 이식하지 않았다. [REC HyRec PR94](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/94) source-specific z20 donor opt-in, BASS_HE warm P01 16-cell은 다른 source, bass_cr의 엄격한 source-conditioned precision HOLD, WU088_HH physical k_HH rate는 공급자 승인되지 않아 모두 해당 조건을 유지한다.

## 연속 물리 방정식과 실제 operator path

Metric (-,+,+,+): ds²=-c²dt²+a² exp(-2b)(dx²+dy²)+a² exp(4b)dz². s=dot b, orthonormal shear diag(-s,-s,2s). 사용자 정의 Sigma=√3|s|/H≥0, epsilon_sigma=sign(s). Frozen q_ref는 original initial-condition adapter에만 남는다.

Gamma/nu energy and number moment arrays in BASS PSTF LRS: J_Eγ,l,Nγ,l,J_Eν,l,Nν,l. κγ,κν initial independent positive angular W=1+κP2; Thomson collision affects photons only, Γ_T=cσ_T n_e(actual evolving CaseA HHe). Gamma+nu quadrupole DeltaP=(P_parallel-P_perp)=rho_crit,0*(OmegaGamma J_Eγ,2+OmegaNu J_Eν,2)/a⁴. Current native stellar ionizing photons give DeltaP_UV=nH_proper (1.602176634e-13 Pa per eV cm^-3) sum[(N_i/N_H)E_i P2(mu_i)]. DeltaP=3Pi where traceless tensor π^i_j=diag(-Pi,-Pi,2Pi). K=8πG/(3c²).

H²=H0²[Omega_m/a³+Omega_Lambda+(OmegaGamma J_Eγ,0+OmegaNu J_Eν,0)/a⁴]+s²+K*(rho_UV+u_th+u_binding).
ds/dln a=-3s+K*(DeltaP_gamma+nu+DeltaP_UV)/H;
db/dln a=s/H, dt/dln a=1/H.
J_E,0'=-2(s/H)J_E,2; N_0'=0, independently tested in Wolfram and per source row. Wolfram exact GR/number/energy/anisotropic-work formal conservation checks 5/5 zero on isolated radiation-only model (CHECK_C15_CAS.wl); NOT a total Einstein external MD14 stellar-source energy conservation proof.

Each short source macro step a0→geometric mean→a1 uses DOP853 of dynamically sourced Einstein H,s,b and BASS photon/nu L=4,8,12 energy/number multipoles. Recomputed *proper time* and updated Killing δb transport the real original C13 photon E,mu per next stage; native source photons injected, actual CaseA photoabsorbed and gas H/He temperature evolved, dt midpoint fixed point solved (max two iterations), second half and next C15 step repeated. C13 photon-number, electron/binding/heat/escaped photon/expansion-energy ledgers checked on every accepted state, nonnegative phase-space and 64-point angular positivity and physical pressure cone required with fail-closed no clipping. Original positive cohort compression may only replace source packet arrays when original C13 event/heat budgets pass.

### Einstein energy closure not yet complete

The stellar MD14 photon emission reservoir and escaped Case-A recombination photons are not included as dynamical gravitating external source energy–momentum, UV absorption and Thomson baryon momentum recoil are not globally accounted for, and gas rest-mass/binding double-counting is not fully addressed. Instantaneous Einstein H constraint receives rho_UV,u_th,u_binding but full sum species ∇_b T^{ab}=0 and evolution of Raychaudhuri under all sources remains **NOT_ISSUED**. Matter pi_m is absent, complete E/B polarized Thomson operator not implemented. This is a scientific bounded operator-split demonstration, NOT an Einstein+HHe fully self-consistent reionization cosmology.

## Actual short interval numerical results

All physical source runs restricted to a=.1999→.2, manufactured receiver gas xHII=.4,xHeII=.5,xHeIII=.3,Tgas=12000 K from original C13. This is NOT the physical cold zbar20 initial condition and not a zbar20→4 EoR history.

64 source steps, L8, real 8 spectral cells per three thresholds ×8 angles:

| source initial Sigma_ref and radiation kappa | final Sigma | xHII | Tgas K | J2γ | UV DeltaP Pa |
|---|---:|---:|---:|---:|---:|
| Sigma0,κγ=κν=0 | ~0 | 0.408818187182 | 12193.4281740 | ~0 | ~0 |
| Sigma0,κγ=κν=.2 | 4.965713124856e-8 | 0.408818187182 | 12193.4281740 | 0.03999969576346 | -8.743e-32 |
| Sigma_ref=.008660145787,sign+1,κ=.2 | .001000001092674 | .40881818566255 | 12193.42813743 | .03999921711067 | -2.11932e-27 |
| Sigma_ref=.008660145787,sign−1,κ=.2 | .000999901778444 | .40881818566255 | 12193.42813743 | .04000017441655 | +2.11914e-27 |

Primordial gamma/nu DeltaP∼1.764e−12 Pa vastly exceeds the stellar UV DeltaP in this fixed short experiment. UV stress on/off produce identical binary64 outputs, so UV feedback is present as a correctly normalized RHS term but its backreaction is **NOT NUMERICALLY RESOLVED**, not detected. Independent BASS primordial κ drives Sigma from zero to 4.966e−8. Removing κ gives FLRW within roundoff.

Original C13 q0,kappa0 source n128 yields xHII=.40882451599893593 and Tgas=12193.495444733417K; C15 q0,kappa0 n128 xHII=.4088245159927982 and Tgas=12193.495444585651K. Differences ∼6.1e−12 and 1.48e−7 K, NOT physical AX11 uncertainty. Actual n16 Thomson τ DOP853=8.44900358315e−6 and independent trapezoid diff relative 2.73e−10. Source chemistry L_N residual <6e−16 and L_E <1.1e−14 eV/H on actual accepted history.

## Real accuracy, speed and source scope

- New C15 physics/invalid-input tests 11/11 PASS before and after physical cone guards.
- Original C13 native/C11 16/16 tests rerun unchanged, C14 gamma/nu external HHe 9/9, original C12 five pinned supplier tests 6/6, total local targeted 42/42 PASS. This is NOT GitHub Actions green status.
- Scoped C15 source experiments: ten signed/κ/Thomson/UV toggle cases, nstep 8/16/32/64/128, Lmax4/8/12, native source 4X8/8X8/16X8/32X8, same relevant IC. Time HII refinement difference ratios approach ∼4 (2nd order), thermal T refinement approaches ∼4. Spectral Tgas 12193.69064878,12193.42817402,12193.36031035,12193.34319790K for increasing source energy subdivision, ratio∼3.96. No global numerical certification.
- Five matched whole C15 original C13-positive coalescence repeats at n64: uncompressed median1.364624614s vs compressed median0.474900842s **2.87349× whole one-scenario solver speedup**; photon packet max array count 64× reduced (not total RSS). Final safety-gated study wall22.70s and peak RSS146172KiB.
- Four true independent scientific q initial cases: 4 process benchmark repeats, CPU2–4, serial median1.864938475s vs 3-worker median0.965374793s, **1.93183× batch throughput**, 12 scientific f64 outputs HEX IDENTICAL in every replay.
- Wolfram15 all five exact radiation-only GR tensor identities zero. No local Codex and no native AI subagents.

GitHub workflows: PR137, PR138, PR139 jobs failed before tests due historical rustfmt --all -- --check mismatches in pre-existing Rust files; GitHub cargo test was **SKIPPED**, not an executed science failure. Do not silently reformat original source in this physics PR.

## Run and next DAG

From isolated worktree:

    export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
    D=research/rei_c15_two_way_shear_20261015
    taskset -c 2 python3 "$D/test_c15_coupled.py"
    taskset -c 2 python3 "$D/study_c15.py"
    taskset -c 2,3,4 python3 "$D/benchmark_parallel.py"
    wolframscript -file "$D/CHECK_C15_CAS.wl"
    python3 -m unittest discover -s research/rei_c13_live_source_20261015 -p 'test_*.py' -v
    python3 -m unittest discover -s research/rei_c14_thomson_receiver_20261015 -p 'test_*.py' -v

Result data: results/STUDY_C15.json, results/parallel_C15.json, original sample CSV and actual PNG, NEXT_DAG.json, SOURCE_MANIFEST.json, RESULT_STATUS.json. Remaining physical C16: actual Q^\mu stellar emission/UV photoabsorption/recombination escape with baryon momentum/energy ownership; BASS polarized I/E/B full collision operator and PR140 massive J_i matter Pi without Omega double count; physical low-T zbar20→4 non-equilibrium HHe source and independent AX11 dt/dE/dmu, thermal and observer tail. Scientific admission **NOT_ISSUED**.
