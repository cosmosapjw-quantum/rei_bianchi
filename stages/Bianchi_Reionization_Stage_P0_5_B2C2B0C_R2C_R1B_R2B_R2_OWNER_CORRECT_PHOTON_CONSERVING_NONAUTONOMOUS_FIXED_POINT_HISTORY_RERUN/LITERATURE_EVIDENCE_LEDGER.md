# Literature and software evidence ledger

- Mellema et al., *C2-Ray: A new method for photon-conserving transport of ionizing radiation*, arXiv:astro-ph/0508416. Used for the rule that bound-free photon depletion must equal photoionizations owned by that absorption and for analytic/local relaxation motivation.
- Friedrich et al., *Radiative transfer of ionizing radiation through gas and helium*, arXiv:1201.0602. Used for the separate thermal convergence gate; temperature can impose stricter timestep constraints than ionization fractions.
- PETSc TS manual and `TSSetEventHandler`, `TSSetPostStep`, `TSSetPostEventStep`. Used only to design the next adaptive accepted-step/event policy: commit after successful steps, localize discontinuities/events, and choose conservative post-event steps for stiff dynamics.
- SUNDIALS ARKODE documentation. Independent design reference for implicit nonlinear solvers and temporal root finding.

No external source supplies numerical state, rate, history, or fitted closure to this stage.

- `rec_bianchi` PR-05C1/v0.62 (`ee54cb44838409f021d6c5fdb502450a11779ec4`), read-only semantic compatibility review. Used only for full-versus-two-half trial acceptance, immutable rejected attempts, event rollback, and exactly-once endpoint commit semantics. No numerical recombination input was imported.
