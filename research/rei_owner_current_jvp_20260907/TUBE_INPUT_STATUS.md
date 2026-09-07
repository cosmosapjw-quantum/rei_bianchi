# Saved input boundary for the resolved-owner JVP

Result: **PHYSICAL_UNIFORM_OWNER_BOUND = UNKNOWN**. This means that the inspected
saved evidence does not establish the complete source-input tube required here.
It does not mean that REI has no enclosure artifacts. No new physical inputs or
intervals were generated. PR #75's illustrative box and the O01--O10 Fraction
fixture are not used as physical tubes.

All paths and local Git blob identities are in
[SOURCE_BINDINGS.json](local_evidence/SOURCE_BINDINGS.json), at tested commit
`12d64833419651a532451ad4c9a180aa65a0a70b`. The data schemas, source constants,
literal-derived prefactors, and historical primary summary are in
[INPUT_INSPECTION.json](local_evidence/INPUT_INSPECTION.json).
The aliases below abbreviate those exact paths, not guessed source locations:

- ADAPT: stage ending `ADAPTIVE_INTERNAL_MICROSTEP_ACCEPTANCE_AND_GLOBALIZATION_LOCK`.
- CROSS: stage ending `CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK`.
- INITIAL: stage ending `CANONICAL_INITIAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK`.
- FORCING: stage ending `CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK_RERUN_V2`.

## One saved enclosure inspected

`CROSS/data/VALIDATED_PUBLIC_BOXES.npz` really contains lower/upper arrays, including
the selected `LOCAL_NEUTRAL_HAZARD_PRIMARY` pair, each shape `(4,46080)` with
coordinates `(x_HII,x_HeII,x_HeIII,log_T)`. Only this lane's archive headers were
inspected. No array-level positivity, numerical enclosure, or rounding claim was
made from the headers.

The producer `CROSS/analysis/containment_audit.py:19--21,38--39,52` serializes the
**final endpoint** returned by `interval_discrete_map.run_lane`. That map uses a
full step and two half steps; lines 343--354 choose `second.population` and
`second.log_temperature`. It does not serialize all internal stage input arrays.
Its final corrector population is indeed also the population argument at the
second half-step's final thermal source (`run_step:318`). That is useful source
correspondence, but does not turn the saved final observable box into the joint
state/forcing/time tube requested here.

For fixed per-node elemental totals, endpoint neutral counts could in principle
be recovered from the charged fractions and totals. The issue is not merely the
absence of fields named `N_HI_lower`: those identities still do not supply the
stage/path enclosures and physical perturbation dependence missing below.

The saved primary JSON reports `certified=true`, `map_enclosed=true`, partition
2048, and no table event, with minimum distance `0.00028926282673857884`.
These are **historical reported results**, read without rerunning or re-certifying
their producer. Its `maximum_validated_local_error` is a full-versus-two-half-step
comparison; this task does not reinterpret it as exact-flow defect rho.

## Required fields and their actual availability

| Required input | File / actual field | Result for this task |
|---|---|---|
| Source-bound N enclosure | `CROSS/data/VALIDATED_PUBLIC_BOXES.npz`, primary `__lower/__upper`; INITIAL NPZ point `N_*` arrays | Endpoint observable enclosure exists. Complete positive stage/path N tube is **UNKNOWN**; no endpoint or initial point was promoted to it. |
| Fixed elemental totals | `INITIAL/data/initial_material_state_metadata.json`; initial `N_*` arrays; map lines 346--347 | Nominal global H=`5.523438018661132e66`, He=`4.363516034742294e65` are recorded; map fixes per-node totals from initial arrays. Fixed-total chemistry is a valid specified tangent subspace. A physical tube/direction binding to these totals is **UNKNOWN**. Metadata decimal totals are not newly certified exact sums. |
| z enclosure and direction | FORCING CSV `z_mid`; `ADAPT/analysis/array_forcing.py:62,87,100` | Tabulated/interpolated z and its time dependence are available as source. Bound and delta-z for a selected joint input tube are **UNKNOWN**. `z_snapshot` in the owner table is not substituted for the forcing adapter's z. |
| Fixed sigma and support | FORCING atomic CSV `gray_sigma_cm2`, `supported`; tensorized inputs lines 135--150 | **AVAILABLE_SOURCE_BOUND**. Atomic support and the narrower explicit-owner support are both respected. |
| J range and direction | FORCING CSV `absorption_{g}_s-1_cMpc-3`; forcing adapter lines 60,85,98 | Point samples and interpolation law exist. No joint-tube J enclosure/direction is recorded; **UNKNOWN**. A sampled maximum was not treated as a certified maximum. |
| External e range and direction | INITIAL `owner_law_time_matrix.csv`, `raw_component_kappa_cMpc_inv`, component `EFFECTIVE_HI_SUBGRID`; tensorized inputs 117--124 | Raw e samples and interpolation law exist. Joint-tube e enclosure/direction is **UNKNOWN**. Conditioned opacity is not substituted for raw e. |
| kappa strictly positive | FORCING CSV `kappa_{g}_cMpc-1`; forcing adapter lines 59,84,97 | Positive point samples do not by themselves constitute this task's strict tube certificate. Coupled tube lower bound **UNKNOWN**. |
| R >= r > 0 | Requires `e + sum(c_s*N_si)` over the same input set | Formula is known. The physical uniform lower bound r is **UNKNOWN**; no arbitrary floor was inserted. |
| Site identity and time span | `CROSS/analysis/interval_discrete_map.py:297--340,343--354` | Static sites: parent at t0, predictor at t1, gamma at t0+gamma*h, corrector population at final thermal t1. Historical microstep endpoint is `duration_seconds(0)/2048`; second half spans `[duration/4096,duration/2048]`. Their joint saved input tube is **UNKNOWN**. Equal times do not identify equal sites. |
| Event-free positive domain | `CROSS/data/LANE_LOCAL_NEUTRAL_HAZARD_PRIMARY.json` | Historical event-free summary exists. Domain validity for a newly specified N/z/J/e perturbation tube is **UNKNOWN**. |

