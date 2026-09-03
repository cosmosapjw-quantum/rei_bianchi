# PHYS-MATH audit — fresh standalone handoff rebind

## Disposition

```text
PASS_NO_PHYSICS_DELTA
```

## Fixed conventions and dimensions

No physical formula changes in this node.  The inherited REI/XCAS formula
contract remains:

```text
metric signature  (-,+,+,+)
ray parameter     s = c t
H(z)              T^-1 in the REI FLRW control
H_geom            L^-1 in the BASS ray-length convention
optical depth     dimensionless
number density    L^-3
```

The production bridge, Rust source, MPFR/GMP identities, precision
`256 bits`, directed-rounding policy `MPFR_RNDD_RNDU`, numerical coefficients,
tolerances and all thermochemistry expressions remain byte-pinned.

## Audit checks

| Check | Result | Reason |
| --- | --- | --- |
| Definition/notation change | PASS | no physics symbol or formula edited |
| Sign/normalization change | PASS | none |
| Unit/dimension change | PASS | none |
| Known-limit regression | NOT RERUN | unnecessary for a handoff-only change; prior bounded matrix remains applicable |
| Positivity/regularity change | PASS | none |
| Hidden approximation change | PASS | none introduced |
| Special-case counterexample | PASS | generic hosted runner remains explicitly non-authoritative |

## Load-bearing distinction

The existing Section 0 receipt is retained as a pinned host/toolchain identity
input.  It is not promoted to an attestation of the patched `INPUT_LOCK` bytes.
The wrapper verifies those bytes independently before dispatch.

Likewise:

```text
byte-identical build artifact
  != interval inclusion proof
  != scientific validity
```

and

```text
runtime bridge PASS
  != first canonical interval PASS
  != provider admission
```

## Residual physics blockers

Unchanged:

```text
real four-site replay ABI
node 38382 parent/fixture/replay authority
exact BASS/REC provider authority
first canonical interval
provider publication
generic Bianchi reionization transport
```

## Claim boundary

The mathematical claim of this node is only that the handoff preserves the
previous physical contract while rebinding one future validation attempt to
the exact PR #37 material delta.
