# RESEARCH RECORD

## Immutable preregistration — 2026-08-23

### Research question

At REI Bianchi HEAD `111b6ace750e36e218df7fc9626c6bad2ec19971`, which mathematical, algorithmic, and coding remediation strategy—using the preceding solutions only as unverified seeds—is the smallest sufficient design to eliminate the frozen ODE-solver false-success and claim-integrity blocker families, and what exact tests and authority gates are required before implementation?

### Scope and instruction boundary

- The attached coding-harness documents define procedure only; their examples do not define the user request or scientific truth.
- Current layer is `diagnose → design`. Phase 5 implementation is `CANCELLED_OUT_OF_SCOPE` unless separately authorized.
- Repository reads, exact small probes, non-production tests, primary-source research, temporary harness-state writes, and independent review are allowed.
- Target writes, production/history/parity/package/BDF drivers, baseline/tolerance/convention changes, new dependencies, external writes, and scientific promotion are forbidden.

### Frozen seed set — not premises

S-01 qualified outward-rounded interval arithmetic and verified elementary functions;
S-02 exact/reproducible summation and residual evaluation;
S-03 correct interval Newton/Krawczyk contracts and fail-closed certificate consumers;
S-04 constraint-aware state representation without silent floors/projection;
S-05 consistent local error estimation, continuous defect, stability/global propagation, and adjoint/QoI estimation;
S-06 dense-output all-root event isolation, grazing/multiplicity handling, rollback/rebuild/restart;
S-07 block-sparse/JVP plus exact low-rank Schur/Woodbury acceleration with dense fallback;
S-08 independent oracle, property/metamorphic/mutation/differential testing, and analytic/manufactured cases;
S-09 typed solver result/admission taxonomy with finite/domain/residual/event/diagnostic predicates;
S-10 explicit controller finite-state machine, absorbing terminals, atomic resume/restart/generation semantics;
S-11 exact runtime/tool/input/output identity, authenticated parity, path/package containment, bounded streaming, and resource forecasts;
S-12 separate forensic-compatibility and corrected-science lanes.

### Competing hypotheses

H1 — Minimal localized repair is sufficient.

- Prediction: correcting current formula/arithmetic/certificate/result checks and adding focused adversarial tests closes every frozen blocker without controller/reference architecture changes.
- Falsifier: at least one blocker intrinsically requires continuous trajectory/event semantics, independent oracle lineage, or cross-process state/custody redesign.

H2 — Layered contract/validation-first repair is the smallest sufficient strategy.

- Prediction: explicit verified-numerics, hybrid-step/event, typed-admission/controller, and independent-reference/custody boundaries cover all frozen blockers while preserving history and interfaces.
- Falsifier: those boundaries cannot be introduced without effectively replacing the architecture, or a blocker remains uncovered after exact interface/test mapping.

H3 — Architectural replacement is necessary.

- Prediction: only a new validated-IVP/hybrid solver and controller/reference stack can satisfy all false-success, global-error, event, and custody requirements coherently.
- Falsifier: H2 yields a dependency-ordered patch series with bounded interfaces, characterization tests, fallbacks, and no unresolved blocker family.

### Planned methods

| ID | Type | Method | Close condition |
|---|---|---|---|
| M-01 | confirmatory | Bind current identity, active call graph, local versions, tests, and every frozen blocker/seed to exact code. | Every blocker has source evidence or a named gap. |
| M-02 | confirmatory | Reproduce declared exact arithmetic/certificate/runtime counterexamples and run the smallest relevant non-production suite. | All planned probes report exact commands/results; failures are not repaired. |
| M-03 | confirmatory | Use at most three external query topics for version-matched official/primary numerical contracts. | Each source claim is reconciled to current code or limited. |
| M-04 | confirmatory | Compare H1–H3 on coverage, interfaces/files, complexity, numerical risk, compatibility, tests, rollback, and authority. | One smallest sufficient candidate or justified no-selection. |
| M-05 | confirmatory | Independent reviewer receives frozen record/evidence/design without expected verdict. | Verdict is confirmed, partially-confirmed, or rejected; not inconclusive. |
| M-06 | confirmatory | Close harness state, decision, validation matrix, repository custody, and bounded contract. | All acceptance criteria pass or task terminates with registered failure. |

