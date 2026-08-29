# rei_bianchi First Canonical Interval Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use Superpowers subagent-driven-development or executing-plans task-by-task. Every task below ends in a separately testable commit.

**Goal:** Turn the accepted partition-2048 four-site FLRW thermochemistry microstep into an uncertainty-qualified adaptive history over the complete first canonical BDF interval.

**Architecture:** A bounded compatibility pass first checks whether the inactive four-loop ODE audit findings reproduce in the active dependency path. The interval driver then applies transactional full-versus-two-half acceptance over all three lanes, bisecting only failed attempted steps and localizing Hummer–Seaton events before commit. `rec_bianchi` is consumed only as an exact monitoring/checkpoint dependency; no numerical recombination history enters this stage.

**Tech stack:** Python 3, NumPy/Pandas, existing node-resolved thermochemistry/history owners and durable-stage validators.

**Spec:** `handoff/CURRENT_HANDOFF_PROMPT.md`, `docs/science/current_00_READ_FIRST.md`, and this package's `PACKAGE.json`.

## Global constraints

- Exact source base: `ace7d91af35bfefcc3a9bd7e83076aa8f8bf557e`.
- Start from the certified partition `2048` microstep; all three lanes are mandatory.
- Width budget `2e-3`; full-versus-two-half local-error budget `2e-4`.
- No clipping, table extrapolation, favorable-lane selection, new minimum step, rec numerical import, CAMB, or Bianchi sweep.
- Independent state/observable replay is required; no unjustified error-of-error comparison.
- One bounded audit-compatibility pass plus at most one repair, then proceed to the interval in the same run.
- One PHYS-MATH and one PHYS-MATH-CODE review; at most one reproduced P0/P1 repair.

---

### Task 1: Active-code ODE audit compatibility

**Files**
- Create: `stages/...FIRST_CANONICAL_INTERVAL.../audit_compatibility/ACTIVE_FINDINGS.json`
- Test: directly affected active modules and audit-shadow negative cases

- [ ] Map each 8/23 shadow finding to an active dependency or `INACTIVE_NOT_APPLICABLE`.
- [ ] Reproduce resource-ceiling, descendant-capture, recorder-preimage, absorber-inventory and certificate-replay findings against active code.
- [ ] Patch only reproduced active defects; never copy the candidate wholesale.
- [ ] Run the focused compatibility selector and commit.
- [ ] Continue immediately to Task 2 if the terminal is `PASS_REI_ACTIVE_ODE_COMPATIBILITY`.

### Task 2: Exact rec monitoring lock

**Files**
- Modify: `external/rec_bianchi.lock.json`
- Modify: stage input lock in the new interval directory

- [ ] Bind exact rec main/audit/package identities supplied by this bootstrap.
- [ ] Assert `contains_astrophysical_reionization=false`.
- [ ] Assert numerical history/rate/population import and surrogate are forbidden.
- [ ] Commit the metadata-only lock.

### Task 3: Adaptive first-interval driver

**Files**
- Modify or create under: `src/rei_bianchi/`
- Test under: active first-interval stage tests
- Create: durable stage skeleton, receipts and manifest under `stages/`

**Interfaces**
- `attempt_step(parent, dt, lane) -> AttemptReceipt`
- `accept_attempt(full, half2, gates) -> AcceptedStep | RejectedStep`
- `run_first_canonical_interval(initial, locked_minimum_dt) -> IntervalHistory`

- [ ] For every lane and attempt compute one full and two half images.
- [ ] Apply implicit, positivity, width, structural-ledger and local-error gates.
- [ ] Bisect only the failed attempted step to the already locked minimum.
- [ ] Localize every Hummer–Seaton knot before commit.
- [ ] Preserve parent state and ledger bytes for rejected attempts and table crossings.
- [ ] Record rank, owner modes, remainder growth, event distance and transactions.
- [ ] Commit the interval driver.

### Task 4: Independent interval proof

- [ ] Replay accepted steps independently and compare state and observables.
- [ ] Check width, positivity, local error and all seven ledgers per step and globally.
- [ ] Demonstrate refinement convergence without requiring secondary error estimators to match unrealistically.
- [ ] Run hostile mutations: favorable-lane selection, stage collapse, ledger-owner drop and nontransactional event commit.
- [ ] Commit durable evidence.

### Task 5: Review and draft delivery

- [ ] Run one PHYS-MATH and one PHYS-MATH-CODE review.
- [ ] Repair only a reproduced P0/P1 defect, at most once.
- [ ] Seal the durable stage artifact and typed identity report.
- [ ] Ordinary-push one draft PR against `audit/ode-four-loop-external-20260823`.
- [ ] Read back exact head/tree/path/evidence and stop.
