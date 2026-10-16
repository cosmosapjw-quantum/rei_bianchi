# GRACKLE_RR_CI_THERMAL_BIND — frozen implementation contract

Selected unit: native temperature-dependent conservative integration, bounded
numerical validation, and subsequent independent review. Implementation proceeds
now under this contract. This framing task writes no implementation. Requested
reviewer role is Astra; observed runtime model identity is not independently known.
No new scientific model or full cosmological campaign is authorized by this unit.

## Source and mutation boundary

Research base PR157: `710f08b2bebaefbd6a28690d450d759877053ebb` at
`/root/REI_C16B_GRACKLE_THERMAL_20261016_001`.
Native authority: current PR150 `a42fd7c9849306074a9f7a262628cd852ce34dea`,
exported unchanged at `/root/REI_C16B_GRACKLE_SCRATCH_20261016/native`.
Native sources include external compile-time include_str inputs from this exact
commit. Use a task-local target directory. The PR157 crate is older and must not
be wholesale replaced or merged with PR150 for this experiment.

Allowed additions: new `research/rei_c16b_grackle_thermal_bind_20261016/` containing
`reaction.rs`, a Rust example/bridge, campaign scripts/tests, raw results and
documentation; copy that example/module into native scratch for compilation or
load the research module by an explicit path. Preserve identical executed/archive
copies. Do not edit native rates, point RHS, EOS, transport, Newton, source or
background science. Do not modify existing runs, checkpoints, other worktrees,
or the running 12-core R9 campaign and backup process.

PR156 `0c2e7b2ada4fea131a5779066894589d0dda8059` is comparison-method intake only:
its `recomb_thermal.py` expressly uses conditional Case-B-like toy alpha(T) and
3/2 kBT recombination cooling, omitting native cooling/CMB. Those coefficients,
threshold binding convention and purported physical oracle are NOT reused here.

## Reuse decision and actual method

FINAL EXECUTION CHOICE: reuse original public `Driver::chemical_stage` unchanged.
Its private ResidualContext fixes density,Tcmb and background from a, but the user
has not required arbitrary fixture density/Tcmb. Native cosmological fixtures
therefore satisfy this bounded scope without a new Newton implementation. Use
fixed a=0.1 (z=9), native nH0/Y, proper nH=nH0/a^3 and Tcmb=2.7255/a=27.255 K.
Record actual nH,nHe,Y and recovered gas temperatures. Add T=10 K CMB-heating
control (strictly inside native [1,1e6] K domain); hotter cases cool to the CMB.

Source inspection confirms chemical_stage freezes transport reconstruction,
solves [x,y,z,w_eV_per_H] with trial-state opacity and original AxbiProvider.point,
enforces original admissibility in line search, integrates converged endpoint
ledgers, and commits *s=next only on success. Its numerical scaffold has at most50
Newton iterations,40 line-search halvings and scaled residual threshold1e-11,
max(|R_x|,|R_y|,|R_z|,|R_w|/max(|wold|,|wnew|,1e-6 eV/H)). Preserve this policy.
Do not implement a duplicate Newton solver or change native convergence tolerance.
Temperature-dependent rates are reevaluated at each native trial EOS state.

Build a thin research transaction wrapper around this API with clone/source/
chemical_stage/ledger-check/commit and external failure retry. Do not use native
Driver::adaptive_step as this fixed-geometry controller: it mixes cosmological
geometry/source sequencing and can return a solver error after halving. Public
Driver::deposit is a legacy nodal diagnostic, not a complete physical PhotonState:
do NOT use it. Use Driver::seed_delta and public transport.inject with all four
PhotonState arrays for native MD14 emission.

Use proper-time seconds, nH,nHe cm^-3 and mean h=0 in the native chemical stage.
Gas fractions x=HII/H,y=HeII/He,z=HeIII/He, w erg/H; solver unknown w is eV/H.
Keep source nH0, gas density, native geometry and source normalization coherent.
Native a_perp=a exp(-b),a_parallel=a exp(2b),Hperp=H-s,Hparallel=H+2s. Do not
silently import a different HE21 prescribed-q sign convention. HE20 executable
uses native geometry; its differing README sign notation is not executable proof
of a native sign error. Frozen nonzero b is not a time-dependent shear history.

