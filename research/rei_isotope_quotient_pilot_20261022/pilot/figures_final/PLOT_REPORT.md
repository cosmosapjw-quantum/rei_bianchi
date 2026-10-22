# Pilot figure readback

Status: **COMPLETE**. Read 79 nominal and 3 tighter-control SHA-matched original trajectories; no IVPs.

Every PNG has a PDF companion. Exact selected source files, SHA-256 values, columns and transformations are in `PLOT_SELECTION_MANIFEST.csv`; derived control and isotropic-baseline differences are also in `controls_differences.csv` and `baseline_differences.csv`.

The figures display 21 n_Aq/n_B outputs, while the inherited equality closure evolves nine independent charge fractions. n and T have zero inventory. Nominal LiIII/IV remain zero in the fixed soft-UV atomic model. Temperature (100–10000 K) and 5–60 eV UV are prescribed; gas/radiation energy is test-fluid bookkeeping. No thermal or nuclear closure, production admission, or observational reionization inference is made.

Run offline with `python pilot/code/render.py` from this package.