Any probe added after an unexpected result is `exploratory` and cannot retroactively confirm a hypothesis.

### Stopping rules

- At most three substantively distinct solution candidates and three external query topics.
- All M-01–M-06 closed; no open confirmatory experiment.
- Every frozen blocker and seed maps to the selected design, a rejected candidate, or an explicit gap.
- Independent review verdict is not inconclusive.
- Target remains unchanged with the same two untouched bundle paths.
- No implementation or scientific authority claim.

## Evidence and result log

Entries below this line are append-only. The preregistration above is never rewritten after result evidence is collected.

### E-001 — Bound identity and custody (M-01, confirmatory)

- Retrieved: 2026-08-23 Asia/Seoul.
- Repository: `/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rei_bianchi`.
- Branch/HEAD: `agent/precalc-adaptive-history-parallel-runtime` at `111b6ace750e36e218df7fc9626c6bad2ec19971`.
- Tracked state: clean. The only top-level untracked entries were the two pre-existing `.bundle` paths named in the work contract; they were not opened, hashed, moved, or modified.
- Current-source SHA-256 bindings: `adaptive_policy.py=c648...57aa9`, `attempt_worker.py=0e507...0671`, `run_adaptive_history.py=b264...233e`, `runtime_contract.py=092165...3ad`, `state_io.py=a8c151...40a1`, `package_local_results.py=a493...814b`, `interval_discrete_map.py=579df...e644`, `interval_arithmetic.py=ea8383...ec22`, `reduced_interval_rhs.py=b1f3d...9b36`, `implicit_certificates.py=197aee...c185`. Full paths and full digests are retained in the M-01 source localization result incorporated below.
- Claim limit: this establishes which bytes were inspected; it does not establish numerical correctness, historical replay, or scientific validity.

### E-002 — Existing unit-suite diagnostic (M-02, confirmatory)

- Command: `python3 -B -m unittest discover -s <bound-active-stage>/tests -p 'test_*.py'`.
- Result: `Ran 49 tests in 8.414s — OK`.
- Adjudication: `PASS_DIAGNOSTIC_ONLY`. The suite does not contain the exact signed-cancellation and exact-solution-containment witnesses below, so its green result cannot discharge the frozen false-containment/certificate blockers.

### E-003 — Exact signed-sum containment witness (M-02, confirmatory)

- Probe used the current `interval_arithmetic.py` signed-sum path on the exactly representable binary64 inputs `[-5e-324, 5e-324]` and compared the returned interval to an exact rational sum.
- Result: `M02-SUM -5e-324 5e-324 exact_1_contained False`.
- Adjudication: `FAIL_CURRENT_NUMERICAL_CONTRACT`; frozen blocker 3 persists. A positive-only sampling test is not a substitute for exact signed cancellation and underflow coverage.

### E-004 — Krawczyk exact-solution containment witnesses (M-02, confirmatory)

- Simple-system result: `certified=[True]`, `lo=[3.9999999999999933, 6.9999999999999885]`, `hi=[3.9999999999999996, 6.999999999999999]`, exact solution `[4.0, 7.0]`, containment `[False, False]`.
- Matrix-system result: `certified=[True]`, `lo=[2.9968035161322564, 0.003196483867745482]`, `hi=[2.996803516132259, 0.003196483867745485]`, exact solution `[2.9968035161322546, 0.00319648386774548]`, containment `[False, False]`.
- Adjudication: `FAIL_FALSE_CERTIFICATE`; frozen blocker 2 persists. The returned Boolean cannot be admitted as a proof while the purported enclosure excludes a known exact solution.

### E-005 — He II coefficient witness (M-02, confirmatory)

- Current evaluation: `current_per_H=0.006241`; number-density-expected value `0.079`; ratio `0.079`.
- Adjudication: `FAIL_FORMULA_BINDING`; the current He II term carries an additional helium-abundance factor relative to the number-density expression. This reproduces frozen blocker 1 without changing physics conventions or code.

