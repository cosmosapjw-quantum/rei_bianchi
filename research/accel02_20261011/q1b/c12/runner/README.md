# C12 whole-history chunk driver

The driver starts from a separately prepared P0 child of PILOT02 gen3. The child binds the full target z=15.9 to 4 (4.011926941800233e16 s), not a short pilot endpoint. Root must include source_paths() in prepare_transition(...,extra_dependency_paths=...).

Run one cooperative chunk:

```bash
python -u research/accel02_20261011/q1b/c11/integration/production/run_full_history_chunk.py --transition-bundle research/accel02_20261011/q1b/c12/evidence/C2_FULL001/TRANSITION_RESULT.json --run-directory research/accel02_20261011/q1b/c12/evidence/C2_FULL001/RUN --new-attempt-cap 3 --wall-s 45
```

Repeat only after CHUNK_ATTEMPT_BOUNDARY, CHUNK_WALL_BOUNDARY or CHUNK_RECOVERED_COMMIT_BOUNDARY. Each invocation retains the global counters and executes only previously unstarted attempts. ALLOCATION_EXHAUSTED is a normal explicit stop requiring a new prospective allocation, not a success or implicit reset. FAILED_ATTEMPT preserves inputs, traceback, notes, and inflight transaction; no automatic numerical retry. An interrupted accepted checkpoint can reconcile its embedded exact transaction and output rows without numerical replay. Inflight work without a committed accepted checkpoint fails closed.

Seven new cheap transaction cases passed. The first five required an absent implementation; the sixth required the caught post-commit exception reconciliation API. The seventh restores a missing authoritative output record and rejects a changed row with the same time and keys. Every accepted checkpoint retains all produced output records; resume restores missing records and rejects byte-different records before numerical work. Epoch0 additionally requires its DONE receipt, stored full record and hash/state/kernel identity; an existing row without its receipt is explicit pending recovery.

No old numerical validation or native trajectory was executed by this owner. Syntax/CLI help checked separately.

Every new accepted macro checkpoint includes the full physical half-step prefix, cursor, full-target/control/dependency binding, and sparse diagnostics for both new half boundaries. Original parent prefix0..6 is unchanged. Exact129 epoch outputs use the real native endpoint kernel; row0 is one newly journaled h=0 opacity diagnostic with zero gas RHS. Observable records are built before accepted checkpoint publication, embedded in checkpoint metadata, and atomically written after it. Journal and output failures cannot silently roll back a durable accepted generation.

The 45 s bound is cooperative between complete attempts. It does not interrupt native work, guarantee wall time, or establish full-run feasibility. Checkpoint prefix replication is exact but storage grows quadratically; no compressed-history claim is made. Scientific admission remains false until the independent complete-history criteria are actually evaluated.
