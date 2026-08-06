# Dimension, sign, and limit audit

## Dimensions

- `kappa_g`, `kappa_g,o`: `cMpc^-1`.
- `J_g`, `J_g,o`: `s^-1 cMpc^-3`.
- `Phi_g=J_g/kappa_g`: `s^-1 cMpc^-2` under the inherited comoving convention.
- `integral J dt`: `cMpc^-3`.
- source coefficients are dimensionless ownership selectors.

All owner fractions and TV distances are dimensionless. No natural-unit substitution is made.

## Signs and structural zeros

All hazards, opacity shares, currents, capacities, and node weights are nonnegative. `EFFECTIVE_HI_SUBGRID` has exact zero resolved H, He, and thermal source coefficients. Unsupported species/group channels and the inherited primary G3 current remain exact zero.

## Limits

- A zero authoritative group current yields zero current for every owner even when opacity is nonzero.
- A zero owner hazard yields exact zero owner opacity and current.
- If only one owner has positive support, its conditional fraction is exactly one.
- The owner split is undefined if the authoritative total is positive but every raw hazard is zero; this fails closed.
- Refinement additivity tends to exact equality because the same continuous PCHIP forcing is integrated over a partition of the same interval.

## Non-load-bearing discrepancy

The raw reconstructed component opacities do not independently reproduce the authoritative total amplitude at all nodes; the maximum relative discrepancy is `1.1697853536868233e-3`. The operator therefore uses the raw components only to determine conditional fractions and preserves the canonical total amplitude exactly. Treating the raw sum as a new total calibration is forbidden.