### E-006 — Runtime contract witness (M-02, confirmatory)

- Live interpreter/packages: Python `3.12.3`, NumPy `2.4.2`, SciPy `1.17.0`, pandas `3.0.0`; JAX absent.
- Bound runtime contract expects NumPy `2.3.5`, SciPy `1.17.0`, pandas `2.2.3`.
- Adjudication: `FAIL_RUNTIME_IDENTITY`; frozen blocker 22 persists. Unit compatibility in this environment is not authenticated parity under the pinned runtime.

### E-007 — External-source topic 1/3: verified arithmetic (M-03, confirmatory)

- Query topic (single frozen topic): validated interval/Krawczyk/reproducible summation contracts.
- Primary sources: S. M. Rump, *Verification methods: rigorous results using floating-point arithmetic*, Acta Numerica 19 (2010), DOI `10.1017/S096249291000005X`; S. M. Rump, T. Ogita, S. Oishi, *Accurate Floating-Point Summation Part I*, DOI `10.1587/nolta.1.2`.
- Reconciliation: verified enclosures require directed/outward rounding through every primitive and a theorem-matched inclusion test; accurate/reproducible summation algorithms provide a principled replacement for ad hoc one-ULP widening under signed cancellation/underflow.
- Limits/dead end: the Rump PDF fetch timed out, so only bibliographic/search metadata was used here and no uninspected theorem text is asserted. These sources do not prove that a particular future implementation is correct.

### E-008 — External-source topic 2/3: ODE error and events (M-03, confirmatory)

- Query topic (single frozen topic): continuous defect/global error/QoI and all-root event semantics.
- Primary sources: D. Estep, *A Posteriori Error Bounds and Global Error Control for Approximation of Ordinary Differential Equations*, SIAM J. Numer. Anal. 32(1), DOI `10.1137/0732001`; W. H. Enright and W. B. Hayes, *Robust and reliable defect control for Runge–Kutta methods*, DOI `10.1145/1206040.1206041`; L. F. Shampine and S. Thompson, *Event location for ordinary differential equations*, DOI `10.1016/S0898-1221(00)00045-6`; T. Park and P. I. Barton, *State event location in differential-algebraic models*, DOI `10.1145/232807.232809`.
- Version-matched official contract: SciPy `1.17.0` `solve_ivp` documentation, `https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.solve_ivp.html`.
- Reconciliation: a step-doubling state distance is not by itself a continuous-defect, stability-weighted global-error, or QoI certificate. SciPy 1.17 explicitly detects events by sign changes over steps and warns that multiple zero crossings within one step may be missed; `success=True` means reaching the interval end or a termination event, not satisfaction of application-specific domain/residual/event/custody predicates.
- Limits: each error theorem has hypotheses that a future design must state and test. Generic `scipy` documentation initially resolved to 1.18 and was rejected as version drift; only the explicit 1.17 URL is used for current-library semantics.

### E-009 — External-source topic 3/3: process/runtime I/O (M-03, confirmatory)

- Query topic (single frozen topic): SciPy 1.17 sparse/Jacobian interfaces and Python 3.12 subprocess buffering semantics.
- Official sources: the SciPy 1.17 `solve_ivp` page above; Python 3.12 `subprocess` documentation, `https://docs.python.org/3.12/library/subprocess.html`.
- Reconciliation: SciPy recommends an analytic callable Jacobian and exposes sparse Jacobian/sparsity support, which can underwrite a dense-correctness-first sparse/JVP optimization seam. Python documents that `run(capture_output=True)` connects `stdout`/`stderr` to pipes and waits via `communicate`; therefore the current post-hoc size check is not a manual-`wait()` pipe-deadlock claim, but it still buffers child output in memory before that check and needs streaming quotas for bounded-resource authority.
- Limits: documentation establishes API semantics, not performance or correctness of the proposed low-rank path. No fourth external query topic was opened.

### E-010 — M-02/M-03 provisional conclusion

