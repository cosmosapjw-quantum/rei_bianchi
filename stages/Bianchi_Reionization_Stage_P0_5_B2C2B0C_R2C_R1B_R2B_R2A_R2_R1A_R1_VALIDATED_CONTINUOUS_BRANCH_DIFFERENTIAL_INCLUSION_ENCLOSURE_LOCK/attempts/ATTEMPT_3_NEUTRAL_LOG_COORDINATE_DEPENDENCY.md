# Attempt 3 — neutral-log coordinate dependency

Representing the small H I and He I reservoirs by logarithms prevents a sign
change, but introduces `d log x/dt = (dx/dt)/x`.  The He I fraction is only
`O(1e-5)`, and a standard interval tube therefore magnified the transformed
right-hand side until its upper log bound crossed zero after a few Picard
iterations.

The final reduced state uses the positive reservoirs themselves:

```text
x_HI,
x_HeI,
r_HeIII = x_HeIII/(x_HeII+x_HeIII),
log T.
```

Adaptive step rejection, rather than a coordinate singularity or numerical
floor, now controls whether a tube remains in the strict population cone.
