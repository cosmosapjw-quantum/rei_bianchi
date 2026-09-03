# REI runtime bridge — fresh standalone handoff rebind after `ntpath`

## Node

```text
REI-RUNTIME-BRIDGE-02_FRESH_STANDALONE_HANDOFF_REBIND
```

This package authorizes **one future native validation attempt only**.  It does
not execute the Rust/MPFR backend, repair another import, run the first
canonical interval, admit a provider, or change a scientific claim.

## Exact parent and material delta

```text
parent Draft PR  #37
parent commit    5b6957237bbe8edfdfe3c980910cba690d23775c
parent tree      805e92779ba6e7d956d5ac936f0934f5879fd3a1

patched INPUT_LOCK SHA-256
20db870e76ff8a82f2b6f6d38d90eb915b73d5564d6dfbee60a524862ab2e989

unchanged production bridge SHA-256
91fe316f1e8b81d64e9929d7a4814b77808fdf486e2ca67cd2f615e8617fce85
```

The sole production-semantic delta inherited from PR #37 is the exact
allowlist addition

```text
runtime_closure.declared_import_roots += ["ntpath"]
```

All 17 declared source paths and the `jax`/`jaxlib` forbidden roots remain
unchanged.

## Why a new handoff is required

The previous standalone attempt created and retained

```text
/tmp/rei-runtime-bridge-host-context-repair-20260901.native-attempt.json
```

That lease is consumed evidence and must never be removed, replaced, bypassed,
or reused.  The published `ntpath` material delta permits exactly one new
attempt under a different create-only claim:

```text
/tmp/rei-runtime-bridge-ntpath-rebind-20260903.native-attempt.json
```

A second invocation under the new claim fails before dispatch.

## Reused runner and new governance wrapper

`runtime_bridge_runner_base.py` is the byte-identical PR #31 handoff runner.
`runtime_bridge_runner.py` is a thin governance wrapper.  Before the inherited
runner can load repository code or dispatch the native path, the wrapper:

1. verifies the closed package by Git blob identity;
2. verifies the PR #37 input-lock SHA and semantics;
3. verifies the production bridge SHA is unchanged;
4. binds a new material-delta-specific `O_EXCL` attempt claim;
5. augments any successful runtime receipt with the patched-input and attempt
   lineage identities.

The wrapper changes no production REI module.

## Section 0 boundary

The existing external receipt

```text
SHA-256 470fec225675a62a3c0121abcc4c568d345b088dd541a49fb18d91d6eacf104b
status  PASS_IMMUTABLE_SECTION_0
```

is retained only as the exact pinned toolchain/host-identity receipt already
required by the inherited runner.  It is **not** treated as evidence for the
new `INPUT_LOCK` bytes; the wrapper verifies those bytes independently before
native dispatch.

## Local verification in this handoff node

The package unit tests are standard-library only and cover:

- package blob closure and an unindexed-file mutation;
- exact PR #37 predecessor, lock and bridge identities;
- actual checked-out lock semantics;
- lock-hash mutation rejection;
- exact regular Section 0 receipt input;
- single-root/non-alternate clone constraints;
- material-delta-bound create-only attempt claim;
- at-most-one dispatch;
- unexpected-exception fail closure.

The GitHub workflow runs these tests and the repository verifier.  It does not
pretend that a generic hosted runner is the pinned production host and it does
not invoke the native runner.

## Claim ceiling

```text
handoff_rebind        PASS only after package CI and remote readback
native_runtime        NOT_RUN
runtime_bridge        STOP_INVALID_UNTIL_FRESH_RESULT_AUDIT
first_interval        NO_PASS_FIRST_CANONICAL_INTERVAL
provider_export       NOT_AUTHORIZED
scientific_pass       NOT_CLAIMED
scientific_publication NOT_RUN
```

Even a future native exit `0` opens only a separate runtime-result audit.  It
must not automatically trigger the first canonical interval or provider
publication.