- H1 is already under pressure: exact arithmetic and formula fixes are necessary, but official event semantics and the runtime/custody witness concern contracts outside a localized numerical kernel.
- This is provisional until the 32-row source crosswalk and independent review close M-01/M-04/M-05.

### E-011 — Identity addendum for E-001/E-002

- `<bound-active-stage>` in E-002 is `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY`.
- Full current-source SHA-256 values, in E-001 order: `c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9`; `0e507c7bc73e4cdcff7c3a55d20ea7afb78fc6ef925bef891029281ccf904671`; `b26432ad582a8b01e9eb3b15585fb69df0d2a2fea26c7bd482020965c0fc233e`; `092165390da33512d034851835d31244e90254edf3c780e308a0abc04279e3ad`; `a8c151c9c1ce32f1e544b205ccffec1b4f8c6bdcaac4cb3685d42488c05c40a1`; `a493cc156ac49a7c6560a78f25e5864452768a7e4b4a08fa62e3961240b0814b`; `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`; `ea8383f8f4bc0d463d9908af9baa4743ad80e125b60d22991028b4d57a10ec22`; `b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36`; `197aee751933a9b80c97453e55ecb9f0a346f8c85198715841ea2255c4e1c185`.

### E-012 — Frozen blocker/seed/current-code/design crosswalk (M-01/M-04, confirmatory)

Path aliases and slice IDs are defined in `PLANS.md`. `REPRODUCED_FAIL` is stronger than code inspection; `DIRECT_LIMITATION` is current source/call-graph evidence; `UPSTREAM_RETAINED` is historical/upstream code consumed but not executed by the active chain; `NOT_BENCHMARKED` is not a correctness failure. Proposed gates are unexecuted.

