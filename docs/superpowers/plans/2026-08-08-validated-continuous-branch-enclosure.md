# Validated Continuous Branch Enclosure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Certify a continuous-parameter enclosure for the first locked microstep of the state-dependent full-OTS H/He thermochemistry differential inclusion, or fail closed with a quantitative enclosure certificate.

**Architecture:** First construct a decisive signed-Jacobian audit for constant orthant monotonicity. If that fails, reduce each node to the invariant coordinates `(x_HII, x_HeII, x_HeIII, log_T)` and propagate a directed-rounding interval enclosure of the exact continuous RHS. Authoritative PCHIP forcing is bounded by exact polynomial extrema; global owner normalization is kept as a low-rank interval coupling; Hummer--Seaton topology events are localized or fail closed.

**Tech Stack:** Python 3, NumPy, SciPy PCHIP/PPoly, custom outward-rounded interval arithmetic, existing 46,080-node owner/event/thermal source, Wolfram symbolic checks, Decimal/mpmath independent replay.

## Global Constraints

- Metric signature `(-,+,+,+)`, `epsilon_123=+1`, explicit `c`, `hbar`, `k_B`.
- Keep the 26-event registry, MPRK22(1), Alexander-SDIRK2, canonical BDF forcing, owner law, exact He II Ly-alpha heating, and unresolved OTS energy ledger unchanged.
- No clipping, source-table extrapolation, owner reassignment, `kappa=J/Phi` constitutive inversion, cloud/geometry inversion, per-node fitting, post-hoc lane selection, numerical `rec_bianchi` import, or surrogate.
- The validated width gate is `2e-3` in `x_HII`, `x_HeII`, `x_HeIII`, and `log_T`.
- Current 24 trajectories are regression endpoints only.

---

### Task 1: Durable pre-calculation lock

**Files:** Create stage scaffold, `INPUT_LOCK.json`, `STAGE_STATE.json`, research-contract files, and initial `SHA256SUMS`.

- [ ] Hash all load-bearing inputs and both research-harness and remote-head evidence.
- [ ] Record hypotheses: constant orthant monotonicity, mixed/interval enclosure pass, wrapping failure, and table-event failure.
- [ ] Commit before any enclosure calculation.

### Task 2: Constant-cone monotonicity audit

**Files:** Create `analysis/monotonicity_audit.py`; test in `tests/test_monotonicity_audit.py`.

- [ ] Write a failing test requiring a robust sign-change witness for at least one off-diagonal reduced-state Jacobian entry.
- [ ] Evaluate the exact source RHS with owner normalization at canonical states and finite, symmetry-preserving perturbations.
- [ ] Emit node IDs, temperatures, derivative signs, margins, and a signed-graph certificate.
- [ ] Conclude only whether a constant diagonal orthant cone is excluded; do not claim exclusion of all nonlinear cones.

### Task 3: Directed-rounding interval primitives and forcing bounds

**Files:** Create `analysis/interval_arithmetic.py`, `analysis/pchip_bounds.py`; tests for every operation and exact polynomial extrema.

- [ ] Implement outward-rounded scalar/vector interval add, subtract, multiply, divide, power, exp, log, sqrt, min/max, sum, and hull.
- [ ] Bound each first-microstep PCHIP forcing component by endpoint and derivative-root extrema over every covered polynomial segment.
- [ ] Verify sampled forcing lies inside each certified bound and serialize extrema receipts.

### Task 4: Reduced invariant RHS interval extension

**Files:** Create `analysis/reduced_interval_rhs.py`; tests for point-degenerate parity and identity preservation.

- [ ] Use `x_HII`, `x_HeII`, `x_HeIII`, `log_T`; reconstruct populations from immutable H/He nuclei totals.
- [ ] Derive explicit-owner node currents with analytic cancellation of global species-measure factors.
- [ ] Implement interval collisional/recombination/event fluxes, exact multi-affine branch ranges, primary and Ly-alpha heating, cooling, expansion, unresolved and escaped-energy rates.
- [ ] Require degenerate intervals to reproduce the floating source RHS within `5e-12` relative and preserve H/He identities structurally.

### Task 5: Validated interval-Picard flow enclosure

**Files:** Create `analysis/validated_enclosure.py`; tests for scalar analytic ODEs, topology events, rollback, and the project microstep.

- [ ] Use recursive time subdivision with an a-priori Picard tube inclusion test.
- [ ] Propagate endpoint boxes with outward rounding; recenter at every accepted substep.
- [ ] Detect Hummer--Seaton knot intersections; localize by bisection until the event-time box satisfies the locked tolerance, otherwise fail closed.
- [ ] Preserve positivity and exact invariant coordinates; record wrapping inflation, rejected substeps, and maximum tube width.

### Task 6: Independent validation and decision gate

**Files:** Create `analysis/independent_validate_enclosure.py`, Wolfram script, data ledgers, formalism and verdict documents.

- [ ] Compare all 24 regression endpoints and an interior sampling auditor against the certified box.
- [ ] Check all three shape lanes; prove or explicitly condition material-state lane independence on the subgrid exact-zero source.
- [ ] Verify photon, resolved thermal, unresolved OTS, escaped, and total-energy enclosure ledgers.
- [ ] Authorize the uncertainty-qualified first canonical interval only if the continuous certificate is valid and every width is `<2e-3`.

### Task 7: Durable packaging and verification

**Files:** Update project state, current handoff, durable ledger, registry; create compact ZIP, annotated tag, and incremental bundle.

- [ ] Run repository verifier, stage tests, file-isolated full suite, exact validator, SHA audit, ZIP CRC, `git diff --check`, and `git fsck --full`.
- [ ] Fetch the incremental bundle into a prerequisite-only checkout and rerun verifier and stage tests.
- [ ] Preserve all failed attempts and do not claim remote push.
