# QUARTIC12 — full nonnegative even-quartic positivity sandwich
Root Astra scientific contract; 2026-10-28; workflow1.0.0.
New user authorization after EXFOR11 COMPLETE_SCOPED: one next R1–R10/C1–C10 loop, actual source publication and Drive/Dropbox backup per paired stage, actual central return and copyable final handoff.
Unit HE-EXP-QUARTIC-12; owned path research/program_expansion_20261025/continuation_quartic_20261028; branch research/he-quartic12-20261028.
Predecessor actual S10=1e393c7901d08aaf97c4c3568ef4ab120d43e9c5, tree7c33ed3f6a9b88402ff9c0ebe7b45840202b7fef. Current local is a partial restored source mirror, not a full Git checkout; no invented local D commit.
Fresh survey must finish before first new scientific execution. This preparatory mathematical contract selects the candidate whose relevance is checked against fresh intake.

## Goal and preserved assumptions
Determine rigorous bounds for the FULL nonnegative even quartic family f(mu)=q(mu^2), q(z)=b0+b1*z+b2*z^2 >=0 for all z in[0,1].
Coefficients b may have either sign. Two physical model choices: endpoint-free and q(1)=0.
This removes EXFOR11's sufficient nonnegative global Bernstein coefficient restriction at degree4, without changing physical masses, energy/angle/data windows, detector geometry, azimuth assumption or experimental errors.
Fixed official M0475002 12 rows and disjoint M0475003 totals from predecessor; source SHA256 b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f.
Use unchanged exfor_aperture.parse_source/geometries, harmonic trig and lower dependencies by pinned identity, no old suite/campaign/CAS/plot rerun.
(-,+,+,+); c,hbar,kB retained. Rest energies A=3727.3794118MeV, M=1875.61294500MeV; e213/258/330MeV. Azimuth uniform declared. ERR-S coordinate windows remain sensitivity choices, with no covariance/confidence/independence claim.
No joining/interpolating the disjoint total-cross-section energy grid.

## Mathematical coefficients and outer compactness
b=(b0,b1,b2); d=(2,2/3,2/5); D(b)=d.b=integral_-1^1 f(mu)dmu.
Use three nominal z values from angles46,61,87. Verify their certified z intervals are pairwise separated by at least g=1/5 and lie[0,1]. Every true feasible ordinate has0<=y<=1.
Lagrange interpolation of q at these3points gives coefficient absolute bounds (75,150,75): each reciprocal denominator <=25; numerator coefficients bounded by(1,2,1); sum of3 ordinates<=3. Thus the uniform bound |b_j|<=B=160 is a proven containing box. It is not fitted after outcomes.
Use all4 original nominal angles for data constraints.

For each theta compute certified mu=cos(theta*pi/180) with inherited H.sincos_turn(theta/720)[1], then exact nonnegative interval powers z=mu^2,z2=mu^4, outward rounded to2^-60 independently. Use row midpoint m=(1,mid(z),mid(z2)) and
epsilon_i=B*(width(z)+width(z2))/2.
For every b in box, |q(z_true)-m.b|<=epsilon_i.
Data outer: L_i-epsilon_i <= m_i.b <= U_i+epsilon_i.
Data inner: L_i+epsilon_i <= m_i.b <= U_i-epsilon_i.
All values are Fraction inputs, never binary64-reinterpreted-as-exact.

## Positive normalization floor
At theta87, each energy's literal lower bound >=L*=7/50. |f'(mu)|<=2|b1|+4|b2|<=6B.
For delta=L*/(12B), the certified mu87±delta is inside[-1,1]; f>=L*/2 there for every true feasible f.
Therefore D>=Dmin=L*^2/(12B)=49/4800000. Add the linear D>=Dmin constraint to both inner and outer. This is implied by the true family, not a new physical assumption.
Use exact Dmin; all saved vertex denominators must meet it.

