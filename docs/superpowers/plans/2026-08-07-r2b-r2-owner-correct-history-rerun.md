# R2B-R2 Owner-Correct Fixed-Point History Rerun Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the five-slab, 46,080-node owner-correct H/He/thermal history with transactional fixed points and `dt`/2/4/8 refinement, while preserving separate resolved and unresolved ledgers.

**Architecture:** Canonical BDF rows provide time-dependent total group opacity/current and global background data. A state-conditioned owner law disintegrates those totals into four exclusive owners and node currents. Each accepted microstep solves positive implicit H/He chemistry and resolved thermal energy from the parent state, commits once on success, and otherwise rolls back exactly.

**Tech Stack:** Python 3.13, NumPy/Pandas/SciPy, JAX 64-bit for batched residual/Jacobian kernels, pytest, Wolfram symbolic audit, Decimal/mpmath independent replay.

## Global Constraints

- Metric signature `(-,+,+,+)`; `epsilon_123=+1`.
- Preserve explicit `c`, `hbar`, `k_B` and all unit adapters.
- No clipping, owner reassignment, `kappa=J/Phi` constitutive inversion, cloud/geometry inversion, per-node fitting, or post-hoc lane selection.
- No recombination surrogate or numerical import from `rec_bianchi`.
- Every calculation runs after the immutable input lock commit.
- Failed attempts are preserved independently.

---

### Task 1: Freeze inputs and baseline receipts

**Files:**
- Create stage `INPUT_LOCK.json`, `STAGE_STATE.json`, receipts, manifest, SHA256SUMS.
- Create `tests/test_input_lock.py`.

**Interfaces:**
- Consumes: R2B-R1 initial state, owner law, canonical BDF forcing, Verner/heating moments, canonical reionization rate sources.
- Produces: immutable stage input registry and baseline proof.

- [ ] Write a test that recomputes every locked repo-file SHA-256 and rejects mutation.
- [ ] Run the test and verify it fails before the input-lock reader exists.
- [ ] Implement the lock reader and hash validator.
- [ ] Run the test and baseline repository/harness suites.
- [ ] Commit the precalculation lock.

### Task 2: Time-slab forcing and owner disintegration

**Files:**
- Create `analysis/forcing.py`, `analysis/owner_kernel.py`.
- Test `tests/test_forcing_owner.py`.

**Interfaces:**
- Produces `ForcingSlab`, `OwnerSplit`, and node current arrays for four owners.

- [ ] Test exact endpoint values, monotone times, group-total additivity, unsupported exact zeros, and subgrid resolved-source exact zero.
- [ ] Verify RED failures.
- [ ] Implement stable PCHIP/Clenshaw-Curtis forcing evaluation and state-conditioned owner/node splitting.
- [ ] Verify GREEN and record residuals.
- [ ] Commit.

### Task 3: Positive implicit H/He and thermal microstep

**Files:**
- Create `analysis/microphysics.py`, `analysis/implicit_step.py`.
- Test `tests/test_implicit_microphysics.py`.

**Interfaces:**
- Consumes owner-resolved photoionization currents and canonical local rate functions.
- Produces a positive node state and separated energy terms.

- [ ] Test identity, Saha-like null lane, nuclei conservation, structural zeros, infeasible-demand rejection, and thermal ownership.
- [ ] Verify RED failures.
- [ ] Implement vectorized full-OTS H/He RHS, cooling/expansion, and positivity-preserving implicit solve in logistic/softmax/log coordinates.
- [ ] Verify analytic/JAX Jacobian against finite difference and GREEN tests.
- [ ] Commit.

### Task 4: Transactional slab fixed point

**Files:**
- Create `analysis/transaction.py`, `analysis/fixed_point.py`.
- Test `tests/test_transaction_fixed_point.py`.

**Interfaces:**
- Produces accepted slabs, failed-attempt certificates, and byte-stable restarts.

- [ ] Test one-time commit, nonconvergence rollback, infeasible-reaction rollback, restart identity, and earliest-certificate retention.
- [ ] Verify RED failures.
- [ ] Implement outer state/owner Picard-Newton iteration with damping declared before results.
- [ ] Verify GREEN.
- [ ] Commit.

### Task 5: Full primary and auditor refinement matrix

**Files:**
- Create `analysis/run_history.py`, output CSV/NPZ/JSON evidence.
- Test `tests/test_history_refinement.py`.

**Interfaces:**
- Produces four refinement histories for primary and two auditor lanes.

- [ ] Test synthetic convergence and deliberate failure classification.
- [ ] Verify RED failures.
- [ ] Run all five slabs at refinement 1/2/4/8, preserving each lane independently.
- [ ] Compute photon, nuclei, thermal, unresolved-energy, fixed-point, rollback, and restart gates.
- [ ] Commit accepted or fail-closed scientific outputs.

### Task 6: Independent validation and durable closeout

**Files:**
- Create Wolfram script, Decimal/mpmath validator, formalism, evidence ledger, adversarial review, final manifest and compact bundle.
- Update `PROJECT_STATE.json`, handoff, artifact registry, and durable ledger in one commit.

**Interfaces:**
- Produces the durable verdict and next-stage authorization.

- [ ] Run Wolfram identities and independent high-precision replay.
- [ ] Run full repository tests, stage SHA audit, ZIP CRC, git fsck, clean-clone bundle verification.
- [ ] Apply the authorization gate exactly as written.
- [ ] Commit and tag the durable stage; do not push from this runtime.
