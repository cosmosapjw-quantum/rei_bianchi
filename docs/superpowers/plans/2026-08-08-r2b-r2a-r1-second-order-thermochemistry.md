# R2B-R2A-R1 Second-Order Thermochemistry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the first-order thermochemistry trial with a nonautonomous MPRK22(1) chemistry update and a positive implicit trapezoidal thermal update, then determine whether the locked local-error gate closes at interval partitions 1024 or 2048 without weakening any conservation or ownership gate.

**Architecture:** Keep the R2B-R2A adaptive controller, tensorized forcing, owner law, and ten ledgers unchanged. Add an independently tested production–destruction decomposition, MPRK22(1) step, positive thermal trapezoid, and a candidate trial adapter. Run the candidate and the inherited backward-Euler oracle on the first canonical segment for all three lanes at partitions 512, 1024, and 2048; benchmark only after parity gates close.

**Tech Stack:** Python 3.13, NumPy/SciPy, existing JAX source-microphysics oracle, pytest, Wolfram Language symbolic checks, Precise Special Functions auxiliary references.

## Global Constraints

- Metric signature `(-,+,+,+)` and `epsilon_123=+1`.
- Keep `c`, `hbar`, and `k_B` explicit; time is seconds and energy is erg internally.
- No clipping, owner reassignment, `kappa=J/Phi` inversion, cloud/geometry inversion, per-node fitting, or post-hoc lane selection.
- `EFFECTIVE_HI_SUBGRID` has exact-zero resolved H, He, and thermal sources.
- Canonical total group `kappa_g,J_g` remain authoritative.
- Chemistry must preserve H and He nuclei and strict positivity without tolerance repair.
- Production candidate must use MPRK22(1) with nonnegative RK parameters; unsupported channels remain structural zero.
- Thermal update must solve a positive implicit predictor and positive trapezoidal corrector in `log T`.
- Candidate acceptance requires local error `<2e-4` at partition 1024 or 2048 for every required lane, plus all owner/nuclei/photon/thermal gates.
- Performance claims require numerical parity and measured warm-runtime evidence; JAX remains diagnostic unless it completes the science sequence deterministically.

---

### Task 1: Seal the pre-calculation stage

**Files:**
- Create: `stages/...R2A_R1.../INPUT_LOCK.json`
- Create: `stages/...R2A_R1.../STAGE_STATE.json`
- Create: `stages/...R2A_R1.../SCIENTIFIC_CONTRACT.md`
- Create: `stages/...R2A_R1.../receipts/HARNESS_RECEIPT.json`

**Interfaces:**
- Consumes: R2B-R2A compact reconstruction at commit `3b208b42...`, approved design, both harness ZIPs.
- Produces: immutable input hashes and predeclared tolerances used by all later tasks.

- [ ] Hash every load-bearing input and record remote read-only SHAs.
- [ ] Declare MPRK22(1), thermal trapezoid, partitions, lanes, and pass/fail criteria before calculation.
- [ ] Commit the pre-calculation lock.

### Task 2: Production–destruction decomposition

**Files:**
- Create: `analysis/pds_decomposition.py`
- Test: `tests/test_pds_decomposition.py`

**Interfaces:**
- Consumes: batched population RHS `[N,5]` and positive state `[N,5]`.
- Produces: nonnegative pairwise flux tensor `[N,5,5]` with exact H/He block conservation.

- [ ] Write RED tests for exact RHS reconstruction, positivity, structural blocks, and deterministic He donor/receiver ordering.
- [ ] Run tests and confirm missing implementation failure.
- [ ] Implement vectorized H 2-state and He 3-state transport decomposition.
- [ ] Run tests and commit.

### Task 3: MPRK22(1) chemistry kernel

**Files:**
- Create: `analysis/mprk22.py`
- Test: `tests/test_mprk22.py`

