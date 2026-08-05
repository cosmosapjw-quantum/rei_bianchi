# Scientific and numerical contract

- Metric signature: `(-,+,+,+)`; `epsilon_123=+1`.
- `c`, `hbar`, and `k_B` remain explicit. Rate outputs use `Myr^-1`; source terms retain `s^-1 cMpc^-3` or `erg s^-1 cMpc^-3`.
- Extensive variables: `M [H cMpc^-3]`, `I [H cMpc^-3]`, `U [erg cMpc^-3]`, `C,J_g [s^-1 cMpc^-3]`.
- Positive cone: `M>=0`, `0<=I<=M`, `U>=0`, `C>=0`, `J_g>=0`, `sum_g J_g<=C`, plus inherited macro mass/volume caps.
- Endpoint macro/group/global moments are exact hard constraints. No inter-macro transport, opacity-to-mass inversion, or clipping is permitted.
- Relative cone/KKT tolerance: `1e-11`; endpoint-moment tolerance: `2e-11`; exact-zero tolerance: exact floating zero and symbolic identity.
- Analytic trajectory certification uses endpoint/equilibrium checks plus a prelocked dyadic interval enclosure with maximum depth 24; unresolved intervals fail closed.
- Refinement levels: `2,4,8`; monotone error reduction and observed order at least `0.5`, unless all errors are below `1e-14`.
