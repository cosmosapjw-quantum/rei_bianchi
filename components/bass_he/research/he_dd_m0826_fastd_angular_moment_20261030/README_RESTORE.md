# BASS_HE PR123 | M0826 measured-shape fast-deuteron angular moment

Source-exact source-only descendant of Draft PR122 HEAD `6d105cd89bc8f47f00560ec07d6e41574bed1c38`, no parent/main mutation. Frozen IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871 M0826/M0011. Pinned masses Mαc²=3727.37941180 MeV, mdc²=1875.61294500 MeV.

Reproduce with Python >=3.10, no external Python packages required:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests
python3 src/build_fastd_angular.py --root .
```

Expected generated output: `results/M0826_FASTD_ANGULAR_MOMENT_ATLAS.json`. Original .x4 files are checked by both SHA-256 and Git blob identity before use; tampering must fail closed. JSON is deterministic per Python/runtime math behavior to the reported precision; verify scientific numeric equivalence, not byte equality across unrelated platforms unless same runtime contract. The ZIP manifest validates exact included package bytes and restore. `R_event`, `heat_rate`, `kappa`, `D_fast_pool` must remain null; no production activation.

For Rice source: the 1998 TUNL PhD PDF was located but only non-numeric scan metadata was accessible in this run; do not invent measured absolute 12 rows. Underlying original experiment's angular acceptance/bin-mean definition and energy weights remain unresolved. Unit progress 2/2 scoped, central28/88 HE14/18 physical_delta0. Independent native R6/C9 NOT_RUN.
