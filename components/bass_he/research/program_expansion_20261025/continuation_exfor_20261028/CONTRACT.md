# EXFOR11 — data-conditioned aperture reference contract
Date: 2026-10-28 KST. Parent scientific authority: root Astra. User explicitly requested one next complete R1–R10 and C1–C10 loop after surveying latest branches/conversations/repos/backups.
Unit: HE-EXP-EXFOR-11.
Repository: cosmosapjw-quantum/BASS_HE.
Branch to create: research/he-exfor11-20261028.
Owned path: research/program_expansion_20261025/continuation_exfor_20261028/.
Immutable predecessor P10 a73773a9e1056bf18405453a0e88b9d12a15e9ac; tree4e308ea37c6907f6b0064951e71d14667831a6a3.
Current local source is a restored partial source mirror, NOT a complete Git checkout. Execution identity will use the actual new publication commit and exact source/dependency manifest; never invent a local D commit.
HARMONIC10 is COMPLETE_SCOPED, original24PASS+1FAIL/targeted1PASS/reserve0 preserved. No old suite/CAS/plot/backup rerun.
Read BASS_HE/AGENTS.md and survey/github/central_AGENTS.md. Tiered contract→lower-tier coding→independent nonauthor scientific review applies.

## R1/C1 target and completion
Use the12 literal EXFOR M0475002 Table1 DCS rows to constrain a finite positive even angular family and rigorously bound coincidence acceptance ratios with inherited finite-mass/finite-detector geometry.
Use actual stored NIST rest energies A=3727.3794118 MeV, M=1875.61294500 MeV and e=213,258,330 MeV. Signature(-,+,+,+); c,hbar,k_B retained. A=m_alpha*c^2 and M=m_d*c^2 are rest energies, not a c=1 convention.
Angles46,61,73,87 degrees are exact nominal record angles. Angular experimental uncertainty is not supplied.
Observed ordinate f(theta)=DATA-CM, units nb/sr, ERR-S statistical. The declared sensitivity window is [max(0,y-ERR-S),y+ERR-S]; it is not a simultaneous confidence region, systematic uncertainty model or likelihood.
Measure model for this unit: reflection-even positive Bernstein DCS and explicitly DECLARED_AZIMUTH_UNIFORM. Actual full polarized law, lab target response and flux are unresolved.
Evaluate n=4 and n=8 separately, each with endpoint_zero=false and true. The true case enforces f(-1)=f(1)=0 as an explicit extrapolation assumption. This is motivated by Rice1998 p115 reporting Arends totals extracted from zero-endpoint Legendre fits; it is not an observed datum.
No changing error multiplier or degree after seeing outcomes merely to obtain feasibility. Empty families remain a scoped incompatibility of this model/window combination, not rejection of experimental data or a global no-go.

## R2/C2 sources and reuse
Official IAEA-NDS exfor_master exforall/M04/M0475.x4; source SHA256 b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f, latest file-changing commit5392fe533a7230d52147949b59ba8cd9b2f5c081 (historical import2022-10-02; record revision2016-04-26).
M0475002 rows in order by e:213→(.22±.04,.35±.09,.41±.09,.54±.10);258→(.08±.03,.23±.08,.16±.07,.25±.07);330→(.14±.03,.16±.05,.07±.05,.19±.05).
M0475003 total rows201,225,253,285,320,359 MeV remain an independent source table. None is equal to a DCS-row energy. Do not silently interpolate or join them.
Arends et al. PLB62(1976)411–412 DOI10.1016/0370-2693(76)90671-7; direct full article normalization still unresolved.
Rice1998 primary thesis pp114–115 Eq5.4 defines its total with2pi for identical daughters and discusses zero-endpoint Legendre extrapolation. It does not directly settle every Arends record convention.
No primary PDF or private conversation/gmail raw content in public source. Public research metadata, derived summaries, own code/raw calculations and official numerical data can be published under this user-authorized scope.
Dependencies are unchanged inherited harmonic.py→azimuth.py→kinematic.py→aperture.py. Reuse actual blob identities in survey/github/DEPENDENCY_FETCH_VERIFICATION.json. New calls using these dependencies are part of EXFOR11; old validation campaigns are not rerun.

