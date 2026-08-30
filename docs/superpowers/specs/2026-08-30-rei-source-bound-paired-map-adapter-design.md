# REI-LOCAL-01 Source-Bound Paired-Map Adapter Design

## Status

Approved for implementation planning on 2026-08-30. This document specifies a
future scientific implementation; it does not implement the adapter, run the
46,080-node pilot, or change the recorded first-interval verdict.

The immutable intake authority is:

- PR14 source commit `053b97c56e089e28a83f37d79a4128ed3cdae9f4`, tree
  `46a96c789a691d671644685893a552cd9486788d`;
- preserved helper commit `82c67218248cb896019b2bffc590da1260a214fc`;
- immutable continuation payload `70330fa5e833411bfa9337691e5773431ccd5ac3`;
- terminal continuation receipt `1893f12d14b212eb4b6bd637332824f692e6f4b3`.

The current scientific status remains `NO_PASS_FIRST_CANONICAL_INTERVAL`, and
the PR14 disposition remains a recorded `BLOCKED_MINIMUM_STEP` result.

## Goal

Implement a source-bound affine/Taylor adapter for the actual
MPRK22(1)-Alexander-SDIRK2 discrete map so that one full step and two dependent
half steps retain their common-parent dependencies through the complete
population, thermal, event, and ledger calculations. Form the public
two-half-minus-full difference before interval projection and certify every
nonlinear remainder used by the comparison.

The adapter is a prerequisite to, not a substitute for, the all-node
three-lane pilot.

## Audience and operating mode

The audience is the local scientific-code executor and the independent
PHYS-MATH and PHYS-MATH-CODE reviewers. Work occurs in a new R3 stage and new
core modules. The immutable R2 source, evidence, tables, controller policy, and
failure record are read-only inputs.

The implementation mode is fail-closed:

- a missing dependency owner, nonlinear certificate, event restart, or ledger
  inclusion is an explicit rejection;
- resource exhaustion is `UNRESOLVED`, not a proof that the map is inaccurate;
- a locally certified adapter does not authorize a canonical pilot or first
  interval;
- a moving publication branch does not change the identity of the pinned Git
  objects.

## Why the current paths are insufficient

The current `interval_discrete_map.run_step` projects intermediate states to
axis-aligned interval boxes. A wrapper applied after that projection cannot
recover the dependency needed by a paired estimator. The delivered
`research/continuation_20260830/paired_budget.py` is therefore only an exact
scalar bookkeeping oracle: it subtracts declared shared coefficients and adds
independent remainder radii, but it does not construct or certify the map.

The current scalar thermal certificate also freezes photoheating/context at an
evaluation site. The new certificate must cover the complete thermal residual,
including state- and temperature-dependent photoheating/context, or prove a
separate outer context tube that self-includes.

Finally, the existing `REIADP1` persistence format stores lower/upper arrays.
It cannot preserve source identities, affine coefficients, mixed monomials, or
remainder ownership across a restart. R3 needs a new immutable affine-state
protocol.

## Domain representation

### Internal coordinates

Use the invariant-reduced node state

\[
Y_i=(x_{{\rm HI},i},x_{{\rm HeI},i},r_{{\rm HeIII},i},\log T_i).
\]

Here

\[
q_{{\rm He,ion},i}=1-x_{{\rm HeI},i},\qquad
r_{{\rm HeIII},i}=\frac{x_{{\rm HeIII},i}}
{x_{{\rm HeII},i}+x_{{\rm HeIII},i}}.
\]

The complete enclosure must certify `q_He,ion > 0` before constructing or
transforming `r_HeIII`; a point-positive midpoint is insufficient.

Dependent ion fractions are reconstructed analytically:
`x_HII=1-x_HI` and, after the public transform,
`x_HeII=1-x_HeI-x_HeIII`. H and He conserved directions are eliminated rather
than bounded numerically.

### Affine/Taylor state

An immutable `AffineState` owns:

- center values with shape `(4, N)`;
- node-local, source-site linear `v` and `f` generators;
- the exact same-site mixed monomial `vf`;
- separately named low-rank global owner/forcing generators;
- outward axis-aligned nonlinear remainders with explicit provenance;
- topology/event cell identity;
- population, thermal, ledger, and rounding certificates;
- a dependency registry binding every coefficient to one owner ID.

