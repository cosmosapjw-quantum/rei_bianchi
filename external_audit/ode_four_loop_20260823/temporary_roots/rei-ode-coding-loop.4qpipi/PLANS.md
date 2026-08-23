# PLANS

## Current task and authority

- **Task:** research the preceding mathematical/algorithmic/coding remedies as unverified seeds against bound REI Bianchi ODE code.
- **Outcome sought:** one smallest-sufficient implementation candidate specification, or justified no-selection.
- **Authorized:** diagnose, design, small read-only probes, current diagnostic tests, primary/official source reconciliation, independent design review.
- **Not authorized:** repository edits; implementation; dependency, tolerance, convention, schema, baseline, or reference changes; production/history/parity/package/BDF runs; promotion of software or science.

## Path aliases

All aliases are repository-relative stage directories.

- `A`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY`
- `P`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK`
- `V`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_VALIDATED_CONTINUOUS_BRANCH_DIFFERENTIAL_INCLUSION_ENCLOSURE_LOCK`
- `C`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_EVALUATION_SITE_SPARSE_GENERATOR_VALIDATED_MPRK22_SDIRK2_DISCRETE_MAP_ENCLOSURE_LOCK`
- `S`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_SPARSE_LOCAL_GENERATOR_AFFINE_TAYLOR_MODEL_ENCLOSURE_LOCK`
- `R2A`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_ADAPTIVE_INTERNAL_MICROSTEP_ACCEPTANCE_AND_GLOBALIZATION_LOCK`
- `U`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_FOUR_CORNER_BRANCH_AND_UNRESOLVED_OTS_ENERGY_PROPAGATION_PREFLIGHT`
- `B`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R1_CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK_RERUN_V2`
- `N` (proposed; does not exist and cannot be created without authorization): `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_R1_LCV_ODE_CORRECTED_SCIENCE_V2_CANDIDATE`

`A/P/V/C/S/R2A/U/B` are immutable forensic/predecessor bindings. Every future write named below is under `N`; references to predecessor files describe wrapped inputs, characterization targets, or imported interfaces—not in-place edits.

## M-04 candidate comparison — maximum three

| Criterion | H1: localized numerical patch | H2: layered contract/validation-first repair | H3: replacement solver/controller/reference stack |
|---|---|---|---|
| Core change | Fix He II formula, interval sum/Krawczyk, labels, and focused tests in place. | Introduce verified arithmetic/certificate, typed admission, error/event, controller/custody, and reference-lane seams as dependency-ordered patches. | Replace current hybrid interval map and operational stack with a new validated-IVP architecture. |
| Prediction | Arithmetic/formula fixes close all false success without architecture changes. | Existing algorithms remain where valid, but no result crosses a boundary without explicit proof/admission contracts. | Only a clean rewrite can express required guarantees coherently. |
| Frozen coverage | Directly addresses 1–8, 12–13, 32; cannot by itself supply active continuous error/event/restart, independent reference, or cross-process custody for 9–11, 14–17, 19–31. | Inventories all IDs 1–32 and S-01–S-12; conditionally targets 31 correctness/custody blockers, while #18/S-07 is a separately gated nonblocking performance opportunity. #19 is `PARTIAL_NARROWED`. | Could cover the same scope, but only after recreating all compatibility, physics, custody, and historical interfaces. |
| Falsifier result | **FALSIFIED:** blockers 9–11, 14–17, 19–31 intrinsically cross trajectory, controller, reference, process, and package boundaries. | Not falsified by current source map: patch seams exist and can retain the dense/current path as characterized fallback. Final selection remains subject to independent review. | **FALSIFIED AS NECESSARY:** H2 can be expressed as bounded interfaces/slices without replacing the current solver wholesale. H3 remains contingency if a future H2 characterization seam proves impossible. |
| Numerical risk | High: makes local green likely while leaving global/event/custody false-success paths. | Medium, controlled by fail-closed defaults, exact witnesses, dense fallback, and per-slice rollback. | Very high: new discretization and lineage invalidate broad compatibility and require new scientific validation. |
| Compatibility | Superficially small but unsafe claim compatibility. | Preserves immutable forensic lane; corrected behavior receives new identity/schema version only at an authorized boundary. | Broadly breaking; new baselines and historical mapping required. |
| Complexity/cost | Low code volume, insufficient outcome. | Moderate/high but decomposable; only candidate that is both sufficient in design and smaller than replacement. | Highest implementation and validation cost. |
| Rollback | Easy but returns to known unsafe admission. | Per-slice feature seam; old path remains forensic-only, never scientific fallback after a soundness failure. | Repository-wide rollback and migration burden. |

