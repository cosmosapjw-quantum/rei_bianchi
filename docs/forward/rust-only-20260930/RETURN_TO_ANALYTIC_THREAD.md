# REI Rust-only forward return

The seven selected fixed-input functions are implemented and tested as the
Rust-only `rei_microphysics` crate. BASS may pin exact revision
`1bda1e8cea7629d31f905e126ba47ec3b3c1d0d8` for Rust integration. The
delivery branch is `forward/rust-reion-kernels-20260922`; verify its exact tip
by `git ls-remote` before intake.

The historical 83/84 cross-runtime result remains in prior raw receipts and
Git commits. Its executable checker was removed from the current branch and is
not an active gate. Rust `exp(-745)` is the positive
minimum subnormal `4.94065645841246544e-324`; no cutoff or flush-to-zero
adapter was introduced. The tested commit passed 26 Rust integration tests,
5 frontend tests, fmt, and clippy. The push CI uses Cargo, while the separate
rec_bianchi monitor uses shell and `jq`.

This is a fixed-input implementation handoff only. The four-site accepted
microstep, 2048/4096 enclosures, scientific state and rec_bianchi physical
lock were not changed. P0 physical admission remains open, HOST4 physical
remains held, HH propagation remains unauthorized, and the whole interval,
splice, CAMB, and Bianchi feedback are outside this port.

Next action: `BASS_EXACT_REV_RUST_INTEGRATION`, limited to these seven APIs.
