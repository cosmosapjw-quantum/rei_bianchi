# Portable narrow VigilODE moment harness — Recovery R1

This is a relocation recipe for the existing validated narrow harness. No Rust source, Cargo manifest, lockfile, upstream file, or validated output is modified by this document. No new test or simulation was run for this follow-up. The main BR06 crate already tested the same R1 adapter; this harness is an inexpensive additional scalar reproduction route, not the entire VigilODE workspace.

## Required relative layout

Choose an absolute `BR06_MOMENT_ROOT` containing the following paths. Preserve each relative name exactly.

| Path below BR06_MOMENT_ROOT | Purpose |
|---|---|
| `adapter_r1/vigilode_moments.rs` | Frozen R1 adapter, SHA-256 b333bbaa9962f6e2ac09ace0afb9a3cccc76d2c56811be1e371d09557e5a3235 |
| `adapter_r1/harness/Cargo.toml` and `Cargo.lock` | Narrow workspace and locked registry resolution |
| `adapter_r1/harness/.cargo/config.toml` | Existing offline source replacement; keep `directory = "../../vendor_r1"` |
| `adapter_r1/harness/src/lib.rs` and `src/main.rs` | Validated harness wrapper and scalar CSV driver |
| `adapter_r1/harness/kernel/Cargo.toml` and `kernel/src/lib.rs` | Separate exact-kernel dependency boundary |
| `vigilode_exact_selected/crates/rodas5p-core/src/error.rs` | Exact pinned upstream errors |
| `vigilode_exact_selected/crates/rodas5p-core/src/damped_moments.rs` | Exact pinned upstream scalar moment implementation |
| `vigilode_exact_selected/crates/rodas5p-core/src/directed.rs` | Exact pinned upstream interval arithmetic |
| `vigilode_exact_selected/LICENSE` | Original VigilODE MIT license |
| `vendor_r1/` | Ten available recovered vendor directories, including each `.cargo-checksum.json`; the final harness lock selects nine registry packages |

The recovered narrow `vendor_r1` inventory contains **10 available directories; the final harness Cargo.lock actually selects 9 registry packages**. The extra `syn-2.0.119` directory is unused. The selected packages are proc-macro2 1.0.107, quote 1.0.47, serde/serde_core/serde_derive 1.0.229, syn 3.0.3, thiserror/thiserror-impl 2.0.19, and unicode-ident 1.0.24.

The full archive's 99-package registry also supplies all nine selected packages with exactly the final lock's checksums. To reconstruct a minimal `vendor_r1` from that archive, copy the nine directories identified in `PORTABLE_MOMENT_HARNESS_LAYOUT_R1.json` by `full_registry_directory`, preserving their contents and `.cargo-checksum.json`. Its `syn` directory is version 3.0.3; do not substitute `syn-2.0.119`. The complete 99-package directory can alternatively serve as the `vendor_r1` directory at the same relative location; unused packages do not alter the locked selection. Neither option requires changing Cargo.lock, the offline configuration, or the validated source.

The complete 477-payload snapshot may be retained in `vigilode_exact_selected`; this narrow harness imports only the three source files listed above. The full main BR06 crate additionally needs the original core workspace, coefficients fixture and its larger registry set. Those are separate restoration requirements.

There are **no symlink requirements**. The current validated layout has no adapter-tree symlinks. Ordinary copies preserving the relative layout suffice. If restoring from `VIGILODE_EXACT_477_PAYLOAD_RECOVERY.tar`, its member prefix is `vigilode/`; extract it into `vigilode_exact_selected` with one leading component removed, preserving the original bytes.

## Why the unchanged relative paths resolve

- The harness `src/lib.rs` imports `../../vigilode_moments.rs`, which resolves to `adapter_r1/vigilode_moments.rs`.
- The kernel's `kernel/src/lib.rs` imports `../../../../vigilode_exact_selected/...`, which resolves to the sibling snapshot directly below `BR06_MOMENT_ROOT`.
- The existing offline vendor source resolves from the harness root to `../../vendor_r1`, the sibling registry source directly below `BR06_MOMENT_ROOT`.

Invoke Cargo from `adapter_r1/harness` as in the recipe. This is the validated configuration-discovery context; an arbitrary working directory with only `--manifest-path` is not this recipe. Do not move the vendor directory or rewrite the source attributes to accommodate a different layout.

## Reproduction commands

Use Rust/Cargo/Clippy 1.94.1 on PATH, as recorded in the existing execution logs. For the current recovered sandbox this is available by sourcing `br06_recovery/runtime/rust_env.sh`; a relocated runtime should provide the same toolchain through its own prefix. Source payloads do not depend on the original sandbox's absolute path.

```bash
set -eu
BR06_MOMENT_ROOT=/absolute/path/to/restored_moment_payload
mkdir -p "$BR06_MOMENT_ROOT/results"
cd "$BR06_MOMENT_ROOT/adapter_r1/harness"
rustc --version --verbose > "$BR06_MOMENT_ROOT/results/RUST_RUNTIME.txt"
cargo test --offline --locked > "$BR06_MOMENT_ROOT/results/TEST.log" 2>&1
cargo clippy --offline --locked --all-targets -- -D warnings > "$BR06_MOMENT_ROOT/results/CLIPPY.log" 2>&1
cargo run --offline --locked --bin moment_recovery_r1 > "$BR06_MOMENT_ROOT/results/MOMENT_API_ROWS.csv" 2> "$BR06_MOMENT_ROOT/results/MOMENT_EXECUTION.log"
```

The existing verified scalar CSV is `adapter_r1/MOMENT_API_ROWS_R1_FINAL.csv`, SHA-256 `505ba529a232602c4ad9754bceb5a4f2ebcb280405507f2ded82f7e082af1b29`. It has 252 rows: 126 successful dyadic outputs, 117 successful direct outputs, and nine retained direct NonFinite refusals at tau=1e12. These direct refusals are expected recorded outcomes, not zero moments. Compare a restored run with the declared scalar acceptance and independent Decimal110 verifier; the commands in this document do not by themselves assert a new restore PASS.

The three R1 unit tests belong to the harness package. Upstream files remain a separate dependency and are not silently rewritten to satisfy local style lints. This route does not run the full upstream solver, its benchmark suite, or the evolving H/He/D history.
