# REI-LOCAL-01 Source-Bound Paired-Map Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to execute this plan task-by-task. Use
> `superpowers:test-driven-development` for every behavior change and
> `superpowers:verification-before-completion` before reporting a result.

**Goal:** Implement and locally certify a dependency-preserving full-versus-two-half
MPRK22(1)-Alexander-SDIRK2 map comparison without changing the immutable R2
stage or claiming a canonical pilot/first-interval pass.

**Architecture:** Three new core modules own the immutable affine/Taylor state,
the joint implicit/remainder certificates, and the concrete locked
MPRK22(1)-Alexander-SDIRK2 binding. A new R3 stage persists that state,
runs one full step and two dependent half steps from the same parent, transforms
both endpoints to public coordinates, subtracts them by dependency owner before
interval projection, and passes the result to the unchanged strict controller
policy. Asymmetric endpoint remainder intervals are subtracted outwardly unless
a separately proved direct-delta certificate exists.

**Tech stack:** Python 3.12, NumPy/SciPy, existing MPRK22(1) and Alexander
SDIRK2 primitives, outward interval arithmetic, pytest in the local scientific
environment, canonical JSON plus explicitly ordered typed binary `REIAFF1`
blocks, Git raw-object provenance. NPZ is permitted only for pinned read-only
predecessor fixtures; it is not the canonical `REIAFF1` persistence format.

**Design authority:**
`docs/superpowers/specs/2026-08-30-rei-source-bound-paired-map-adapter-design.md`.

**Claim boundary:** REI-LOCAL-01 may end at
`IMPLEMENTED_AND_LOCALLY_CERTIFIED`. It must keep `canonical_pilot: NOT_RUN`,
`first_interval: NO_PASS`, and `scientific_pass: NOT_CLAIMED`. The 46,080-node
three-lane pilot is a separate REI-LOCAL-02 task.

## Protected inputs

Do not modify:

- any existing path present at PR14 commit
  `053b97c56e089e28a83f37d79a4128ed3cdae9f4`; all imports, registration, and
  integration live only in newly created R3/core paths;
- the existing R2 stage
  `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY/`;
- `external/rec_bianchi.lock.json`;
- old tables, blocked-run archives, manifests, receipts, audit reports, plots,
  or accepted/rejected history;
- strict source binary64 thresholds, controller bisection policy, three-lane
  atomicity, or Richardson policy.

---

### Task 0: Authenticate the handoff and isolate the implementation

**Files:** no repository edits.

- [ ] Run the pinned `FETCH_AND_VALIDATE.py` from the published handoff commit
  with an existing local repository and a new destination outside every Git
  worktree.
- [ ] Require the exact result fields:

  ```json
  {
    "transport_status": "PASS_IMMUTABLE_PAYLOAD_ONLY",
    "scientific_validation": "NOT_RUN",
    "canonical_adapter": "NOT_RUN",
    "pilot_46080x3": "NOT_RUN",
    "first_interval": "NO_PASS",
    "pr14_disposition": "RECORDED_BLOCKED_MINIMUM_STEP"
  }
  ```

  The locator also emits `remote_ref_status` as observational metadata with
  exactly one of `MATCH`, `DRIFT`, or `NOT_CHECKED`; it does not change the six
  immutable/scientific result fields above.

- [ ] Create a new sibling worktree from the exact handoff terminal commit.
  Do not reset, clean, stash, rebase, amend, merge, or reuse a dirty worktree.
- [ ] Record `git rev-parse HEAD`, `git rev-parse HEAD^{tree}`, `git status
  --short`, and `git worktree list --porcelain` before mutation.
- [ ] Starting from the minimum roots named in Tasks 6, 7, and 9, enumerate the
  complete static imported-code, dynamically loaded-code, copied-envelope, and
  opened-data closure (including CSV/NPZ tables and phase-space kernels). Pin
  every explicit path/mode/Git blob/raw SHA-256 in
  `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/INPUT_LOCK.json` only
  after the new stage directory is created in Task 1. The named tables below
  are minimum roots, not a transitive-closure claim; globs are not authority.

**Verification command:**

```bash
python /absolute/path/to/FETCH_AND_VALIDATE.py \
  --repo /absolute/path/to/rei_bianchi \
  --destination /absolute/path/to/rei_intake_20260830
```

Stop on any nonzero exit or any status other than the six values above.

---

### Task 1: Lock dependency ownership with a RED unit fixture

**Create:**

- `src/rei_bianchi/correlated_map_adapter.py`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_correlated_map_adapter.py`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/INPUT_LOCK.json`

**Behavior:** An immutable registry accepts unique owner IDs, rejects collisions,
and denies aliases unless a pinned authority record names both owners.

