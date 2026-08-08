# Four-Corner OTS Propagation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Propagate every predeclared Hummer–Seaton/absorption/energy uncertainty lane through one partition-2048 thermochemistry microstep, prove population/photon/total-energy closure, and classify whether the resulting ionization/temperature enclosure is narrow enough to authorize an uncertainty-qualified first canonical interval.

**Architecture:** Keep the accepted 26-event topology, MPRK22(1), Alexander SDIRK2 thermal solver, owner law, material state, and canonical forcing unchanged. Add a stage-local event kernel that replaces the legacy scalar `v(T)` and `f(x_HI)` closures with explicit lane policies, emits event-resolved nonnegative PDS fluxes, and separates exact Ly-alpha heating from bounded two-photon heating and unresolved OTS radiation. Run full-step/two-half-step trials for every lane and aggregate deterministic componentwise enclosures without selecting a preferred corner.

**Tech Stack:** Python 3, NumPy, existing JAX-backed source-rate functions, MPRK22(1), Alexander SDIRK2, pytest, SymPy/Decimal, Wolfram Language validation, CSV/NPZ/JSON durable evidence.

## Global Constraints

- Metric signature `(-,+,+,+)`; `epsilon_123=+1`; explicit `c`, `hbar`, `k_B`.
- Base commit is `893d2e06f6a32015603087881933e4763f00d2cb`.
- Keep the accepted 26-event registry, MPRK22(1), Alexander-SDIRK2, analytic root backend, 46,080-node material state, owner law, and ten-ledger structure fixed.
- No clipping, owner reassignment, `kappa=J/Phi` inversion, cloud/geometry inversion, per-node fitting, post-hoc lane selection, or numerical import from `rec_bianchi`.
- Hummer–Seaton table nodes are source-locked; piecewise linear interpolation in `log10(T)` is a named adapter, not source-identical data.
- Below `10^4 K`, retain strict `v in [0,1]`; above `10^5 K`, fail closed with `BRANCH_DOMAIN_ESCAPE`.
- Use `f in {0.1,1.0}` as the published endpoint lanes.
- Exact He II Ly-alpha packet energy is `40.813320 eV`.
- Unidentified packet energy is never set to zero; it remains in `E_OTS_unres` or an explicit interval bound.
- Numerical hard gates: nuclei/owner/PDS `1e-11`, photon `1e-8`, thermal root `1e-10`, local error `2e-4`.
- Predeclared uncertainty-qualified gate: maximum absolute width of each ion fraction `<=2e-3`, maximum `log(T)` width `<=2e-3`.

---

### Task 1: Durable Stage Scaffold and Input Lock

