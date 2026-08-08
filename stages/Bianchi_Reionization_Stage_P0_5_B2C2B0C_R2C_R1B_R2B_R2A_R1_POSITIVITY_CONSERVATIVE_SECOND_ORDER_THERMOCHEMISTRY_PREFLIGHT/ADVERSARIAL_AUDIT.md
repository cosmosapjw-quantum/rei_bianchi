# Adversarial audit

## Attacks that failed

- Negative or zero species input is rejected before MPRK assembly.
- Nonconservative H or He RHS blocks fail closed.
- Unsupported owner/group channels remain exact zero.
- The subgrid owner has exact-zero resolved H, He and thermal source.
- Parent state is not mutated by full/two-half trial evaluation.
- The analytic thermal root remains inside the positive bracket and falls back
  to bisection when Newton is unsafe.
- A 90-digit Decimal approximation is not used as an exact algebra oracle after
  the recorded validator false negative.

## Load-bearing limitation

The deterministic greedy PDS decomposition is not event-resolved.  In the He
block, both

```text
HeI -> HeIII
```

and

```text
HeI -> HeII plus HeII -> HeIII
```

produce the same net RHS `(-1,0,+1)`.  Their energy and reaction ownership differ.
This prevents production-history promotion even though positivity, conservation,
accuracy and performance gates pass.

## Prohibited interpretation

Do not claim that MPRK unconditionally preserves the original full-OTS event
ledger merely because it preserves the deterministic net-RHS decomposition.
That stronger statement requires the next source-level ownership lock.
