# REI successor Section-0 re-attestation and read-only preflight

## Status

```text
preflight source                         IMPLEMENTED_CANDIDATE
successor Section-0 receipt              NOT_CREATED
read-only exact-host preflight           NOT_RUN
remote global attempt lease              NOT_ACQUIRED
persistent local attempt lease           NOT_CREATED
native runtime                            NOT_RUN
first canonical interval                 NO_PASS_FIRST_CANONICAL_INTERVAL
provider export                           NOT_AUTHORIZED
```

This package implements the exact node following Draft PR #42.  It verifies a
fresh standalone clone at PR #42's executable release, observes a new successor
Section-0 toolchain receipt, and checks all pre-lease state without consuming
the one remaining attempt.

## Exact executable release

```text
PR      42
commit  eb1c05f3ea2bda910ddf85ef7f3bab08c73eca13
tree    0aa13dd9cb8630f208307342a933a8c68abf62c8
```

The successor toolchain must reproduce semantic lock
`a3da50241ed6423212ab40c79f7810b5eaad042acdff29eb40f330aa39d2d4fa`.
The historical raw Section-0 receipt remains historical evidence and is not
accepted or reconstructed.

## Read-only boundary

The preflight may:

1. verify this package and the exact PR #42 package/source blobs;
2. verify fresh standalone Git state;
3. inspect an empty persistent attempt-state directory;
4. perform two read-only GET observations of the fixed global attempt ref;
5. invoke the already-published successor Section-0 emitter;
6. audit the emitted receipt with the PR #42 executable validator;
7. write only successor-Section-0 and preflight evidence under a distinct
   persistent output directory.

It may not:

```text
create/update/delete the global attempt ref
create the persistent local attempt lease
invoke the native bridge
run the first canonical interval
admit a provider
promote a scientific claim
```

A `404` observation of the global ref is evidence of absence at that instant,
not authorization.  The later execution node must still use one atomic
create-only remote reservation.

## Target-host command

Run against a fresh full clone checked out exactly at the PR #42 release:

```bash
python3 \
  /PATH/TO/THIS/PACKAGE/successor_section0_preflight.py \
  --repo /ABS/FRESH/rei_bianchi-pr42 \
  --rustc /ABS/rust-1.94.1-prefix/bin/rustc \
  --python /usr/bin/python3 \
  --mpfr /usr/lib/x86_64-linux-gnu/libmpfr.so.6 \
  --gmp /usr/lib/x86_64-linux-gnu/libgmp.so.10 \
  --cc /usr/bin/cc \
  --ld /usr/bin/ld \
  --attempt-state-root /ABS/PERSISTENT/attempt-3-state \
  --output-root /ABS/NEW/successor-section0-preflight
```

The attempt-state root must already exist and be empty.  The output root must
not exist.  Both must be persistent, outside `/tmp`, and outside all Git
worktrees.

## Next node after an exact-host PASS

```text
REI-RUNTIME-BRIDGE-03B_ATOMIC_GLOBAL_LEASE_AND_ONE_NATIVE_DISPATCH
```

That next node, not this package, may atomically reserve the global ref and
consume the final attempt.  Its first outcome must be preserved without repair
or retry and audited before any first-interval decision.
