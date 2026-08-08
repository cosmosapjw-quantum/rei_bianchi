# R2B-R2A-R2-R1A Four-Corner OTS Propagation Design

## Goal

Propagate the source-locked Hummer--Seaton branch uncertainty and unresolved OTS energy uncertainty through the accepted MPRK22(1)+Alexander-SDIRK2 first-canonical-interval operator without post-hoc lane selection, while preserving population, photon, resolved-energy, unresolved-energy, escaped-energy, and augmented total-energy ledgers at every microstep.

## Locked inputs

- prerequisite commit `893d2e06f6a32015603087881933e4763f00d2cb`;
- 46,080-node initial material state and three fixed shape lanes;
- 26-event full-OTS registry;
- Hummer--Seaton nodal `v` table and nodewise cell endpoints;
- `f in [0.1,1]` only;
- exact He II Ly-alpha packet energy `40.813320 eV`;
- locked two-photon first-moment bounds;
- MPRK22(1), Alexander-SDIRK2, analytic safeguarded root backend, owner law, and existing ledgers.

## Uncertainty lanes

Use four global `v` policies, two `f` endpoints, two OTS-energy policies, and all three shape lanes:

1. `CELL_LOWER_STRICT`: table-cell lower endpoint; below-table nodes use `v=0`.
2. `CELL_UPPER_STRICT`: table-cell upper endpoint; below-table nodes use `v=1`.
3. `ADAPTER_TABLE_LOW_STRICT`: named log-linear adapter inside the table; below-table nodes use `v=0`.
4. `ADAPTER_TABLE_HIGH_STRICT`: named log-linear adapter inside the table; below-table nodes use `v=1`.

For each, use `f=0.1` and `f=1`.  For energy:

- `UNRESOLVED_ONLY`: only exact He II Ly-alpha excess is resolved; all other OTS packet energy stays in `E_OTS_unres`.
- `TWO_PHOTON_BOUND_EXTREME`: propagate the locked lower/upper two-photon excess-energy endpoint while free-bound, Balmer, and case-B first moments remain unresolved.

The implementation represents the two energy endpoints as `ENERGY_LOWER` and `ENERGY_UPPER`, giving 16 uncertainty policies per shape lane and 48 global runs.

## Numerical scope

Run the first canonical interval with partition 2048.  This is an uncertainty-propagation preflight, not an accepted production history.  Each microstep is transactional; a failed lane leaves its parent state and ledgers unchanged.

## Acceptance gates

Every lane must satisfy:

- strict material positivity without clipping;
- H and He nuclei residuals `<1e-11`;
- owner and group photon closure `<1e-11`;
- thermal/root residual `<1e-10`;
- augmented total-energy residual `<1e-10`;
- exact-zero unsupported support and exact-zero subgrid resolved source;
- no negative branch multiplicity or branch-domain escape.

Predeclare the uncertainty qualification gate as ten times the numerical local-error gate:

- `max width(x_HII,x_HeI,x_HeII,x_HeIII) <= 2e-3`;
- `max width(log T) <= 2e-3`.

This gate is a project research budget, not a literature-derived universal tolerance.  Failure does not invalidate the event graph; it routes the project to source-extension calibration.

## Outputs

- per-lane and per-microstep ledger tables;
- final nodewise interval enclosures;
- lane failure certificates;
- exact symbolic and Decimal replay receipts;
- durable stage state, input lock, manifest, hashes, compact bundle, registry and handoff updates.

## Claim boundary

A pass authorizes only a first-canonical-interval uncertainty-qualified history stage.  It does not authorize production node chemistry, R2C-R2, B2C2B, recombination splice, CAMB transfer, front/Q_M, source/fesc fitting, or Bianchi feedback.
