# R2B-R2A-R2-R1A Four-Corner Propagation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Propagate all source-safe full-OTS branch corners through the validated second-order thermochemistry microstep, close population/photon/total-energy ledgers, and decide the predeclared uncertainty gate without post-hoc lane selection.

**Architecture:** Add a self-contained durable stage that imports the previous event registry and second-order solver as immutable oracles. A branch-kernel module constructs source-safe per-node lane arrays; an event-flux module emits nonnegative reaction fluxes and energy owners; a propagation driver runs full/two-half microsteps and computes load-bearing enclosures. Existing production modules are not modified.

**Tech Stack:** Python 3, NumPy, pandas only for evidence tables, existing JAX-backed microphysics oracle, MPRK22(1), Alexander SDIRK2, SymPy/Decimal, Wolfram validation script, pytest, Git/SHA-256/ZIP.

## Global Constraints

- Metric `(-,+,+,+)` and `epsilon_123=+1`.
- Keep `c`, `hbar`, and `k_B` explicit.
- No clipping, owner reassignment, `kappa=J/Phi` inversion, geometry inversion, per-node fitting, post-hoc lane selection, recombination surrogate, CAMB transfer, or Bianchi feedback.
- The four source-safe corners are load-bearing; log-linear table adapters are auditors only.
- Production node chemistry remains unauthorized unless every load-bearing lane and the predeclared uncertainty gate pass.

---

### Task 1: Durable Precalculation Lock

