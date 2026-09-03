# Governance patch plan

## Chosen repair

Introduce a versioned host-epoch model rather than weakening the original hash checks.

### Historical epoch

The original Section-0 receipt remains identified by SHA-256 and status but is not recreated. Its two native attempts remain consumed historical evidence independent of whether `/tmp` survives.

### Successor epoch

A different machine may qualify only by emitting a fresh O_EXCL receipt whose thirteen load-bearing fields equal the locked semantic toolchain map. This is equivalence of declared execution authority, not raw receipt or host identity.

### Attempt reservation

Use a unique GitHub ref created with one POST. HTTP 201 is success; 422 means already reserved. Never update or delete the ref. Only after this global reservation may the target host create its persistent local O_EXCL lease.

## Rejected alternatives

- Reconstruct the missing old receipt from known fields.
- Restore or synthesize the old `/tmp` file.
- Allow any Rust 1.94.1 installation by version string.
- Replace the global lease with GET-then-local-write.
- Reuse the closed PR #38 runner unchanged.

## Completion boundary

This node closes governance design and portable tooling only. It does not close the executable successor handoff or consume the remaining attempt.
