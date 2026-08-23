# VALIDATION MATRIX

Statuses describe this research loop only. A proposed implementation check is `NOT_RUN` and cannot inherit a pass from current diagnostics.

## Current-code diagnostics

| ID | Requirement | Check | Level | Expected | Status | Evidence / authority ceiling |
|---|---|---|---|---|---|---|
| C-01 | Bound repository identity | HEAD, tracked diff, exact untracked-name inventory | custody | unchanged | PASS | E-001; recheck required at closeout. |
| C-02 | Existing behavior | 49-test active-stage `unittest` suite | software compatibility | pass | PASS | E-002; diagnostic compatibility only. |
| C-03 | Signed interval containment | exact subnormal cancellation witness | numerical/adversarial | exact sum enclosed | FAIL | E-003. |
| C-04 | Krawczyk enclosure soundness | two known exact linear solutions | numerical/adversarial | `certified` implies containment | FAIL | E-004. |
| C-05 | He II coefficient binding | number-density convention witness | scientific | algebraic identity | FAIL | E-005. |
| C-06 | Runtime identity | live package versions vs runtime contract | reproducibility | exact match | FAIL | E-006. |
| C-07 | Event completeness | current call graph plus grazing/multiple-root test inventory | numerical/hybrid | all roots isolated or explicit ambiguity | CONCERN | E-012 #14–17/E-013: stop-only active path and disconnected monotone localizer; trajectory tests NOT_RUN. |
| C-08 | Global/QoI error | active-interface/negative search plus proposed manufactured checks | numerical/scientific | declared bounds cover reference error | CONCERN | E-012 #8–11: discrepancy is admitted as local error; no active defect/global/QoI interface found; trajectory tests NOT_RUN. |
| C-09 | Independent BDF oracle | legacy source lineage inspection | scientific | independent implementation and reference | CONCERN | E-012 #19–21/E-013: partial domain controls, solver-success-like admission, same-trajectory replay; BDF tests/runs forbidden. |
| C-10 | Authenticated parity | tracked parity evidence and controller caller search | custody/reproducibility | authenticated admitted transition | FAIL | E-013: current tracked parity is 13/22 and helper is manual/disconnected; parity run forbidden. |
| C-11 | FSM/resume | status-load/run-entry and transition-test inspection | software/custody | absorbing terminal semantics | CONCERN | E-012 #24/E-013: terminal status is restored but not gated by a complete legal-status FSM; behavioral exploit NOT_RUN. |
| C-12 | Containment/resources | package/process/preflight static inspection | security/operational | closed-world fd-bound bounded behavior | CONCERN | E-012 #25–31/E-013: positive controls exist, but manifest/race/tool/forecast/scaling/buffering gaps remain; drivers NOT_RUN. |

## Proposed implementation acceptance gates

