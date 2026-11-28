# T8DR4 — complex TERM and Q/S spectral branch-point solver

## Scope
Implemented:
- asymmetric `Z1 != Z2` TERM recurrences at complex `R`;
- real-to-complex analytic-sheet continuation;
- direct two-sheet spectral coalescence solver;
- CPC Eq. (36) and Eq. (37) S-series helpers;
- five precise Appendix-A branch-point regressions.

The branch solver is a clean-room formulation. Unknowns are
`(p_a,lambda_a,p_b,lambda_b,R)` and it solves the two TERM residual pairs plus
`p_a^2-p_b^2=0`, equivalent to equal electronic energy at common `R`.

## Fresh tests
Only DR4 tests were run:
`[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m                                                               [100%][0m
[32m[32m[1m10 passed[0m[32m in 3.99s[0m[0m`

Maximum discrepancy from the five Appendix-A author-program branch points:
`1.663726e-05 a0`.

## Source discrepancy
CPC Table 1 gives the S `2p-sigma / 3p-sigma` point approximately as
`(0.58,0.69)`, while Appendix A prints
`(0.5002386252692,0.7522845045231)`.
DR4 keeps this discrepancy explicit and uses Appendix A as the precise numeric
regression oracle.

## Claim gate
CLOSED:
- `TERM_COMPLEX_R_ASYMMETRIC__IMPLEMENTED`
- `REAL_TO_COMPLEX_SHEET_CONTINUATION__IMPLEMENTED`
- `Q_S_SPECTRAL_COALESCENCE_SYSTEM__DERIVED_AND_IMPLEMENTED`
- `APPENDIX_A_Q_BRANCHPOINTS_4__BOUNDED_REPRODUCTION_PASS`
- `APPENDIX_A_S_BRANCHPOINT_1__BOUNDED_REPRODUCTION_PASS`
- `COMPLEX_CONJUGATION_SYMMETRY__PASS`
- `TABLE1_VS_APPENDIX_A_S_DISCREPANCY__PRESERVED`

OPEN:
- `GENERIC_ALL_BRANCH_ENUMERATION__NOT_CLAIMED`
- `STUECKELBERG_CONTOUR_INTEGRAL_EQ56__NOT_STARTED`
- `ROTATIONAL_TRANSITION_ODE_EQ47__NOT_STARTED`
- `END_TO_END_ARSENY_REPRODUCTION__NOT_STARTED`
- `BASS_CT2_PRODUCTION_CODE__CLOSED_NOT_STARTED`

Next exact node:
`T8DR5_STUECKELBERG_CONTOUR_INTEGRAL_AND_BRANCH_ORDERING`
