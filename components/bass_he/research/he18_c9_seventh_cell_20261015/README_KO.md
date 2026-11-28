# BASS_HE HE18 C9: Seventh warm P01 saved-cell implementation

2026-10-15 KST. Original finite-source parent BASS_HE PR62 at SHA 490ac4a980b582d983f15975dc813ef5457efa02, with source authority rei_bianchi a5c958c414dea41216b445c05f58df837f05cacb. The current live rei_bianchi PR117 branch is separate and was read only.

This public directory includes executable code, tests, exact kinematic checks, a public scientific summary and resume contract. Source-private P01_STATE.npz, HM12 emissivity, and all 2904 raw photon uncertainty entries are never pushed to GitHub.

## Reproduce on the authorized Ubuntu workstation

Must begin with the complete, hash-pinned sixth-cell PRIVATE runtime. Stage to a UNIQUE destination. Stage refuses overwrites. In a shell:

    ROOT=/tmp/BASS_HE_HE18_C9_20261015/research/he18_c9_seventh_cell_20261015
    PREV=/tmp/HE18_C8_SIXTH_CACHED_20261015
    NEW=/tmp/HE18_C9_UNIQUE_20261015
    python3 "$ROOT/src/stage_seventh.py" --previous-runtime "$PREV" --output "$NEW"
    python3 "$NEW/src/run_parallel.py" --runtime "$NEW"
    python3 "$ROOT/src/prepare_long_fraction.py" --runtime "$NEW"
    python3 "$ROOT/src/optimize_memoized_residuals.py" --runtime "$NEW"
    cd "$NEW"
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=src python3 src/assemble_certificate.py
    python3 checks/propagate_seventh.py
    PYTHONPATH=src python3 checks/verify_seventh.py
    PYTHONPATH=src python3 checks/vectorized_preview.py

Optional source-matched assembly benchmark: stage another unique seventh runtime from the same preceding sixth source and run the same two midpoint/whole passes, but apply prepare_long_fraction.py only, NOT optimize_memoized_residuals.py. Source inputs and the two actual Jet arrays must match byte-identically for a fair comparison. Use unique results, no output overwrite.

Public-only checks:

    cd "$ROOT"
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s checks -p test_c9.py -v
    wolframscript -file wolfram/lrs_redshift_xact.wl
    wolframscript -file wolfram/seventh_global_clock.wl

## Physics / outcome

Time t=[37500000000,43750000000]s measured from original epoch, no local-time shear reset. LRS Bianchi-I non-tilted warm FT03/HM12 Case-A with 3 CI, 3 RR, 2 DR, Verner photoabsorptions. Signature (-,+,+,+), physical photon energy E=hbar omega, explicit c,hbar,k_B and original source's CGS conventions. Four gas states, 2904 photon rays, 784 rigorously transparent cross-section nodes. NumPy float64 preview is DIAGNOSTIC ONLY.

The exact residual bound memoization caches duplicate rational Taylor inputs but does not identify rays, drop physical source modes, alter positivity, relax intervals or omit outgoing photon errors. The Python digit-cap adjustment is for trusted, byte-pinned exact-rational output only, not model precision. Conditional status: SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES. Native binary64/provider roundoff, independent formal mpmath.iv verification, whole 16-cell history, real EoR species histories and observer foreground remain open.

See THEORY_AND_EXECUTION_KO.md, results/PUBLIC_SUMMARY.json and NEXT_ACTION.json. Full private evidence is backed up separately with SHA/CRC manifest and provider verification.

## Durable source-private evidence

Full 85-member evidence archive SHA256: a5f3d5dfa10d5679481cd137aa5933ced18a6312a78df70487a6aa13078c65bb. It is stored in the established private Dropbox folder under the filename BASS_HE_HE18_C9_SEVENTH_MEMOIZED_EVIDENCE_20261015_v1.zip. Actual independent Dropbox server download matched original SHA256 and CRC. Google Drive upload could not be verified: drive.googleapis.com returned RATE_LIMIT_EXCEEDED on a diagnosed known-folder-ID retry. Do not claim dual-backup completion. A future create-only retry must first check whether the original stalled attempt created an object. See EVIDENCE_INDEX.json for confirmed versus pending provider state. The private ZIP is not republished publicly.
