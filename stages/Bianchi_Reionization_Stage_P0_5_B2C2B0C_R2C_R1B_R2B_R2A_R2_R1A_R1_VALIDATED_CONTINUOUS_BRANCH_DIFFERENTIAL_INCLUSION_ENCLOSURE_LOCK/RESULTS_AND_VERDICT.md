# Results and verdict — R2-R1A-R1

## Verdict

```text
DURABLE_FAIL_CLOSED_R2_R1A_R1_CONSTANT_ORTHANT_EXCLUDED_COMPONENTWISE_BOX_WRAPPING_CROSSES_SOURCE_TABLE_BOUNDARY_AFFINE_TAYLOR_MODEL_LOCK_AUTHORIZED
```

The stage is complete as a bounded method-selection audit.  It does not certify the continuous `(v,f)` family, does not authorize production history, and does not claim physical nonexistence.

## Evidence

1. The previous 24 numerical realization runs all passed fixed-point, positivity, H/He nuclei, owner, photon, thermal, PDS, and unresolved-OTS energy gates.  Their strict-corner endpoint widths were `2.3889647e-6`, `7.3120149e-6`, `5.3727747e-9`, and `3.3999420e-5` for `x_HII`, `x_HeII`, `x_HeIII`, and `log T`.
2. A robust sign reversal in `d(d log T/dt)/d x_HII` excludes every constant diagonal orthant comparison theorem.
3. The directed-rounding Picard implementation certifies an analytic scalar control problem.
4. On the project RHS, partitions 16, 32, and 64 all fail in the first segment because componentwise wrapping pushes the tube through the upper Hummer--Seaton source boundary.
5. No table extrapolation, clipping, owner reassignment, or source-function fitting was used.

## Interpretation

The numerical corner evidence strongly suggests that the physical uncertainty is narrow over this microstep, but it is not a theorem.  The failed box audit shows that an axis-aligned interval representation destroys the state/parameter correlations needed to prove that fact.  The failure is therefore assigned to the enclosure representation, not to the thermochemistry equations or to existence of physical trajectories.

## Authorization

```text
continuous_parameter_certified        = false
production_history_authorized          = false
production_node_chemistry_authorized   = false
R2C_R2_authorized                      = false
B2C2B_authorized                       = false
affine_Taylor_model_next_stage         = true
```
