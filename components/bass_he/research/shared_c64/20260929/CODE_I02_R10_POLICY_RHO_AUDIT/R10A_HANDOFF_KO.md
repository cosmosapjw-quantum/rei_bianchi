# BASS_HE R10A handoff: separate factor-two normalization from author frozen-rho artifact

This prompt is self-contained. Execute in a fresh isolated worktree. Do not alter
production defaults or reopen closed CODE-I02 work.

## 0. Fresh identity gate

Repository: `cosmosapjw-quantum/BASS_HE`

Fresh-read before execution:
- PR #15 `audit11/dr11h-certificate-binding`, expected HEAD
  `b8b2fe47a367459f6faf6796eb2f251feacbbd7c`.
- PR #17 research branch, newest `CODE_I02_R9_AUTHOR_CODE_AUDIT` and R10 policy
  synthesis namespace.
- root `AGENTS.md`.

R9 author source identities:
- dataset DOI `10.17632/n43srxwdnm.1`, Version 1;
- provider ZIP SHA256
  `48a06833600ae1789ba853945d9b878837ffd9c95d08c085a3875c12cd41bc67`;
- `arseny.f` SHA256
  `96827045654428cff9a32930415a9f6c39615b0b41677d00d377edf7c37d6f78`;
- classification `AUTHOR_USES_FACTOR2_DIRECT`.

Do not import/copy author FORTRAN into clean-room source.

## 1. Frozen scientific state

Preserve:
- `CODE_I02_CLOSED=true`
- `full_certificate_fail_closed=true`
- `scientific_PROMOTE=HOLD`
- `Eq55_next_node_authorized=false`
- `Eq55=NOT_RUN`.

R10 policy:
- factor-two = primary **research** candidate;
- Eq.(52)-literal factor-one = source-compatibility control;
- Appendix-A author numbers = implementation-reproduction benchmark, not physical gold;
- no production default change is authorized.

## 2. Question

Quantify R9 Important finding I2:

> ARSENY STCKLBR2 stores a Delta(rho) grid, but SECTION uses the first stored sample
> `CMES(1)` for every impact parameter while support gating still changes with rho.

Separate that artifact from the exponent-normalization question.

## 3. Three required lanes

Use the same existing Nmax=3 clean-room scope, five published branches, identical
rotation/trajectory/integration settings, and energies 0.5 and 5 keV/u.

### F2-RHO
Current clean-room factor-two lane:
`P = exp[-2 Delta(rho)/v]`.

### F2-FROZEN
Research-only emulation of the static author data flow:
for each branch compute `Delta0 = Delta(rho=0)` once, then inside the branch's
existing support cutoff use
`P = exp[-2 Delta0/v]`
for every rho.

Do not change support cutoffs, branch order, matrix topology, rotation, or upper-shell
handling. Do not put this mode into production source or make it a default.

### F1-RHO
Literal printed Eq.(52) control:
`P = exp[-Delta(rho)/v]`.

## 4. Reuse before recompute

Read first:
- `evidence/DR8_ADAPTIVE_SURROGATE_STUDY.json`
- `evidence/DR8V_ADVERSARIAL_HOLDOUT.json`
- `legacy/reference/r5_appendix_a_stueckelberg_regression.csv`
- DR9B normalization audit
- R9 `STATIC_DATA_FLOW.md` and `NORMALIZATION_CROSSWALK.json`.

Reuse validated DR8 surrogate/integration artifacts if their identity is available.
Do not rebuild the entire scientific pipeline merely for audit theater.

If the raw surrogate table is unavailable, create only the minimum new rho-dependent
Delta evaluations needed for this comparison and record that fact.

## 5. Required branch diagnostics

For each of the five scoped branches, record at least:
`rho/support = 0, 0.25, 0.5, 0.75, 0.9, 0.99`
unless a node is numerically invalid, in which case preserve the failure.

Record:
- Delta(rho);
- Delta(rho)/Delta(0);
- P_F2_RHO at 0.5 and 5 keV/u;
- P_F2_FROZEN;
- ratio `P_F2_FROZEN/P_F2_RHO`;
- support status.

Regression identity:

`P_F2_FROZEN/P_F2_RHO = exp[-2(Delta0-Delta(rho))/v]`.

## 6. Integrated comparison

Using the existing scoped Eq.(50)/(54) research integrator, compute all three lanes:

- indexed reaction-loss / current scoped observables already used by DR8/DR9B;
- shell-aggregated values used in Appendix-A comparisons;
- stochasticity/range diagnostics;
- existing convergence/error estimator.

Do not introduce new physical channels.

For Appendix-A comparisons label every metric:

`AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION`.

Report:
- F2-RHO vs author;
- F2-FROZEN vs author;
- F1-RHO vs author;
- F2-RHO vs F2-FROZEN.

## 7. Interpretation contract

### Case A: F2-FROZEN improves author reproduction materially
Conclude that the R9 `CMES(1)` static trace has measurable output impact and explains
some author/clean-room discrepancy. Do not promote F2-FROZEN physically.

### Case B: F2-FROZEN changes results but does not improve author reproduction
Conclude that additional implementation differences dominate. Identify them only by
bounded static/source inspection.

### Case C: F2-FROZEN is numerically negligible
Record an empirical upper bound within the scoped five branches/two energies only.

## 8. Verification

This node changes research harness/evidence only.

Required:
- TDD for any new frozen-lane adapter;
- focused tests of lane isolation and analytic probability ratio;
- exact/surrogate sentinels sufficient for any newly evaluated Delta nodes;
- `git diff --check`.

Run full repository pytest only if production/package code was affected; intended
solution requires no production change.

Do NOT run:
- CODE-I02 hostile matrix;
- 56-action replay;
- worker sweep;
- R1/R2;
- L2/Krawczyk;
- author FORTRAN execution;
- production Eq.(55) or Eq.(50)/(54) default changes.

## 9. Durable evidence

Publish append-only under a new PR #17 timestamped namespace.

Return machine-readable:
- exact source commit/tree;
- reused evidence identities;
- new Delta evaluations and convergence metadata;
- three-lane branch/table outputs;
- Appendix-A discrepancy metrics;
- measured I2 impact;
- what was NOT run;
- gate ledger.

Back up new artifacts create-only to the established BASS_HE Drive folder and Dropbox
`/BASS_DERIVATION_DOSSIERS_20260912/`, with provider ACK/IDs/hash/readback semantics.

## 10. Return decision

Do not self-promote production policy.

Return:
- whether factor-two normalization remains the preferred research interpretation;
- quantitative effect of frozen Delta(0);
- whether Appendix-A residual is explained by R9 I2;
- remaining model/systematic gates;
- a bounded next decision prompt.

Keep:
- `scientific_PROMOTE=HOLD`
- `Eq55_next_node_authorized=false`
- `Eq55=NOT_RUN`
unless a later separately authorized policy decision changes them.
