# P0.5-B2C2B0C-R2A — Global-moment-constrained macro sink distribution

## Durable verdict

```text
DURABLE_PASS_R2A_CORE_MACRO_DISTRIBUTION_LOCK_TAU10_FEASIBILITY_WITNESS_R2B_AUTHORIZED
```

`R2B MOMENT-CONSTRAINED-NODE-LIFT-HISTORY` is authorized. Full `B2C2B` authorization remains false.

## What was locked

For all 10 validated B2C2B0C reduced-DAE substeps and all three B2C2B0A shape priors, this stage holds fixed the global sink H inventory, sink ionized fraction and temperature, G1/G2a sink opacity and absorption moments, and the diffuse/sink H-transfer rate. It distributes those moments over the 18 macro states without solving a separate quasi-static cloud abundance.

All 30 constrained KL problems are strict-feasible identity information projections: the B2C2B0A prior itself lies inside the mass, volume, current-Gamma, and photo/recombination cycling-capacity constraints. Generalized KL, projection TV, KKT stationarity, and complementarity are exactly zero at the operator level. The maximum macro volume filling is 0.0906544 and the minimum mass-cap slack is 4.13308e-05 of the cosmic-H inventory.

G2b/G3 effective-HI sink opacity and primary HeII/G3 absorption remain exact zeros in both canonical source locks and R2A output.

## Finite-relaxation result

The separate implied-equilibrium auditor gives:

- tau=10 Myr: 30/30 absolute-state and 30/30 shape-only cases feasible;
- tau=100 Myr: 12/30 absolute-state and 18/30 shape-only cases feasible;
- tau=300 Myr: 6/30 absolute-state and 12/30 shape-only cases feasible.

The 10 Myr lane is only an existence witness, not a calibrated physical timescale. The 100/300 Myr failures are preserved as explicit sensitivity constraints for R2B; they were not clipped or hidden.

## Firewalls retained

R1 node diagnostics remain fail-closed and were not promoted. R2A did not start node chemistry history, unresolved subtraction, front/Q_M, source/fesc, primordial recombination, or Bianchi feedback. The external `rec_bianchi` remote remained unavailable in this runtime, and no recombination surrogate was implemented.
