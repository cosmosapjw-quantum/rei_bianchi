# C2: frozen formula–data–code mapping and finite binding diagnostic

Date: 2026-10-22. Selected stage: C2 only. Authority: the completed C1 unit
`../rei_coupled_isotope_contract_20261022/CONTRACT.md` at commit
`9f621b684fedb9b71f2148022f6909d1760ba947`. C1 is reused without re-review.
This unit maps actual inputs and executes a small local diagnostic. It neither
implements a coupled cosmological IVP nor declares C3–C10 complete.

## Source pins and ownership

- Existing working checkout: `rei_isotope`, branch
  `research/rei-coupled-isotope-contract-20261022`, starting HEAD
  `3e56bbd3d939ab235df2d47f9d012c95674d00fc`.
- Nuclear/source lineage: PR219 `a7bff87fd7cb4c2bba1810ee8d6384ae208fb824`,
  whose scientific pilot parent is `5a1e5220b301a1c497f2863d6fd823e605faba80`.
- Read-only atomic donor: existing `rei_bianchi` checkout, PR220
  `8be7533cc97b3302bf42608699d6e8313ed6af8a`.
- Recovered RR candidate: exact member bytes in
  `/workspace/scratch/d5baa30c266d/recovery_intake_c2/REI_RUNTIME_RECOVERY_CHECKPOINT_20261022.zip`,
  SHA256 `d5efb39514fc22df573f81488c7b822500d724b2396b5bc4d8806e28e740e8ce`.
  Its recorded tests are historical, and its bootstrap errors are not rerun
  here. Its RR source is a candidate comparison input, not a newly admitted
  production provider.

All new canonical files belong exclusively to this directory. Concurrent
changes under `rei_bootstrap_energy_providers_20261022` and the old pilot DAG
are outside this task: do not change, stage, or publish them. No branch or
checkout changes, reset, new worktree, source donor edit, or old C1 edit.
Use only observed files; do not substitute a current uncommitted recovery
implementation for the pinned recovery archive.

## Required constructive mapping

Record ordered 21 slots, isotope mass number/nuclear charge/ionic charge,
absolute abundance normalization, 13 photo/RR edges, six DR edges, exact
coefficient keys and original source row identities. Use the full 18-family
nuclear JSON registry (not the 13-family `channels()` helper), 34 directed
physical entries, per-direction units, and explicit applicability statuses.
Unresolved charge branches and energy partitions remain explicit required
inputs; no physical branch probabilities may be invented.

Map proper-time source functions to the outer x=ln(a/a_ref) implementation:
physical sources return dY/dt, and the outer solver divides by H and the
population scale once. Map initial data, fixed spectrum, boundaries, and
the old compact quotient's zero-n/T restriction. Off-grid nuclear rates,
tiny-stock representation, and new thermal Jacobians belong to C3 onward.

## RR formula and scientific meaning

For a coefficient row A,B,T0,T1,C,T2, define

    u=sqrt(T/T0), v=sqrt(T/T1), b=B+C exp(-T2/T)
    alpha=1e-6 A/[u(1+u)^(1-b)(1+v)^(1+b)]    [m^3/s]
    b_dot=C exp(-T2/T) T2/T
    D=-1/2 -(1-b)u/[2(1+u)] -(1+b)v/[2(1+v)]
      +b_dot log[(1+u)/(1+v)]
    lambda=k_B T alpha (3/2+D)                 [J m^3/s].

The lambda identity assumes nonrelativistic Maxwellian relative electrons,
one temperature-independent cross section/target population, and the same
number-rate function. Applying it to an empirical fit is a conditional
derivative-of-fit moment, not an independently accurate energy-loss table,
final-state spectrum, or branch model. Do not replace either source's alpha.
Keep each alpha and its own derivative/moment together.

Recovered VF and donor H/He rows should agree within binary64 roundoff.
Recovered VF Li and donor Badnell Li are intentionally different providers;
measure differences, never use equality as their acceptance criterion.
Badnell's temperature-dependent b requires the b_dot term above.

