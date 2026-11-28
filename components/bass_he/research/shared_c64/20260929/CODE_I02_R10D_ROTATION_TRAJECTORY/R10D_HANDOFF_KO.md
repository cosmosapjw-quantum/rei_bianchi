# BASS_HE R10D handoff: rotational trajectory/cutoff separation

이 prompt는 R10C exact-node PASS 이후 실행할 bounded research node다.
새 contour/Stückelberg 계산을 하지 않고, rotational model만 분리한다.

## 0. fresh identity gate

Repository: `cosmosapjw-quantum/BASS_HE`

Fresh-read:
- PR15 expected HEAD `b8b2fe47a367459f6faf6796eb2f251feacbbd7c`
- PR17 latest research head
- root `AGENTS.md`
- R10C `EXECUTION_VERDICT.json`
- R10C `EXACT_NODE_TABLE.json` and manifest
- R9 author-code audit static flow
- R10D `AUTHOR_ROTATION_CROSSWALK.json`

Required R10C exact table SHA256:
`21b9ca0fa7934e05cc9d3da7044b184a6286cc0c18de01b1e43a15d21e5d3a49`

Author source:
- DOI `10.17632/n43srxwdnm.1`
- `arseny.f` SHA256
  `96827045654428cff9a32930415a9f6c39615b0b41677d00d377edf7c37d6f78`
- DMP=0.80, Z1=1, Z2=2.

Do not copy author source into clean-room code.

## 1. frozen state

Preserve:

`CODE_I02_CLOSED=true`
`full_certificate_fail_closed=true`
`scientific_PROMOTE=HOLD`
`Eq55_next_node_authorized=false`
`Eq55=NOT_RUN`.

R10C:
- exact-node table COMPLETE
- surrogate consumed-query PASS
- fixed GK15 PASS
- R9 I2 = `I2_MEASURABLE_CASE_B`
- F2-RHO remains primary research lane
- old R10A exploratory values remain quarantined.

## 2. source discrepancy to test

CPC paper formulation:
- global nuclear trajectory: straight line `R=(vt,rho,0)`
- Eq.(47): rotational evolution
- Eq.(36), m=0 real-part cutoff:
  `R_CPC=((l+1/2)^2-1/2)/(Z1+Z2)`.

Distributed author WRN:
- `a=Z1 Z2/(DM v^2)`
- repulsive Coulomb trajectory
  `R(theta)=rho^2/(-a+sqrt(a^2+rho^2) cos(theta))`
- `Rmin=a+sqrt(a^2+rho^2)`
- rotation only if `Rmin<Rcut`
- `R_author=(l+1/2)^2/(Z1+Z2)`.

This node tests these two differences separately.

## 3. research-only Coulomb rotation adapter

Implement from Eq.(47) and analytic classical trajectory, not by translating author FORTRAN.

Use the existing clean-room angular-momentum operators and probability-collapse convention.

For `rho>0`, parameterize the collision by internuclear-axis angle theta.
Classical angular momentum gives `R^2 |dtheta/dt| = rho v`.
Construct the Hermitian Eq.(47) generator in a basis/convention that is algebraically
equivalent to the straight-line implementation.

Required tests before lane execution:

1. `a -> 0` / numerically tiny-a limit at fixed cutoff converges to existing
   straight-line rotation probabilities.
2. If `Rmin>=Rcut`, Coulomb block is identity/not-entered.
3. Unitarity defect and collapsed column-stochastic defect stay within the existing
   numerical precision scale.
4. step doubling is converged before use; report 64/128/256 or an equivalent
   predeclared sequence.
5. changing only cutoff with straight trajectory reproduces current implementation
   when cutoff is reset to `R_CPC`.
6. no author source lines are copied into implementation.

Do not support rho=0 by an improvised formula. Fixed GK quadrature nodes are interior.
If a requested consumed node is exactly zero, stop and design the limit separately.

## 4. five lanes

