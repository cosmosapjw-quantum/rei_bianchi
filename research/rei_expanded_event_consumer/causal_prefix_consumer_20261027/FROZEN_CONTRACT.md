# REI causal prefix consumer — frozen contract
Unit REI_CAUSAL_PREFIX_CONSUMER_20261027; physmath-research-loop1.0.0.
Root scientific authority /root. Base PR239 c0e76fb13785dd6aab45e056ee54d2b318ca8f41; AGENTS6464cd96b7023e3e91e30246bc93650d4e435a10.
Working32/88, central5abe0d19df95db730e3e33bae0373c81ba37ce89 declared27/88. Original node delta0; L4false/globalphysicalcompletionnull.
Goal: consume the CR108 two finest actual finite-age exports, preserve one pulse's cumulative correlation, derive sharp contiguous-window bounds in the interval-monotonicity information polytope, and lift a common N/E basis to native25+retained-photon ports with explicit normalization and proper/eta bin-average semantics.

## Input and scope
Provider repo cosmosapjw-quantum/bass_cr, PR108, branch research/cr-rr-causal-clock-20261027, frozen containing commit2776752de6952f60d8d690a128f33fec4df2c57b.
Two cases chi1.5_R80_N2048 and chi3_R80_N2048; each three source-z alternatives2.316,2.479,2.649. Seven horizons proper seconds0,1000,10000,100000,300000,1000000,10000000. Six disjoint bins per source:36 actual bin events,126 contiguous source windows,252 scalar N/E window bounds.
Exact input paths: research/cr_rr_causal_clock_20261027/runs/cr_clock_primary_20261027_v1/payload/{case}_SUMMARY.json and {case}_BIN_EXPORTS.json.
Expected Git blobs: chi1.5 SUMMARY7ae97b5efa9426a64dff7aa9582d14332d9da73b; BINf95c48d581816d86b3a7b16cb8ad7dff7c3a7813. chi3 SUMMARYba9a32016c768c7bee5d05183f17140090f7f509; BIN67d9e8d3c7c47a5de824d1c1c67fd7e8257bd9c7.
Copy raw UTF8; integers above2^53 must never roundtrip through JS Number. Scientific importer uses Python json integers and exact values of binary64 interval endpoints (Fraction.from_float / float.fromhex). Source documents/binary64 intervals are immutable inputs; no K/solver/clock tail/source projection recomputation.
Retain case/source/operator/bath/projection identity and actual canonical_event_id. Source alternatives are not additive histories. Cumulative views are not extra events in the disjoint event book.
Current public provider state C08/18of20; final executed C9 not published at intake. Conversation says C9passed but exact Git C9_PREEXEC_REVIEW is PASS_STATIC_AFTER_TARGETED_REPAIR_PENDING_EXECUTION. Preserve this discrepancy; conditional consumer algebra cannot promote provider qualification.
Actual continuous injection/history, recipientnb, physicalpointwiseRHS, exposure, spectrum, physicalstopping remain null. Source time_basis=comoving_proper_seconds and frame=bath_frame_rest_target. He4III12→He4II11(1s), conditional elementalHe→He4, stationaryheavy/zerorecoil, scalarisotropic, groundspontaneous, frozenbath asPR107/108.
Source interval target is exact represented saved K,w,r. Physical/model/continuum errors and unknown extra N/E correlations are outside the represented information set.

## Derived information polytope
For each source and each of countN[cm^-3], kineticE[eV cm^-3], let F_i be the same unknown cumulative reward at ordered T_i.
P={F: L_i<=F_i<=U_i, F_i<=F_(i+1), F_0=0, F_i<=P_upper}.
Enforce exact zero horizon, finite values, source ordering and all-time cap. Nonnegative lower may be strengthened by0; an inconsistent interval or l_i>u_i must fail rather than clip to a success.
l_i=max(0,L_0,...,L_i); u_i=min(P_upper,U_i,...,U_m). P nonempty iff l_i<=u_i for all i.
Both l,u are feasible monotone chains. For0<=a<b<=m,
D_ab=F_b-F_a lies in [max(0,l_b-u_a), u_b-l_a].
Sharpness is solely over P; not over the fixed-K semigroup family.
Upper witness: F_i=l_i fori<b, max(l_i,u_b) fori>=b.
Lower witness: c=min(u_a,l_b); F_i=min(u_i,c) fori<a, max(l_i,c) fori>=a.
Verify witnesses against original intervals, cap, F0 and all adjacent monotonicity.
Telescoping sum_i(F_i-F_(i-1)) must be taken before interval bounding. Compare actual canonical independent-bin sums as a deliberately looser enclosure; record widths and gain, not a new physical error bound.
General normalized endpoint objective atfixed b_a,b_b>0 is F_b/b_b-F_a/b_a. Its information-polytope range can be computed from the rectangle [l_a,u_a]×[l_b,u_b] clipped byx<=y: feasible rectangle corners plus diagonal endpoints max(l_a,l_b),min(u_a,u_b). Do not claim differentiability of a selected max/min vertex.

