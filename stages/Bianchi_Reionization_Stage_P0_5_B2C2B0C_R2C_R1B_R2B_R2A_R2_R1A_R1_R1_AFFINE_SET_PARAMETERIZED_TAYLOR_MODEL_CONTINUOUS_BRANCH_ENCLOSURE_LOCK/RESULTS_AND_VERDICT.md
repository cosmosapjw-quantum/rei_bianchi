# Results and verdict

## Verdict

```text
DURABLE_FAIL_CLOSED_R2_R1A_R1_R1_
SOURCE_SAFE_PARAMETER_RANK_NOT_REPRESENTED_
COHERENT_GLOBAL_TAYLOR_AUDITOR_NARROW_
SPARSE_LOCAL_GENERATOR_LOCK_AUTHORIZED
```

## Rank result

- node count: `46080`
- robust rank-two node blocks: `45923`
- rank-one remainder blocks: `157`
- source-safe sensitivity-rank lower bound: `92003`
- coherent global parameter rank: `2`
- rank deficiency: `92001`
- sparse quadratic local-generator storage: `4.21875 MiB`
- dense generator matrix estimate: `0.123596 TiB`

## Coherent auditor

All three shape lanes pass all inherited numerical and ledger gates on the locked 3x3 training grid and five withheld points.  The maximum coherent empirical widths are

```text
x_HII   2.3891773770e-06
x_HeII  7.3120954844e-06
x_HeIII 5.3728507095e-09
log_T   3.3999308329e-05
```

The maximum withheld absolute residual is `1.96719e-10`.  These values are conditional on one coherent global `alpha` and one coherent global `beta`; they are not source-safe enclosure widths.

Two node-local sign-selected adversarial trajectories remain inside the global corner envelope after a 128-ulp robustness tolerance.  Raw last-bit excursions occur in some components but are non-load-bearing.  Their failure to leave the endpoint hull does not remove the exact instantaneous rank mismatch.

## Claim boundary

The stage proves that the authorized two-generator affine/Taylor ansatz is dimensionally insufficient for the source-safe node-local branch family.  It does not prove that the physical continuous family is wide or that an uncertainty-qualified history does not exist.


## Verification boundary

Fresh file-isolated regression covers `61` test files and `249` tests with zero failures. The stage tests report `8 passed`, the independent validator reports `PASS`, and the research harness validator reports `PASS`.
