# PHYS-MATH-CODE audit

## Current claim

Draft PR #49 closes source-level freshness and live pre-reservation readback. This child supplies a source-only, admin-scoped way to create and attest the required server rule.

## Actual evidence

- the ruleset payload targets only `refs/heads/attempt-ledger/**`;
- initial creation remains allowed;
- update, deletion, and non-fast-forward mutation are forbidden;
- bypass actors are empty;
- the script has a single permitted POST endpoint: repository ruleset creation;
- exact ruleset details, prospective effective rules, and exact global-ref absence are read back;
- mutation evidence and GET-only controller-consumable evidence are separate;
- the source workflow has `contents: read` and cannot apply the ruleset;
- no production bridge or worker module is imported.

## Ranked residuals

### P1 — actual server mutation not performed by the source commit

The repository ruleset is not established until an administrator executes `--apply` and the exact readback succeeds. Source tests cannot substitute for this result.

### P1 — administrator mutation between live GET and global POST

GitHub does not expose one transaction combining policy readback and ref creation. PR #49 minimizes this window by performing a fresh GET-only revalidation immediately before POST and binding its hash. Under an adversarial repository-administrator model, a later admin mutation remains a residual risk; no source-only patch can make GitHub administration cryptographically immutable.

### P1 — output durability is operator-dependent

The actual admin receipts must be written to a persistent root, checksum-manifested, and published append-only. A temporary output directory is not acceptable.

### P2 — prospective branch-rule response semantics

The implementation requires each load-bearing effective rule to carry the exact ruleset ID. If GitHub changes the response schema, the operation fails closed and must be audited rather than relaxed silently.

### P2 — ruleset name collision

More than one ruleset with the canonical name is rejected. An existing same-name but nonidentical ruleset is not modified automatically.

## Strongest failure mode

A successful ruleset POST followed by an interrupted readback can leave the server changed without a complete source-protection receipt. The script records `ruleset_creation_may_have_occurred=true`, performs no rollback, and requires a later read-only reconciliation. This is preferable to deleting or rewriting a possibly valid protection rule.

## Minimal condition for support

Only the following may close this admin node:

```text
exact ruleset details                         PASS
prospective branch effective rules            PASS
exact global attempt ref                      HTTP 404
ADMIN_MUTATION_RECEIPT                        PASS
fresh SOURCE_PROTECTION_RECEIPT               PASS
attempt ref / local lease / dispatch / native absent
```

## Disposition

```text
ADMIN_HANDOFF_SOURCE             CANDIDATE_PENDING_EXACT_HEAD_CI
ACTUAL_SERVER_PROTECTION         NOT_YET_ATTESTED
GLOBAL_ATTEMPT                   NOT_RESERVED
NATIVE_RUNTIME                   NOT_RUN
```
