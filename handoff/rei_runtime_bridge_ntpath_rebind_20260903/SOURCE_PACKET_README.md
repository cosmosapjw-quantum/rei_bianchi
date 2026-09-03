# REI PR #38 compact exact-source inspection packet

This transfer-only node exports a compact, exact-byte subset of REI Draft PR #38:

```text
source commit  3169d1b0554193ababfb568406764d53df29649d
source tree    1fa2da1a818bb311bf6cec42f76ff05693ed0903
```

The archive contains the complete PR #38 handoff directory and the exact bound `INPUT_LOCK`, production Python bridge, Rust source, Rust build receipt, and Rust implementation amendment. It is sufficient for portable package replay and inspection, but it is **not** a complete repository clone.

An initial full-source artifact passed its workflow but was 1,294,322,295 bytes and exceeded the connector's 512 MiB download limit. It is preserved as historical workflow evidence under artifact `9877661352`; the compact successor avoids treating transfer size as scientific evidence.

The packet does **not** contain or replace either host-bound input required for native execution:

```text
Section-0 receipt SHA-256
470fec225675a62a3c0121abcc4c568d345b088dd541a49fb18d91d6eacf104b
status PASS_IMMUTABLE_SECTION_0

Rust 1.94.1 archive SHA-256
294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40
```

A compact source archive is not a fresh standalone Git clone and cannot satisfy the production repository-context gate. The local executor must still clone the exact PR #38 release normally, verify the delivery-time head/tree, recover the exact external Section-0 receipt, authenticate an absolute Rust 1.94.1 compiler locator, and invoke the native runner at most once under the new create-only claim.

The workflow performs no Rust build, native bridge call, first canonical interval, provider export, BASS/REC splice, merge, or scientific promotion.
