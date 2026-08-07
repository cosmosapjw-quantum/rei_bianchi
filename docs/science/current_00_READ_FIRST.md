# Current science state — rei_bianchi

Current durable stage:

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2-OWNER-CORRECT-PHOTON-CONSERVING-NONAUTONOMOUS-FIXED-POINT-HISTORY-RERUN
DURABLE_FAIL_CLOSED_R2C_R1B_R2B_R2_NOMINAL_DT_TO_DT8_FIRST_SLAB_FIXED_POINT_NONCONVERGENCE_INTERNAL_DT256_EXISTENCE_WITNESS_ADAPTIVE_MICROSTEP_LOCK_AUTHORIZED
```

The R2B-R1 46,080-node material state and state-conditioned four-owner law were coupled to the owner-correct implicit H/He/thermal operator. At the first canonical BDF slab, all required macro refinements `dt,dt/2,dt/4,dt/8` failed the locked hard maximum Picard convergence gate after 40 iterations, with residuals `{'1': 0.13302637807989015, '2': 0.1469936199885531, '4': 0.10784482370613802, '8': 0.1186895886857986}`. H and He nuclei residuals remained below `8e-16`; no material-capacity or thermal-cone failure occurred, and rejected attempts preserved the parent byte image.

An internal interval/256 microstep converged to residual `4.9730886075849412e-11` in 25 iterations. This is an existence witness, not a production history. It rules out a physical-history no-go and identifies the missing object as a predeclared adaptive internal-microstep/globalization policy.

Next stage: `P0.5-B2C2B0C-R2C-R1B-R2B-R2A-ADAPTIVE-INTERNAL-MICROSTEP-ACCEPTANCE-AND-GLOBALIZATION-LOCK`. Production node chemistry, R2C-R2, B2C2B, recombination splice, CAMB and Bianchi feedback remain unauthorized.

`rec_bianchi/main` is connector-verified at PR-05B3/v0.61 (`796eabf6339b9a13355ccc61907a5314b9cd9196`). Only XOR ownership and accepted-step/rollback semantics are referenced; no numerical recombination input is imported.