`AxisAlignedRemainderBlock` stores an outward offset interval `[lower, upper]`
relative to the affine polynomial, not a silently symmetrized half-width. The
locked predecessor's asymmetric remainders remain asymmetric. An
implementation may recenter one only by choosing a representable center shift,
outwardly transforming `[lower, upper] - shift`, and recording every arithmetic
and `nextafter` operation in the rounding certificate; the represented real set
must remain unchanged. It must not assume the exact midpoint is representable.

Public H/He remainders are conservation-coupled, never independent
species-axis boxes. The public transform creates the nonlinear helium
remainder on `x_HeIII`, then reconstructs `x_HeII` from
`1-x_HeI-x_HeIII` with the same owner and opposite sign (an equivalent
sum-zero constrained block is permitted). Every generator/remainder
realization must satisfy H and He sums exactly.

### Physical state cone

At the parent, every predictor, every population/thermal implicit substage,
every endpoint, and the public transform, the complete enclosure must certify:

- finite `x_HI`, `x_HeI`, `r_HeIII`, and `logT`;
- fractions in `[0,1]` (strict interior wherever the inherited log/event map
  requires it), `q_He,ion > 0`, and `r_HeIII in [0,1]`;
- nonnegative reconstructed H/He species with exact conserved sums;
- finite `T=exp(logT) > 0` under outward exponential evaluation; and
- positive particle and energy factors used by the thermal map.

Krawczyk self-inclusion or positive denominators alone does not establish this
cone. Any boundary crossing is `PHYSICAL_STATE_CONE_FAILURE` before the state
is used by a later site.

The `vf` term is a mixed monomial of one site's `(v,f)` pair. It is not a third
independent uncertainty coordinate.

Minimum owner namespaces are:

```text
parent/{generation}/{coordinate}/{node}
source/{lane}/{attempt}/{leg}/{site}/{channel}/{node}
global/{lane}/{attempt}/{leg}/{site}/{owner-group}
remainder/{lane}/{attempt}/{leg}/{stage}/{kind}/{coordinate}/{node}
```

Owner aliases are denied by default. An alias requires a pinned source path,
raw-byte hash, and a scientific reason showing that the source authority makes
the two quantities identical. Equal numerical bounds are never evidence of a
shared owner.

## Composition contract

For each lane and attempted interval:

1. Lift the parent into one immutable `AffineState`.
2. Start the full step and first half from that byte-identical dependency
   state.
3. Propagate the first half without projecting it to an interval box.
4. Pass the entire first-half `AffineState` to the second half, including all
   parent, source-site, global, mixed, and remainder owners.
5. Keep full-step and half-step evaluation-site source blocks distinct unless
   an authority-backed alias explicitly joins them.
6. Retain rejected candidates as evidence without mutating the parent,
   accepted history, or ledgers.

The four inherited source-evaluation sites remain explicit:

```text
population_t0
population_t1_predictor
thermal_tgamma
thermal_t1_final
```

No temporal coherence between their branch variables may be invented.
“Four sites” means four named physical site/owner classes per leg, not four
total numerical function calls: validated nonlinear/root iterations may
evaluate repeatedly within one named site while retaining that site's owner
law.

## Module boundaries

### `src/rei_bianchi/correlated_map_adapter.py`

Owns the dependency registry, immutable sparse state representation,
same-parent full/two-half composition, source-site ownership, public-coordinate
transformation, difference-first projection, and paired diagnostics.

Required public interfaces:

```python
lift_parent_box(...) -> AffineState
run_affine_step(parent, t0, t1, ownership, ...) -> AffineStepResult
run_paired_map(parent, t0, t1, ...) -> PairedMapResult
to_public_model(state, certificate) -> PublicAffineState
subtract_public(half, full) -> PublicAffineDelta
project_delta(delta) -> PublicIntervalBox
```

There is one schedule owner: the adapter-level `run_affine_step` performs only
protocol/type/inheritance checks and delegates one leg to
`LockedMPRK22SDIRK2Operator.run_affine_step`; the operator owns the four-site
per-leg physics. Adapter `run_paired_map` alone owns full/half1/half2
composition.

