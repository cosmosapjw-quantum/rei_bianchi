# Attempt 4 — external watchdog timeout

The corrected canonical propagation runner was launched through an external
`timeout 35s` wrapper.  The 24-policy calculation requires longer than 35 s on
the locked 46,080-node state and was terminated before any result table or
`results.json` was written.

Classification: `RUNTIME_WRAPPER_TIMEOUT_NOT_SCIENCE_EVIDENCE`.

This attempt is not evidence of a hard-gate, local-error, branch-width, or
physical-history failure.  The next attempt must run the same locked runner in
an unrestricted subprocess and record its actual exit code.
