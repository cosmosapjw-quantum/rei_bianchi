# Local formal cross-checks

These scripts independently check the exact rational toy lemmas used by the
Rust-first interval substrate.  They do **not** connect those lemmas to the
missing four-site physical evaluator, node-38382 replay authority, or a
canonical interval.  Their successful execution therefore cannot raise the
scientific claim above `NO_PASS_FIRST_CANONICAL_INTERVAL`.

The scripts are intentionally redundant across systems available on the local
handoff host:

```text
wolframscript -file tangent_and_krawczyk.wl
sage tangent_and_krawczyk.sage
Singular tangent_and_krawczyk.sing
# Run only inside a separately supplied, pinned Lean/mathlib workspace:
lake env lean /absolute/path/to/TangentAndKrawczyk.lean
coqc TangentAndKrawczyk.v
```

Each command must exit zero.  Wolfram and Sage check the tangent, mixed
derivative, and interval-corner arithmetic; Singular independently checks the
tangent polynomial ideal.  Lean/mathlib and Rocq check the exact rational
tangent and strict-inclusion margin identities without depending on
floating-point computation.  The executor used to create this
handoff did not expose these programs on `PATH`; all five runs are `NOT_RUN`
here and must be recorded with tool versions and raw logs on the local host.

This repository deliberately does not invent a `lakefile`, `lean-toolchain`,
or mathlib lock.  Consequently the Lean command above is a host-bound recipe,
not a reproducible in-repository invocation.  A valid host receipt must add the
exact Lean version plus the external workspace's toolchain and dependency-lock
digests.  Without those identities, the Lean result remains `NOT_RUN` for this
work unit even if an unpinned interactive invocation succeeds.
