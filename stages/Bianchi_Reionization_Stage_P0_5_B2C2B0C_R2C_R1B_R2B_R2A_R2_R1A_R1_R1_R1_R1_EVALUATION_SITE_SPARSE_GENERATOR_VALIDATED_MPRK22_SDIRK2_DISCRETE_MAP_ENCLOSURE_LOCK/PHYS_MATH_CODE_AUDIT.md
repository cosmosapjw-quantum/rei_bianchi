# PHYS-MATH-CODE audit

## Equation-to-code map

| Equation/contract | Code path | Evidence |
|---|---|---|
| four source sites | `analysis/evaluation_site_trial.py` | all-lane bitwise primal parity |
| `A dz = db-dA z` | `analysis/implicit_certificates.py` | complex-step mismatch <= `3.372e-15` |
| population Krawczyk | `linear_interval_krawczyk` | 552,960 blocks pass |
| thermal derivative interval | `analysis/thermal_interval.py` | point and 101-sample interval tests |
| scalar root Krawczyk | `scalar_root_krawczyk` + local audit | 276,480 roots pass |
| stagewise counterexample | `analysis/run_stagewise_witness.py` | static hull escape reproduced |
| table-event distance auditor | `analysis/build_plots_and_event_audit.py` | non-load-bearing endpoint margin |

## TDD record

The missing local certificate APIs, thermal derivative interval, full root
interval and final-stage contract were each recorded as RED before the minimal
implementation. The cancellation-prone centered finite-difference oracle was
not patched by loosening tolerance; it was replaced by a complex-step oracle and
preserved as a failed attempt.

## Code-path reality

The wrapper delegates to the inherited production trial and changes only branch
policy dispatch. With identical controls it produces bitwise-equal state and
ledgers, so the audit path has not silently changed the primal physics.

## Remaining code blocker

No code currently propagates a rigorous second-order remainder across all four
sites, state-dependent owner normalization and thermal fixed-point feedback.
Neither table-event rollback nor set-valued ledger composition is connected to
that missing image. Consequently `full_discrete_map_enclosure_closed=false` is
correct even though all local certificates pass.

## Optimization honesty

No performance claim is made in this stage. BASS Rust remains optional and may
only accelerate a contraction after Python outward containment and event parity
are demonstrated.
