# R1B-R1 upload recovery — read first

This directory is a provenance-only recovery artifact. It is **not** the
R1B-R1 science stage and does not promote the previously reported R1B-R1 pass.

Observed failure:

```text
Failed to get upload status for rei_bianchi_R2C_R1B_R1_incremental.bundle
```

A filesystem and remote-branch search recovered only two byte-identical
research documents. The original Git objects, incremental bundle, compact
science bundle, numerical data, receipts, test logs, state files and stage
commit were not recovered. Under the project durability policy, all numerical
and completion claims from that lost run are therefore transcript-only.

The current durable science state remains the R1B fail-closed lock at
`2e3e144c0d60af3ed0c1bbfa68e988264936ae55`. The exact R1B-R1 research stage must be rerun from that prerequisite
before R1B-R2 can be authorized.

Recovered documents:

- `recovered/FORMALISM.md`
- `recovered/LITERATURE_EVIDENCE_LEDGER.md`

See `RECOVERY_INVENTORY.json` and `TRANSCRIPT_ONLY_CLAIMS.md` for the evidence
boundary.
