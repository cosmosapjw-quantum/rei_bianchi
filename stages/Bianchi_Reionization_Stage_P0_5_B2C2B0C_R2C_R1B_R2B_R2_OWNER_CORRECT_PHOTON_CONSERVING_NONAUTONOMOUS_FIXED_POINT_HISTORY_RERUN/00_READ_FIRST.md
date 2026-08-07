# R2B-R2 owner-correct fixed-point history rerun — read first

This durable stage is a **fail-closed numerical-policy result**, not a production history.

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2-
OWNER-CORRECT-PHOTON-CONSERVING-NONAUTONOMOUS-FIXED-POINT-HISTORY-RERUN

DURABLE_FAIL_CLOSED_R2C_R1B_R2B_R2_
NOMINAL_DT_TO_DT8_FIRST_SLAB_FIXED_POINT_NONCONVERGENCE_
INTERNAL_DT256_EXISTENCE_WITNESS_ADAPTIVE_MICROSTEP_LOCK_AUTHORIZED
```

The exact 46,080-node R2B-R1 material state, state-conditioned owner law, 17-node canonical BDF forcing and positive implicit H/He/thermal map were exercised at the first canonical slab. All required macro refinements `dt,dt/2,dt/4,dt/8` failed only the prelocked hard maximum Picard convergence gate after 40 iterations. H and He nuclei residuals stayed below `8e-16`, species and temperature remained positive, and rejected solves preserved the parent byte image.

A much smaller internal step, interval/256, converged below the same `1e-10` hard residual. This is an existence witness only: it excludes a physical-history no-go but does not define an accepted adaptive controller or promote node chemistry.

The next stage is:

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-
ADAPTIVE-INTERNAL-MICROSTEP-ACCEPTANCE-AND-GLOBALIZATION-LOCK
```

Production node chemistry, R2C-R2, B2C2B, recombination splice, CAMB transfer and Bianchi feedback remain unauthorized.