## Correlated physical map
Common basis N_cm3,E_eV_cm3; countSI=1000000*N, kineticSI=1000000*eV_J*E; eV_J=801088317/5000000000000000000000000000 J/eV; I_eV=2721/50.
All source EXACT_RATIONAL signed-map coefficients must be checked once against these source definitions, preserving all seven reservoirs and zero external/thermal/recoil/escaped terms.
At explicit constant consumer b>0, unchanged native25 order(Y[21],zeta,w_nt,w_ext,logT):
DeltaY11=n/b,DeltaY12=-n/b,Deltazeta=-n/b,Deltaw_nt=-e/b; every othernativeentry0. Separate photoncount=n/b,photonenergy=(e+I_J*n)/b, bindingchange=-I_J*n/b.
Sum species=0, charge q11=1,q12=2 with qDeltaY-Deltazeta=0, thermalparticle=(1+q)DeltaY-Deltazeta=0; binding+fast+photon=0 exactly for the same pair.
No independent reservoir-corner joint event. Product P_N×P_E is an outer information set, not complete unknown physical source correlation. Feasible witnesses certify the information set only.
Default missing b gives proper-volume joint map and null nativeprojection. b=1400000m^-3 is an explicit consumer fixture; not supplied recipientnb. Diagnostic27 flattening is not a new27state ODEclient. Physicalstateupdatefalse.

## Reference and clock derivatives
At a frozen feasible basis witness and fixed source bin, f=N orE, scale s>=0,
integrated=s*f/b, JVP=ds*f/b-s*f*db/b^2.
Conditional proper-bin average=s*f/(b*dt), dt=T_b-T_a>0; JVP includes -s*f*ddt/(b*dt^2) when dt is explicitly treated as an interface divisor. No derivative of the unknown source with horizon is inferred.
For supplied dimensionless deta>0, etaaverage=s*f/(b*deta)=(dt/deta)*properaverage; corresponding full quotient JVP. Missing deta gives etaaverage=null.
Integrated event is clock invariant. An arbitrary endpointH is not the general finite-bin conversion. Manufactured clock only: eta(T)=T/Tstar+(T/Tstar)^2,Tstar=10000000s; deta=dt*(1/Tstar+(T_a+T_b)/Tstar^2). Actual cosmological eta clock is not supplied.
At varying reference endpoints and frozen latent witness F_a,F_b:
normalizedstatechange=s*(F_b/b_b-F_a/b_a)
event_at_endpoint=s*(F_b-F_a)/b_b
referencecorrection=s*F_a*(1/b_b-1/b_a)
statechange=event_at_endpoint+referencecorrection.
Differentiate s,b_a,b_b fully; no silent omission of either quotient term.
Use b_i=1400000*(1+i/20)m^-3 only as a manufactured positive reference fixture; s=7/10,ds=11/100,db_i=(13/100)*b_i for the constant-b/binaverage direction; endpoint use db_a=.13b_a,db_b=-.07b_b.
Old continuous convention dotr+3Hr=Rr,Fx=(S-xRr)/r and its full derivative remains inherited. Endpoint state change is not an inferred integral of j(t)/b(t) for an absent variable physical history.
Do not export a smooth Jacobian of max/min extrema at kinks. Derivatives refer to frozen witnesses/interface divisors only.

