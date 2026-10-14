# Completed-history comparison reducer

`compare_histories.py` is read-only data reduction, not a solver. It consumes an explicit JSON manifest with `reference` and `candidate` objects. Each needs an exact saved CSV case `id`, `clock_origin="elapsed proper seconds since zbar20"`, and `{path, sha256}` descriptors for `history`, `abundances`, `config`, `source_identity`, and `terminal`. The example manifest intentionally has null identities and cannot produce physical results.

Run from the repository root:

    python3 research/axbi_goal_20261014/convergence/compare_histories.py --manifest INPUT.json --output research/axbi_goal_20261014/convergence/NEW_RESULT

Use `comparison_kind="PAIRED"` or `"REFINEMENT"`. PAIRED permits q_ref differences with other physical/numerical choices fixed. REFINEMENT permits exactly one of local_target, energy_subdivisions, or n_mu to differ. Resource/output bookkeeping may differ; configuration numbers are compared numerically, not by formatting. Raw source/config identities remain recorded, and their physical compatibility remains an independent scientific-review responsibility.

Only terminal COMPLETE_REPRESENTED_INTERVAL with actual full a=1/21→1/5 coverage, origin t=0, all accepted history rows and aligned complete H/He/electron blocks is admitted to arithmetic. Missing identities, missing files or incomplete completion return a typed JSON HOLD/UNKNOWN with null metrics and milestones. A byte mismatch is reported as a frozen-input binding signal, never automatically as scientific-integrity failure. Existing result directories are preserved.

The frozen authority convention is `scenario/FULL_PROGRESS_RESOURCE_DECISION.json:comparison_interpolation_convention`: exactly 1001 equally spaced ln(a) samples with exact native endpoints; piecewise linear interpolation between chronological accepted neighbors; no extrapolation or T sorting. Both proper clocks remain separate at matched zbar. First upward xHII=.1/.5/.9 crossings use theta linear in xHII, applied to ln(a) and t; zbar is reconstructed. Initial exact thresholds and additional distinct upward crossings are retained. Missing crossings are null/NOT_REACHED with coverage; an initially above-threshold state does not fabricate a prior crossing.

Outputs:

- `sampled_comparisons.csv`: all corresponding x, xe, Y, Tgas, proper ne, U0 and U2 differences and both clocks at the matched zbar grid.
- `comparison_summary.csv`: sampled absolute supremum, signed value/location, initial and endpoint differences.
- `milestones.csv` and `REDUCTION_RECEIPT.json`: first crossings/shifts, complete bracket records and additional crossings.

Units: x/xe/Y dimensionless, proper ne cm^-3, Tgas K, U0/U2 eV/H, elapsed proper time seconds, ln(a) dimensionless. Yi uses complete selected-model nH+4nHe; electron ye is separate from nuclear inventory. Known fraction/T/Y floors are diagnostic metadata. ne/U0/U2 floors remain null because not bound here.

For future reductions, the approved electron-floor corrigendum supersedes only the `xe` part of the frozen AX11 `comparison.near_zero_floors.ionic_fraction_and_xe` entry. Ionic fractions keep an absolute floor of `1e-7`; with case factors `h=nH/(nH+4nHe)` and `he=nHe/(nH+4nHe)`, `xe` uses `1e-7*(h+3*he)/h`. The existing `Y_electron` floor remains `1e-7*(h+3*he)`, so the two floors use consistent per-H and per-baryon normalizations. The frozen AX11 contract bytes are retained. This changes diagnostic floor metadata only; sampled values, differences, crossings, and uncertainty status do not change. The supplier patch, bounded regression, and raw outcomes are recorded in `electron_floor_001/`.

Interpolation uncertainty and evolution-refinement uncertainty remain UNKNOWN. These sampled metrics are not continuous suprema. No Richardson estimator, numerical accuracy PASS, resolved response, resolved null, upper bound or continuum claim is issued. `error_kind` in this auxiliary table explicitly says estimation has not occurred; it is not the final canonical `response_resolution.csv`. Retain D01 and D12 by running separate T0→T1 and T1→T2 (or corresponding E/A) manifests; three levels and independent interpretation remain required.

The two recorded synthetic self-tests exercise analytic linear interpolation, independent clocks, endpoint/no-extrapolation behavior, multiple/initial/not-reached crossing cases, a small completed CSV parser fixture and typed incomplete completion. They have no physical-history scope. No actual full histories have been reduced by this preparation task.
