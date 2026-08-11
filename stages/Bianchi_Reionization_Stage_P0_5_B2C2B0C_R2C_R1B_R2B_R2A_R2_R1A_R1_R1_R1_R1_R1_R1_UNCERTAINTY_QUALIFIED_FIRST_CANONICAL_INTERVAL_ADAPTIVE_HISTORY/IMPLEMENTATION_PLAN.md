# Implementation plan

1. Lock predecessor hashes, lanes, gates, dyadic grid, process model, and claim
   boundary before calculation.
2. Characterize the sealed partition-2048 microstep without running the full
   interval.
3. Add failing tests for deterministic state, common commit, bisection, event
   fail-close, worker failure, and resume identity.
4. Implement state I/O, a short-lived one-lane worker, and deterministic
   three-lane supervisor around the unchanged sealed kernel.
5. Add preflight, launcher, compact result packager, and local pull/run/push
   guide for Ubuntu 24.04 / Ryzen 5900X / 64 GB.
6. Run unit, parity, serial/parallel, corruption, scope, and independent review
   checks; do not run the full interval.
7. Commit and push the optimization branch without changing global state.
