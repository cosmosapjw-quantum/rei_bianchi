# R2C-R1B validation report

## Data coverage

- Node-state endpoint rows: `1,382,400`.
- Node/group endpoint rows: `2,764,800`.
- Shape/substep/group endpoint summaries: `60`.
- Node-level shape-pair TV comparisons: `1,080`.
- Global photon-ledger intervals: `5`.

There were zero nonfinite endpoint states, zero endpoint cone failures, zero
negative node currents, zero negative node opacities, and zero nonpositive
inherited flux rows.

## Algebraic endpoint checks

The maximum relative residual in `J=kappa Phi` is `9.1434613e-16`.  Source
inspection confirms that R2B first projects `J`, defines macro `Phi=J/kappa`,
and then sets node `kappa=J/Phi`.  The identity is therefore a correct endpoint
moment check but not independent evidence for a dynamic-opacity law.

## Global/sink partition

The time-weighted sink G1+G2a current is `0.4361578--0.5464111` of the global
G1+G2a absorption.  G2b contributes `0.00492--0.01789` of all global group
absorption and is absent from the R2B active sink lift.  The global ledger is
not a node/sink boundary condition.

## Constructive rank and null tests

- Single history, eight knots: rank/nullity `(3,5)`.
- `46,080` nodes, eight knots, fixed node endpoints and pointwise total:
  nullity `276,474` per group/case.
- Temporal witness: endpoints exact, integral residual `1.30e-16`, currents
  positive, interior relative separation `0.3991`.
- Spatial witness: pointwise total residual `1.51e-16`, endpoints exact,
  currents positive, nonzero opposite node-integral shifts.

## Shape-prior dependence

Macro-current shape differences are small (`TV<=5.50e-6`) because the macro
moments are tightly locked.  Within each fixed macro/group total, node
allocation remains shape dependent: TV minimum/median/maximum are
`0.006316/0.053431/0.330056`.

## Thermal audit

The fixed `E^-2.5` primary spectrum supplies candidate group moments, but the
absorbed energy depends on optical depth.  The global thin/thick atomic-HI
heating envelope differs by `14.75--18.60%` across intervals.  This is an
auditor, not a production thermal solution.

## Independent computation

- Wolfram plugin: Metzler signs, zero column sums, integrated ledger,
  temporal/spatial nulls, and rank/nullity all pass.
- Precise Special Functions plugin, 80 dps: `Gamma(3)`, `Gamma(4)`,
  `zeta(3)`, `zeta(4)` and the number/energy moment ratio pass.
- SymPy/mpmath fallback, 100 dps: pass.
- Independent replay: maximum global partition residual `3.33e-16`, analytic
  spectral replay `9.28e-16`, endpoint relation replay `9.14e-16`; all gates
  pass.

## Validation conclusion

The fail-closed identifiability verdict is supported.  Numerical integration
was deliberately not attempted because its operator inputs are not yet
identified.
