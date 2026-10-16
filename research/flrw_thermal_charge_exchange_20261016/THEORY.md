# Isolated thermal charge exchange

## R1 — Research question and scope

Construct the isolated fixed-proper-volume evolution of D0 + H+ ↔ D+ + H0 with the existing Savin2002 rate coefficients evaluated at the evolving common temperature. A single signed extent must own density changes, binding-energy change and thermal-energy change. Completion requires a concrete bounded scalar algorithm, an independently checkable temperature-dependent manufactured solution, and new small verification fixtures.

This unit starts from canonical commit `eb2abcac4f44b7bc4ff532286953fcb4e353c7bb`. The existing exact frozen-coefficient map in `deuterium_charge_exchange.rs`, blob `dd0a8c9b96ef3e53b8eef0fd08961045779f20b7`, is reused. The existing isotope-native point RHS and frozen wrapper in `deuterium_atomic.rs`, blob `8477162430af02585a32d18092454e1f7bb52f60`, are also reused as source-level evidence. Evolving temperature inside the kinetic flow is the new contribution.

The actual completed SOURCE011 three-stage diagnostic supersedes the historical missing-packet plan. Its tiny sampled Newton corrections do not supply whole-history error or cause attribution. PR166 owns its positive signed-MD14 reference and source-age convergence diagnosis. This unit is independent of those active supplier tasks and writes only its new directory.

The intended physical scope is isolated CX in fixed proper volume, with ideal monatomic common-temperature EOS and conserved particle count. Expansion, photoionization, recombination, electron ionization, source transport and full isotope evolution remain separate. Neither native production files nor existing rates, domains or defaults are changed.

The theory author performs source intake and mathematical construction. The assigned coding agent performs only the frozen bounded implementation and tests. A separate reviewer decides scoped mathematical/numerical acceptance. Actual stage artifacts are captured before advancing. No numerical computation or scientific code was executed for R1.

