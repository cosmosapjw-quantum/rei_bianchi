# BASS193 × CCC6/Kim92 first-event competing hazard, 2026-10-31

One source-conditional exploratory physical unit; no cosmological IVP, no source-owner edit.

Input SHA-locked files: original BASS193 192 source arrival, 192 BASS H/He compositions and thermal clock rows, 193 original BASS21 electron feedback state rows, and 6 CCC adaptive channel data from PR311/EXHALE.

Run:

```
python code/competing_first.py
python code/plot_science.py
python -m unittest discover -s tests -v
python code/verify_manifest.py
```

All emitted numbers are source-conditioned on the explicitly conditional maximum Li II singlet 2E1 source, not source-owner production. The full physical explanation and provenance are in SCIENTIFIC_REPORT_KO.md.

Input baseline frozen PR #311 HEAD `63052797e382b438ef375e8389f539118a7e2a0c`. Parallel read-only PR #310 HEAD `6a9343f49da8287616c338de5f853bb1a0b44b5d`, PR #309 `701add5f6536d091350650f2b6649cded0c0de06`.

Do not merge, force-push, replace native BASS/REI source owners, or promote F4/L4 from this record alone.