## R3/C3 exact family and cosine enclosure
Let x=(mu+1)/2; n even; m=n/2. For j<m, psi_j=B_j^n(x)+B_(n-j)^n(x); psi_m=B_m^n(x).
f(mu)=sum_j a_j psi_j(mu), a_j>=0. For endpoint_zero=true set a_0=0 and remove that variable.
d_j=integral_-1^1 psi_j dmu=4/(n+1) for j<m, d_m=2/(n+1).
This coefficient cone is sufficient positivity only. Evenness/finite degree/azimuth uniformity are declared model assumptions.
Compute cos(theta*pi/180) with unchanged harmonic.sincos_turn(theta/720)[1]. This is an actual-angle enclosure, not a floating cosine reinterpreted as exact.
Evaluate each nonnegative Bernstein basis over the cosine interval by rational interval powers/products, then outward round each basis evaluation to a2^-60 grid. Preserve lower>=0 and strictly positive lower for the measured interior angles.
Write row vectors l_i<=psi(mu_i)<=u_i componentwise.
P_outer={a>=0: l_i*a<=U_i and u_i*a>=L_i for every i}.
P_inner={a>=0: u_i*a<=U_i and l_i*a>=L_i for every i}.
Then P_inner subset P_true subset P_outer, where P_true uses exact nominal cosines and literal sensitivity bounds.
A positive lower basis row and finite U give coordinate bounds a_j<=U/l_ij, so every polytope is bounded. At least one L_i>0 excludes a=0; normalization d*a>0.
No rounding of input DCS/error decimals through binary64; use Fraction strings.

## R4/C4 algorithm and proof obligations
Enumerate exact vertices of each finite polytope by all d-element active-constraint subsets, solve exact rational systems, skip singular systems, retain only exact feasible solutions and deduplicate. Nonnegative constraints are included. Closed bounded nonempty polytopes have vertices; no retained vertex means empty for this bounded finite contract.
Optimization of a linear-fractional functional c*a/(d*a), denominator>0, attains extrema at vertices: for a convex combination a=sum lambda_v v, ratio is the weighted average of vertex ratios with weights lambda_v*d*v/(d*a).
Record total bases attempted/singular/feasible and unique vertices. Cache matrix factorizations across3energy right-hand-sides when useful; do not conceal skipped candidates.
Inner/outer constraints use the same official table and family. Record any empty family honestly.
For any outer vertex v, objective lower uses c_lower*v/(d*v), upper uses c_upper*v/(d*v); global bounds are min lower and max upper. This encloses every true feasible family member. Inner witnesses demonstrate attainable nominal fits but geometry bounds remain intervals.
Provide witness coefficient vectors for each extremum and verify inequalities/denominators exactly. Store exact fractions and human-readable floats separately.
No black-box floating optimization may constitute a certificate. An optional floating oracle can only independently corroborate a saved small case, not replace exact vertex/feasibility evidence.

## Detector objectives and inherited geometry
For each energy build PhysicalAngularMap(A,M,e). Declare polar preimage delta=2^-48 fixed for new geometry.
Use inherited azimuth_pair_response with dummy positive uniform polar density to obtain strips/SetBounds once per geometry/energy. Only strips/sets are reused, not dummy numerical response.
Geometries:
FULL: A=B full polar[-1,1] and full-turn arcs; exact acceptance1 for every nonempty family.
HEMISPHERES: A polar[0,1] full-turn; B polar[-1,0] full-turn.
CAPS: A polar[1/2,1] full-turn; B polar[-1,-1/2] full-turn.
Integrate each nonnegative psi over every coincidence inner/outer interval union, multiply by exact azimuth strip width, sum to c_lower/c_upper. d is the same family full-sphere integral.
0<=c_lower<=c_true<=c_upper<=d componentwise. Return actual coefficient widths and global family objective intervals; do not claim a new universal2^-40 relative guarantee for ratios.
Acceptance p_C=(integral_C f dmu dt)/(integral f dmu dt). Global calibration,2pi, and event-vs-inclusive factor cancel if common positive scales; A common positive scale cancels separately at each fixed energy; angle-dependent response, or energy-dependent weighting inside an energy-integrated observable, does not generally cancel.
Do not equate detector-event probability with inclusive counts or independent daughters. Geometry C is inherited same-event Boolean coincidence.

