# Attempt 4 — eight-chunk runtime-state stall

The first full-suite verifier grouped 61 test files into eight fresh Python processes. Chunk 1 passed (`29 passed`), while chunk 2 stalled without an assertion failure. Every chunk-2 file then passed when run in its own interpreter. The final verifier therefore ran every collected test file in a fresh interpreter, split across multiple sandbox commands to avoid cumulative process-budget throttling. No source or scientific equation changed.
