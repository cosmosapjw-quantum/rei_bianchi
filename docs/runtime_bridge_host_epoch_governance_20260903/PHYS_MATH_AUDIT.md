# PHYS-MATH audit — successor-host governance

## Disposition

`PASS_NO_PHYSICS_DELTA`

The patch changes no thermochemistry, opacity, H/He conservation law, Bianchi transport coefficient, Rust interval formula, precision, rounding policy or tolerance.

## Load-bearing distinctions

- Historical raw receipt identity is not semantic toolchain equivalence.
- A distinct host epoch may reproduce the exact locked compiler/library closure without being the old host.
- Byte identity of a compiled artifact is not an interval-inclusion proof.
- Runtime bridge success is not first-canonical-interval success.
- REI provider admission remains downstream of runtime-result audit, interval eligibility, REC and BASS dependencies.

## Exact semantic lock

The successor receipt must match thirteen fields exactly: rustc bytes/version, rustc-driver, LLVM, Rust stdlib closure, Python, MPFR, GMP, C compiler, linker, target, 256-bit precision and `MPFR_RNDD_RNDU`.

## Special-case attacks rejected

1. Rewriting the old receipt with the known hash/status but invented body.
2. Treating a matching `rustc --version` string as compiler identity.
3. Treating absence of the old `/tmp` claim on a new machine as proof that no previous attempt occurred.
4. Starting the first interval after native exit 0 without result audit.

## Claim boundary

No scientific or numerical result is produced by this governance patch.
