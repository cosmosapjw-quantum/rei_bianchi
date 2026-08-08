# Read first — R2B-R2A adaptive globalization and optimization lock

Stage:

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-
ADAPTIVE-INTERNAL-MICROSTEP-ACCEPTANCE-AND-GLOBALIZATION-LOCK
```

Verdict:

```text
DURABLE_FAIL_CLOSED_R2C_R1B_R2B_R2A_DT1024_LOCAL_ERROR_FAILURE_FIXED_POINT_AND_CONSERVATION_GATES_PASS_DEEPER_DT4096_AUDITOR_PASS
```

The previous first-slab Picard blocker is removed: all full and half trials
converge at the predeclared minimum partition `dt/1024`, with positivity,
owner/photon closure, H/He nuclei identities, resolved thermal balance,
rollback and restart gates closed. The stage still fails closed because the
full-versus-two-half hard maximum local error is
`0.00083986559199900057`, above the locked `2e-4`
threshold.

A post-lock feasibility auditor gives local errors
`0.0002626521892992173` at `dt/2048` and
`7.872276255582733e-05` at `dt/4096`; only the latter passes.
These deeper rows do not rescue the prelocked `dt/1024` production gate.

The array-native owner hot path is promoted with parity and a
`31.838842x` speedup. Whole-solver performance is not
promoted because no comparable legacy science-scale run completed. The JAX
thermal candidate remains diagnostic after reproducible science-sequence
synchronization stalls; the stable production backend is the NumPy array
oracle.

No microstep was accepted, so all ten ledgers remain at their parent values and
no production node chemistry is promoted. `R2C-R2`, `B2C2B`, recombination
splice, CAMB transfer and Bianchi feedback remain unauthorized.

Next bounded stage:

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R1-POSITIVITY-CONSERVATIVE-SECOND-ORDER-THERMOCHEMISTRY-PREFLIGHT
```
