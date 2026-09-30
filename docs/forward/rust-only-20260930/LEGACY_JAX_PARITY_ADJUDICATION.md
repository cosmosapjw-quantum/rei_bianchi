# Historical JAX comparison

The frozen cross-runtime run at `fbce265b8182cc4c9383caa554a71c8524cef8f7`
reported **83/84** cases passing. Its sole failure was
`transform_exp_extreme`: the pinned JAX-x64 reference returned zero for
`exp(-745)`, while Rust returned `4.94065645841246544e-324`. The original
receipt remains at
`docs/forward/rust-20260922/evidence/final_local_20260929/parity-jax.json`.
Neither that receipt nor the fixture has been changed to report a pass.

Classification:

- `LEGACY_CROSS_RUNTIME_PARITY_DIVERGENCE`
- `NON_BLOCKING_AFTER_RUST_ONLY_CANONICALIZATION`

The old Python blobs `3d806e1c1d3bb523bb3c339d1a141f67d7f10069` and
`6f5c13f02d0e549e581a02d3c4d8b8313b209bbf` establish source derivation,
not a current bitwise runtime oracle. The frozen Python checker remains only as
a nonproduction archival verifier and is not called by the Rust build, tests,
or push workflow. No Python/JAX environment was restored.

Rust binary64 operations in the seven exported functions are the current
fixed-input contract. A positive subnormal is retained; only actual Rust
underflow produces zero. NaN and infinity behavior follows the public API and
is covered by Rust tests. This decision does not alter physical constants,
source ownership, scientific thresholds, or validated enclosures.