`PairedMapResult` retains the full, first-half, and second-half states; both
public endpoint models; the public delta; every implicit/remainder certificate;
and projection diagnostics. It must not expose an acceptance flag that bypasses
the R3 policy.

### `src/rei_bianchi/joint_implicit_remainder.py`

Owns interval residual/Jacobian evaluation for complete implicit equations,
2x2 H and 3x3 He population Krawczyk certificates, the whole thermal residual
certificate, implicit tangent propagation, and nonlinear remainder creation.

Required public interfaces:

```python
certify_population_stage(...) -> PopulationImplicitCertificate
certify_whole_thermal_stage(...) -> ThermalImplicitCertificate
propagate_implicit_generators(...) -> AffineState
certify_step_remainder(...) -> StepRemainderCertificate
```

Every population denominator must remain strictly positive over the complete
enclosure. Every implicit derivative denominator must exclude zero. A midpoint
Jacobian, successful point solve, or frozen-context scalar root alone is not a
uniform certificate.

Every certificate primitive and accumulation uses the source-pinned
binary64-`nextafter` interval layer and certified PCHIP bounds, or an explicitly
pinned replacement with equivalent proof. Applying one final `nextafter` to an
ordinary NumPy/SciPy calculation is not outward interval arithmetic. Primitive,
accumulated, cancellation, and table-knot cases require independent long-
double/high-precision oracle checks.

Population certification uses the actual full 2x2 H and 3x3 He Patankar
systems; it does not delete a conserved row before Krawczyk inclusion. After a
full-system certificate succeeds, the generator and remainder variations are
mapped to `(x_HI, x_HeI, r_HeIII)` and H/He conservation is checked exactly,
generator by generator. Tangents solve the full
`A delta_Z = delta_b - (delta_A) Z` system before analytic conservation
reconstruction/projection.

For thermal stages, one of two paths is mandatory:

- total differentiation and outward evaluation of all residual terms,
  including photoheating/context dependence; or
- a separately recorded outer context tube whose recomputation is proved to
  self-include and is bound into the root certificate.

### `src/rei_bianchi/source_bound_mprk_sdirk_operator.py`

Owns the concrete binding to the inherited MPRK22(1)-Alexander-SDIRK2 map. It
defines `EvaluationSiteRequest`, `AffineEventModel`, `IntegratedLedgerModel`,
`AffineStepResult`, and `LockedMPRK22SDIRK2Operator.from_repo(...)` with:

```python
evaluate_site(request) -> AffineEventModel
certify_population_stage(...) -> PopulationImplicitCertificate
certify_thermal_stage(...) -> ThermalImplicitCertificate
integrate_ledgers(evaluations, parent, endpoint, dt) -> IntegratedLedgerModel
run_affine_step(...) -> AffineStepResult
```

`run_affine_step` owns the exact `t0`, predictor, `tgamma`, and `t1`
orchestration. Its certified implicit substages are: t0 Patankar-Euler
population predictor; backward-Euler thermal predictor; MPRK22 population
corrector; gamma Patankar population stage; and coupled SDIRK2 gamma/final
thermal roots. Every population solve and thermal predictor/gamma/final
residual carries a source-bound full-enclosure certificate; a point or frozen-
photoheat thermal predictor is forbidden. Every site recomputes coefficients and remainders from that
request's state, time, forcing, and owner registry. The predecessor
`source_generators.build_source_rhs_taylor()` and
`global_coupling.audit_global_coupling()` are initial-state characterization
oracles only; their `t0` coefficients must not be reused at later sites.
`interval_discrete_map.py` is a pinned parity/containment oracle and must not be
runtime-imported by the new operator.

`evaluations` is one authenticated `StepSiteEvaluations` containing all four
site models, owners, and forcing: photon/owner ledgers consume `population_t0`
and `population_t1_predictor`, while OTS/thermal ledgers consume
`thermal_tgamma` and `thermal_t1_final`. No two-site summary may stand in for
this object.

Heat channels are unambiguous: `base_photoheat` is the atomic photoheating,
`resolved_ots_heat` is the resolved OTS Ly-alpha contribution, and
`thermal_photoheat = base_photoheat + resolved_ots_heat` exactly once.
`unresolved_ots` remains ledger-only and must never enter the resolved thermal
state. The integrated ledger adds `resolved_ots_heat` exactly once as well; a
drop, double-add, or unresolved-to-thermal injection rejects.

