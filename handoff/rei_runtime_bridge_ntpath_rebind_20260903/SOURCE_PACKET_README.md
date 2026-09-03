# REI PR #38 exact source packet

This transfer-only node exports the exact tracked source tree and the bounded runtime-handoff directory from REI Draft PR #38:

```text
commit  3169d1b0554193ababfb568406764d53df29649d
tree    1fa2da1a818bb311bf6cec42f76ff05693ed0903
```

The packet is intended for recovery, inspection, and local preflight. It does **not** contain or replace either host-bound input required for native execution:

```text
Section-0 receipt SHA-256
470fec225675a62a3c0121abcc4c568d345b088dd541a49fb18d91d6eacf104b
status PASS_IMMUTABLE_SECTION_0

Rust 1.94.1 archive SHA-256
294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40
```

A source archive is not a fresh standalone Git clone and cannot satisfy the production repository-context gate by itself. The local executor must still clone the exact release normally, copy the delivery-time head/tree pins, verify the external Section-0 receipt and absolute rustc locator, and invoke the native runner at most once under the create-only claim.

The workflow performs no Rust build, native bridge call, first canonical interval, provider export, BASS/REC splice, merge, or scientific promotion.
