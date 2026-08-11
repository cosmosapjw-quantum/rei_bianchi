# Plot-driven CRAG adversarial audit

## Evidence read directly from plots

### Validated widths versus gate

All four public widths lie far below `2e-3`; `log_T` is the largest. The plot
supports a one-microstep uncertainty claim only.

### Partition sensitivity

All four widths decrease from partitions 1024 to 2048 to 4096. No coordinate
shows a refinement reversal.

### Local Krawczyk margins

Every displayed row-sum is below `1.6e-2`, far from the contraction limit 1.
Local implicit conditioning is not the limiting uncertainty.

### Table-event clearance

The nearest-knot distance exceeds the `ln T` enclosure width at every tested
partition. The smallest clearance ratio is `2.86892743475`.

### Validated local error

Partition 1024 lies above `2e-4`; 2048 and 4096 lie below. This plot caused an
actual narrowing of the claim: public width alone was insufficient for adaptive
acceptance.

## CRAG

- **Correctness:** plot values reproduce sealed JSON and gates.
- **Retrieval:** behavior agrees with refined-map expectations, but no formal
  observed-order claim is made from only three points.
- **Augmented:** three shape lanes and three partitions were checked; first-
  interval accumulation is not yet checked.
- **Generation:** the next likely limiter is accumulated thermal width or a
  table event, not local MPRK conditioning.

## Adversarial mutations

| Mutation | Result |
|---|---|
| static temporal coherence | rejected by stagewise witness |
| endpoint-only event detection | rejected by between-site crossing |
| halve partition count to 1024 | local-error gate fails |
| refine to 4096 | widths and local error decrease |
| replace exact ledger with raw interval subtraction | loses sharpness; rejected as authority |

## Claim status

```text
surviving:
  four-site source-safe accepted microstep at partition 2048 is enclosed
  and passes width/local-error/containment/event/structural-ledger gates

narrowed:
  event restart semantics are certified, but the load-bearing step is event-free

rejected:
  production history, first canonical interval, Bianchi-family history,
  arbitrary-platform formal proof
```
