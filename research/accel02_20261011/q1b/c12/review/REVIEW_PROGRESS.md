# C12 independent integration review

Reviewer: `/root/c12_review`, explicit GPT-6 Astra/high dispatch. Separate from candidate implementation, numerical test design, and oracle authorship. This is one continuing review, not a repeated whole-branch review. No tests, native maps, scientific trajectories, or completed evidence campaigns are executed by the reviewer.

Scope: new Q2_FULL_HISTORY_BINDING implementation extending PILOT02 generation 3 under an explicit child identity. The prelaunch decision concerns only the authorized first full-target continuation chunk, with at most three new attempts and a 45-second cooperative wall budget. Whole-history admission remains unevaluated.

Context reviewed: C12 contract; C11 handoff, next DAG, production design and output schema; previous independent decision; preserved controller/map/checkpoint interfaces as necessary to trace new bindings; owner-authored new test evidence. Protected whole-history criteria remain temporal nine fields 2e-6, spectral/full24 fields 1e-3, energy/original-energy and number/original-nH 1e-9, geometry 1e-11. Local 2e-7 controller defect is not a global science gate.

Confirmed semantic paths so far:

- Transition checks the original parent manifest, six-slot identity, 41 inherited dependency hashes, exact original output epoch source, and lossless physical arrays/cursor before creating a declared new runtime binding.
- Hard events consist of exact output epochs, source band/cell-edge crossings, and emissivity redshift knots. Every map still calls the frozen source-internal breakpoint routine. Opacity cuts stay internal.
- Diagnostic proxies forward the unchanged map's actual absorption and native RHS calls, retain final converged K0/KE/direct heat, and bind them to the exact gas and cell state. Gamma is the native return value. Heat uses the same per-cell native measure; instantaneous source fields use StableCellSource.source.
- Runner uses total allocation controls for child checkpoint identity and a separate single-trial invocation cap; inherited cumulative counters continue. Both accepted half-step states are included in each complete-prefix snapshot. Exact epoch outputs are constructed before accepted snapshot publication and embedded in checkpoint transaction metadata.
- Review is pending owner completion, transaction repair, pinned final source hashes, and actual zero-map child / first-chunk evidence.

## C12-IR-001 — Important, resolved by owner

The initial runner writes an accepted checkpoint and then publishes output rows, prints progress, and writes an attempt result before journal commit. An ordinary exception in these post-checkpoint operations enters `run_chunk`'s `journal.fail()`. The failure file unconditionally says `physical_prefix_advanced=False`; `resume()` refuses a failure before invoking checkpoint reconciliation. A durable accepted generation can therefore be stranded while the reported cursor and prefix remain old. Crash-only reconciliation does not resolve this caught-exception path. Owner was notified before launch; fix and targeted new evidence are required before scoped GO.

Owner repair records the caught exception separately, reconciles the matching immutable accepted checkpoint before marking terminal failure, and stops the chunk with the advanced exact cursor and no repeated trial. A new targeted post-publication exception check passes. Pending reconciliation remains explicitly distinct from no accepted checkpoint. Failure records no longer assert a false physical-prefix status.

## C12-IR-002 — Minor, resolved by owner

The one-trial effective control dictionary and its canonical hash initially existed only implicitly in the code. The production design calls for explicit total/effective controls, counts and both hashes. Runtime counters and total allocation semantics were already correct. Owner is adding the missing explicit provenance record.

Final runner stores total controls/hash in launch evidence and actual one-trial controls/hash, saved cursor and remaining allocation in each attempt's CONTROL_LINEAGE before any map.

## C12-IR-003 — Important, resolved by owner

The initial runner skipped epoch-zero diagnostics whenever the output file existed, without checking its completion hash or state binding. Resume did not reconcile or verify earlier accepted epoch rows; final completion checked times and field names only. Although new output rows were included in each accepted checkpoint transaction, later snapshots retained only that generation's transaction rows. This leaves prior output files outside a verified resume path. Require exact existing row verification/restoration from committed checkpoint transactions and an authoritative epoch-zero completion/state binding, without repeating native evaluation. Interrupted incomplete output publication must remain explicit.

Final runner stores cumulative authoritative output records in every accepted checkpoint, verifies them against exact epochs and accepted prefix-state hashes on resume, restores missing rows, and rejects changed rows. Epoch-zero completion records contain the full row, its hash and initial state/kernel binding; a row without a completion record is explicitly held for recovery. The new owner-authored lost/altered-row targeted case passes. No numerical evaluation is repeated for restoration.

All owners completed. Final scoped pre-native decision and hashes are recorded in INDEPENDENT_DECISION.json and REVIEWED_FILE_HASHES.json. Nineteen distinct new targeted cases pass in owner evidence. Actual h=0 native diagnostic and continuation are still unexecuted at this decision. No unresolved Important finding remains; whole-history admission remains HOLD_NOT_EVALUATED.
