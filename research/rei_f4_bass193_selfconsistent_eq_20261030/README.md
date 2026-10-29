# BASS21 self-consistent algebraic equilibrium from 193 archived real model epochs

Restore original source archive nested under `source/PR276_IMMUTABLE_FULL.zip` without editing bytes. This research module is an independent *post-processor* of the original 193 snapshots. To verify: `bash VERIFY.sh` (no new IVP). To reproduce the data in place from exact archived original trajectory and native BASS rates, explicitly run `OPENBLAS_NUM_THREADS=1 python code/quasi_eq.py` and then the tests. `source/BASS_ATOMIC_NETWORK.py` is byte-identical to the BASS source. The loader shim in `code/native_full_rate.py` is explicit and only replaces a manifest-read operation with numerically verified frozen coefficients, not reaction equations.

See THEORY_KO.md for uniqueness proof and REPORT_KO.md for scientific interpretation. Canonical REI 33/88, central 28/88, fast 4/7 unchanged; no new IVP, no actual REI 300 K chemistry replacement or physical tau claims. Distinct-author R6/C9 not performed.
