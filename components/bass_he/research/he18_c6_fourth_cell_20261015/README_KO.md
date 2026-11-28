# HE18 C6: warm P01 fourth saved-cell scientific implementation

Selected work: C5 implementation with affected C6 tests and C8 measured optimization. Parent BASS_HE PR59 head `9a4a554bfffd5aea81dbf0ea018f092f55e3efa9`. Production-rate owner stays rei_bianchi `a5c958c414dea41216b445c05f58df837f05cacb`.

This public folder has no private NPZ/HM12 table or raw photon error vectors. All private data stay in uniquely staged runtimes and the separately backed-up evidence archive.

## Reproduction on authorized local Ubuntu

Prerequisites: NumPy and mpmath.iv, actual **immutable** C5 private runtime staged according to PR59, Wolfram/xAct optional for tensor checks. Use a NEW destination; staging refuses to overwrite existing results.

```bash
BASE=/tmp/BASS_HE_HE18_C6_20261015/research/he18_c6_fourth_cell_20261015
OLD=/tmp/HE18_C5_THIRD_REAL_20261015
NEW=/tmp/HE18_C6_FOURTH_UNIQUE_20261015
python3 "$BASE/src/stage_fourth.py" --previous-runtime "$OLD" --output "$NEW"
python3 "$BASE/src/optimize_sparse.py" --runtime "$NEW"
cp "$BASE/src/run_parallel.py" "$NEW/src/run_parallel.py"
python3 "$NEW/src/run_parallel.py" --runtime "$NEW"
cd "$NEW"
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=src python3 src/assemble_certificate.py
PYTHONPATH=src python3 checks/propagate_fourth.py
PYTHONPATH=src python3 checks/verify_fourth.py
cp "$BASE/checks/vectorized_preview.py" "$NEW/checks/"
PYTHONPATH=src python3 checks/vectorized_preview.py
```

Compare the optimized runtime against a separate unmodified C5-derived fourth-cell runtime using

```bash
python3 "$BASE/checks/compare_optimization.py" --baseline /path/to/baseline \
 --optimized "$NEW" --output /path/to/new/OPTIMIZATION_COMPARISON.json
python3 -m unittest discover -s "$BASE/checks" -p test_c6.py -v
wolframscript -file "$BASE/wolfram/lrs_redshift_xact.wl"
```

## Source and physics invariants

Signature (-,+,+,+), explicit c, ℏ and k_B. Non-tilted LRS Bianchi I warm P01 FT03/HM12 Case-A selected source, no CR/RCT/HH. Proper time fourth cell [18,750,000,000;25,000,000,000] seconds from ORIGINAL epoch. The ray redshift derives from `R=sqrt(exp(2b)(1-mu0²)+exp(-4b)mu0²)/a` with `b(t)=∫s(t)dt`, `a=V^(1/3)`. Initial-epoch integration must not be silently reset each cell.

All 2904 photon residuals are evaluated, 784 source nodes are rigorously transparent. Sparse skip activates only if all opacity Jet coefficient intervals are exactly [0,0] and never uses the float64 vector preview. Positive comparison resolvent uses the complete 4-gas+2904 incoming errors.

Physical values and benchmark results are in REPORT_KO.md, machine-readable numbers in results/PUBLIC_SUMMARY.json. Conditional numerical status only: interval backend independently verified? NO; binary64 native provider roundoff certificate? NO; 16-cell history? NO; observer foreground / IGM abundance history? NO.

## Evidence and independent restore

The original P01/HM12 private bundle and execution logs are kept in the [verified Google Drive evidence archive](https://drive.google.com/file/d/1AkD3E9YvIo_WwxAA8K6waFdwfm_qc4LM/view), with a second immutable copy in the original private Dropbox dossier. Archive SHA256: `d3176ee4e503894e04a1b8a6019fd907b0a9b68735c90e7d5bfd5559b57b132e`. Google Drive restored bytes, CRC and archive SHA256 match. The full evidence identity and exact storage locations are in `EVIDENCE_INDEX.json`.
