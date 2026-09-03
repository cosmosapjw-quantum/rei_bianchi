# Local administrator prompt — REI 03A3-R2

Operate only on the exact admin-handoff release descended from:

```text
771363866d5de436c3218be56d81a310b091874b
```

## Required preconditions

- The repository origin is `cosmosapjw-quantum/rei_bianchi`.
- The handoff source-index verifier passes.
- The fixed global attempt ref is still absent.
- No native attempt-state file exists.
- The token has repository Administration write permission.
- The output root is new, absolute, persistent, outside `/tmp` and outside every Git worktree.

## Failure-safe source verification

```bash
set +e
set +u
set +o pipefail 2>/dev/null || true

python -m unittest -v \
  tests.governance.test_rei_runtime_attempt_ref_server_ruleset_handoff
RC_TEST=$?

python docs/rei_runtime_bridge_03a3r2_admin_ruleset/\
apply_and_attest_ruleset.py --self-test
RC_SELF=$?

python docs/rei_runtime_bridge_03a3r2_admin_ruleset/\
verify_source_index.py
RC_INDEX=$?

printf 'tests=%s self=%s index=%s\n' "$RC_TEST" "$RC_SELF" "$RC_INDEX"
```

Do not continue unless all three return zero.

## Apply and attest

```bash
export GITHUB_TOKEN='REDACTED'
OUT="$HOME/Dropbox/bianchi/_runtime_receipts/REI_03A3R2_RULESET_$(date -u +%Y%m%dT%H%M%SZ)"

python docs/rei_runtime_bridge_03a3r2_admin_ruleset/\
apply_and_attest_ruleset.py \
  --apply \
  --output-root "$OUT"
RC=$?

printf 'admin_rc=%s\nreceipt_dir=%s\n' "$RC" "$OUT"
```

## Required terminal result

```text
admin_rc = 0
ADMIN_MUTATION_RECEIPT status =
  PASS_RULESET_CREATED_AND_READ_BACK
  or PASS_EXISTING_RULESET_READ_BACK
SOURCE_PROTECTION_RECEIPT status =
  PASS_ATTEMPT_REF_SERVER_PROTECTION
global_ref_http_status = 404
global_ref_absent = true
attempt_ref_created = false
local_lease_created = false
native_runtime = NOT_RUN
```

Preserve the entire output directory and compute a SHA-256 manifest. Then stop and publish an append-only readback receipt. Do not run target-host Section-0, create the global attempt ref, create a local lease, dispatch the worker, run the first interval, or admit a provider in this node.
