# Affine Taylor Continuous Branch Enclosure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Determine whether a low-rank affine/quadratic Taylor parameterization can certify the full source-safe continuous branch family, and identify the smallest next representation if it cannot.

**Architecture:** Separate the source-safe node-local branch family from a two-global-parameter coherent-field auditor. Compute the exact instantaneous sensitivity-rank lower bound for the source-safe family, run all-lane coherent quadratic endpoint audits, and preserve an adversarial node-local trajectory that tests whether coherent corners enclose independent branch choices.

**Tech Stack:** Python 3, NumPy, existing MPRK22/SDIRK2 thermochemistry, Wolfram exact algebra, Git durable artifacts.

## Global Constraints

- Metric signature `(-,+,+,+)` and `epsilon_123=+1`.
- Keep `c`, `hbar`, and `k_B` explicit.
- Preserve the 26-event registry, owner law, exact He II Ly-alpha heating, and unresolved OTS energy ledger.
- No clipping, post-hoc lane selection, fitted branch interpolation, recombination surrogate, CAMB transfer, or Bianchi feedback.
- A coherent two-parameter field is an auditor axiom, not the source-safe admissible family.

---

### Task 1: Lock inputs and claim boundary
- [x] Hash the prerequisite stage, four-corner endpoints, event operator, and trial solver.
- [x] Create `INPUT_LOCK.json`, `STAGE_STATE.json`, and the research contract before calculation.

### Task 2: Build source-safe parameter-rank audit
- [ ] Derive the local `v_i` and `f_i` sensitivity columns from the event graph.
- [ ] Prove the node-block rank formula and count a robust numerical lower bound.
- [ ] Store rank, support, and memory estimates.

### Task 3: Build coherent quadratic auditor
- [ ] Run a locked 3x3 global `(alpha,beta)` grid in all three shape lanes.
- [ ] Fit the total-degree-two endpoint polynomial and test withheld interior points.
- [ ] Record residual envelopes without calling them a validated source-safe enclosure.

### Task 4: Construct adversarial independent-field witness
- [ ] Select node-local lower/upper branches from the signed source sensitivity.
- [ ] Integrate the witness with the unchanged production thermochemistry operator.
- [ ] Test membership in the coherent global-corner envelope.

### Task 5: Decide and seal
- [ ] Apply the predeclared source-safe/coherent claim gate.
- [ ] Update project state, handoff, registry, durable ledger, hashes, and compact bundle.
- [ ] Run fresh verifier, stage tests, full isolated suite, bundle fetch, and Git integrity checks.
