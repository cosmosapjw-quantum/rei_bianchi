# T8DR5 — Stückelberg contour integral and branch ordering

## Scope

Implemented:
- CPC Eq. (56), first integral form
  `Delta = |Im integral_(Re Xc)^Xc DeltaE(R(X)) dX|`;
- `X=sqrt(R^2-rho^2)` mapping with continuous square-root branch tracking;
- real-to-complex adiabatic sheet continuation along the integration path;
- quadratic endpoint clustering for the square-root sheet coalescence;
- CPC Eq. (55) transition probability helper;
- hidden-crossing ordering by increasing `Re Rc` for Eq. (50);
- Appendix-A `DELTA(B=0)` regression for all five printed branch points.

## Fresh validation

Only `tests/test_r5.py` was executed:

`[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m                                                                 [100%][0m
[32m[32m[1m8 passed[0m[32m in 14.24s[0m[0m`

Maximum relative discrepancy versus Appendix-A `DELTA(B=0)`:
`4.185247e-04`.

This is a clean-room bounded reproduction.  It does not establish author-code
identity.

## Numerical path

The source Eq. (56) gives both a two-sheet gap integral and an equivalent
contour integral on the multivalued energy surface.  DR5 implements the first
form directly because DR4 already provides both analytically continued sheets.

For endpoint stability, the vertical segment in X is sampled with
`t=1-(1-s)^2`.  The exact branch endpoint is supplied by the independent DR4
spectral coalescence solve and `DeltaE(Xc)=0` is imposed there.

## Claim gate

CLOSED:
- `STUECKELBERG_EQ56_TWO_SHEET_INTEGRAL__IMPLEMENTED`
- `APPENDIX_A_DELTA_B0_FIVE_BRANCHES__BOUNDED_REPRODUCTION_PASS`
- `EQ55_SINGLE_PASS_PROBABILITY__IMPLEMENTED`
- `HIDDEN_CROSSING_ORDER_BY_RE_RC__IMPLEMENTED`
- `NONZERO_RHO_CONTOUR_PATH__IMPLEMENTED_SELF_CHECKED`

OPEN:
- `BRANCH_SEMIWIDTH_DELTA_RC_FOR_EQ52_CUTOFF__NOT_IMPLEMENTED`
- `GENERIC_RHO_AUTHOR_REGRESSION__UNAVAILABLE`
- `FULL_AUTOMATIC_BRANCH_ENUMERATION_TO_NMAX__NOT_IMPLEMENTED`
- `ROTATIONAL_TRANSITION_ODE_EQ47__NOT_STARTED`
- `END_TO_END_ARSENY_REPRODUCTION__NOT_STARTED`
- `BASS_CT2_PRODUCTION_CODE__CLOSED_NOT_STARTED`

Next exact node:
`T8DR6_ROTATIONAL_TRANSITION_ODE_AND_P_ROT`