For prepared nodes k, all N are photons/H and physical E is from native geometry.
With a source transaction adding DeltaN_k before the implicit reaction,

```
Ntilde_k = Nold_k + DeltaN_k
kappa_k(xnew) = nH*(1-xnew)*sigmaHI(Ek)
             + nHe*(1-ynew-znew)*sigmaHeI(Ek) + nHe*ynew*sigmaHeII(Ek)
Nnew_k = Ntilde_k / (1 + dt*c*kappa_k(xnew))
Gamma_i = c*nH*sum_k Nnew_k*sigma_i(Ek)
Heat_i = c*nH*eV_erg*sum_k Nnew_k*sigma_i(Ek)*(Ek-chi_i)
(x,y,z)new = (x,y,z)old + dt*fraction_dt(native_point(new,photo))
wnew = wold + dt*w_dt(native_point(new,photo))
```

This is FIRST ORDER backward Euler, including source/chemistry splitting. Two
accepted half steps remain first order; no Richardson extrapolation of gas,
photons or ledgers, and no claim of second order from a symmetric wrapper.
Native thermal rates are reevaluated at every trial EOS temperature. Physical
chi=[13.598434599702,24.587389011,54.41776] eV differs from fit activation
[13.60,24.59,54.42] eV. c=2.99792458e10 cm/s, eV_erg=1.602176634e-12.
All native RR/CI/DR/CE/freefree/CMB remain active; no fake coefficients or
mislabelled RR-only mode. Empty photons means full native collision/cooling
physics with photo off, not selective removal of native processes. Test-only
photo/RR/CI diagnostics may select original native event/energy fields or subtract
photo-on/off point outputs; label them as diagnostic isolates. Every integrated
trajectory retains the complete native process set.

## Transaction, source age, admissibility and rollback

Store accepted gas, complete photon state, all physical ledgers, proper time and
source cursor/age metadata together. A trial clones that accepted bundle, applies
its source once, calls the native-owner coupled implicit stage, checks every invariant, and commits only
on complete success. Rejected full-step and half-step trials discard all injected
photons, gas changes, source cursor progress and ledgers. Diagnostic attempt/RHS
counters may increase outside physical state and must be identified separately.

On an admissibility, Newton or ledger failure halve dt and retry from the accepted
bundle; at most20 consecutive halvings, maximum20000 accepted steps and bounded
RHS/wall limits. dt must be finite and positive. Invalid input is an immediate
error without mutating accepted state; it is not a retry-until-pass condition.
Never clip fractions, photon counts, thermal energy, T or rates. Validate
0<=x<=1, y>=0,z>=0,y+z<=1, N>=0, w>0 and native recovered T in[1,1e6] K.
Do not claim positivity from a successful Newton solve alone: test postconditions
and explicit rejection rollback, including native failures and source updates.

Implement deterministic source interface `emit(t0,t1,accepted_source_state)` with
returned source state, count/energy increment, and emission epoch metadata.
Provide no-source, a known finite-duration pulse, and native MD14 emission at the
fixed fixture redshift through `AxbiSource`/`CovariantTransport::inject`.
Native MD14 already specifies emissivity, not an age-resolved stellar population;
do not invent an SSP lifetime or convolve that rate with another formation history.
An emission-cohort ledger records interval, chosen quadrature birth time, emitted
number and energy, and source identity. Ages at observation are proper t-t_emit;
these are emission-age metadata, not an inferred distribution of surviving
photons unless survival by cohort is actually tracked and checked. Name this limit.
At source on/off discontinuities split steps exactly; source evaluation must be
pure/replayable and retry must not duplicate emission. Source number/energy sums
must equal committed native source increments.

Source injection into complete native PhotonState: rebuild the four public arrays
from DriverState, call transport.inject on the trial only, write all four arrays
back, and update source_n/source_u once from the returned SourceLedger. No UV
reinsertion of Case-A bolometric escape and no second photon reaction owner.

