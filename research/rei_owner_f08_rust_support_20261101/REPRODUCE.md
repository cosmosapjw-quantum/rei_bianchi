# REI F08 first-step Rust source-char reproducer

In repository root run:

```bash
cargo test --offline --manifest-path research/rei_owner_f08_rust_support_20261101/rust/Cargo.toml
cargo fmt --manifest-path research/rei_owner_f08_rust_support_20261101/rust/Cargo.toml --check
cargo run --offline --quiet --manifest-path research/rei_owner_f08_rust_support_20261101/rust/Cargo.toml --example first_step > /tmp/rei_f08_firststep_128.csv
cmp /tmp/rei_f08_firststep_128.csv research/rei_owner_f08_rust_support_20261101/results/F08_ORIGINAL_FIRSTSTEP_128_RAYS.csv
sha256sum research/rei_owner_f08_rust_support_20261101/results/F08_ORIGINAL_FIRSTSTEP_128_RAYS.csv
```

Expected CSV SHA256: `330c91e9920fd7e13c373dbc0c48aa526eb5a7e00e559e3b72ba3762ffeb7343` (128 source-model rays). Rust unit tests: 4/4 pass on rustc/cargo 1.99.0. No original full F08 end-to-end transport test is claimed. Fixed-grid native `hat` remap is reproduced **diagnostically** and not used as physical output. Keep owner frozen original source and production untouched.
