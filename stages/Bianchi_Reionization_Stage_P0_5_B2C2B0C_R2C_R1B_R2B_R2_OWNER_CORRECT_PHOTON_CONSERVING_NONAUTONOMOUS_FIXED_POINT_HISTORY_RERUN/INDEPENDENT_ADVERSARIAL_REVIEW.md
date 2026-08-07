# Independent adversarial review

## Load-bearing objections tested

1. **Physical no-go masquerading as solver failure.** Rejected. An interval/256 internal microstep reaches the same hard `1e-10` residual gate, so at least a local positive fixed point exists at smaller step.
2. **Positivity or nuclei loss hidden by clipping.** Rejected. The four nominal failures retain positive species, H/He residuals below `8e-16`, and `clipping_used=false`.
3. **Thermal failure hidden inside a generic residual.** Rejected. The positive scalar backward-Euler root closes; no nominal failure is classified `THERMAL_CONE`.
4. **Small-measure tail waived by averaging.** Rejected. Weighted tail metrics are recorded only as auditors; the hard maximum residual remains the acceptance gate.
5. **Post-hoc lane choice.** Rejected. No production lane is selected because no production history is accepted.
6. **Overclaim from the dt/256 witness.** Rejected. The witness authorizes only an adaptive-microstep policy stage, not production chemistry or a full history.

## Remaining risks

- Convergence is solver- and globalization-dependent; Picard failure does not rank Newton-Krylov, Anderson or fully coupled DAE alternatives.
- The interval/256 witness does not identify an optimal or globally safe minimum step.
- Later slabs may expose new material, thermal, boundary/storage or subgrid-exchange blockers.
- The fixed maximum-node gate is stringent but deliberately retained because low-weight nodes remain physical states.
