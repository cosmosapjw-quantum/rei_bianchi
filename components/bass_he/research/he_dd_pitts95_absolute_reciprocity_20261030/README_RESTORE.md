# HE_DD_PITTS95_ABSOLUTE_SOURCE_RECIPROCITY_20261030

Read `SOURCE_IDENTITY.json`, `notes/THEORY_KO.md`, `STAGE_LEDGER.json` and `results/PITTS95_SOURCE_RECIPROCITY_ATLAS.json` first. Frozen parent PR123 HEAD `df061ecb581188539fb028897adb92ee0a3700d4` must not be mutated. The original `.x4` is byte-pinned. Local Python 3.10+ stdlib only.

Run:

```
python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests
python3 src/build_pitts95.py --root .
```

Check resulting JSON+CSV byte identity (SHA in `PAYLOAD_MANIFEST.json` of full ZIP). C0621002 DA is an original absolute *capture* measured observable, while reciprocal `photo_*` data are computed **conditional** quantities at matching s, not observed photonuclear values. No full 4π angular fit/integral is asserted, no Rice numeric data substituted. The 4% scale covariance component does not certify complete angular covariance. Independent distinct-author review NOT_RUN, central 28/88 HE physical14/18, production HOLD.
