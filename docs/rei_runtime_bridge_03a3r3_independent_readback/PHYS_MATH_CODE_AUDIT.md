# PHYS-MATH-CODE audit — independent ruleset readback

## Current claim

The active v2 surface audits the historical administrator bundle and then establishes present server state through fresh GET-only reads. It does not mutate GitHub or execute native code.

## Actual evidence

- missing-module RED: 9/9 `FileNotFoundError` errors observed on PR #51;
- first GREEN: nine-method contract, self-test, exact source index and read-only live state passed;
- hostile temporal tests then exposed one error and one failure on exact commit `07b7c031...`;
- active repair is versioned, test-first and exact-pins the v1 donor blob;
- no POST, PATCH, DELETE, lease, dispatch or native controller surface is present in the active source.

## Root cause

The first GREEN called historical-bundle validation with `require_current_freshness=True`. This converted an original execution receipt into a current authorization token. It also failed to require `operation_completed <= original_receipt_expires`.

## Minimal repair

```text
historical bundle:
  validate schema, TTL and original operation-time ordering
  do not require freshness at later audit time

current state:
  require fresh independent GitHub GETs
  emit a new 300-second controller-compatible receipt
```

## Ranked residuals

### P1 — actual ruleset and actual audit remain unexecuted

Source tests cannot establish live server protection. The repository ruleset must be installed by the PR #50 admin client and then audited by this active surface.

### P1 — output publication and controller consumption are separate nodes

The new receipt is only valid for 300 seconds. A later target-host preflight/controller must revalidate it or perform the PR #49 immediate live revalidation. Audit success alone must not reserve the attempt.

### P1 — administrator-level race remains outside source control

A repository administrator could alter rules after one GET and before a later ref POST. The controller reduces but cannot eliminate this server-level transaction gap.

### P2 — v1 donor remains present

The byte-pinned v1 file is retained for ancestry and implementation reuse but is not the active CLI surface. Documentation, workflow and source index must consistently point to v2.

### P2 — unauthenticated CI readback is visibility-limited

Source CI verifies only that the endpoint returns a list and the exact ref remains absent. It cannot attest the future private authenticated ruleset details before the admin operation occurs.

## Disposition

```text
TEMPORAL_SEMANTICS_REPAIR_SOURCE  pending exact-head GREEN
ACTUAL_RULESET                    not created
ACTUAL_INDEPENDENT_AUDIT          not run
GLOBAL_ATTEMPT                    not reserved
NATIVE_RUNTIME                    not run
```