**Post-review disposition:** H2, named `LCV-ODE` (Layered Contract and Validation repair), is the **conditional smallest-scope candidate architecture** among the three. It is not implementation-ready. It becomes eligible for an implementation plan only after D-01–D-07 below are owner-resolved; no implementability, correctness, performance, compatibility, or scientific validity is established.

## H2 contract architecture

```text
qualified arithmetic + physical domains
  → algebraic certificate / discrete-step candidate
  → independent residual, invariant, error, and event evidence
  → typed AttemptResult admission
  → explicit controller FSM and atomic generation
  → authenticated runtime/process/path/package custody
  → forensic or corrected-reference lineage (never conflated)
```

The one-way rule is decisive: a downstream layer may reject an upstream candidate but may not manufacture missing evidence, coerce an invalid value, or reinterpret `success` from a lower layer as admitted success.

## Dependency-ordered implementation specification

Every slice starts red with the named tests, lands independently, and has a single revert boundary. No slice is authorized in this work unit.

### I-0 — Successor-stage characterization and failure vocabulary

- **Files:** add `N/analysis/result_contract.py`, `predecessor_adapters.py`, `routing.py`; add all tests under `N/tests/`. Read A/P interfaces only through SHA-bound adapters; do not edit predecessor tests or code.
- **Interface:** immutable `AttemptResult(status, state, evidence, diagnostics, identity)`; the closed v2 status taxonomy is exhaustively mapped below. Only controller-produced `ADMITTED_CORRECTED` is consumable success; worker output can reach at most `AWAITING_PARITY`.
- **Behavior:** characterize current outputs and transitions first; require finite/schema/domain/residual/event/invariant/diagnostic predicate truth before admission. Missing evidence is not Boolean false-success.
- **Tests:** golden current compatibility; one mutation test per predicate/status transition; unknown enum/schema; partial diagnostics; NaN/Inf/overflow; attempt-output-to-controller boundary.
- **Rollback:** remove/disable N routing as one slice and retain N diagnostics as quarantined evidence; A remains byte-identical. Old Boolean success remains forensic/diagnostic-only, never an authorized scientific fallback.

### I-1 — Successor-stage verified arithmetic, formula, constraints, and certificates

- **Files:** add `N/analysis/verified_backend.py`, `corrected_interval_arithmetic.py`, `corrected_physics.py`, `certificate_adapter.py`, and `corrected_discrete_map.py`, plus exact/property/differential tests under `N/tests/`. V/R2A/P/C are immutable characterization/reference inputs.
- **Arithmetic contract:** basic operations and sums enclose exact real results, including signed cancellation, subnormals, overflow, zero, infinities, and domain endpoints. Use error-free/exact/reproducible reduction plus final directed conversion; every elementary function is delegated to a named, version-qualified outward-rounded backend. If no such backend is owner-approved, return `CERTIFICATE_UNAVAILABLE`—never heuristic proof.
- **Krawczyk contract:** check dimensions/finiteness; build a verified residual and Jacobian interval enclosing all derivatives over the box; use a verified approximate inverse; form the full interval operator with outward matrix products; issue unique-root success only for strict interior inclusion. Recompute residual/enclosure independently at the consumer; failure is inconclusive, not nonexistence.
- **Physics/constraint behavior:** derive He II attenuation once from absorber number density (remove the duplicate `YHE` only in a new corrected lane); compute 54 eV shares as nonnegative opacity ratios, not a subtractive complement; represent closed H/He simplex faces and exact vacuum/trace as explicit regimes, not silent floors/logs/logits/projections.
- **Tests:** the E-003/E-004/E-005 witnesses; exact-rational and high-precision differential corpora; monotonicity/inclusion metamorphisms; ill-conditioned, zero-denominator, nonexistence, and mutation cases; pure-H/pure-He I/pure-He II/vacuum/trace limits; complement near 0/1; declared convention/units.
- **Rollback:** disable N's verified-kernel route and quarantine the N generation; any containment failure disables corrected certificate admission globally. A forensic v1 result may still be reproduced under its old label but cannot be promoted as a fallback. Dependency or convention choice is blocked by D-01/D-02.

