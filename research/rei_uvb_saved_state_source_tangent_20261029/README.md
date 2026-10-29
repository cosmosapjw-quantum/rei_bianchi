# REI saved17 photo-source tangent

Add-only scoped science after REI PR261. Read `THEORY_KO.md`, `REPORT_KO.md`, `CONTRACT.json` and `HANDOFF_NEXT_THREAD_KO.md`.

Clean checkout at PR261 parent HEAD contains `research/rei_uvb_six_moment_response_20261029/code/source_response.py` and pinned source JSON. Run only new target tests:

```bash
python -B -m unittest discover -s research/rei_uvb_saved_state_source_tangent_20261029/tests -p 'test_*.py' -v
python -B research/rei_uvb_saved_state_source_tangent_20261029/code/source17.py
python -B research/rei_uvb_saved_state_source_tangent_20261029/code/crosscheck_cpp.py
```

C++20 compiler required only for the optional independent-algorithm crosscheck. No new IVP, native solver, network fetch, or previous GLS campaign. The seven saved rows are an exact numerical projection of a public source CSV, not a raw-byte copy. All derived results are frozen-state counterfactual source evaluations. Do not confuse them with a calibrated trajectory, physical tau, or full BASS chemical6.
