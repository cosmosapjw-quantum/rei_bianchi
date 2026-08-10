# PHYS-MATH audit

## Definitions and units

For a local Patankar stage, `A z = b` is dimensionally a population solve:
`A` is dimensionless, while `z` and `b` carry the same population-density unit.
Its exact tangent is

\[
 A\,\delta z=\delta b-(\delta A)z.
\]

For a thermal root

\[
 r(x)=C_U e^x-U_0-wR(x),\qquad x=\ln T,
\]

`r`, `C_U e^x` and `wR` carry the same energy-density unit, and

\[
 \partial_xr=C_U e^x-w\,\partial_xR.
\]

The Krawczyk contraction and image-to-tube ratios are dimensionless.

## Exact identities

- H and He tangent invariants vanish exactly.
- The owner-normalization derivative sums to zero.
- The implicit-tangent and thermal-root derivative residuals simplify to zero.
- Structural H/He cross blocks are exactly zero in the audited local population
  matrices.

## Numerical inclusion

- local population block certificates: `552960/552960`;
- maximum population row-sum bound: `0.031102095838177812`;
- local thermal-root certificates: `276480/276480`;
- maximum thermal contraction bound: `1.0686929563519243e-08`;
- maximum Krawczyk image/tube ratio: `9.9706373090339612e-05`;
- root derivative intervals contain no zero.

## Known limits and assumptions

The certificates freeze material state, owner amplitude, volume, heating and
Hubble rate at each evaluation site. They prove local existence/uniqueness only.
They do not prove that the four independently controlled sites compose into the
reported public-width enclosure.

## Ranked findings

- **P0:** cross-site/state-feedback remainder is absent.
- **P1:** Hummer–Seaton event localization and restart are not certified for the
  continuous image.
- **P1:** photon/thermal/OTS/escaped total ledgers are not yet propagated as
  sets through the full map.
- **P3:** native Wolfram was unavailable; an executable `.wl` script and exact
  SymPy receipt are preserved.