- [ ] Write these tests first:

  ```python
  def test_duplicate_dependency_id_rejects():
      registry = DependencyRegistry.empty()
      registry = registry.register(owner("parent/g0/log_T/7"))
      with pytest.raises(DependencyError, match="DEPENDENCY_ID_COLLISION"):
          registry.register(owner("parent/g0/log_T/7"))


  def test_equal_numeric_sources_with_distinct_ids_do_not_alias():
      left = local_source("source/lane0/a0/full/population_t0/v/7", 0.125)
      right = local_source("source/lane0/a0/half1/population_t0/v/7", 0.125)
      delta = subtract_coefficients({left.owner_id: left.value},
                                    {right.owner_id: right.value})
      assert delta == {left.owner_id: -0.125, right.owner_id: 0.125}


  def test_alias_without_authority_rejects():
      registry = DependencyRegistry.empty()
      left = "source/lane0/a0/full/population_t0/v/7"
      right = "source/lane0/a0/half1/population_t0/v/7"
      registry = registry.register(owner(left))
      registry = registry.register(owner(right))
      with pytest.raises(DependencyError, match="UNAUTHORIZED_SOURCE_ALIAS"):
          registry.alias(left, right, authority=None)
  ```

- [ ] Run the focused tests and capture RED caused by missing production
  symbols, not by import/setup failure.
- [ ] Implement frozen dataclasses `DependencyOwner`, `AliasAuthority`, and
  `DependencyRegistry`; use tuples/read-only arrays at public boundaries.
- [ ] Define stable enum values for every design failure state. Exceptions
  expose a `classification` field and never encode policy in free-form text.
- [ ] Implement owner parsing as an exact schema, not string-prefix matching.
- [ ] Re-run focused tests to GREEN, then refactor only duplicate validation.

**Verification command:**

```bash
PYTHONPATH=src python -m pytest -q \
  stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_correlated_map_adapter.py \
  -k 'dependency or alias'
```

---

### Task 2: Implement immutable affine/Taylor state and same-parent composition

**Modify:**

- `src/rei_bianchi/correlated_map_adapter.py`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_correlated_map_adapter.py`

**Interfaces:**

```python
@dataclass(frozen=True)
class AffineState:
    center: NDArray[np.float64]
    local_site_blocks: tuple[LocalSiteBlock, ...]
    global_blocks: tuple[GlobalGeneratorBlock, ...]
    remainders: tuple[AxisAlignedRemainderBlock, ...]
    registry: DependencyRegistry
    topology: TopologyIdentity
    event_certificates: tuple[EventCertificate, ...]
    population_certificates: tuple[PopulationImplicitCertificate, ...]
    thermal_certificates: tuple[ThermalImplicitCertificate, ...]
    remainder_certificates: tuple[StepRemainderCertificate, ...]
    rounding_certificates: tuple[OutwardRoundingReceipt, ...]
    integrated_ledger_certificates: tuple[IntegratedLedgerCertificate, ...]


def run_affine_step(
    parent: AffineState,
    t0: float,
    t1: float,
    ownership: StepOwnership,
    operator: AffineStepOperator,
) -> AffineStepResult:
    """Validate the protocol call and delegate one leg to operator.run_affine_step."""
    pass


def run_paired_map(
    parent: AffineState,
    t0: float,
    t1: float,
    operator: AffineStepOperator,
) -> PairedMapResult:
    pass
```

- [ ] Write RED tests that assert:

  - full and first-half receive the exact same immutable parent object/hash;
  - second-half input contains every owner present in the first-half output;
  - deleting one first-half remainder produces
    `FIRST_HALF_DEPENDENCY_DROPPED`;
  - full, half1, and half2 source-site IDs remain distinct;
  - the same-site `vf` block ranges its four coupled corners and is not treated
    as an independent generator;
  - all public NumPy arrays are non-writeable and caller arrays cannot mutate a
    constructed state.

- [ ] Confirm meaningful RED by temporarily using a Cartesian-box fake that
  drops first-half owners.
- [ ] Implement state validation, immutable array copying, exact owner-set
  inheritance, and same-parent orchestration.
- [ ] Keep one schedule owner: `AffineStepOperator.run_affine_step` owns the
  four-site per-leg physics; this adapter function is a thin protocol/type/
  inheritance validator and delegate. `run_paired_map` alone owns the
  full/half1/half2 composition.
- [ ] Do not import the existing interval-map endpoint wrapper into this core
  module; connect the real operator only in Task 6.
- [ ] Run GREEN and the Task 1 regression set.

**Verification command:**

```bash
PYTHONPATH=src python -m pytest -q \
  stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_correlated_map_adapter.py \
  -k 'parent or half or site or mixed or immutable'
```

---

### Task 3: Transform to public coordinates and subtract before projection

**Modify:**

- `src/rei_bianchi/correlated_map_adapter.py`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_correlated_map_adapter.py`

**Interfaces:**

