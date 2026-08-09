# PHYS-MATH-CODE audit

## Equation-to-code map

| Equation/contract | Code path | Status |
|---|---|---|
| Local bilinear source | `analysis/source_generators.py` | exact at one evaluation site |
| Sparse polynomial storage | `analysis/sparse_local_model.py` | implemented and tested |
| Owner-amplitude rank | `analysis/global_coupling.py` | analytic + centered-difference audit |
| Node normalization JVP | `analysis/global_coupling.py` | local + rank-one decomposition |
| Outward bounds | Python model and `rust/sparse_bounds.rs` | differential parity, <=1 ULP gate |
| Locked point solver | inherited MPRK22/SDIRK2 path | used by temporal witness |
| Stagewise control audit | `analysis/temporal_control_audit.py` | actual solver path, three lanes |
| Evaluation-site rank | `analysis/evaluation_site_contract.py` | contract locked; propagation open |

## Ranked failures

- **P0:** the current model stores one parameter pair per node and substep, but
  the production map evaluates the uncertain source at four distinct states.
- **P0:** no validated discrete-map JVP/Hessian/remainder encloses those four
  independent source selections.
- **P1:** Rust accelerates only the final bounds contraction; it is not a
  validated thermochemistry integrator.
- **P2:** table-knot localization exists as a contract and distance audit, not
  yet as a Taylor-map restart implementation.

## What is genuinely fixed

The previous `2`-global-parameter rank defect is fixed without dense storage.
Local rank is retained and global normalization is isolated to at most eleven
modes per evaluation site.

## What remains uncertain

The accepted endpoint family under independent evaluation-site branch controls,
including state-dependent owner and thermal feedback, has no rigorous outward
remainder yet.
