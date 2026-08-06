# R2C-R1B results and durable verdict

## Result

R2C-R1B fails closed before production integration.  The endpoint node/group
lifts and global interval photon ledger do not identify the nonautonomous
forcing, dynamic opacity, node partition, or thermal history required by a
C2-Ray-type photon-conserving fixed point.

This is an input/closure identifiability failure.  It is not a physical
no-go, not an integration failure, and not a failure of the inherited global
photon ledger.

## Load-bearing evidence

- Global/sink mismatch: the R2A sink G1+G2a current is only
  `0.4361578--0.5464111` of global G1+G2a absorption.
- Endpoint relation: `J=kappa Phi` closes to `9.14346e-16`, but source
  inspection shows node `kappa` is defined from projected `J/Phi`.
- Temporal rank: endpoints plus one integral leave nullity `K-3`; at `K=8`,
  nullity is `5`.
- Node rank: fixed endpoints and pointwise total leave
  `(N-1)(K-2)` directions; at `N=46080`, `K=8`, nullity is `276474` per
  group/case.
- Actual positive witnesses preserve all corresponding locked constraints.
- Fixed macro totals still admit node shape-prior TV up to `0.330056`.
- Under the fixed primary spectrum, thin/thick atomic-HI heating differs by
  `14.75--18.60%` globally because the absorbed spectrum depends on optical
  depth.

## Hypothesis decision

- H1 identifiable endpoint forcing: REJECT.
- H2 chemistry forcing identifiable but thermal underidentified: REJECT.
- H3 forcing and thermal jointly underidentified: PROMOTE.
- H4 immediate larger coupled generator: HOLD / NOT AUTHORIZED.

## Durable verdict

```text
DURABLE_FAIL_CLOSED_R2C_R1B_ENDPOINT_AND_GLOBAL_LEDGER_DO_NOT_IDENTIFY_NODE_GROUP_FORCING_DYNAMIC_OPACITY_OR_THERMAL_HISTORY
```

Authorization:

- `R2C_R1B_completed = true`;
- `R2C_R1B_R1_authorized = true`;
- `production_node_chemistry_authorized = false`;
- `R2C_R2_authorized = false`;
- `B2C2B_authorized = false`.

## Next smallest action

Extract and lock the canonical time-resolved group boundary/source forcing,
a state-derived dynamic-opacity/optical-depth operator, and energy-weighted
heating moments.  Only after those inputs pass provenance, conservation, and
identifiability gates may the photon/chemistry fixed point be attempted.