```python
def to_public_model(
    state: AffineState,
    certificate: PublicTransformCertificate,
) -> PublicAffineState:
    pass


def subtract_public(
    half: PublicAffineState,
    full: PublicAffineState,
    direct_delta: DirectDeltaCertificate | None = None,
) -> PublicAffineDelta:
    pass


def project_delta(delta: PublicAffineDelta) -> PublicIntervalBox:
    pass
```

- [ ] Write RED tests for the exact nonlinear helium identities
  `x_HeII=(1-x_HeI)*(1-r)` and `x_HeIII=(1-x_HeI)*r` using hand-computed
  rational corner values.
- [ ] Reconstruct `x_HII=1-x_HI`. Create the nonlinear helium remainder on
  `x_HeIII` and reconstruct `x_HeII=1-x_HeI-x_HeIII` with the same remainder
  owner/opposite sign (or an equivalent sum-zero constrained block). Require
  exact H/He sums for every generator/remainder realization; independently
  owned HeII/HeIII remainder mutations reject.
- [ ] Prove the test fails when internal coordinates are subtracted before the
  public transform.
- [ ] Define `AxisAlignedRemainderBlock` as an asymmetric outward offset
  interval `[lower, upper]`. Write RED tests showing shared public coefficients
  cancel, distinct IDs do not cancel, and endpoint remainders subtract as
  `[H_lower-F_upper, H_upper-F_lower]` when no direct-delta certificate exists.
- [ ] Add an asymmetric remainder with nonzero midpoint; serialize/recenter it
  and prove no midpoint is silently discarded.
- [ ] Require a valid independent `DirectDeltaCertificate` before replacing
  the conservative endpoint remainder difference.
- [ ] Add strict-threshold tests at both `float(2e-4).hex()` local-error
  equality and `float(2e-3).hex()` public-width equality; each rejects with its
  exact gate classification because the policies are strict less-than.
- [ ] Use `research/continuation_20260830/paired_budget.py` only as a scalar
  differential oracle in tests. Do not make it the runtime representation.
- [ ] Implement public-coordinate polynomial propagation, same-site corner
  ranging, difference-first subtraction, and final outward projection.

**Verification command:**

```bash
PYTHONPATH=src python -m pytest -q \
  stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_correlated_map_adapter.py \
  -k 'public or helium or delta or remainder or threshold'
```

---

### Task 4: Certify population implicit stages and generator tangents

**Create:**

- `src/rei_bianchi/joint_implicit_remainder.py`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_joint_implicit_remainder.py`

**Interfaces:**

```python
def certify_population_stage(
    residual: PopulationResidual,
    enclosure: PopulationTube,
    generators: GeneratorBatch,
) -> PopulationImplicitCertificate:
    pass


def propagate_implicit_generators(
    certificate: PopulationImplicitCertificate,
    generators: GeneratorBatch,
) -> GeneratorBatch:
    pass
```

- [ ] Build a literal 2x2 H and 3x3 He fixture with a hand-computed midpoint
  inverse and outward interval bounds.
- [ ] Write RED tests requiring strict Krawczyk self-inclusion of the actual
  full 2x2 H and 3x3 He systems. Do not delete a conserved row before
  Krawczyk.
- [ ] After full-system certification, map to
  `(x_HI, x_HeI, r_HeIII)` and require H/He generator and remainder sums to be
  exactly zero after the structured public reconstruction, generator by
  generator and remainder realization. Require `q_He,ion=1-x_HeI > 0` over the
  complete enclosure before constructing `r_HeIII`.
- [ ] Mutate one denominator interval to include zero and require
  `POPULATION_DENOMINATOR_NONPOSITIVE`.
- [ ] Mutate the tangent solve by dropping `(delta A) * Z` and require the
  fixture to fail its hand-computed tangent result.
- [ ] Implement interval residual/Jacobian evaluation and the full-system
  `A*delta_Z=delta_b-(delta_A)*Z` solve for every named generator; only then
  apply analytic conservation reconstruction/projection.
- [ ] Bind every resulting coefficient and remainder to its original owner ID.

**Verification command:**

```bash
PYTHONPATH=src python -m pytest -q \
  stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_joint_implicit_remainder.py \
  -k 'population or denominator or tangent'
```

---

### Task 5: Certify the whole thermal residual and nonlinear step remainder

**Modify:**

- `src/rei_bianchi/joint_implicit_remainder.py`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_joint_implicit_remainder.py`

**Interfaces:**

```python
def certify_whole_thermal_stage(
    residual: WholeThermalResidual,
    temperature_tube: ScalarTube,
    context_tube: ThermalContextTube,
    generators: GeneratorBatch,
) -> ThermalImplicitCertificate:
    pass


def certify_step_remainder(
    stages: tuple[ImplicitStageCertificate, ...],
    hessian_bounds: HessianVectorBounds,
    rounding: OutwardRoundingReceipt,
) -> StepRemainderCertificate:
    pass
```

