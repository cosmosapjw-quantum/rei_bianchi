# Current science state — rei_bianchi

Current durable stage:

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-ADAPTIVE-INTERNAL-MICROSTEP-ACCEPTANCE-AND-GLOBALIZATION-LOCK
DURABLE_FAIL_CLOSED_R2C_R1B_R2B_R2A_DT1024_LOCAL_ERROR_FAILURE_FIXED_POINT_AND_CONSERVATION_GATES_PASS_DEEPER_DT4096_AUDITOR_PASS
```

The adaptive/globalization blocker is removed through recursive bisection and safeguarded damped Picard. All fixed-point, positivity, owner/photon, H/He nuclei and thermal-ledger gates close at the locked minimum `dt/1024`, but the full-versus-two-half hard maximum local error is `8.398655919990006e-4`, above `2e-4`. A post-lock auditor passes at `dt/4096`; it is not production-promoted.

The array-native owner hot path is promoted (`31.84x` benchmark speedup); JAX remains diagnostic and NumPy is the stable production oracle. No microstep was accepted, no production node history exists, and `R2C-R2`, `B2C2B`, recombination splice, CAMB and Bianchi feedback remain unauthorized.

Next stage: `P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R1-POSITIVITY-CONSERVATIVE-SECOND-ORDER-THERMOCHEMISTRY-PREFLIGHT`.
