# Nonlinear residual and correction diagnostic

This standalone standard-library module implements the supplied-packet, four-variable scaled linearized residual/Jacobian diagnostic defined in `CONTRACT.json`. The independent C9 verdict is `PASS_SCOPED`; the reviewed code commit is `e0d547521cd71047670d5c3967ca4289ea0db8b1`.

Actual SOURCE007 cause attribution remains on HOLD because the accepted-state residual/Jacobian telemetry packet is missing. The template contains null telemetry intentionally. The implementation does not establish a certified nonlinear, evolution or global error bound.

The archive preserves repository-relative paths under this unit. Runtime code is `nonlinear_budget.py` and has no third-party dependencies. Follow `CODEX_HANDOFF_PROMPT.md` and `HANDOFF.md` for continuation; `REPORT_KO.md` describes the scoped result. `SOURCE_BINDING_HANDOFF.md` and `NEXT_NATIVE_OBSERVER_PLAN.json` describe the future observer owner's source intake and binding obligations. They do not authorize changing the concurrently owned SOURCE009 solver or short-run work.

`PROGRESS_DAG.json`, the theory/coding stage records, checkpoint metadata and `DELIVERY_LOG.json` document twenty separate R1–R10/C1–C10 checkpoints. Each stage has its own Git commit and ZIP with completed Dropbox and Google Drive acknowledgments and matching sizes. The final C10 receipt uses its containing commit; the publisher response identifies the actual final commit and archive hash without an extra receipt-only commit.

Earlier snapshots remain immutable. Their stale top-level R1/R2 progress summaries are documented in the delivery log; C9 onward derives summary fields from the actual completed nodes. Final progress is `completed_through=C10`, with next owner intake `O1` and the actual-stage HOLD unchanged.

The final package receives one CRC, dependency-list and reviewed-runtime-member hash check. The completed C6 CLI evidence is reused, with no additional scientific or CLI execution for packaging. No private raw histories, checkpoints, production repository snapshot or full external search texts are included. Prior FULL005 PL results and their original budget/deadline are reused without replay or reset.