## Code and acceptance
Purestdlib consumer; O(7) chain enclosure, O(1) window after closure, bounded vertices for normalized endpoint. No old scientific imports.
Main exact values and bounds use Fraction; expose readable floats by directed outward rounding using nextafter and exact rational comparisons. Keep rawrational endpoints in output; no tolerance floors or midpoint-as-truth.
Actual252 scalar windows: sharp formula+independently constructed extremizing witnesses; direct 2endpoint feasible-corner oracle; actual36 canonical bin containment and exact rational source maps; telescoping36bin allocations and126 source windows.
Positive/zero and invalid controls: infeasible temporal intervals, alltimecap contradiction, nonzeroT0, unordered time, source/case/operator mismatch, overlapping/duplicate/cumulative-as-extra events; zero/nonfinite/bool normalization, invalid bin widths; missing b/eta must remain null.
Scalar-map identities exact; outwardfloat intervals must contain exact rational values with no tolerance. JVP: independent rational closed form and centered floatFDh2e-4,1e-4 on each of6source fullwindow witnesses plus36bin averages as feasible under bound. Relative residual uses sum of absolute analytic physical operands, zero rows exact0. Frozen FDcriterion2e-8. No fullJacobian/convergence-order claim.
Discriminants: independent reservoircorner nonzero energy residual; repeated cumulative+bin invalidbook; missing referencecorrection or db terms; endpointH replacing interval clock; JS roundedinteger metadata detected from exactgammahex ratio.
Produce one saved OBSERVATIONS.json/JSONL, compact CHECKS.json/JSONL with actual counts/results, full36bin table, rawstdout/stderr, resource receipt, manifest.
One actual new scientific attempt only. No automaticrerun. C5root/independent preexecGO before C6.
Scientific total reserve.18CPU s: childtarget.12,wrappertarget.04,tail.02; one worker,512MiB,wall5s, hardCPU1s failsafe. Stop on scientific failure, preserveoutputs; root classifies and authorizes only evidenced repair withinremainingcumulativebudget.
Implementationprep .06, independentreviews .08, root+additiveDAGmetadata .045 prospective. Knownplanning14.611466549 before these; temporary14.99. Presentation42.140963211 inherited,temporary44.99. Original10/30 restoredafterunit; no resets/transfers. Main595.225063/600NO_MORE_IVPs and foreignownerbudgets unchanged.
Stage/checkpoint serialization and archives charge presentation; semantic/physics checks charge planning; unmeasured costs UNKNOWN_NOT_ZERO.

## Reuse, representation, publication
Reuse PR219 bootstrap, old83, GRID044 opacity, PR221conditional, PR233/235/236/237/239 and actualCR source certificates undertheirqualifications. GRID044 is a cosmologicalhistory artifact, not a44pointphotonenergygrid; the initial moment-grid candidate was corrected before freezing.
No new83,NCP,IVP,producer solves,source projection,spectral quadrature,oldfullsuite,priorattempt replay.
Reuse previous actual plot where useful; new aggregate width visualization, if made, uses saved consumer values only with measuredpresentationcost and actualview. ColdMatplotlib'sprevious4.97CPU is outside thisunitremainingpresentationallowance; do not repeatit.
R1–R10/C1–C10 each gets own expectedSHA/nonforcepublication plus immutableincrementalZIP and Drive/DropboxcompletedACK. Finalfullunit/sourceinputsZIP and separatepostarchiveACKmetadata. PriorPR239sourcesstaypinned; no clone/worktree.
DAG update is additive REC-COUPLED consumerpointer+return, preserving priorcontracts,88IDs17edgescounts; use exact insertion and removal equality, reuse prior frozen-DAG proof rather than fullDAG rescan.
Root owns finaladmission; code author and independentreviewer separate. NG1–NG7 considered: no newstrongno-go ornoveltyclaim; main result is constructive bound and implementation.

## R6 clarification before code freeze
Raw prefix/window bounds remain in N_cm3 and E_eV_cm3. Every normalized map or reference/average JVP first uses SI F (c_N=1000000, c_E=1000000*eV_J) exactly once; generic f below denotes the corresponding SI reward, not an unconverted raw component.
The clipped pair polygon includes diagonal vertices only if d_lo=max(l_a,l_b)<=d_hi=min(u_a,u_b). No-overlap cases use feasible rectangle corners only.
Nonzero frozen interface divisor directions: ddt=(17/100)*dt and ddeta=-(9/100)*deta, independently supplied positive-divisor perturbations, not a source horizon derivative. Retain FD steps/tolerance.
Add six nonzero-start [a=1,b=6] reference endpoint witnesses and JVP controls, so F_a>0 makes omitted reference correction and db_a detectable; retain the six full-window and36 bin-average checks. This closes R6 ambiguity without changing model, source, tolerance or claim.


