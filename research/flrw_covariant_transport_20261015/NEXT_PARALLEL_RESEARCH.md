# Next parallel research: Unit5 proposal

Status: PROPOSED_AFTER_UNIT4. No new implementation, numerical execution, old-test replay, or full-campaign allocation. Frozen Unit4 files and ZIP remain unchanged.

## Actual evidence

Read Unit3 axbi_driver.rs (SHA256 798440f50e8cd488b48a9fda30f2c0d0b4303c517dfe144a3931648f522f3d8f), axbi_covariant_transport.rs, axbi_parallel.rs and axbi_background.rs from /home/cosmosapjw/REI_UNIT3_CLOSEOUT_20261015_001/source.

Controller-reported Unit4 C10: PASS, cache benchmark speedup 1.698x, uncached background evaluations 1743 -> 135. This is not a full-history or 64-core utilization measurement. CPU adequacy remains OPEN. The proposed post-cache profile has NOT been performed.

The reported five-case 8/8/8/8/32-worker allocation used about 8.2 busy cores and 159 MB RSS; prepare scaling flattened at 32/64 workers. These observations do not isolate the true serial fraction. Extra idle threads or unused RAM allocation are not useful utilization.

## Small next DAG

| Node | Dependencies | Purpose |
|---|---|---|
| FLRW5_SCREEN | Actual five short-case terminal results | Apply unchanged space/time/angular convergence criteria; reuse completed evidence. |
| CACHE4_ADMIT | Existing C10 and Unit4 review | Reuse PASS without replay. |
| NEXT_PARALLEL_CHOICE | CACHE4_ADMIT | Proposed post-cache cost profile, not performed. Select one measured bottleneck. This optional optimization does not block otherwise admitted science. |
| FLRW_FULL_Q0 | FLRW5_SCREEN, CACHE4_ADMIT | Full FLRW abundance/Tgas/proper-time history under the existing authorized resource contract; no allocation made here. |
| BI_SIGNED_SHORT | FLRW5_SCREEN, supported Bianchi backend | Existing q=+/-0.01 with selected resolution and genuinely needed angular refinement; check source support and signed anisotropic transport. |
| BI_FULL_FAMILY | BI_SIGNED_SHORT | Existing q=+/-0.005,+/-0.01 physical-density-fixed family; may overlap q0 full. q0 completion is needed for final comparison, not starting independent trajectories. |
| PROGRESSIVE_REPORT | Any valid preserved history | Abundance versus proper time AND gas temperature; retain time order for nonmonotonic Tgas. |

No dummy cases, arbitrary amplitude enlargement, or refinement merely to occupy hardware. The current inactive_hi_split flag is q=0-only. Do not enable it for Bianchi without separate support; use the general active backend when appropriate. Signed q results are not interchangeable; odd responses are possible.

## Candidate order and grain

1. Reuse cache admission, then inspect post-cache geometry/source/prepare/RHS/Jacobian/output cost before choosing the next change.
2. Four finite-difference Jacobian columns are independent after the baseline residual. Keep each column's positive-perturbation then negative-fallback order and return columns in j=0..3 order. For the seven-RHS pattern, the ideal RHS-only schedule is 7T -> 4T (1.75x). This is an algebraic ideal for that pattern, not measured speedup or whole-step scaling.
3. Prepared absorption node maps are independent. Preserve cell-local compensated sums and original node/species order for global Gamma, heat and event folds. Do not reduce worker partial sums. Scheduling can cost more than these inexpensive maps; select by measured grain.
4. Coarse versus fine branch parallelism is secondary. Half2 depends on half1. Three equal-cost tentative solves have ideal 3T -> 2T (1.5x), not 2x. No measured gain is claimed.

Driver clones share Arc<OrderedWorkerPool>; cloning does not create an independent pool. Do not recursively wait for nested tasks inside the same bounded leaf pool. Bound workers including coordinator effects, and share immutable prepared data rather than copying it per task.

Potential later serial costs visible in source are per-accepted-output directory-size traversal and checkpoint-string formatting. These are profiling candidates, not measured bottlenecks or instructions to alter output/durability.

## Branch physics and accounting

Branches start from independent clones of the same accepted state. Source, photon, gas and thermal ledgers are private. The coordinator evaluates existing error_metric(full,half2) once and commits half2 only; never sum coarse and fine ledgers.

Current adaptive_step runs coarse first and does not launch fine after coarse failure. Speculative parallel execution therefore cannot preserve identical actual work counts for all failures. Count every actual tentative/RHS, including discarded sibling work; distinguish speculative debit from the serial-equivalent logical path. Keep error precedence coarse, half1, half2 deterministic. Use serial fallback near caps. If exact serial launched-work counts are required even on failure, keep branches serial.

For successful joined trials with unchanged arithmetic, require bitwise equality of physical arrays, gas, proper-time geometry, physical ledgers, local metric, acceptance and next-step decisions. Exclude wall time, scheduling and deliberately separate execution-accounting fields. Each artifact retains its own source binding. Physics equality and operational-accounting equality are distinct.

## Resources and stopping

Retain aggregate 64 CPU and 112 GiB; no RAM filling. Full cases share the existing first-full-start 43200 s deadline and closeout reserve. Resume or a new case does not reset this deadline. Five-case convergence precedes any new full-family allocation. Do not reintroduce the superseded two-case cap.

## R1-R10 status

- R1 COMPLETE: useful utilization scoped to frozen FLRW-to-axisymmetric goals.
- R2 COMPLETE: actual source read and existing measured evidence reused.
- R3 COMPLETE: state, counter, reduction and temporal dependencies identified.
- R4 COMPLETE: cache first, then one measured remaining bottleneck.
- R5 COMPLETE: dependency DAG and branch/Jacobian ideal schedules derived.
- R6 SOURCE_REVIEW_ONLY: invariance/accounting reasoning checked against code; no new numerical or symbolic validation.
- R7 PROPOSED_NOT_PERFORMED: post-cache profile and new algorithm tests.
- R8 PROPOSAL_ONLY: no new scientific admission; CPU adequacy OPEN.
- R9 CONTRACT_SUPPLIED: deterministic folds, independent branch states, complete actual-work accounting.
- R10 PRESERVED_PROPOSAL: separate next-unit documents; no frozen Unit4 mutation or new ZIP cycle.
