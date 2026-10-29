# Recorded scientific repair (single bounded episode)

- **Observed first execution FAIL:** `LOGLINEAR_ABS_ENERGY_LEDGER` when independently applying a logarithmic mean to endpoint absorbed power, in addition to independently log-interpolating photoheat and photoionization-storage sources. This violates energy additivity between knots because log interpolation is nonlinear: `L(H+I)` generally differs from `L(H)+L(I)`.
- **Smallest physics-preserving correction:** define the interpolated absorbed-power function as the sum of independently interpolated heat power and `I_j` times photo-event rate; integrate as `Q_abs=Q_heat+Q_ion`, not a separate logmean of the endpoint total. Keep the trapezoid separately, which preserves additivity by linearity.
- **Subsequent actual result:** 12 Python regression methods PASS; 168 independent mpmath90 comparisons PASS; all 84 event records have positive source integrals and exact component-energy closure within finite precision. No tolerance relaxed.
- **Visual repair:** removed a bottom caption overlapping the time-axis label; information moved to chart title.
- **Not an error certificate:** difference of two assumed interpolants is descriptive scheme sensitivity; no smoothness/curvature bound on true history was supplied.

- **Packaging boundary:** initial ZIP builder discovered a receipt output file while the shell redirected the builder stdout into the very directory being archived; that file was empty at scan time and mutated after archiving. Corrected the packager to exclude its own mutable receipt from source payload, while including the independent clean-restore logs. This is packaging-only, not a science result revision.
