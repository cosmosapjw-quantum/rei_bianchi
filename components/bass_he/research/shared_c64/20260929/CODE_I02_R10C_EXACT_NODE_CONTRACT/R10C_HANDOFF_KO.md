# BASS_HE R10C handoff: exact consumed-node geometry audit and fixed-GK replay

이 prompt는 R10B independent review PASS 이후의 별도 승인된 numerical-contract node다.
R10A를 다시 시작하거나 interpolation을 추가 수정하지 않는다.

## 0. Fresh identity gate

Repository: `cosmosapjw-quantum/BASS_HE`

Fresh-read:
- PR #15 `audit11/dr11h-certificate-binding`
  expected HEAD `b8b2fe47a367459f6faf6796eb2f251feacbbd7c`.
- PR #17 `research/shared-c64-crossrepo-20260928`
  expected R10B review basis at least
  `7bda18fafe9a800a13146b38276bef204584c079`.
- root `AGENTS.md`.

Read before execution:
- R10B independent `REVIEW_VERDICT.json`
- R10B `DECISION.json`
- R10B `PROPOSED_QUERY_CONTRACT.json`
- R10A `RUN_CONTRACT.json`
- R10A full evidence archive.

Pinned R10A numerical source identity:
`496a1d9be062e074e72f4d2d8033dd865c4671b65f95daaeaeafa2fcde4eb4a`.

Pinned query-contract SHA256:
`97ee706c2765cac40cb001592fe5c543053ed5457b3ee4776e282a742238f215`.

If any source/query identity differs, stop `R10C_IDENTITY_MISMATCH`.
Do not force/reset/merge user worktrees.

## 1. Frozen gates and inherited decisions

Preserve:
- `CODE_I02_CLOSED=true`
- `full_certificate_fail_closed=true`
- `scientific_PROMOTE=HOLD`
- `Eq55_next_node_authorized=false`
- `Eq55=NOT_RUN`

R10B:
`NODE_IDENTITY_REPAIR_REVIEW=PASS_BOUNDED_RESEARCH_VIEW`.

R10A:
`SURROGATE_REBUILD_UNRESOLVED` remains a historical verdict.
Its 3.333/1.880 ratios and Appendix-A comparison remain quarantined.

## 2. Exact query set

Use **exactly** the query rows in R10B `PROPOSED_QUERY_CONTRACT.json`:

- 105 unique GK15 rho coordinates
- 360 active branch/rho pairs
- branch counts:
  - S23 30
  - Qother 75
  - Q12 60
  - Q23 105
  - Qm1 90

No new rho coordinates, adaptive refinement, fitting nodes or branch set.

## 3. Phase A: exact consumed-node Delta table

For each active pair, obtain the same numerical-contract geometry used by R10A:

- depth 96
- contour panels 32
- same source/dependencies
- same branch endpoint/certificate authority

Restore the original R10A evidence archive and endpoints. Do not automatically
recompute missing endpoints. If an endpoint/source authority is unavailable, return
`R10C_ENDPOINT_AUTHORITY_BLOCKED`.

### Reuse

Reuse a Delta record only when exact source, environment, branch, rho hex, depth and
panel identity match the R10A cache contract.

R10B forensic cross-match found only one candidate overlap between its 50 stored
posthoc references and the fixed query set:

- Q23
- rho hex `0x1.a48d0b9cfad3cp+2`
- stored 64-panel Delta `0.5023163509308193`

This is only a candidate. Do not reuse unless the underlying cache/source/environment
identity authorizes it. Otherwise calculate it afresh at 32 panels.

Maximum new 32-panel contour calls: 360.
Expected if that one exact reuse is valid: 359.

R10A measured 109 geometry cache calls at mean ~1.412 s, median ~1.347 s on the old
host. Treat ~8.4 serial minutes for 359 calls only as a planning estimate, not SLA.

Persist each result atomically as soon as it is computed.

Immediate STOP only for:
- identity mismatch
- missing endpoint authority
- contour/certificate failure
- nonfinite/negative Delta

Do **not** stop merely because the repaired surrogate exceeds 2e-4. That classifies
the surrogate, while the exact-node table remains usable for Phase B.

## 4. Surrogate consumed-node audit

Using the independently reviewed repaired Q23 fit view, compare surrogate Delta to
each exact 32-panel consumed-node Delta.

For every pair record:
- exact Delta and hex
- surrogate Delta
- absolute and relative error
- local stencil indices
- local rank/condition number
- `pass = relative_error <= 2e-4`

