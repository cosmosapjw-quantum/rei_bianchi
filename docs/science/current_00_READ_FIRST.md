# R2C finite-relaxation audit — current durable science state

Current stage:

```text
P0.5-B2C2B0C-R2C-MOMENT-CONSTRAINED-NODE-CHEMISTRY-RELAXATION-AUDIT
DURABLE_FAIL_CLOSED_R2C_CONSTANT_EQUILIBRIUM_RELAXATION_NOT_ALL_LANES_REACHABLE
```

The R2B static node lift remains a valid constrained endpoint lock, but it is
not a production chemistry history. After a macro-local initial current KL
projection removed a boundary-only capacity inconsistency, every physically
feasible case converged under `dt`, `dt/2`, and `dt/4`. The one-rate,
one-constant-equilibrium model was feasible in only 18/30, 10/30, and 6/30
cases for tau=10, 100, and 300 Myr. The remaining obstruction is physical-cone
extrapolation, dominated at tau=10 Myr by node cycling-capacity deficits.

Production node chemistry and B2C2B are unauthorized. The next authorized
work is the rate-derived positive multirate relaxation-cone model-adequacy
lock; it must not generate a production history.
