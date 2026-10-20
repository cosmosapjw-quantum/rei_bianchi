# BRPERF01 isolated Rust runtime

## Verified state

The supplied Rust 1.94.1 archive was read in full and matched the official
distribution SHA-256 obtained by HTTP 200 from
`https://static.rust-lang.org/dist/rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz.sha256`.

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| Rust 1.94.1 Linux x86_64 archive | 192,287,020 | `294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40` |
| BR06 99-package registry archive | 13,249,025 | `a609f400af02d432e16956ef44d4ba5187a5a9b5360a9f6218f1d540818b3292` |

The official installer was read before execution and copied unchanged to
`upstream_install.sh`. Only rustc, Cargo, the x86_64 Linux standard library,
rustfmt, and Clippy were installed. The prefix is inside this task's scratch
runtime directory. `--disable-ldconfig` was supplied. The previous attachment's
environment script points to `/mnt/data` and was not sourced.

The supplied detached OpenPGP signature is retained. **OpenPGP signature
verification was not performed.** Archive identity here rests on the official
HTTPS checksum comparison, not a verified signing key.

## Use

```sh
source /workspace/scratch/996fc62899da/brperf01/runtime/env.sh
```

This sets `PATH`, `LD_LIBRARY_PATH`, and a task-specific `CARGO_HOME`. It does not
set `CARGO_TARGET_DIR`; parallel research workers should choose distinct target
directories, then serialize timing measurements to avoid contention.

The vendored registry is:

```text
/workspace/scratch/996fc62899da/brperf01/runtime/vendor/registry
```

Every one of the 4,944 declared payload hashes was checked, across 99 packages.
All 99 registry package checksums match the unchanged BR06 Cargo.lock, whose
SHA-256 is `2d1c997de506d31d57d42c40cae55e6ab6ff3f953e93091b99e9798d5413f4be`.
Cargo uses this directory as a crates.io replacement and runs offline by
default. A project's nearer `.cargo/config.toml` can override Cargo-home
configuration; account for that when moving a project.

## Executed validation

| Check | Result |
| --- | --- |
| `rustc --version --verbose` | 1.94.1, e408947bfd200af42db322daf0fadfe7e26d3bd1, LLVM 21.1.8 |
| `cargo --version` | 1.94.1, 29ea6fb6a |
| `rustfmt --version` | 1.8.0-stable |
| `cargo-clippy --version` | 0.1.94 |
| Offline smoke compile and execution with approx 0.5.1 | PASS |
| Strict Clippy on smoke crate | PASS |
| rustfmt check on smoke crate | PASS |

These are runtime and package-availability checks. They are not a validation
of any science code, new algorithm, convergence claim, or production regression.
No previous source file or lockfile was modified by this runtime task.

## Available benchmark resources

The process reports 9 CPU affinity slots, while cgroup `cpu.max` is
`800000 100000`, equivalent to an 8-core CPU time quota. The memory limit is
8,589,934,592 bytes (8 GiB). The reported processor model is AMD EPYC 9V74
80-Core Processor. This is host identification; benchmark capacity is limited
by the quota and is shared among concurrent workers. CPU flags and complete
resource readings are in `RUNTIME_IDENTITY.json`.

## Reproduction

`RESTORE_RUNTIME.py` provides a checksum-pinned offline bootstrap into a new
directory. Supply the Rust and registry archives explicitly:

```sh
python3 RESTORE_RUNTIME.py \
  /absolute/path/rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz \
  /absolute/path/REGISTRY_99_CARGO_LOCKED.tar.gz \
  /absolute/path/new-runtime
```

The bootstrap repeats the same extraction, installer command, registry payload
checks, and configuration used here. The script itself was syntax checked;
a second complete toolchain installation was not run as part of this bounded
runtime preparation task. Rebuildable compiler binaries, installer payloads,
and smoke targets can be omitted from the research archive when these pinned
input identities and restoration instructions are retained.

Detailed evidence: `RUNTIME_IDENTITY.json`, `REGISTRY_VERIFICATION.json`,
`REGISTRY_LOCK_MATCH.json`, `TOOL_VERSIONS.json`, `INSTALL.log`, `SMOKE.json`,
`OFFICIAL_RUST_ARCHIVE.sha256`, and `RUST_EXTRACTED_MEMBERS.json`.
