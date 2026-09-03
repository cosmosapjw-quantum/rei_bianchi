# Plot-based CRAG audit — successor Section-0 preflight

## Figure

`PREFLIGHT_STATE.svg` is generated deterministically from
`PREFLIGHT_STATE.csv` and verified byte-for-byte by
`render_preflight_state.py --verify`.

## Correctness

The first two rows are source/governance deliverables already implemented:

```text
PR42 executable handoff       100%
read-only preflight source    100%
```

All execution-bearing rows remain zero:

```text
successor Section-0 re-attestation  0%
target-host preflight               0%
global lease                        0%
local lease                         0%
native runtime                      0%
runtime-result audit                0%
first interval                      0%
provider export                     0%
```

## Retrieval

The plot agrees with the contract and GitHub ref readback: source exists, but
no successor receipt or attempt reservation has been created.

## Adversarial readings rejected

1. Two completed rows out of ten do not imply 20% solver completion.  The rows
   have different scientific and operational weight.
2. `READ_ONLY_PREFLIGHT_SOURCE = 100%` does not mean the target-host preflight
   has run.
3. `global ref absent` does not mean the global lease has been acquired or the
   attempt has been authorized.
4. A future successor Section-0 PASS does not imply native runtime, first
   interval, or provider PASS.

## Surviving claim

```text
The fail-closed read-only preflight source is implemented and can be executed
on an exact successor host without consuming attempt state.
```

## Withheld claim

```text
No target-host re-attestation, lease, native runtime, interval, provider or
scientific result is established by this figure.
```