### I-2 — Successor-stage independent physics ledgers and error hierarchy

- **Files:** add `N/analysis/independent_ledgers.py`, `error_evidence.py`, `hybrid_step_certificate.py`, and v2 worker/policy adapters; add manufactured/reference tests under `N/tests/`. P/A stay read-only.
- **Behavior:** rename current full-step/two-half-step distance to `step_discrepancy`; never label it LTE. Independently accumulate incident, escaped, and absorbed photons and radiative input, ionization potential, heating/cooling/work, and internal-energy change from primitive quantities. Construct a branch-consistent dense reconstruction, continuous defect `delta(t)=y_tilde'(t)-f(t,y_tilde)`, a stated stability/duality propagation, event-time error, and adjoint/QoI contribution for owner-selected observables.
- **Separation:** algebraic solve residual, discrepancy, LTE/order evidence, continuous defect, global trajectory error, event-time error, and QoI error have distinct fields/units/budgets. An unproved estimator is `UNESTABLISHED` and cannot gate as a bound.
- **Tests:** manufactured solutions with known local/global/QoI error; refinement/order studies; independent primitive-ledger mutation tests; scale/unit tests; stiff and near-boundary cases; reference-bound coverage, not mere estimate agreement.
- **Rollback:** ledgers/error evidence remain shadow-only while D-03/D-04 or tests are open. Corrected-lane admission is structurally impossible—not merely discouraged—until I-1/I-2/I-3/I-5/I-6 reach `ESTABLISHED`. Failure leaves A and its history unchanged.

### I-3 — Successor-stage all-root hybrid events and conservative restart

- **Files:** add `N/analysis/validated_event_locator.py`, `event_transition.py`, and v2 worker/controller adapters, using P's disconnected localizer/audit only as characterized predecessor evidence; add all-root/restart tests under `N/tests/`.
- **Algorithm:** isolate all simple roots of every event function over the dense step representation; use interval bounds for `g` and total derivative `dg/dt`; order/coalesce roots only under an explicit priority policy. If tangency/multiplicity/simultaneity or dense-output error prevents certification, bisect/retry; after a hard cap return `EVENT_AMBIGUOUS` and stop.
- **Restart:** roll back to the isolated root enclosure, apply the authorized discrete transition, rebuild table/branch rates, forcing, Jacobian, and caches, increment generation, then restart from the post-event state. No ordinary projection hides violations.
- **Tests:** simple, even-multiplicity/grazing, two/many/near-coincident, endpoint and direction-filter roots; step-partition/time-shift metamorphisms; priority ambiguity; crash at every rollback/rebuild boundary; event time and post-event invariant checks.
- **Rollback:** disable N routing and quarantine N generations; never route a corrected candidate into A's endpoint-only path. A detected but unresolved v2 event remains a typed blocked N result.

### I-4 — Nonblocking sparse/low-rank performance opportunity after dense correctness

- **Files:** add `N/analysis/structured_linear_solve.py` and N-local dense-vs-structured tests/benchmarks; S is an immutable derivation input.
- **Algorithm:** on a verified fixed smooth branch only, factor the Jacobian as block-local `B + U V^T`, with nonlocal right-factor span derived from the three global absorber sums and audited rank `<=3`; solve local blocks and the small Schur/Woodbury system exactly relative to the same candidate model.
- **Guards:** certify/estimate conditioning of local blocks and `I+V^T B^{-1}U`, verify full residual/backward error and physical/interval predicates, and use the dense implementation as the correctness fallback on rank, branch, conditioning, or residual failure. Never use approximate truncation to force rank three.
- **Tests/performance:** randomized admissible-state differential tests; exact factorization/rank mutation; near-singular Schur cases; interval containment; branch-event exclusion; preregistered wall/memory scaling versus dense baseline.
- **Coverage status:** #18/S-07 is inventoried but reclassified as a nonblocking performance opportunity. It is not counted among the 31 mandatory correctness/custody closure obligations. It becomes mandatory only for a separate performance-promotion claim.
- **Rollback:** optional performance slice; removing it leaves the corrected dense path unchanged. No performance claim without benchmark receipts.

