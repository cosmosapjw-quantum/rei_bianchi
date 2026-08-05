# R2C-R1 macro-shared multirate cone lock — read first

Current durable stage:

```text
P0.5-B2C2B0C-R2C-R1-RATE-DERIVED-POSITIVE-MULTIRATE-RELAXATION-CONE-LOCK
DURABLE_FAIL_CLOSED_R2C_R1_MACRO_SHARED_COMMON_EQUILIBRIUM_MULTIRATE_CONE_NOT_ALL_LANES_REACHABLE
```

This stage tested a deliberately bounded model class: for each macro and each
family `M,I,U,C,J_G1,J_G2a`, one positive rate is shared by all 2,560 fixed
micro nodes. Rates lie in intervals frozen before feasibility from inherited
secants and explicit process-rate evidence. One exponential mode was mandatory
first; a two-mode completely monotone mixture was allowed only after one-mode
trajectory failure and added no new endpoint attenuation freedom.

The result is fail-closed. Of 540 macro cases, 43 had an equilibrium inside the
locked cone, 43 had an analytically certified one- or two-mode trajectory, and
27 passed the full `dt/2,dt/4,dt/8` refinement gate. No shape lane passed all
180 macro cases. The other 497 cases have independently replayed Farkas
certificates: 209 cycling-capacity, 125 G1-current, 157 G2a-current, and six
macro-mass-cap obstructions.

This is a no-go only for the **macro-shared, common-equilibrium, locked-rate-box
model class**. It does not rule out deterministic node-local physical rate
fields, non-autonomous forcing, or a physics-derived coupled positive
generator. It does rule out repairing the 497 equilibrium no-go cases merely
by adding more positive exponential modes while retaining the same common
equilibrium and rate box.

Production node chemistry, R2C-R2, and B2C2B remain unauthorized. The next
bounded task is the node-local physics-derived rate-field identifiability and
cone preflight in `NEXT_STAGE_PROMPT.md`; rate intervals must not be widened
from the post-result dual diagnostic.
