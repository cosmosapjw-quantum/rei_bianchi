# ATTEMPT 4 — long-lived runtime stall

Classification: `EXECUTION_ARCHITECTURE_STALL_NOT_SCIENCE_FAILURE`.

Each shape lane, run in a fresh Python process, completed all eight policies in roughly 15–18 seconds. Repeated attempts to execute all lanes inside one long-lived process either stalled past the command limit or completed nondeterministically. This matches the repository's prior JAX/BLAS extension-state accumulation pattern and is not a fixed-point or ledger failure.

Resolution: one fresh process per shape lane, single-thread BLAS variables, SHA-256-receipted JSON/NPZ worker artifacts, deterministic parent merge. The successful single-process science bytes are retained solely as a parity reference and will not be the final load-bearing execution receipt.