| # | Frozen blocker | Current binding and adjudication | Seed(s) | H2 owner slice and mandatory gate |
|---:|---|---|---|---|
| 1 | He II extra `YHE` | `R2A/analysis/array_owner_kernel.py:203-235,320-362`; `V/analysis/reduced_interval_rhs.py:405-435,471-503`; E-005 `REPRODUCED_FAIL`. | S-04,S-08,S-12 | I-1; P-05 pure-He II convention identity; corrected lane only. |
| 2 | Krawczyk false certificate/exact solution excluded | `C/analysis/implicit_certificates.py:1-6,41-119` → `P/analysis/interval_discrete_map.py:171-197,202-341`; E-004 `REPRODUCED_FAIL`. | S-01,S-03,S-08,S-09 | I-1; P-02–P-04 exact containment, theorem hypotheses, independent residual, fail-closed consumer. |
| 3 | Signed-sum false containment | `V/analysis/interval_arithmetic.py:1-7,212-217`; E-003 `REPRODUCED_FAIL`. | S-01,S-02,S-08 | I-1; P-02 exact-rational signed/subnormal/property corpus. |
| 4 | One-`nextafter`/transcendental proof gap | `V/analysis/interval_arithmetic.py:1-7`; `V/analysis/reduced_interval_rhs.py:573-589`; heuristic scope is explicit: `DIRECT_LIMITATION`. | S-01,S-08 | I-1; P-03 qualified outward elementary functions or `CERTIFICATE_UNAVAILABLE`. |
| 5 | Strict-positive/log/logit excludes exact zero/trace | `V/analysis/reduced_interval_rhs.py:316-384,505-523,573-589`; current serialized state also requires positive lower populations at `A/analysis/state_io.py:27-35`: `DIRECT_LIMITATION`. | S-04,S-08,S-12 | I-1; P-05 closed-simplex active-face/vacuum/trace domain and no silent floors. |
| 6 | 54 eV complement cancellation | `P/analysis/interval_discrete_map.py:104-156`; point operator `U/analysis/event_uncertainty_operator.py:139-165`: `DIRECT_LIMITATION`. | S-02,S-04,S-08 | I-1; P-05 direct nonnegative opacity ratios and limiting/complement cases. |
| 7 | Vacuum/floor ambiguity | Same strict-chart paths as #5; no explicit active vacuum/trace regime found: `DIRECT_LIMITATION`, with convention owner decision still open. | S-04,S-09,S-12 | I-1/I-0; P-05 typed regimes and transition semantics; no numerical default may choose physics. |
| 8 | Full/two-half distance is not established LTE | `A/analysis/attempt_worker.py:98-133`; `P/analysis/interval_discrete_map.py:343-390`; `A/analysis/adaptive_policy.py:245-283` names/admits it as validated local error: `DIRECT_LIMITATION`. | S-05,S-08,S-09 | I-2; P-06 rename discrepancy and independently establish each error budget. |
| 9 | No continuous defect | Negative search over the mechanically traced active chain found no dense-reconstruction defect interface: `DIRECT_LIMITATION`. | S-05,S-08 | I-2; P-06 branch-consistent reconstruction and independent defect coverage. |
| 10 | No global-error control | No stability-weighted propagation/adjoint/global estimator in the active chain: `DIRECT_LIMITATION`. | S-05,S-08,S-09 | I-2; P-06 manufactured bound-coverage under stated hypotheses. |
| 11 | No QoI budget | No QoI definition, adjoint, dual weight, or owner-approved error allocation in the active chain: `DIRECT_LIMITATION`. | S-05,S-08,S-09 | I-2; P-06 separate owner-selected QoI budgets; unavailable means `UNESTABLISHED`. |
| 12 | Photon validator self-cancels | `P/analysis/interval_discrete_map.py:104-156,370-381` → `A/analysis/attempt_worker.py:121-126` → `A/analysis/adaptive_policy.py:235-285`; same-path closure: `DIRECT_LIMITATION`. | S-02,S-08,S-09 | I-2; P-05/P-09 independent primitive incident/escape/absorption ledger plus mutation tests. |
| 13 | Energy validator tautology | Same paths as #12; unresolved energy is constructed to close the checked sum: `DIRECT_LIMITATION`. | S-02,S-08,S-09 | I-2; P-05/P-09 independently accumulated energy terms and mutation tests. |
| 14 | Grazing events missed | Active table-event path `P/analysis/interval_discrete_map.py:297-341`; controller only stops at `A/analysis/adaptive_policy.py:426-427`; no active tangency locator: `DIRECT_LIMITATION`. | S-06,S-08,S-09 | I-3; P-07 interval `g,dg/dt`, multiplicity ambiguity, bisection then hard stop. |
| 15 | Multiple/simultaneous events missed | Same active path; disconnected locator does not prove all-root/priority semantics: `DIRECT_LIMITATION`. | S-06,S-08,S-09,S-10 | I-3; P-07 isolate/order/coalesce all roots or reject ambiguous step. |
| 16 | No production localization | Localization exists only in disconnected `P/analysis/cross_site_discrete_map.py:42-130`; active decision is stop-only at `A/analysis/adaptive_policy.py:426-427`: `DIRECT_LIMITATION`. | S-06,S-08,S-09,S-10 | I-3; P-07 active call-path and admission mutation tests. |
| 17 | No restart/rebuild | Synthetic `P/analysis/table_event_restart_audit.py:26-82` is disconnected; active run returns `BLOCKED_TABLE_EVENT` at `A/analysis/run_adaptive_history.py:2102-2108`: `DIRECT_LIMITATION`. | S-06,S-08,S-09,S-10 | I-3; P-08 rollback, branch/table/Jacobian/cache rebuild, generation restart, crash injection. |
| 18 | Rank-`<=3` block/nonlocal structure unused | Active dense blocks at `P/analysis/interval_discrete_map.py:171-281`; nonlocal factorization machinery `S/analysis/global_coupling.py:52-76,128-250` is disconnected: `NOT_BENCHMARKED`. | S-07,S-08 | I-4 optional; P-10 exact factorization/rank/condition/residual differential tests and dense fallback. |
| 19 | Legacy BDF domain/extrapolation | `B/inputs/canonical_b2c2a_r1_src/gamma_conditioned_reconciliation.py:647-689`, `absorption_decomposition.py:438-480`; active chain consumes immutable derived interpolation via `R2A/analysis/array_forcing.py:49-103`: `UPSTREAM_RETAINED`. | S-08,S-09,S-12 | I-7; P-14 additive corrected lane with explicit domain/extrapolation admission. |
| 20 | Legacy BDF admission | Same legacy solves primarily consume `.success`; no current replay executed: `UPSTREAM_RETAINED`. | S-08,S-09,S-12 | I-7; P-14 expected terminal, finite/domain/residual/invariant admission. |
| 21 | Legacy BDF oracle not independent | `B/analysis/replay_canonical_bdf_dense.py:111-141,161-281` is same-lineage replay: `UPSTREAM_RETAINED`. | S-08,S-12 | I-7; P-14 analytic/manufactured and independently assembled primitive-flux oracle. |
| 22 | Runtime mismatch | `A/analysis/runtime_contract.py:18-51,71-107,153-220`; E-006 `REPRODUCED_FAIL`. | S-09,S-11 | I-5; P-11 pinned clean environment and exact executable/dependency/source/input fingerprint. |
| 23 | Unauthenticated parity | Guide-only `A/analysis/validate_one_attempt.py:13-34` compares one endpoint; no controller caller/admission transition found: `DIRECT_LIMITATION`. | S-09,S-10,S-11 | I-6; P-11/P-14 authenticated candidate-validator-runtime-source-input-output receipt. |
| 24 | Terminal resume semantics | `_load` restores status at `A/analysis/run_adaptive_history.py:1517-1584`, while `run` enters the loop at `2056-2118` without a distinct already-terminal entry branch: `DIRECT_LIMITATION`. | S-09,S-10,S-11 | I-5; P-08/P-11 absorbing-terminal transition properties and explicit resume/restart/new. |
| 25 | Package containment/over-collection | `A/analysis/package_local_results.py:47-69` broad-selects JSON/history/receipt/snapshot files: `DIRECT_LIMITATION`. | S-11 | I-6; P-12 generation allowlist and verified manifest postimage. |
| 26 | Symlink/path containment | `package_local_results.py:47-69` checks discovered symlinks/realpaths but traverses names before descriptor-anchored custody and has no race proof: `DIRECT_LIMITATION`. | S-11 | I-6; P-12 descriptor/no-follow containment and traversal/swap/hardlink corpus. |
| 27 | Bare `PATH`/tool identity | `A/analysis/preflight.py:15,19-24` invokes `git`/`sha256sum` by name; `runtime_contract.py:71-94,140-148` also shells out: `DIRECT_LIMITATION`. | S-11 | I-5/I-6; P-11 resolve/hash executables or qualified library operation; environment allowlist. |
| 28 | Weak candidate semantic validation | `A/analysis/run_adaptive_history.py:1697-1727`; `adaptive_policy.py:235-374` validates schema/metadata/current ledgers but no independent physical oracle: `DIRECT_LIMITATION`. | S-08,S-09 | I-0/I-2; P-05/P-09 independent physical/event/error predicates and predicate mutation. |
| 29 | Quadratic ancestry/custody | `A/analysis/run_adaptive_history.py:842-1029,1391-1498` repeatedly walks/reads validated record/journal/generation material: `DIRECT_LIMITATION` for scaling; no benchmark run. | S-10,S-11 | I-6; P-13 authenticated incremental parent/index with O(1) append and O(n) full audit. |
| 30 | Incomplete resource forecast | `A/analysis/preflight.py:38-43` covers memory; `run_adaptive_history.py:421-463,2125-2147` caps workers/attempt arguments; no disk/inode/log/package forecast found: `DIRECT_LIMITATION`. | S-09,S-11 | I-5/I-6; P-13 hard wall/disk/inode/memory/output/ancestry maxima and estimate-vs-actual. |
| 31 | Unbounded worker buffering | `A/analysis/run_adaptive_history.py:1630-1678` uses `subprocess.run(capture_output=True)` before `_bounded_text`; `package_local_results.py:87-96` uses `read_bytes`/`BytesIO`: `DIRECT_LIMITATION`. | S-09,S-11 | I-5/I-6; P-13 streaming drain/hash/archive quotas and process-tree termination. |
| 32 | Nonfinite/overflow gaps | State/adaptive layers have partial finite checks (`state_io.py:27-35`; `adaptive_policy.py:235-374`), but verified arithmetic/transforms/external boundaries lack complete overflow/domain semantics: `PARTIAL_RETAINED`. | S-01,S-04,S-08,S-09,S-11 | I-0/I-1/I-5; P-02/P-03/P-05/P-09/P-11 checked arithmetic and typed failure at every boundary. |

