# Design revision 2 — project the constructed initial current into the capacity cone

## Evidence requiring revision

The first full R2C run scaled the z=6 node cycling capacity by the locked
initial/first-endpoint sink-mass ratio while retaining the first-endpoint node
current distribution. This preserved every macro and global G1/G2a current
moment, but it left 25,356 node rows with negative cycling-capacity slack.
The total capacity of every macro remained sufficient, so the inconsistency
was distributive rather than global.

Repeated substep projections then acted as an implicit initialization repair.
As the refinement increased, the repair was applied nearer to the initial
boundary and the endpoint current error increased. The resulting first-step
nonconvergence was therefore a consequence of starting outside the hard cone,
not a defect in the backward-Euler order estimator.

## Minimal correction

Before any time step, apply one constrained generalized-KL projection to the
initial current of each inherited macro separately:

- preserve each macro's G1 and G2a current totals exactly;
- retain the fixed R2B micro-node support;
- enforce `sum_g J_mig <= C_mi` on every node;
- use no clipping and no current transport between macros;
- record the complete projection/KKT certificate;
- keep the R2A first-current/current-Gamma global and macro moments unchanged.

No R2B endpoint is modified. This revision only makes the constructed z=6
boundary state belong to the same admissible cone imposed on every subsequent
substep.
