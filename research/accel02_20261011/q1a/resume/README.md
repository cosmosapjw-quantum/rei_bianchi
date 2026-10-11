# Optional G2 wall-only continuation handoff

Status: implemented and software-tested, **not executed**. Independent source review conditionally allows the single wall-only diagnostic trial; root has selected that conditional phase in `PLAN_ADDENDUM_C08C.md`. Production invocation still requires the original G2 terminal failure artifacts to exist, dual backup to complete, and actual manifest validation. If G2 finishes, do not use this capability. Actual restart parity is untested.

1. Create a terminal manifest from immutable G2 artifacts (read-only scientific data operation):

```sh
python3 research/accel02_20261011/q1a/resume/checkpoint.py \
  research/accel02_20261011/q1a/evidence/GAUSS2_FINE \
  research/accel02_20261011/q1a/resume/G2_TERMINAL_MANIFEST.json
```

2. Review the manifest SHA, exact `TimeoutError` reason, all prior gates, source/grid identities and backed-up terminal archive. Only then execute, at most once, in a new sibling directory:

```sh
python3 research/accel02_20261011/q1a/resume/run_wall_continuation.py \
  --manifest research/accel02_20261011/q1a/resume/G2_TERMINAL_MANIFEST.json \
  --manifest-sha REVIEWED_MANIFEST_SHA256 \
  --n1 research/accel02_20261011/n1 \
  --output research/accel02_20261011/q1a/evidence/GAUSS2_FINE_CONTINUED \
  --additional-wall-seconds 600
```

The wall budget is checked before each BDF step, matching the original driver. A single step and final artifact serialization may finish after the declared phase budget; the budget is not a process-kill timeout. Reconstruction/setup time is outside the numerical phase timer, as in the original driver. There is no automatic second continuation.

3. Immediately archive and dual-back up all completed or failed raw artifacts, including `predecessor/`, before postprocessing. If complete:

```sh
python3 research/accel02_20261011/q1a/resume/postprocess_continuation.py \
  research/accel02_20261011/q1a/evidence/GAUSS2_FINE_CONTINUED \
  --n1 research/accel02_20261011/n1
```

The result is `CONTINUATION_MOMENTS.json`, **not** an automatically admitted `MOMENTS.json`. The unchanged comparator rejects this state. Independent review must explicitly accept the original-operator/extra-BDF-restart distinction before using the separate diagnostic wrapper below. A completed resumed trajectory does not inherit a time-convergence certificate.

Artifacts preserve original `driver_as_run.py` as the operator/event reference, `resume_driver_as_run.py` as the executed continuation entrypoint, and `resume_checkpoint_as_run.py` as its validator. Both phases' raw artifacts and hashes are retained. All gas, radiation and cumulative counter values resume from the last accepted scaled state with original scales and original Cauchy ledger origins.

Tests performed: five pure manufactured artifact checks; Python compilation; CLI help. No production provider initialization, native call, RHS, ODE, RUN002, EVENT003, or Q0 execution was performed in preparing this capability.

4. A separate diagnostic comparator is now provided. It requires actual completed-chain review, distinct from the prospective code review. The review JSON schema is:

```json
{
  "schema": "rei.q1a.actual_continuation_review.v1",
  "decision": "ALLOW_DIAGNOSTIC_COMPARISON",
  "chain_sha256": "SHA256_OF_CONTINUED_RUN_CONTINUATION_JSON",
  "result_sha256": "SHA256_OF_CONTINUED_RUN_RESULT_JSON",
  "continuation_driver_sha256": "SHA256_OF_EXECUTED_RESUME_DRIVER"
}
```

After actual review:

```sh
python3 research/accel02_20261011/q1a/resume/compare_continuation_diagnostic.py \
  research/accel02_20261011/q1a/evidence/GAUSS1_FINE \
  research/accel02_20261011/q1a/evidence/GAUSS2_FINE_CONTINUED \
  research/accel02_20261011/q1a/resume/G1_G2_CONTINUED_DIAGNOSTIC.json \
  --actual-chain-review PATH_TO_ACTUAL_CHAIN_REVIEW_JSON
```

This wrapper checks unchanged frozen field budgets on all 24 fields at both 65 and 129 epochs, with each epoch set's own fine amplitude. Even if every numerical check passes, its status remains `CONTINUED_TRAJECTORY_DIAGNOSTIC_NOT_ADMITTED`; scientific admission and inherited time convergence are false. The extra initialization and distinct executed control source remain explicit.

The extra resume boundary is evaluated once and bound in `CONTINUATION_START.json`; its energy and photon-number residuals are included in the aggregate endpoint ledger maxima, without adding a 130th common sample. This additional saved-state point evaluation occurs only during an authorized continuation.

Validation additions: two manufactured diagnostic routing tests pass. They verify that equal trajectories cannot auto-admit and that the 65/129 epoch sets use their own amplitudes. Actual numerical restart parity remains **UNTESTED**.
