# REI_BASS_LI6_ELECTRON_LIFT_20261029

Source-locked **BASS-internal** Li6/Li7 electronically equivalent isotope lift (21→17) with full electron-feedback Jacobian correction. Standalone proofs use synthetic rational electronic rates in the exact structure extracted from the original BASS 21-state `AtomicNetwork.evaluate`. No native rate calibration, cross-repository physical model promotion, IVP, tau history, or CMB observable.

- `THEORY_KO.md`: derivation, source owner/units, counterexamples, limitations.
- `source/`: exactly byte-locked original JSON / Python donor and REI seven saved reference rows.
- `code/lift.py`: exact Fraction source-structure oracle; `code/make_reference.py`: seven counterfactual input rows; `code/reference.cpp`: C++20 standalone reconstruction.
- `tests/test_lift.py`: 30 targeted scientific/execution tests.
- `results/`: source-only output, test logs, C++ input/output and symbolic checks.
- `CONTRACT.json`, `SOURCE_PROVENANCE.json`, `STAGE_LEDGER.json`, `NEXT_DAG_OVERLAY.json`: claims and counters.
- `HANDOFF_NEXT_THREAD_KO.md`: reproducible continuation.

From a clean extract in an environment with Python≥3.11, SymPy and a C++20 compiler:

```bash
bash VERIFY.sh
```

The script uses **no network access and solves no IVP**. It does not run the BASS owner `AtomicNetwork` against actual empirical coefficient files because those were not part of this specific pinned PR234 source archive. Expected output `30 tests`, `CPP_PASS rows=7`; these are target-scoped rather than full production/CI acceptance.

Original REI DAG: working33/88, central28/88, physical delta0. `F4=PARTIAL`, `L4_ready=false`, `NO_MORE_IVPs=true`, independent different-author R6/C9 NOT_RUN. The original pilot inventory mismatch from PR265 remains.
