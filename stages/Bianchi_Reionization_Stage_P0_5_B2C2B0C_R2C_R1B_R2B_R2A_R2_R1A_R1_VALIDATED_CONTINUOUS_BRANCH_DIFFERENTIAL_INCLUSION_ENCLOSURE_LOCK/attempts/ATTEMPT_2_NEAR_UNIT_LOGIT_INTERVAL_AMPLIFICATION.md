# Attempt 2 — near-unit logit interval amplification

A full logit representation preserved the population cone, but the helium
ionized fraction satisfies `q_He_ion = 1-O(1e-5)`.  Its transformed derivative
contains `1/[q(1-q)]`, so ordinary interval dependency amplified the second
Picard tube until the logit interval spanned roughly `[-1.3e4,2.3e5]` and the
corresponding sigmoid interval contained numerical zero.

The issue is not a physical singularity.  It is a poor coordinate choice for a
nearly saturated variable.  The final internal coordinates instead track the
small positive reservoirs directly:

```text
log x_HI,
log x_HeI,
logit[x_HeIII/(x_HeII+x_HeIII)],
log T.
```

This keeps the H and He simplex exact while avoiding division by the small
neutral fractions in the coordinate map itself.
