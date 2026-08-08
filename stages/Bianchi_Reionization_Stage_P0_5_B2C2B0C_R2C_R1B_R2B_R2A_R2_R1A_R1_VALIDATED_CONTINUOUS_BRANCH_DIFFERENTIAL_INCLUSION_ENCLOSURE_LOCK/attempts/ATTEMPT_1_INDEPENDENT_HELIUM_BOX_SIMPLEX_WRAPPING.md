# Attempt 1 — independent helium fraction box wrapping

The first interval tube used independent coordinates `(x_HeII,x_HeIII)`.
Although every sampled endpoint remained in the physical helium simplex, the
componentwise hull lost their anticorrelation and produced

```text
max(upper x_HeII + upper x_HeIII) = 1.0005012733971193
min implied x_HeI                  = -0.0005012733971193
```

This caused a denominator interval to contain zero.  The failure is a wrapping
artifact, not a physical negative population and not a tolerance problem.

The load-bearing interval state was therefore changed to the triangular
coordinates

```text
q_He_ion = x_HeII + x_HeIII
r_HeIII  = x_HeIII / q_He_ion
```

with reconstruction

```text
x_HeI   = 1 - q_He_ion
x_HeII  = q_He_ion (1-r_HeIII)
x_HeIII = q_He_ion r_HeIII.
```

This preserves the simplex structurally for every rectangular interval in
`0<=q<=1`, `0<=r<=1`.