Reuse the R10C exact Delta table. New contour solves = 0.

Hidden crossings for lanes 1-4:
`P=exp[-2 Delta_exact(rho)/v]`.

Run:

1. `SL_CPC`
   current straight-line rotation + `R_CPC`.

2. `SL_AUTHORCUT`
   straight-line rotation + `R_author`.

3. `COUL_CPC`
   Coulomb rotation + `R_CPC`.

4. `COUL_AUTHOR`
   Coulomb rotation + `R_author`.

5. `COUL_AUTHOR_FROZEN`
   Coulomb + author cutoff + `exp[-2 Delta_exact(0)/v]`.
   This is implementation-reproduction-only and not a physical candidate.

Keep:
- Nmax=3
- same five hidden-crossing branches
- same 105 fixed GK nodes
- same support cutoffs for hidden crossings
- energies 0.5 and 5 keV/u
- same absorbing upper-shell semantics
- fixed-GK no-refinement integration.

## 5. precommitted decomposition

For each indexed and shell observable O:

`cutoff_effect = O_SL_AUTHORCUT - O_SL_CPC`

`trajectory_effect = O_COUL_CPC - O_SL_CPC`

`interaction =
 O_COUL_AUTHOR - O_COUL_CPC - O_SL_AUTHORCUT + O_SL_CPC`.

Also record lane ratios and log ratios where O>0.

Material output effect:
- relative change > 1% at either energy, AND
- absolute change > 10 times both lanes' summed embedded GK error estimates.

Author-reproduction improvement:
both
- all-six multiplicative RMS, and
- dominant n=2,n=3 multiplicative RMS
must decrease by at least 5% relative to `SL_CPC`.

Label every Appendix-A comparison:
`AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION`.

## 6. numerical verification

Use TDD RED->GREEN for the Coulomb adapter.

Record:
- trajectory/cutoff constants and source identity
- rotation matrix convergence
- unitary/stochasticity defects
- fixed 105-node set identity
- evaluations=105 and refinements=0
- component GK estimator
- no new contour calls.

If rotation step convergence fails, stop `R10D_ROTATION_NUMERICS_UNRESOLVED`.
Do not loosen tolerances after seeing lane results.

If fixed GK requests refinement, stop
`R10D_FIXED_GK_QUADRATURE_UNRESOLVED`.

## 7. interpretation

### Rotation explains residual
If `COUL_AUTHOR` materially improves both Appendix RMS metrics, conclude that the
author/clean-room rotational trajectory/cutoff discrepancy explains a measurable
part of the Appendix-A residual.

Use the 2x2 decomposition to state whether cutoff, Coulomb bending, or their interaction
dominates.

### Partial author-like lane improves further
If `COUL_AUTHOR_FROZEN` improves beyond `COUL_AUTHOR`, record an interaction between
R9 I2 and the author rotation model. Do not make frozen Delta physically preferred.

### No improvement
If `COUL_AUTHOR` does not improve Appendix reproduction, do not broaden the model
immediately. The next bounded source differences are author JMAX=300 midpoint
impact integration and MODKG/C_S_AT mapping.

## 8. non-scope

Do NOT:
- change production rotation/default
- run new contour Delta solves
- change factor-two policy
- rerun CODE-I02
- start bent-trajectory hidden-crossing Delta
- run author FORTRAN
- add physical continuum channels
- start L2/Krawczyk
- merge/force-push.

## 9. durable return

Publish append-only on PR17.

Return:
- source/table identities
- independent Coulomb derivation note
- RED/GREEN commands and counts
- rotation convergence table
- five-lane fixed-GK results
- 2x2 effect decomposition
- Appendix-A RMS comparison
- whether `COUL_AUTHOR` explains residual
- what remains open
- backup receipts
- next bounded policy prompt.

Keep:
`scientific_PROMOTE=HOLD`
`Eq55_next_node_authorized=false`
`Eq55=NOT_RUN`
until a separate policy decision.
