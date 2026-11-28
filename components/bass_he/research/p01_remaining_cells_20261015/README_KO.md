# BASS_HE warm P01, saved cells 8–16

Completed locally on 2026-10-15 KST. Frozen original warm HM12/FT03 Case-A source is rei_bianchi commit a5c958c414dea41216b445c05f58df837f05cacb; inherited BASS_HE seven-cell evidence is PR63 commit a3eeff91eb9d0c2ba42d553cfda7eab7ecbc53ef.

The actual local campaign executed cells 8 through 16, using existing certified 1 through 7 results. All nine new cells completed and independently passed 11 scientific checks each. Final conditional source-scoped Thomson optical depth at t=1e11 seconds:

tau_16 in [1.27998310917642936032734511983425822491e-7,
           1.27998310917643067537790506329945423459e-7].

This is a FINITE selected warm-source trajectory, not the physical cosmological H/He reionization ionic-abundance history.

## Reproduce

Prerequisites: complete, already verified PRIVATE seven-cell C9 P01 source runtime, NumPy/mpmath.iv, and the original confidential NPZ/HM12 source. Never overwrite previous source evidence.

CODE=research/p01_remaining_cells_20261015
ORIGINAL=/tmp/HE18_C9_SEVENTH_MEMOIZED_20261015
NEW=/tmp/A_UNIQUE_REPLAY_ROOT

PYTHONDONTWRITEBYTECODE=1 python3 "$CODE/src/run_remaining.py" --from-cell 8 --through 16 --parent-runtime "$ORIGINAL" --root "$NEW"

python3 "$CODE/src/verify_campaign.py" --previous-seven "$ORIGINAL" --campaign "$NEW" --until 16 --output "$NEW/CHAIN_VALIDATION.json"

python3 "$CODE/src/summarize_cells.py" --campaign "$NEW" --through 16 --output /tmp/A_UNIQUE_PUBLIC_OUTPUT

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "$CODE/tests" -p test_continuation.py -v

The plotter also needs the original first-to-sixth legacy runtimes to reconstruct the first six source points, and the original C9 predecessor. The more limited independent chain verifier needs only the seven-cell C9 runtime and newly executed cells.

## Protected scientific assumptions

Non-tilted LRS Bianchi I, signature (-,+,+,+), keep c, hbar, k_B, original epoch integrated shear and photon energy redshift. HM12/FT03 3CI 3RR 2DR, Verner photoabsorption, Case-A escape, unchanged CGS source units. Two original saved source RHS evaluations per new slab, NO full source ODE re-integration.

Every slab computes 2904 photon modes and four gas error variables. Two scientific processes run midpoint and whole-cell interval/Taylor evaluations with BLAS thread caps. Exact Fraction assembly retains the 16-subpanel positive Bernstein upper bounds and safe memoization of mathematically identical residual inputs only. Neither photon source nor its error component is skipped. Validation enforces original immutable source/hash, physical proper clock, nonnegative 2904 output radii and full positive gas comparison inverse. The runner stops on a failed gate, without claiming the failing cell complete.

Public reports, plots, CSVs and source code are here; private per-ray errors, source NPZ, emissivity, midpoint/whole coefficient arrays, exact certificates and logs are in the create-only private evidence archive. See RESULT_KO.md, results/RESULT_STATUS.json and NEXT_ACTION.json.

Claim level: SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES. NOT a full physical reionization abundance history, independent proof of mpmath.iv, native binary64 roundoff, observer/foreground result, or external independent review. Separate live rei_bianchi PR117/118 retains its own ownership and was not modified. Standalone Codex was not invoked.