**Interfaces:**
- Consumes: `flux_fn(t,y)->[N,5,5]`, positive parent populations, `dt`.
- Produces: positive conservative predictor and corrector populations plus stage diagnostics.

- [ ] Write RED tests for positivity, exact nuclei conservation, nonautonomous two-state second order, structural zeros, and failure on invalid flux.
- [ ] Implement Patankar-Euler predictor and MPRK22(1) corrector with `sigma=y^(2)`.
- [ ] Verify observed order near 2 and commit.

### Task 4: Positive second-order thermal kernel

**Files:**
- Create: `analysis/thermal_trapezoid.py`
- Test: `tests/test_thermal_trapezoid.py`

**Interfaces:**
- Consumes: parent/final populations, parent energy/temperature, stage photoheating, volumes, Hubble rates, and `dt`.
- Produces: positive predictor temperature and implicit trapezoidal corrector with balance residual.

- [ ] Write RED tests for expansion-only second order, positivity, bracketing failure, and energy-balance closure.
- [ ] Implement `log T` predictor and trapezoidal corrector using deterministic vectorized bisection.
- [ ] Verify second-order convergence and commit.

### Task 5: Integrated second-order physical trial

**Files:**
- Create: `analysis/second_order_trial.py`
- Test: `tests/test_second_order_trial.py`

**Interfaces:**
- Consumes: R2B-R2A tensorized inputs, continuous forcing, owner kernel, source microphysics, and thermal/MPRK modules.
- Produces: one full second-order microstep and exact split ledgers.

- [ ] Write RED tests for all-lane owner support, exact-zero subgrid resolved source, transactional failure, and BE-limit consistency.
- [ ] Implement stage-time owner evaluations at `t0,t1`, MPRK chemistry, thermal predictor/corrector, and ledger routing.
- [ ] Verify tests and commit.

### Task 6: Science preflight and local-error comparison

**Files:**
- Create: `analysis/run_preflight.py`
- Create: `data/preflight_results.csv`
- Create: `results.json`
- Test: `tests/test_preflight_contract.py`

**Interfaces:**
- Consumes: candidate trial and inherited backward-Euler oracle.
- Produces: full/two-half local-error rows for partitions 512, 1024, 2048 and three lanes.

- [ ] Run candidate and BE oracle with no post-hoc changes.
- [ ] Record blockwise errors, gates, timings, and earliest failure certificates.
- [ ] Classify pass/fail using the sealed contract and commit raw results.

### Task 7: Optimization and lightweighting audit

**Files:**
- Create: `analysis/benchmark_second_order.py`
- Create: `PERFORMANCE_BENCHMARK_REPORT.md`
- Create: `receipts/PERFORMANCE_RECEIPT.json`

**Interfaces:**
- Consumes: numerically equivalent legacy/candidate kernels.
- Produces: cold/warm timing, peak-memory, map-call, and parity evidence.

- [ ] Benchmark array-native candidate against inherited BE fallback at matched accuracy.
- [ ] Verify no DataFrame/groupby or per-node objects occur in the hot path.
- [ ] Report speedup only if parity and repeatability gates pass.

### Task 8: Independent validation and durable closeout

**Files:**
- Create: `analysis/exact_validation.py`
- Create: `analysis/wolfram_validation.wl`
- Create: `FORMALISM.md`, `RESULTS_AND_VERDICT.md`, `MANIFEST.json`, `SHA256SUMS`
- Modify: `PROJECT_STATE.json`, `handoff/CURRENT_HANDOFF_PROMPT.md`, artifact registry, durable ledger.

**Interfaces:**
- Consumes: all stage results and tests.
- Produces: durable pass or fail-closed stage, compact artifact, tag, and incremental bundle.

- [ ] Run Decimal/mpmath and Wolfram symbolic checks.
- [ ] Run targeted tests, repository verifier, and file-isolated full pytest.
- [ ] Seal hashes and compact artifact.
- [ ] Commit, tag, verify from a prerequisite-only clone, and export delivery files without pushing.
