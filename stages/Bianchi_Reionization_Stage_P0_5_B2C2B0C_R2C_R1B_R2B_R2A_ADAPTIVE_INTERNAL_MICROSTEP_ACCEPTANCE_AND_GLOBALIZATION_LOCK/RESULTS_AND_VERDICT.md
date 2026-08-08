# Results and verdict — R2B-R2A

## Verdict

```text
DURABLE_FAIL_CLOSED_R2C_R1B_R2B_R2A_DT1024_LOCAL_ERROR_FAILURE_FIXED_POINT_AND_CONSERVATION_GATES_PASS_DEEPER_DT4096_AUDITOR_PASS
```

This is a completed bounded audit and a fail-closed science stage. It is not a
production-history pass.

## Adaptive three-lane result

All predeclared lanes reached the same earliest certificate:

| Lane | Attempts | Bisections | Maximum partition | Fixed point at 1024 | Local error | Elapsed s |
|---|---:|---:|---:|---|---:|---:|
| `LOCAL_NEUTRAL_HAZARD_PRIMARY` | 8 | 7 | 1024 | PASS_AT_MINIMUM_PARTITION | 8.398655920e-04 | 76.814 |
| `RECOMBINATION_WEIGHTED_AUDITOR` | 8 | 7 | 1024 | PASS_AT_MINIMUM_PARTITION | 8.398655920e-04 | 76.487 |
| `SCRIPT_SELF_SHIELDING_AUDITOR` | 8 | 7 | 1024 | PASS_AT_MINIMUM_PARTITION | 8.398655920e-04 | 76.054 |


At partitions 8, 16, 32 and 64 the earliest certificate is fixed-point
nonconvergence. From partition 128 onward all full and half trials converge,
and the earliest certificate becomes the hard local-error gate. At the locked
minimum partition 1024:

```text
fixed-point residuals: below 1e-10 for all three trials
local error:           0.00083986559199900057
locked threshold:      2e-4
```

All non-local-error gates pass:

```text
max H nuclei residual:        6.6597779806276521e-16
max He nuclei residual:       7.1341279867285638e-16
max photon residual:          2.7964414122537431e-16
max thermal balance residual: 1.2687726288519003e-14
minimum species count:        2.1499811260378858e-155
rollback byte identity:       true
restart identity:             true
accepted commits:             0
```

Because the terminal path is rejected, the accepted ledger is unchanged. This
is expected transactional behavior, not missing bookkeeping.

## Local-error diagnosis

The hard maximum error is dominated by `log T`; `x_HeII` is the second-largest
component. The maximum `log T` differences are approximately:

```text
dt/512:  2.4708046e-3
dt/1024: 8.3986561e-4
dt/2048: 2.6265219e-4
dt/4096: 7.8722761e-5
```

A post-lock deeper-partition auditor therefore passes at partition 4096 but not
at 2048. Since the input lock fixed the minimum partition at 1024, this cannot
be relabelled as a current-stage pass.

## Performance result

The array-native owner kernel reproduces the legacy oracle and reduces the
100-call benchmark from `22.208009` s to
`0.697513` s:

```text
speedup: 31.838842261x
max-RSS reduction: 0.849%
```

The owner hot path meets the predeclared `>=5x` promotion gate. A whole-solver
speedup is not claimed: the comparable legacy physical benchmark timed out, and
the stable NumPy candidate requires about 76 s per rejected three-lane first
segment audit. The JAX thermal candidate passed isolated parity but stalled in
repeated science-scale synchronization and is not promoted.

## Scientific interpretation

The previous macro-step Picard blocker is resolved. The remaining load-bearing
blocker is first-order thermochemistry local truncation error under the hard
maximum-node metric. The positive/conservative physical operator, owner
allocation, photon ledger, nuclei identities and thermal implicit solve do not
show a no-go.

## Authorization

```text
R2C_R1B_R2B_R2A_completed = true
R2C_R1B_R2B_R2A_R1_authorized = true
R2C_R1B_R2B_completed = false
production_node_chemistry_authorized = false
R2C_R2_authorized = false
B2C2B_authorized = false
```

## Repository-wide test execution note

All 150 collected tests pass when each of the 33 historical test files is run in a fresh Python process. Two monolithic runs timed out at different late-suite boundaries without an assertion failure; the timeout and the isolated-pass matrix are both preserved. This changes no science gate.
