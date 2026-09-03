# REI runtime host-epoch governance patch

## Purpose

The original machine-bound Section-0 receipt and old `/tmp` attempt-claim bytes are unavailable on the current execution container. Their known hashes and historical outcomes remain valid evidence, but inventing their missing bytes or requiring their ephemeral filesystem presence forever would make the one remaining authorized attempt impossible to execute on a distinct host.

This patch separates four predicates:

1. **historical receipt identity** — preserved, never reconstructed;
2. **successor-host semantic equivalence** — a fresh raw receipt must match every locked toolchain/library field exactly;
3. **historical attempt lineage** — recorded durably in Git rather than inferred from `/tmp`;
4. **one-attempt exclusion** — atomic global create-ref first, then a persistent local `O_EXCL` lease.

## Current state

```text
compact PR38 source packet       PASS
historical attempt ledger        PASS
successor Section-0 policy       PASS_DESIGN
remote global lease protocol     PASS_DESIGN / NOT ACQUIRED
successor executable handoff     NOT IMPLEMENTED
native runtime                   NOT RUN
first canonical interval         NO PASS
provider export                  NOT AUTHORIZED
```

## Critical non-equivalence

```text
old raw receipt SHA identity
  != successor raw receipt identity

old host identity
  != successor host identity

exact semantic toolchain lock
  == required on both admitted epochs
```

The old Section-0 SHA `470fec...104b` remains historical. A successor receipt must use status `PASS_EQUIVALENT_SECTION_0_SUCCESSOR`, have a new raw SHA, and reproduce the semantic lock SHA `d670...87a7` field-by-field.

## Attempt protocol

```text
historical attempt ledger
source packet backup
        ↓
fresh successor Section-0 receipt
        ↓
atomic GitHub create-ref reservation
        ↓
persistent local O_EXCL lease
        ↓
one native dispatch
        ↓
separate runtime-result audit
        ↓
first-interval eligibility review
```

No lease has been created by this branch. The ref namespace is only a protocol until the successor executable handoff is composed and an exact target host passes re-attestation.

## Next node

`REI-RUNTIME-BRIDGE-02B_SUCCESSOR_HOST_EXECUTABLE_HANDOFF`

It must copy or adapt the PR #38 runner into a new closed package, accept the successor receipt by exact semantic lock, reserve the global ref before the local lease, and preserve all downstream claim gates. It must not edit the closed PR #38 handoff directory.