Optional step-doubling controller compares a full trial with two half trials,
accepts the two-half state and its ledgers, and records error/rejections. It must
also retry solver failures. A fixed-step dt-halving campaign is required even if
adaptive stepping is implemented, so order is measured separately from safety.

## Energy and reaction accounting

Binding per H is chiH*x+Y*[chiHeI*y+(chiHeI+chiHeII)*z]. All chemical event ledgers
are dt*event_cm3_s/nH at the same converged endpoint; escape and CMB energy are
dt*erg_cm3_s/(nH*eV_erg). Sum accepted substep ledgers only. Diagnostic exclusions
(CI floors, CE caps, excluded low-branch DR cooling) remain visible.

Frozen geometry total: photon energy+w/eV_erg+binding+bolometric escape
-signed CMB input-source input. Also include boundary terms if populated; work
terms are zero for this fixed-geometry unit. H and He nuclei are algebraic stocks;
electron charge must agree with net photo+CI-RR-DR reaction events. Photon count
change equals source minus photo absorption, not CI or recombination. Test both
per-transaction and cumulative identities against the actually initialized state.
Driver's private initial_energy precedes custom fixture edits, so do not blindly
use absolute Driver::residuals/validate anchors after replacing the fixture gas or
seeding photons. Save a research initial anchor or compare total-energy/residual
differences. Preserve original native validation wherever its anchor applies.

Acceptance: absolute ledger residual <=1e-10 times the sum of physically relevant
absolute initial/final reservoirs and accumulated exchange terms in that unit;
zero scale requires exact zero. Do not scale by elapsed step count or unrelated
large numbers. Record raw residual, physical scale and normalized result. Check
all transactions and cumulative endpoint. Native science and its1e-11 Newton tolerance remain unchanged;
if measured ledger criteria fail, return the concrete mismatch for one targeted
repair decision, not an undocumented tolerance relaxation.

## Independent integration and finite numerical campaign

Independent Radau means SciPy Radau advances the CONTINUOUS coupled ODE, not the
backward-Euler map. It shares the authoritative native point rate provider by
design, and independently owns integration and photon ODE assembly. Preferred independent reference: compile the existing literal-C Grackle reference
into a task-local shared library, expose its unchanged coefficient bodies, and
independently assemble the same full native H/He/CMB/energy equations in Python.
Retain exact native physical chi, EOS constants, low-branch DR exclusion and
CI-floor/CE-cap conventions. Require point parity of each coefficient, event and
energy field against native exported points at100,8000,1e4,1e5 K before trajectory
comparison; tolerance1e-10 relative with exact structural zeros and128eps gross
cancellation bounds. This is a reference-only implementation, not a replacement
production provider. Alternatively a persistent native point-RHS server/FFI with
independent Radau integration is admissible as an algorithmically independent
reference, explicitly labelled shared physical RHS; it cannot be labelled an
independent coefficient implementation. Do not omit any full native term in either
reference.
No temperature interpolation table or frozen coefficient surrogate is admitted.
For delta-node reference cases evolve Ndot_k=S_k-c*kappa_k*N_k, fractions,w and
escape/CMB/source/event integrals. Use identical initial state and units; at source
edges restart Radau. Record nfev/njev/nlu, success and actual endpoint.

Run these compact fixture families, freezing exact numeric inputs in a manifest
before interpreting outputs. Use interior temperatures and mixed nonzero ions.

1. Empty photons, recombination/cooling-dominated T=8000 K; all native terms stay
   active. Horizon around a few percent of recombination time, observable change.
2. Empty photons, collision-dominated T=1e5 K; horizon with visible ionization and
   cooling while remaining well inside native T domain.
3. Mixed20/40/80 eV positive photon stocks/H with T=1e4 K and mixed ions; dynamic
   photoionization, thermal evolution, recombination and finite photon depletion.
4. Source pulse with exact edge splitting and native MD14 source smoke trajectory;
   source-off after emission proves no duplicated births and deterministic ages.
