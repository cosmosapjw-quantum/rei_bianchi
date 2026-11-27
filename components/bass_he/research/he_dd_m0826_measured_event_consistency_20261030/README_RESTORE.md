# BASS_HE M0826 measured event consistency: reproducible restore

Parent BASS_HE PR121 immutable HEAD `ea1e7968636aae6200c26a0377159736d009cee0`. This is new physical **source-derived** consistency evidence, not a measured new σ, not a rate. Standalone inputs are source-exact EXFOR M0011 and M0826 only. Cross-comparison is conditional on equal-width energy averaging, angular bin averaging and event-counted 1/2! interpretation.

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests
python3 src/build_m0826_event_consistency.py --root .
```

After running, check `results/M0826_MEASURED_EVENT_CONSISTENCY.json` and `results/M0826_SOURCE_DA_EVENT_CONTRIBUTIONS.csv` against the manifest. Original EXFOR source `SHA256` and Git blob are checked by code on every run; corrupted source fails closed. No numpy/scipy dependency. Python >=3.10.

Full source-inclusive ZIP has `PAYLOAD_MANIFEST.json`. No native R6/C9, no full repo tests or IVPs. Preserve `production=HOLD`, `R_event=null`, `kappa=null`, `heat_rate=null`.