Mechanical result: exactly `32/32` frozen blocker IDs appear once. All twelve frozen seeds appear at least once. This is completeness only relative to the frozen inventory and bound inspected roots—not a proof that unknown defects do not exist, nor evidence that any proposed gate passes.

### E-013 — Independent localization reconciliation and corrections

- Active chain reverified as `A/analysis/run_adaptive_history.py:1630-1654` → `A/analysis/attempt_worker.py:96-133` → `P/analysis/interval_discrete_map.py:24-33,297-341` → `V/analysis/reduced_interval_rhs.py` plus `C/analysis/implicit_certificates.py`. No `solve_ivp`/`BDF` lexical match exists in the bound active A/P/V/C source-and-test roots; legacy BDF is upstream/disconnected.
- **Superseding clarification for row #19:** `PARTIAL_NARROWED`, not evidence of active extrapolation. `B/inputs/canonical_b2c2a_r1_src/gamma_conditioned_reconciliation.py:135-172` and `absorption_decomposition.py:166-210` declare domains and `PchipInterpolator(..., extrapolate=False)`; active `R2A/analysis/array_forcing.py:49-103` bounds time and checks finite/nonnegative forcing. Residual surfaces are a raw-Gamma path lacking an explicit knot-range predicate at `absorption_decomposition.py:292-304`, unguarded `solution.sol(t)` API use at `B/analysis/replay_canonical_bdf_dense.py:111-141`, and disconnected older extrapolating evaluators. Tracked replay nodes appear in range. The proposed I-7 domain/admission tests remain warranted, but no current active out-of-range evaluation has been demonstrated.
- **Row #23 refinement:** tracked `A/runtime/first_interval/parity.json` and `first_interval_py31213/parity.json` report `13/22`, while older validation/optimization receipts retain `22/22` language. The standalone parity helper is manually invoked and not an authenticated controller transition. This is current evidence inconsistency, not a newly numbered blocker.
- **Row #24 refinement:** the transition journal and atomic controls are useful reusable infrastructure, but `_validate_transition_step` validates mechanics rather than a complete legal previous-status/action FSM. Paused-resume tests do not establish absorbing `BLOCKED_*`/`COMPLETE` semantics.
- **Rows #25–26 refinement:** packaging blocked evidence is legitimate forensic behavior. The defect is lack of distinct forensic/admitted closed-world manifests and descriptor-bound check/use custody, not merely that blocked runs can be packaged. Existing lexical/leaf symlink checks are positive controls but do not close parent-swap, hardlink, special-file, or mutation races.
- **Row #32 refinement:** JSON parsing rejects literal `NaN`/`Infinity`, while numeric exponent overflow, nested diagnostics, `worker_timeout=NaN`, interval infinities/intermediate overflow, and legacy nonfinite-skip/serialization paths retain gaps. Existing downstream finite checks are partial controls.
- An additional identity observation—`A/INPUT_LOCK.json` and `external/rec_bianchi.lock.json` name different rec_bianchi commits—was recorded under frozen identity/parity blocker #23 rather than expanding the frozen 32-item acceptance universe. No numerical import established which identity was consumed.
- Negative-search ceiling: absence searches covered tracked `analysis/` and `tests/` under A/P/V/C. Alternate names, generated code, dynamic imports, and data artifacts could evade lexical search. Completeness is therefore inventory-relative, not universal over unknown unknowns.

