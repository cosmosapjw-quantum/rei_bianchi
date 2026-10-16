# V11 C6: local sandbox test evidence

- Command: `python -m pytest -q tests/test_ci_thermal_clock.py`
- Python `3.13.5`; NumPy `2.3.5`, SciPy `1.17.0`, pytest `9.0.2`.
- Actual status: 41/41 PASS. `evidence/C6_PYTEST.log`.
- Includes all 96 Grackle C literal rows and 17 rate/cooling coefficients, max observed relative difference `2.8410045294244635e-14` (independent Python literal port).
- Exact native SHA256 frozen checks: `igm_rates.rs=310164e620617f3089d488bd1f9668996b4a4cbd191383e45303def176ef81cf`, `igm_thermal.rs=30515d96270ec73a37829ba298513a42112991168479d3cb40f33b67fd469ab2`, `igm_state.rs=1651b00a517d67aaa71b38d3c69af6413570adfc38b591a3ed25284f039e0ae0`.
- Tests: source-domain CI floor/DR gate, metastable HeI CE n_e squared, CMB sign, EOS, positive nuclear simplex, process-wise thermal/chemical/escape/CMB ledger, independent Radau, source-off native N128 endpoint parity, observed BE/mixed clock order ~1 and all-midpoint order ~2.
- No Rust executable/native source-on NCP job was run by this stage. Tests are sandbox Python only.
