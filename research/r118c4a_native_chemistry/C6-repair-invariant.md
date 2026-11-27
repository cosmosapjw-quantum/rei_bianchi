# C6-repair-invariant | R118-C4A REI

The first native run failed an exact equality between requested eV input and round-tripped cgs state, with 1 ulp conversion discrepancy. Check bitwise pre/post stored state instead; no physics or tolerance change. Preserve first failure and partial outputs.
