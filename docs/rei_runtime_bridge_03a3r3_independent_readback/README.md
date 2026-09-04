# REI-RUNTIME-BRIDGE-03A3-R3 — Independent ruleset readback

This node is the minimal GREEN successor to the executed Draft PR #51 RED and the temporal-semantics RED observed on Draft PR #52.

```text
admin source parent  PR #50 / a24f4710a1a105443da4c1bc5c7191ca1a4e33a5
executed missing-module RED
                     PR #51 / 6827ec513cdee78fbc808e08692cab3b7dfc915e
first GREEN source   7ba95fd50cd641e546ae42ab80b62a4ea4f72772
temporal RED         07b7c03131f674579937be0368d24772fa524cbb
```

## Purpose

The administrator's mutation receipt is historical evidence that a client reported an operation. It is not proof of present GitHub state. The source therefore separates three temporal questions:

```text
1. Was the original administrative operation internally coherent?
2. Did it finish while its original protection receipt was valid?
3. Does a fresh independent GET-only readback establish the state now?
```

The original source-protection receipt **may be expired at the later independent audit**. Requiring it to remain currently fresh would conflate retrospective provenance with current authorization and introduce an artificial 300-second race. What is required is:

```text
operation_started
<= admin_receipt_created
<= original_source_receipt_generated
<= operation_completed
<= original_source_receipt_expires
```

Current authorization evidence comes only from the independent live GETs and the newly emitted fresh receipt.

## Inputs and cross-binding

The active surface `independent_readback_audit_v2.py` validates three canonical, colocated records:

```text
ADMIN_MUTATION_RECEIPT.json
SOURCE_PROTECTION_RECEIPT.json
RAW_OPERATION_EVIDENCE.json
```

It cross-binds schema, fixed authority, repository, global ref, ruleset ID, exact operation ordering, response SHA-256 values, timestamps, active enforcement, no-bypass policy, and absence of attempt/native effects.

The byte-pinned v1 module remains an implementation donor. The v2 surface changes only the temporal semantics above and exact-pins both the donor blob and the PR #50 administrator-client blob.

## Independent live reads

After the historical bundle passes, the active surface performs only:

```text
GET repository rulesets
GET exact ruleset details
GET prospective branch effective rules
GET exact global attempt ref
```

It requires active `update`, `deletion`, and `non_fast_forward` protection from the exact ruleset ID, no `creation` rule, no bypass actors, and HTTP 404 for the final attempt ref.

Only then does it atomically publish:

```text
INDEPENDENT_AUDIT_RECEIPT.json
AUDITED_FRESH_SOURCE_PROTECTION_RECEIPT.json
SHA256SUMS
```

The fresh receipt remains controller-compatible and binds the independent audit plus the original administrator and source receipts.

## Source verification

```bash
python -m unittest -v \
  tests.governance.test_rei_runtime_attempt_ref_ruleset_independent_readback_red

python docs/rei_runtime_bridge_03a3r3_independent_readback/\
independent_readback_audit_v2.py --self-test

python docs/rei_runtime_bridge_03a3r3_independent_readback/\
verify_source_index.py
```

## Actual use after administrator apply

Run only from the exact published active release. Use a new persistent output path outside every repository and temporary directory.

```bash
python docs/rei_runtime_bridge_03a3r3_independent_readback/\
independent_readback_audit_v2.py \
  --repo "$PWD" \
  --expected-head '<exact-active-head>' \
  --expected-tree '<exact-active-tree>' \
  --admin-receipt /absolute/admin/ADMIN_MUTATION_RECEIPT.json \
  --source-receipt /absolute/admin/SOURCE_PROTECTION_RECEIPT.json \
  --operation-evidence /absolute/admin/RAW_OPERATION_EVIDENCE.json \
  --output-root /absolute/persistent/REI_03A3R3_AUDIT_UTC
```

The token is read from `GITHUB_TOKEN`. The historical source receipt need not still be fresh. The newly emitted audited receipt has a fresh 300-second validity window and must be consumed, if at all, only by a later separately reviewed target-host preflight/controller node.

## Strict boundary

This package cannot create or modify a ruleset or Git ref. It cannot create a local attempt lease, write a dispatch intent, import the production bridge, run native code, start the first canonical interval, or admit a provider.

Current live state at source repair remains:

```text
repository ruleset        NOT_CREATED
global attempt ref        ABSENT
remaining native attempts 1
native runtime            NOT_RUN
```
