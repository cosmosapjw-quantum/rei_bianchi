# ENDPOINT14 — endpoint-zero even-sextic angular reference

Root-authored frozen scientific contract. physmath-research-loop 1.0.0, 2026-10-28.
Unit HE-EXP-ENDPOINT-14; owned path research/program_expansion_20261025/continuation_endpoint_20261028; branch research/he-endpoint14-20261028.

## Authorization, baseline, objective
The user explicitly requested a new next R1–R10/C1–C10 loop after fresh related branch/PR/commit/conversation/backup intake, actual publication and dual backup at every paired stage, DAG counters, and copyable final handoff. This is one new unit after completed TANGENT13, not a rerun of that unit.
Base source S10 049e79cb453b92ac663c4e0a93577a8364c3cf54, exact tree ad7c7dbf7d90159b7b938da61038989b0fc24f16. Latest central intake 66ef9a0147a0573b77e74e151dc280ba2bd4b64c; refresh before central publication.
Local is an existing restored partial source mirror, without .git or a local D commit. Preserve all predecessor files and receipts.

Scientific question: at 330 MeV, does the endpoint-zero full nonnegative even-sextic family contain a distribution satisfying the SAME four nominal-angle EXFOR windows, and what rigorous same-event aperture bounds follow? QUARTIC12 already certified that its endpoint-zero full even-quartic family is empty. This unit changes polynomial degree alone, preserving the endpoint condition, data, kinematics and geometry. It quantifies model-class sensitivity; it does not identify the physical angular/polarization law.

## Fixed data and conventions
Reaction He4(g,d)d, EXFOR M0475002. Source official_source/M0475.x4 SHA256 b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f.
QUARTIC12 saved exact input research/program_expansion_20261025/continuation_quartic_20261028/evidence/validation/initial/SAVED_PLOT_DATA.json SHA256 a8fbe269d3941706a510796963f059d7404f3f4655a6a3163042e85011aa0d45.
TANGENT13 saved result SHA256 bb23c922246b3bd34566f436f6068539e7b2040fc0fa61b4b73daf787931fae6 is prior completion evidence, not a new runtime science input.
330 MeV DCS windows at theta_cm=46,61,73,87 degrees: [11/100,17/100], [11/100,21/100], [1/50,3/25], [7/50,6/25] nb/sr. ERR-S remains a deterministic coordinate sensitivity window, with no joint confidence interpretation. M0475003 total-cross-section energy grid remains separate; no energy joining/interpolation.
Use mu=cos(theta_cm), z=mu^2, declared uniform azimuth, inherited same-event two-detector union, metric(-,+,+,+), and c,hbar,k_B retained. Rest energies A=3727.3794118 MeV, M=1875.61294500 MeV, photon e=330 MeV are unchanged.

## Model and containing constraints
q(z)=(1-z)r(z), r(z)=a0+a1*z+a2*z^2 >=0 on [0,1]. Then f(mu)=q(mu^2) is an even polynomial of degree at most six with f(+/-1)=0. Conversely every even sextic with endpoint zero has this factorization and q>=0 iff r>=0 (continuity at z=1). Signed a coefficients carry nb/sr units.
The ordinary cubic coefficients are b=(a0,a1-a0,a2-a1,-a2). Degree<=4 is exactly a2=0 in this family.
D=integral[-1,1] f(mu)dmu = d.a, d=(4/3,4/15,4/35). P_g=k_g.a/D.
Containing box B=160 is a theorem, not regularization: saved z intervals for angles46/61/87 have pair separation>=1/5 and z<1/2; all selected q upper windows<=1/2, so 0<=r(z_i)=q(z_i)/(1-z_i)<=1. Exact degree-two Lagrange interpolation gives |a|<=(75,150,75), hence |a_j|<=160.
Since |b1|<=2B, |b2|<=2B, |b3|<=B, |df/dmu|<=18B. With L*=7/50 at87 degrees and delta=L*/(36B), f>=L*/2 on the centered interval of length2delta, contained in[-1,1]. Thus D>=L*^2/(36B)=49/14400000. Require this floor in every polytope.

