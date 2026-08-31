# REI Rust stdlib closure repair handoff

This is a bounded Section 0 authority-materialization repair. It does not
modify the locked build driver, its expected digest, repository code, or any
scientific certificate.

## Root cause, reproduced from the admitted archive

The immutable driver hashes the immediate regular files under `RUST_STDLIB`
with this exact pipeline:

```text
cd RUST_STDLIB
find . -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum
```

The exact Rust archive contains a `rust-std` component with 62 direct files.
Their legacy closure is exactly the value reported by the stopped local job:

```text
62 base rust-std files  7aae7f6cffe33365096e9f837378c9a26de46efd7d109eccd446d45703eee6c0
```

The lock instead describes the full 64-file sysroot closure. It is reproduced
only after adding these two archive-owned `llvm-tools-preview` members:

| Target name | Archive member | Size | SHA-256 |
|---|---|---:|---|
| `libLLVM.so.21.1-rust-1.94.1-stable` | `llvm-tools-preview/.../libLLVM.so.21.1-rust-1.94.1-stable` | 186,862,176 | `158c711c64147bb127a2a5174df22718d26b755560a1487945e7c788c947986f` |
| `libLLVM-21-rust-1.94.1-stable.so` | `llvm-tools-preview/.../libLLVM-21-rust-1.94.1-stable.so` | 42 | `9f31038f7c2c676542a29289adbbaec6a04b2e28d2680718eda70647b8611991` |

```text
62 base + both exact llvm-tools-preview files
1d6d31c8f1c99b69b120c91fcff14220bbfcf0e8f976096f0c4992b7e2edc799
```

The full target paths and identity data are machine-readable in
`REPAIR_CONTRACT.json`.

## Contents

- `stdlib_closure_audit.py` is read-only. It reproduces the base-component
  closure and records host utility identities; it is useful for retaining the
  original `7aae...` diagnosis.
- `materialize_missing_components.py` is a narrowly create-only repair. It
  checks every base file against the exact archive, permits only the two
  declared supplemental target names, never overwrites a target, and verifies
  the final 64-file closure before emitting a receipt.
- `LOCAL_CODEX_REPAIR_PROMPT.md` is the executable handoff contract for the
  local Codex job.

Both programs use no-follow descriptors for authority inputs. Neither invokes
`rustc`, `cargo`, repository Python, JAX, a native build, or an archive member.

## Required boundary after a successful repair

The repair receipt is not a Section 0 pass. Run the **complete, unchanged
immutable Section 0** in a fresh process. Only that new process may observe
the existing driver accept the locked stdlib aggregate. Any failure remains
`STOP_INVALID`; no downstream runtime, BASS/REC, four-site, node replay,
restart, formal audit, pilot, or scientific claim is authorized by this
package.
