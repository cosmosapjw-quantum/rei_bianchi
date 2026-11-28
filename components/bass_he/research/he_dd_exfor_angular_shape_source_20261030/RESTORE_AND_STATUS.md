# BASS_HE source-only angular shape research recovery

Parent PR119 frozen HEAD `62b925b739656f01131e152ace05624d0f102850`. New PR number/HEAD: read the LIVE remote; package is immutable standalone snapshot before closeout receipt.

Inputs: original Arends EXFOR M0475.x4 3349B SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`. No external Fermi gamma field needed to reproduce this physical angular-shape science.

Run after ZIP extraction from package root:

```bash
PYTHONDONTWRITEBYTECODE=1 python src/experimental_shape_atlas.py --root .
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
python -m compileall -q src tests
```

Expected: source reported 12 DA input, 30 exact dimensionless measured-point contrasts, nine conditional WLS fits; source ERR-S Cartesian boxes are not confidence intervals. `results/` JSON and two CSVs are deterministically reproducible at matched numpy/scipy/Python environment. Git SHA and full binary ZIP readback tracked in Git DELIVERY_RECEIPT after upload.

DAG original Central 28/88 HE physical 14/18 and PR119 angular 2/3 unchanged, new source-scoped science 2/2, physical_delta0, production HOLD. Distinct-author native R6/C9 NOT_RUN. No nuclear event rate or heat rate obtained.