### E-014 — M-01/M-04 synthesis before independent review

- H1's preregistered falsifier fired: even perfect local repairs to blockers 1–8 cannot create the continuous trajectory/error/event/restart contracts for 9–11 and 14–17; 21 needs independent lineage; 22–31 cross runtime, controller, filesystem, resource, and provenance boundaries.
- H3's necessity prediction is not supported: the active solver boundary, immutable-parent journal, lock, canonical JSON, hash binding, atomic writes, dyadic subdivision, and dense numerical path are reusable. `PLANS.md` supplies a bounded H2 patch series with characterization, fail-closed interfaces, dense fallback, additive corrected lineage, and slice rollback.
- Provisional M-04 result: H2/`LCV-ODE` is the only candidate that is sufficient in design without wholesale replacement. It remains a specification with all implementation gates `NOT_RUN` and now proceeds to the single independent review round.

### E-015 — M-05 independent review result

- Independent verdict: `PARTIALLY_CONFIRMED`.
- Supported: H2 is the best of the three research directions; all frozen IDs/seeds are mechanically inventoried; central exact-HEAD diagnosis, conservative failure semantics, authorization boundary, and diagnostic-only treatment of the 49-test suite are well supported.
- Mandatory corrections: eliminate in-place forensic-stage edits; downscope readiness until open numerical/physics decisions are fixed; make slice/admission/FSM dependencies total; reclassify #18 or make it mandatory and preserve #19's narrowed status; bind full numerical ABI, lock identity, controller-consumed parity, and exact review preimage.
- Authority ceiling: the verdict establishes neither implementation readiness nor any numerical, performance, compatibility, parity, replay, reference, or scientific pass. `DESIGN_REVIEW.md` records the exact pre-repair file hashes and full review ceiling. This was the sole review round.