### I-5 — Successor-stage controller FSM, runtime, bounded subprocess, and atomic state

- **Files:** add `N/analysis/controller_fsm.py`, `state_io_v2.py`, `runtime_contract_v2.py`, `preflight_v2.py`, and `bounded_process.py`, with v2 tests. Reuse A's proven primitives only through SHA-bound adapters; do not mutate A.
- **FSM:** explicit legal transitions among new/running/retry/event/terminal states; terminal states are absorbing. `resume` continues an incomplete identical generation, `restart` creates a new child generation, and `new` has no parent. Atomic write-then-fsync-then-rename plus generation/parent compare-and-swap prevents partial or competing commits.
- **Runtime/process:** bind container/image or host identity; interpreter realpath/hash; Python SOABI; package metadata/RECORD and loaded shared-library hashes; libc/libm; BLAS/LAPACK vendor/build; CPU features; floating-point rounding, FTZ/DAZ/FMA behavior; affinity/thread counts and environment; locale/timezone/kernel; source/config/input/forcing hashes; resolved tool hashes/versions; command/output identities. Replace all-at-once `capture_output` with continuously drained bounded streams, byte/line quotas, wall timeout, process-group termination, bounded diagnostic tail, and explicit `RESOURCE_EXHAUSTED`.
- **Forecast:** preflight hard caps for attempts/workers/memory plus wall time, disk, inode, log, package, and ancestry work; record estimated versus actual resources.
- **Tests:** exhaustive/property FSM transitions; resume terminal/partial/stale/concurrent generations; crash injection at each atomic-write phase; wrong PATH/tool/runtime/input; child flood/hang/fork tree; quota and cleanup checks; deterministic rerun.
- **Rollback:** N controller/runtime cannot be partially enabled. On identity/state/resource uncertainty, fail before work or return typed failure; never resume through a warning and never fall back to A as corrected science.

### I-6 — Successor-stage package containment, authenticated parity, and linear ancestry

- **Files:** add `N/analysis/package_results_v2.py`, `containment.py`, `parity_admission.py`, and v2 state/ancestry modules and tests. A packager/parity/state code remains immutable forensic behavior.
- **Containment:** explicit generation allowlist; descriptor-anchored/no-follow traversal; reject absolute, `..`, symlink/hardlink/device/FIFO and race-swapped members; stream hashing/archiving under per-member and aggregate quotas; verify manifest postimage before admission.
- **Parity/ancestry:** parity receipt binds candidate, validator, numerical ABI manifest, source, inputs, outputs, diagnostics, and controller head. The v2 controller alone consumes that receipt and atomically transitions `AWAITING_PARITY → ADMITTED_CORRECTED` or `PARITY_REJECTED`; a standalone file cannot confer authority. Store authenticated parent hash and incremental/indexed ancestry so validation is O(1) per append and O(n) total, with explicit cycle/fork detection.
- **Tests:** traversal/symlink/hardlink/race corpus; wrong-generation and swapped-output negatives; malformed/cyclic/forked ancestry; large files/logs and quota termination; complete postimage reconstruction.
- **Rollback:** N packaging cannot run from a partial generation. Any mismatch aborts artifact creation and preserves quarantined N diagnostics without authority; A remains untouched.

### I-7 — Immutable forensic BDF lane and successor-stage corrected reference

- **Files:** leave B inputs/outputs and R2A forcing immutable; add `N/analysis/corrected_reference.py`, `reference_admission.py`, and independent oracle tests, all under the N identity and owner-approved lineage.
- **Corrected lane:** explicit interpolation domain/extrapolation policy; finite/domain/expected-terminal/residual/physical-invariant admission; analytic/manufactured limiting cases and an independently assembled primitive-flux oracle; exact runtime/input/output identity.
- **Rules:** same-code replay and legacy expected output are forensic compatibility evidence only. The corrected lane cannot overwrite or silently substitute legacy forcing. Current downstream promotion remains blocked until corrected reference, uncertainty impact, and owner-selected scientific budgets are admitted.
- **Tests:** out-of-domain/extrapolation, early solver termination, nonfinite/partial output, independently known solutions, cross-lane substitution negatives, lineage and uncertainty propagation.
- **Rollback:** N is additive and route-disableable. Historical BDF and consumers remain byte-identical; no scientific baseline changes without separate authority.

