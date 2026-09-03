# REI PR #38 compact exact-source inspection packet

This transfer-only node exports a compact, exact-byte subset of REI Draft PR #38 without adding any file to the closed handoff package directory.

```text
source commit  3169d1b0554193ababfb568406764d53df29649d
source tree    1fa2da1a818bb311bf6cec42f76ff05693ed0903
```

The archive contains the complete PR #38 handoff directory and the exact bound `INPUT_LOCK`, production Python bridge, Rust source, Rust build receipt, and Rust implementation amendment. It is sufficient for portable package replay and inspection. It is not a complete repository clone and cannot satisfy the production standalone-Git-context gate.

## Failure-preserving predecessor

Draft PR #39 established two useful facts and is retained rather than rewritten:

1. A full-source artifact passed but was 1,294,322,295 bytes, exceeding the connector's 512 MiB download limit.
2. A 55,407-byte compact artifact passed, but transfer metadata was placed inside the closed handoff directory; the inherited package-index test correctly rejected the extra unindexed files.

This R2 packet keeps transfer metadata under `docs/` and leaves the original PR #38 handoff package byte-unchanged.

## Host-bound exclusions

The packet does **not** contain or replace:

```text
Section-0 receipt SHA-256
470fec225675a62a3c0121abcc4c568d345b088dd541a49fb18d91d6eacf104b
status PASS_IMMUTABLE_SECTION_0

Rust 1.94.1 archive SHA-256
294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40

absolute authenticated rustc locator
```

The local executor must still create a fresh full non-shallow/non-promisor clone of the exact PR #38 release, verify the delivery-time head/tree and external Section-0 receipt, authenticate the Rust compiler, and invoke the native runner at most once under the create-only lease.

No Rust build, native bridge call, first canonical interval, provider export, BASS/REC splice, merge, or scientific promotion occurs in this packet node.
