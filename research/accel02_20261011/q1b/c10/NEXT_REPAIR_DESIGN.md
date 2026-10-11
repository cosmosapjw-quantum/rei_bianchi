# Next bounded unit: entry precision and production time control

Status: proposed numerical design, not implemented or scientifically admitted. Continue from preserved C10 outputs; do not repeat the same 1/2/4 family, source scans or C3 check unchanged.

Two distinct risks were measured: source quadrature becomes roundoff-sensitive for tested small entry steps; the first-order split map changes noticeably under a coarse local time refinement. Neither observation proves that every intermediate step fails or that the full-interval normalized temporal criterion fails. Treat the saved common-final comparison as diagnosis, not a substitute for the original 65/129-epoch comparison.

## Precision lane (parallel with controller design)

1. Locate loss in the declared formulas separately: R(t)-R1; cell/source energy intersections; log(right/left); Q-aN; and mean reconstruction. Use saved failing h=5e9/2.5e9 inputs, an independent high-precision evaluation of the *same* pinned interpolation/background equations, and a breakdown of absolute and cell-relative errors. Do not change the source model or silently substitute a different background solution.
2. Derive stable differences with log1p/expm1 and cell-relative coordinates where they are algebraically equivalent. Retain a compensated moment offset D=Q-aN or a two-component Q only if it is computed from and reconciled with the authoritative moment state. It is numerical precision metadata, not a new physical variable or a seeded mean. Threshold sides must remain explicit.
3. Use direct positive integrals for D and heat where possible; report the roundoff of conversion back to N/U and native physical energy. The generic physical-q guard remains until a provider-specific value bound and explicit trace contract justify an alternative. Never remove the guard because one output looks smooth.
4. Extend checkpoint identity/arrays to every authoritative low component. Test one changed-source birth and one restarted continuation; reuse completed C3 and old native bridge evidence.

## Production time-control lane

1. Predeclare fixed physical scales for the numerical controller, including initially zero trace ions; these solver scales do not replace final scientific normalization. Existing completed histories can inform scale design with their limited scope disclosed; they are not new accepted fine references.
2. Compare a prospective bounded first-order controller against a positive higher-order or source/absorption-coupled alternative if its measured cost is excessive. The current split map delays all absorption to the second substep; conservation alone cannot bound that splitting error. New methods need common source/absorption/heat/counter pairing, explicit strict domains and their own convergence evidence.
3. Do not infer a full-history error from the relative error of xHeIII≈1e-16 at one early endpoint. Track absolute defects, relative errors with declared solver scales and the eventual whole-history maxima separately. No floor may be added to physical state or to the official acceptance denominator.
4. Once changed local representation/controller and actual restart gates pass independent review, run the complete15.9→4 interval with immutable C2/C3 plus a same-grid temporal pair, checkpoint natural boundaries, and measure all24 fields on65/129 sets. A local pass is authorization to attempt this measurement, not its scientific result.

The full native acceptance remains time2e-6, energy/initial-energy1e-9, number/initial-nH1e-9, spectral/angular1e-3 and geometry1e-11. BASS new-native adoption waits for an actually accepted producer history; old reduced N4 results never transfer by relabeling.
