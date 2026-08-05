# Hypothesis graph — R2C-R1A

## H1 — unchanged scalar-rate taxonomy

**Core claim:** Node-local rates for `M,I,U,C,J_g` remove the old failures
without changing the variables.

**Threat:** `C` has no autonomous law and `J_g` is an algebraic absorption
flux.  Node-local fitting would merely hide the category error.

**Decision:** `REJECT`.

## H2 — state/flux/budget reclassification

**Core claim:** Use material states `(N_HI,N_HII,U)` plus transfer, algebraic
RT fluxes `J_g=Gamma_g N_HI`, and a cumulative photon ledger.  Retain the old
storage-plus-recombination expression only as a whole-interval necessary
budget.

**Predictions tested:**

1. `C` fails refinement covariance — passed.
2. All inherited endpoints remain in the physical state cone — passed 540/540.
3. Direct endpoint rates and RT fluxes are finite/nonnegative — passed all rows.
4. The six mass Farkas cases have feasible endpoint segments — passed 6/6.

**Decision:** `PROMOTE` as the corrected operator basis.

## H3 — immediately introduce a more general coupled positive generator

**Core claim:** Even after H2, cross-coordinate coupling beyond H chemistry is
required.

**Threat:** No corrected nonautonomous photon-conserving forcing audit has yet
failed.  Adding couplings now would be premature and underidentified.

**Decision:** `HOLD` until R2C-R1B.
