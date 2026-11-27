# R8–R10 theory handoff to implementation

## Adopted result

The positive nominal-input comparison problem is solved by THEORY_KO.md Eqs1–8. The common scale multiplies the experimental nominal value: `model_i = A*u_i*experiment_i`. Its feasible interval, free/clipped minimax optimum, two-anchor contrast and signed-angle mapping are derived and independently reviewed. R6_REPORT.json is PASS with no blocking finding. A single bounded Wolfram evaluator returned both logical equivalences True and the exact rational/angle controls specified by the frozen contract. The nominal-input mathematical result is DERIVED and INDEPENDENTLY_CHECKED_SCOPED.

This is a reconstruction and explicit implementation of normalization/shape diagnostics on an actual newly acquired primary table. It is not a new physical theory, a statistical confidence analysis, or a full outgoing-electron event provider. Exact rational arithmetic describes the printed decimal inputs, not the accuracy of the underlying experiment or calculations.

## Exact implementation targets

- `ratio_profile`: positive paired data -> exact r_i and extrema.
- `feasible_scale_interval`: Eq2 with optional positive scale interval; `delta` in [0,1); represent an empty set explicitly.
- `minimax_profile`: Eq3–4, plus exact witness factors and residual; preserve constrained minimum >=1 when applicable.
- `pair_contrast`: Eq5–6, dimensionless ratios and conditional sensitivity bounds; common-scale cancellation.
- `source_angle_vectors`: Eq7 with the declared xz-plane convention; only source-located rows may enter this path.
- `conditional_printing_ratio_interval`: Eq8 for this positive 0.01-printed table; separate printing compatibility from physical uncertainties.
- `validate_source_rows`: preserve all 24 source values, 16 printed ratios, producer/convention metadata and exactly two located coordinates.

The scope is one 54.4 eV input with slow-electron energy5 eV. The 4-binary-height and 8-reported-feature groups are auxiliary feature comparisons. Their unknown slow angles remain null. No table extrema are fabricated as joint coordinates. Unit conversions, additional normalization factors, spin averaging, finite-mass shell values, interpolation and integrated moments are outside this contract.

## Acceptance and numerical accountability

Fraction equality against independently derived rational controls is authoritative for ratios, interval endpoints and extrema. Geometry uses binary64 trigonometry at the two declared points with absolute tolerance2e-14. The primary hand controls and R6 extra controls are in THEORY_KO.md and reviews/R6_REPORT.json; Wolfram raw controls are in evidence/wolfram/R7_RAW.json. Do not import the kernel as the test oracle. The source paper's approximate printed summary is descriptive and must not become an equality gate.

The frozen fresh allocation is CPU8 s / wall30 s for three planned children and at most one diagnosed repair. Prior unit allowances, failures and UNKNOWN_NOT_ZERO remain nontransferable. B1 actual dual-provider backup precedes any new scientific script execution. Root must review actual raw outcomes and separate C9 before admission/publication. No unchanged previous suite is replayed.

## Actual next transition

R6 PASS + R7 PASS -> lower-tier implementation/preparation -> B1 ACK -> bounded tests/source analysis/figure -> independent C9 -> root result decision and S/C publication -> B2 -> D/E -> B3 actual tail receipt. Until these outputs exist, their execution/publication/backup states remain PENDING. LOOP_PROGRESS.json records these axes separately.

The next physical input after this scoped unit is still HE-ANG-SOURCE-PAYLOAD: a source-consistent full joint outgoing-electron law or amplitude/event payload with count, spin, exchange, support, frame and recoil contracts. The completed sparse points can serve as located source controls for that future input. Source acquisition should first follow explicit numeric data links in the literature; no renewed global provider sweep or old CCC/Hex solve is authorized by this handoff alone.
