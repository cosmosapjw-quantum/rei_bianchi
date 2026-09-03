# REI-RUNTIME-BRIDGE-03A2 — Authority-Binding TDD RED

## Exact lineage

```text
parent Draft PR #45
commit 6e9f590d945843495df0a03b293469947750f783
tree   c48172f66afbd1c3e9100eeaf047fb196dea28e2

intentional RED payload
commit c65fecc10c7c6310b494ad4b4de081b1ca57e1a6
tree   ea9d86a5ec493426a4425bababf2967759ca13c4
```

The parent import-order firewall remains valid: static preflight and the lease-owning controller do not import the production bridge, and the separate worker is the first production-runtime surface.

This node freezes a narrower but load-bearing gap in the authorization contract.  The final attempt is not yet bound to an immutable GitHub authority and the exact executing release bytes.

## Expected RED obligations

The test-only suite requires:

1. no public or production-callable `api_base` override;
2. typed constants for `https://api.github.com` and `cosmosapjw-quantum/rei_bianchi`;
3. preflight observations carrying exact authority, method, repository, ref, target, HTTP status, and ordinal;
4. preflight receipts bound to the controller's actual state root, output root, and successor receipt path;
5. the executing package to be the exact package inside the verified standalone checkout;
6. exact `HEAD:<path>` Git-blob binding for executable package files;
7. the complete 13-field successor toolchain to be rechecked immediately before global reservation;
8. server-side update/deletion protection for the attempt-ledger ref to be a required input.

## Exact execution result

```text
workflow  rei-runtime-authority-binding-red
run       33767960622
job       100690555079
result    FAILURE_EXPECTED

setup                         SUCCESS
checkout                      SUCCESS
PR45 ancestry assertion       SUCCESS
intentional RED test step     FAILURE
repository verify             SUCCESS — run 33767960673
```

The connector exposes the exact failed step but not the raw unittest log text.  The committed suite contains ten test methods; every method is constructed to reject the exact PR #45 source.  No formula or native-runtime failure is inferred from this workflow.

## Live attempt state

```text
global attempt ref            ABSENT on live GitHub GET (404)
repository-level rulesets      []
persistent local lease         NOT_CREATED
dispatch intent                NOT_CREATED
remaining native attempts      1
production bridge import       NOT_RUN_BY_THIS_NODE
native runtime                 NOT_RUN
first canonical interval       NO_PASS_FIRST_CANONICAL_INTERVAL
provider export                NOT_AUTHORIZED
scientific pass                NOT_CLAIMED
```

## Next node

```text
REI-RUNTIME-BRIDGE-03A3_AUTHORITY_BINDING_GREEN
```

That node may minimally remove the configurable authority surface, bind executing bytes and receipts to the verified checkout, and revalidate the complete toolchain.  Attempt-ref server protection remains a separate administration gate before target-host preflight.