## Positivity sandwich, fixed resolution choices
Endpoint-free cases: N in{1,4,16}, fixed before outcomes, nested uniform grids z=k/N.
Outer positivity: q(k/N)>=0 at every grid point.
Inner positivity: all quadratic Bernstein controls on each cell [l,r] nonnegative:
beta0=q(l);
beta1=b0+b1*(l+r)/2+b2*l*r;
beta2=q(r).
Duplicate identical constraints may be removed exactly, with counts retained.
Combine these with data constraints, box and Dfloor. Then Pinner_N subset Ptrue subset Pouter_N.
Under nested subdivision the inner sets enlarge and outer sets shrink. Document actual finite-N gaps, not a promised universal convergence tolerance.
Outer nodal certificate yields q(z)>=-max(b2,0)/(4N^2) on every cell. Inner controls suffice by convex hull. Strictly positive q with positive margin eventually has positive controls; zero-touching boundary polynomials need not enter a finite inner set. Do not claim unqualified finite-inner completeness.

Endpoint-zero case is exact linear positivity, calculated ONCE per energy instead of repeating it for every N:
write parameters v=(b0,b1), b2=-b0-b1.
q(z)=(1-z)[b0+(b0+b1)z].
q>=0 on[0,1] iff b0>=0 and 2*b0+b1>=0.
Apply these two inequalities to both inner/outer plus transformed data, all3 box constraints and Dfloor.
Case set is12 unique cases:3energies*(freeN1/freeN4/freeN16/endpointzero_exact). No higher-degree or error-window changes after results.

## Exact vertices and observables with signed coefficients
Enumerate every r-active-constraint combination, exact rational inverse, skip singular, verify all inequalities, deduplicate; reuse coefficient-matrix inverses across3energy RHS when identical. Reuse unchanged EXFOR11 inverse/enumerate utility if suitable; don't invoke its campaign.
The box makes each polytope compact; every nonempty polytope has vertices, so exhausted empty vertex list proves that specified outer polytope empty. Distinguish attempted bases, singular, feasible bases, unique vertices and actual inversions/RHS candidates.
Save all matrices/RHS/vertices/counts as exact fractions, separate floats for display.

Use inherited same-event FULL/HEMISPHERES/CAPS strips at fixed delta2^-48 once perenergy/geometry (9calls).
For monomial basis (1,mu^2,mu^4), primitive integrals are (h^(2j+1)-l^(2j+1))/(2j+1); derive k_j^-<=integral_C mu^(2j)<=k_j^+, 0<=k^-<=k^+<=d.
At each signed coefficient vector b, numerator interval:
nlow=sum(b_j*k_j^- if b_j>=0 else b_j*k_j^+);
nhigh=sum(b_j*k_j^+ if b_j>=0 else b_j*k_j^-).
Lower is concave in b and upper convex. With positive linear D, minimum of nlow/D and maximum of nhigh/D over a polytope occur at vertices by denominator-weighted Jensen. Prove this extension rather than applying positive-coefficient formula unchanged.
Outer raw range [min_Vout nlow/D,max_Vout nhigh/D]; physical certified range intersects[0,1].
For feasible inner vertices, actual objective is inside their interval.
Minimum bracket: [outer_lower_clipped, min_Vin nhigh/D].
Maximum bracket: [max_Vin nlow/D, outer_upper_clipped].
These inner quantities are attained-witness bounds, not a full attained-range equality. Empty inner yields null witness-bracket endpoint; empty outer yields allobjective null. FULL=1 exactly whenever nonempty.

For each inner vertex independently classify exact quadratic positivity by endpoints and stationary minimum when b2>0, -b1/(2b2) in(0,1).
Select deterministic inner witness for each nonempty case, store qminimum exact, data intervals, coefficients and old EXFOR11 degree4 folded Bernstein coordinates:
a0=b0+b1+b2; a1=b0-b2; a2=b0+b2-b1/3.
Inspect330MeV freeN4/N16 witnesses. Negative a demonstrates a valid positive polynomial outside old sufficient cone; preserve old correctly scoped EMPTY, do not rewrite it as an implementation failure.
Read unchanged prior saved result/hash for comparison, do not recompute it.

