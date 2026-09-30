# Rust-only seven-function forward closeout

This directory closes only the fixed-input `rei_microphysics` implementation.
The canonical development/runtime language is Rust. Python and JAX are not
required to build, test, or execute these seven functions.

- Rust-only parent: `e54e8745ca35e5ef3a093b13dc7deafbbcf55516` on
  `forward/rust-reion-kernels-20260922`.
- Tested Rust source and BASS exact-rev candidate:
  `1bda1e8cea7629d31f905e126ba47ec3b3c1d0d8`.
- The delivery commit is the commit containing this directory; resolve its
  exact SHA with `git rev-parse HEAD` on the named branch and compare to
  `git ls-remote origin refs/heads/forward/rust-reion-kernels-20260922`.
- [Execution receipt](EXECUTION_RECEIPT.json) has exact commands, exit codes,
  and raw logs under `evidence/`.
- [API map](RUST_CANONICAL_API.json) and [purge audit](RUST_ONLY_PURGE_AUDIT.json)
  define the bounded implementation surface.

The former 83/84 Python/JAX comparison is retained in the
[legacy adjudication](LEGACY_JAX_PARITY_ADJUDICATION.md) and its original raw
receipt. It remains a true historical divergence, with no active Rust gate.
Rust `f64` behavior permits positive subnormals; `exp(-745)` is
`4.94065645841246544e-324` on the tested toolchain. No FTZ shim or cutoff
was added.

This is fixed-input implementation evidence. The accepted four-site FLRW
microstep, outward enclosures, source admission, full interval, splice, CAMB,
and Bianchi feedback retain their existing independent scientific states.