5. A stiff absorption/reaction trial (dimensionless exposure >=10 is sufficient)
   demonstrates admissible accepted steps or documented retry to them. Include a
   deliberately failed trial proving bitwise rollback of physical accepted state.
6. Native AxbiBackground q_ref=0,+0.1,-0.1 at fixed a=.1, recording actual b
   and explicit reference rays. These are
   signed geometry controls, not dynamic shear trajectories. Dynamic source-age/
   redshift work may be exposed as an interface but remains unresolved unless an
   actual evolving-geometry campaign separately accounts thermal/photon work.
   Do not confuse q_ref with instantaneous b or s/H.

For smooth nontrivial families1–3 run dt grids n=32,64,128 (allow256,512 within
same preauthorized refinement ladder). Re-evaluate native rates dynamically.
Compare common output times and endpoints with Radau rtol1e-9 and componentwise
atol approximately1e-12 for fractions/counts,1e-12 times initial thermal energy
for w (scaled variables preferred). Verify tighter Radau rtol1e-10 changes the
reference by <1% of the finest native error or <1e-7 in the norm below.

State error norm: max of absolute errors in fractions, relative thermal-energy
and T errors with max(initial,reference) scale, photon L1 error divided by
max(initial total+emitted total,1e-8). Finest native error <=5e-3 and decreasing;
when differences exceed the solver/roundoff floor, finest-two observed order
log2(error_coarse/error_fine) in[0.7,1.4] establishes first-order behavior on those
smooth cases. If branch transitions spoil a case, report it and use a separately
frozen smooth fixture for order; never hide the original result. Constant/zero
components do not receive a false order estimate. Native RHS/ledger tolerances
must not be widened to manufacture convergence.

Angular and spectral refinement are separate: use native MD14 smooth spectrum
with source subdivisions16,32,64 and native angles8,16,32; hold dt sufficiently
small and use a nonzero frozen anisotropy so angular refinement is nontrivial.
Hold the other grid fixed at its finest level. Report gas/T, photon number/energy
and angular moments against the finest grid. Require finite admissible histories,
ledger acceptance, finest-neighbor normalized observable difference <=5e-3, and
reduction of successive differences unless already <1e-7. Reconstructed spectra
change with grid, so this supports measured refinement only, not equality to the
delta Radau model. Record native transport cell count separately and keep it
fixed sufficiently fine or perform its own32/64/128 refinement; do not label
source-subdivision refinement as transport-cell convergence. Cases and cost may
be combined but each refinement axis must be identifiable.

Survey establishes all8 relevant native dependency files byte-identical to the
previous admitted PR150 source. Reuse prior point/focused-test evidence under that
explicit binding; run new wrapper and independent-reference point controls only.
Do not repeat old native tests or unrelated historical campaigns merely for the
new commit label.

## Resources, return and finite transition

Initial compile jobs2, native transport worker1 unless a bounded comparison needs
more; at most8 campaign workers, no nested pool oversubscription, memory8GiB.
Protect existing12-core R9 and backup jobs. Per executable campaign timeout300s,
unit wall budget20min before checkpoint/reassessment; max20000 accepted steps and
explicit RHS/attempt caps. If expensive Radau/grid cases approach limits, preserve
their partial evidence and report the unresolved axis rather than silently shrink
its acceptance domain. No repeated Ubuntu DesktopCommander quota calls; execute
on the already available NCP host without unnecessary SSH.

Return code diff, frozen input manifest, executed source identity, commands/exits,
raw histories/ledgers/rejections, timing/memory, point and focused-test evidence,
independent Radau and each refinement result, and concise owner/claim mapping.
One independent final read-only review may authorize one bounded targeted repair
episode and affected regressions. PASS transitions to the user's authorized
publication/backup closeout by the controller; failure returns a concrete scoped
HOLD with preserved evidence. Do not recursively review or add process gates.

