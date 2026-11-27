# HE-ANG independent implementation review — C9 PASS_SCOPED

Reviewer: `/root/heang_independent_review`. Workflow **1.0.0** / approval **0.2**.

**Decision: PASS_SCOPED for the exact event/moment implementation, structural provider precheck, manufactured-fixture CLI, and comparison with saved independent R7 evidence. No open code findings remain in this scope. No additional scientific execution is requested.**

This decision follows a full read-only source audit, independent hand evaluation of the nontrivial expected values, inspection of the actual C6 and C7 outputs, and final byte/receipt/resource-ledger readback. The reviewer did not author the implementation, import project modules, execute scientific controls, regenerate the oracle, or replay an old suite. Reviewer scientific executions: **0**. The reviewer role is observed from the team assignment; no separate model identity is asserted.

## Reviewed boundary and source identities

Canonical unit: `BASS_HE/research/he_ang_provider_contract_20261023/`. Paths in this report are relative to that unit unless qualified otherwise.

The frozen author manifest is `code/SOURCE_MANIFEST.json`, SHA256:

`d1ab2796ef737f95de7e6e5d176b6f8336f51b3f2ec96c198feedd953136bac9`

All ten files listed in that manifest match both its recorded sizes/hashes and the original `heang_code/` bytes. The author manifest's `science_execution=NOT_RUN` describes the authoring checkpoint. The actual later executions are established by the separate C6/C7 receipts and charged attempts.

| Reviewed source | SHA256 |
|---|---|
| `code/heang_contract/exact_events.py` | `bd6754457c34460ec6439ea6bc766e79f810266c036f46a60b8260b14b6504db` |
| `code/heang_contract/metadata.py` | `5b2caf10bc4861ca998c76d682f34034c21c75dd71dba0c5942a45c6940359f0` |
| `code/heang_contract/cli.py` | `7f2d1f6810b0df0425da44ecff6c637f4ddd040f2dd894ef627b48aa9d5452b8` |
| `code/controls.py` | `f252976b06d6ba201250de3397cb5ba9a37d4b563170e7ae11635b024cdbf035` |
| `code/compare_saved_witness.py` | `a2fad1d9728321757e9c6892f69189eb89b6b5c0748d57956a513522d8efd665` |
| `theory/check_witness.py` | `30f8b023979f1f6b38e5b0a85f903513beaec1b1625adbab42808c4f31f4d08b` |
| `run_bounded.py` | `505fe06d2adcc7c3d93ad7207a1a2fcf437a6c08582430d140f58f2f1a98503c` |

The C7 comparison script is a root-authored supplement outside the immutable author manifest. Its separate identity is reviewed here and must remain included in the final science package identity. The full identity inventory and 112 successful administrative consistency checks are in `heang_independent_review/EXECUTION_READBACK.json`, SHA256 `bc8233a69503826042bea206fbc4ef6c0b1b0d556628420ddc37f94f3d37a96a`. These 112 checks are byte, record and bookkeeping checks, not additional scientific cases or executions.

## Equation-to-code decision

The detailed source inspection and independent hand calculations are preserved in `heang_independent_review/CODE_REVIEW_PRELIMINARY.md`. Its pending execution requirement is closed by the actual evidence below.

The accumulator uses a positive finite event law with event count one, inclusive electron count two and ion count one. Before accumulation it checks normalized event weights and each event's finite-mass COM momentum and energy shell. It constructs both species from the same joint event law. The pressure-type convention is

\[
P_s=\langle\sum q\rangle,\qquad
R_s=\left\langle\sum\frac{qq^{\mathsf T}}{m_s}\right\rangle,\qquad
K_s=\tfrac12\operatorname{tr}R_s.
\]

With common event-measure mass \(Z\), the implemented ledger has \(N_e=2Z\), \(N_p=Z\), \(K_e+K_p=Z(E-I)\), and

\[
R_p=\frac{m}{M}R_e+\frac{C_{12}}{M},\qquad
\operatorname{tr}C_{12}=2MZ(E-I)-2(M+m)K_e.
\]

