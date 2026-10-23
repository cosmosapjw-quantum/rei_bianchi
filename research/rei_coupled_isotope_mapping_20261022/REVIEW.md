# Independent scientific review — selected C2

Decision: **PASS_SCOPED_C2_MAPPING_AND_FINITE_BINDINGS**.
No C2 correctness blocker was found and no repair is requested. The positive
transition is **C3 numerical design of the conditional local source adapter**.
Physical coupled production remains **HOLD_DEPENDENCIES**.

## Scope, source authority and independence

This is the single independent review of C2 formula–data–code mapping and its
finite diagnostic. The completed C1 at `9f621b684fedb9b71f2148022f6909d1760ba947`
is reused, not re-reviewed. Starting checkout HEAD was observed as
`3e56bbd3d939ab235df2d47f9d012c95674d00fc`; the atomic donor remains PR220
`8be7533cc97b3302bf42608699d6e8313ed6af8a`, and the nuclear source lineage is
the frozen a7 checkpoint with scientific pilot parent 5a1e522.

The reviewer did not author the C2 theory, diagnostic, fixtures or bindings.
Actual source and output were read without running the diagnostic, any physical
provider campaign, the old C1 tests, nuclear sweep, or cosmological solver.
Read-only JSON inspection summarized recorded residuals and confirmed that
the current script, execution contract, source-identity document and bindings
match their recorded execution SHA256 values. Only this review and its JSON
companion were written. There was no recursive delegation.

Requested identity: independent Astra-tier scientific reviewer. The session
instructional model description is GPT-6 Astra Pro, but runtime tool output
does not expose an actual model identifier; none is inferred. Skill context:
physmath-research-loop 1.3.0 SKILL.md, POLICY_INTEGRATION.md and CODING_LOOP.md
C2/C9, read earlier and reused unchanged, plus AGENTS.md and this C2 execution
contract. The selected-stage and one-pass stopping rules remain binding.

The recovered RR source is the exact archive candidate identified in
SOURCE_INTAKE.md and SOURCE_IDENTITY.json. CONCURRENT_UPDATE.md records a
new published parallel admission of the same RR bytes. That is separate
provenance/handoff information: neither concurrently dirty files nor that
parallel admission replace this C2 source comparison or expand its claim.
The old bootstrap errors are not a current C2 or C3 execution blocker. This
review does not independently re-admit the parallel provider campaign.

## Observed finite evidence

The producer's sole invocation reports **214 PASS, 0 FAIL, exit 0**, wall
0.948761436 s, CPU 0.897878138 s, peak RSS 41952 KiB. It records two actual
AtomicNetwork constructors, seven donor rates calls including the evaluate
call, one evaluate call and 18 recovered rr_rate calls. Source inspection
supports the reported absence of nuclear rate recomputation, propagators,
historical campaigns, ODEs and IVPs. Resource use is inside the frozen cap.

| Check | Observed result | Frozen criterion |
|---|---:|---:|
| 39 five-point log-temperature slope comparisons | max absolute error 7.2618577817706864e-12 | <=1e-8 |
| 26 photo energy partitions | max normalized error 1.3950455899595689e-16 | <=128 epsilon |
| Nine same-provider H/He comparisons | max relative error 2.303380110673309e-16 | <=128 epsilon |
| 18 donor-alpha direct-formula comparisons | max relative error 3.0585297285950283e-16 | <=128 epsilon |
| Beta-free atomic RHS plus old D versus evaluate | 4.727320392486554e-24 | <=128 epsilon |
| Beta-free atomic Jacobian plus old D versus evaluate | 0 | <=128 epsilon |
| Intentionally omitted Li+ b-dot term at 1e6 K | error 0.21665764584750102, rejected | must exceed 1e-8 |
| Intentionally retained beta in beta-free source | error 0.9999999535576315, rejected | must exceed 128 epsilon |

Here `128 epsilon=2.842170943040401e-14`. Expected negative controls pass by
rejecting their deliberately wrong constructions; they are not hidden product
failures. The saved nuclear sample has exact observed array agreement with
the direct slices at case 0, epochs 0/128/256. Its saved shared T grid, family
order, array shapes and natural-log decay convention pass the prescribed checks.

## Scientific assessment

**RR derivation and provider identity.** For the stated fixed target,
temperature-independent cross section and nonrelativistic Maxwellian electrons,
differentiating the number-rate integral gives
`lambda=k_B T alpha(3/2+dln(alpha)/dln(T))`. The derivative-of-fit error formula
in THEORY.md follows exactly and correctly shows why a number-fit error bound
alone is insufficient for an energy-moment error bound. Badnell's variable
exponent contributes `+b_dot*ln[(1+u)/(1+v)]`; both sign and coefficient are
correct. The high-T formula-only negative control actually detects omission.

