# Benchmark attempt 0 — legacy trial-record API mismatch

The first cross-version benchmark assumed both implementations exposed
`PhysicalTrialSolver.trial_records`.  Commit `d978d09` predates that diagnostic
field, so the harness failed before timing.  No timing from this attempt is
load-bearing.  The harness was corrected to clear the field only when present.
