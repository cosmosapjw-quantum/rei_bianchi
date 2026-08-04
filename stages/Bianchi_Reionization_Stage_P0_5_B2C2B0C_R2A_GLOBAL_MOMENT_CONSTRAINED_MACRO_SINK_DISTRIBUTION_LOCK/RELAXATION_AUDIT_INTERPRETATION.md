# Finite-relaxation feasibility auditor

For each macro variable target `y_n` and previous locked target `y_{n-1}`, the auditor asks whether a bounded equilibrium state exists for

```text
y_n = y_{n-1} + [1-exp(-Delta t/tau)] (y_eq,n-y_{n-1}).
```

It therefore reconstructs

```text
y_eq,n = y_{n-1} + (y_n-y_{n-1})/[1-exp(-Delta t/tau)]
```

and checks non-negativity, macro mass and volume caps, opacity non-negativity, and photo/recombination cycling capacity. A separate shape-only lane applies the same test to normalized mass and opacity measures.

This is a feasibility test, not a kinetic calibration. Passing tau=10 Myr proves that at least one finite response scale can track every locked target without violating the R2A constraints. Failure at tau=100/300 Myr means that slow first-order relaxation cannot reproduce parts of the inherited reduced-DAE history without an overshooting, negative, over-capacity, or cycling-infeasible equilibrium. R2B must not silently promote those slow lanes.
