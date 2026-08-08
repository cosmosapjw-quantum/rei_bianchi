# Attempt 1 — long-lived endpoint worker runtime stall

The first all-lane coherent endpoint sweep accumulated numerical-runtime/BLAS state and stalled after a subset of endpoint solves. No scientific assertion failed. The evidence architecture was changed to one fresh process per endpoint with SHA-addressed caches and deterministic consolidation. This change affects orchestration only.
