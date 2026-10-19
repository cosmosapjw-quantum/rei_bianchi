# Reproduce the RUN18 exact-polynomial adapter

The actual producer commands and environment are recorded in
`build_execution01/BUILD_RECEIPT.json` and
`adapter_execution01/RUST_EXACT_VIGILODE_RESULT.json`. These historical receipts
contain absolute producer paths. The source crate has no absolute dependency
path. The following commands select new paths explicitly and need no gas server,
original IVP, or network download.

Set the three paths to an extracted or Git-restored RUN18 directory, an existing
Rust 1.94.1 prefix containing `bin/rustc` and `bin/cargo`, and a nonexistent writable
build workspace. The fixture and independent reference belong to the published
`theory/execution01` directory and are hash-guarded by the validator.

```bash
rei_run18_root=/absolute/path/to/run18
rei_rust_prefix=/absolute/path/to/rust-1.94.1
rei_fresh_build=/absolute/path/to/new-run18-build

python -B "$rei_run18_root/runtime/restore_vendor_from_archives.py" \
  --runtime-root "$rei_run18_root/runtime" \
  --workspace-dir "$rei_fresh_build"

env PATH="$rei_rust_prefix/bin:$PATH" \
  RUSTC="$rei_rust_prefix/bin/rustc" \
  CARGO_HOME="$rei_fresh_build/cargo_home" \
  CARGO_TARGET_DIR="$rei_fresh_build/target" CARGO_BUILD_JOBS=2 \
  "$rei_rust_prefix/bin/cargo" test --offline --locked --lib \
  --manifest-path "$rei_run18_root/runtime/exact_dense_adapter/Cargo.toml" \
  --config "$rei_fresh_build/vendor_config.toml"

env PATH="$rei_rust_prefix/bin:$PATH" \
  RUSTC="$rei_rust_prefix/bin/rustc" \
  CARGO_HOME="$rei_fresh_build/cargo_home" \
  CARGO_TARGET_DIR="$rei_fresh_build/target" CARGO_BUILD_JOBS=2 \
  "$rei_rust_prefix/bin/cargo" build --offline --locked --release \
  --bin rei_exact_dense \
  --manifest-path "$rei_run18_root/runtime/exact_dense_adapter/Cargo.toml" \
  --config "$rei_fresh_build/vendor_config.toml"

python -B "$rei_run18_root/runtime/validate_exact_adapter.py" \
  --fixture "$rei_run18_root/theory/execution01/DENSE_B_F64_BITS.json" \
  --reference "$rei_run18_root/theory/execution01/EXACT_C0_DEPTH_REFERENCE.json" \
  --binary "$rei_fresh_build/target/release/rei_exact_dense" \
  --output-dir "$rei_fresh_build/exact_validation"
```

The helper reads the five locked official crate archives, cross-checks preserved
metadata/checksums and bounded safe archive members, restores only regular files,
and writes standard Cargo vendor checksum maps. It does not execute Cargo, tests,
or build scripts. It refuses an existing workspace. The inspection-only Inari
archive is preserved as research evidence and is not needed by this build.

Expected actual science comparison counts are 5,911 exact endpoint/jump cases,
5,911 right-endpoint interval value inclusions and 5,911 right-endpoint interval
derivative inclusions. The source unit has four tests: three new adapter tests and
one unchanged imported VigilODE arithmetic test. All timing values in the existing
receipts belong to the producer run, not to an unexecuted future restoration.

`vendor_config.toml` at the historical runtime root contains the original absolute
vendor path and should not be used after relocation. The helper writes a new
config for the explicitly selected fresh workspace. `fetch_exact_dependencies.py`
is the original network acquisition recipe, uses create-only outputs, and is not
the offline restore command. It should not be rerun in an existing delivered tree.

The built binary depends on compiler/platform/build options and may include
producer paths. Its observed producer SHA is an artifact identity, not a promise
of a bit-identical build at every new path. Reproduction acceptance compares the
exact rational outputs and inclusion results; any binary difference is recorded
separately. The final gas trajectory, native physical owners and old M2 histories
are not recomputed by these commands.

The helper's current execution status must be read from a corresponding
`OFFLINE_VENDOR_RESTORE.json` receipt if present. Writing these commands alone
does not establish a new clean build or runtime verification.
