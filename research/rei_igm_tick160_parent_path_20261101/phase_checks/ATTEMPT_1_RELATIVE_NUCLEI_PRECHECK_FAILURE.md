# Actual second GitHub Actions attempt failure, source-unit preflight (preserved)

- First fix PR #336 HEAD `41e3292712822eb3bdee8533a26bb14a8971598b`, GH run `41274114476` FAIL, 3/3 jobs.
- All three source identity checks passed. Each job stopped before `m.run_step` on `ValueError: original nuclei mismatch`.
- Root cause: this new probe's additional nucleus check used unjustified absolute difference `>1e-12` against source populations whose unit/magnitude are not 1. It had not matched the original source helper's scale-aware addition semantics. The existing original 26-event source is unchanged and the original `src.representative` already correctly checks in-box and totals.
- Repair: replace with 64 machine epsilon times relative H/He element total. Normalized residual only, **not a change of any original state-width or local-truncation gate**. Add positive large-unit and negative true-relative-error regression tests. Diagnostic output intervals tested with the same rounding-scale principle.
- Both attempts stopped before the real 26-event nonlinear full/half map, so neither is an empirical physical failure. Execute one bounded third targeted attempt; if not a productive diagnosis, checkpoint and stop, do not start a new audit loop.
- ORIGINAL_FIRST_INTERVAL=BLOCKED_MINIMUM_STEP, CENTRAL_DAG=28/88_REPORTED, CANONICAL_DELTA=0.
