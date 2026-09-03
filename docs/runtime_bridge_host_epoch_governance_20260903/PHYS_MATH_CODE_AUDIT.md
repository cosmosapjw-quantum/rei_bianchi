# PHYS-MATH-CODE audit — successor-host governance

## Disposition

`PASS_GOVERNANCE_IMPLEMENTATION / EXECUTABLE_SUCCESSOR_HANDOFF_NOT_YET_COMPOSED`

## Fixed at the governance layer

- The unavailable old Section-0 receipt is preserved by identity and explicitly forbidden from reconstruction.
- A new host must produce a fresh raw receipt with exact semantic-lock equality.
- Two historical attempts are recorded durably and cannot be erased by `/tmp` cleanup.
- One remaining attempt requires an atomic create-only GitHub ref before any local lease.
- The lease ref cannot be updated or deleted by the supplied protocol.
- Native dispatch and every downstream claim remain absent.

## P0 guard

The existing PR #38 runner still accepts only the historical raw Section-0 SHA and creates its local claim before validating that receipt. Therefore this governance branch must not invoke it directly. A new successor-handoff adapter is required after this policy passes.

## P1 residuals

1. The global lease script requires a user-supplied GitHub token with contents-write permission; missing or failed network authorization must stop before local lease creation.
2. The successor receipt script must run on the actual target host and may fail on any library or executable mismatch.
3. GitHub branch refs are durable coordination evidence but not a substitute for the local execution receipt.
4. The Rust detached signature trust remains unverified on the current container because the public key is absent; locked archive-byte identity remains separate.

## Next code node

`REI-RUNTIME-BRIDGE-02B_SUCCESSOR_HOST_EXECUTABLE_HANDOFF`

It must compose this policy with a new runner, reorder validation and lease acquisition, accept only `PASS_EQUIVALENT_SECTION_0_SUCCESSOR`, and leave the closed PR #38 package byte-unchanged.
