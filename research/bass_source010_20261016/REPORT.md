# Source010 bounded controller-target and environment sensitivity

Status: BOUNDED_DIAGNOSTIC_EXECUTION_COMPLETE_INDEPENDENT_REVIEW_PENDING

source009 baseline LOCAL vs source010 NCP; exact ELF/source, CPU/libm/runtime floating environment not proved bitidentical; controller-target plus environment sensitivity, no exclusive causal/timeerrorattribution.

Same source009 ELF and compiled source were used, without builds or baseline reruns. The only physical config change was local_target 1e-5 → 5e-6. Operational caps used corrected supported output_budget_mib=2048 (1920 MiB science plus128 MiB reserve), native880 s/external900 s, 90k accepted/300k starts/3M RHS. Initial unsupported1024/992/32 values were superseded before staging.

| Case | Native status | Accepted | Starts | RHS | z end | Wall s |
|---|---|---:|---:|---:|---:|---:|
| COLD_FLRW | NATIVE_COMPLETE_PENDING_REVIEW | 39580 | 118806 | 831672 | 19.8 | 852.0436366869835 |
| SIGNED_MINUS | NATIVE_COMPLETE_PENDING_REVIEW | 39624 | 118935 | 832569 | 19.8 | 872.0777580699942 |

Native saved tables/counts/ledgers and terminal source/config/table/case/mode/epoch/sixarray/bodyhash bindings were validated once. Baseline checks were reused. All full raw native files remain preserved on NCP. The four comparison CSVs are local; full local raw collection continues privately. Partial earlier transfers are retained. The public selection is compact. Each worker used one selected nonexclusive CPU; no 64-core utilization claim. R9 was observed without modification.

The unchanged C9 engine measures 21 piecewise-linear saved reconstructions in stored ln(a). Gamma units are s^-1, proper elapsed time uses elapsed_time_s in seconds, photonN/H is dimensionless. Full requested comparisons require both complete matching stored endpoints; partial outputs receive overlap-only labels. No extrapolation or endpoint projection. Actual accepted step distributions are recorded; halving the controller target does not establish fixed step ratio, method order or continuum error.

| Case | Observable | Sup absolute difference | Endpoint difference | Units |
|---|---|---:|---:|---|
| SIGNED_MINUS | xe | 4.607339791802556e-12 | 3.969212762286456e-12 | 1 |
| SIGNED_MINUS | Tgas_K | 0.0002295205366351638 | -0.0002295205366351638 | K |
| SIGNED_MINUS | photonN_per_H | 4.607340210855563e-12 | -9.090849346292685e-13 | 1 |
| SIGNED_MINUS | Gamma_HI_per_s | 5.57446228356588e-22 | -5.788267804179596e-23 | s^-1 |
| SIGNED_MINUS | Gamma_HeI_per_s | 5.628206196628421e-22 | -1.2860100675684838e-22 | s^-1 |
| SIGNED_MINUS | Gamma_HeII_per_s | 5.396503043052595e-24 | 1.4316024068363927e-26 | s^-1 |
| SIGNED_MINUS | elapsed_time_s | 14938.08203125 | 0.0 | s |
| COLD_FLRW | xe | 4.607366788436651e-12 | 3.5886860974207457e-12 | 1 |
| COLD_FLRW | Tgas_K | 0.00022918201801402915 | -0.00022918201801402915 | K |
| COLD_FLRW | photonN_per_H | 4.607369128957429e-12 | -9.092323203274719e-13 | 1 |
| COLD_FLRW | Gamma_HI_per_s | 5.574574437715742e-22 | -5.789178908326545e-23 | s^-1 |
| COLD_FLRW | Gamma_HeI_per_s | 5.628209304555498e-22 | -1.2860257347620624e-22 | s^-1 |
| COLD_FLRW | Gamma_HeII_per_s | 5.3965919166306224e-24 | 1.4315994535431936e-26 | s^-1 |
| COLD_FLRW | elapsed_time_s | 15482.81640625 | 0.0 | s |

Source007 time convergence, source008 threshold/angle/energy-grid, full-history/isotope admission remain HOLD. No agreement tolerance or physical admission is invented. Source009 initial8.098143045064857K differs from full005 REC IC. This unit awaits independent review.
