# Independent D9 review — PASS_SCOPED_D9

The frozen identity, changed code, actual numerical diagnostics, raw/compact mapping, figures, README and NCP wrapper pass this one bounded complementary review. No current blocker remains.

All 175 cases and 153 epochs satisfy the pre-fixed sampled-data residual gate; maximum normalized residual is 1.473444875767401e-6 against 2e-5. The four existing D8 brackets retain their endpoint signs, with largest local |R|/|Q|=2.022140048467199e-5 against 0.1. Independent algebra from actual stored arrays exactly reproduced M, Q, reconstructed Q, residual, scales and endpoint tables. Three representative original raw files matched both their byte hashes and every corresponding compact array value. No ODE, momentum recomputation, or new quadrature was executed by this reviewer.

Two concrete findings were repaired within this pass: the source-free unit test now uses nonconstant M and its targeted test passes; the diagnostic legend no longer covers the largest residual values and the repaired figure was visually read back. The actual other two PNGs were also inspected. The compact reader representative numerical comparison is exact for all 13 diagnostics; the production run was not repeated.

The focus endpoint budgets explain the sign split: radiation contributes about -0.003305 to -0.003308 against initial +0.003; only the +0.0003 initial matter case supplies enough positive accumulated matter contribution (+0.00037222) to leave Q positive (+0.00006456) at z=2. The nominal zero initial matter case develops I_m=-0.000003614709, so zero initial matter stress must not be described as zero matter contribution throughout. These are trajectory-specific budgets on coupled solutions.

Final source hash, compact identities, reviewed artifact hashes, closed findings and precise scope are recorded in FINAL_REVIEW.json. Publication, provider preservation and central status integration remain controller-owned. This result does not grant production admission or strengthen AGE/Grackle claims. No additional audit cycle is indicated.

## Narrow portability repair closeout

The controller identified a further concrete current-task portability defect: the original NCP wrapper called `python`, while actual `intake_remote/PR215_NCP.json` records that command failing with exit 127 and recovery using `/usr/bin/python3`. The wrapper now defaults to `python3`, accepts a quoted single-executable `D9_PYTHON` override, and checks interpreter existence before execution. The README documents this without treating PR215 as a D9 run. Read-only review of these changed surfaces and actual targeted receipts confirmed bash syntax exit 0, Python 3 help exit 0, and missing interpreter exit 69. The finding is closed within the same review pass; no scientific gate reopened and no numerical validation repeated. Updated wrapper and README hashes are in FINAL_REVIEW.json. PASS_SCOPED_D9 remains unchanged.
