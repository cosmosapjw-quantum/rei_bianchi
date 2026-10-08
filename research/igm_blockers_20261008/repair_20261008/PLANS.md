# Repair milestones

1. `DONE`: carry paired photon number/energy canonical values through density, weighting, observers and restart; preserve scalar compatibility.
2. `DONE`: add V3 checkpoint records for paired density and direct heat owner metadata, with explicit V1/V2 migration.
3. `DONE`: resume the pinned partial checkpoints; coarse k14, fine k28 and tail k14 pass the unchanged common-epoch checks.
4. `DONE`: replace ambiguous subnormal A/B subtraction with a direct positive excess-energy owner only when the historical operation cannot resolve the sign. Coarse k15 and k16 accept.
5. `STOPPED_BY_RULE`: coarse k17 requires a tracked stock/source-convolution solver path. The rejected state and counts are preserved; no tolerance or zero-floor workaround was used.
6. `DONE`: exact repository CI commands and the 16-test numerical library suite pass. The nested research package formatter still reports preserved compact snapshot files; repository CI formatting passes.
7. `PENDING`: implement a bounded `Tracked/Wide` characteristic stock/source path, then re-run k17 only. Broader horizons remain conditional on that common state passing all original gates.

Rollback is removal of the paired/direct-heat V3 path. No original checkpoint or accepted historical evidence was mutated.
