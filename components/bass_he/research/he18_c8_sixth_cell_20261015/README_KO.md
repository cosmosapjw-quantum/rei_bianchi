# BASS_HE HE18 C8: Sixth warm P01 source cell

2026-10-15 KST. Parent BASS_HE PR61 head b3a56b360f3d913002dd63f8097b1457cf170e6a. Exact finite-source authority is the archived rei_bianchi revision a5c958c414dea41216b445c05f58df837f05cacb, NOT necessarily the currently developing repo head.

This public folder holds real executable source, tested optimized exact rational assembly, tests, Wolfram/xAct verification source and condensed outputs. The original non-public P01 NPZ, HM12 emissivity and all 2904 raw photon uncertainty entries must remain in the separate evidence ZIP, not in public Git.

## Execute in an isolated location on authorized Ubuntu

Prerequisites: already verified private C7 fifth-cell runtime with original P01 model and full 2904 incoming errors; Python3.12, NumPy, mpmath.iv. The target must not exist because staging refuses overwrites.

    ROOT=/tmp/BASS_HE_HE18_C8_20261015/research/he18_c8_sixth_cell_20261015
    OLD=/tmp/HE18_C7_FIFTH_BERNSTEIN_20261015
    NEW=/tmp/HE18_C8_NEW_UNIQUE_20261015

    python3 "$ROOT/src/stage_sixth.py" --previous-runtime "$OLD" --output "$NEW"
    python3 "$NEW/src/run_parallel.py" --runtime "$NEW"
    cd "$NEW"
    PYTHONPATH=src python3 src/assemble_certificate.py
    python3 checks/propagate_sixth.py
    PYTHONPATH=src python3 checks/verify_sixth.py
    PYTHONPATH=src python3 checks/vectorized_preview.py

To benchmark exact rational optimization, preserve an identical frozen input and mid/whole source-jet runtime in a new unique directory, remove only its *derived* previous CERTIFICATE.json and RESIDUAL_COUPLING.json, then:

    python3 "$ROOT/src/optimize_cached_bernstein.py" --runtime "$OPT"
    cd "$OPT"
    PYTHONPATH=src python3 src/assemble_certificate.py
    PYTHONPATH=src python3 checks/panel_refinement.py --runtime "$OPT"

Regression and actual algebraic tensor verification:

    cd "$ROOT"
    python3 -m unittest discover -s checks -p test_c8.py -v
    wolframscript -file wolfram/lrs_redshift_xact.wl

## Scientific scope

Sixth proper-time interval [31250000000,37500000000] seconds. Warm non-tilted axisymmetric/LRS Bianchi-I HM12/FT03 Case-A, CI3 RR3 DR2 and Verner photoabsorption with retained photon threshold branches. Original-epoch Hubble volume/shear integral, signature (-,+,+,+), explicit c, hbar, k_B. Photon p=(E/c)(u+e), E=hbar omega. Global time is t/h=5+z on this cell, not reset to zero.

The cache only holds shared *exact Fraction* Bernstein panel weights. It cannot change absorption branches or the source; all 2904 positive photon intervals and outgoing uncertainty radii remain. An auxiliary NumPy float64 ray preview is diagnostic only, NEVER a gate for skipping physics. The source's original emission/opacity inputs, physical chemistry model and accepted 16-panel Taylor remainder stay unchanged.

Claim: SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES. No external formal mpmath.iv backend review, native binary64/provider-roundoff proof, global 16-cell numerical result, full physical EoR ion histories, or observer/foreground certification is asserted.

Read THEORY_AND_EXECUTION_KO.md, results/PUBLIC_SUMMARY.json and NEXT_ACTION.json for actual results and open actions. Full original source-private evidence and publication receipt are linked separately.

## Durable evidence and independent restoration

The complete source-private 70-member evidence ZIP is [on Google Drive](https://drive.google.com/file/d/1Ug798JnVUxHZ07oNQ2dV28GnilYV26Zo/view) and in the established private Dropbox dossier, SHA256 0fe0022574f467a7a81f1ccbbdd42a0446f3d13f06c7f1df03208091c23fc089. The Drive version was actually downloaded and matched the original bytes and ZIP CRC. See EVIDENCE_INDEX.json for provider IDs, source identity and evidence limitations. This new receipt was written after the evidence ZIP was frozen and is not a member of the earlier evidence archive.
