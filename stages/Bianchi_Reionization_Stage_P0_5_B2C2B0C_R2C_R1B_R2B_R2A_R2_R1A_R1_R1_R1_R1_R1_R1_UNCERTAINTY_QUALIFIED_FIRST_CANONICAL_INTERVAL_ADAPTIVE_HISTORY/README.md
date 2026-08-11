# Uncertainty-qualified first canonical interval: pre-calculation runtime

This unsealed successor adds orchestration, fresh-process lane parallelism,
deterministic state transport, and resumable checkpoints around the sealed
predecessor kernel. It does not change equations, floating-point operation
order inside that kernel, tolerances, lanes, forcing, or promotion boundaries.

Current classification: `PRECALCULATION_RUNTIME_ONLY_NO_SCIENCE_RESULT`.

The complete 2048-segment calculation is intentionally not run here. Follow
`LOCAL_RUN_GUIDE.md` locally and push the compact candidate bundle for audit.
All outputs remain `CANDIDATE_UNSEALED_LOCAL_EXECUTION`.

The runtime fails closed on dependency/runtime drift, non-finite values, invalid
worker envelopes, hash or journal mismatch, missing/duplicate lanes,
minimum-step exhaustion, concurrent run/package access, and table events. A
persistent `.RUN.lock`, immutable transition journal, exact runtime contract,
and journal-bound receipts make resume and packaging validate the same owned
checkpoint before any repair or publication.
The predecessor exposes no production continuous event callback/topology
rebuild, so an event preserves the parent and reports
`TABLE_EVENT_RESTART_IMPLEMENTATION_REQUIRED`.

Only this new stage directory is changed. Global state, pointers, registries,
ledgers, predecessor bytes, and production authorization remain unchanged.