Primary VF table documentation, Badnell RR/DR definitions, and Mao–Kaastra–
Badnell equations (1)–(4) were independently opened during this review.
They support the units and target/product row interpretation. No adf48 energy
table or new physical uncertainty was imported. Each donor alpha stays with
its own derivative/moment. The Li differences are provider comparisons, not
equality failures or evidence that one provider is physically more accurate.
For example at 10000 K, Li+ donor/recovered alpha is 1.0029243575549798 while
its lambda ratio is 0.9867929314892422: using a common ratio would lose the
derivative dependence. The recovered API is called only inside 100–10000 K;
finite-difference probes evaluate the analytic formula, not that API outside
its admitted range.

**Atomic mapping and energy.** The actual donor yields the recorded 21 slots,
13 photo edges, 13 RR edges and six DR edges. RR keys use the incoming upper
charge, while photo keys use the lower charge. VF product N and Badnell target
N are correctly distinguished; inspected extract row positions and parameters
agree with CODE_MAP.md. Signed DR fit amplitudes remain coefficients of a
total fit and are not interpreted as branch probabilities. RR kinetic moments
bind to Grr/rr_m3_s only. Gne includes DR and is not an RR energy coefficient.

The photo partition uses the donor's actual finite quadrature and retains
Li 1s core energy separately. The 60 eV support zeros and 200 eV positive
support refer to those named external fields. The comparison is internally
consistent without claiming quadrature convergence or accounting for generated
nuclear photons. RR cascade/binding bookkeeping in THEORY.md has the correct
signs under its expressly conditional completed-cascade model.

**Beta boundary and outer conversion.** At fixed T, UV and n_B with all thermal
electrons, the stated `G0+ne Gne+nb outer(Gne Y,q)` Jacobian follows directly
from `ne=nb q.Y`. The actual old evaluate includes D in both RHS and Jacobian;
the new beta-free assembly uses rates and omits D. The nonzero-n/T manufactured
state makes the duplicate-beta control effective. Actual coupled.py divides
the proper-time abundance source by scale and H at the outer boundary and
applies the corresponding scale_j/scale_i Jacobian conversion. New thermal
and nonthermal cross derivatives remain C3 onward work, not validated here.

**Nuclear registry, units and saved data.** The full 18-family registry is used,
not the smaller 13-family channels helper. There are 34 physical directions:
24 binary coefficients in m^3/s and ten unary coefficients in s^-1, comprising
two forward decays and eight external photodisintegration support zeros.
The two extra reverse-beta array slots explicitly have `physical_entry=false`
and absent-weak-bath status. Their nominal s^-1 storage metadata does not admit
an inverse coefficient. In particular, the inherited array name
`log_reverse_rate_m3_s` does not control physical units or applicability.

The saved fluxes are a replay of the old population/background, not general
rate coefficients for a changed Y. Natural-log values are preserved; finite
very negative logs, initial zero stocks, zero initial cumulative events,
external support zeros and absent weak inverse channels are distinguishable
through their process/status context. The diagnostic reads NPZs directly and
never imports the nuclear evolution module. Off-grid interpolation, tiny-stock
representation and general daughter maps are explicitly deferred to C3 design.

## Findings, obligations and termination

Current C2 defects: **none found**. The mapping and observed finite tests satisfy
the selected execution contract. No extra physical input is required to accept
this C2 deliverable, and no repeat execution or historical campaign is justified.

Conditional RR fit moments and scalar provider admissions remain narrower than
physical cooling/thermal closure. Charge-conditioned daughter probabilities,
consistent binding references, physical moment accuracy, DR energy moments,
fast transport/stopping/stress, and generated-photon closure remain future
provider obligations for the corresponding physical claims. They do not block
the next conditional numerical-design action. This review admits C2 only and
does not claim completion of C3–C10 or a coupled cosmological solution.

Final same-pass expression check: REPORT_KO.md, README.md, DAG.json and
RESUME.md agree with this admission and the observed results. The report
distinguishes 214 checks from independent physical experiments; the README
explicitly identifies the external full nuclear arrays and mapping references
required to repeat all checks, so the compact checkpoint is not advertised as
a standalone replacement for the old campaign. The next-stage notes retain
conditional RR moment scope and do not revive historical bootstrap errors as
current blockers. No claim expansion or further repair was identified.
The single bounded review is complete; stop verification and hand off to C3.
