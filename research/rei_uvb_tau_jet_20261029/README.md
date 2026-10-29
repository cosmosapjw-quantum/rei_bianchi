# REI UVB local tau-jet invariant (2026-10-29)

This additive research unit proves and implements a **conditional local output-jet determinant** using the exact parent PR262 saved source coefficients. It does NOT integrate an IVP or compute physical optical depth.

Clean stacked PR262 checkout:

```bash
python -B research/rei_uvb_tau_jet_20261029/code/jet.py > /tmp/rei_tau_jet_result.json
python -B -m unittest discover -s research/rei_uvb_tau_jet_20261029/tests -p 'test_jet.py' -v
g++ -std=c++20 -O2 -Wall -Wextra -Werror -pedantic research/rei_uvb_tau_jet_20261029/code/jet_reference.cpp -o /tmp/rei_tau_jet_cpp
/tmp/rei_tau_jet_cpp research/rei_uvb_tau_jet_20261029/results/CPP_INPUT.tsv
```

Dependencies: Python standard library, mpmath 1.3.0 for one independent high-precision test; g++ C++20. The code prefers parent `research/rei_uvb_saved_state_source_tangent_20261029/results/RESULT.json` and falls back to bundled `source/PR262_RESULT_LOCKED.json`; both require exact SHA256.

Scientific equations and assumptions: `THEORY_KO.md`; numbers and scopes: `REPORT_KO.md`; machine contract: `CONTRACT.json`; next DAG: `NEXT_DAG_OVERLAY.json`; staged checkpoint: `STAGE_LEDGER.json`.