The conditional-to-cross-section operation scales all counts and moments once, including the correlation tensor. Its separate nonzero-cross-trace control exercises the general normalization formula beyond the two-cone witness's special zero trace. The zero-cross-section branch constructs zero unconditioned moments without introducing a normalized conditional law.

The raw transform implements \(q'=O(q-m_sU)\), hence

\[
P'_s=O(P_s-m_sN_sU),
\]
\[
R'_s=O\bigl(R_s-UP_s^{\mathsf T}-P_sU^{\mathsf T}
+m_sN_sUU^{\mathsf T}\bigr)O^{\mathsf T}.
\]

The signed reactive number term is retained. A nontrivial boost and rotation and a signed incoming loss both have independently hand-checked expected outcomes and successful actual controls. The raw-moment carrier is explicitly not a PSD or realizability certificate; direct positive event support and a candidate-bound X1 decision remain distinct forms of evidence.

Exact represented inputs accept rational strings/integers and refuse binary floats, booleans, invalid dimensions, negative weights, inconsistent shells and double weighting. The CLI confines payload paths, bounds input size/event count, rejects duplicate keys and nonfinite constants, checks the known fixture payload's identities and physical-coordinate declarations, and executes the manufactured discrete COM schema only.

## Provenance and admission decision

The metadata precheck binds sigma, inclusive-electron data, moments and correlation to common source/law/preparation/angular-source identities and actual supplied byte hashes. It keeps incident energy/frame/relative-flux declarations, support coverage, coordinate roots and Jacobian references, and physical versus numerical uncertainty separate.

The source-reference fields establish declared dependencies. Their presence does not establish the scientific truth of their contents, and structural readiness never grants physical admission. Partial coverage and missing correlation remain scoped/partial outcomes; missing required evidence and unknown physical uncertainty remain deferred. All outcomes retain `empirical_admission=false` and `runtime_activation=false`.

Inherited X1 algorithm and completed-fixture evidence are distinct from the certificate for a new candidate moment payload. The candidate digest must bind the currently supplied payload; an old PASS alone is insufficient. PASS/FAIL/INDETERMINATE and the represented-input/source-uncertainty qualifications are retained. The manufactured analytic certificate does not relabel the old 32-fixture execution as a new candidate run.

No source audit defect was found within this declared structural scope. Physical exchange/support, energy-threshold conventions, coalescing-root treatment, measured-data uncertainties and the scientific content of source references still require the source-admission work already identified by the claim gate.

## Actual evidence accepted

| Stage | Actual result inspected | Scope |
|---|---|---|
| R7 | 252/252 predicates, 2 cases, 4 laws, 32 saved events | Independent exact manufactured witness; reused as saved evidence for C9 |
| C6 | 51/51 affected controls, failure count 0 | Event support/algebra, normalization, frame transform, metadata dependency errors, candidate binding and CLI behavior |
| C7 | 28/28 saved-oracle comparisons, failure count 0 | The new accumulator applied to the same 32 saved events; 2 cases and 4 laws |

Every inspected attempt finished with return code 0, `state=PASS`, `code_unchanged=true`, `timed_out=false`, `within_cumulative_cap=true`, and empty stderr. Saved raw artifacts are byte-identical to their corresponding attempt stdout. Receipt output/FINISH digests, START source identities and ledger event hashes match the actual files.

| Actual output | SHA256 |
|---|---|
| `theory/WITNESS_RESULTS.json` | `18d02cb7c94efba5d4129f71fc4ba1b2afb8d57a7cfcbca09eb4cd3da1797658` |
| `evidence/execution/AFFECTED_CONTROLS_RAW.json` | `602ef23d0352982888418bb480eca8c5dee0f88cb9811414fd9223935e026ee9` |
| `evidence/execution/SAVED_ORACLE_COMPARISON.json` | `bc0e25c5a0d3e8fe3a8b7133660ef40526e907023f1495126fd52a61c9c58a00` |

