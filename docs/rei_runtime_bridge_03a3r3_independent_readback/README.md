# REI-RUNTIME-BRIDGE-03A3-R3 — Independent ruleset readback

This node is the minimal GREEN successor to the executed Draft PR #51 RED.

```text
admin source parent  PR #50 / a24f4710a1a105443da4c1bc5c7191ca1a4e33a5
executed RED         PR #51 / 6827ec513cdee78fbc808e08692cab3b7dfc915e
RED workflow         33823494482 / SUCCESS
RED fingerprint      9 FileNotFoundError errors; no mutation or attempt state
```

## Purpose

The administrator's mutation receipt is evidence that an administrative client reported an action. It is not proof that the current GitHub state still matches the declared protection. This package therefore performs a separate, GET-only audit.

It validates three canonical input records:

```text
ADMIN_MUTATION_RECEIPT.json
SOURCE_PROTECTION_RECEIPT.json
RAW_OPERATION_EVIDENCE.json
```

The validation cross-binds:

- schema, fixed authority, repository and global ref;
- ruleset ID, name, active enforcement and no-bypass policy;
- exact operation ordering;
- response SHA-256 values for ruleset details, effective rules and ref absence;
- timestamp ordering;
- the 300-second source-receipt lifetime;
- explicit absence of attempt-ref, local-lease and native-runtime effects.

It then independently performs these live reads:

```text
GET repository rulesets
GET exact ruleset details
GET prospective branch effective rules
GET exact global attempt ref
```

Only after all four reads pass does it publish, as one atomically renamed directory:

```text
INDEPENDENT_AUDIT_RECEIPT.json
AUDITED_FRESH_SOURCE_PROTECTION_RECEIPT.json
SHA256SUMS
```

The fresh protection receipt retains the controller-compatible schema and additionally binds the independent audit receipt plus the original administrator and source receipts.

## Source verification

```bash
python -m unittest -v \
  tests.governance.test_rei_runtime_attempt_ref_ruleset_independent_readback_red

python docs/rei_runtime_bridge_03a3r3_independent_readback/\
independent_readback_audit.py --self-test

python docs/rei_runtime_bridge_03a3r3_independent_readback/\
verify_source_index.py
```

## Actual use after administrator apply

Run only from the exact published GREEN release. Supply the exact commit/tree and a new persistent output path outside the repository.

```bash
python docs/rei_runtime_bridge_03a3r3_independent_readback/\
independent_readback_audit.py \
  --repo "$PWD" \
  --expected-head '<exact-green-head>' \
  --expected-tree '<exact-green-tree>' \
  --admin-receipt /absolute/admin/ADMIN_MUTATION_RECEIPT.json \
  --source-receipt /absolute/admin/SOURCE_PROTECTION_RECEIPT.json \
  --operation-evidence /absolute/admin/RAW_OPERATION_EVIDENCE.json \
  --output-root /absolute/persistent/REI_03A3R3_AUDIT_UTC
```

The token is read from `GITHUB_TOKEN`. The input source-protection receipt must still be fresh, so this audit is intentionally immediate. If it has expired, run the PR #50 client in read-only mode to generate a new source receipt before auditing.

## Strict boundary

This package cannot create or modify a ruleset or Git ref. It cannot create a local attempt lease, write a dispatch intent, import the production bridge, run native code, start the first canonical interval, or admit a provider.

Current live state at source creation remains:

```text
repository ruleset       NOT_CREATED
global attempt ref       ABSENT
remaining native attempts 1
native runtime           NOT_RUN
```
