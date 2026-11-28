# Numerical design and execution DAG

The production path uses the unchanged HE37 E2 radial evaluation and a μ prefactor. Finite mass, energy sharing, species heat and STF are algebraic contractions. I, k_B and SI units remain explicit. Signed net sources are not covariance-clipped. Underflow, overflow and absent-reactant boundaries have different statuses.

Stable outputs: use log1p in the conditional transfer mean; direct total heat; direct heavy combined heat; direct species/total STF. The cancellation-prone U2 difference is not needed to compute production heat. A positive 1D H integral is an independent reference, not a physical tail certificate.

| New workload | Dependency / target | Reuse and budget |
|---|---|---|
| Exact theory controls | Rational event/Wick and65-digit transfer-only checks | Separate author script, no old tests |
| Affected implementation controls | New mass/coordinates/heat/STF/bridge boundary | Only new affected path; old suites0 |
| Nonauthor raw quadrature | Maxwell COM+relative coordinates, original event velocities and direct Grad weights | At most30CPU s /512MiB; three selectedT and one discriminating refinement |
| New129T diagnostic | Finite-mass API versus exact saved HE37 radial rows | One new diagnostic, ≤30CPU s /512MiB |
| Sharing cost comparison | Same selected conditional sharing average, compressed versus direct positive quadrature | Small bounded repeat; accuracy and timing both reported |
| New plot | Saved HE38 diagnostic rows only | One final PNG/SVG pair with actual visual inspection |

Scientific execution can be authored/prepared in parallel; stage DAG records acceptance order and actual timestamps, not invented serial compute dates. A repeated check is allowed only for a concrete changed dependency or remaining numerical risk; every attempt is retained. A saved-evidence verifier reads hashes and receipts without launching science.