| ID | Requirement | Planned check | Level | Expected | Status | Failure semantics / rollback trigger |
|---|---|---|---|---|---|---|
| P-00 | Successor/predecessor isolation | exact hashes of A/P/V/C/S/R2A/U/B before/after every N slice; routing/schema negative tests | custody/compatibility | predecessors byte-identical; no v1/v2 cross-route | NOT_RUN | Any predecessor mutation or cross-route aborts and reverts the N slice. |
| P-01 | Characterization before change | existing suite plus golden typed-result/state transitions | software | unchanged forensic behavior | NOT_RUN | Unexpected drift blocks patch; revert that slice. |
| P-02 | Verified primitive arithmetic | exact-rational boundary corpus, MPFR/qualified interval differential oracle, subnormal/overflow/signed-cancellation properties | numerical/adversarial | enclosure for every finite in-domain case; explicit indeterminate otherwise | NOT_RUN | Any false enclosure blocks all certificate consumers. |
| P-03 | Verified elementary functions | endpoint/extrema/domain corpus for `exp/log/log1p/expm1` and required tables | numerical/adversarial | outward enclosure under named backend/version | NOT_RUN | Domain or containment failure returns typed failure, never certificate success. |
| P-04 | Krawczyk/interval Newton | analytic exact systems, ill-conditioned/nonexistence/zero-denominator cases, mutation tests | numerical | theorem hypotheses and strict inclusion imply unique-solution certificate | NOT_RUN | Missing hypothesis or failed independent residual makes result inconclusive/failure. |
| P-05 | Physics formula/constraints | units, abundance convention, exact-zero/vacuum/complement limiting cases | scientific | analytic identities and declared domains hold | NOT_RUN | No clipping/flooring/projection may convert invalid input into success. |
| P-06 | Error hierarchy | order study, dense reconstruction defect, stability-weighted global bound, adjoint/QoI dual-weighted residual | numerical/scientific | each distinct budget covers independent reference under stated hypotheses | NOT_RUN | An unavailable theorem component is `UNESTABLISHED`, not estimated success. |
| P-07 | Hybrid events | manufactured simple/multiple/grazing/near-coincident roots, step-partition metamorphism, direction filters | numerical/adversarial | all roots isolated to time/state tolerance or explicit ambiguity | NOT_RUN | Missing/ambiguous expected event rejects step and blocks admission. |
| P-08 | Rollback/rebuild/restart | branch/table event state-machine and atomic crash-injection properties | software/hybrid | deterministic generation and idempotent restart | NOT_RUN | Partial state or illegal transition is absorbing failure. |
| P-09 | Typed admission | mutation test each finite/domain/residual/event/invariant/diagnostic predicate | software/adversarial | deleting/inverting any predicate makes tests fail | NOT_RUN | Only fully admitted typed result can serialize as success. |
| P-10 | Sparse/low-rank opportunity | dense-vs-sparse/JVP/Schur differential tests, rank audit, condition estimator, fallback injection | numerical/performance | same admitted result; bounded speed/memory gain | NOT_RUN | Nonblocking for correctness; rank/conditioning mismatch takes dense fallback. Mandatory only for performance promotion. |
| P-11 | Numerical ABI/process identity | container/host, interpreter/SOABI, package RECORD/shared libs, libc/libm, BLAS/LAPACK, CPU/fenv/FTZ/DAZ/FMA, affinity/threads/locale, tool hashes, deterministic rerun | reproducibility/security | exact manifest identity and repeated outputs | NOT_RUN | Drift or unresolved rec_bianchi identity is preflight failure. |
| P-12 | Path/package containment | symlink/race/traversal/adversarial archive corpus and manifest postimage | security/custody | no escape; complete verified manifest | NOT_RUN | Containment uncertainty aborts package. |
| P-13 | Bounded resources | streaming stdout/stderr quotas, timeout/process-tree kill, disk/memory/ancestry forecasts | operational/performance | hard maxima enforced with complete diagnostics | NOT_RUN | Quota termination is typed failure; partial output cannot promote. |
| P-14 | Forensic/corrected lanes | D-01–D-07 decision audit, predecessor hash, rec_bianchi-lock adjudication, schema/routing/consumer negative tests | reproducibility/scientific | no in-place edit/cross-lane substitution; authorized N identity | NOT_RUN | Any unresolved decision or lineage ambiguity blocks implementation/comparison/promotion. |
| P-15 | Aggregate exact-head review | all prior gates in pinned clean environment plus independent code/scientific review | aggregate | all mandatory gates pass | NOT_RUN | Local green alone is insufficient; no scientific promotion in this plan. |
| P-16 | Admission dependency/FSM | model-check slice-state table and every typed status/action; controller-consumed parity transition | software/custody | no shadow/standalone receipt can admit; terminals absorbing | NOT_RUN | Any illegal/missing/multiple transition blocks corrected routing. |

Status vocabulary: `PASS / CONCERN / FAIL / NOT_RUN / NOT_APPLICABLE`.