## Pre-implementation decision gates — all unresolved

Until every gate is resolved in a separately authorized contract, H2 remains `CONDITIONAL_ARCHITECTURE_NOT_IMPLEMENTATION_READY`.

| Gate | Owner decision/evidence required | Fail-closed result while open |
|---|---|---|
| D-01 | Select and qualify a verified arithmetic/elementary-function backend and dependency/version policy on the exact numerical ABI. | No certified arithmetic or Krawczyk success; diagnostic only. |
| D-02 | Fix model-authoritative exact vacuum, trace, simplex-face, floor prohibition, and table-knot ownership semantics. | Boundary/vacuum cases are `DOMAIN_UNRESOLVED`; no coercion. |
| D-03 | Specify the physical norm/scales, branch-correct dense reconstruction, continuous-defect construction, stability/global-error theorem and its hypotheses. | Step discrepancy remains diagnostic; no trajectory bound. |
| D-04 | Name QoIs and quantitative local/global/event/QoI budgets with units and owner authority. | No QoI/scientific admission. |
| D-05 | Specify event functions, true-solution/dense-output error coupling, root completeness regime, grazing/repeated/simultaneous priority and terminal policy. | Possible non-simple event is `EVENT_AMBIGUOUS` and blocks. |
| D-06 | Adjudicate the authoritative rec_bianchi commit (`A/INPUT_LOCK.json` vs `external/rec_bianchi.lock.json`) and freeze full numerical ABI/tool manifest plus exact parity predicate. | Preflight `IDENTITY_UNRESOLVED`; no execution/resume/parity. |
| D-07 | Authorize exact N stage ID, schemas, dependency changes, resource ceilings, worktree, and permitted slice order. | No filesystem implementation work. |

## Successor identity, routing, and rollback contract

- **Stage identity:** N has its own `INPUT_LOCK.json`, `MANIFEST.json`, `SHA256SUMS`, `ROUTING_POLICY.json`, `SCHEMA.md`, `requirements-runtime.txt`, and numerical-ABI manifest. `INPUT_LOCK.json` binds exact A/P/V/C/S/R2A/U/B predecessor paths and hashes, the chosen rec_bianchi identity, all D-01–D-07 decisions, and the H2 spec hash.
- **Schema identities:** `LCV_ATTEMPT_V2`, `LCV_CONTROL_V2`, `LCV_STATE_V2`, `LCV_PARITY_V2`, `LCV_PACKAGE_V2`. V1 readers are allowed only in `FORENSIC_COMPATIBILITY_V1`; v1 bytes are never rewritten into v2 in place.
- **Routing:** `FORENSIC_COMPATIBILITY_V1` routes only to A and retains its original claim ceiling. `CORRECTED_SCIENCE_V2_CANDIDATE` routes only to N. `BLOCKED_EVIDENCE_V2` packages diagnostics under a distinct closed-world manifest and cannot be consumed as a candidate.
- **Rollback:** atomically disable the N route, preserve/quarantine every N generation, and continue to offer read-only v1 forensic reproduction. Rollback never relabels v1 as corrected science and never deletes/reseals/migrates predecessor evidence.

## Slice-state admission dependency

| N slice state | Permitted output | Corrected commit/admission |
|---|---|---|
| `SCHEMA_ONLY` (I-0) | characterized v1 projection and typed diagnostics | forbidden |
| `ARITHMETIC_SHADOW` (I-1) | verified-kernel shadow evidence | forbidden |
| `ERROR_SHADOW` (I-2) | independent ledger/error shadow evidence | forbidden |
| `EVENT_SHADOW` (I-3) | root/restart shadow evidence | forbidden |
| `OPERATIONAL_SHADOW` (I-5/I-6) | ABI/FSM/custody/parity shadow evidence | forbidden |
| `CORRECTED_ELIGIBLE` | only after I-0/I-1/I-2/I-3/I-5/I-6 are `ESTABLISHED`, all D-gates resolved, and aggregate mandatory tests pass | candidate may enter `AWAITING_PARITY`; not yet admitted |
| `REFERENCE_QUALIFIED` (I-7) | independent corrected-reference evidence | required for any scientific promotion, still outside this work unit |
| `PERFORMANCE_QUALIFIED` (I-4) | optional structured-solve performance evidence | irrelevant to correctness admission; required only for performance claims |

