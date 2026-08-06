# Closeout — R2C-R1A

## Confirmed

- The H reaction generator is positive and H-nucleus conserving.
- `J_g` is an RT-coupled absorption/reaction flux.
- `C_Delta t=N_HI,start/Delta t+R_rec` is an interval budget rate, not an
  autonomous state.
- All 1,382,400 node states and 2,764,800 active-group rows pass endpoint sign,
  support, finite-rate and current-Gamma gates.
- All 540 endpoint pairs lie in the convex `M-I-U`/mass-cap cone.
- The six mass-cap Farkas cases have both endpoints within cap.

## Rejected or weakened

- Independent scalar relaxation of `C,J_G1,J_G2a`.
- Interpreting the 497 certificates as a physical-history no-go.
- Using endpoint-local `N/dt+R` as a substitute for a time-averaged photon
  ledger.

## Still uncertain

- The unique or minimally parameterized interior `Gamma_g(t)`/flux history.
- Thermal evolution at optically thick nodes.
- H/He/recombination-radiation coupling outside the inherited exact-zero lane.

## Durable verdict

`DURABLE_PASS_R2C_R1A_STATE_FLUX_BUDGET_RECLASSIFICATION_RESOLVES_FARKAS_BLOCKER_R1B_AUTHORIZED`

## Authorization

- `R2C_R1B_authorized = true`
- `production_node_chemistry_authorized = false`
- `B2C2B_authorized = false`
