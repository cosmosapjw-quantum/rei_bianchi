from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent
R=[
('R1','PASS_SCOPED','Frozen PR104 alpha/deuteron rest energies, metric -+++; next physics is the two-D birth ledger with no rate activation.'),
('R2','PASS_SOURCE_SCOPED','Source original EXFOR M0475 and publisher abstracts; current BASS_HE#107 and related seven-repo actual PR report intake; no 330MeV event normalization.'),
('R3','PASS_CONVENTION','Separate two-body pair-count energy from detector inclusive/event DA and identical initial dd thermal factor; angle symmetry unnecessary for two-D mean.'),
('R4','PASS_CONSTRUCTIVE','Compare (i) per-event fixed energy invariant; (ii) shape-dependent second moment; (iii) real photon-history collision operator; select kinematic path.'),
('R5','PASS_DERIVED','Derive K±=K0±Delta mu, Ksum=E-Q, Var_marginal=Delta²<mu²>, Cov_labelled=-Delta²(<mu²>-<mu>²), conservation.'),
('R6','PARTIAL_NATIVE_REVIEW_NOT_RUN','Wolfram four exact zeros and self-adversarial audit performed; separate native distinct-author R6 reviewer NOT_RUN.'),
('R7','PASS_CAS_SCOPED','Wolfram symbolic zeros; static threshold, E213/E330 and uncertainty convention checks; no physical flux or source interpolation.'),
('R8','PASS_CLAIM_SCOPED','Admit event-kinematic lemma only, not physical rate, angular law, deposition or original-source same-s inverse DA.'),
('R9','PASS_THEORY_TO_CODE','Contract exact Fraction s/q²/Delta², pair moments, target-frame Eprime²; no event sigma/flux/calibrated heat implementation.'),
('R10','PASS_HANDOFF','THEORY_KO/REPORT_KO/IMPLEMENTATION_CONTRACT/RESULTS and copyable handoff; no old science replay, physical HOLD.'),
]
C=[
('C1','PASS_SCOPED','Acceptance in MeV, exact stoichiometry and pair mean, fail-closed R_event/kappa; fresh tests only.'),
('C2','PASS_CODEPATH','New independent src/birth_ledger.py under research root; original PR107 experiment_semantics and reciprocity preserved, no production wiring.'),
('C3','PASS_ALGORITHM','Fraction exact squared invariants and weighted moments; Decimal90 non-certified sqrt; target energy squared exact.'),
('C4','PASS_RESOURCE','CPU-only bounded tests, 8-case independent C++100, synthetic 300 rational trials, one diagnostic figure; no old IVP.'),
('C5','PASS_IMPLEMENTED','Written runnable birth_ledger.py and tests with kinematic event energy, angular second moments, target frame, explicit null physical gates.'),
('C6','PASS_TARGETED','27 fresh Python unittest PASS; compileall PASS; C++ initializer-list expression-template compile defect fixed to explicit array.'),
('C7','PASS_PHYSICS_SCOPED','Event rest+kinetic+photon energy=0, baryon and charge=0; asymmetric weighted law distinguishes covariance definitions.'),
('C8','PASS_NUMERIC_SCOPED','CPP100 eight cases max mass-shell residual 1.78277808761e-109; Fraction random 300 PASS; plot threshold float visual fix.'),
('C9','PARTIAL_NATIVE_REVIEW_NOT_RUN','Bounded PHYS-MATH-CODE self-review and independent-algorithm C++ done; distinct-author native C9 reviewer NOT_RUN.'),
('C10','PASS_SOURCE_HANDOFF','Delivery manifest, proof/source model limits, fast-D and real photon next interface, production HOLD; source inclusive local archive.'),
]
for track,items in [('R',R),('C',C)]:
 done=0
 for stage,status,description in items:
  if status.startswith('PASS'):done+=1
  md=f"# {stage}: {description.split(';')[0][:90]}\n\nStatus: `{status}`\n\nScientific action/evidence: {description}\n\nBASS_HE central `28/88`, HE `14/18`, PR105 `2/2`, PR106 `1/2`, prior reciprocity `1/2`. This is a **new scoped** track `{done}/10` after this stage (track-local). No central physical DAG increment, `kappa=null`, `R_event=null`, `production=HOLD`. Git SHA and Drive/Dropbox ACK recorded in the publication ledger after actual provider calls.\n"
  (root/'stages'/f'{stage}.md').write_text(md)
stage_packet=[{'stage':stage,'status':status,'path':'stages/'+stage+'.md','content':(root/'stages'/f'{stage}.md').read_text()} for stage,status,_ in R+C]
(root/'STAGE_PACKET.json').write_text(json.dumps(stage_packet,ensure_ascii=False))
print('R',sum(1 for s,st,_ in R if st.startswith('PASS')),'C',sum(1 for s,st,_ in C if st.startswith('PASS')))