Claim ceiling: tested native temperature-dependent conservative H/He transaction,
measured first-order temporal accuracy, measured finite angular/spectral refinement,
and deterministic emission-age/MD14 interface. This does not establish production
cosmological ionization/T histories, general stiff accuracy, continuum convergence,
escaping-photon spectrum, SSP-age physics, baryon recoil or Einstein backreaction.

## Authorized supplemental native evolving-background smoke

After the core transaction/reference checks pass, run a NEW original native
Driver::adaptive_step trajectory for each q_ref=0,+0.1,-0.1, using a clean
Driver::new state and its original initial-energy anchor. Do not import, restart,
edit or extend an existing campaign. Target exactly3 accepted steps per sign
(up to5 only if a final observable is unavailable after3), attempts<=1000,
RHS evaluations<=30000, wall<=30s per sign. Keep native source, background,
geometry_map, thermal work, photon work and adaptive policies unchanged; no
additional geometry/adiabatic operator in the research wrapper for this test.
Set config bounds before construction; retain original density/source consistency.

Record initial and each accepted state, scale factor, native proper clock,
actual b,s/H,Sigma, source number/energy, photon number/energy, thermal/binding/
escape/CMB reservoirs, thermal_work,photon_work, boundary terms, native residuals,
attempt/RHS/reject counts, timestep and elapsed time. Check physical admissibility
and the full dynamic ledger against its native initial anchor:

  photons+w/eV_erg+binding+escape+boundary_energy
  +thermal_work+photon_work-source_energy-cmb_input = initial_total.

Use the core1e-10 physical-gross-scale ledger criterion, and also report native
validate/residual outcomes without conflating different scale conventions.
Likewise photon count+absorbed+boundary-source must preserve its initial anchor.
Use native source emission directly; do not add the fixed-geometry research source
again. Actual native q_ref and instantaneous signed s/H are distinct observables;
Sigma=sqrt(3)*abs(s)/H contains no sign. No angular/sign convention is inferred
from labels. Existing native step rejection may be handled using its already
reduced dt within the fixed caps, retaining the failure record and accepted
physical state; no solver/model repair or broadened campaign is implied.

Report PASS_SMOKE only for completed admissible3-step sequences with ledgers
passing. A capped or failed sequence is a preserved supplemental HOLD, not hidden
or converted to a core fixed-geometry failure. It must narrow any claim concerning
the evolving-background path. Do not spend an open-ended repair cycle on this
supplemental check. This adds actual short native MD14 injection and signed
background/work execution evidence only; it establishes neither source-age
population physics nor dynamic discretization convergence, production z=20->4
history, or backreaction. The controller's THEORY_KO note must retain this ceiling.

## Bounded reference-coordinate and angular-fixture repair authorization

These two corrections belong to the existing implementation/verification episode;
no native science, acceptance tolerance or additional review cycle changes.

1. Source-free photon equations obey Ndot_k=-c*kappa_k*N_k. An initially exact
zero mode is an invariant subspace and may be omitted from Radau's unknown vector,
reconstructing exactly N_k=0 for native gas/photo evaluation. For initially positive
source-free modes, use ell_k=log(N_k), ell_dot_k=-c*kappa_k, reconstructing N_k=exp(ell_k).
This is an exact coordinate change of the continuous ODE; do not clip values,
replace negative values by zero, or widen native domain checks. Integrate event/
energy ledgers consistently and assess final accuracy in the same physical-state
norm as the original contract. Report the coordinates and oracle error controls.
The permission applies only to source-free invariant-zero/positive modes; a mode
with future continuous source cannot be omitted or treated as source-free logN.
Unrepresentable exp(ell) or an invalid native state remains an explicit failure.
Preserve the original tiny-negative-photon Radau failure (about2e-39) and report
it as a coordinate/admissibility defect of the numerical reference, not negative
physical emission or a native reaction defect.

