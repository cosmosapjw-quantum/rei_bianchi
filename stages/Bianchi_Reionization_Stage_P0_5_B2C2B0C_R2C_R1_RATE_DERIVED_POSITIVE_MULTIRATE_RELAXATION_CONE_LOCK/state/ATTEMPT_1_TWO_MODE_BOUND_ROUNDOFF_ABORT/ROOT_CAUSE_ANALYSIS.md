# Attempt 1 root-cause analysis

The abort occurred on the first macro while constructing the bounded two-mode weight. The selected C rate exceeded its locked upper bound by `2.0787283e-9 Myr^-1`, although the LP coordinate was exactly `z_C=0`.

This exposed a deeper false-feasibility problem. The original row scale was the maximum coefficient over the full attenuation box. For weakly identified radiative rates, `a_max` is of order `10^15`; a real cycling-capacity defect was therefore divided by the width of a rate box rather than by the physical node state. The first macro was accepted with normalized slack `-4.12e-14` while its equilibrium cycling slack was negative at physically material relative size. This was solver-conditioning error, not scientific infeasibility.

The repair keeps the locked rate box and normalized-equilibrium objective unchanged, but scales each inequality by the corresponding start/end physical state. Boundary rates are represented exactly, endpoint equilibria use the LP attenuation inverse directly, and the SciPy marginal signs in the KKT equation are corrected. No clipping, post-hoc interval expansion, or node-rate fitting is used.