## Bounded execution and controls
Requested coding executor gpt-6.1-sol (lower-tier) per current central AGENTS; actual runtime/model identity may be unobservable and must be labeled accordingly.
Astra/root authors mathematical contract/admission; lower-tier writes code/tests/runner/plotter/packaging. An independent nonauthor Astra reviews unchanged source, outcomes and figure in one complementary pass.
New science budget CPU60s/wall180s, address-space768MiB perprocess, threads1; initial scientific campaign1. Targeted repair allowance at most1 within same cumulative cap, only on diagnosed defect and parent authorization. No allowance borrowed from past units.
First save/publish implementation S05 and exact execution pin. Then run one bounded validation campaign that calculates actual tables/vertices/objectives and meaningful controls once. Static syntax/import checks must be recorded; avoid running full calculations during development.
Minimum control categories:
- parser/table identity12DCS+6total, no energy join, exact decimals/error bounds.
- n4/n8 symmetry, integral d, endpoint-zero law, sufficient cone scope.
- cosine and row interval containment against independent highprecision Decimal/Taylor or mpmath oracle, exact cardinal and invalid-angle checks.
- inner/outer implication via exact constructed polynomials, known LP vertices, known empty/bounded/degenerate cases.
- ratio extrema proof controls (constant objective, known interval simplex, common scaling).
- all actual3energies×2degrees×2endpointfamilies with feasibility outcomes, rational witnesses and coverage bounds; do not expect every family feasible.
- FULL ratio1; hemispheres/caps exact expected polynomial integrals in a rational-kinematic manufactured control, not inherited test replay.
- all stored inequalities, witness objectives and inner⊂outer checked by an independent exact certificate reader in the same primary invocation; counts reported as observed.
- invalid types/negativeerrors/missingdata/source identity, no silent float inputs, physical/null boundaries.
Save all raw stdout/stderr, exact JSON outputs, source hash pin, CPU/wall/maxRSS and attempt count. Do not round away failed results or turn runtime failure into a physical claim.
Wolfram evaluator one bounded20s call for selected new basis/integration/polytope ratio identities and exact analytic controls; context invocation SERVICE_ERROR recorded separately. Remote CPU remains null if not supplied.
Plot one saved-JSON-only PNG/SVG, CPU10s/wall30s,768MiB,threads1. Read the actual image. Plot data bands/degree/endpoints/acceptance values using stored results; no scientific functions/imports or old plot regeneration. Fix actual blocking layout faults only if diagnosed; record any additional attempt.

## Stage publication, DAG and closure
Use10 paired checkpoints S01=R1/C1,...,S10=R10/C10. Each has substantive work for both tracks and one distinct source publication plus Drive and Dropbox archive ACK.10paired checkpoints are20work products, not20independent uploads.
S01 scope/baseline/DAG;S02 source synthesis/equation-code mapping;S03 claims/algorithm;S04 choice/derivation/resources;S05 theory+implementation/staticreview;S06 independentmath+implementationvalidation;S07 discriminants/science/CAS;S08 judgement/numerics/plot;S09 formalresult+finalindependentreview/admission;S10 closeout/handoff.
Append one scoped local node EXFOR11-DATA-CONDITIONED-APERTURE-REFERENCE to inherited14. Start10complete+1partial+3physicalopen+1pending/15; adoption11complete+1partial+3physicalopen/15. Do not increment for20workflow stages.
Central remains28/88 with HE delta0 unless actual newphysicalclosure evidence legitimately changes it (none currently supplied). Current observedcentraldf806909aee8f25efcfa4faeefca77a5271f546c; freshHEAD required for finalHE-onlyownerreturn.
Use base tree+only owned newpaths for source publication; expected_sha forcefalse for every existing ref mutation. Preserve all foreign changes. Final central publication appends oneHEreturn pointer/status and scoped metadata, with actual currentHEAD/AGENTS/readback; no non-HE node edits.
EstablishedbackupfolderDrive1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI; Dropboxns:183516487//BASS_DERIVATION_DOSSIERS_20260912. Newnames BASS_HE_EXFOR11_Sxx_20261028_<manifestprefix>.zip. ActualACKs external/next-stage recorded; do not inject futureACKs into sealed ZIP.
Final delivery authority metadata_scope=POSTPUBLICATION_EXTERNAL_DELIVERY; sourcecreationflags remain PREPUBLICATION snapshots.
Preserve all three physical open nodes, population_rest_energy_witness solebindingowner, independent_binding_RHS/Gamma_thermal/Cv/species_heating/thermal_deposition=null,birth_pool=UNASSIGNED,globalphysicalcompletion=null,L4=false,productionNOT_APPROVED,activationfalse.
No globalnovelty/strongno-go claim; NG1–NG7 recorded notadmitted because finite model-sensitivity results are the intended contribution.
Stop after this new loop and actualfinaldelivery; noautomaticEXFOR12.