- [ ] Create an independently solvable nonlinear scalar residual in
  `tests/fixtures/nonlinear_thermal_fixture.json`; store literal coefficients,
  a rational containing tube, and independently computed root bounds.
- [ ] Write RED tests that detect removal of the temperature-dependent
  photoheating derivative.
- [ ] Require `THERMAL_DERIVATIVE_CONTAINS_ZERO` if the derivative tube includes
  zero and `THERMAL_CONTEXT_NOT_SELF_INCLUDED` if an outer context tube fails to
  self-include.
- [ ] Reject a midpoint-only Jacobian when no outward nonlinear remainder is
  attached.
- [ ] Include state-dependent rates/cooling, owner normalization feedback,
  cross-site composition, thermal-root curvature, and floating-point outward
  error in `StepRemainderCertificate`.
- [ ] Ensure every remainder has a nonempty provenance owner and a source
  certificate hash plus an available authenticated certificate payload.

**Verification command:**

```bash
PYTHONPATH=src python -m pytest -q \
  stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_joint_implicit_remainder.py \
  -k 'thermal or context or nonlinear or rounding or provenance'
```

---

### Task 6: Bind the concrete source-bound MPRK22/SDIRK2 operator

**Create:**

- `src/rei_bianchi/source_bound_mprk_sdirk_operator.py`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_source_bound_mprk_sdirk_operator.py`

Define these exact repo-relative predecessor constants in `INPUT_LOCK.json` and
`runtime_contract.py`:

```text
SPARSE_STAGE=stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_SPARSE_LOCAL_GENERATOR_AFFINE_TAYLOR_MODEL_ENCLOSURE_LOCK
CONTINUOUS_STAGE=stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_VALIDATED_CONTINUOUS_BRANCH_DIFFERENTIAL_INCLUSION_ENCLOSURE_LOCK
IMPLICIT_STAGE=stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_EVALUATION_SITE_SPARSE_GENERATOR_VALIDATED_MPRK22_SDIRK2_DISCRETE_MAP_ENCLOSURE_LOCK
FOUR_CORNER_STAGE=stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_FOUR_CORNER_BRANCH_AND_UNRESOLVED_OTS_ENERGY_PROPAGATION_PREFLIGHT
SDIRK_STAGE=stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R1_POSITIVITY_CONSERVATIVE_SECOND_ORDER_THERMOCHEMISTRY_PREFLIGHT
CROSS_SITE_STAGE=stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK
```

At source commit `053b97c56e089e28a83f37d79a4128ed3cdae9f4`, pin these
minimum load-bearing roots exactly. This table is not the complete transitive
code/data closure required by Task 0:

| Authority | Git blob | Raw SHA-256 |
|---|---|---|
| `SPARSE_STAGE/analysis/evaluation_site_contract.py` | `9820ee4993c9102c14dc6d6cd4d91896974a6d8d` | `10973cadf793a94adf0681eae9d2382269b05996bb41b8c1e1b6c7d5fafc1143` |
| `SPARSE_STAGE/analysis/source_generators.py` | `7ae47387d1446aae10337a446771b5a94be95843` | `7b0bbdd3880e1219638847ed1df1829814e95b1f665839cd80bbb3c4b4a2b130` |
| `SPARSE_STAGE/analysis/global_coupling.py` | `721676551e8418082ca1f8c119324b5ec9cea32f` | `6e3e9cb91cf0d8891ac73ee506c527726632eb6b1b59854e11252badbb7c712e` |
| `SPARSE_STAGE/analysis/temporal_control_audit.py` | `617711033236ae57ce9a40742491814070cfba18` | `b035dc197b51397ccae8406bd77dd5d00241afe65c7346ddb6d4405733c304fe` |
| `CONTINUOUS_STAGE/analysis/reduced_interval_rhs.py` | `57f71d6aef1918c771e673afee0c608f426cad35` | `b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36` |
| `CONTINUOUS_STAGE/analysis/interval_arithmetic.py` | `7a5fd472426678fa014c0f1148765df99447e662` | `ea8383f8f4bc0d463d9908af9baa4743ad80e125b60d22991028b4d57a10ec22` |
| `CONTINUOUS_STAGE/analysis/pchip_bounds.py` | `b12d298c1c42059a8c0596a0ae591d4701f5c9a9` | `a3e5771a8d4bed54395b9ab671bfededc539bdfbc153f59149960f26ace47d37` |
| `IMPLICIT_STAGE/analysis/implicit_certificates.py` | `52538eefb3b1bb41a289d7c6d03794160b88d64c` | `197aee751933a9b80c97453e55ecb9f0a346f8c85198715841ea2255c4e1c185` |
| `FOUR_CORNER_STAGE/analysis/uncertainty_trial.py` | `e6f96cd53f3e66e3334adee792ff33154c55833d` | `c9a9117a68d1e2f9c6fbd8bb2004a1bd6e5ef4ee14653e58a2bd9ccf05d4a8c9` |
| `FOUR_CORNER_STAGE/analysis/uncertainty_policy.py` | `b5c065ed50c2724a81f6d5d3f24a600d61558896` | `06b84d532774c60518826ffe06d3fc494a22477edbdca46217f371e6781cadbe` |
| `FOUR_CORNER_STAGE/analysis/event_uncertainty_operator.py` | `765f2cb2957c0466a5cf0bde15a55e5a2ed5e0f3` | `b9cb365989149a4368b6a257e15cabf8e07c522419bd2328401c90d2fe49ce5d` |
| `SDIRK_STAGE/analysis/second_order_sdirk_fast_trial.py` | `34483b130bc0538f2a10a89b1a86fd5191d13318` | `de2a5a2e76c77e4f1f6239fdd7563c849faab9d88957b270c1702f6c560eba20` |
| `CROSS_SITE_STAGE/analysis/cross_site_discrete_map.py` | `1cc104060c013db75d2a56e7ddf4b9a17652a8c6` | `cbb068ae640ded0ab9467e0d58ed6e5a3fa0266ac26f8dc5bb1a399fe9902a07` |
| `CROSS_SITE_STAGE/analysis/interval_discrete_map.py` (comparison oracle only) | `ca2676c84b3c93766c59aa3ef81740565226dad9` | `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644` |

- [ ] Before implementation, finalize and independently review an explicit
  `INPUT_LOCK.json` closure for every statically imported, dynamically loaded,
  copied, or opened code/data authority reachable from these roots. Instrument
  tests so any undeclared runtime import/open rejects; no runtime discovery may
  silently extend authority.
- [ ] Use the pinned binary64-nextafter `interval_arithmetic.py` and certified
  `pchip_bounds.py` layer for every interval primitive and accumulation, or
  replace it only with an explicitly pinned equivalently verified layer. A
  single final `nextafter` around ordinary NumPy/SciPy arithmetic is not a
  certificate. Compare primitive and accumulated bounds against independent
  long-double/high-precision oracles, including adversarial cancellation and
  table-knot cases.

**Interfaces:**

```python
@dataclass(frozen=True)
class EvaluationSiteRequest:
    leg: StepLeg
    site: EvaluationSite
    t: float
    state: AffineState
    ownership: StepOwnership


