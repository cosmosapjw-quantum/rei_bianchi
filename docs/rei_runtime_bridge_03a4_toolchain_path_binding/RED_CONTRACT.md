# REI-RUNTIME-BRIDGE-03A4-PATH RED

## Classification

```text
INTENTIONAL_TEST_ONLY_RED
NO_PRODUCTION_SOURCE_CHANGE
NO_ATTEMPT_RESERVATION
NO_NATIVE_RUNTIME
```

## Triggering target-host evidence

The 03A4 operator-side locator stopped before the standalone clone and before
the static-preflight entrypoint:

```text
state_root_empty=true
pinned /usr/bin/git SHA-256 PASS
STOP_EXACT_CC_NOT_FOUND
expected cc_sha256
6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234
```

The system Rust 1.94.1 installation is not the observed blocker.

## Source-level root cause

The pinned production bridge uses fixed post-lease paths:

```text
compiler driver  /usr/bin/x86_64-linux-gnu-gcc
linker            /usr/bin/ld
MPFR              /usr/lib/x86_64-linux-gnu/libmpfr.so.6.2.1
GMP               /usr/lib/x86_64-linux-gnu/libgmp.so.10.5.0
```

Rust compilation explicitly includes:

```text
-Clinker=/usr/bin/x86_64-linux-gnu-gcc
```

The current Section-0 emitter, static preflight, and pre-lease controller instead
accept caller-selected absolute regular files for `cc`, `ld`, `mpfr`, and `gmp`
and compare only their hashes.  The worker receives only the Python and Rust
locators; it does not receive those four caller-selected paths.  It then enters
the unchanged bridge, which uses the fixed paths above.

Consequently an exact-hash copy at an alternate path can satisfy Section-0 and
the controller re-attestation while the actual post-lease runtime path remains
different.  The global attempt could then be reserved before the worker detects
the real-path mismatch.

## Required GREEN

1. Declare the exact post-lease runtime paths in the authority contract.
2. Validate the `cc`, `ld`, `mpfr`, and `gmp` witnesses against those paths—not
   merely against hashes—before Section-0 emission.
3. Repeat the same path validation during the final pre-lease toolchain
   re-attestation.
4. Bind a canonical runtime-path snapshot hash into the static-preflight
   receipt, global/local/dispatch chain, and worker input.
5. Re-read and validate the actual runtime paths in the worker before entering
   `run_native_once`.
6. Reject an alternate exact-hash copy with the typed classification
   `RUNTIME_TOOLCHAIN_WITNESS_PATH_MISMATCH`.
7. Preserve fixed GitHub authority, one-attempt/no-retry semantics, the
   production-import firewall, and all physics/source bytes.

## Forbidden shortcuts

```text
use an archived exact-hash compiler from an arbitrary path as --cc
change the semantic lock merely to match the current host
modify or monkeypatch the production bridge in this RED
reserve the global attempt ref
create persistent local attempt state
run the native worker
promote first-interval/provider/scientific claims
```

## Expected RED fingerprint

```text
6 tests
6 assertion failures
0 errors
PASS_EXPECTED_03A4_TOOLCHAIN_PATH_BINDING_RED
```

The RED is a governance/runtime-authority result.  It changes no formula,
physical convention, numerical tolerance, source coefficient, or provider
claim.
