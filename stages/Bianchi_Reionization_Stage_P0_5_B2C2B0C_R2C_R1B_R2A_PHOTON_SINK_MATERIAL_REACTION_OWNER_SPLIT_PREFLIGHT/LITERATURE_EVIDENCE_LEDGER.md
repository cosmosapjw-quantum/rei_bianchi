# Literature and external-code evidence ledger

| Evidence | Load-bearing use | Boundary |
|---|---|---|
| Mellema et al., *C2-Ray: A new method for photon-conserving transport of ionizing radiation*, arXiv:astro-ph/0508416 | Photon depletion must equal the photoionizations owned by that absorption channel; analytic relaxation motivates a later owner-correct fixed point | Does not justify mapping unresolved sink absorption to resolved atoms |
| Friedrich et al., H/He multifrequency C2-Ray extension, arXiv:1201.0602 | H/He owner separation and separate thermal convergence gate | Does not provide this project's node partition or sink law |
| Verner et al., *Atomic Data for Astrophysics II*, arXiv:astro-ph/9601009 | Inherited H/He photoionization cross-section moments | Absolute group opacity remains inherited from B2C2A-R1 |
| PETSc 3.25 TS documentation | Next-stage fully implicit ODE/DAE and event-handling design | No PETSc production integration occurs in R2A |
| `rec_bianchi` PR-05B2/v0.60 and PR-05B3 handoff | XOR ownership, transaction-safe accepted history, event-localized switches, no removal before complete replacement | Read-only semantics only; no recombination state, rate, or history is imported |
