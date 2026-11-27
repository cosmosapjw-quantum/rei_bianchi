# Staged C2d bounded recovery

This staging directory was prepared while the original FOLLOWUP batch remained active. No scientific source under the running package was modified and no physical workload was launched here.

After the original launcher terminates at its fixed 1800-second cap and confirms complete owned-process cleanup, integrate only these five code files:

- `code/recovery_support.py` and `code/prepare_recovery.py`: new scalar-only recovery helpers.
- `code/analyze_states.py`: minimal `PARTIAL_BATCH_INDEX.json` collector branch.
- `code/mpi_batch.py` and `code/launch_ncp.py`: explicit local-unbound OpenMP environment plus MPI-rank affinity telemetry.

The staged `task_worker.py` and `run_bounded.py` are exact unchanged originals and need not be copied. All native libraries and scientific algorithms stay fixed. The root-owned `analyze_all.py` may make its separately reviewed collector adaptation; the helper permits this analysis file but pins the two execution-boundary changes to exact registered SHA256 values.

The local environment correction acts before mpirun starts: explicit `binding='none'` sets `BASS_LOCAL_UNBOUND=1` and `OMP_PROC_BIND=FALSE`; subsequent worker environments inherit that policy. Explicit `binding='core'` resets a stale local marker and retains `OMP_PROC_BIND=close`. Existing default NCP binding remains core. The native ABI-only manufactured evidence demonstrates the original close policy narrowing an unbound child from CPUs 0–8 to CPU 0; FALSE preserves all nine allowed CPUs in each of three fresh MPI ranks. This is effective-affinity evidence, not a timing or speedup benchmark.

After integrating the helpers and recording the new source identity:

```bash
python code/prepare_recovery.py --root /workspace/scratch/0b54847633d9/BASS_HE_C2D_LARGE_R_SCALED_20261001_v1
```

This refuses an original launch unless its actual receipt records returncode 124, timed_out=true, source_unchanged=true, cleanup_complete=true, preflight_passed=true and wall_cap_seconds=1800. It first creates the explicit `evidence/FOLLOWUP_MPI/PARTIAL_BATCH_INDEX.json`. It does not fabricate or overwrite an original `BATCH_SUMMARY.json`.

It then creates `inputs/RECOVERY_TASKS.json` and `review/RECOVERY_PLAN.json` for only never-started or interrupted-without-result tasks, with distinct `rec_` IDs and unchanged scientific parameters/state references. Any existing RESULT without a validated PASS TASK_EXECUTION requires manual classification and prevents automatic replay. Validated completed tasks are excluded. Finalized failures remain explicit and also require classification.

A narrowly scoped post-timeout classification is available for explicitly selected finalized `WORKER_NONZERO_EXIT/-9` tasks. `timeout_kill_classification(root, batch, explicit_task_ids)` verifies that each selected task has no RESULT or DATA, empty stdout/stderr, unchanged input and artifact identities, zero OOM/oom_kill deltas, and exactly one actual whole-batch cleanup SIGKILL record matching its task ID, namespace PID, start ticks and ownership batch token. The pinned cleanup guard binds the recorded namespace/boot identity at signaling time. Preserve its returned document unchanged as separate immutable evidence after independent review, then supply `--classification review/TIMEOUT_TASK_CLASSIFICATION.json`. The existing partial index and every original failed class remain unchanged. Other finalized failures are still blocked. Final recovery verification rechecks this evidence and its binding. An existing byte-equivalent partial index is reused without overwriting it.

The plan counts every existing task directory as a started attempt, including failures and interrupted tasks, and records the full manifest upper bound separately. Parity attempts remain ≤4, overlap attempts ≤240, and no new eigenstates are permitted. All recorded launcher elapsed times are conservatively charged, including failed preflight time. The recovery cap is `min(1800, floor(3600 - charged_prior_wall - 30))` seconds. The ordinary launcher must still pass a fresh resource gate before executing that exact cap.

Use the existing `run_bounded.py` with the plan's printed cap and the new manifest/output directory; source the existing `runenv.sh` first. This staging package does not itself start the recovery computation.

After recovery terminates:

```bash
python code/prepare_recovery.py --root /workspace/scratch/0b54847633d9/BASS_HE_C2D_LARGE_R_SCALED_20261001_v1 --verify
```

Only full immutable task coverage, no completed-task replay, valid source/backend/state binding, preserved original cap, final cleanup and total charged wall ≤3600 can yield `WHOLE_BATCH_TIMEOUT_RECOVERED_WITHIN_ORIGINAL_BUDGET`. Scientific raw/scaled/continuation/parity gates are separate and full C2 remains false.

Four environment/affinity manufactured tests and ten recovery file-fixture tests passed. Their actual logs and the independent three-rank affinity output are under `evidence/`. No scientific solver, operator integral or benchmark was invoked by these tests.
