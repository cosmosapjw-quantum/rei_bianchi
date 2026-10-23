# Observed execution results — ANGTHERM01

This file reports numerical observations. Scientific admission is pending the independent Astra decision. No new atomic accuracy or self-consistent reionization history is inferred.

## Completed finite work

Ten prescribed/owner-authorized cases completed. The source backgrounds and atomic input bytes are preserved. One interrupted nominal attempt was resumed from the persisted eta=0.3720455828589731 endpoint; the first failed attempt had 365 in-memory attempted nodes, 363 persisted. Only its two unpersisted terminal nodes were recomputed. No persisted interval was replayed. The full oracle was integrated once to ln7; later zero-face guard and JSON serialization repairs regenerated summaries only. No numerical state was clipped, projected or renormalized.

## State dimensions and observed costs

These are one-run observations with different tolerances and native state/error norms: nominal primary rtol2e-9, full direct rtol2e-10, tight M4/M8/M16 rtol2e-11. Component atols are listed verbatim in each case JSON. These costs do not establish fixed-tolerance or equal-error speedup. Case times include raw saving and summaries; whole-child import/setup/orchestration costs are recorded separately in the budget.

| Case | States | rtol | Case CPU [s] | Case wall [s] | Solver wall [s] | Accepted nodes |
|---|---:|---:|---:|---:|---:|---:|
| grid044_M4_nominal | 41 | 2.0e-09 | 6.717560 | 6.730494 | 6.142540 | 639 |
| grid022_M4_nominal | 41 | 2.0e-09 | 3.774080 | 3.801111 | 3.622843 | 476 |
| grid044_M4_tight | 41 | 2.0e-11 | 12.562236 | 12.609585 | 12.080673 | 1782 |
| grid044_M4_oracle | 221 | 2.0e-10 | 46.322443 | 46.456853 | 45.448681 | 1073 |
| grid044_M4_reverse | 41 | 2.0e-09 | 6.763442 | 6.785091 | 6.243296 | 642 |
| grid044_M4_zeroUV | 41 | 2.0e-09 | 3.914913 | 3.921884 | 2.570463 | 209 |
| grid044_M4_ionized | 41 | 2.0e-09 | 19.610231 | 19.631540 | 18.827955 | 1097 |
| grid044_M8_tight | 65 | 2.0e-11 | 18.151175 | 18.259027 | 15.635657 | 2030 |
| grid044_M16_tight | 113 | 2.0e-11 | 26.378726 | 26.566215 | 22.243171 | 2410 |
| grid044_M4_mean_tight | 41 | 2.0e-11 | 5.887058 | 5.890213 | 5.762378 | 1422 |

## Matched reporting-time agreement

Both comparisons use the same 201 eta values.

| Observable | Nominal − full maximum | Nominal − tight maximum | Limit |
|---|---:|---:|---:|
| fractions | 8.16731266e-11 | 8.00320088e-11 | 2.0e-07 |
| atomic_scaled | 8.167316823e-11 | 8.00320088e-11 | 2.0e-07 |
| temperature_K | 1.86959986e-09 | 1.737152861e-09 | 2.0e-06 |
| electron_per_Href | 4.563763256e-11 | 4.905201245e-11 | 2.0e-07 |
| photon_per_Href | 3.885780586e-16 | 0 | 2.0e-08 |
| UV_energy | 1.776356839e-14 | 0 | 2.0e-06 |
| Q | 3.314685562e-16 | 0 | 2.0e-06 |
| U | 3.381982472e-10 | 3.362924383e-10 | 2.0e-06 |
| Eesc | 6.841647249e-10 | 7.428219151e-10 | 2.0e-06 |
| Wgas | 3.006164206e-10 | 2.960454104e-10 | 2.0e-06 |
| Wmean | 1.296485141e-11 | 1.138017458e-11 | 2.0e-06 |
| Wshear | 8.937194301e-12 | 9.040918621e-12 | 2.0e-06 |
| tauT | 8.682186914e-12 | 8.436640275e-12 | 2.0e-07 |

Temperature errors in this table are relative; other errors use the absolute units declared in THEORY.md. Both comparisons pass all frozen numerical agreement limits.

## Conservation and numerical state observations

