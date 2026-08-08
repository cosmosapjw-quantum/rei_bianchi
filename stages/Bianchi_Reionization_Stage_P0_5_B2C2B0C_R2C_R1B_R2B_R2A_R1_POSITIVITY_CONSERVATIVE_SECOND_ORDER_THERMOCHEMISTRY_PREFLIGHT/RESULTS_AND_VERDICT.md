# Results and verdict — R2B-R2A-R1

## Verdict

```text
DURABLE_PASS_R2C_R1B_R2B_R2A_R1_MPRK22_ALPHA1_LSTABLE_SDIRK2_CLOSE_ALL_LANES_AT_PARTITION_2048_FAST_ROOT_BACKEND_PROMOTED_EVENT_RESOLVED_PDS_LOCK_REQUIRED
```

This is a narrow durable pass for a second-order positive/conservative
thermochemistry preflight.  It is not a production-history pass.

## Attempt ledger

1. `ATTEMPT_0_MPRK22_ALPHA1_TRAPEZOID` was the originally locked candidate.
   It failed the local-error gate at partition 2048 with
   `0.0007087377621424196`.
2. `ATTEMPT_1_MPRK22_ALPHA1_LSTABLE_SDIRK2_THERMAL` was separately locked
   before implementation.  It passed all lanes at partition 2048.
3. The first combined matched-accuracy benchmark timed out and an import-order
   benchmark failed; both are preserved as Attempt 2 evidence.
4. `ATTEMPT_3_ANALYTIC_THERMAL_NEWTON_OPTIMIZATION` changed no physical equation
   or RK coefficient.  It reproduced the bisection reference and passed the
   performance gate.
5. `ATTEMPT_4_DECIMAL_EXACT_EQUALITY_VALIDATOR_FALSE_NEGATIVE` records a
   validator-only `-3E-90` Decimal equality false negative.  SymPy exact algebra
   and Decimal-90 replay both pass after correction.

## Science matrix

| Partition | Maximum local error | Disposition |
|---:|---:|---|
| 512 | `0.00285960302` | fail |
| 1024 | `0.000525038599` | fail |
| 2048 | `6.39278236e-05` | pass |

All three lanes pass at 2048:

- `LOCAL_NEUTRAL_HAZARD_PRIMARY`
- `RECOMBINATION_WEIGHTED_AUDITOR`
- `SCRIPT_SELF_SHIELDING_AUDITOR`

Maximum partition-2048 residuals:

```text
H nuclei:          4.397361e-16
He nuclei:         4.504562e-16
owner closure:     1.953502e-16
photon closure:    1.449900e-16
thermal balance:   9.999943e-13
PDS reconstruction:5.069599e-16
minimum species:   1.408422e-154
```

No clipping, owner reassignment, `kappa=J/Phi` inversion, per-node fitting, or
numerical recombination import was used.

## Performance

At matched local accuracy, five independent warm candidate processes and three
independent BE reference processes give median runtimes

```text
candidate MPRK22+SDIRK2, partition 2048: 0.791705 s
backward Euler, partition 4096:           8.017088 s
speedup:                                  10.126360 x
```

The predeclared primary `5x` gate passes.  Peak RSS is about 9.7 percent higher,
so no memory-reduction claim is made.

## Claim boundary

A net conservative RHS does not uniquely determine event-resolved reaction
fluxes in the helium block.  The exact counterexample is stored in
`receipts/EXACT_VALIDATION.json` and verified by Wolfram.  Consequently:

```text
production history integrated:          false
production node chemistry authorized:   false
R2C-R2 authorized:                      false
B2C2B authorized:                       false
```

The next stage must source-lock full-OTS reaction and energy ownership before
using this method in the first accepted canonical interval.
