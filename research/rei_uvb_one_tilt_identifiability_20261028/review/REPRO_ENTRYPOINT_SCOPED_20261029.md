# PR252 reproducibility entrypoint repair (scoped, provisional)

Base PR252 HEAD: eecd9b2c1c95f9319c1da41951b814855b0feb11 (branch research/rei-uvb-one-tilt-20261028). Frozen source is immutable.

## Reproduced source-contract mismatch

At this exact Git tree, `CONTRACT.json` exposes `tolerance.relative=1e-10`, `tolerance.absolute=1e-12`, and `tolerance.variance_abs=1e-15`. The tracked `src/suite.py` reads absent `spec['acceptance']['rtol']` and `['atol']`. Execution from the published Git tree therefore raises KeyError before the GLS fit. The frozen Git tree also lacks a tracked `results/` directory, while both the suite and runner write files there without creating it. This prevents clean-checkout replay.

## Minimal changes

Only replace the two obsolete tolerance references with the existing frozen tolerance keys, replace the hard-coded variance tolerance with the same frozen `variance_abs`, and create the output directory before writing in suite and runner. Inputs, `tilt_gls.py`, `reference_decimal.py`, design, data, original R/C ledger, source ZIP, numbers and numerical tolerances are unchanged.

Local standalone two-probe check: old schema lookup raises KeyError; uncreated results path raises FileNotFoundError; mapped keys and created path behave as intended (2/2, 0 failures; this is NOT full PR252 Python test execution). Native PR252 24/24 and Decimal80 checks are historical and have NOT been replayed for this patch. Independent distinct-author R6/C9 remain NOT_RUN, status stays 18/20. No physical F4, L4, 28/88 DAG or astrophysical tilt claim changes.

Supplementary mathematical robustness: retaining BB13 EOS slope-response vector with `d(theta)=d+theta*v` and fixed correlated statistical C yields conditional `kappa(theta)=0.06866173948059069-0.009302630273776256 theta` (dex/redshift), so `theta in [-1,1]` maps to [0.059359109206814406,0.07796436975436696]. This is an analytic sensitivity, NOT a refit with a systematic covariance and NOT a physical significance claim. Raw field arrays were used through the previous semantic input copy, not new source byte retrieval.

## Gates

- No mutation of the source PR252 owner branch: stacked isolated branch/draft PR only.
- No additional IVP, rate generation or existing scientific campaign.
- Git publication is actual; dual Drive/Dropbox backup of this NEW patch is NOT VERIFIED (immutable PR252 S0/S1 archives remain preserved).
- Gate for scientific admission: different-author review of exact new diff and original raw records, and bounded full source-tree replay after fixing the reproduction path.