| Case | Max normalized energy residual | Max charge residual | Max photon residual | Max nucleus-block residual |
|---|---:|---:|---:|---:|
| grid044_M4_nominal | 5.5709063e-12 | 4.8647874e-16 | 9.8440842e-13 | 1.7763568e-15 |
| grid022_M4_nominal | 4.9290781e-12 | 1.7104528e-15 | 9.8276072e-13 | 1.5246593e-15 |
| grid044_M4_tight | 2.4981713e-13 | 2.317255e-15 | 1.8783765e-13 | 1.8634725e-15 |
| grid044_M4_oracle | 7.0048911e-13 | 1.4018669e-15 | 5.4923289e-16 | 2.1684043e-15 |
| grid044_M4_reverse | 6.6505794e-12 | 1.4018669e-15 | 9.8514073e-13 | 1.1858461e-15 |
| grid044_M4_zeroUV | 7.7638878e-16 | 8.1312927e-16 | 0 | 6.2038546e-16 |
| grid044_M4_ionized | 2.539543e-11 | 1.1445156e-15 | 3.1761595e-11 | 2.0328791e-15 |
| grid044_M8_tight | 2.7484577e-13 | 1.8935304e-15 | 2.4129632e-13 | 2.3665827e-15 |
| grid044_M16_tight | 3.5133956e-13 | 4.6972642e-15 | 3.0354271e-13 | 2.8460307e-15 |
| grid044_M4_mean_tight | 2.1415132e-13 | 3.7818761e-15 | 1.8802073e-13 | 2.220446e-15 |

Energy normalization is the absolute fixed initial total energy (5.677836979412036 eV/Href for default data; 28.616383188369145 eV/Href for the ionized control). Count normalization is max(initial UV count, initial electron count), using their actual per-Href values; each nonzero isotope uses its own fixed initial total. Exact zero inventories use an absolute scaled diagnostic rather than division by zero.

Primary lifts preserve exact n/T zeros. The full numerical oracle retained its raw neutron roundoff: maximum accepted scaled magnitude1.7899843162408834e-30, below the owner-set64epsilon bound1.4210854715202004e-14; T remains exactly zero. Full direct photons have an observed reporting minimum−2.159477009891523e-21 per Href. These states are preserved, and no strict numerical positivity theorem is claimed.

## Accepted and reporting temperature ranges

| Case | Accepted min/max [K] | Reporting min/max [K] |
|---|---:|---:|
| grid044_M4_nominal | 216.5903681 / 9921.176996 | 216.5903681 / 9745.859681 |
| grid022_M4_nominal | 216.6214499 / 9921.234501 | 216.6214499 / 9746.260114 |
| grid044_M4_tight | 216.5903681 / 9921.177818 | 216.5903681 / 9745.859681 |
| grid044_M4_oracle | 216.5903681 / 9921.177442 | 216.5903681 / 9745.859681 |
| grid044_M4_reverse | 216.5903681 / 9921.176996 | 216.5903681 / 9745.859681 |
| grid044_M4_zeroUV | 6.12245771 / 300 | 6.12245771 / 300 |
| grid044_M4_ionized | 404.6770671 / 13803.0397 | 404.6770671 / 13758.22784 |
| grid044_M8_tight | 216.5903681 / 9921.177828 | 216.5903681 / 9745.859681 |
| grid044_M16_tight | 216.5903681 / 9921.177826 | 216.5903681 / 9745.859681 |
| grid044_M4_mean_tight | 216.5903681 / 9921.177818 | 216.5903681 / 9745.859681 |

All accepted and reported temperatures lie in the inherited3..1e9K fit domain. The complete observed range is6.122457710232248..13803.039704945777K.

## Same-background directional versus mean-redshift control

The two cases use exactly the same grid044 H/nHref, default IC, M4 quadrature, rtol2e-11 and component atols. The control sets only the existing b,bprime geometry multiplier to0. It is a prescribed counterfactual, not a physical FLRW solution. Differences below are directional minus mean.

| Observable | Max absolute difference | Endpoint signed difference | Directional endpoint | Mean endpoint |
|---|---:|---:|---:|---:|
| temperature_K | 8.435836207e-08 | 4.925453823e-09 | 216.5903681 | 216.5903681 |
| electron_per_Href | 2.411357225e-11 | 1.023196805e-11 | 0.07044183809 | 0.07044183808 |
| UV_energy | 0.004655881289 | 0.002629418385 | 0.07405798953 | 0.07142857114 |
| Q | 0.04030696901 | -0.01610782452 | -0.01610782452 | -1.040834086e-17 |
| Wmean | 0.006523994185 | 0.006523994185 | 0.4351021985 | 0.4285782043 |
| Wshear | 0.00915341273 | -0.00915341273 | -0.00915341273 | 0 |
| tauT | 1.100852048e-12 | 1.094953989e-12 | 0.02907054098 | 0.02907054098 |