@dataclass(frozen=True)
class AffineEventModel:
    population_flux: AffineBlock
    base_photoheat: AffineBlock
    resolved_ots_heat: AffineBlock
    thermal_photoheat: AffineBlock
    unresolved_ots: AffineBlock
    escaped: AffineBlock
    chemical: AffineBlock
    photon_identity: AffineBlock
    forcing: AffineBlock
    owners: DependencyRegistry
    certificate: EventCertificate


class LockedMPRK22SDIRK2Operator:
    @classmethod
    def from_repo(cls, repo_root: Path, input_lock: Path): ...
    def evaluate_site(self, request: EvaluationSiteRequest) -> AffineEventModel: ...
    def certify_population_stage(self, ...): ...
    def certify_thermal_stage(self, ...): ...
    def integrate_ledgers(
        self,
        evaluations: StepSiteEvaluations,
        parent: AffineState,
        endpoint: AffineState,
        dt: float,
    ) -> IntegratedLedgerModel: ...
    def run_affine_step(self, ...) -> AffineStepResult: ...
```

- [ ] Make `run_affine_step` own the exact `population_t0`,
  `population_t1_predictor`, `thermal_tgamma`, and `thermal_t1_final`
  physical owner classes for every full/half leg, with no extra or omitted
  named site. This is not a limit of four numerical calls: validated
  nonlinear/root iterations may reevaluate within one named site while keeping
  its site owner law.
- [ ] Certify every implicit substage: t0 Patankar-Euler population predictor,
  backward-Euler thermal predictor, MPRK22 population corrector, gamma Patankar
  population stage, and coupled SDIRK2 gamma/final thermal roots. Every
  population solve and thermal predictor/gamma/final residual uses its
  source-bound full enclosure; point/frozen-context thermal predictors reject.
- [ ] Gate the complete physical state cone at every parent, predictor,
  implicit substage, endpoint, and public transform: finite `logT`, outward
  finite `T=exp(logT)>0`, required `[0,1]`/strict-interior fractions,
  `q_He,ion>0`, `r_HeIII in [0,1]`, nonnegative reconstructed species, and
  positive particle/energy factors. Boundary mutations emit
  `PHYSICAL_STATE_CONE_FAILURE`.
- [ ] Make `StepSiteEvaluations` contain all four authenticated site models,
  owners, and forcing. Photon/owner ledgers use `population_t0` plus
  `population_t1_predictor`; OTS/thermal ledgers use `thermal_tgamma` plus
  `thermal_t1_final`. Mutating away any one site must fail ledger construction.
- [ ] Define `thermal_photoheat = base_photoheat + resolved_ots_heat` exactly
  once. Add `resolved_ots_heat` to the resolved ledger exactly once;
  `unresolved_ots` is ledger-only and never enters the resolved thermal state.
  Drop/double-add/injection mutations must reject.
- [ ] Recompute each site's coefficients and asymmetric remainders from its own
  state, time, forcing, and ownership. Use
  `source_generators.build_source_rhs_taylor()` and
  `global_coupling.audit_global_coupling()` as initial-state characterization
  oracles, never as reusable later-site runtime operators.
- [ ] Certify before division every Patankar, `q_He,ion`, particle/energy,
  owner-normalization/raw-absorption, OTS (`y`, `z`, `y2`), and forcing
  denominator over the full enclosure. Zero-containing/nonfinite inputs emit
  `SOURCE_NORMALIZATION_DENOMINATOR_NONPOSITIVE` (or the narrower population
  class) before any coefficient or remainder is constructed.
- [ ] Keep `CROSS_SITE_STAGE/analysis/interval_discrete_map.py` as a pinned
  point-degenerate parity and interval-containment oracle only. Add a test that
  runtime import of that wrapper is absent.
- [ ] Write these RED behaviors before implementation:

  ```text
  test_exact_four_sites_per_leg_and_no_extra_sites
  test_leg_site_owner_ids_distinct_but_parent_ids_shared
  test_each_event_flux_photoheat_and_ledger_uses_same_site_state
  test_resolved_ots_heat_enters_thermal_and_ledger_exactly_once
  test_unresolved_ots_never_enters_resolved_thermal_state
  test_later_sites_recompute_instead_of_reusing_t0_coefficients
  test_each_implicit_substage_has_authenticated_certificate
  test_thermal_predictor_is_full_enclosure_not_point_or_frozen_context
  test_physical_state_cone_rejects_each_boundary_crossing
  test_second_half_consumes_complete_first_half_state
  test_locked_operator_point_degenerate_matches_physical_map_all_lanes
  test_each_local_operation_and_remainder_contains_locked_oracle_realizations
  test_all_division_denominators_certify_before_construction
  test_integrated_ledgers_share_dependency_registry_and_close_jointly
  test_ledger_construction_rejects_when_each_required_site_is_dropped
  test_marginal_ledger_zero_without_common_owner_realization_rejects
  test_table_event_rejects_without_candidate_mutation
  test_earliest_table_event_localizes_rebuilds_topology_and_restarts
  test_nonmonotone_or_uncertified_event_tube_fails_closed
  test_unpinned_predecessor_hash_rejects
  test_interval_wrapper_is_reference_only
  ```

- [ ] `IntegratedLedgerCertificate` must prove generator-by-generator
  identities plus an outward remainder containing exact zero, or one joint
  feasible residual-vector enclosure/self-inclusion. Independent marginal
  zero-containment is not acceptance.
- [ ] Localize the earliest validated Hummer-Shull table event, reject without
  candidate mutation, rebuild the fixed topology, and restart. A non-monotone
  or uncertified event tube emits `TABLE_EVENT_LOCALIZATION_FAILURE`; it is not
  silently advanced.
- [ ] Return events, population/thermal/remainder/rounding certificates, the
  shared dependency registry, and integrated ledgers in `AffineStepResult`.

**Verification command:**

```bash
PYTHONPATH=src python -m pytest -q \
  stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_source_bound_mprk_sdirk_operator.py
