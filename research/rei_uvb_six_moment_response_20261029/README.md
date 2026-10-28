# REI UVB six-moment source response (2026-10-29)

An isolated, source-locked conditional H/He rate response after PR260. **Not a physical Bianchi optical-depth response**. Requires Python3, NumPy and mpmath for the high-precision clock regression.

```bash
python -B code/run_once.py
python -B -m unittest discover -s tests -v
```

Frozen source SHA256 `13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b`; Puchwein 13-row projection SHA256 `dcd13144072584085f49698e40c9822e074fecc2a6046605dc9d67cfe7cc3eff`. P19 original 59-row Git blob `218d81f68447da438228a7b102e1cec96a8e8a1a`. No rate extrapolation beyond observation calibration z=2.4..4.75. The original 59-row source file is not copied or claimed byte-identical to the projection.

See `THEORY_KO.md`, `REPORT_KO.md`, `RESOURCE_AND_CLAIM_GATE.json`, `HANDOFF_NEXT_THREAD_KO.md` and `delivery/STAGE_ARCHIVE_MANIFEST.json`. Stage capsules are **closeout-reconstructed** per-stage recoverable snapshots, not historical snapshots captured during original execution. Original DAG 33/88 working, 28/88 central, delta0; unit 18/20 with distinct-author R6/C9 pending. No IVP, new plot or original campaign replay.