The C7 supplement checks the saved oracle digest and the author manifest digest, reads the saved events and compares both species' raw N/P/R, C12, K and axial D. It imports the new accumulator but does not import or regenerate the R7 oracle. The second saved case uses unequal masses and a rotated axis, producing nonzero off-diagonal entries. Its arbitrary positive threshold is stated explicitly; only the saved outgoing energy W matters for this correspondence, so it does not establish an empirical H1 threshold.

The independent R7 script uses separate rational point-list algebra rather than the production package. The C7 expected values come from its saved output. This supplies a useful independent calculation path alongside the directly hand-checked C6 values. The 252 R7 predicates, 51 C6 controls and 28 C7 comparisons are separate counts with separate meanings; they are not a larger population of physical source cases.

## Cumulative budget readback

`BUDGET.json` is the frozen fresh-unit allocation. `RESOURCE_LEDGER.json` is the current accounting authority; its immutable input hashes and all six START/FINISH event records were checked. The known charges are:

| Attempt | Charged CPU seconds | Charged wall seconds | Child peak RSS KiB |
|---|---:|---:|---:|
| R7 exact witness | 0.211275 | 0.1680309520015726 | 9984 |
| C6 affected controls | 0.177225 | 0.17479019000165863 | 15104 |
| C7 saved-oracle correspondence | 0.203702 | 0.1739993850060273 | 13056 |
| Total | 0.592202 | 0.5168205270092585 | Per-child values above |

Fresh caps remain 10 CPU seconds / 30 wall seconds with per-invocation 2 CPU seconds / 5 wall seconds and 268435456-byte address-space limit. The current ledger records **9.407798 CPU seconds** and **29.48317947299074 wall seconds** remaining, with no unknown fresh cost records. Charges include whole-child startup/wait/exit and the measured wrapper contribution. FINISH/ledger persistence and wrapper exit after measurement are explicitly recorded as unmeasured non-scientific bookkeeping.

These are the fresh HE-ANG-CONTRACT charges. Historical budgets remain nontransferable; the inherited unknown-cost record is not converted into an exact residual old allowance. No old HE-X1/HE38/HE32 replay, new IVP, provider scan, render or benchmark is part of these attempts. These resource receipts are execution accounting, not performance benchmarking.

## Findings and closure

| Finding | Evidence and impact | Minimum correction and closure |
|---|---|---|
| F1, original theory normalization ambiguity | Conditional-only recoil formulas were initially paired with a template that also allowed cross-section-weighted inputs. | CLOSED by the canonical Z-dependent theory/template and now by the implemented sigma path and successful general nonzero-cross-trace control. |
| F2, original preparation-dependent rate omission | A general angular source could not suppress incoming-axis/preparation dependence without an explicit symmetry condition. | CLOSED by canonical `sigma(E,a;preparation)` and its suppression condition; the metadata contract retains this declaration. |
| New code findings | No blocking defect found in the actual reviewed implementation and controls. | Open code findings: 0. No correction or further run required for this scope. |

The original findings and correction readback remain preserved in `heang_independent_review/THEORY_REVIEW_INITIAL.*` and `THEORY_REVIEW_FINAL.*`. Canonical theory SHA256 `c71c7d702f708d79449f70870a62184c5ea71128ef4351f0dde529bc4558fc3d` and template SHA256 `a96df2ade32b5fbe21529555758ea32f9f06d55fcb2a2adc54d0688260bdc99c` remain unchanged from the R6 acceptance.

## Accepted completion and remaining science

This C9 decision closes independent implementation review for the HE-ANG-CONTRACT subunit and supports C10 packaging/publication of that precise result. It establishes an executable event/source/frame contract and a specific kinematic witness for the correlation information needed to recover ion recoil tensors from electron-inclusive information.

The parent HE-ANG physical source remains **SOURCE_INPUT_PENDING**. Empirical calibration, replacement of the HE38 source model, runtime activation and merge remain false/held. This review does not assert a new universal no-go theorem, empirical angular correction, literature novelty, completed baryonic closure or completion of the user's full atomic/nuclear research goal. The next dependency remains a source-qualified same-law event dataset or certified moments, followed by full support/frame/label/root review, physical uncertainty allocation and a new source-model pin with affected controls.

No additional scientific execution is necessary to close this review.