## Prescribed implementation and bounded checks

The lower-tier worker creates `code/check_bindings.py`, immutable minimal
`vendor/` copies, `fixtures/`, `BINDINGS.json`, `SOURCE_IDENTITY.json`, and
raw `evidence/` outputs. Copy the donor atomic Python file plus the ten inputs
required by its source manifest, preserving relative paths and original bytes.
Copy the recovered RR Python and row JSON directly from ZIP members and retain
their original contract/implementation record as historical context. Include
the saved nuclear contract, evaluated decay inputs, and a small extracted
sample of its NPZ arrays; avoid copying large histories when samples suffice.
Record source file SHA256, upstream commit/member identity and sampled indices.

One finite invocation shall perform:

1. Map all 21 slots, 13 RR/photo edges and six DR edges to actual code rows.
   At T=100,1000,10000 K, evaluate the pinned donor `rates()` and recovered
   `rr_rate()` for six electronic channels. Check H/He equality with relative
   residual <=128 epsilon; output all three Li alpha and lambda ratios.
   A separately evaluated direct formula must reproduce the donor alpha.
2. At the same temperatures for all six rows, plus T=1e6 K for the three Li
   rows only, compare analytic D against a five-point centered derivative of
   log alpha with respect to log T, step h=1e-3, absolute tolerance 1e-8.
   The 1e6 K points are formula controls within the donor runtime domain,
   outside the 100–10000 K pilot comparison. Deliberately omit b_dot for Li+
   at 1e6 K and require that control to fail the same 1e-8 criterion.
3. Evaluate fixed UV cutoffs 60 and 200 eV using the actual donor API. For
   each photo edge, check absorbed=threshold*Gamma+primary+core with normalized
   residual <=128 epsilon. Check the named Li1s/LiII/LiIII external-field
   support zeros at 60 eV and their positive support at 200 eV. These checks
   concern the finite quadrature, not continuum quadrature convergence or
   newly generated nuclear photons.
4. Use a single declared manufactured positive 21-vector, normalized by
   A.Y=1, nb=1 m^-3, T=10000 K, UV=1. Form
   Fatom=(G0+ne Gne)Y and Jatom=G0+ne Gne+nb outer(GneY,q).
   Compare Fatom+D.Y with old evaluate dY_dt, and Jatom+D with its jacobian.
   Normalize residual by the sum of norms of the constituent terms, avoiding
   loss-of-significance artifacts from subtracting a dominant beta term;
   tolerance 128 epsilon. Also demonstrate that retaining D in an allegedly
   beta-free assembly disagrees with Fatom at that criterion. This verifies
   the integration boundary; it supplies no physical daughter probabilities.
5. Read the already saved nuclear NPZ files directly. Assert recorded shapes,
   family order, natural-log convention, and shared T grid. Save case index0
   at epochs0,128,256, including x,T,nB,time, log T/n, both direction rates,
   fluxes and cumulatives, with explicit per-direction applicability statuses.
   Encode negative infinity as a tagged string/status in valid JSON, never
   conflate it with support zero or an absent reverse beta channel. No rate
   quadrature, event recomputation, propagator or sweep is called.

All comparisons must report raw values, residuals and tolerances. Negative
controls must be recorded as expected rejections, not product failures. Use
NumPy with the existing Python runtime; no dependency changes. CPU limit60 s,
working data256 MiB, exactly zero ODE/IVP calls. Record wall/CPU time and RSS.
Do not rerun old C1, bootstrap, RR grid campaign, full pilot or nuclear sweep.

The scientific controller owns this contract, theoretical interpretation and
final admission. The lower-tier worker owns code, prescribed execution and
mechanical evidence. One independent Astra review follows the observed diff
and outputs. A concrete defect permits one targeted repair; otherwise stop
verification and publish the scoped result. Missing physical closure does not
block this finite diagnostic. C2 PASS leads directly to C3 numerical design
of the conditional local source adapter, retaining unresolved physical inputs.
