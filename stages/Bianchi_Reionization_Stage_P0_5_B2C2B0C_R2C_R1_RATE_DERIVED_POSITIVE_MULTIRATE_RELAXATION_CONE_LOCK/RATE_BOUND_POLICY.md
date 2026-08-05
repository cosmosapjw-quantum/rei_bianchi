# Rate-bound policy — locked before feasibility

For each shape/substep/macro, rates are **macro-shared**, never node-fitted.

The interval for each family is the closed hull of independent nonnegative estimates available before feasibility:

- `M`: endpoint secant turnover and start/end gross signed-transfer turnover `(dot M+ + dot M-)/M`.
- `I`: endpoint secant turnover and start/end gross H-ionization activity `(J_HI + R_HII + C_HI + ionized mass transfer)/M`.
- `U`: endpoint secant turnover and start/end gross thermal activity `(heating + cooling + expansion + transferred thermal energy)/U`.
- `C`: endpoint secant turnover and the start/end neutral-stock/recombination driver envelope. This family is not independently identifiable and is labelled an interval nuisance parameter.
- `J_g`: endpoint secant turnover and start/end radiative absorption rate `c(1+z) kappa_g/Mpc`. It is labelled an interval nuisance parameter because no independent node redistribution equation is inherited.

Zero estimates are retained in the evidence table but do not define a positive lower bound. If a changing endpoint has no positive estimate, the case is `UNIDENTIFIABLE_REQUIRED_RATE` and fails. If the endpoint is constant, the rate is dynamically irrelevant and receives the shared reference `1/Delta t` only for evaluation.

One-mode is mandatory first. Two-mode has exactly two rates fixed at the family interval endpoints and no extra fitted rate; allowed weights are induced by a previously feasible one-mode attenuation. Mode count and bounds cannot change after the rate lock is written.