**Files:**
- Create: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_FOUR_CORNER_BRANCH_AND_UNRESOLVED_OTS_ENERGY_PROPAGATION_PREFLIGHT/INPUT_LOCK.json`
- Create: same stage `STAGE_STATE.json`, `RESEARCH_CONTRACT.md`, `00_READ_FIRST.md`, `receipts/REMOTE_READ_ONLY_RECEIPT.json`
- Modify: `docs/superpowers/specs/2026-08-08-r2b-r2a-r2-r1a-four-corner-propagation-design.md`

**Interfaces:**
- Consumes: prerequisite commit `893d2e06f6a32015603087881933e4763f00d2cb` and exact hashes of prior-stage data/code.
- Produces: immutable input lock with `calculation_started=false` and all numerical/uncertainty gates.

- [ ] Hash every input listed in the design, including the research harness and current remote receipts.
- [ ] Write the input lock before any propagation result is computed.
- [ ] Validate the research harness with `tools/validate_workspace.py` in a temporary extraction.
- [ ] Commit the precalculation lock.

### Task 2: Branch Lane Generator

**Files:**
- Create: stage `analysis/branch_lanes.py`
- Test: stage `tests/test_branch_lanes.py`

**Interfaces:**
- Produces: `BranchLaneSet` with arrays `v`, `f`, `load_bearing`, `lane_id`, `table_domain`, and exact semantic lane names.

- [ ] Write failing tests for below-table four-corner completeness, table-cell endpoint corners, two log-linear adapter lanes, exact knot semantics, and nonnegative branch multiplicities.
- [ ] Run the focused tests and confirm RED.
- [ ] Implement table bracketing and log-linear interpolation in `log10(T/K)` without extrapolation.
- [ ] Run the focused tests and confirm GREEN.
- [ ] Commit the lane generator.

### Task 3: Event-Resolved Branch Flux and Energy Ledger

**Files:**
- Create: stage `analysis/event_flux.py`
- Test: stage `tests/test_event_flux.py`

**Interfaces:**
- Consumes: material state, proper volume, owner-correct photo events, per-node `v,f`, and locked atomic rate functions.
- Produces: nonnegative event flux tensor, reconstructed five-species RHS, resolved Ly-alpha heating, unresolved OTS energy bounds, escaped energy, and owner certificates.

- [ ] Write failing tests for event-sum parity, H/He invariants, no direct He I to He III event, exact Ly-alpha ownership, two-photon bound ordering, and zero duplicate/unowned energy owners.
- [ ] Run focused tests and confirm RED.
- [ ] Implement the six parent recombination channels and existing ionization channels with the locked 26-event topology.
- [ ] Implement exact Ly-alpha energy ownership and unresolved-energy bookkeeping.
- [ ] Run focused tests and confirm GREEN.
- [ ] Commit the event/energy operator.

### Task 4: Branch-Aware Second-Order Microstep

**Files:**
- Create: stage `analysis/branch_trial.py`
- Test: stage `tests/test_branch_trial.py`

**Interfaces:**
- Consumes: existing `SecondOrderSDIRKFastTrial` inputs and the event-flux callback.
- Produces: branch-aware `SecondOrderTrialResult` plus resolved, unresolved, escaped, chemical, and total-energy ledger residuals.

- [ ] Write failing tests showing the legacy branch functions are not called, parent bytes survive rejection, and one synthetic lane preserves positivity/nuclei/photon/energy.
- [ ] Run focused tests and confirm RED.
- [ ] Implement a branch-aware subclass that replaces only the population/OTS heating callback while retaining owner law, MPRK22, SDIRK2, and forcing.
- [ ] Implement total-energy residual from resolved thermal, chemical binding, unresolved OTS, escaped radiation, and photon ledgers.
- [ ] Run focused tests and confirm GREEN.
- [ ] Commit the microstep implementation.

### Task 5: Full Corner Propagation and Enclosure Decision

**Files:**
- Create: stage `analysis/run_four_corner_preflight.py`
- Create: stage `data/BRANCH_LANE_REGISTRY.csv`, `data/MICROSTEP_RESULTS.csv.gz`, `data/ENCLOSURE_SUMMARY.json`, `results.json`
- Test: stage `tests/test_preflight_results.py`

**Interfaces:**
- Produces: full/two-half certificates for three shape lanes, all load-bearing corners, adapter auditors, and final uncertainty verdict.

- [ ] Run partition-2048 full/two-half trials for all lanes without selecting or pruning corners.
- [ ] Verify every hard numerical gate and record earliest failure certificates.
- [ ] Compute nodewise widths for `x_HII`, `x_HeII`, `x_HeIII`, and `log T` using load-bearing lanes only.
- [ ] Apply the predeclared `2e-4` uncertainty gate.
- [ ] Write tests that replay counts, gate logic, and no post-hoc lane selection.
- [ ] Commit the scientific results.

### Task 6: Exact Validation, Harness Closeout, and Durable Seal

**Files:**
- Create: stage `validation/wolfram_four_corner_validation.wl`
- Create: stage `analysis/exact_validate_four_corner.py`
- Create: stage phase documents `01_RESEARCH_CONTRACT.md` through `10_CLOSEOUT_AND_HANDOFF.md`
- Create: stage `MANIFEST.json`, `SHA256SUMS`, compact ZIP, receipts, and `NEXT_STAGE_PROMPT.md`
- Modify: `PROJECT_STATE.json`, `handoff/CURRENT_HANDOFF_PROMPT.md`, `docs/science/current_00_READ_FIRST.md`, `docs/provenance/DURABLE_STAGE_LEDGER.csv`, `artifacts/registry/ARTIFACT_REGISTRY.json`

**Interfaces:**
- Produces: durable pass or fail-closed stage, next-stage authorization, annotated tag, and incremental bundle.

- [ ] Verify multi-affine corner completeness, branch identities, nuclei invariants, and energy-owner identities in Wolfram.
- [ ] Replay stored summaries with SymPy/Decimal at high precision.
- [ ] Run repository verifier, stage tests, file-isolated full suite, stage SHA audit, ZIP CRC, `git diff --check`, and `git fsck --full`.
- [ ] Update all project/provenance files in the same science commit.
- [ ] Create annotated tag and incremental Git bundle; verify the bundle in a prerequisite-only clone.
- [ ] Preserve all failed attempts separately and leave the source worktree clean.
