# Saved n/T nuclear projection

`project_saved.py` reads the recovered canonical nuclear NPZ, verifies its pinned source identities and registries, selects exactly `quotient_L16_S-0.6_Am0_Ar0`, and writes the 257 saved epochs as raw-natural-log CSV plus JSON with log10 presentation columns. `plot_saved.py` renders the two-panel figure from that JSON. The initial `-Infinity` is retained as a tagged source zero and omitted from the numeric plot; no abundance exponentiation or stock reconstruction is performed.

The stocks come only from `log_T_n[...,T,n]`. The distinct forward `n_beta` and `t_beta` cumulative event columns count beta daughters, not H or He3 total stocks. Source DD fluxes and fast sources at three epochs are tabulated as diagnostics. Elapsed proper seconds belong to this source history and are not cosmic age. This conditional all-bare, instantly thermalized, passive-reservoir nuclear sensitivity is separate from the 17-ion ANGTHERM01 baseline.

After the root allocation and static review, the bounded extractor and targeted tests may run once, followed by one bounded render. This code does not import the original nuclear solver, rerun an IVP, or splice ionic histories.
