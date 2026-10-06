# Results at this finite checkpoint

Software and endpoint gates pass; numerical accuracy gate FAILS.

- 203 Rust full-suite tests, 3 additional CLI tests, and 14 Python tests pass.
- All 22 intended update files match a patch applied to an isolated reconstructed thermal base.
- 15 frozen foundation/thermal files are byte-identical; only additive library exports and the approved Verner cutoff accessor touch pre-existing code.
- The final baseline reaches z=11.5 in 232 accepted steps with zero rejects. Source births and independent analytic implementation agree to floating roundoff.
- Continuous/restarted source-emitting histories have exact terminal checkpoint parity. Malformed identities, cursors, logs, packets and ledger state reject before use. Existing output directories are never overwritten.
- The 12,560-step finest measured time refinement reaches the same endpoint and closes its own budgets. Its maximum budget-to-allowance ratios are 3.00e-5 (number) and 9.83e-5 (energy), but its worst field comparison still exceeds the target by 361.69 times (Gamma_HI).
- That Gamma discrepancy is a real total-rate error: at z=11.97453, 2.28218e-15 versus 1.67596e-15 s^-1, not solely an underflowed photon artifact.
- The energy4→8 axis still exceeds its target by 2.133 times for active energy. Birth refinement remains pulse-phase-sensitive. The birth64 exploratory reference also fails its own ledger criterion and is not an accepted reference.
- No combined refinement or larger brute-force campaign was run after the separate-axis failures. No source amplitude, physical closure or accuracy target was changed.

The source-time discretization and first-order stiff photon treatment need a new reviewed numerical method. proposal_only/ contains a possible next-method design, not an implementation. This checkpoint should be published and backed up as failed-accuracy diagnostic evidence, not promoted as a scientific baseline.
