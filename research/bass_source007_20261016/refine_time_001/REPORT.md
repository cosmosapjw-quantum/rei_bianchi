# Source007 fixed-step time sensitivity diagnostic

Execution/invariant status: PASS_SCOPED_FIXED_STEP_SENSITIVITY_EXECUTION. Four new bounded native runs exited0; coarse h=1e-4 four-step results were reused unchanged. The approved binary/source identities matched all four launches and native checkpoint envelopes. No source, build, test or coarse rerun occurred.

Both backgrounds have SAME_NOMINAL_INTERVAL_ACTUAL_ENDPOINT_DIFFERENCES. Nominal h×steps=0.0004; actual endpoint a bits are3fa864055ae91ef6 (coarse),3fa864055ae91ef7 (middle),3fa864055ae91efa (fine). No interpolation, state projection or nearest-state operation was used. These raw differences are not same-endpoint convergence evidence.

| Background | T(h) K | T(h/2) K | T(h/4) K | abs delta1 K | abs delta2 K | R | p=log2(R), diagnostic only |
|---|---:|---:|---:|---:|---:|---:|---:|
| COLD_FLRW | 8.69922201847 | 8.69921779638 | 8.69921131932 | 4.22209146e-06 | 6.47706099e-06 | 0.651852973 | -0.617381497 |
| SIGNED_MINUS | 8.69919161606 | 8.69918739403 | 8.69918091713 | 4.22202719e-06 | 6.47690014e-06 | 0.651859238 | -0.617367631 |

Temperature differences increase in both cases. Across102 recorded/missing comparison rows: {"DECREASE": 64, "STAGNATION": 13, "INCREASE": 21, "NOT_RECORDED": 4}. These counts describe raw differences, with no method-order threshold or accuracy floor. Three rows have opposite signed differences; nineteen have at least one exact zero delta. R/p are null where a denominator/log is undefined, with reasons retained. No near-cancellation tolerance was introduced.

comparison.csv/COMPARISON.json contain Tgas, all five fractions, actual five ionic Yi plus electron Ye, photon N/U, photo-event and source/absorption/escape/work/energy ledger values, time, b, H and signed s/H. Endpoint CSVs are headerless; the explicit current compiled schemas preserve row0. Absorbed energy and escaped number are not recorded in the native schema and remain null.

Main plus resumed extra RHS calls: {"COLD_FLRW_h2": [104, 52], "SIGNED_MINUS_h2": [104, 52], "COLD_FLRW_h4": [118, 56], "SIGNED_MINUS_h4": [112, 56]}. New component wall 0.29052651301026344s of240s. Original three compile/test invocations20.121775138075463s and coarse component0.130703988019377s are preserved; no campaign epoch reset.

Independent result review is pending. Full time/angular/history/Bianchi admission remains HOLD; scientific admission is NOT_ISSUED. GL4/GL8 quadrature differences were not emitted, so no error bound is inferred.
