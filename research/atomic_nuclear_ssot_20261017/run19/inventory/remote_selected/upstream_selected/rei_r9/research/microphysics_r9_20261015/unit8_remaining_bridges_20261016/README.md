# R9 Unit8 — recovered lightweight atomic/nuclear bridges

Start with [REPORT_KO.md](REPORT_KO.md), [progress/DAG.md](progress/DAG.md), and the final independent decision in `review/IMPLEMENTATION_REVIEW.json`. Historical execution JSON may still say review pending; the dated independent review owns final admission.

This unit contains original theory, implementation, actual saved numerical outputs and exact portable inputs for:

* A: six atomic photoionization/Milne/total-RR channels and early Li charge bookkeeping. Original and balanced BDF comparison failures are preserved; independent BDF validation remains HOLD.
* B: finite-curve LiH nuclear levels/E1 emission and complete public ExoMol CLT LTE line sums.
* C: actual Be7-source weighted first Klein–Nishina scattering.
* C2: positive photon redistribution through16 cold-electron collisions, with kinetic-energy and waiting-time diagnostics.
* D: pinned native PRIMAT C64-sample propagated prior, joint nuclear covariance and dossier-prescribed conditional17+excluded-baryon projection.

The all59-isotope original donor is inventoried in `intake/DOSSIER_NUCLIDE_AUDIT.md`. D's eight-isotope small-network covariance is a distinct model. Do not silently normalize the17 retained entries, collapseBe7 intoLi7, or use the conditional bare-charge lift as a solved atomic history.

`figures/UNIT8_RESULTS.png` summarizes saved B/C2/D results. Photon-to-electron kinetic transfer is not a deposited-heat calculation. The figure's rounded correlations and all64-sample standard deviations retain finite-sampling limitations.

## Layout and reproducibility

- `spec/`: formulas, constants, assumptions, scopes, limits and minimal repair amendments.
- `code/`, `tests/`: actual source and focused tests.
- `inputs/`: exact copied provider/donor files. B's compact curve table was extracted from verified original electronic NPZ records; those large original CI arrays are not copied here.
- `inputs/laneD/primat_source_4bf97d5082ee.tar.gz`: all517 pinned public source/data/license files. The native runner restores this automatically when an explicit provider root is absent, and checks the manifest. No user-side manual provider download is needed.
- `results/`, `evidence/`: saved actual arrays/tables/logs, including failures and raw MC samples.
- `review/`: scoped independent decisions.
- `progress/`: twenty-step stage mapping, programme DAG and delivery receipts.

Python3/NumPy/SciPy are needed for analysis; D's source uses GCC and GNU make. The original no-repeat execution receipt is intentionally retained: inspecting or analysing existing results does not authorize another budgeted scientific campaign. A fresh replication should use an explicitly new task/output allocation and retain these immutable results.

Useful read-only commands from this directory include:

```sh
python -m unittest discover -s tests/laneB
python -m unittest discover -s tests/laneC
python -m unittest discover -s tests/laneC2
python -m unittest discover -s tests/laneD
```

Test modules' own receipts document what was actually executed. The commands above are reproduction guidance, not a claim of another invocation in this delivery.

The public portable archive contains `progress/MANIFEST_PORTABLE.json`, which hashes exactly its payload members (excluding the manifest itself). The private full backup additionally contains the separate full `progress/MANIFEST_S2.json`; its intake snapshot inventory is not the public package inventory.

No NCP calculation, production activation, main merge, or external-job restart is part of Unit8. Original external campaign deadlines remain unchanged. Refer to `progress/NEXT_ACTIONS_KO.md` for precise remaining inputs and the read-only NCP recovery task.
