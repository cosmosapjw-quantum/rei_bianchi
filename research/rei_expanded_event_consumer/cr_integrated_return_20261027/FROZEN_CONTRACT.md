# Frozen REI CR integrated-return consumer contract
Unit REI_CR_INTEGRATED_RETURN_20261027, physmath-research-loop1.0.0.
Root authority: current user continuation and persistent publication/dual-backup authorization.
Base ee6746ab172f862dddfdec63b59e5e3707b59eaa; working DAG32/88, central5abe0d19df95db730e3e33bae0373c81ba37ce89 declared27/88.
Scientific target: consume the actual24 CR diagnostic alternatives, derive and implement exact normalization/JVP and clock-invariant pairing to unchanged native25 plus a separate retained-photon number/energy port. No physical finite abundance step is applied.

## Inputs and ownership
CR science4e72c89b714431eb4c6ae07def777bbf72a5ae4c, deliveryec463db0c7e5c7fb5070796071c926caa4db6445, PR107.
INTEGRATED_EVENT_EXPORTS Gitblob3284a00148f5e16522f1c28e5db350f345c2b797, SHA256c6da1e2f8a079c123ab218875c27bd6f5bc73beb5465832cc28a9275b455e1b1,91839bytes.
Reuse unchanged exporter validation and admitted24 alternative rows, not source generators/solvers. Pin copied exporter and native21 species/charge/binding coefficients. Never sum the24 numerical/source alternatives.
Native reaction He4III12 + taggedfast electron -> He4II11(1s) + retained photon. Native binding difference54.42eV, eV_J=1.602176634e-19; compare cumulative floating sums by residual.
Fixed actual provider bathT10000K, ne.14cm^-3, nHeIII.01cm^-3, HI/HII/HeI/HeII/HeIII=(.9,.1,.07,.02,.01)cm^-3; elemental-He-to-He4 conditional, stationary heavy/zero recoil/nonrelativistic scalar isotropic/ground spontaneous/frozen baths. Photon support54.42..50000eV. No resampling or spectral reconstruction.
Actual exported nb, exposure, rate, instantaneousRHS, history, spectrum, physicalheating remain null; finite_coupled_abundance_update/state_update_applied false. Provider legacy source_commit identifies earlier stored-chain source, distinct from actual export-containing4e72. Preserve both.
Use A=Ncap>=0 [m^-3], K=-fast_kinetic>=0 [Jm^-3], G=storedradiation>=0 [Jm^-3]. Preserve suppliedG, all7reservoirs, canonicaleventID, frame andqualification. Original source energy criterion abs(G-K-I*A)/(abs(G)+abs(K)+abs(I*A))<=2e-13. No repeatedSI conversion.
WU nuclear activation and REC/HE/BASS/VigilODE authorities are inherited actualdomains; none authorize a new rate/history/spectrum. PR219/old83/GRID044/PR221/PR233/235/236/237 evidence reused.

## Mathematical interface
A positive explicit consumer b=nb is required for a per-baryon diagnostic. The production reader with no b returns proper-volume data and null native projection; never infer b from PW19 donor or CR bath. Tests use b=1.4e6m^-3 as a declared consumer normalization fixture only; no donor-state admission.
Let a=A/b,k=K/b,gamma=G/b. Paired output: native25 DeltaY11=a,DeltaY12=-a,Deltazeta=-a,Deltawnt=-k; all othernative entriesincludingwext(index23)andlogT(index24) exactly0; photonport (DeltaNgamma=a,DeltaWgamma=gamma).
Flattened27 view is diagnosticserialization only: native25indices0..24 unchanged; appended25=count,26=energy. All density-like indices0..23,25,26; logT24 never scaled. This is not a new27state ODEclient.
Charge/nuclear identity, thermal-electron delta qDeltaY-Deltazeta=0, thermal-particle delta(1+q)DeltaY-Deltazeta=0. Native binding+fast+retained energy=(-I*A-K+G)/b. No thermal power or external ledger consumption.
For interface directions dA,dK,dG,db, da=dA/b-a*db/b; dk=dK/b-k*db/b; dgamma=dG/b-gamma*db/b. They are input-interface derivatives, not exported CR physical parameter sensitivities. Keep all3moment directions independent in API. Conservative tangent subspace dG=dK+I*dA is explicitly selected for energy-tangent checks; incompatible directions return the correct nonzero constraint derivative rather than falsely claiming conservation.
Reference b=beta*r: DeltaX=beta*DeltaZ on density rows and dDeltaX=beta*dDeltaZ+dbeta*DeltaZ. Impose db=beta*dr+r*dbeta in consistency tests; verify direct physical/r result and cancellation ofbeta. No floor max(1,tiny).
Integratedincrements are independentofclock H; proper/eta integratedpacket identical and d/dH=0. Reject calling it a rate or dividingbyH/exposure. ExistingPR237 continuousRHS contract is untouched.
Separate algebra-only endpointreference utility atfixed physicalvolume: xplus=(rminus*xminus+Deltan)/rplus for density rows; tangent=(rminus*dxminus+xminus*drminus+dDeltan)/rplus-xplus*drplus/rplus. logT ispassedthrough unchanged withtangent. No physicalhistory supplied or expansion step claimed. Continuous reference convention stays dotr+3Hr=Rr,Fx=(S-xRr)/r withfull quotientderivative, reusedfromPR237.
Nonnegative-state diagnostic admissibility: for nonnegative density capacities nHeIII,Nfast,Ufast and A,K>0, amplitude smax=min(nHeIII/A,Nfast/A,Ufast/K); zeros yield explicit unconstrained bounds/null serialized infinity. This is a capacity certificate for a manufactured candidate, not an applied step or submeasure/history qualification. Fixture capacities nHeIII=1e4m^-3,Nfast=1m^-3,Ufast=100eV_J Jm^-3. Evaluate s=0,.25*smax,smax,1.01*smax onlyin declared manufactured controls, nonativephysicalupdate.

