# Decision log

## 2026-08-11 — process boundary

Use one short-lived process per lane/attempt, three lanes concurrently. Reject
persistent workers due prior BLAS/runtime-state stalls and numerical threads due
shared imported state and oversubscription.

## 2026-08-11 — numerical/adaptive scope

Compose sealed `run_step` without copying or reordering it. Lock partition 2048,
six bisections, 131072 common ticks, common all-lane acceptance, two rolling
generations, and snapshots every 64 endpoints.

## 2026-08-11 — events and result status

Fail closed at real table events because no production callback/rebuild exists.
Synthetic localization is not relabeled. All local results remain unsealed; no
global pointer, registry, ledger, or authorization is updated.
