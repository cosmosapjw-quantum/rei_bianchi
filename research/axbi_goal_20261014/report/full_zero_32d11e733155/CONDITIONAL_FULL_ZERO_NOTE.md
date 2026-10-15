# Conditional full-interval ZERO abundance figures

The actual composed ZERO history covers the selected zbar20→4 interval, a=0.2, with 312237 cumulative accepted steps and 312238 saved history states. This is conditional output from the frozen source/initial-condition/numerical model; independent full-history science review remains pending.

Elapsed proper time since zbar20 is 1356.08827799 Myr. This is not absolute cosmic age. Conditional endpoint values are Tgas=7900.62136567 K, xHII=0.999997317099, xHeII=0.974208101237, xHeIII=0.0257843175744. These stored values do not imply their displayed digits are accurate.

All joined history/abundance rows were read using the existing completed-history validator: exact selected interval/count, finite and ordered state, complete species blocks, history alignment, charge census and baryon normalization at the inherited 1e-12 checks. COMPOSITION_RECEIPT and COMPLETED_CASE_INPUT identities, composed input files and original/segment library identities were bound and rechecked. Original binary32d11e733155 and continuation wrappera7e3f1d98bd8 remain separately labelled in FIGURE_MANIFEST.json.

The display uses 6250 chronological samples. Each 100-row block contributes first/last and extrema of each species and gas temperature; global endpoints, first positive points and positive minima are also retained. Original data remain untouched. Intermediate display points are omitted, not modified; sampling does not estimate continuous interpolation error. True zeros are masked only on the logarithmic axis. Retained positive values have no floor or clipping. Temperature is never sorted, so heating and cooling branches preserve their actual time order; arrows indicate increasing time. Electron abundance is a charge census, not a nucleus.

Tiny trace abundances, including the saved minimum near1e-34, have not been proved accurate by this validation. No evolution convergence, resolved shear response, absolute-age, observer-tail or broader physical accuracy claim is made. Whole-history feedback and optical depth remain PENDING as explicitly recorded by the composition receipt.

![Elapsed proper time](abundance_vs_elapsed_time.png)

![Chronological gas temperature](abundance_vs_Tgas_time_ordered.png)

One actual plotting command: `python3 research/axbi_goal_20261014/report/full_zero_32d11e733155/plot_full_zero.py`. Exit0; wall16.345048s; CPU16.934297s; peakRSS153604KiB. Raw stdout/stderr and invocation record are under raw/. No solver or Cargo invocation occurred. Both PNGs were visually checked: labels readable, positive minima within the logarithmic axes, and time-ordered Tgas branches retained. Independent admission remains pending.