The forcing tables have sample fields, not saved lower/upper or tangent fields.
PCHIP point evaluation and step averaging are different source operations. No
PCHIP or production import was executed to manufacture a missing enclosure.
The current Rust wrapper's unavailable four-site replay is unchanged; its
availability or security metadata is not used as an extra gate for this research.

## Actual prefactors and dependencies

Read source constants: `NH0_CM3=1.88e-7`, `YHE=0.079`,
`MPC_CM=3.085677581491367e24`. For each fixed group, let m be its explicit-owner
support mask, distinct from the atomic CSV's support flag:

```
p_HI   = m_HI   * NH0_CM3 * MPC_CM * sigma_HI   * (1+z)^2
p_HeI  = m_HeI  * NH0_CM3 * MPC_CM * sigma_HeI  * YHE * (1+z)^2
p_HeII = m_HeII * NH0_CM3 * MPC_CM * sigma_HeII * YHE * (1+z)^2
c = (p_HI/H, p_HeI/He, p_HeII/H)
```

The owner masks for `(G1,G2a,G2b,G3)` are HI=`(0,0,1,1)`, HeI=`(0,1,1,1)`,
HeII=`(0,0,0,1)`; subgrid is `(1,1,0,0)`. In particular, positive atomic HI sigma
at G1/G2a does not activate the explicit HI owner there. The JSON constructs
all 12 source-literal coefficients `p/(1+z)^2` by exact rational multiplication.
It does not insert a made-up z, total, or bound into `coefficient_jvp`. Literal
rationalization is bookkeeping for the real expression, not binary64 parity.

N already carries node quadrature weight. `_allocate` uses `N*sigma`; no second
node weight belongs in this resolved-owner law. Opacity has units cMpc^-1.
The forcing CSV supplies J per second per cMpc^3; the source allocates that
normalized-box current directly to its extensive nodes. For the source's
one-cMpc^3 normalization this is the numerical box photon current per second.
There is no additional node volume conversion in `photo_fields`.

For a state-only partial at fixed forcing/time, sigma/support and z,J,e,kappa
are frozen, and chemistry directions keep H/He fixed. This is a declared partial,
not a claim that physical forcing is independent of time/state/parameters.
Time perturbations pass through interpolated z,J,e,kappa; external input
perturbations can change their tables. Arbitrary state/parameter perturbations
also require delta-H/delta-He. At fixed constants/support,
`delta-p=2*p*delta-z/(1+z)` and the tested coefficient helper retains total
derivatives. Direct kappa cancellation leaves all indirect J/e/c/N dependence.

The exact-real conditional inequality remains

```
||delta j_aug||_1 <= |delta J| + (2 Jmax/r) *
  (|delta e| + sum_si [c_s,max |delta N_si| + N_si,max |delta c_s|]).
```

All maxima, positive r, and direction envelopes must apply on the same tube;
none is numerically supplied here. The unresolved subgrid node distribution,
OTS/atomic rate derivatives, thermal coupled bound, and exact-flow rho remain
separate unresolved obligations.