Before any division, the operator certifies every denominator on the full
enclosure: Patankar species denominators, `q_He,ion`, particles/energy,
owner-normalization and raw-absorption totals, OTS branch totals (`y`, `z`,
`y2`), and forcing normalizations. A zero-containing or nonfinite denominator
rejects before coefficient or remainder construction.

### New R3 stage

Create `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/` with its own:

```text
analysis/attempt_worker.py
analysis/affine_state_io.py
analysis/runtime_contract.py
tests/
```

Do not edit or relabel the R2 stage. R3 preserves its original grid, strict
binary64 thresholds, common three-lane decision, bisection policy, and atomic
transaction semantics. Its runtime contract must pin all three new core modules and
the complete new state protocol.

`INPUT_LOCK.json` also enumerates the complete explicit imported,
dynamically-loaded, copied-envelope, and opened-data authority closure,
including CSV/NPZ tables and phase-space kernels. Named predecessor files are
minimum roots only; undeclared runtime imports/opens reject and globs confer no
authority.

`analysis/affine_state_io.py` introduces `REIAFF1`. A restart round-trip must
preserve the dependency registry, structured generator blocks, mixed terms,
remainder owners and complete certificate payloads, topology identity, and
public envelope. Hashes alone are not restart evidence: event, population,
thermal, remainder, rounding, and integrated-ledger certificates must be
embedded canonically or content-addressed to mandatory authenticated sidecars.
An R2 `REIADP1` state may enter only through an explicit
`CONSERVATIVE_PARENT_BOX_LIFT`; this must never be described as recovered
covariance.

## Difference-first public comparison

The public helium coordinates are nonlinear:

\[
x_{\rm HeII}=(1-x_{\rm HeI})(1-r_{\rm HeIII}),\qquad
x_{\rm HeIII}=(1-x_{\rm HeI})r_{\rm HeIII}.
\]

For each endpoint:

1. propagate the internal affine/Taylor state;
2. transform to a certified public dependency model, including the nonlinear
   public-coordinate remainder;
3. subtract public two-half and full models by owner ID;
4. range each same-site local bilinear block over its four corners;
5. subtract the asymmetric endpoint remainder intervals as
   `[H_lower - F_upper, H_upper - F_lower]` unless an independently proved
   direct delta-remainder certificate exists;
6. only then project the delta and endpoints to public intervals.

Subtracting internal coordinates, subtracting public interval endpoints, or
subtracting interval widths is forbidden.

## Events, ledgers, and transaction rules

- A validated temperature tube intersecting a Hummer-Shull table surface
  rejects the attempt, localizes the earliest event, commits no state, rebuilds
  the fixed topology, and restarts.
- H and He invariants hold generator-by-generator and for every structured
  remainder realization; independent HeII/HeIII remainder owners reject.
- Photon, resolved heat, unresolved OTS energy, escaped radiation, and total
  energy ledgers are set-valued and must contain exact zero residual.
- Marginal ledger intervals containing zero are not evidence of simultaneous
  or whole-history closure; the integrated certificate must share the same
  dependency state and prove generator-by-generator algebraic identities with
  an outward remainder containing exact zero, or one joint feasible
  residual-vector enclosure/self-inclusion.
- No clipping, post-hoc narrowing, favorable-lane selection, source-site
  aliasing by equal bounds, or Richardson-factor change is permitted.

## Failure states

The implementation must emit stable, machine-readable classifications at
least for:

```text
DEPENDENCY_ID_COLLISION
UNAUTHORIZED_SOURCE_ALIAS
PARENT_DEPENDENCY_DROPPED
FIRST_HALF_DEPENDENCY_DROPPED
REMAINDER_PROVENANCE_MISSING
PROVENANCE_REBIND_REQUIRED
AFFINE_STATE_PROTOCOL_FAILURE
CERTIFICATE_PAYLOAD_MISSING
CERTIFICATE_PAYLOAD_AUTH_FAILURE
POPULATION_KRAWCZYK_FAILURE
POPULATION_DENOMINATOR_NONPOSITIVE
CONSERVATION_COUPLING_FAILURE
PHYSICAL_STATE_CONE_FAILURE
SOURCE_NORMALIZATION_DENOMINATOR_NONPOSITIVE
THERMAL_WHOLE_RESIDUAL_CERTIFICATE_FAILURE
THERMAL_DERIVATIVE_CONTAINS_ZERO
THERMAL_CONTEXT_NOT_SELF_INCLUDED
TABLE_EVENT_REQUIRES_RESTART
TABLE_EVENT_LOCALIZATION_FAILURE
SET_LEDGER_EXCLUDES_ZERO
SET_LEDGER_JOINT_INFEASIBLE
PUBLIC_WIDTH_GATE_FAILURE
VALIDATED_LOCAL_ERROR_GATE_FAILURE
NONFINITE_AFFINE_STATE
RESOURCE_EXHAUSTED_UNRESOLVED
```