```

---

### Task 7: Lock real-node RED and point-degenerate parity fixtures

**Create:**

- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/analysis/build_locked_fixtures.py`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/fixtures/locked_node_38382.json`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_real_node_red.py`

- [ ] Authenticate the predecessor witness at source commit
  `053b97c56e089e28a83f37d79a4128ed3cdae9f4` before extracting data:

  ```text
  SPARSE_STAGE/RESULTS_AND_VERDICT.md
    blob dace03c1478c36e728078f21bcb27eaf7dba9d7d
    sha256 481da31e05ca543b0c21df360d42993b8efe92071160d518280ed57276562a96
  SPARSE_STAGE/data/temporal_control_lanes.json
    blob aa68aa8a2761d6a89405c2e2edfc87ac3bda8cca
    sha256 c323641d38012bf83806c7f26bc986a7e84554737f5d1b6fcb833ec2c11371e2
  SPARSE_STAGE/analysis/temporal_control_audit.py
    blob 617711033236ae57ce9a40742491814070cfba18
    sha256 b035dc197b51397ccae8406bd77dd5d00241afe65c7346ddb6d4405733c304fe
  ```

  The authenticated JSON must name node `38382` and `x_HeIII` in all three
  lanes, and the verdict must bind the upper-before-half/lower-after-half
  schedule. Any discrepancy is `PROVENANCE_REBIND_REQUIRED`, not a new witness.
