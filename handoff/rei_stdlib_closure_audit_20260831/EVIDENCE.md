# Closure-member evidence

This document records the bounded forensic conclusion used by the repair
contract. It is not a receipt from the user's host and does not claim a repair
has been performed there.

## Fixed inputs

- Archive: `08-rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz`
- Archive SHA-256: `294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40`
- Driver algorithm: `find . -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum`
- Locked closure: `1d6d31c8f1c99b69b120c91fcff14220bbfcf0e8f976096f0c4992b7e2edc799`
- Prior local observation: `7aae7f6cffe33365096e9f837378c9a26de46efd7d109eccd446d45703eee6c0`

## Reproduction result

| Direct regular-file set | Count | Legacy closure SHA-256 | Meaning |
|---|---:|---|---|
| Exact `rust-std` component directory | 62 | `7aae7f6cffe33365096e9f837378c9a26de46efd7d109eccd446d45703eee6c0` | Exactly reproduces the reported stopped-gate value. |
| The same 62 files plus only the large LLVM file | 63 | not equal to the lock | Not sufficient. |
| The same 62 files plus only the 42-byte LLVM soname file | 63 | not equal to the lock | Not sufficient. |
| The same 62 files plus both declared LLVM files | 64 | `1d6d31c8f1c99b69b120c91fcff14220bbfcf0e8f976096f0c4992b7e2edc799` | Exactly reproduces the existing lock. |

Thus neither a changed aggregate algorithm nor a changed lock is required to
explain the discrepancy. The base component is intact; the locked closure
requires the two additional archive members specified in `REPAIR_CONTRACT.json`.

## Safety conclusion

The permitted repair is only exact, create-only materialization of those two
members after dry-run verification. A target that already exists with different
bytes, any unexpected direct file, archive drift, or a post-write aggregate
mismatch is a stop condition. The original immutable Section 0 must then run
again in a fresh process.
