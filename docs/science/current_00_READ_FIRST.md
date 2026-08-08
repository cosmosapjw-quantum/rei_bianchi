# Current science state — rei_bianchi

Current durable stage:

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R1-POSITIVITY-CONSERVATIVE-SECOND-ORDER-THERMOCHEMISTRY-PREFLIGHT
DURABLE_PASS_R2C_R1B_R2B_R2A_R1_MPRK22_ALPHA1_LSTABLE_SDIRK2_CLOSE_ALL_LANES_AT_PARTITION_2048_FAST_ROOT_BACKEND_PROMOTED_EVENT_RESOLVED_PDS_LOCK_REQUIRED
```

The original MPRK22(1)+implicit-trapezoid attempt failed.  A separately locked
Alexander L-stable SDIRK2 thermal attempt closes the local-error gate in all
three lanes at partition 2048:

```text
local error:       6.392782e-05
H residual:        4.397361e-16
He residual:       4.504562e-16
owner residual:    1.953502e-16
photon residual:   1.449900e-16
thermal residual:  9.999943e-13
minimum species:   1.408422e-154
```

The analytic safeguarded root backend passes science parity and the predeclared
performance gate with `10.126360x`
matched-accuracy warm speedup.  No memory reduction is claimed.

This is not a production-history pass.  The current PDS flux tensor is a
deterministic decomposition of the net H/He RHS, but event-level helium reaction
and energy ownership is nonunique.  The exact counterexample and Wolfram proof
are in the stage receipts.

Next stage: `P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-EVENT-RESOLVED-FULL-OTS-PDS-OWNERSHIP-LOCK`.  Production node chemistry, R2C-R2, B2C2B,
recombination splice, CAMB transfer and Bianchi feedback remain unauthorized.