- [ ] Make `build_locked_fixtures.py` authenticate and extract only the pinned
  predecessor witness/full-field context: node `38382`, all four
  source-evaluation sites, all three lanes, the upper-then-lower schedule, and
  point-degenerate lower-corner inputs. It must not import or call the new
  operator while generating expected bytes; the test separately feeds the
  frozen fixture to `LockedMPRK22SDIRK2Operator`.
- [ ] Retain and pin the full 46,080-node absorption/owner-normalization
  aggregates and global low-rank context while evaluating the bounded
  node-local propagation. Alternatively execute the locked full-field fixture
  and assert only node `38382`. Never renormalize a one-node slice; a mutation
  that does so must reject.
- [ ] Write the exact source paths and SHA-256 values into the fixture. Refuse
  generation if any predecessor hash differs from `INPUT_LOCK.json`.
- [ ] Write a RED test reproducing the recorded static-hull escape in
  `x_HeIII`, then require the source-bound model to contain the same schedule.
- [ ] Write point-degenerate parity tests for state, temperatures, event
  identities, and every ledger in all three lanes.
- [ ] Require this bounded locked-context output to carry
  `scientific_pass: NOT_CLAIMED` and `canonical_pilot: NOT_RUN`.
- [ ] Do not derive expected values with the adapter under test; freeze them
  from the independently executed predecessor/fixture builder.

**Verification commands:**

```bash
PYTHONPATH=src python \
  stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/analysis/build_locked_fixtures.py \
  --verify-only
PYTHONPATH=src python -m pytest -q \
  stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_real_node_red.py
```

---

### Task 8: Add deterministic `REIAFF1` persistence and split restart

**Create:**

- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/analysis/affine_state_io.py`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_affine_state_io.py`

- [ ] Specify `REIAFF1` with canonical JSON metadata and explicitly ordered,
  typed little-endian binary blocks. Include schema, topology, registry,
  aliases, local/global/mixed coefficients, asymmetric remainder bounds and
  owners, complete event/population/thermal/remainder/rounding/ledger
  certificate payloads, their hashes, and the public envelope. A certificate
  may be content-addressed only when its authenticated sidecar is mandatory and
  present at load.
- [ ] Write RED tests for byte-deterministic save/load/save, truncated input,
  duplicate owner IDs, unknown block types, nonfinite values, and certificate
  hash mismatch.
- [ ] Write a split-restart test: run half1, serialize, load in a fresh process,
  run half2, and compare the complete state and certificate graph in
  `PairedMapResult` to an uninterrupted run.
- [ ] Delete and tamper each certificate payload/sidecar in turn and require
  `CERTIFICATE_PAYLOAD_MISSING` or `CERTIFICATE_PAYLOAD_AUTH_FAILURE` before
  restart execution.
- [ ] Reject `REIADP1` unless the caller explicitly requests
  `CONSERVATIVE_PARENT_BOX_LIFT`; mark every new parent dependency as an
  independent conservative owner.
- [ ] Never call that lift recovered covariance.

**Verification command:**

```bash
PYTHONPATH=src python -m pytest -q \
  stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_affine_state_io.py
```

---

### Task 9: Integrate a new R3 worker without changing R2 policy

**Create:**

- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/analysis/attempt_worker.py`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/analysis/runtime_contract.py`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_worker_protocol.py`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_runtime_contract.py`

Use this exact copied-envelope authority root:

```text
R2_STAGE=stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY
```

| Minimum R2 authority | Git blob | Raw SHA-256 |
|---|---|---|
| `R2_STAGE/analysis/adaptive_policy.py` | `8b37c11f5698fa255ab8e111ed555aa9dab6f211` | `c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9` |
| `R2_STAGE/analysis/attempt_worker.py` | `20f6175935d5635b02f6e7075ba354309615421a` | `0e507c7bc73e4cdcff7c3a55d20ea7afb78fc6ef925bef891029281ccf904671` |
| `R2_STAGE/analysis/state_io.py` | `4902e23d6215e58f335ac25e3e5e5700d96bda97` | `a8c151c9c1ce32f1e544b205ccffec1b4f8c6bdcaac4cb3685d42488c05c40a1` |
| `R2_STAGE/analysis/runtime_contract.py` | `5d6bd2dc4d1d45a02e41b5a686c8e41953b1bb72` | `092165390da33512d034851835d31244e90254edf3c780e308a0abc04279e3ad` |
| `R2_STAGE/analysis/run_adaptive_history.py` | `07347beb0fea0b8fcff5be71d2620c9dd41a2f6c` | `1517670e937ab06b3baa7aa97b67935633fc6a85792a9a5a626796bd04ab6320` |

These are copied/imported minimum roots, not the complete closure. Task 0's
explicit lock includes every additional authority even when R3 copies rather
than imports it.

- [ ] Copy only the external worker envelope/protocol required for
  compatibility; instantiate `LockedMPRK22SDIRK2Operator` and call
  `run_paired_map` instead of the R2 Cartesian endpoint comparison.
