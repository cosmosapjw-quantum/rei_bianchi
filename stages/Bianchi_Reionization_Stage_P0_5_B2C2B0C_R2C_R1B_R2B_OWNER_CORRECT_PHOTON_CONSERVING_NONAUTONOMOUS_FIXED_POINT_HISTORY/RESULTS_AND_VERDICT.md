# Results and verdict — R1B-R2B

## Provenance of this workspace

This stage was rebuilt under Case C. The `d60c7f7…` workspace named in
transcript does not resolve in any durable ref of `rei_bianchi`, `rec_bianchi`
or `htt_base`, is absent from the reflog and from all remote refs, and is
referenced by no file in the tree. It was therefore **not inherited**. The
workspace was recreated from the durable R1B-R2A pass
(`47df6c5d`, tag `checkpoint-b2c2b0c-r2c-r1b-r2a-owner-split-pass`) and the
input lock regenerated from files present at `e11dcb56`.

The implementation below was authored in-session under RED–GREEN, not produced
by the upstream research pipeline. It is offered for external cross-validation,
not as an independently validated result.

## What passed

The three required RED gates were written first, watched fail, then made to
pass with minimal implementations.

### Owner conservation

`sum_o N_gamma,g,o^abs = N_gamma,g^abs,tot` holds on canonical data with

```text
max owner closure relative residual = 1.47775955132743e-16
```

over 20 group cases and 60 owner rows drawn from `CANONICAL_DIRECT_REEVOLVED`
(5 intervals x 4 groups; 5 further cases carry exactly zero component support
and zero authoritative total, and are recorded as such rather than skipped).

`S_resolved[EFFECTIVE_HI_SUBGRID] = (0, 0, 0)` held on every owner row:

```text
exact-zero subgrid resolved-source violations = 0
```

The zeros are exact integer-flag products, not tolerances.

### Positive H/He chemistry

Nuclei totals are conserved *by construction*: the partner species is obtained
by subtraction from the locked total, so `N_HI + N_HII = N_H` and
`N_HeI + N_HeII + N_HeIII = N_He` cannot drift. Positivity is enforced by
refusing infeasible demand — `InfeasibleReaction` carries the offending species.
There is no clipping on any code path.

### Transaction

Failed fixed-point attempts, rejected substeps and event rollbacks all leave the
accepted state and ledger **byte-identical**, asserted against a canonical byte
image using `repr` floats so that a one-ulp residue would fail. Rejections are
appended to `failed_attempts` rather than erased.

### Refinement matrix

Budget additivity at `dt, dt/2, dt/4, dt/8` on canonical data:

```text
max refinement relative delta = 0.0
```

Exactly zero, as the formalism predicts for an exactly integrated forcing. This
is a budget-additivity result, not a chemistry convergence claim.

### Separate ledgers

All ten ledgers are kept independent, with owner routing by exact table lookup
so the subgrid owner has no code path into a resolved account.

Test totals: 40 new stage tests, 120 in the full repository suite, all passing
with the pinned optional `jax==0.9.0.1` present.

## What did not run, and why

**The stage cannot be closed as a production photon-conserving nonautonomous
fixed-point history.** Two independent obstructions:

1. **No locked initial material state.** The durable inputs carry no
   `(N_HI, N_HII, N_HeI, N_HeII, N_HeIII, U_resolved)` vector. The fixed macro
   parcel template holds statistical weights, not species counts. Supplying one
   would be a fabricated initial condition.

2. **No identified nonautonomous fraction law.** R1B-R1 fail-closed established
   that the durable inputs do not identify a state-derived dynamic-opacity
   operator, and the input lock forbids the `kappa = J/Phi` inversion that would
   manufacture one. The locked component table yields a per-interval *frozen*
   law, which is autonomous within a slab. The implemented loop accepts an
   injected state-dependent law and reaches a fixed point under one — that
   capability is verified by test — but no such law exists in the durable
   inputs to supply it.

The slab loop, the positivity certificate and the transactional history are
therefore delivered as a **verified operator with closed gates**, exercised on
canonical data for the photon side only.

## Verdict

```text
DURABLE_FAIL_CLOSED_R2C_R1B_R2B_OWNER_CORRECT_OPERATOR_VERIFIED_BUT_NO_LOCKED_MATERIAL_STATE_AND_NO_IDENTIFIED_NONAUTONOMOUS_LAW
```

- owner-correct photon pipeline on canonical data: **pass**
- owner conservation, exact-zero subgrid, positivity, transaction, refinement gates: **pass**
- production photon-conserving nonautonomous fixed-point history: **not integrated**
- science promotion: **false**
- R1B-R2B completed: **false**
- production node chemistry, R2C-R2, B2C2B: **false**
- independent external cross-validation: **required**

## What would unblock R1B-R2B

A durable initial material state vector, and a state-derived opacity/partition
law derived from explicit local physics rather than fitted per node — the same
requirement R2C-R1A placed on R1B and R1B-R1 placed on its successor. Neither
can be supplied from inside this stage without violating the input lock.
