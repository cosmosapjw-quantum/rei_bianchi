# BASS_HE PR121 real inverse DD experimental source package

Immutable parent BASS_HE Draft PR120 HEAD `83596b913a08dd31496b7abbb7d5a9972fff5cc1`. New Draft PR121: https://github.com/cosmosapjw-quantum/BASS_HE/pull/121. 

This archive contains **original source-owned experimental data** from IAEA EXFOR (4 byte-locked original files; C0122 29 source rows and A1256 12 new source rows), `M0011/M0826` existing lower-energy forward donors, working Python parsing and physical invariant-s energy map, 41 measured-record JSON+CSV, derived exact-energy crosswalk, and 20-stage Git evidence. Nested original parent PR120 ZIP is included with exact SHA identity. The accessible scanned Rice PhD original full numeric tables were **not acquired** and are not claimed.

Reproduce from clean extracted archive root:

```
python src/build_inverse_dd_atlas.py --root .
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

Expected targeted tests: **19/19 PASS**. All four original source SHA256/Git blob locks are checked. The physical claim is **41 original experimental record rows**, not an absolute unpolarized photonuclear cross section, no production event rate, and no heat.

Output files:

- `results/INVERSE_DD_EXFOR_REAL_MEASUREMENTS_41.json`
- `results/INVERSE_DD_EXFOR_REAL_MEASUREMENTS_41.csv`
- `results/SOURCE_ENERGY_CROSSWALK.json`

Check `PAYLOAD_MANIFEST.json` against each non-manifest file. `STAGE_LEDGER.json` has 20 actual distinct stage Git commits, with per-stage Central28/88, HE14/18, new source 0/2→1/2→2/2 statuses. Google Drive binary ZIP readback may be verified independently; Dropbox Paper text is not binary backup.

Strict science gates: Central28/88, HE14/18, PR114 lowE3/4, PR119 Angular2/3, PR120 Shape2/2, NEW_INVERSE_SOURCE2/2 scoped; physical_delta0; `kappa=null`, `R_event=null`, `heat_rate=null`, `L4=false`, `production=HOLD`. Distinct-author R6/C9 NOT_RUN. No auto next node, no merge, no force push.
