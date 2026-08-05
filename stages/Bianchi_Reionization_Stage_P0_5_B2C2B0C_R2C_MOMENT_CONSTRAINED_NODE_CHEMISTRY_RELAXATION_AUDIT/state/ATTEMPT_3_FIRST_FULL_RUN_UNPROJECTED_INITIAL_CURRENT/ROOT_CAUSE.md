# Attempt 3 — first full run with unprojected initial current

This run is preserved and superseded, not overwritten as evidence.

The z=6 initial construction scaled the extensive cycling capacity by the
locked initial/first-endpoint sink-mass ratio while retaining the first
endpoint node current distribution.  Although each macro retained enough
total capacity for its assigned group totals, 25,356 global node rows began
outside the row-capacity cone.  Repeated current projections therefore acted
as an initialization correction whose accumulated redistribution increased
with refinement, producing the non-monotone first-endpoint current error.

The correction is not clipping and does not alter any R2B hard endpoint.
The revised initialization performs one constrained KL projection per macro,
preserving each macro's G1/G2a totals exactly while enforcing the scaled node
capacity rows, and records the KKT/dual certificate before time integration.
