# BASS_HE HE_SIG_DA_ENERGY_COMPAT_20261029

Source-pinned conditional mathematical DA/SIG compatibility analysis for 4He(gamma,d)d. NOT a physical cross-section normalization, measured 330 MeV SIG, or production reaction rate.

Python 3.13.5 reference environment; `requirements.txt` pins optional numerical and plotting packages.

```bash
cd BASS_HE_SIG_DA_BRIDGE_20261029
python -m unittest discover -s tests -v
python evidence/independent_lp.py
python evidence/independent_angular.py
python make_figures.py
python evidence/build_results.py
```

Authoritative parent: BASS_HE PR105 HEAD `88a85c859744a0930b1cb776b4d9e8fa0794976d`. Exact EXFOR raw source SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`.

Read `THEORY_KO.md`, `REPORT_KO.md`, `IMPLEMENTATION_CONTRACT.json`, `RESULTS.json`, `STAGE_LEDGER.json`, `EXTENSION_DAG.json` and `HANDOFF_NEXT_THREAD_KO.md`.

Claim gate: central 28/88, HE 14/18, predecessor conditional 2/2, new scoped 1/2. R6/C9 distinct independent reviewer NOT_RUN. R_event=null, activation=false, L4=false, production=HOLD.