Maximum T relative difference is4.981474451980455e-11. Interpretation of whether a small thermochemical difference is resolved belongs to the independent numerical/physical review. The saved stress and work differences are shown separately from those small thermal differences.

## Angular refinement

| Observable | M4−M8 max absolute | M8−M16 max absolute | log2 successive-difference ratio |
|---|---:|---:|---:|
| temperature_K | 3.417198968e-08 | 3.771606316e-08 | -0.1423648 |
| electron_per_Href | 1.325883847e-12 | 1.084576873e-12 | 0.2898221 |
| photon_per_Href | 5.005024173e-14 | 2.319672232e-14 | 1.109456 |
| UV_energy | 5.317292903e-07 | 4.617196903e-11 | 13.49139 |
| Q | 9.029666633e-06 | 1.489284196e-09 | 12.56584 |
| Wshear | 1.065865518e-06 | 8.375442527e-11 | 13.6355 |
| tauT | 2.237966756e-13 | 1.952500661e-13 | 0.1968656 |

This logarithmic ratio is not a demonstrated asymptotic order. T, electron and Thomson differences are at numerical noise level and do not resolve an angular convergence order. The finite M4 quotient/oracle claim and the angular-continuum question remain distinct.

## Resources and stopping boundary

Frozen pre-Li-reporting conservative child ledger CPU: 217.943352000s /300s; wall: 230.352828152s /420s. This includes the preflight hard-cap charge20CPU/30wall, the saved-array inspection charge1CPU/2wall, all five main process launches (one summary-only), and three raw-result plotting passes. No optional timing repetition was used.

All raw histories, failures, logs, accepted nodes and support-boundary metadata remain available. Science execution has stopped. The controller and fresh Astra reviewer own the admission decision.

## Species-resolved native fractions: lithium signal and qualification

The small common-temperature and total-electron differences do not bound changes in a trace species. The inherited total Li abundance is5.0001e-10/Href. Its native electronic fractions show a much larger directional-threshold signal, even though their contribution to the total electron count is correspondingly small. These values use existing201-point report-grid arrays only; no model or IVP was rerun.

| Comparison | H max fraction difference | He max fraction difference | Li max fraction difference |
|---|---:|---:|---:|
| directional_M4_minus_mean_M4 | 6.279851639e-12 | 4.589158914e-13 | 0.04899986856 |
| directional_M16_minus_mean_M4 | 6.209602277e-12 | 4.551706234e-13 | 0.04912182803 |
| angular_M4_minus_M8 | 1.314504061e-12 | 1.359953816e-13 | 9.977434663e-05 |
| angular_M8_minus_M16 | 1.075195488e-12 | 1.132427485e-13 | 4.641599593e-05 |

For M4 directional versus matched mean, the largest Li difference is0.0489998685596 at eta=0.729716305896, stateLiI: directional fraction0.00156001484114, mean fraction0.0505598834007. The final LiI fractions are0.325605980229 and0.358702778516. M16 directional versus the same mean control has maximum Li difference0.0491218280304.

The M4→M8 and M8→M16 maximum Li fraction differences are approximately9.97743e-5 and4.64160e-5. These do **not** establish angular convergence at the2e-7 finite-oracle representation-agreement tolerance. The successful M4 reduced/full comparison is an equivalence check within the same finite angular discretization; it is not a Li angular-continuum accuracy certificate.

Figure07_lithium_threshold.png separates the finite LiI directional-versus-mean signal from the angular-refinement error. Its actual M16 LiI5.392eV crossing span for the10eV cohort is eta0.4568282378842937..0.7279924649929239; the M4 span is0.4889140699867012..0.7267243875735505. The matched mean crossing is approximately0.617668719. These spans come from already saved per-case source-crossing records, not from rounding report-grid times.

## Final saved-data reporting costs

Species analysis used one saved-array-only command (observed command wall0.340638s; conservatively charged1CPU/2wall because CPU was not separately measured). The authorized single Li figure plus its overlap-only repair used measured whole-child CPU5.835404s and wall5.999889s, below its CPU20/wall30 allowance. No additional IVPs or timing experiments were run. Final conservative accounting is CPU224.778756000s /300 and wall238.352717220s /420.
