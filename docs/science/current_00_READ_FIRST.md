# R2C-R1 macro-shared multirate cone lock — current durable science state

Current stage:

```text
P0.5-B2C2B0C-R2C-R1-RATE-DERIVED-POSITIVE-MULTIRATE-RELAXATION-CONE-LOCK
DURABLE_FAIL_CLOSED_R2C_R1_MACRO_SHARED_COMMON_EQUILIBRIUM_MULTIRATE_CONE_NOT_ALL_LANES_REACHABLE
```

R2C-R1 froze 3,240 macro-shared physical/nuisance rate intervals before
feasibility and tested 540 macro cases over all three shape priors and ten
reduced-DAE substeps. Only 43 equilibrium boxes were feasible. All 43 obtained
an analytically certified one- or two-mode path, but only 27 passed the full
`dt/2,dt/4,dt/8` gate and no shape lane passed all 180 macro cases. The other
497 cases have independently replayed Farkas certificates: 209 cycling, 125
G1-current, 157 G2a-current, and six macro-mass-cap no-go rows.

Adding more positive exponential modes cannot repair those 497 failures while
the same common equilibrium and rate box are retained; mode count changes
interior path shape, not the endpoint equilibrium box. This is not a no-go for
deterministic node-local physical rate fields or a coupled/non-autonomous
positive operator.

Production node chemistry, R2C-R2, and B2C2B remain unauthorized. The next
bounded stage is
`P0.5-B2C2B0C-R2C-R1A-NODE-LOCAL-PHYSICS-DERIVED-RATE-FIELD-CONE-PREFLIGHT`.
It must derive node dependence from explicit local physics rather than fit one
free rate per node, and it must not widen R2C-R1 bounds from the post-result
dual diagnostic.
