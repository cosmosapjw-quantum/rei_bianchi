# PHYS-MATH-CODE audit

## Equation-to-code map

| Contract | Implementation |
|---|---|
| four independent source sites | `analysis/interval_discrete_map.py` |
| outward interval primitives and local linear certificate | `analysis/cross_site_discrete_map.py` |
| MPRK22 full and half maps | `analysis/interval_discrete_map.py` |
| analytic thermal derivative and interval Newton | `analysis/interval_discrete_map.py` |
| table path-hull detector and restart | `analysis/cross_site_discrete_map.py`, `analysis/table_event_restart_audit.py` |
| exact structural ledgers | `analysis/exact_symbolic_validator.py` |
| direct witness/interior containment | `analysis/containment_audit.py` |
| independent result replay | `analysis/independent_stage_validator.py` |
| partition and plot evidence | `analysis/run_partition_case.py`, `analysis/plot_stage_evidence.py` |

## Code-path reality

- Load-bearing lane cases were run in fresh processes to avoid optional
  extension-runtime teardown/state interference.
- The interval implementation calls the inherited event graph, owner law,
  physical trial and forcing data; it does not substitute a toy ODE.
- Tangent/enclosure code is disabled in primal parity controls.
- Failed attempts are preserved and not used as positive evidence.

## Numerical findings

- all three lanes pass at partition 2048;
- partition 1024 encloses the map but fails local error;
- partitions 2048 and 4096 pass;
- widths and local error decrease under refinement;
- maximum local Krawczyk row sum is `0.015847428383092121`;
- no load-bearing table event occurs;
- direct stagewise and interior containment pass.

## Regression risk

1. same-process orchestration can hang after successful output in optional
   extension teardown; fresh-process lane execution is authoritative;
2. manifest generation must exclude caches and self-referential artifacts;
3. structural ledgers must not be replaced by independently widened interval
   total subtraction;
4. Rust acceleration must not own topology or acceptance decisions.

## Test sufficiency

Current stage tests cover primitives, local error, structural identities,
partition acceptance, direct containment, event rollback, independent replay,
and preserved invalid attempts. Repository-wide file-isolated verification completed in fresh processes:
`75` files, `291` passed assertions, `0` failures. The pinned Rust 1.94.1
toolchain was restored for the inherited optional Rust regression; it remains
non-load-bearing for this stage.

## Verdict

The code supports the bounded one-microstep durable pass. It does not yet
support first-interval or production-history claims.
