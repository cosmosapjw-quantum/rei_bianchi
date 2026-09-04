# REI-RUNTIME-BRIDGE-03A4-PATH — GREEN contract

## Purpose

Close the path-identity gap exposed by Draft PR #56 without changing REI physics, the Rust numerical source, the semantic toolchain hashes, the server ruleset, the attempt budget, or the production bridge.

The load-bearing invariant is:

```text
Section-0 runtime-path snapshot
= preflight runtime-path snapshot
= immediate pre-reservation runtime-path snapshot
= global lease snapshot hash
= local lease snapshot hash
= dispatch-intent snapshot hash
= post-lease worker runtime-path snapshot
```

## Exact post-lease path authority

The unchanged production bridge uses:

```text
cc    /usr/bin/x86_64-linux-gnu-gcc
ld    /usr/bin/ld
mpfr  /usr/lib/x86_64-linux-gnu/libmpfr.so.6.2.1
gmp   /usr/lib/x86_64-linux-gnu/libgmp.so.10.5.0
```

The preflight may receive only the resolved regular files behind those declared paths. A byte-identical file at any other path is rejected with `RUNTIME_TOOLCHAIN_WITNESS_PATH_MISMATCH:<role>`.

## Executable ordering

```text
validate exact executing package and release
→ resolve and hash exact post-lease paths
→ emit successor Section-0 receipt
→ emit read-only static-preflight receipt with snapshot
→ stop for independent review

later, in a separate node:
validate the same snapshot
→ re-run all thirteen Section-0 fields
→ live ruleset and global-ref GET readback
→ create protected global lease
→ create persistent local lease
→ write dispatch intent
→ start one separate worker
→ recheck the same actual paths
→ enter unchanged production runtime once
```

The active freshness/live-readback descendant is included. Fixing only the older firewall controller is insufficient because the final reservation path runs through `rei_runtime_attempt_ref_protection_freshness_20260904`.

## TDD lineage

```text
PR #56 structural RED
  6 tests / 6 assertion failures / 0 errors

active freshness-layer RED
  4 additional tests

combined behavior RED
  10 tests / 10 assertion failures / 0 errors

GREEN requirement
  all 6 structural and all 10 behavior obligations pass
  inherited authority/freshness suites pass
  both package indexes pass
  global attempt ref remains absent
  no attempt/native state is created
```

## Compiler provenance boundary

The locked compiler bytes were identified in Ubuntu Snapshot package:

```text
gcc-13-x86-64-linux-gnu=13.3.0-6ubuntu2~24.04
snapshot 20250115T120000Z
DEB SHA-256 7cd398670e8306eabc9e77202f356a3206c440bd9f3dc764680a19be01784776
compiler SHA-256 6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234
```

This identifies provenance only. It does not authorize an alternate-path executable or a downgrade of the interactive host. The next operational node is isolated host-epoch reconstitution where the canonical in-environment path itself resolves to the locked bytes.

## Claim ceiling

```text
runtime-path-binding source       candidate pending exact-head CI
compiler package provenance       identified
current host compiler equality    false
isolated host epoch               not reconstructed
successor Section-0               not run
read-only static preflight        not run
global attempt ref                absent
persistent local lease            not created
remaining native attempts         1
native runtime                     not run
first canonical interval          no pass
provider/scientific admission     not authorized
```