### E-016 — Sole repair/closeout round response to M-05

- Defined proposed successor stage `N`; A/P/V/C/S/R2A/U/B are now explicitly immutable predecessor/forensic bindings. All I-0–I-7 future writes and tests route under N with v2 stage/schema/manifest identities and additive rollback.
- Downgraded H2 from “smallest sufficient/implementation-ready” to `CONDITIONAL_ARCHITECTURE_NOT_IMPLEMENTATION_READY`; D-01–D-07 must resolve verified backend, boundary physics, error theorem/reconstruction, QoIs/budgets, event regime/policy, rec_bianchi/numerical-ABI identity, and exact implementation authority.
- Added a slice-state admission table and a total typed status-to-FSM action table. Shadow results cannot admit; authenticated parity is consumed by the N controller as a generation transition.
- Reclassified #18/S-07 as an inventoried nonblocking performance opportunity. The corrected completeness statement is `32/32 inventoried = 31 mandatory correctness/custody obligations + 1 performance opportunity`; #19 remains `PARTIAL_NARROWED` with no demonstrated active extrapolation.
- Expanded the runtime contract to container/host, interpreter/SOABI, package RECORD/shared libraries, libc/libm, BLAS/LAPACK, CPU/fenv/FTZ/DAZ/FMA, affinity/threads/locale and tool identities; D-06 blocks until the two rec_bianchi lock identities are adjudicated.
- No second review was performed or inferred. The repair answers the textual/architectural corrections only; every implementation gate remains `NOT_RUN`.

### E-017 — M-06 aggregate closeout result

- First aggregate command failed before validation because it was launched from the target repository and could not resolve the temporary harness's relative `tools/validate_harness.py`; F-011 records the error. The single allowed same-failure retry was consumed.
- Corrected aggregate retry from `/tmp/rei-ode-coding-loop.4qpipi` passed: 32 exact ordered blocker rows; S-01–S-12 present; exactly three external query-topic entries; eight I-slices; seven D-gates; independent verdict token present; coding-harness validation PASS; bounded-work contract PASS.
- Target custody passed: branch `agent/precalc-adaptive-history-parallel-runtime`, HEAD `111b6ace750e36e218df7fc9626c6bad2ec19971`, tracked diff empty, and exact `git status --porcelain=v1` equal to the same two untouched untracked bundle names.
- Final claim: M-01–M-06 research loop complete with design `HOLD`. Current exact witnesses remain failures; all implementation gates remain `NOT_RUN`; no implementation or science is promoted.