## Controls and bounded execution
Primary science CPU120s/wall300s/AS768MiB/threads1; one initial campaign. One diagnosed targeted repair within same cumulative remaining cap only after root authorizes; no automatic retries. Preserve raw failures. If cost unexpectedly exceeds cap, save progress and return exact diagnosis, not a no-go.
Plot CPU10s/wall30s/AS768MiB/threads1; one saved-only PNG/SVG. Actual image review, no scientific import/recalculation in plotter.
Wolfram one new bounded20s evaluator for control formulas, normalization, endpoint factorization, old coefficient map and analytic signed/Jensen controls. Current context response is successful documentation/no numerical result, distinct from earlier EXFOR11 context error; remoteCPU null unless actually supplied.
Record whole runner+waited-child CPU/wall and separate outer-orchestration scope, not fake model/provider total.

Meaningful new controls: signed angle row perturbation with known polynomial; B proof separations and Dfloor derivation; exact quadratic positivity vs Bernstein-cell controls including positive polynomial with negative global control; endpoint factorization+exact cone; nested mesh and known negative-between-nodes outer example; exhaustive known rational polytopes/empty/degenerate signed cases; signed moment integration using manufactured rational geometry; ratio lower-concave/upper-convex control; all saved inequalities, Dfloor, exact quadratic positivity of inner vertices, extrema+witnesses, FULL, sourceandphysicalnullboundary.
Independent saved certificate reader is not a second optimizer and must not be reported as one. Count actual control methods honestly.
Make source S05 actually published and execution manifest before the one primary campaign. Static compilation preparation only; no scientific execution before root GO.
Requested lower-tier code executor gpt-6.1-sol (existing implement_exfor11 agent); observed runtime identity null if unexposed.
Root owns science and admission. survey_github does fresh source intake only and remains nonauthor for one review pass from source through results/figure/metadata.

## Publication, counters and stop
10paired checkpoints S01=R1/C1...S10=R10/C10,20actual workproducts. Each new sourcecommit+Drive+DropboxactualACK; creation snapshots preserve their time.
Inherited15localnodes retainstatuses; append QUARTIC12-FULL-POSITIVE-QUARTIC-REFERENCE. Start11complete+1partial+3physicalopen+1pending/16; accepted12complete+1partial+3physicalopen/16.
Central28/88 HEdelta0 unless actually justified new physical evidence; this reference supplies none of the3missingphysicalinputs.
FreshcentralHEAD/AGENTS before metadata-only9HEpath publication; expected_sha actualhead,forcefalse,readback. PreserveallnonHEchanges andWU sourceownership.
Drivefolder1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI; Dropboxns:183516487//BASS_DERIVATION_DOSSIERS_20260912. Newarchives BASS_HE_QUARTIC12_Sxx_20261028_<manifesthash12>.zip. Existingfinishedarchivesneverregenerated/reuploaded.
Final external metadata_scope=POSTPUBLICATION_EXTERNAL_DELIVERY; fourauthoritydocs+finaltransportreceipt. No futureACK inserted into sealedZIP.
Physicalinputs3open; binding soleowner population_rest_energy_witness; independent_binding_RHS/Gamma_thermal/Cv/species_heating/thermal_deposition=null; birth_poolUNASSIGNED; globalphysicalcompletionnull,L4false,productionNOT_APPROVED,activationfalse.
Preserve EXFOR11 single6PASS0FAIL,21zero8True,plotPASS; HARMONIC10 initial24PASS+1FAIL+targeted1PASS,reserve0 and earlierpartialworkflows.
Do not claim a strong global no-go. Record NG1-NG7 against any finite model exclusion; no literature-wide novelty assertion. Stop after this one new loop and finalactualdelivery until next explicittask.

