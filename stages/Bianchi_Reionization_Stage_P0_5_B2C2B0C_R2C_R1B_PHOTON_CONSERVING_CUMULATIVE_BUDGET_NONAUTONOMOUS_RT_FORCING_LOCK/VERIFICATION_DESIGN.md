# R2C-R1B verification design

## Decisive questions

1. Do the locked artifacts contain an independent time-resolved boundary or
   source history by group?
2. Is the global-to-sink-to-node partition uniquely supplied?
3. Is node opacity a constitutive function of evolving state rather than an
   endpoint quotient `J/Phi`?
4. Does photon-number closure identify energy deposition and temperature?

## Minimal tests

- Inventory every candidate source, boundary, opacity, partition, and heating
  field before constructing a history.
- Replay the global sink/global ledger ratios.
- Compute exact constraint ranks and nullities.
- Construct positive temporal and spatial null witnesses from actual R2B
  node currents.
- Audit node endpoint signs and `J=kappa Phi` without interpreting that
  algebraic identity as a dynamic law.
- Compare optically thin and thick energy-weighted moments under the locked
  primary spectrum.
- Verify all identities independently with Wolfram, SymPy, mpmath, and a
  separate validator that does not import the producer.

## Pass criterion

R2C-R1B can pass as a forcing lock only if the canonical inputs predeclare,
without per-node fitting:

- time-resolved incident or absorbed group forcing;
- dynamic opacity/optical-depth closure;
- node allocation or transport geometry;
- energy-weighted heating and cooling operator;
- a convergent photon/chemistry and separately convergent thermal fixed point.

Endpoint feasibility and global ledger closure alone are insufficient.

## Fail-closed criterion

A nontrivial positive null family preserving all currently locked constraints,
or a missing load-bearing constitutive input, is sufficient to fail closed on
identifiability.  Such a failure does not assert physical nonexistence.
