# Runtime design

## Numerical boundary

The predecessor's sealed `interval_discrete_map.run_step` remains the only
load-bearing map. It already vectorizes 46,080 nodes and stacked small matrix
solves. This stage neither copies nor edits it; only unchanged reductions and
transport validation are vectorized.

Each interval runs in three independent short-lived workers, one per lane. A
worker evaluates full step, first half, then dependent second half in the
validated order. All three outputs commit together or none commits.

Persistent pools are excluded because repository evidence records accumulated
BLAS/runtime-state stalls. Numerical threads are excluded; the launcher forces
BLAS/OpenMP counts to one and recommends three workers on Ryzen 5900X.

## Protocol and adaptive grid

Process health is separate from science classification. A valid gate rejection
exits zero with `transport_status: OK`; nonzero is reserved for runtime/protocol
failure. Every envelope embeds lane, dyadic interval, hex times, input/kernel
hashes, parent hash, classifications, gates, widths, local error, ledgers, and
candidate hash. Missing, duplicate, stale, or mismatched jobs fail before a
transition.

The interval uses `2048 * 2^6 = 131072` integer ticks. A base segment is 64
ticks. An ordinary gate failure bisects only the current interval for all lanes,
to depth six. A table event stops and preserves the parent because arithmetic
bisection cannot supply the absent certified callback/rebuild.

## Atomic commit

Workers write only to a unique temporary attempt directory. Common acceptance
creates an immutable three-state generation and canonical record. Each durable
transition then publishes in the fixed order `transition journal -> LATEST ->
CONTROL`. The journal is the resume authority: it replays ACCEPT, BISECT, STOP,
pause, and completion transitions, derives counters/cursors, and binds every
attempt receipt by path and SHA-256. ACCEPT also binds its accepted record; the
record chain binds each lane's parent state to the preceding candidate state.

A persistent regular `.RUN.lock` inside the owned run directory is acquired
nonblocking before coordinator or packager reads run state. It is never
unlinked, is not inherited by workers, and its device/inode identity is bound
to the immutable run-owner marker. The lock is shared explicitly by package
validation so runner, resume, and package cannot race. Recovery validates the
journal-selected state/history/generation first, recognizes at most one fully
validated next-attempt receipt, removes only its positively owned pre-journal
artifacts in runner repair mode, validates snapshots, and repairs `LATEST` then
`CONTROL` last. Packaging is validate-only: any needed repair fails without
changing source bytes, while the same lock remains held through no-clobber
archive and sidecar publication.

Deterministic payloads use sorted JSON metadata plus fixed-order little-endian
float64 arrays. Two rolling generations and snapshots every 64 accepted
endpoints (plus final) are retained. Rejections are immutable receipts, never
resumable candidate state.

## Runtime closure

Production execution requires a clean tracked worktree, a matching immutable
preflight whose complete check set passes, the default worker hash, and exact
pinned NumPy/SciPy/pandas plus their load-bearing dependency closure. The
preflight SHA-256 is bound into run ownership, metadata, and the transition
journal. JAX presence is rejected. Every job, state, checkpoint, record, and
receipt carries the runtime-contract SHA-256.
Tests may inject a fake worker only through an explicit test-only seam whose
artifacts cannot be packaged as science candidates.

## Claim boundary

Even an event-free complete run is an unsealed local candidate. Sparse rank,
named owner modes, event rebuild, point-trajectory containment, and whole-
history ledger closure are not exposed by the sealed result and remain for an
independent scientific stage.
