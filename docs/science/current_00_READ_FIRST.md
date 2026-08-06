# R2C-R1A state–flux–budget reclassification — current durable science state

Current stage:

```text
P0.5-B2C2B0C-R2C-R1A-NODE-LOCAL-PHYSICS-DERIVED-RATE-FIELD-CONE-PREFLIGHT
DURABLE_PASS_R2C_R1A_STATE_FLUX_BUDGET_RECLASSIFICATION_RESOLVES_FARKAS_BLOCKER_R1B_AUTHORIZED
```

R2C-R1A resolves the previous 497-certificate blocker narrowly but
decisively. The certificates remain valid against the rejected macro-shared
common-equilibrium surrogate; they are not no-go theorems for physical node
histories.

The corrected taxonomy is:

- material states: `M=N_HI+N_HII`, `N_HI`, `N_HII`, and a separately audited
  thermal variable;
- algebraic radiation/reaction fluxes: `J_g`, `Gamma_g`, `kappa_g`, `Phi_g`;
- interval budget, not state:
  `C_Delta t=N_HI,start/Delta t+R_rec,average`;
- conservation law: absorbed photons close through the cumulative neutral-H
  ledger rather than the artificial pointwise cone `sum_g J_g<=C(t)`.

The full audit covered 1,382,400 node states,
2,764,800 active group rows, and 540
macro cases. Endpoint state/sign/finiteness failures were zero; the maximum
current–Gamma and locked-moment residuals were
`9.143e-16` and
`3.541e-14`. All
540 endpoint pairs lie in a convex state/mass-cap
segment, including the six former mass-cap Farkas cases.

This is not a production-history pass. The interior radiation forcing,
cumulative photon ledger, and genuine thermal equation remain unconstructed.
Production node chemistry, R2C-R2, and B2C2B remain unauthorized.

Next stage:

```text
P0.5-B2C2B0C-R2C-R1B-PHOTON-CONSERVING-CUMULATIVE-BUDGET-NONAUTONOMOUS-RT-FORCING-LOCK
```

R2C-R1B must remove `C` from the state vector, build a prelocked
photon-conserving nonautonomous RT/chemistry fixed point, close node/macro/global
photon and H/He ledgers under `dt,dt/2,dt/4,dt/8`, and retain a stricter
optical-depth-dependent thermal gate.
