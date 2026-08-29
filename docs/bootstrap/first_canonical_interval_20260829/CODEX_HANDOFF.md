# Codex handoff — rei first canonical interval

Use the exact-pinned prompt and publication receipt. Preserve all existing
worktrees and untracked files.

Materialize the immutable package, verify manifest/offline/live validation and
the exact rec monitoring lock. Create
`agent/runtime/first-canonical-interval-20260829-r1` from the immutable package
commit.

Execute REI-BOOTSTRAP-00 → REI-ENDPOINT-01. If endpoint parity passes, continue
in the same run to REI-FIRST-INTERVAL-02, REI-AUDIT-03 and REI-DELIVER-04.
Do not reactivate the historical corrected-ODE candidate or import rec numerical
state. A table event without a certified callback is an accepted STOP boundary,
not permission to extrapolate.

Final report: STATUS / ACTUAL PROGRESS / VERIFIED / DEFERRED / BLOCKERS / NEXT.
