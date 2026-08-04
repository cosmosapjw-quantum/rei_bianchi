# D0 and PR roadmap

The adopted target remains D0 with roughly 10--12 PRs. PR 2 has expanded internally because multiple fail-closed physics gates were discovered.

| PR | Scope | Current state |
|---|---|---|
| PR 1 | B2C1C primary He III decay | science artifact complete |
| PR 2 | B2C2 absorption, hierarchical sink/chemistry, front/QM | in progress; current R2A macro distribution blocker |
| PR 3 | B2D source ensemble and Q/Gamma closure | pending |
| PR 4 | B2E homogeneous FLRW/FlexRT end-to-end and interface freeze | pending |
| PR 5 | C0 Bianchi I/V/II geometry coupling | pending |
| PR 6 | C1A finite tilt/electron frame/multifluid exchange | pending |
| PR 7 | C1B all 11 Bianchi types and exceptional VI_-1/9 | pending |
| PR 8 | C2 CMB Thomson/kinetic coupling | pending |
| PR 9 | C3 anisotropic LoS and CAMB-level observables | pending |
| PR 10 | D0 all-type verification | pending |
| PR 11 | external recombination adapter/splice | waits for rec_bianchi |
| PR 12 | equation compendium/release, if separated | optional |

## PR 2 internal order

```text
B2C2A-R1 opacity reconciliation        PASS
B2C2B0A hierarchical two-scale closure PASS with caveats
B2C2B0B diffuse-only history            FAIL-CLOSED
B2C2B0C reduced global sink DAE         reduced PASS / requested scope FAIL
B2C2B0C-R1 node-resolved lift           FAIL-CLOSED
B2C2B0C-R2A macro moment distribution   NEXT
B2C2B0C-R2B moment-constrained history  pending
B2C2B unresolved sink closure           blocked
B2C2C front/QM/full ledger               blocked
```