## New row and moment algebra; no old geometry campaign rerun
Read saved certified Z=[zl,zh] at each angle; do not recompute trigonometry. For j=0,1,2, c_j(z)=(1-z)z^j has a safe positive interval [zl^j*(1-zh), zh^j*(1-zl)]. Define midpoint m_j and epsilon=B*sum_j(width_j)/2. Then |c(z).a-m.a|<=epsilon on the containing box. Contract windows for inner data and expand for outer data.
For fixed full-azimuth hemispheres/caps, prove the same-event set is [-1,-t] union[t,1]. The inherited lab map is increasing when K=e^2-(A+e)^2*(s-4M^2)/s<0, s=A^2+2Ae. Verify this exact rational inequality as a changed-evidence compatibility control. For polar threshold nu0=0 or1/2, if alpha=F^{-1}(nu0), beta=F^{-1}(-nu0), monotonicity gives t=max(alpha,-beta)>=0. Thus the saved zeroth monomial moment bounds determine t_lo=1-k0_hi/2, t_hi=1-k0_lo/2.
New weighted moments use the nonnegative basis directly:
G_j(t)=2*((1-t^(2j+1))/(2j+1)-(1-t^(2j+3))/(2j+3)),
k_j in[G_j(t_hi),G_j(t_lo)], j=0,1,2. The derivative -2(1-t^2)t^(2j)<=0 proves enclosure. FULL moments are exactly d. Save threshold intervals and new moments. Require old saved monomial j=0,1,2 bounds to overlap the same threshold-formula bounds; report exact equality separately if observed. This control is not the reason the geometry shape is true: the preceding analytic topology proof is required.
No old science module imports, preimage solver calls, trigonometry, optimizer or geometry reevaluation. Standard-library Fraction arithmetic only for the new campaign.

## Predeclared construction and bounded finite sandwich
Hand-selected rational candidate a*=(1411/10000,-1/4,33/25). Check its exact r minimum using endpoints and stationary point, all four true-data enclosures, box, denominator floor and endpoint factorization. Its success is not assumed. Preserve exact candidate outcome even if it fails; do not silently tune it after seeing the result.
Fixed resolutions N in {1,4,16}; three cases, each with one inner and one outer polytope in the three a parameters.
Outer positivity rows r(k/N)>=0 at nodes; inner adds middle Bernstein controls a0+a1*(l+h)/2+a2*l*h>=0 in every cell. Deduplicate identical left-hand-side constraints, keeping tightest RHS. Enumerate ALL triples of active constraints by exact rational elimination, skip singular bases, check all inequalities and deduplicate vertices. Each polytope includes the six box inequalities and positive D floor. Save matrices/RHS/vertices/counts so completeness rests on exhausted bounded-polytope enumeration.
Check nested inner1 subset inner4 subset inner16 and outer16 subset outer4 subset outer1 by all vertices and constraints. Verify exact r>=0 for every inner vertex and candidate. For outer vertices record exact quadratic minima; do not presume full positivity.
Sign-aware moment interval at any a gives numerator nlo/nhi. Concavity/convexity plus positive denominator-weighted convex combinations prove outer extrema of nlo/D and nhi/D occur at vertices. Inner vertices supply feasible min/max witness bounds. Include the fixed candidate as an additional feasible witness if certified. Publish raw outer range, [0,1]-clipped physical range, minimum bracket and maximum bracket, all exact fractions with outward decimal displays. FULL=1 exact for every feasible distribution.
No unearned tightness target: report the actual N16 bracket widths and comparison across fixed resolutions. Primary success requires a constructive feasible endpoint-zero sextic, all six enumerations complete within cap, exact inner/outer inclusion controls and valid aperture brackets. If inner/outer gaps remain, record them explicitly; no post-result extra mesh.
Compare to the saved330MeV endpoint-zero quartic EMPTY_OUTER and existing330MeV free quartic aperture ranges by reading only. Keep EXFOR11 finite Bernstein-cone endpoint-zero EMPTY and all earlier results intact. A new higher-degree witness demonstrates degree/coefficient-cone sensitivity within the stated conditional models; no strong global no-go is sought.