## Implementation and predeclared acceptance
Owned paths only thisnewunit; preserve priorunits andoriginalDAG. Purestdlib implementation/checker preferred; source copying doesnot authorize oldmoduleexecution.
C5: consumer, checker, boundedrunner, exactinputmanifest, command, rawoutputsJSONL andfull24map table, no scientificrun untilrootauthorizes frozenhashes.
C6-C8 one bounded attempt, failfastwithpreservedrawstderr/exit/resource receipt. No automaticrerun. One worker/OMPBLAS1,512MiB,wall8s. ScientificchildCPUcap.75s; wrappercap.10s; combinedreserve.90s including .05tail. Only root mayauthorize diagnosticrepair withinremainingcumulativebudget.
For actual24: inheritedenergyclosure2e-13; new algebra/projection/independentDecimal50 oracle2e-14 scaled by sumofabsolute physical operands, exactzeroentries exact0. JVP compare independent quotient and mixedFD two steps h=2e-4,1e-4 with same frozenanalyticoperand scales and criterion2e-8; no universalconvergenceorderclaim.
Frozenmixedrelative direction dA=.11A,dK=-.07K,dG=dK+I*dA,db=.13b,dbeta=-.09beta, beta=1.7,r=b/beta,dr=(db-r*dbeta)/beta. Endpoint fixture usespositiveexplicit rminus=2,rplus=3, x_i=1 for densityrows,ell=log(10000), drminus=.13*rminus,drplus=-.07*rplus,dx=.11x (logT.03), Deltan constructed fromscale-amplified actualevent with s=.25*smax; directionsapplyds=.17s andnativevector tangent; physical capacities arefixtureonly.
Controls: zeroevent/zeroamplitude; missing/negative/nonfinite/bool b/frame/channel/support/duplicateevent/alternative-batch guard; unchangedzero n/Trows0,5,6; no rate/historyfabrication. Negative andwrong-sign energy/tangent handlingexplicit.
Discriminating mutations: dropfastcount, routeGalsotowext, thermalizeK, missingdb, missingdbeta, use/H, omitendpointdrplus, wronglyrebase logT. Checknonzero signatures usingrow-specificunits; no irrelevant mutantfor identicallyzerologTincrement.
Preserve24rawobservations andnumericqualifications; useDecimal independentlywrittenexplicitrowformulasforreference, notcallingconsumerfunctiontoformexpected.
Figure: savednewoutputonly, two-panels actual24 retainedenergy/count groupedby3zand8case alternatives plus reference/clock mutant residuals asrelevant; donotdrawhistoryoruncertaintybands. One Matplotlibrender<=4CPU/8wall/512MiB underpresentation. Root+independentrevieweractuallyview it. No newphysicscalls fromplot.

## Budgets, stages, publication
Preserve inheritedplanning13.297430367 andpresentation33.948087957CPU. Temporaryceilings14.9/44.5 authorized byworkingAGENTS6464cd96b7023e3e91e30246bc93650d4e435a10 (<50%overoriginal10/30). Restoreoriginalceilingsafterunit,neverresetcumulative.
Observedrecoverydownload.149425973CPU andextract.184582739CPU arepresentationdebits. Extraction exceededitsprospective.15jobestimate by.034582739; preserveoverrunrecord,noretroactivePASS. No scientificrunwasperformed. Newhelperjobbounds mustallow actualmeasuredrestorationclasscost.
Suppliermetadata.00459858CPU planning; otherlocalmetadataactualsappend; remote/tool/LLM/startupunknownUNKNOWN_NOT_ZERO. Entirecostnotcertifiedbyknownsubtotal.
Main595.225063/600NO_MORE_IVPs unchanged; CR6.988054525/30belongsCR; HE101reserve0,V6closedleasepreserved; no budgettransfer. New83/NCP/IVP/fullsuite/quadrature禁止.
R1..R10/C1..C10 exact20stages, perstageowncommit/nonforceexpectedSHA andimmutablecheckpointZIP+Drive/DropboxcompletionACK; stagecountversusoriginalDAGcountseparate. Evidence/premisesreuse allowed. Stagepublicationnotasubstituteforscience.
Root owns scientificdecision and DAG. SeparateAstrareviewer code-read/raw-result/visual reviewafterlower-tierimplementation. Preliminarycheckpointslabelpending, notadmitted. Finitefinaldecisiononlyafterreview. No strongno-go/novelty claim.
Scopeclosurepreserves working32/88, central27/88unless originalnodecriterionactuallycloses. L4false/globalphysicalcompletionnull. UpdateCRlatestreturnandthisconsumerpartialobservation preservingall88IDs17edgesnestedcontracts.
