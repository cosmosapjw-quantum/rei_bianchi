# HE DD reciprocal kinematics

This is a source-locked **conditional** bridge from BASS_HE PR106, not a production event-rate provider.

```
python -m unittest discover -s tests -v
python evidence/independent_oracle.py
python evidence/verify_independent.py
python make_figures.py
```

Python3.13.5, mpmath, numpy, matplotlib are needed for all scripts; unit tests need mpmath. In a full PR106-derived checkout the default source reader reuses `research/he_sig_da_energy_compat_20261029/source/M0475.x4`; in this ZIP it uses `source/M0475.x4`. Both paths are verified against the exact same SHA256 and Git blob. See THEORY_KO.md, REPORT_KO.md, IMPLEMENTATION_CONTRACT.json and HANDOFF_NEXT_THREAD_KO.md.