The R3 result envelope names the estimator schema
`SOURCE_BOUND_PAIRED_MAP_V1`. It must not imply that the R2 Cartesian estimator
was repaired in place.

## Acceptance criteria for REI-LOCAL-01

REI-LOCAL-01 is implemented and locally certified only if all of the following
hold:

- full and first-half inputs have byte-identical parent dependency state;
- second-half input retains every first-half owner and remainder;
- undeclared aliases and owner-ID collisions reject;
- all population and whole thermal implicit certificates strictly self-include;
- every population, public-coordinate, source-normalization, OTS, energy, and
  forcing denominator stays positive/nonzero as its contract requires, and
  implicit derivative intervals exclude zero;
- every parent/predictor/implicit-substage/endpoint/public enclosure satisfies
  the physical state cone;
- public `H-F` is formed before interval projection;
- asymmetric endpoint remainder intervals are subtracted conservatively unless
  a direct delta certificate exists;
- for every REI-LOCAL-01 exercised fixture/case only, public half-state widths
  are strictly less than the source binary64 `2e-3` value;
- for every REI-LOCAL-01 exercised fixture/case only, paired local comparison
  bounds are strictly less than the source binary64 `2e-4` value; no
  all-node inference is permitted;
- a separately solved nonlinear fixture and a real locked-node RED test pass;
- point-degenerate behavior matches the inherited physical map;
- `REIAFF1` serialization and split restart preserve every owner, coefficient,
  remainder, complete certificate graph, and bound hash; missing or tampered
  certificate payloads reject;
- rejected attempts write no candidate state;
- the R2 source and evidence hashes remain unchanged;
- independent PHYS-MATH review is followed by independent PHYS-MATH-CODE
  review, with at most one bounded repair and differential retest.

Even after these criteria pass, the only allowed status is:

```text
adapter: IMPLEMENTED_AND_LOCALLY_CERTIFIED
canonical_pilot: NOT_RUN
first_interval: NO_PASS
scientific_pass: NOT_CLAIMED
```

The all-46,080-node, all-three-lane run is REI-LOCAL-02.

## Required verification ladder

### Adapter behavior

- common parent owner IDs for full and first-half;
- complete first-half dependency/remainder inheritance into second-half;
- no cancellation for equal values with distinct source-site IDs;
- rejection of an unauthorized alias;
- same-site corner ranging of `vf`;
- detection of a dropped first-half remainder;
- public transformation before subtraction/projection;
- asymmetric endpoint interval subtraction without a direct delta certificate;
- asymmetric-remainder recentering/serialization retains its midpoint;
- independently certified direct-delta path only;
- exact strict-threshold rejection at both binary64 `2e-4` local-error equality
  and binary64 `2e-3` public-width equality.

### Implicit and nonlinear remainder

- independently solved nonlinear scalar fixture containment;
- strict 2x2/3x3 population Krawczyk inclusion;
- rejection when a Patankar denominator crosses zero;
- rejection when `q_He,ion`, source normalization, OTS, energy, or forcing
  denominator enclosures contain zero or a nonfinite value;
- physical cone/simplex checks reject a parent, predictor, substage, endpoint,
  or public enclosure that crosses a required fraction/temperature/energy
  boundary;
- every population solve and thermal predictor/gamma/final residual has an
  authenticated full-enclosure certificate;
- whole thermal residual includes temperature-dependent photoheating;
- frozen-photoheat derivative mutation is detected;
- midpoint-only Jacobian without uniform remainder is rejected;
- outer context path requires recorded self-inclusion;
- thermal derivative containing zero rejects;
- implicit certificates preserve source owner IDs.
- resolved OTS heat enters thermal photoheat and the resolved ledger exactly
  once; dropped/doubled resolved heat and unresolved-OTS thermal injection
  reject.
