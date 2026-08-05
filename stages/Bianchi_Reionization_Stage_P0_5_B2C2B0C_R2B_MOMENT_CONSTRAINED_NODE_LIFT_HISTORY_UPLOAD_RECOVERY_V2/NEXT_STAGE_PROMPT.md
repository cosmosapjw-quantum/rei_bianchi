# Authorized next stage — R2C constrained node-chemistry relaxation audit

Execute `P0.5-B2C2B0C-R2C-MOMENT-CONSTRAINED-NODE-CHEMISTRY-RELAXATION-AUDIT` from the R2B lock.

1. Create a new durable directory, input lock, stage state, receipts, manifest, and SHA256SUMS before calculation.
2. Treat the R2B node distributions and all R2A macro/global moments as hard endpoint constraints; do not independently solve cloud abundance or derive mass from opacity.
3. Test whether the large node-level photon redistribution is dynamically reachable using finite-relaxation chemistry lanes and timestep refinement. Preserve tau=10/100/300 Myr results separately.
4. Require dt, dt/2, and dt/4 convergence of node mass/ionization/temperature/current moments before promoting any history.
5. Record projection work, KL/TV drift, active capacity sets, photon and H/He nuclei ledgers, and dual certificates at every substep.
6. Infeasible lanes must fail closed without clipping; tau=10 Myr remains an existence witness, not calibrated physics.
7. Keep G2b/G3 effective-HI and primary HeII/G3 exact zeros unless a separately authorized species-support stage changes them.
8. Do not begin unresolved subtraction, front/Q_M, source/fesc, recombination adapter/surrogate, CAMB transfer, or Bianchi feedback.
9. `rec_bianchi/main` is locked at `0d24bf7fc6b2643f0bf5fd7f693a6ebc3889958d`; any use requires a deliberate adapter/input-lock review first.

Only a convergent all-lane relaxation audit may authorize a production moment-constrained node chemistry history.
