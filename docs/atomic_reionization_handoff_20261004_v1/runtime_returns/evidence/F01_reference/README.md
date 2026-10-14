# REI-F01 reference validation and closeout

Run from repository root:

```sh
cargo test --manifest-path rust/rei_microphysics/Cargo.toml --locked
python3 docs/atomic_reionization_handoff_20261004_v1/runtime_returns/evidence/F01_reference/verify_candidate.py
python3 docs/atomic_reionization_handoff_20261004_v1/runtime_returns/evidence/F01_reference/verify_underflow.py
cargo fmt --manifest-path rust/rei_microphysics/Cargo.toml -- --check
cargo clippy --manifest-path rust/rei_microphysics/Cargo.toml --lib --locked -- -D warnings
cargo clippy --manifest-path rust/rei_microphysics/Cargo.toml --all-targets --locked -- -D warnings -A clippy::excessive_precision
```

The underflow verifier directly compiles a Rust consumer using the built crate and the recorded `/home/cosmosapjw/.cargo/bin/rustc` toolchain. Build the crate first. The original frozen tests and reference values remain byte-identical; `excessive_precision` is explicitly allowed for source-reference decimals in the frozen fixture, not a relaxation of numerical acceptance. Strict library Clippy passes. Strict all-target Clippy produced 1119 precision-literal lints in the native author's check; this is disclosed rather than called a full strict-lint PASS.

`selected_original_functions.c` preserves all 18 original function bodies exactly, matched to pinned Grackle af7939494ce65007887ada7b98d1813df6843346 source. It is an isolated C comparison harness, not the library ABI or full solver. Keep its accompanying `LICENSE` notice. `c-reference.json` contains 540 original C evaluations at units=1, all selected flags enabled, both cases, including 5500/9284/1e9 branches. Frozen Rust comparisons use relative 3e-12. `verner-oracle.json` contains 24 mpmath80 parameter/formula values and explicit threshold zeros. These are implementation-value tests, not independent atomic accuracy or derivative enclosures.

`review.json` retains the actual independent review and distinguishes reviewer Python arithmetic/binary execution from direct Host Rust API reproduction. One P2 underflow finding was repaired. Positive intermediate products or photon-density conversions that lose normal binary64 precision now return a domain error; the adapter does not supply a scaled arithmetic implementation for extreme inputs. `underflow-red.log` preserves the pre-repair first counterexample; four cases pass in `underflow-green.log`. Final full crate has 55 tests and final frozen verifier has 32 tests (including 26 unchanged forward API tests).

`native-runtime.json` records observed author/reviewer identity and cumulative native usage; cached tokens are included in input tokens, not added again. Monetary cost and pre-transition failed local request usage remain NOT_MEASURED. `mode-transition.json` preserves the earlier failed managed request, cleanup and owner CODEX_ONLY switch; no local source was integrated and no new local request followed. Full original managed receipt stays in the local `.cuh` evidence referenced by its hash.

No physical provider admission, thermal/recombination closure, H/He solver, interval/history certificate or FT04 actual-map binding is established. Raw reference support/domain/error metadata and primary absorption energy ownership are separate from such claims. Original synthetic F00/F02 inputs and historical FAIL receipts are unchanged.