- every authenticated locked realization and stagewise witness is contained;
  each local operation/remainder is checked against its pinned interval oracle.
  The final source-bound box is not required to contain the entire older
  Cartesian overapproximation.

### Real numerical RED and protocol

- The node `38382` witness is not an external-memory claim. At source commit
  `053b97c56e089e28a83f37d79a4128ed3cdae9f4` it is bound by the predecessor
  `SPARSE_LOCAL_GENERATOR_AFFINE_TAYLOR_MODEL_ENCLOSURE_LOCK` stage's
  `RESULTS_AND_VERDICT.md` (blob `dace03c1478c36e728078f21bcb27eaf7dba9d7d`),
  `data/temporal_control_lanes.json` (blob
  `aa68aa8a2761d6a89405c2e2edfc87ac3bda8cca`), and
  `analysis/temporal_control_audit.py` (blob
  `617711033236ae57ce9a40742491814070cfba18`). The JSON identifies
  `outside_node: 38382` and `outside_coordinate: x_HeIII` in all three lanes;
  the verdict records the upper-before-half/lower-after-half schedule. Task
  execution must revalidate those blobs before deriving the fixture.
- the locked node `38382` check retains the pinned full 46,080-node aggregate
  and global low-rank context (or executes the locked full field while
  asserting only that node); it never renormalizes a one-node slice;
- locked node `38382` reproduces the stagewise schedule that escaped the static
  hull and is contained by the source-bound adapter;
- a single-node owner/absorption renormalization mutation rejects;
- the earliest validated table event is localized, the candidate remains
  uncommitted, fixed topology is rebuilt, and execution restarts; non-monotone
  or uncertified event tubes fail closed;
- point-degenerate parity holds in all three lanes;
- one-node success cannot emit a scientific-pass status;
- `REIAFF1` round-trip is byte-deterministic;
- split restart preserves the full registry and remainder owners;
- deleting or altering any restart certificate payload rejects, while an
  uninterrupted and split run have the same complete certificate graph;
- marginal ledger zero-containment without one common feasible owner
  realization rejects;
- an interval-only candidate rejects without an explicit conservative lift;
- R3 worker emits `SOURCE_BOUND_PAIRED_MAP_V1`;
- R2 source and evidence remain byte-identical.

## Alternatives considered

### Recommended first implementation

Certify the full and two-half maps separately, subtract all shared coefficients,
and conservatively subtract asymmetric endpoint remainder intervals. This is
the smallest sound path and may fail closed if the bound is too wide.

### Stronger fallback

Certify one augmented residual for `(full, half1, half2, delta)` and produce a
direct delta remainder. This may be tighter but materially expands the proof,
implementation, storage, and audit surface. It is authorized only after the
recommended path produces a sound but insufficiently narrow result.

### Rejected substitute

Retain the existing Cartesian interval map only as a fail-closed comparison
baseline. Wrapping it, subtracting widths, or assigning shared IDs after
projection cannot recover dependency and is not a repair.

## Non-goals

- No adapter implementation or numerical pilot in this delivery.
- No modification of old source equations, rates, tables, evidence, or the rec
  monitoring lock.
- No production chemistry, CAMB, Bianchi feedback, family sweep, GPU, Wolfram,
  timing, or performance promotion.
- No merge, ready transition, force push, rebase, or mutation of PR14/PR18.
- No replacement of the recorded PR14 blocker with a pass claim.

## Recommended next module and checkpoint

The next implementation begins with the dependency registry and an
independently solved nonlinear fixture in
`src/rei_bianchi/correlated_map_adapter.py`; it must demonstrate RED against
the current Cartesian/static approach before connecting the real solver.
`src/rei_bianchi/joint_implicit_remainder.py` follows only once owner
propagation and difference-first projection are behaviorally locked. The real
solver is then connected only through
`src/rei_bianchi/source_bound_mprk_sdirk_operator.py` and its pinned
point-degenerate/interval-oracle tests.

Checkpoint: this specification is ready for a task-by-task implementation
plan and local executor handoff. Scientific implementation remains pending.
