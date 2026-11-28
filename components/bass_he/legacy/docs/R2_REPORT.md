# T8DR2 — real-R TERM spectral solver

## Scope

Implemented:
- asymmetric two-center problem Z1 != Z2;
- real positive internuclear separation R;
- bound states E<0;
- Jaffe quasi-radial and Baber-Hasse quasi-angular recurrences;
- state-specific matched continued fractions;
- damped two-variable Newton solve for `(p, lambda)`;
- branch continuation in R from a united-atom-labelled seed.

Not implemented:
- symmetric Z1=Z2 special angular recurrence;
- complex R;
- analytic continuation / Q- and S-series branch points;
- CORDIR/CORINV separated-atom label assignment;
- Stückelberg contour integral;
- rotational-transition ODE.

## Main numerical form

For recurrence
`A_s y_{s+1}+B_s y_s+C_s y_{s-1}=0`,
R2 constructs:

1. a finite continued fraction from `y_-1=0` to the state node-count index;
2. a downward minimal-solution tail from large s;
3. the sign-consistent matching condition

`F_low - A_n C_{n+1}/F_high = 0`.

For the radial recurrence the node count is
`n_xi=N-l-1`.

For the asymmetric angular recurrence it is
`n_eta=l-m`.

The two matching residuals are solved simultaneously.

## Fresh validation

Only R2 tests were executed.

Validation lanes:
1. continued-fraction depth convergence;
2. R->0 united-atom hydrogenic limit;
3. R->infinity separated-atom asymptotic behavior for traced 1s-sigma and
   2p-sigma branches;
4. residual closure for several low states;
5. branch-continuation behavior.

The large-R checks are asymptotic checks, not imported author-code regression.

## Claim gate

Closed:
- `PRIMARY_TWO_CENTER_CONVENTION_ERRATA_AUDIT__CLOSED`
- `TERM_REAL_ASYMMETRIC_RECURRENCES__IMPLEMENTED`
- `TERM_REAL_MATCHED_CONTINUED_FRACTIONS__IMPLEMENTED`
- `TERM_REAL_DAMPED_NEWTON__IMPLEMENTED`
- `TERM_REAL_UNITED_ATOM_LIMIT__NUMERICALLY_CHECKED`
- `TERM_REAL_SEPARATED_ATOM_LIMIT__NUMERICALLY_CHECKED`
- `TERM_REAL_LOCAL_CONTINUATION__IMPLEMENTATION_VERIFIED`

Open:
- `TERM_COMPLEX_R__NOT_STARTED`
- `Q_S_BRANCH_POINT_SOLVER__NOT_STARTED`
- `CORDIR_CORINV__NOT_STARTED`
- `END_TO_END_ARSENY_REPRODUCTION__NOT_STARTED`
- `BASS_CT2_PRODUCTION_CODE__CLOSED_NOT_STARTED`