2. A locally isotropic source inserted at the already-frozen final geometry is
not a strong anisotropic angular-accuracy control. Construct a prescribed photon
initial condition by injecting an original native MD14 cohort at native a_ref=1/21
(z=20), then applying unchanged native geometry_map to a=0.1 with q_ref=+0.1.
This supplies a native direction-dependent redshifted spectrum. Record cohort
emission amount/time convention, original source normalization, ray labels,
initial/final geometry and photon number/energy before/after construction. Retain
all threshold-crossed photons according to original native transport policy.
Then explicitly initialize the test gas at the final fixed geometry, set the
research photon/gas initial anchor there, and evolve source-free local reactions.
No source is injected again during this local trajectory. Native geometry-map
work during construction is recorded as initial-condition provenance; do not
count it again as work of the subsequent fixed-geometry evolution. Reset or
baseline-difference ledger anchors coherently when resetting gas, retaining the
construction record separately. This is a prescribed photon IC, not a claimed
cosmological gas evolution from z20 to9.

Use the already frozen source subdivision16/32/64 and angular8/16/32 ladders,
transport128 fixed (with any separately declared transport refinement), and
identical native emission and local-reaction horizons. Change one resolution axis
at a time and keep the other at the stated finest level. This permits a nontrivial
angular control within the original numerical campaign bounds; it does not assert
its convergence before measurement. Apply the existing error/ledger criteria and
record a scoped unresolved angular result if they fail. No new physical source
model, coefficient override, or sign-convention substitution is permitted.

## Mixed-photo transient accuracy: targeted refinement extension

Observed mixed T=1e4 K trajectory at n=128 has endpoint error3.3064e-4 and
endpoint order1.0148, but maximum error at the existing common observation times
is0.0209758 (n32:0.06806,n64:0.03937). Endpoint agreement does not establish the
requested trajectory accuracy. Preserve these raw histories and both error
summaries; do not label the n128 trajectory as meeting the0.005 maximum-time target.

Authorize only this affected temporal axis to continue at n=256,512 and, if the
maximum common-time error still exceeds0.005, n=1024. The1024 extension is a bounded
reassessment justified by the observed approximately first-order transient error
and predicted need beyond512; it changes neither physical inputs nor tolerance.
Keep horizon3e12 s, native rates, source/photons, solver settings, Radau reference,
physical error norm and the original common observation times fixed. Intermediate
steps may provide additional observations, but retain the fixed common-time
comparison for order. Report endpoint and maximum sampled-trajectory error
separately, plus the time/component of the maximum. The finest selected run must
have maximum common-time physical-norm error<=0.005 and the existing first-order
criterion on the resolved finest-two errors. This is sampled trajectory accuracy,
not a rigorous continuous-time supremum bound.

Retain an n512 failure if present; do not widen the threshold. Stop at1024 and
return a scoped HOLD if acceptance remains unmet. No other axis or campaign is
expanded by this authorization. Keep the established per-run resource limits;
record this bounded wall-budget reassessment and added evidence size, estimated
about12MiB and seconds of native work, rather than starting an unbounded ladder.

## Pulse adapter exact-delta representation repair

The retry-recovery test exposed AXBI_COVARIANT_SUPPORT_DOMAIN after repeated
same-q pulse deposits: separately accumulated N and U may not satisfy the native
exact-delta representation U=q*N at binary64 precision. Authorize a pulse-only
adapter repair, with no native source modification: verify a single known fixed-q
delta per affected occupied ray, combine surviving N and requested birth N, rebuild
a fresh complete PhotonState and call original native add_delta once per ray.
This canonically represents the same physical delta; it is not clipping or an
alteration of a broad-spectrum closure. Preserve all unrelated/passive cells or
reject an unsupported layout explicitly; do not silently discard photon support.

Committed source number/energy and emission-cohort counts must match the actual
native inventory increments. Preserve requested birth quantities separately and
record requested-minus-represented differences, which must remain roundoff-scale;
a substantive loss is HOLD, not an adjusted physical emissivity. The photon
energy convention stays the existing fixed geometry q times native ray scale.
Preserve the first failing stderr and recheck only affected early/delayed pulse32,
retry/recovery/rollback, and independent pulse-reference comparisons. Scientific
owners, tolerances, pulse timing, and other accepted cases remain unchanged.