**Files:**
- Create: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_FOUR_CORNER_BRANCH_AND_UNRESOLVED_OTS_ENERGY_PROPAGATION_PREFLIGHT/INPUT_LOCK.json`
- Create: same directory `STAGE_STATE.json`, `00_READ_FIRST.md`, `RESEARCH_CONTRACT.md`
- Create: `receipts/RESEARCH_HARNESS_RECEIPT.json`, `receipts/REMOTE_READ_ONLY_RECEIPT.json`

**Interfaces:**
- Consumes: current durable HEAD, preceding stage hashes, connector-verified remote heads, research harness SHA-256.
- Produces: immutable pre-calculation policy and hard-gate configuration for all later tasks.

- [ ] **Step 1:** Hash every upstream input and write `INPUT_LOCK.json` with `calculation_started=false`.
- [ ] **Step 2:** Record `rei_bianchi/main=fc744213...` and `rec_bianchi/main=2d777b1c...`; classify the latter as semantic review only.
- [ ] **Step 3:** Validate `physmath-research-harness-gpt56(6).zip` and store the receipt.
- [ ] **Step 4:** Run `python scripts/verify_repo.py` and the preceding stage tests; save logs.
- [ ] **Step 5:** Commit the scaffold and lock before any propagation calculation.

### Task 2: Branch Policy and Two-Photon Energy Bounds

**Files:**
- Create: `analysis/branch_uncertainty.py`
- Test: `tests/test_branch_uncertainty.py`
- Create: `validation/wolfram_branch_uncertainty.wl`

**Interfaces:**
- Produces: `evaluate_v_policy(T, policy) -> ndarray`, `branch_coefficients(...)`, and `two_photon_excess_bounds(y) -> (lower, upper)`.

- [ ] **Step 1: Write failing tests** for exact Hummer–Seaton nodes, below-table strict endpoints, above-table fail-close, adapter bracketing, four-corner photon identity, and analytic two-photon bounds at `y=0` and `y=1`.
- [ ] **Step 2: Verify RED** with `pytest -q .../tests/test_branch_uncertainty.py`.
- [ ] **Step 3: Implement the minimal branch module** using exact table values and support-class formulas.
- [ ] **Step 4: Verify GREEN** and run the Wolfram symbolic identities.
- [ ] **Step 5: Commit** the branch and energy-bound kernel.

### Task 3: Event-Resolved PDS and OTS Energy Ownership

**Files:**
- Create: `analysis/event_flux_kernel.py`
- Test: `tests/test_event_flux_kernel.py`

**Interfaces:**
- Consumes: five-species state, proper volume, resolved photoionization fields, `v` and `f` lane values, energy-bound policy.
- Produces: nonnegative `flux[N,5,5]`, population RHS, exact Ly-alpha heat rate, bounded two-photon heat rate, unresolved/escaped OTS energy rates, and event diagnostics.

- [ ] **Step 1: Write failing tests** that event-flux sums reproduce the source RHS when supplied the legacy branch values, every transfer is nonnegative, no direct HeI-to-HeIII edge exists, H/He invariants vanish, and energy owners are mutually exclusive.
- [ ] **Step 2: Verify RED**.
- [ ] **Step 3: Implement explicit source channels** for photo/collisional ionization, HII recombination, HeII ground/case-B, HeIII ground/n2/cascade.
- [ ] **Step 4: Implement exact Ly-alpha and bounded two-photon energy ownership**; assign all other unidentified packet energy to `E_OTS_unres` by conservation.
- [ ] **Step 5: Verify GREEN** and commit.

### Task 4: Uncertainty-Aware MPRK22/SDIRK2 Trial

**Files:**
- Create: `analysis/uncertainty_trial.py`
- Test: `tests/test_uncertainty_trial.py`

**Interfaces:**
- Produces: `UncertaintyTrialResult` with final state, full ledgers, closure residuals, lane identifiers, and failure certificate.

- [ ] **Step 1: Write failing tests** for one small-node trial: positivity, nuclei closure, photon closure, total-energy closure, exact parent-state immutability, and deterministic repeatability.
- [ ] **Step 2: Verify RED**.
- [ ] **Step 3: Implement a stage-local trial** that uses event fluxes in MPRK22 and adds exact/bounded OTS heat to the existing SDIRK2 photoheat while preserving unresolved energy separately.
- [ ] **Step 4: Verify GREEN** and commit.

### Task 5: Full 46,080-Node Four-Corner Preflight

**Files:**
- Create: `analysis/run_four_corner_preflight.py`
- Create: `data/LANE_RESULTS.csv`, `data/ENCLOSURE_SUMMARY.json`, `data/ENCLOSURE_EXTREMA.npz`
- Test: `tests/test_preflight_artifacts.py`

**Interfaces:**
- Runs 3 shape lanes × 4 `v` policies × 2 `f` endpoints × 2 energy-bound policies = 48 deterministic lanes.
- Each lane performs one full and two half partition-2048 trials.

- [ ] **Step 1: Write artifact tests** for exact lane count, no post-hoc selection, closure gates, envelope extrema, and deterministic hashes.
- [ ] **Step 2: Verify RED**.
- [ ] **Step 3: Run all 48 lanes**, preserving every failure certificate.
- [ ] **Step 4: Aggregate componentwise extrema** for `x_HII`, `x_HeII`, `x_HeIII`, and `log(T)`.
- [ ] **Step 5: Apply the predeclared uncertainty gate** and classify either `UNCERTAINTY_QUALIFIED_FIRST_INTERVAL_AUTHORIZED` or `SOURCE_EXTENSION_CALIBRATION_REQUIRED`.
- [ ] **Step 6: Verify GREEN** and commit science results.

### Task 6: Harness Closeout, Durable Packaging, and Verification

**Files:**
- Create: phase documents `01_...` through `10_...`, `FORMALISM.md`, `RESULTS_AND_VERDICT.md`, `INDEPENDENT_REVIEW.md`, `NEXT_STAGE_PROMPT.md`
- Create: `results.json`, `MANIFEST.json`, `SHA256SUMS`, compact ZIP, receipts.
- Modify: `PROJECT_STATE.json`, `handoff/CURRENT_HANDOFF_PROMPT.md`, `artifacts/registry/ARTIFACT_REGISTRY.json`, `docs/provenance/DURABLE_STAGE_LEDGER.csv`.

- [ ] **Step 1:** Run independent exact Decimal/SymPy replay and Wolfram validation.
- [ ] **Step 2:** Run stage tests, repository verifier, file-isolated full pytest, SHA audit, ZIP CRC, `git diff --check`, and `git fsck --full`.
- [ ] **Step 3:** Write the ten research-harness phase records and adversarial review.
- [ ] **Step 4:** Build deterministic compact artifact and delivery package.
- [ ] **Step 5:** Commit the durable stage, create an annotated tag, and create an incremental Git bundle.
- [ ] **Step 6:** Verify the bundle in a prerequisite-only fresh checkout; do not push remotely.
