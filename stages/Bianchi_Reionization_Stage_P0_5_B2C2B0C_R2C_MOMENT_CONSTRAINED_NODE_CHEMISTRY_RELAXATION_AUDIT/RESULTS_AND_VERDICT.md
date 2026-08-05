# R2C results and verdict

## Scope and conventions

The audit uses homogeneous backgrounds, metric signature `(-,+,+,+)`,
`epsilon_123=+1`, and explicit `k_B=1.380649e-16 erg K^-1`. No natural-unit
conversion is made. The extensive variables are

\[
M_i,\qquad I_i=M_i x_{{\rm HII},i},\qquad
U_i=\frac32 k_B M_i T_i,\qquad C_i,\qquad J_{ig}.
\]

For each consecutive hard R2B endpoint and each
`tau={10,100,300} Myr`, the stage infers a constant equilibrium through the
exact exponential map and audits backward Euler at refinement factors 1, 2,
and 4. Current measures are constrained by fixed group totals and the node
cycling-capacity inequalities through generalized-KL projection. No clipping
is permitted.

## Initialization correction

The first full run exposed a boundary inconsistency: scaling the z=6 cycling
capacity with sink mass while retaining the first current distribution left
25,356, 25,590, and 26,009 rows outside the capacity cone in the three shape
lanes. Every macro still had sufficient total capacity. A single macro-local
KL projection was therefore applied before time integration, preserving each
macro's G1/G2a totals and current-Gamma opacity moments. It reduced the
post-projection violating-row count to zero; maximum group-total residual was
`2.08e-14` and maximum relative capacity violation was `6.77e-18`.

The superseded run and root-cause receipt are preserved under
`state/ATTEMPT_3_FIRST_FULL_RUN_UNPROJECTED_INITIAL_CURRENT/`.

## Feasibility and refinement

| tau [Myr] | feasible and convergent cases | requested cases |
|---:|---:|---:|
| 10 | 18 | 30 |
| 100 | 10 | 30 |
| 300 | 6 | 30 |

There are 90 shape/tau/substep cases and 1,620 macro equilibrium certificates.
The equilibrium-feasibility flag and the temporal-convergence flag agree in
all 90 cases: every feasible case converges, and no infeasible case is run or
promoted. The minimum observed `dt/2 -> dt/4` order among feasible cases is
`0.8705`. The largest n=4 endpoint error is `4.0357e-2`; this is retained as a
numerical-accuracy warning and is not used to justify production.

At `tau=10 Myr`, the 12 failures occur at interval/substep `(1,2)`, `(2,2)`,
`(3,1)`, and `(4,1)` in all three shape lanes. Every one of the 18 macros in
those cases violates the extrapolated cycling-capacity/current cone. The
SCRIPT self-shielding lane at `(3,1)` also has nine negative inferred photon
currents. Thus the R2A global/macro tau=10 feasibility witness does not survive
the stricter node-level capacity gate.

## Numerical and exact gates

- successful refined macro substeps: `4,802`
- fail-closed skipped macro substeps: `6,538`
- maximum group-column residual: `4.57e-16`
- maximum relative capacity violation: `3.13e-17`
- maximum KKT stationarity residual: `2.22e-16`
- maximum KKT complementarity residual: `0`
- maximum current-Gamma residual: `1.95e-16`
- H and He nuclei identity residuals: exactly `0`
- exact-zero G2b/G3 effective-HI and primary HeII/G3 rows: `450/450`
- clipping: never used

Native Wolfram execution was unavailable in this runtime. The complete `.wl`
validation script is included, and the independent SymPy plus 90-digit Decimal
fallback proves the endpoint, semigroup, backward-Euler limit, nuclei,
current-Gamma, KKT, and exact-zero identities with zero 90-digit endpoint and
semigroup residuals.

## Durable decision

```text
DURABLE_FAIL_CLOSED_R2C_CONSTANT_EQUILIBRIUM_RELAXATION_NOT_ALL_LANES_REACHABLE
```

The static R2B lift remains a valid constrained endpoint construction, but a
single positive relaxation time and one constant equilibrium per interval do
not supply an admissible node history for all locked endpoints. Production
node chemistry and B2C2B remain unauthorized.
