# C9 visual addendum

Date: 2026-10-27. Reviewer: `/root/normalization_review`.

**Decision: `PASS_PRESENTATION_SAVED_DATA_CORRESPONDENCE`. Blocking findings: 0.** This addendum closes the presentation review left pending in the earlier C9 report. The scientific decision and the source/checker review remain unchanged.

## Inspected artifacts

The reviewer viewed the actual `delivery/figures/THERMAL_ASSIMILATION_LOCAL_SOURCE.png` using `view_image`, then compared `PLOT_DATA.json` and `CAPTION_KO.md` with the preserved `implementation/attempt01/stdout.json`. No source was imported or evaluated, no FD was run, and no new image or PDF was rendered. The companion PDF was hashed for artifact identity; this addendum does not claim an independent PDF visual inspection.

| Artifact | SHA256 |
|---|---|
| Actual viewed PNG | `e9473cb8c2803ed30aca39b4d6678eaa701e79cb52079887ceed5a010b217cdc` |
| Companion PDF | `1d950f8347c04addfef2582f52d926edd34d70db13a34132315a1df20f45c2cc` |
| `PLOT_DATA.json` | `3c33d127346f0824c83e04ecc7d47375675562e606ecff3288f32b72372a9c18` |
| `CAPTION_KO.md` | `93e506a26c93af5289016f2607f06c6634511e7a2667d7cea9a4b848f25304ef` |
| Preserved numerical stdout | `3f6e942336cb18cf1422ce4736984fb5d7f7d85ca1af39aa0f126748a0c66d99` |

## Correspondence and presentation findings

All six signed power values, all eight map/step FD residuals, the frozen `2e-8` criterion and every state annotation in `PLOT_DATA.json` are exactly equal to the corresponding saved stdout fields. The source SHA in the data and caption identifies that same stdout. This is a comparison of saved values, not a numerical recomputation of the source.

The title and upper annotations identify the real cached PW19 background at z=2.479 separately from the **MANUFACTURED** fast pool. They show the constructed count and energy moments and retain the explicit **CONDITIONAL nu** annotation: it is an independent parameter that happens to equal the snapshot H numerically. The lower text limits the figure to a local source, without a trajectory or qualified physical stopping-rate claim.

The power panel labels `Photo → fast store` separately from `Fast store → bath`. The printed bath balance includes assimilation, RR/DR losses and Planck Compton; the accompanying sentence explicitly excludes direct addition of photo primary power to that bath sum. Positive and negative signs, W/m^3 units and the symmetric logarithmic axis are clear. The small nonzero DR contribution is numerically labeled instead of being presented as an exact zero.

The FD panel labels Proper, Density, Reference and eta clock in the same order as the saved `proper`, `physical`, `reference`, `eta` map keys. The legend identifies h=2e-4 and h=1e-4, the vertical axis names the maximum row-scaled JVP error, and the dashed criterion is correctly placed and labeled. Both steps use the same fixed row-unit scales, as stated in the footer. The figure makes no factor-four convergence or full-Jacobian claim.

At the actual displayed PNG size, titles, ticks, values, legends and scope annotations are readable. No clipping, material text overlap, missing sign or ambiguous source-ownership arrow was observed. No presentation repair is requested.

## Scope and cost

The unchanged numerical decision is `PASS_CONDITIONAL_NATIVE_COUPLED_LOCAL_SOURCE`. `REC-COUPLED` remains PARTIAL, original-node completion delta is 0, L4 remains false and global physical completion remains null. This visual acceptance adds no physical-provider admission.

The measured metadata phase—JSON reads, saved-value comparisons and hashes before serialization—used **0.021065780 process CPU seconds**, separately from the attempt execution and previous C9 metadata costs. The `view_image` tool's CPU and unmeasured initialization/serialization tail remain `UNKNOWN_NOT_ZERO`. These observations are preserved in `C9_VISUAL_ADDENDUM.json`.
