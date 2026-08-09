# PHYS-MATH audit

| Check | Result | Evidence / limitation |
|---|---|---|
| Definitions and coordinates | PASS | Reduced coordinates and dimensionless branch parameters are explicit. |
| Units | PASS | All reduced RHS generators have `s^-1`; bounds preserve units. |
| H nuclei | PASS | Every population generator sums to zero in the H block. |
| He nuclei | PASS | Every population generator sums to zero in the He block. |
| Branch bilinearity | PASS | `v`, `f`, and `vf` coefficients reproduce direct source evaluation. |
| Positivity of parameter domain | PASS at source level | Bounds use exact square corners; this is not a positive discrete-map proof. |
| Global normalization structure | PASS | `h/sum(h)` derivative is local plus one rank-one mode. |
| Hummer-Seaton topology | PASS as event contract | No extrapolation; event distance is recorded. |
| Static-substep control completeness | **FAIL / P0** | An admissible localized stagewise schedule escapes the static-corner hull. |
| Validated MPRK22/SDIRK2 remainder | **OPEN / P0** | No outward proof for state feedback and cross-evaluation-site dependence. |

The failure narrows the claim; it does not invalidate the underlying event
physics or the accepted point trajectories.
