# BASS_HE R10E handoff: extended fixed-step closure for Coulomb rotation, then R10D factorial lanes

This handoff is outcome-informed research design, not a blind precommitment. It follows
R10D's valid stop and defines a new numerical contract without weakening the old gate.

## 0. Fresh identity

Repository: cosmosapjw-quantum/BASS_HE

Fresh-read:
- PR15 expected HEAD b8b2fe47a367459f6faf6796eb2f251feacbbd7c
- PR17 latest research HEAD
- root AGENTS.md
- R10D EXECUTION_VERDICT.json
- R10D ROTATION_CONVERGENCE.json
- R10D coulomb_rotation.py
- R10C exact table and manifest
- R10E DECISION.json and EXPLORATORY_NUMERICAL_DIAGNOSTIC.json

Required identities:
- R10C table SHA256 21b9ca0fa7934e05cc9d3da7044b184a6286cc0c18de01b1e43a15d21e5d3a49
- R10D Coulomb adapter Git blob 543ff5e5c20ff2969547f03410cd30353998348c

If the adapter or exact table changed, stop R10E_IDENTITY_MISMATCH.

## 1. Preserve R10D history

Keep R10D_ROTATION_NUMERICS_UNRESOLVED as the historical verdict for the
64/128/256 contract. Do not edit that evidence or claim the original gate passed.

Frozen:
CODE_I02_CLOSED=true
full_certificate_fail_closed=true
scientific_PROMOTE=HOLD
Eq55_next_node_authorized=false
Eq55=NOT_RUN.

## 2. New numerical gate

Before any lane integration write a gate file with:
- all fixed 105 rho nodes
- all 12 N,l,E,cutoff combinations
- steps [256,512,1024]
- probability successive-difference limit 1e-7
- unitarity/stochasticity limits 5e-13
- originally failed combinations:
  (2,1,0.5,AUTHOR), (3,2,0.5,CPC), (3,2,0.5,AUTHOR)
- minimum observed order 3.5
- independent auditor SciPy DOP853
- auditor rtol=1e-12, atol=1e-14
- auditor probability agreement limit 1e-8.

Write this before the fresh convergence run. Do not change thresholds afterward.

## 3. Fresh extended Magnus convergence

Run the unchanged R10D adapter at 256,512,1024 over the same 105 nodes and all 12 combinations.

For each combination record:
- max |P256-P512| and rho hex
- max |P512-P1024| and rho hex
- unitarity/stochasticity maxima
- entered-node count.

PASS requires:
1. every max |P512-P1024| <=1e-7
2. unitarity <=5e-13
3. stochasticity <=5e-13
4. step differences decrease.

For the three previously failed combinations compute pointwise observed order at the
node producing D512_1024:
p_obs=log2(D256_512/D512_1024), require p_obs>=3.5.
Do not divide maxima from different rho.

## 4. Independent DOP853 auditor

Code this independently from the Magnus loop.

For each of 12 combinations, preselect the node after the fresh step-doubling run as
the rho giving the largest |P512-P1024|, tie-breaking by smaller rho hex.

Integrate the same gauge ODE and physical interval with SciPy solve_ivp DOP853,
rtol=1e-12, atol=1e-14.

Require max |P_Magnus1024-P_DOP853| <=1e-8 for each combination.
Record nfev, accepted step count, and solver success.

DOP853 is an auditor only.

## 5. Numerical decision

If Sections 3-4 pass:
R10E_ROTATION_NUMERICS_PASS_EXTENDED_CONTRACT.

Accepted research resolution:
straight-line 64 steps, Coulomb 1024 steps.

If any criterion fails:
R10E_ROTATION_NUMERICS_UNRESOLVED and STOP before five-lane transport.

Do not increase to 2048 or loosen tolerance in the same execution context.

## 6. Resume original R10D factorial comparison only after PASS

Reuse R10C exact Delta table. New contour solves=0.

Run:
SL_CPC
SL_AUTHORCUT
COUL_CPC
COUL_AUTHOR
COUL_AUTHOR_FROZEN

Lanes 1-4 use factor-two exact rho-dependent Delta.
Lane 5 uses author-like frozen Delta(0) as implementation-reproduction diagnostic only.

Straight lanes use 64 steps; Coulomb lanes 1024.

Keep Nmax=3, five branches, same 105 fixed GK nodes, same support cutoffs,
energies 0.5 and 5 keV/u, same upper-shell bookkeeping, no adaptive GK refinement.

Effect decomposition:
cutoff_effect = SL_AUTHORCUT-SL_CPC
trajectory_effect = COUL_CPC-SL_CPC
interaction = COUL_AUTHOR-COUL_CPC-SL_AUTHORCUT+SL_CPC.

## 7. Fixed-GK and Appendix-A gates

Use exactly the R10C fixed GK15/GK7 query set.
Assert evaluations=105 and refinements=0.

If embedded component gate fails, stop R10E_FIXED_GK_QUADRATURE_UNRESOLVED.

All Appendix-A metrics remain:
AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION.

Use the original R10D materiality rules.

## 8. Interpretation

Return separately:
- numerical convergence verdict
- cutoff main effect
- trajectory main effect
- interaction
- frozen-Delta addition effect
- Appendix-A changes
- whether rotation explains a measurable residual component.

Even if COUL_AUTHOR improves Appendix A, do not call it physically validated.

If it does not improve both Appendix RMS metrics materially, next bounded source
differences are author JMAX=300 midpoint impact integration and MODKG/C_S_AT mapping.
Do not broaden to them in this run.

## 9. Non-scope

Do not change production source/defaults/tolerances or adapter algebra.
No new contour Delta solve, CODE-I02 rerun, 56-action replay, worker sweep,
author FORTRAN execution, L2/Krawczyk, new channels, merge or force-push.

## 10. Durable return

Publish append-only under new PR17 namespace.

Return source identities, gate file, all convergence records, DOP853 audit,
R10E verdict, admitted five-lane results, 2x2 decomposition, Appendix-A RMS,
commands/exits, not-run list, backup receipts, and a bounded next policy prompt.

Keep scientific_PROMOTE=HOLD, Eq55_next_node_authorized=false, Eq55=NOT_RUN
until a separate policy decision.
