# Architecture lock

```text
BackgroundHistory / BackgroundSnapshot
            |
            v
R1 total-opacity / photon-control operator
            |
            +--> macro environment moments
            |       +--> constrained sink distribution
            |       +--> fixed-weight micro parcels
            |
            v
node H/He chemistry + thermal state
            |
            v
MatterSource {Omega, q_a, Pi_ab, Q_energy, Q_momentum}
            |
            v
Bianchi geometry backend (introduced only at C0)
```

Primordial recombination is an external `RecombinationProvider`; it is not part of the current chemistry implementation. The primitive Bianchi code is an immutable geometry/audit oracle until the B2E interface freezes.