## Implementation, controls and output
Complete producer plus independent saved-certificate reader that does NOT re-enumerate or solve for candidates. New tests use exact manufactured cases and independently specified expectations: factorization/normalization/derivative identities; positive quadratic with negative coefficient and negative-quadratic rejection; row interval signs; analytic threshold-moment examples at t=0 and1/2; cube/simplex known vertices and singular rejection; actual source and immutable saved-input binding; all actual six polytope certificates/nesting/witness/data/denominator/positivity; signed ratio and outward display; corrupted-certificate rejection. Keep one construction call per actual campaign and no computations on import. No meaningless smoke-only validation.
Save complete exact output SAVED_PLOT_DATA.json, TEST_REPORT.json, READER_REPORT.json, START/FINISH and whole-resource record. Plotter reads saved results only, with scientific imports/calls0. Plot intended as two panels: feasible sextic/data windows plus aperture range comparison by N. Save any curve samples needed in the primary campaign; plotter must not recalculate science. Use ordinary-scale axes to avoid T13's 1e-14 tick overlap. Inspect actual PNG and preserve SVG.

## Execution and finite trust boundary
Root owns theory, source/physical interpretation, criteria, repair decisions and admission. Project policy requires lower-tier mechanical implementation/execution and a fresh nonauthor Astra scientific review before admission. Record requested model separately from runtime-observed model (null if unavailable).
Freeze and actually publish S05 source before primary execution; save execution pin and code/input hashes. Reuse the repaired namespace-aware T13 run_once.py execution mechanism, with task-specific paths and caps, without rerunning its old diagnostics. Preserve correct host/local PID accounting and whole runner+waited children measurements.
One new primary campaign: wholeCPU120s/wall300s/AS768MiB/threads1. One diagnosed targeted repair may consume the SAME remaining cumulative cap if root authorizes it. This allowance is for this new unit and does not replenish predecessor reserves. Preserve every failure and classify it correctly.
One new Wolfram evaluator, timeConstraint20s, checks generic factorization/normalization/weighted primitive/positivity and rational candidate identities. Remote CPU/wall null unless actually supplied. The preceding new context call succeeded with documentation and some semantic NoResultsFound; it is not a science evaluator run.
One saved-only PNG/SVG render, wholeCPU10s/wall30s/AS768MiB/threads1. No repeated successful science/test/CAS/plot. Transport failures may be retried with changed transport evidence while preserving the sealed archive and original failure.

## Stages, publication and final delivery
S01=R1/C1 through S10=R10/C10, 20 workproducts. Every completed pair receives actual source commit, expected-parent/nonforce ref update, ref/parent/tree readback, sealed unique ZIP, Drive+Dropbox ACK and size check before advancing publication. Raw provider receipts are external, never fabricated from plan fields.
Append exactly one ENDPOINT14-ZERO-ENDPOINT-SEXTIC-REFERENCE node to the existing17-node local scientific DAG. Start13complete+1partial+3physicalopen+1pending /18. Accepted14complete+1partial+3physicalopen /18. Central28/88 HEdelta0. Stage counters reflect scientific admission separately from20workproducts.
Drive folder1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI; Dropbox ns:183516487//BASS_DERIVATION_DOSSIERS_20260912/. Unique BASS_HE_ENDPOINT14_Sxx_20261028_<digest12>.zip. New local metadata/operations/checkpoints under publication14,operations14,checkpoints14,delivery_authorities14,final_delivery14; never overwrite T13 records.
Central update only established HE observation surfaces plus the new status record, using fresh actual expected_sha,force=false, and structural preservation checks. Preserve88nodes,17edges,15authorities,85nonHE, owners and unrelated result payloads.
Final external metadata_scope=POSTPUBLICATION_EXTERNAL_DELIVERY. S10 and PRE_CAS pending fields remain creation-time history. Final transport ACK goes in a separate external FINAL_DELIVERY_TRANSPORT_RECEIPT.json. Provide final package, substantive Korean result and copyable handoff. Stop after actual final delivery unless another explicit task arrives.

## Physical ownership and historical failures
Keep open: event/inclusive normalization+liquid-He electron/target-motion/response projection; actual full angular/polarization law+photon encounter flux/history; named nonthermal birth/deposition/thermalization+global species binding.
Binding sole owner=population_rest_energy_witness. independent_binding_RHS/Gamma_thermal/Cv/species_heating/thermal_deposition=null; birth_pool=UNASSIGNED; global_physical_completion=null; L4=false; production=NOT_APPROVED; activation=false.
Preserve T13 initial runner namespace failure+one targeted successful repair, QUARTIC12/EXFOR11/HARMONIC10 scoped completions, HARMONIC10 initial24PASS+1FAIL/targeted1PASS/reserve0, KINEMATIC08partial and PHOTON05plotCPUfailure. No predecessor result is rerun or rewritten.
