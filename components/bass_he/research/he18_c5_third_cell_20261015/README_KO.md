# HE18 C5: third warm P01 saved cell

This public directory contains runnable code and tests, but no private NPZ/HM12 photon inputs. Source scope: non-tilted LRS Bianchi I, warm FT03/HM12 Case A, selected source commit a5c958c414dea41216b445c05f58df837f05cacb. Signature (-,+,+,+). Keep c, hbar, k_B and original source CGS conventions. No CR/RCT/HH channels added.

## Run from the verified previous C3 private runtime

    BASE=/tmp/BASS_HE_HE18_C5_20261015/research/he18_c5_third_cell_20261015
    OLD=/tmp/HE18_C3_RUN_20261015
    NEW=/tmp/HE18_C5_THIRD_REAL_20261015
    python3 "$BASE/src/stage_third_cell.py" --previous-runtime "$OLD" --output "$NEW"
    cd "$NEW"
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=src python3 src/run_evaluations.py mid
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=src python3 src/run_evaluations.py whole
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=src python3 src/assemble_certificate.py
    python3 checks/propagate_third.py
    PYTHONPATH=src python3 checks/verify_third.py

Staging enforces exact C3 result/hash identity and rejects an existing destination. The input path must have the private C3 source/reference and its two-cell certificate. Without that predecessor, first reproduce C3 using its published stage_inputs/README and the original three immutable archives.

Public synthetic regressions:

    cd "$BASE"
    python3 -m unittest discover -s checks -p test_c5.py -v

## Actual 2026-10-15 KST result

Proper cell [12500000000,18750000000] seconds; two endpoint RHS calls to freeze the same archived reference, no new source ODE. Midpoint and whole-cell interval/Taylor passes each evaluated all 2904 photon nodes. 784 exactly transparent nodes. Assembly, full componentwise incoming/output radius and 11 source-scoped exact-rational conditions passed.

Third tau interval [7.99991270416755664757,7.99991270416755953851]e-9.
Three-cell tau [2.39997480791313923367,2.39997480791313977182]e-8.
Three-cell first collision probability [2.39997477911374407097,2.39997477911374460912]e-8.
Third column radius 21728.2654846 m^-2, gain 0.002305074646923<1, original global gas box usage 0.116714947555<1.

This is conditional on existing 70-digit mpmath.iv interval primitives and the pinned exact-real finite source; not native binary64/provider-roundoff verification, all 16 cells, full reionization history, or observer foreground. No simultaneous rei_bianchi Codex worktree was touched.

## Evidence and backup

[Private full evidence archive on Google Drive](https://drive.google.com/file/d/1r0syRJdeYsoudtLhAHVGX8un_XnxyqlT/view), also saved under the established Dropbox private dossier folder. Read `EVIDENCE_INDEX.json` for immutable SHA256, matching sizes and tested Drive restore. Original private source inputs are not tracked in this Git branch.