- [ ] Require estimator schema `SOURCE_BOUND_PAIRED_MAP_V1` in every success or
  failure envelope.
- [ ] Preserve the source binary64 `2e-4` strict local gate, `2e-3` strict public
  width gate, all-three-lane atomic decision, minimum one tick, bisection,
  rollback, and event restart classifications.
- [ ] Write RED protocol tests showing an interval-only candidate rejects unless
  it carries the explicit conservative lift classification.
- [ ] Write transaction tests proving every rejected outcome leaves the parent
  state, accepted history, and all ledgers byte-identical.
- [ ] Pin all three new core modules, `affine_state_io.py`, the worker, every imported
  predecessor file, and `INPUT_LOCK.json` in `runtime_contract.py`.
- [ ] Add mutation tests that drop the first-half remainder, alias two source
  sites, freeze photoheat, reverse `H-F`, relax `<` to `<=`, and emit acceptance
  from one lane. Apply and detect the `<` to `<=` mutation independently at
  both the `2e-4` local-error gate and `2e-3` public-width gate. Every mutant
  must be detected numerically or by protocol.

**Verification commands:**

```bash
PYTHONPATH=src python -m pytest -q \
  stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_worker_protocol.py \
  stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests/test_runtime_contract.py
```

---

### Task 10: Run the bounded local certification ladder

**Create:**

- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/LOCAL_CERTIFICATION.json`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/TESTS.log`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/MANIFEST.sha256`

- [ ] Run all new stage tests in a fresh process.
- [ ] Run directly affected predecessor tests for implicit certificates,
  interval arithmetic, event localization, worker protocol, persistence, and
  controller policy. Do not run unrelated historical full suites for
  reassurance.
- [ ] Run the independently solved nonlinear fixture and real node `38382` RED
  in all three lanes.
- [ ] Perform only the bounded node-38382 propagation against its authenticated
  full-field aggregate/global context (or the locked full-field fixture with
  only node 38382 asserted). Do not infer all-node certification or run the
  canonical all-46,080-node pilot.
- [ ] Record every command, interpreter/dependency version, exit code, test
  count, and mutation result in `TESTS.log`.
- [ ] Record status exactly as:

  ```json
  {
    "adapter": "IMPLEMENTED_AND_LOCALLY_CERTIFIED",
    "canonical_pilot": "NOT_RUN",
    "first_interval": "NO_PASS",
    "scientific_pass": "NOT_CLAIMED",
    "performance": "NONE"
  }
  ```

- [ ] If any certificate or gate fails, replace the adapter status with the
  earliest exact failure classification. Never preserve a stale pass field.
- [ ] Generate a manifest over only the new R3/core evidence and verify it from
  raw bytes.

**Verification commands:**

```bash
PYTHONPATH=src python -m pytest -q \
  stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/tests
python scripts/verify_repo.py
git diff --check
git status --short
```

---

### Task 11: Independent dual audit and delivery checkpoint

**Create:**

- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/PHYS_MATH_AUDIT.md`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/PHYS_MATH_CODE_AUDIT.md`
- `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/NEXT_STAGE_PROMPT.md`

- [ ] Request an independent PHYS-MATH review first. It must audit the domain
  model, same-parent semantics, public transformation, whole thermal residual,
  remainder proof, events, and simultaneous ledgers.
- [ ] Request an independent PHYS-MATH-CODE review second. It must trace every
  claim to executable code/tests and inspect dependency IDs, persistence,
  mutation detection, transaction rollback, and protected-input hashes.
- [ ] Permit at most one bounded P0/P1 repair. Re-run only affected tests plus
  the full new-stage suite after that repair.
- [ ] Recompute the manifest and re-run raw-byte verification after the last
  change.
- [ ] Compare the final tree to the implementation base and require an exact
  allowlist of the three new core modules, the new R3 stage, and the approved
  design/plan/handoff documents.
- [ ] Publish only a stacked draft PR. Do not merge, mark ready, enable
  auto-merge, move an existing branch, or update PR14/PR18.
- [ ] Set `NEXT_STAGE_PROMPT.md` to REI-LOCAL-02 only if every local criterion
  passes. It must require all 46,080 nodes and all three lanes and must continue
  to deny a first-interval claim until that separate pilot passes.

## Final verification record

Before reporting REI-LOCAL-01 complete, retain:

- the RED and GREEN command for every behavior slice;
- fresh new-stage and directly affected regression results;
- mutation outcomes for dependency drop, false alias, frozen photoheat,
  reversed difference, threshold relaxation, and one-lane acceptance;
- protected-input before/after hashes;
- deterministic `REIAFF1` restart receipt;
- both independent audits and the bounded repair record;
- exact commit, tree, manifest blob, changed-path allowlist, draft PR head/base,
  and CI readback.

Anything missing from that record is an explicit gap, not an inferred pass.
