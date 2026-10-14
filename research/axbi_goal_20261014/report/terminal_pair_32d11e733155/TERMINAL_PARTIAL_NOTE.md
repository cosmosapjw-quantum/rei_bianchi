# Matched-scale-factor terminal partial ZERO / SHEAR_PLUS

Both original runs stopped at the accepted-step resource cap (200000 accepted), at exactly a=0.08873654701704167, zbar=10.269313869154184. This is a terminal partial interval from zbar20; the selected endpoint zbar4 was not reached.

|Case|Elapsed proper time [Myr]|Tgas [K]|xHII|xHeII|xHeIII|
|---|---:|---:|---:|---:|---:|
|ZERO|275.733582305|2964.86532393|0.0991426055371|0.104701820973|3.07503796717e-05|
|SHEAR_PLUS|275.72815814|2964.83878191|0.0991413487793|0.104700505199|3.07496898396e-05|

These are conditional values from the stored discrete histories. The same terminal scale factor has unequal proper times. No signed shear response is claimed resolved without matched numerical refinement; no full-history, convergence, or tiny-trace accuracy claim follows.

Abundances use Y_i=n_i/(nH+4nHe), with the electron curve labelled a charge census, not a nucleus. Exact zeros are masked only for log display, and every retained positive sample is plotted without flooring/clipping. Temperature curves preserve chronological order with arrows, never sort by temperature. All 200001 accepted rows per case were checked for ordered history/abundance alignment and saved nuclei/charge/baryon normalization using inherited 1e-12 checks.

Display downsampling retains the first/last row and extrema of each of six species and gas temperature in every chronological 100-row block, producing 4003 samples per case. Intermediate points are omitted for rendering, not modified; raw original CSVs remain untouched and exact SHA identities are in FIGURE_MANIFEST.json. This sampling does not provide a continuous interpolation error bound. Both PNGs were visually checked for labels, logarithmic domain and chronological temperature arrows.

![Elapsed proper time](abundance_vs_elapsed_time.png)

![Chronological gas temperature](abundance_vs_Tgas_time_ordered.png)

Actual single plot command: `python3 research/axbi_goal_20261014/report/terminal_pair_32d11e733155/plot_terminal_pair.py`. Exit 0. Raw stdout/stderr/resource record are under raw/. Reproduction is fail-closed against existing output; use a fresh copy of this plotting directory if rerendering is later authorized.
