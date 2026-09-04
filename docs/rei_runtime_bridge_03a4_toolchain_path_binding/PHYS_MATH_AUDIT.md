# PHYS-MATH audit — 03A4 runtime-toolchain path binding

Status: `PASS_NO_PHYSICS_DELTA`.

## Conventions and scope

The change does not modify the metric, tetrad, photon, collision, thermochemistry, interval-arithmetic or source equations. Locked physical conventions remain:

```text
metric signature       (-,+,+,+)
spatial orientation    epsilon_123 = +1
speed of light         explicit
MPFR precision         256 bits
rounding               MPFR_RNDD / MPFR_RNDU
```

The exact homogeneous polarized-photon SSOT remains formula authority for cold, non-tilted electron-rest Thomson transport. Recombination/reionization microphysics, solver construction, numerical evolution, first-interval execution and inference remain outside that formula theorem.

## Mathematical invariant added

Let `P_r` be the declared post-lease path for role `r`, `R(P_r)` its strict resolved regular file, and `H_r` the semantic-lock SHA-256. The admissibility predicate is

```text
supplied witness path = R(P_r)
SHA256(R(P_r)) = H_r
```

for each role

```text
r in {cc, ld, mpfr, gmp}.
```

The path snapshot is canonical JSON over the four ordered role records and is itself hashed. All later records carry the same snapshot hash.

An alternate file `Q_r` with

```text
SHA256(Q_r) = H_r,  Q_r != R(P_r)
```

is deliberately rejected. This is not a physical claim about compiler equivalence; it is the operational requirement that the preflight witness equal the file the unchanged post-lease bridge will actually invoke.

## Limits and counterexamples

- Exact same bytes at a different path: rejected.
- Correct path with wrong bytes: rejected.
- Missing declared path: rejected.
- Non-executable compiler/linker: rejected.
- Identical snapshot in preflight but drift before reservation: rejected by immediate re-attestation.
- Identical prelease snapshot but drift before native entry: rejected by worker-side recheck.

## Claim boundary

```text
path-binding source PASS
  does not imply target-host epoch reconstruction
  does not imply successor Section-0 PASS
  does not imply native execution
  does not imply first canonical interval
  does not imply provider or scientific admission
```

No physical P0 or P1 is introduced by this bounded governance change.