Return:
- `SURROGATE_CONSUMED_QUERY_PASS` if all 360 pass
- otherwise `SURROGATE_CONSUMED_QUERY_FAIL`

This is not a global interpolation bound.

Do not alter anchors, cubic method, tolerance or rcond after seeing failures.

## 5. Phase B: exact-node three-lane transport replay

Phase B is authorized if and only if Phase A produces a complete valid exact-node
table for all 360 active pairs. It does **not** require surrogate PASS.

At the fixed 105 rho coordinates assemble geometry directly from the exact Delta table.

Compute exactly these research lanes:

- `F2-RHO`: `P=exp[-2 Delta_exact(rho)/v]`
- `F2-FROZEN`: `P=exp[-2 Delta_exact(0)/v]` inside unchanged branch support
- `F1-RHO`: `P=exp[-Delta_exact(rho)/v]`

Keep unchanged:
- Nmax=3
- five branch order/topology
- support cutoffs
- rotation steps 32
- absorbing upper-shell semantics
- energies 0.5 and 5 keV/u

### Fixed quadrature only

Use the same support cutoffs and existing GK15/GK7 pair.

Run the existing support-split quadrature with `max_intervals` fixed equal to the
number of mandatory support intervals. Assert:

- requested rho set exactly equals the pinned 105-coordinate set;
- evaluations = 105;
- refinements = 0.

If any component has embedded error above

`atol + rtol*abs(total)`, with `rtol=2e-4`, `atol=1e-10`,

stop `EXACT_NODE_FIXED_GK15_QUADRATURE_UNRESOLVED`.

Do not add new nodes/refine.

If all components pass, return:

`EXACT_NODE_FIXED_GK15_REPLAY_PASS_NOT_GLOBAL_CONTINUUM_BOUND`.

## 6. Separate surrogate/model error from quadrature error

At each node/event let

`p = exp(-f Delta/v)`, `f in {1,2}`.

Record exact-vs-surrogate `delta_p`.

For both reversible and absorbing event blocks:

`||delta T_e||_1 = 2 |delta_p_e|`.

Because Eq.(50) uses the crossing sequence on both sides of an unchanged
column-stochastic rotation, record the conservative nodewise bound

`||delta y||_1 <= 4 sum_e |delta_p_e|`.

Use it only as a surrogate-model discrepancy diagnostic. Do not add it to the
embedded GK estimator and call the sum a rigorous continuum error bound.

## 7. Appendix-A comparison and I2 impact

Only if Phase B passes, report:

- exact-node F2-RHO
- exact-node F2-FROZEN
- exact-node F1-RHO
- F2-FROZEN/F2-RHO impact at both energies
- Appendix-A comparisons

Every Appendix-A metric must remain labeled:

`AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION`.

Compare to the quarantined R10A exploratory values, but never overwrite them.

Classify R9 I2:

- `I2_MEASURABLE_CASE_A`: frozen lane materially improves author reproduction
- `I2_MEASURABLE_CASE_B`: frozen lane changes outputs but does not improve author reproduction
- `I2_SCOPED_NEGLIGIBLE_CASE_C`
- or `I2_QUANTIFICATION_UNRESOLVED`

State the numerical criterion actually used for “materially”.

## 8. Verification and non-scope

Any new research runner/helper must use TDD RED→GREEN.

Required:
- exact query-set identity tests
- cache reuse identity tests
- exact geometry table completeness
- fixed-node/no-refinement assertions
- F2-FROZEN lane isolation
- analytic probability-ratio regression
- `git diff --check`

Do not run repository full pytest unless production/package code is changed, which is
not intended.

Do NOT:
- modify production source/defaults/tolerances
- add interpolation refinement
- switch interpolation family
- rerun CODE-I02
- run 56-action replay or worker sweep
- execute author FORTRAN
- start L2/Krawczyk
- create new physical channels

## 9. Publication, backup, return

Publish append-only under a new timestamped PR17 namespace.

Return:
- fresh refs/source hashes
- exact reuse count and new Delta call count
- exact-node table manifest
- surrogate consumed-query PASS/FAIL
- fixed-GK quadrature PASS/FAIL
- exact-node three-lane outputs if admitted
- I2 classification
- separate surrogate and quadrature diagnostics
- commands/exits
- what was not run
- backup receipts
- bounded next policy-decision prompt

Back up create-only to the existing BASS_HE Drive folder and Dropbox dossier.
Distinguish provider ACK from raw restore verification.

Do not self-promote:
`scientific_PROMOTE=HOLD`,
`Eq55_next_node_authorized=false`,
`Eq55=NOT_RUN`
remain until a later policy decision.
