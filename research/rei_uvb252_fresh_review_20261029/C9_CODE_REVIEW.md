# C9: PR252 reproduction gate and separate QR code audit (2026-10-29)

## Exact objects reviewed
- PR252 at `eecd9b2c1c95f9319c1da41951b814855b0feb11`: `CONTRACT.json`, BB13/CALIBRATION frozen inputs, `src/tilt_gls.py`, `src/reference_decimal.py`, `src/suite.py`, `tests/test_tilt.py`, result/delivery/handoff.
- PR254 at `2a1c163e3bddef9706e133117b35a1fb5750f4aa`: corrected `src/suite.py`, `src/run_bounded.py`, review/REPRO_ENTRYPOINT_SCOPED_20261029.md.
- PR255 EOS verifier `63c8659670e159ce4a76db243a65fed25286da82` (does not close author-independent R6/C9); PR253 remains EOS owner.

## Blocking source replay defect, already repaired in a sibling
Original PR252 `suite.py` indexes absent `spec['acceptance']['rtol']` and `['atol']` while actual frozen `CONTRACT.json` uses `tolerance.relative/absolute/variance_abs`. Both original suite and wrapper write into an untracked `results/` directory without ensuring it exists. On a clean checkout these are **reproducibility failures**, not a mathematical or astrophysical contradiction. PR254 changes only the tolerance lookups and result directory creation; **do not duplicate, overwrite, or silently merge** its code. PR254's 2/2 schema/filesystem probes did not perform a whole postpatch run.

## Independently executed new code tests (not owner campaign)
An independent, producer-free QR-whitened Python reference `review_gls.py` and targeted `test_review_gls.py` were run in a conversation-owned sandbox with SciPy; **11 PASS, 0 FAIL**, exit 0, actual whole command wall 2.16 seconds, child user CPU 1.95 and system CPU 0.20 seconds, MaxRSS 140668 KiB. Controls included: source grid/C symmetry/SPD; QR vs saved beta/kappa/Cov/Q; normal-equation residual; nested Wald identity; signed EOS and Jeans endpoints; correct 7x7 permutation; detect wrong diagonal substitution; isotropic scalar redshift table gives zero sky dipole. No original 24-test campaign, original Decimal80 evaluator, physics IVP or old multi-provider source was rerun. Input values manually transcribed from GitHub, so the review checks semantic numerical identity, not byte-perfect source restoration.

One saved-review-only plot (not a physical rate solve), `COORDINATE_SENSITIVITY.png/.pdf`, command wall 1.45 seconds, user CPU 1.32, system CPU 0.13 seconds. Opened and visually checked; all axis labels legible, no overlap. The formal box is *not a confidence interval*. One new Wolfram evaluator call returned four exact symbolic zeros (no reliable remote CPU log).

## Decision and next executable action
`C9=HOLD_POSTREPAIR_CLEAN_CHECKOUT_AND_DISTINCT_REVIEWER`. It is wrong to claim `20/20` now: the original PR252 authority ledger remains `18/20`, original R6/C9 need author-independent admission. This supplemental packet establishes a useful mathematical and numerical cross-check and pinpoints the actual remaining code-path step, but **cannot substitute for running PR254's corrected existing entrypoint in a clean checkout**. No native subagent was exposed in this turn and no full original suite postpatch receipt is available.

Required positive transition:
1. Confirm original PR252 exact inputs and PR254 current head, owner checkout cleanliness and new bounded CPU/wall allocation; do not borrow closed main/review budgets.
2. From PR254 head run **once** `python src/run_bounded.py --once` with actual source/input identity, preserving stdout/stderr/exit/CPU/wall and verifying old 24/24 tests + 13 reference checks.
3. Obtain one distinct-author reviewer of the resulting patched code and raw output; then promote only the fixed statistical-model scope. Do not merge automatically or claim physical Bianchi global tilt, L4, full error radii, or new provider activation.

Canonical DAG **28/88**, other draft owner working **33/88**, H-Li auxiliary nine excluded. Physical F4 PARTIAL, production held, new IVPs zero.

Reviewer code, tests, numerical JSON, raw command logs and figure are preserved in the separately downloadable conversation ZIP and can be run without the owner model; GitHub source publication is restricted to this review summary until exact code transport is available.
