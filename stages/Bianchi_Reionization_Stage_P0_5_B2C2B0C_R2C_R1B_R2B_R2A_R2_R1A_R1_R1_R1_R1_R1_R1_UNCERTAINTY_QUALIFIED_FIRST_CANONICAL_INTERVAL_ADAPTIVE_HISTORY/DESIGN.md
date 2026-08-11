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
creates an immutable three-state generation and canonical record, then replaces
`LATEST.json` atomically on the same filesystem. Every record links to the prior
record hash. Deterministic payloads use sorted JSON metadata plus fixed-order
little-endian float64 arrays. Two rolling generations and snapshots every 64
accepted endpoints (plus final) are retained. Rejections are receipts, never
resumable candidate state.

## Claim boundary

Even an event-free complete run is an unsealed local candidate. Sparse rank,
named owner modes, event rebuild, point-trajectory containment, and whole-
history ledger closure are not exposed by the sealed result and remain for an
independent scientific stage.
