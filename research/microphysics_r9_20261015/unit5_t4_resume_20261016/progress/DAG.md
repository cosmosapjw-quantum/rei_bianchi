# Unit5 dependency progress

Scoped local admission: **PASS_SCOPED_LOCAL_IMPLEMENTATION**. S1 published as c2928c5d6d0e981d6a0d3b5b484237566e68fbc6 and dual-backed up. S2 final delivery resolves in DELIVERY_FINAL.json. Each R1–R10 and C1–C10 stage has its evidence/checkpoint row in STAGES_FINAL.json.

| Node | Depends on | Current status | Evidence / next action |
|---|---|---|---|
| Unit4 actual64 | historical saved inputs | REUSED; PARTIAL_WALL_LIMIT | intake/NCP_EXECUTION_RECEIPT.json |
| Resume and residual theory | frozen operator | PASS_SCOPED | spec/THEORY.md; THEORY_REVIEW.json |
| Local adapter and continuation | theory + legacy format | PASS_SCOPED | 8 tests; real64→95; complex32→64 |
| Independent implementation review | code + raw outputs | PASS_SCOPED_LOCAL_IMPLEMENTATION | review/IMPLEMENTATION_REVIEW.json |
| Backup/publication | admitted local output | S1 COMPLETE; S2 receipt resolution | progress/DELIVERY_FINAL.json |
| Actual64 checkpoint admission | actual archive + native reconstruction | NOT_RUN | exact input restoration and6charged checks |
| Actual64→128 + residual grid | admission + separate new allocation | NOT_RUN | prepared70newactions/7200s; olddeadline expired |
| Actual spectral refinement | actual64→128 outputs | HOLD | retain eta and0.001 spectrum/CDF limits |
| Full daughter continuum | refinement + T2 continuum channels | OPEN | EC,recoil/phase-space and basis closure also open |

No new physical H action or NCP execution occurred. Actual historical count is UNKNOWN [86,160]; toy bookkeeping is separately labeled. Direct residual-grid evaluation is implemented; its actual-size wall time is unmeasured.
