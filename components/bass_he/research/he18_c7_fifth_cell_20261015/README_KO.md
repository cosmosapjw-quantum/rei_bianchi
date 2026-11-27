# HE18 C7: fifth warm P01 source cell

Research unit (2026-10-15 KST): **C7 physics/source validation**, with directly needed C5 implementation and bounded C8 optimization checks. Parent BASS_HE PR60 head `e08a3695db89a817675778dcff11b801f53e904d`. Source owner `rei_bianchi a5c958c414dea41216b445c05f58df837f05cacb`.

This is public runnable code/tests only, with **no** original private HM12 emissivity file, NPZ state, or full 2904 uncertainty vector. Use a newly staged private runtime and compare exact source/parent hashes.

## Execute

```bash
BASE=/tmp/BASS_HE_HE18_C7_20261015/research/he18_c7_fifth_cell_20261015
PREVIOUS=/tmp/HE18_C6_FOURTH_OPT_20261015
NEW=/tmp/HE18_C7_FIFTH_NEW_20261015
python3 "$BASE/src/stage_fifth.py" --previous-runtime "$PREVIOUS" --output "$NEW"
python3 "$NEW/src/run_parallel.py" --runtime "$NEW"
cd "$NEW"
PYTHONPATH=src python3 src/assemble_certificate.py  # baseline
PYTHONPATH=src python3 checks/propagate_fifth.py
PYTHONPATH=src python3 checks/verify_fifth.py
PYTHONPATH=src python3 checks/vectorized_preview.py
```

To optimize assembly without overwriting the baseline, copy the staged runtime and preserve only the frozen inputs, mid/whole Jets; remove the derived certificate/result files in the new unique destination. Then run `python3 "$BASE/src/optimize_assembly.py" --runtime "$OPT"`, assemble and verify again. Reference-to-optimized comparison is in the evidence archive. Public-only unit tests:

```bash
python3 -m unittest discover -s "$BASE/checks" -p test_c7.py -v
wolframscript -file "$BASE/wolfram/lrs_redshift_xact.wl"
```

## Physics and admission

Initial-epoch global shear `b(t)=int_0^t sigma(t')dt'`, not a per-cell reset. (E(t)/E_0=a(t)^{-1}\sqrt{e^{2b}(1-\mu_0^2)+e^{-4b}\mu_0^2}). Signature (-,+,+,+), c, hbar and k_B retained, CGS internal units. Exact positive source, HM12/FT03/Verner/Case-A, fixed selected warm non-tilted axisymmetric Bianchi I. No extra CR/RCT/HH channel.

Cell five `[25000000000,31250000000]` proper seconds, total 2904 photons and 4 gas components, 784 rigorously transparent nodes. **The NumPy float64 ray preview never changes source activation or interval admission.**

Scientifically: source-scoped interval/Taylor enclosure conditional on the original mpmath.iv backend; exact Fraction Bernstein improvement retains all degree-2 controls and inherited third-derivative remainder. This is NOT formal backend verification, native binary64 end-to-end, all 16 cells, or cosmological observer/EoR abundance plots. Same-owner local Codex was not launched; existing repo worktrees outside this task were not modified.

See `REPORT_KO.md`, `DERIVATION_KO.md`, `results/PUBLIC_SUMMARY.json` and `NEXT_ACTION.json`.

## Evidence and backup

The complete source-private fifth-cell archive is in [Google Drive](https://drive.google.com/file/d/1nbC1uzqnuDUrlC4rOz6JYE4UyZc05DtA/view), and mirrored in the original private Dropbox dossier. The full Google Drive copy was actually downloaded and SHA256/ZIP-CRC matched. Archive SHA256: 9cc4894f116078d71821d25b292f0785f66ac1d2e9a8f171be5ca2d52e5ea977. Detailed IDs and validation scope: EVIDENCE_INDEX.json. No raw P01 NPZ/HM12/2904 error vector is published on GitHub.
