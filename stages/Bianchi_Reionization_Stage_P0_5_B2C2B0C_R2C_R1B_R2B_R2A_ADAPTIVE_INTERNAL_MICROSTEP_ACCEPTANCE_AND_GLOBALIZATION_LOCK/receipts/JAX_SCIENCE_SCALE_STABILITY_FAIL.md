# JAX science-scale stability failure

The static-shape JAX thermal root passed numerical parity, compile-count and
small-batch tests, and accelerated isolated trials.  It was not promoted.

In the actual adaptive sequence the process repeatedly stalled while
synchronizing the compiled root after several successful trials with changing
`dt` values.  Faulthandler located the stalls in `jax.device_get` / array
materialization.  The same full-node roots were stable under the NumPy oracle.
The failed runs are preserved in `SCIENCE_RUN.log`, `ADAPTIVE_DEBUG.log`,
`REPEATED_TRIAL_FAULTHANDLER.log`, and
`REPEATED_TRIAL_DEVICE_GET_PROFILE.log`.

This is an implementation/runtime stability failure, not a physics or
convergence certificate.  Under the predeclared backend policy, the JAX
candidate remains diagnostic and the stable NumPy array oracle is the
production backend.
