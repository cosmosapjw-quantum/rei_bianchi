# REI-RUNTIME-BRIDGE-03A3-R2 — Admin ruleset handoff

This directory is the source-only administrative handoff following Draft PR #49.

## Exact parent

```text
repository       cosmosapjw-quantum/rei_bianchi
parent PR        #49
parent commit    771363866d5de436c3218be56d81a310b091874b
parent tree      5e4396640c7c4c50b16130b5741195220aec5030
tested payload   34293f44e278426d60c83104d006ebdd127e0a0b
```

PR #49 has already closed the source-level freshness and live pre-reservation readback contract. This handoff does not repeat that implementation. It supplies the separate repository-administration operation required to make the declared protection real.

## What the operation may do

With explicit `--apply`, the script may create exactly one active repository ruleset:

```text
name             REI immutable attempt-ledger refs v1
pattern          refs/heads/attempt-ledger/**
update           forbidden
deletion         forbidden
non-fast-forward forbidden
creation         allowed
bypass actors    none
```

After creation, or when the exact ruleset already exists, the script performs GET-only readback of:

1. the exact ruleset details;
2. effective rules for the prospective attempt branch;
3. the exact global attempt ref, which must remain HTTP 404.

It writes two separate records:

```text
ADMIN_MUTATION_RECEIPT.json
  records whether the ruleset was created in this invocation

SOURCE_PROTECTION_RECEIPT.json
  a fresh GET-only rei-runtime-attempt-ref-protection-receipt/v1
  mutation_effect = NONE
  lifetime = 300 seconds
```

The separation is load-bearing: a mutation record is not itself reservation authority.

## What the operation cannot do

The script contains no endpoint or import path for:

```text
global attempt-ref creation/update/deletion
persistent local lease
dispatch intent
REI production bridge import
native worker
first canonical interval
provider admission
```

## Source-only validation

```bash
python -m unittest -v \
  tests.governance.test_rei_runtime_attempt_ref_server_ruleset_handoff

python docs/rei_runtime_bridge_03a3r2_admin_ruleset/\
apply_and_attest_ruleset.py --self-test

python docs/rei_runtime_bridge_03a3r2_admin_ruleset/\
verify_source_index.py
```

The GitHub Actions workflow has `contents: read` only. It cannot apply the ruleset.

## Actual administrative use

Use a new absolute persistent output directory and a token with repository Administration write permission:

```bash
export GITHUB_TOKEN='...'
python docs/rei_runtime_bridge_03a3r2_admin_ruleset/\
apply_and_attest_ruleset.py \
  --apply \
  --output-root /absolute/persistent/rei-03a3r2-$(date -u +%Y%m%dT%H%M%SZ)
```

Do not run this until the exact source head and workflow are read back. After a successful apply/readback, stop. Do not run target-host preflight or reserve the global attempt in the same operator session.

## Claim ceiling

```text
admin handoff source           candidate pending exact-head CI
repository ruleset             not created by this source commit
global attempt ref             absent
local lease / dispatch         absent
remaining native attempts      1
native runtime                 not run
first canonical interval       no pass
provider export                not authorized
scientific pass                not claimed
```
