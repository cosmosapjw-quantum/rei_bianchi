# R2C failure analysis

## What failed

The failure is not photon/nuclei bookkeeping, KKT closure, timestep
convergence, or a serialization/runtime defect. Once the initial current is
put inside the capacity cone, every physically feasible lane converges.
The obstruction is the inferred constant equilibrium

\[
Y_{\rm eq}=Y_0+\frac{Y_1-Y_0}{1-\exp(-\Delta t/\tau)}.
\]

Because this is an extrapolation beyond the hard endpoint, it need not remain
inside the nonnegative mass/ionization/thermal/current cone or the coupled
capacity cone even when both endpoints are admissible.

## Constraint census

At `tau=10 Myr`, the dominant and universal obstruction is
`CYCLING_CAPACITY_DEFICIT` (216 macro constraints), with nine additional
`NEGATIVE_PHOTON_CURRENT` constraints in one SCRIPT case.

At `tau=100 Myr`, larger extrapolation also produces negative mass, ionized-H,
thermal measure, cycling capacity and photon current, over-ionization, and
macro mass-cap violations. At `tau=300 Myr` those failures broaden further.
The complete 2,363-row census is in `data/violated_constraints.csv`; no row is
clipped or silently discarded.

## What this rules out

It rules out the **specific** one-mode, common-timescale, constant-equilibrium
closure as an all-lane bridge between the locked R2B endpoints. It does not
rule out:

1. state-dependent or node-dependent physical rates;
2. separate relaxation spectra for mass, ionization, thermal, capacity and
   photon-current measures;
3. a positive two-mode kernel;
4. a non-autonomous constrained DAE whose equilibrium changes within the
   interval.

Those alternatives must be tested as model-adequacy questions before any
production history is generated.
