# R1B-R2B-R1 Material-State and Owner-Law Lock Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lock the canonical initial 46,080-node material state and a deterministic state-dependent four-owner opacity/current law, then decide whether the fixed-point history rerun is authorized.

**Architecture:** Reuse the fixed B2C2B0A hierarchy and exact R1B-R1 direct-history initial row. Build material states in comoving extensive units, with local temperature recovered from resolved internal energy. Compute owner fractions from nonnegative component responses and condition them to canonical total opacity/current; use `LOCAL_NEUTRAL_HAZARD_PRIMARY` as the predeclared subgrid node law and retain two alternatives as auditors.

**Tech Stack:** Python 3.13, NumPy, pandas, SciPy, pytest, SymPy, Wolfram Language validation, Git.

## Global Constraints

- Metric `(-,+,+,+)` and `epsilon_123=+1`.
- Keep `c`, `hbar`, and `k_B` explicit.
- No per-node fitting, clipping, mass/geometry inversion, owner reassignment, or recombination surrogate.
- Do not integrate a production history in this stage.

---

### Task 1: Canonical initial material state

**Files:**
- Create: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R1_CANONICAL_INITIAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK/analysis/initial_material_state.py`
- Test: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R1_CANONICAL_INITIAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK/tests/test_initial_material_state.py`

**Interfaces:**
- Produces `build_initial_material_state(...) -> InitialMaterialState`.

- [ ] Write RED tests for H/He/energy closure, positivity, deterministic hash and exact canonical source row.
- [ ] Run the targeted tests and confirm failure because the module is absent.
- [ ] Implement the minimal positive hierarchy lift and single-factor thermal normalization.
- [ ] Run targeted tests and commit.

### Task 2: State-derived owner law

**Files:**
- Create: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R1_CANONICAL_INITIAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK/analysis/state_derived_owner_law.py`
- Test: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R1_CANONICAL_INITIAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK/tests/test_state_derived_owner_law.py`

**Interfaces:**
- Consumes the initial material state and canonical forcing row.
- Produces `evaluate_owner_law(...) -> OwnerLawResult`.

- [ ] Write RED tests for owner closure, common flux, exact zeros and state sensitivity.
- [ ] Confirm RED.
- [ ] Implement current-state atomic response plus deterministic subgrid primary law.
- [ ] Confirm GREEN and commit.

### Task 3: Full evidence matrix and independent checks

**Files:**
- Create: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R1_CANONICAL_INITIAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK/analysis/run_stage.py`
- Create: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R1_CANONICAL_INITIAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK/analysis/wolfram_validation.wl`
- Create: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R1_CANONICAL_INITIAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK/analysis/exact_fallback.py`
- Create data CSV/NPZ/JSON under `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R1_CANONICAL_INITIAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK/data/`.

- [ ] Run the initial-state and 85-time-row owner-law matrix.
- [ ] Run material-state perturbation, homogeneous, zero-support and structural-zero adversaries.
- [ ] Run Wolfram and high-precision fallbacks.
- [ ] Run full repository regression and independent review.

### Task 4: Durable closeout

**Files:**
- Update: `PROJECT_STATE.json`, `handoff/CURRENT_HANDOFF_PROMPT.md`, `docs/science/current_00_READ_FIRST.md`, `docs/provenance/DURABLE_STAGE_LEDGER.csv`, `artifacts/registry/ARTIFACT_REGISTRY.json`.
- Create final stage formalism, verdict, manifest, receipts, compact artifact and `SHA256SUMS`.

- [ ] Decide pass/fail solely from predeclared gates.
- [ ] Preserve every failed attempt.
- [ ] Verify repository, tests, hashes, ZIP CRC and Git integrity.
- [ ] Commit, tag, and export an incremental bundle without pushing.
