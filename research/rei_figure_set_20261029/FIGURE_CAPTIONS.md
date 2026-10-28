# Figure captions


All panels show the frozen illustrative external-source/escape model with a prescribed bath initially at 300 K. The lower axis is proper time elapsed since source onset in Myr (1 Myr = 31557600000000 s); the upper axis is mean redshift obtained from the saved eta(t) clock, z = 21 exp(-eta) - 1, and does not denote an absolute cosmic age. Curves connect the supplied saved samples without smoothing, resampling, or abundance floors. Positive vertices outside each stated plotting window are excluded from vector geometry; nonpositive points are omitted on logarithmic axes. Exact values and signs remain in outputs/raw_saved_arrays.csv, outputs/signed_differences.csv and outputs/plot_data.json; per-curve exclusion counts are in figures/FIGURE_METADATA.json.


## 01_all17_ON_refined


(a) Evolution of all 17 states in ON_refined. The shared log–log panel contains n, H I–II, D I–II, T I–II, 3He I–III, 4He I–III and 7Li I–IV. The plotted abundance is particles per Href multiplied by 10^22 for n, 1 for H, 10^4 for D and 3He, 10^18 for T, 10 for 4He and 10^9 for 7Li. These fixed multipliers separate traces for display; the grouped panels show unscaled abundances. The y window is 10^-8 to 2; t = 0 is omitted on the log-time axis.


## 02_group_1


(b) High-abundance group: peak >= 10^-3. H I, H II, 4He I, 4He II and 4He III are shown in raw particles per Href; the y window is 10^-5 to 1. Group membership uses each state’s positive peak across all three saved cases. The y limits use positive samples at t >= 1 Myr, rounded outward to decades, while the full elapsed-time span is retained. OFF_base is dashed, ON_base dotted and ON_refined solid; state colors are shared with panel (a).


## 02_group_2


(c) Intermediate-abundance group: 10^-6 <= peak < 10^-3. D I, D II, 3He I, 3He II and 3He III are shown in raw particles per Href; the y window is 10^-9 to 10^-4. Group membership uses each state’s positive peak across all three saved cases. The y limits use positive samples at t >= 1 Myr, rounded outward to decades, while the full elapsed-time span is retained. OFF_base is dashed, ON_base dotted and ON_refined solid; state colors are shared with panel (a).


## 02_group_3


(d) Lithium group: 10^-12 <= peak < 10^-6. 7Li I, 7Li II and 7Li III are shown in raw particles per Href; the y window is 10^-15 to 10^-9. Group membership uses each state’s positive peak across all three saved cases. The y limits use positive samples at t >= 1 Myr, rounded outward to decades, while the full elapsed-time span is retained. OFF_base is dashed, ON_base dotted and ON_refined solid; state colors are shared with panel (a).


## 02_group_4


(e) Trace lithium group: 10^-16 <= peak < 10^-12. 7Li IV is shown in raw particles per Href; the y window is 10^-22 to 10^-13. Group membership uses each state’s positive peak across all three saved cases. The y limits use positive samples at t >= 1 Myr, rounded outward to decades, while the full elapsed-time span is retained. OFF_base is dashed, ON_base dotted and ON_refined solid; state colors are shared with panel (a).


## 02_group_5


(f) Lowest-abundance group: peak < 10^-16. n, T I and T II are shown in raw particles per Href; the y window is 10^-23 to 10^-18. Group membership uses each state’s positive peak across all three saved cases. The y limits use positive samples at t >= 1 Myr, rounded outward to decades, while the full elapsed-time span is retained. OFF_base is dashed, ON_base dotted and ON_refined solid; state colors are shared with panel (a).


## 03_source_response


(g) Signed response to the full configured switch. For each of the 17 states, the ordinate is (ON_base - OFF_base) divided by the frozen state scale. This comparison switches both external sources and escape. The linear signed axis retains zero and negative responses; it does not divide by an instantaneous OFF abundance.


## 04_refinement


(h) Signed two-resolution agreement. For each state, the ordinate is (ON_base - ON_refined) divided by the frozen state scale. The maximum absolute normalized difference over saved times is 9.4756292130907 x 10^-8, below the original 10^-5 criterion. This normalized comparison supplies neither a convergence order nor an individual relative-error certificate for rare ions.


## 05_initial_transient


(i) Source-onset transient of n, T I and T II in ON_refined. Positive saved times and raw abundances are shown on logarithmic axes; all three stocks begin at zero at source onset. The upper axis explicitly states that mean z is approximately 20 throughout this short interval. The first stored times satisfying the subsequent-sample 1% stationarity/tracking conditions are 4142.168 s for n and 3.442953888 x 10^9 s for T I + T II; these sampled diagnostics do not specify exact continuous-time entry or separate T-charge-state equilibration times.


## 06_conservation


(j) Signed open-system conservation residuals. Baryon and heavy-charge/electron residuals for OFF_base, ON_base and ON_refined are divided by the original absolute tolerance 1.0820350005000101 x 10^-8 particles per Href. The baryon inventory includes visible nuclei, fast n/T and hidden Li6, together with the accumulated external baryon ledger; the charge residual subtracts the electron ledger and its initial value. The declining open baryon inventory is distinct from its near-zero signed balance residual. Maximum absolute baryon and charge residuals are 1.3041 x 10^-12 and 6.5361 x 10^-13 particles per Href.


Visual inspection status: all10 corrected raster panels (a)–(j) have been inspected. The independent completion review records PASS_SCOPED for the final layout in review/VISUAL_COMPLETION_REVIEW.json. The earlier3/10 partial inspection and bounded failed raster stage are preserved in Git history and the completion receipt.

The early-transient panel resolves n, T I and T II only; early He/Li positive samples excluded from grouped windows remain available in the raw tables and plot_data.json.
