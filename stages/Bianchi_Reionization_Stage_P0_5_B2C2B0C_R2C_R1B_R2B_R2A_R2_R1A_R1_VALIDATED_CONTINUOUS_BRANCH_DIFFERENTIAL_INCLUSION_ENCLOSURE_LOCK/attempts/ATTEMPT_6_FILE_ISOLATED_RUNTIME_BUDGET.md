# Attempt 6 — full file-isolated regression exceeded the execution budget

A fresh interpreter was launched per collected test file with external pytest plugins disabled and BLAS threads pinned to one.  The run completed 17 of 56 files with zero assertion failures before the parent command reached its execution-time limit.  The repeated import/startup cost, rather than a scientific assertion, was the blocker.

This partial run is not counted as a full-suite PASS.  Final verification uses the complete stage suite, independent validators, repository verifier, and a fresh monolithic full-suite command.  The partial progress log is retained.
