# Corrected bootstrap budget handling

Root-authorized one-repair contract: `/workspace/scratch/d855c1e0c0ed/contracts/providers/BOOTSTRAP_REVIEW_REPAIR_CONTRACT.md`.

Corrected source is `bootstrap.py`; `historical_before_budget_repair/` preserves the original recovered bootstrap, prior fixture-repaired tests, all prior raw logs and record unchanged. No prior logs were rewritten. `BUDGET_REPAIR.diff` is the exact two-file source/test change from that preserved version.

Engine records whether cumulative state existed at initialization. The partial legacy case-only receipt-budget inference is removed. Complete legacy inventory returns no-work without writes; incomplete state-less inventories with receipt/prerequisite/bootstrap-log evidence stop INPUT_BUDGET_UNKNOWN before launch or state save. Existing bootstrap state retains its cumulative budget. Empty preparation remains runnable.

Updated owned-partial fixture creates its prior cumulative state through Engine.run_one. Added legacy receipt-only/retained-file, prerequisite-only/command/outcome/stderr-only, and complete legacy no-work regression coverage. The five affected tests pass (exit 0); the previous unaffected full suite and summary fixtures are reused, not rerun. Measured receipt: wall 1.1102544400000625 seconds, child CPU 0.696016 seconds, one test process, injected serial bootstrap executor. Raw stdout/stderr and the exact command are stored separately.

Requested execution identity: lower-tier coding agent. Observed runtime model identity was unavailable and is not asserted; Python runtime metadata is in the receipt. Limits remain 90 attempts / 2400 CPU seconds / 900 wall seconds / maximum 4 workers, actual bootstrap serial 1. All eight pinned source file hashes/bytes and historical logs rechecked unchanged. No IVP, actual point check, rendering, full suite repeat, full83 integration, commit or push. Full fresh83 NOT_RUN. Admission remains PENDING_INDEPENDENT_REVIEW.