No shadow evidence can be treated as a gate pass. `ADMITTED_CORRECTED` requires a controller-consumed authenticated parity receipt after `CORRECTED_ELIGIBLE`; scientific promotion additionally requires I-7 and a separate authority decision.

## Typed status-to-FSM action table

| Typed status | Sole legal controller action |
|---|---|
| `ADMITTED_CORRECTED` | atomically commit and advance; legal only as the controller's successful transition from `AWAITING_PARITY` with the bound receipt |
| `AWAITING_PARITY` | run the one bound validator under the identical manifest; validator emits either `PARITY_CONFIRMED` or `PARITY_REJECTED` |
| `PARITY_CONFIRMED` | controller verifies receipt identity and transitions atomically to `ADMITTED_CORRECTED` |
| `RETRY_STEP` | bisect/retry the same immutable parent within the frozen retry/depth/resource budget |
| `CERTIFICATE_INCONCLUSIVE` | invoke the single qualified dense fallback; it must emit a new terminal/result status |
| `FALLBACK_UNAVAILABLE` | map once to `RETRY_STEP`; no direct commit |
| `EVENT_PENDING` | invoke validated locator/transition/rebuild; publish no candidate state |
| `EVENT_AMBIGUOUS` | map once to `RETRY_STEP` within the event budget |
| `EVENT_BUDGET_EXHAUSTED` | transition to absorbing `BLOCKED_EVENT` |
| `PAUSED_LIMIT` / `PAUSED_ATTEMPT_LIMIT` / `INTERRUPTED` | resume only the identical nonterminal generation and ABI manifest |
| `DOMAIN_ERROR` / `NONFINITE` / `ADMISSION_REJECTED` / `IDENTITY_DRIFT` / `PARITY_REJECTED` | absorbing failure; leave admitted parent unchanged |
| `TRANSIENT_TRANSPORT_FAILURE` | map once to `RETRY_STEP` and consume the frozen retry budget |
| `RESOURCE_EXHAUSTED` / `TRANSPORT_FAILURE` | absorbing failure; leave admitted parent unchanged |
| `TERMINAL_FAILED` / `BLOCKED_EVENT` / `COMPLETE` / `ABORTED` | absorbing; resume forbidden; any restart creates a new run/generation identity |
| unknown/missing/partial status | `BLOCKED_PROTOCOL`, absorbing |

## Milestones and authorization gates

| ID | Milestone | Dependency | Required validation | Status |
|---|---|---|---|---|
| R-01 | Freeze scope/evidence and reproduce exact witnesses | none | E-001–E-014, 32-row crosswalk | Done |
| R-02 | Select H1/H2/H3 research direction | R-01 | coverage/falsifier/file/test/rollback comparison | Done |
| R-03 | Independent design review | R-02 | `PARTIALLY_CONFIRMED`, one review only | Done |
| R-04 | One mandatory-correction/closeout round | R-03 | D-gates, successor routing, admission/FSM, validation, decision, custody/bounded checks | Done |
| X-00 | Owner resolves D-01–D-07 and authorizes isolated implementation | separate request | exact N identity, permitted slices, dependencies, conventions, budgets | Blocked |
| X-01 | Implement I-0 through I-3 in isolated worktree | X-00 | P-01–P-09 | Cancelled |
| X-02 | Implement I-5 through I-7 | X-01 and new authority | P-11–P-14 | Cancelled |
| X-03 | Optional I-4 optimization | dense admitted path and performance authority | P-10 plus benchmark budget | Cancelled |
| X-04 | Aggregate exact-head/software/scientific admission | all authorized slices | P-15 and independent review | Cancelled |

Status vocabulary: `Planned / In Progress / Done / Blocked / Cancelled`.
