# R10C exact-node contract research summary

## Starting point

Independent R10B review returned
`NODE_IDENTITY_REPAIR_REVIEW=PASS_BOUNDED_RESEARCH_VIEW`, reproducing the Q23
rank repair while preserving `R10A=SURROGATE_REBUILD_UNRESOLVED`.

The repaired view does not validate every consumed GK15 branch/rho pair. The R10B
review explicitly left the 105-coordinate / 360-active-pair reference gate unrun.

## Research decision

Do not add another interpolation refinement or switch interpolation families.
The next bounded node computes exact 32-panel Delta on the exact downstream query set.

The pinned R10B query contract contains:
- 105 unique GK15 rho coordinates
- 360 active branch/rho pairs
- S23 30, Qother 75, Q12 60, Q23 105, Qm1 90.

Only exact source/environment/cache-key matches may be reused. Cross-matching the
50 archived posthoc references against the fixed query set found one candidate exact
branch+rho overlap; actual reuse still requires cache identity verification.

R10A has 109 measured geometry cache calls with mean ~1.412 s, so 359 new calls imply
~8.4 serial minutes on the old host as a planning estimate only.

## Error-channel separation

R10A demonstrated that a GK15/GK7 embedded estimator can converge while the Delta
surrogate is wrong. Therefore R10C separates:

1. exact geometry / surrogate discrepancy;
2. transport sensitivity to that discrepancy;
3. fixed quadrature embedded error.

SciSpace literature on adaptive quadrature, surrogate uncertainty and discretization
uncertainty supports this separation conceptually, but does not certify the project
threshold.

Wolfram verifies for `p=exp(-f Delta/v)`:
- `||delta T||_1 = 2|delta p|` for reversible and absorbing crossing blocks;
- with the crossing sequence on both sides of an unchanged column-stochastic rotation,
  `||delta y||_1 <= 4 sum_e |delta p_e|`.

This is a nodewise audit bound, not a continuum cross-section theorem.

## Exact-node transport replay

Once all 360 exact Delta entries exist, the three research lanes are recomputed from
the exact node table, not from the surrogate:

- F2-RHO
- F2-FROZEN
- F1-RHO

The same seven support intervals and GK15/GK7 rule are used with refinement disabled.
Any component requiring refinement returns
`EXACT_NODE_FIXED_GK15_QUADRATURE_UNRESOLVED`.

If all components pass, the claim is only
`EXACT_NODE_FIXED_GK15_REPLAY_PASS_NOT_GLOBAL_CONTINUUM_BOUND`.

Appendix-A comparisons remain implementation-reproduction diagnostics rather than
physical validation.

## Gates

No gate changes during authoring:
`CODE_I02_CLOSED=true`,
`full_certificate_fail_closed=true`,
`scientific_PROMOTE=HOLD`,
`Eq55_next_node_authorized=false`,
`Eq55=NOT_RUN`.
