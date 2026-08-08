# R2B-R2A-R2-R1A Four-Corner OTS Propagation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify a durable 48-lane first-interval uncertainty-propagation preflight for the source-locked full-OTS event graph.

**Architecture:** Add a focused event/energy uncertainty operator that wraps the accepted physical trial without changing its owner law or integrators.  The runner executes 16 uncertainty policies for each of three fixed shape lanes, streams microstep evidence, constructs nodewise enclosures, and fail-closes on any physical, ledger, or uncertainty gate.

**Tech Stack:** Python 3, NumPy, existing JAX-backed source rates, MPRK22(1), Alexander-SDIRK2, pandas only for final evidence tables, SymPy/Decimal, Wolfram validation, Git durable artifacts.

## Global Constraints

- Metric `(-,+,+,+)`, `epsilon_123=+1`, explicit `c`, `hbar`, `k_B`.
- No clipping, source-table extrapolation, owner reassignment, `kappa=J/Phi` inversion, cloud/geometry inversion, per-node fitting, or post-hoc lane selection.
- Preserve all 26 event IDs and source branch topology.
- Keep non-Ly-alpha unidentified energy in `E_OTS_unres`; never set it to zero.
- User performs remote push; no remote-write claim.

---

### Task 1: Durable stage scaffold and input lock

**Files:**
- Create: `stages/...R1A.../INPUT_LOCK.json`
- Create: `stages/...R1A.../STAGE_STATE.json`
- Create: `stages/...R1A.../analysis/uncertainty_policy.py`
- Test: `stages/...R1A.../tests/test_uncertainty_policy.py`

**Interfaces:**
- Consumes: R2-R1 node envelope NPZ, event registry, initial state, accepted trial modules.
- Produces: `UncertaintyPolicy`, `build_v_field(policy, envelope)`, `policy_registry()`.

- [ ] Write failing tests for exactly four `v` policies, two `f` endpoints, two energy endpoints, no below-table extrapolation, and 16 unique policies.
- [ ] Run the targeted test and confirm failure.
- [ ] Implement immutable policy records and vectorized `v`/`f` field construction.
- [ ] Run targeted tests and commit the scaffold/input lock.

### Task 2: Event-resolved branch and augmented-energy operator

**Files:**
- Create: `stages/...R1A.../analysis/event_uncertainty_operator.py`
- Test: `stages/...R1A.../tests/test_event_uncertainty_operator.py`

**Interfaces:**
- Consumes: material populations, proper volume, photo owner fields, `v`, `f`, exact Ly-alpha energy, two-photon bounds.
- Produces: `EventFluxResult(population_rhs, pds_flux, ledger_rates, diagnostics)`.

- [ ] Write failing tests for event-sum parity, H/He invariants, photon-count identity, exact Ly-alpha heat/escape ownership, unresolved-energy nonnegativity, and no direct HeI-to-HeIII event.
- [ ] Run tests and confirm failure.
- [ ] Implement explicit nonnegative parent/child event rates using the existing source rate formulas and branch fields.
- [ ] Implement augmented energy rates with separate resolved, unresolved, escaped, chemical, and recombination/collisional owners.
- [ ] Run tests and commit.

### Task 3: MPRK22/SDIRK2 uncertainty trial

**Files:**
- Create: `stages/...R1A.../analysis/uncertainty_trial.py`
- Test: `stages/...R1A.../tests/test_uncertainty_trial.py`

**Interfaces:**
- Consumes: `SecondOrderSDIRKFastTrial`, `EventFluxResult`, one `UncertaintyPolicy`.
- Produces: `UncertaintyTrialResult` with state, microstep ledgers, and failure certificate.

- [ ] Write failing tests proving transactional rollback, all ledger gates, exact-zero support, and deterministic replay.
- [ ] Run tests and confirm failure.
- [ ] Override only RHS/energy ownership paths; retain MPRK22, SDIRK2, owner kernel, forcing, and root solver.
- [ ] Run tests and commit.

### Task 4: Full 48-lane first-interval preflight

**Files:**
- Create: `stages/...R1A.../analysis/run_four_corner_preflight.py`
- Create: `stages/...R1A.../data/lane_summary.csv`
- Create: `stages/...R1A.../data/node_enclosure.npz`
- Create: `stages/...R1A.../data/microstep_ledger.csv.gz`
- Test: `stages/...R1A.../tests/test_preflight_outputs.py`

**Interfaces:**
- Consumes: three shape lanes and 16 uncertainty policies.
- Produces: 48 lane dispositions and final nodewise enclosures.

- [ ] Write output-contract tests before running science.
- [ ] Execute all 48 runs at partition 2048 with streamed evidence.
- [ ] Compute closure maxima and nodewise widths in species fractions and `log T`.
- [ ] Classify each failure without clipping or lane reassignment.
- [ ] Run output-contract tests and commit evidence.

### Task 5: Exact verification and adversarial audit

**Files:**
- Create: `stages/...R1A.../validation/wolfram_four_corner_validation.wl`
- Create: `stages/...R1A.../analysis/exact_validate_four_corner.py`
- Create: `stages/...R1A.../receipts/EXACT_VALIDATION.json`
- Create: `stages/...R1A.../ADVERSARIAL_AUDIT.md`

**Interfaces:**
- Consumes: lane summary and enclosure outputs.
- Produces: symbolic identities, Decimal replay, and red-team disposition.

- [ ] Verify multi-affine corner extrema, photon-count identity, H/He invariants, and augmented energy identity symbolically.
- [ ] Replay representative and extremal rows at Decimal-90 precision.
- [ ] Attack monotonicity assumptions, below-table handling, owner duplication, and uncertainty-gate interpretation.
- [ ] Commit validation receipts.

### Task 6: Durable closeout, registry, bundle, and handoff

**Files:**
- Create/update: stage reports, `MANIFEST.json`, `SHA256SUMS`, compact ZIP.
- Modify: `PROJECT_STATE.json`, `handoff/CURRENT_HANDOFF_PROMPT.md`, `artifacts/registry/ARTIFACT_REGISTRY.json`, `docs/provenance/DURABLE_STAGE_LEDGER.csv`, rec-bianchi lock/receipt.

**Interfaces:**
- Produces: durable verdict, next-stage authorization, incremental Git bundle and verification receipt.

- [ ] Derive verdict strictly from hard gates and uncertainty widths.
- [ ] Update all provenance files in one closeout commit.
- [ ] Run repository verifier, stage tests, file-isolated full suite, hash audit, ZIP CRC, `git diff --check`, and `git fsck --full`.
- [ ] Create annotated tag and incremental bundle; verify it in a prerequisite-only clone.
- [ ] Preserve the worktree for user integration.
