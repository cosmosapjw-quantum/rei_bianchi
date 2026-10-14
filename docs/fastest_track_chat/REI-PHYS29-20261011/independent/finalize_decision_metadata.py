#!/usr/bin/env python3
"""Write this reviewer's final records from actual retained evidence. Science0."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent


def read(rel):
    return json.loads((ROOT/rel).read_bytes())


def rec(path):
    p = Path(path)
    p = p if p.is_absolute() else ROOT/p
    b = p.read_bytes()
    name = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
    return {'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}


def write(name, value):
    p = HERE/name
    assert not p.exists(), 'Never overwrite a retained reviewer artifact'
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    return rec(p)


raw = read('contributions/numerics/SECOND_ORDER_FIRST.json')
audit = read('independent/STATIC_CACHED_REVIEW.json')
prep = read('independent/REVIEWER_PREPARATION.json')
base = read('evidence/CANDIDATE_FROZEN.json')
add = read('evidence/CANDIDATE_ADDENDUM_FROZEN.json')
first = read('contributions/numerics/EXECUTION.json')
replay = read('portability/REPLAY_RECEIPT.json')
summary = read('report/PHYS29_RESULTS_SUMMARY.json')
assert audit['status'] == 'STATIC_CACHED_CHECKS_PASS' and audit['summary'] == {'checks':782,'passed':782,'failed':0}
assert all(v == 0 for v in audit['scientific_execution_counts'].values())
execution = write('STATIC_REVIEW_EXECUTION.json',{
    'task':'REI-PHYS29-20261011','reviewer':'/root/phys29_decision',
    'kind':'ONE_RETAINED_STATIC_FILE_AND_CACHED_ARITHMETIC_AUDIT',
    'actual_command':'python phys29/independent/review_cached_evidence.py > phys29/independent/STATIC_REVIEW_STDOUT.txt 2> phys29/independent/STATIC_REVIEW_STDERR.txt',
    'cwd':str(ROOT.parent),'started_utc':audit['started_utc'],'ended_utc':audit['ended_utc'],
    'actual_tool_exit_code':0,'actual_tool_wall_seconds':0.198409883,
    'stdout':rec('independent/STATIC_REVIEW_STDOUT.txt'),'stderr':rec('independent/STATIC_REVIEW_STDERR.txt'),
    'script':rec('independent/review_cached_evidence.py'),'result':rec('independent/STATIC_CACHED_REVIEW.json'),
    'retained_audit_invocations':1,'audit_exceptions':0,'audit_failed_checks':0,
    'candidate_or_old_program_invocations':0,'scientific_execution_counts':audit['scientific_execution_counts'],
    'counts_interpretation':'782 includes hashes, duplicate identity rechecks, serialized predicates and cached sums; never add it to scientific-check counts.'})

full = [
    'PHYSICS_CONTRACT.json','independent/REVIEWER_PREPARATION.json','evidence/CANDIDATE_FROZEN.json','evidence/CANDIDATE_ADDENDUM_FROZEN.json',
    'contributions/theory/DERIVATION_KO.md','contributions/theory/THEORY_CLAIMS.json',
    'contributions/numerics/second_order_width.py','contributions/numerics/SCIENTIFIC_CONTRACT.md','contributions/numerics/PROTOCOL.json',
    'contributions/numerics/PREEXECUTION_FROZEN.json','contributions/numerics/PREEXECUTION_CHANGES.json',
    'contributions/numerics/EXECUTION_STARTED.json','contributions/numerics/EXECUTION.json','contributions/numerics/POSTEXECUTION_PROVENANCE.json',
    'contributions/numerics/FIRST_STDOUT.txt','contributions/numerics/FIRST_STDERR.txt','contributions/numerics/NUMERICS_NOTE_KO.md',
    'contributions/numerics/preexecution_versions/draft1_to_frozen.patch',
    'contributions/numerics/preexecution_versions/freeze_v1_to_v2_doc.patch','contributions/numerics/preexecution_versions/freeze_v2_to_v3_doc.patch',
    'report/PHYS29_REPORT_KO.md','report/reviewed/PHYS29_REPORT_KO.md','README_KO.md','START_HERE_KO.md',
    'evidence/REPORT_CORRECTION.json','evidence/REPORT_CORRECTION.patch','owner_tools/make_reviewed_report.py',
    'evidence/CLAIM_DAG.json','evidence/INTAKE_REMOTE.json','evidence/LITERATURE_LEDGER.json','SOURCE_MANIFEST.json',
    'next/PHYS30_NEXT_HANDOFF_KO.md','portability/PORTABILITY_PROTOCOL.json','portability/REPLAY_NOTE_KO.md','portability/USAGE_KO.md','portability/repro.py',
    'figures/DISPLAY_RECEIPT.json']
selected = {
    'contributions/numerics/SECOND_ORDER_FIRST.json':'Whole JSON parsed. Actual core constants/nodes/kernel outputs/two root algorithms/decomposition/toys/diagnostics/counts read. All238 predicate rows independently checked from retained data:152scaled,38Fraction,48boolean/identity. No scientific import/evaluation.',
    'portability/REPLAY_RESULT.json':'Whole JSON parsed and all bytes compared with first raw; semantic result scope inherited from exact equality. No reviewer replay.',
    'portability/REPLAY_RECEIPT.json':'Whole JSON parsed; execution/success/identity/count/closure fields read; all pre/post runtime rows and dependency flags statically checked. No OS-wide tracing.',
    'portability/PORTABLE_MANIFEST.json':'Whole JSON parsed, exact26runtime paths plus manifest checked against actualZIP and existingrestore; mode/size/hash/bytes checked.',
    'report/PHYS29_RESULTS_SUMMARY.json':'Whole JSON parsed. Nonduplicate fields read; duplicate primary/diagnostic/first-summary objects exactly compared with raw; summed process counters checked.',
    'inputs/PHYS22_INITIAL_COEFFICIENTS.json':'Actual baseline_local.J_nonphoto row2 read; exact component0/3 strings checked against currentJ. Remaining historical computation not rerun.',
    'inputs/PHYS26/contributions/numerics/FIXED_VARIANCE_ENVELOPE_FIRST.json':'Selected constants, inherited_boundary_residuals, root strings, responses and summary; source blob identity only for other sections.',
    'inputs/PHYS27/contributions/numerics/FINITE_WIDTH_FIRST.json':'Selected constants, threshold_comparison, stored physical root midpoints and summary; no new roots or historical program audit.',
    'inputs/PHYS28/contributions/numerics/SMALL_WIDTH_FIRST.json':'Selected constants, four nodes, retainedjointkernel outputs, primarysensitivity, delta005comparison and summary; no historical program run.',
    'inputs/pinned_source/rust/rei_microphysics/src/atomic_provider.rs':'Actual source excerpt lines316–355 for threshold/HI Verner parameters/formula; whole-file byte/hash/Gitblob check. Not a full provider audit.',
    'independent/STATIC_CACHED_REVIEW.json':'Whole JSON result parsed; resultsummary,all failed/exception fields, categories and observedvalues read. Every individual row generated by this reviewer retained; metadata counts are not science.',
}
harness_extra = [
    ROOT.parent/'harness_phys27/prompts/phases/06_physics_math_validation.md',
    ROOT.parent/'coding_harness_phys28/START_HERE.md',ROOT.parent/'coding_harness_phys28/AGENTS.md',
    ROOT.parent/'coding_harness_phys28/SCIENTIFIC_CONTRACT.md',ROOT.parent/'coding_harness_phys28/VALIDATION_MATRIX.md']
semantically_read = set(full)|set(selected)
read_manifest = write('REVIEW_READ_MANIFEST.json',{
    'task':'REI-PHYS29-20261011','reviewer':'/root/phys29_decision',
    'preparation_reads':prep['actual_reads'],'preparation_harness_archive':prep['harness_archive'],
    'full_text_actual_reads':[dict(rec(p),actual_read_scope='full actual text, sometimes recovered in nontruncated chunks') for p in full],
    'additional_harness_texts':[dict(rec(p),actual_read_scope='full actual text; coding templates treated as instructions, not scientific evidence') for p in harness_extra],
    'selected_or_programmatically_checked':[dict(rec(p),actual_read_scope=s) for p,s in selected.items()],
    'actual_visual_inspection':[dict(rec('figures/PHYS29_SECOND_ORDER_DECOMPOSITION.png'),actual_read_scope='Final PNG opened once by reviewer; axes/log-residual/grouping read, legible. Earlier image iterations were not independently viewed.')],
    'remaining_bound_payloads_byte_identity_only':[dict(v,actual_read_scope='byte/size/hash only unless separately covered by preparation; no claim of complete semantic audit') for v in base['files']+add['files'] if v['path'] not in semantically_read],
    'static_read_ledger':rec('independent/STATIC_CACHED_REVIEW.json'),
    'external_primary_text_reads':[
      {'url':'https://web.stanford.edu/class/math51h/taylor.pdf','retrieval_ref':'turn41view0','source':'Stanford Mathematics, Math51H — Mean value theorem, Taylor theorem and integrals','actual_read_scope':'Full4-page retrieved PDF text. Used pp2–3 second-order Taylor/integral remainder and continuity of Hessian only. Individual author/date not verified.','application_limit':'Open-domain background does not by itself prove physical one-sided C2 or this model root.'},
      {'url':'https://math.mit.edu/~larsh/teaching/F2007/handouts/implicit.pdf','retrieval_ref':'turn41view1','source':'MIT Mathematics18.022 — The implicit function theorem','actual_read_scope':'Full2-page retrieved PDF text. C1 theorem, derivative, and general level F(x,y)=F(a,b). Individual byline not verified.','application_limit':'Does not itself prove a C2 half-domain theorem or validate physical coefficients.'}],
    'not_performed':['No independent remote Git read; owner intake record and local7source Gitblob checks used.','No full re-audit or rerun of PHYS24/25 certificates or PHYS26–28 programs.','No candidate/old module import, scientific main, kernel derivative, root, quadrature, finite difference, toy evaluation or replay.','No originality/priority literature survey.','No claim that reading hashes means semantic review of all119base files.'],
    'tooling_events':prep['tooling_events']+['Some large combined read displays were truncated; core code/report/protocol gaps were recovered by smaller actual reads, with JSON row arrays additionally checked by retained static audit.','One read-only rg inventory included a nonexistent versions path; actual preexecution_versions paths were then read. No mutation/science occurred.']})

final_rows = []
audited_reads = {v['path']:v for v in audit['actual_byte_reads']}
audited_checks = {v['name']:v for v in audit['checks']}
for label, rows in [('base119',base['files']),('addendum5',add['files'])]:
    for row in rows:
        actual = {k:audited_reads[row['path']][k] for k in ('path','bytes','sha256')}
        prefix = 'end_base_119__' if label == 'base119' else 'end_addendum_5__'
        final_rows.append({'group':label,**actual,'pass':actual == row and audited_checks[prefix+row['path']]['pass']})
assert len(final_rows) == 124 and all(x['pass'] for x in final_rows)
final_identity = write('REVIEW_FINAL_IDENTITY_CHECK.json',{
    'task':'REI-PHYS29-20261011','checked_utc':audit['ended_utc'],'record_written_utc':datetime.now(timezone.utc).isoformat(),
    'base':rec('evidence/CANDIDATE_FROZEN.json'),'addendum':rec('evidence/CANDIDATE_ADDENDUM_FROZEN.json'),
    'payload_count':124,'base_count':119,'addendum_count':5,'all_pass':True,'files':final_rows,
    'scope':'Transcription of the last124 original/addendum payload checks within the successful782-check retainedaudit; no additional broad recheck. Reviewer records are additional.',
    'scientific_execution_counts':audit['scientific_execution_counts']})

theory_notes = {
 'TC29-01':('DERIVED_WITH_INHERITED_FAMILY','Endpoint-first notation and physical support/mean/actual-variance relation checked; uniform profile and identical family only.'),
 'TC29-02':('CONDITIONAL_DIRECT_DERIVATION','Valid physical half-rectangle, one-sided continuous partials, positive FW, root-sign persistence and derivative extension. Exact interior root premise conditional; no numerical neighborhood size.'),
 'TC29-03':('DIRECT_DERIVATION','Band path second derivative includes velocity-square plus1/3 and center acceleration; Taylor coefficient ksecond/6, not full second derivative.'),
 'TC29-04':('DIRECT_DERIVATION','Probability and center Vsecond effects both included once; fixedactualW distinguished from fixedV geometry.'),
 'TC29-05':('DIRECT_DERIVATION','B,C,K,M,N compact/chain formulas verified without assuming stored residualzero.'),
 'TC29-06':('CONDITIONAL_DIRECT_DERIVATION','Integral C and N formulas and s/R sign checked; strict ksecond/kthird premises inherited, no new certificate.'),
 'TC29-07':('CONDITIONAL_DIRECT_DERIVATION','d=Whalfsecond formula and factor2 correct; exactroot continuation, o(delta2) only.'),
 'TC29-08':('DIRECT_DERIVATION','All nine code K terms and eleven d terms present; theory grouping equivalent, no missing probability-motion or acceleration term.'),
 'TC29-09':('DIRECT_DERIVATION','dV=1/3 exact and davg negative under C,ksecond positivity; total d sign remains uncommitted.'),
 'TC29-10':('CONDITIONAL_DIRECT_DERIVATION','Implicit Wcurvature term signs correct given inherited strict kthird and nonzero c.'),
 'TC29-11':('DIRECT_DERIVATION','Common1/3 cancels from d_zero-d_star; no universal total gap coefficient sign.'),
 'TC29-12':('DIRECT_DERIVATION_AND_STATIC_IMPLEMENTATION_CHECK','Only four inherited nodes required; no reviewer evaluations and candidate counters/protocol enforce4perpath.'),
 'TC29-13':('DIRECT_DERIVATION_AND_IMPLEMENTATION_CHECK','E^-2(D4+2D3-3D2)phi and fourthlog/Bell scalar expansion checked; native behavior not emulated.'),
 'TC29-14':('DIRECT_DERIVATION','General F=A continuation and residual-preserving numerator identities including -(4/3)A checked; finiteDecimal error and exactroot premise separate.'),
 'TC29-15':('DIRECT_DERIVATION_AND_CACHED_EXACT_CHECK','Quadratic moment identity and retainedFraction truthchecked; no new toyexecution; strictkthird/uniqueness not claimed.'),
 'TC29-16':('DIRECT_DERIVATION_AND_CACHED_BOOKKEEPING','Units, fixed oldserializedlinear plus newd increment and explicit c difference checked. One width only; no error/rate certificate.')}
theory_claims = read('contributions/theory/THEORY_CLAIMS.json')['claims']
claim_decisions = []
for claim in theory_claims:
    status, reason = theory_notes[claim['id']]
    claim_decisions.append({'id':claim['id'],'decision':'PROMOTE_SCOPED','evidence_status':status,
        'claim':claim['claim'],'reviewer_assessment':reason,'retained_dependencies':claim['depends_on'],'retained_limits':claim['limits']})
extra_claims = [
 {'id':'N29-COEFFICIENTS','decision':'PROMOTE_SCOPED','evidence_status':'NUMERICALLY_CHECKED_AT_STORED_POINTS','scope':'Reported d values/signs and full decomposition in frozen source-real/Decimal80 model. Exactzero coefficient interpretation conditional; no physical/error enclosure.'},
 {'id':'V29-TWOALGORITHMS','decision':'PROMOTE_SCOPED','evidence_status':'IMPLEMENTATION_VERIFIED','scope':'LogJet/Bell kernels plus separatechain/bivariate envelope and retainedexactquadratic knownlimit. Sharedfit,J,source,Decimal,family; independentphysicalcredit0.'},
 {'id':'N29-DELTA005','decision':'PROMOTE_SCOPED','evidence_status':'SINGLE_WIDTH_DIAGNOSTIC','scope':'ExistingPHYS27root and PHYS28linear values; residual improvement and lowerovershoot observed, never an acceptance criterion. No Odelta3, remainder or validitywidth certificate.'},
 {'id':'V29-REPLAY','decision':'PROMOTE_SCOPED','evidence_status':'IMPLEMENTATION_VERIFIED','scope':'One retained freshpath replay; 26runtime+manifest closure,238PASS,rawbytes/JSONidentical. Samehost/Python/program, no independentphysicscredit.'},
 {'id':'P30-NEXT','decision':'PROPOSED_NOT_RUN','evidence_status':'PROPOSAL_ONLY','scope':'Fixed symmetric profile with sameouter[-1,1]support and samecenterinterval. No PHYS30 theorem, profile computation or root approved as completed.'},
 {'id':'PHYSICAL-ADMISSION','decision':'HOLD','evidence_status':'NOT_ESTABLISHED','scope':'No finite-time/finiteepsilon/history/emitter admission result.'}]

decision = {
 'schema':1,'task':'REI-PHYS29-20261011','decision':'PROMOTE_SCOPED','decision_token':'PROMOTE_SCOPED',
 'decided_utc':datetime.now(timezone.utc).isoformat(),'fatal_issue_count':0,'fatal_issues':[],
 'reviewer':{'identity':'/root/phys29_decision','model':'GPT-6 Astra Pro','model_basis':'Trusted developer runtime designation and inherited full-history model; not inferred from tool names.',
    'role':'Distinct final decision reviewer','NONBLIND':True,'blind_review':False,'full_parent_history_inherited':True,
    'candidate_theory_generation':False,'candidate_numerics_generation':False,'candidate_validation_design':False,'candidate_tolerance_design':False,'candidate_portability_generation':False,'owner_self_review':False,
    'recursive_review':False,'independence_limit':'Separate reviewer role from generators and validation designers, same model family and shared history; no independent physical data.',
    'authorization':'Actual root explicit final-review GO after candidate freeze; later explicit additive-correction GO. Interim report finding did not edit candidate.'},
 'candidate':{'base_manifest':rec('evidence/CANDIDATE_FROZEN.json'),'base_payload_count':119,'base_payloads_unchanged':True,
    'addendum_manifest':rec('evidence/CANDIDATE_ADDENDUM_FROZEN.json'),'addendum_payload_count':5,'addendum_payloads_checked':add['files'],'addendum_payloads_unchanged':True,
    'canonical_user_report':rec('report/reviewed/PHYS29_REPORT_KO.md'),'preserved_original_report':rec('report/PHYS29_REPORT_KO.md'),
    'first_raw':rec('contributions/numerics/SECOND_ORDER_FIRST.json'),'replay_raw':rec('portability/REPLAY_RESULT.json'),
    'final_identity_check':final_identity,'self_referential_final_archive_claim':False},
 'promoted_scope':[
    'Conditional physical one-sided C2 exact interior simple-root expansion at fixed actual variance for the frozen uniform-band center family, with d=-(K+2Mc+Nc2)/(2C).',
    'Complete probability, center/end motion, averaging, Vsecond and implicit-root derivative decomposition; exact dV=1/3 and common-term gap cancellation.',
    'Residual-preserving general F=A local-level interpretation at stored finite root values; no silent zero substitution.',
    'FrozenDecimal80 numerical d coefficients and observed signs/decomposition at inherited points, supported by two kernel expressions and separate root derivative algorithms.',
    'Retained exactquadratic knownlimit, preregistered238PASS first result and one238PASS byte-identical freshpath replay with precise independence limits.',
    'One inherited delta=.05 diagnostic including lower residual overshoot and gap-reduction residual, with no remainder/convergence/validity claim.',
    'Reporting and preserving corrected full deliverable and evidence for the next research stage; PHYS30 remains proposed/notrun.'],
 'physical_admission':'HOLD',
 'not_promoted':[
    'Unconditional exactzero root existence or interval root enclosure from stored finiteDecimal roots or tiny response residuals.',
    'Numerical error bounds for d, propagated storedroot error budgets or directed interval arithmetic.',
    'Quantitative Taylor remainder, Odelta3 convergence rate, certified delta=.05 validity or generalwidth inclusion/monotonicity.',
    'Universal totald sign for arbitrary parameters/profile/source/J.',
    'Independent physical validation from two shared-input formulas or same-program same-host replay.',
    'Physical uncertainty removal, native floating-point equivalence, finite-time/finiteepsilon/emitter/history admission.',
    'PHYS30 profile theorem or computations, new derivative certificate campaign, new roots, production runtime/source/default changes.',
    'Priority or novelty supported by a comprehensive literature survey.'],
 'claim_decisions':claim_decisions+extra_claims,
 'mathematical_assessment':{
    'one_sided_C2':'Physical compacthalfrectangle supports endpointband paths; k,kprime,ksecond continuity yields needed partials, FWpositive lowerbound and signpersisting unique root. Right derivatives extend from delta>0 and integration yields o(delta2). No negativewidth/outsidekernelextension needed.',
    'exact_root_premise':'Exactinterior simple root premise explicit. Inherited endpoint signs remain numerically supported; stored153digitvalue is not an enclosure.',
    'variance_and_terms':'FixedactualW gives V=W-delta2/3 and Vsecond=-2/3. Probability and center effects both present and counted once. NineK/eleven d terms complete; dV=1/3 exact, averagingnegative under positivity.',
    'implicit_curvature':'C integralweights t, N s/R integralweights t2 checked. UpperNnegative/lowerNpositive under inheritedkthirdnegative; only implicitcurvature component sign follows.',
    'kernel':'Fourth logderivative and Bell4 expansion checked by direct differentiation. ksecond requires E^-2(D4+2D3-3D2)phi; normalization/source literals consistent with readinputs.',
    'stored_level':'A retained. Ndelta+2RA,NW-A,and ndd+2ndWc+nWWc2-4A/3 corrections verified. -A/C diagnostic not appliedrootcorrection or errorbound.',
    'quadratic_limit':'MomentidentityFtoy=W-w establishes c=d=0, average -1/3 plusV+1/3 cancels. ExactFraction cached resultschecked; no strictkthird inheritance.'},
 'findings':[
    {'id':'F29-01','severity':'NONBLOCKING_REPORTING_ERROR','status':'RESOLVED_IN_FROZEN_ADDENDUM','summary':'Original report described denominator selection too broadly; dimensional suppliedscales do not use maxwithvalues. Code and protocol were already correct.',
     'found_by':'/root/phys29_decision','edited_by':'/root','resolution':'Complete corrected report kept additively; exactsentence/header/relative-link-only transformation and5identities verified. No original119 mutation or scientific rerun.',
     'evidence':[rec('evidence/REPORT_CORRECTION.json'),rec('evidence/REPORT_CORRECTION.patch')]},
    {'id':'L29-01','severity':'SCOPE_LIMIT','status':'RETAINED_NONBLOCKING','summary':'Exactroot theorem conditional; finite reference defines sameA level. Tiny response and two-expression agreement are not errorcertificates.'},
    {'id':'L29-02','severity':'SCOPE_LIMIT','status':'RETAINED_NONBLOCKING','summary':'Singlewidth diagnostic explains observed residual only, with lowerovershoot; no new width/rate/remainder evidence.'},
    {'id':'L29-03','severity':'INDEPENDENCE_LIMIT','status':'RETAINED_NONBLOCKING','summary':'Separate algebra algorithms share physical inputs, family and Decimal; replay samecodehost. Independentphysicalcredit0.'}],
 'uncertainty':{
    'inherited':['Atomicfit/J/gas/input physical uncertainty unquantified.','Derivative-sign evidence and envelope family inherited only within prior approvedsupport/model scope; not independently recertified.','Storedzero and finitewidthroots lack promoted exactroot enclosure.','Source-real interpretation distinct from native floating-point behavior.'],
    'new':['Secondlogderivativeextension and d postprocessing checked at finiteDecimal80 precision, no numerical enclosure.','Strong response cancellation leaves small A with few meaningful computed digits; exacterror budget absent.','Propagation from storedroot to exactzero d not bounded.','Singlewidth comparison provides no rate, certifiedrange or remainderconstant.'],
    'not_new_physical_evidence':['Byteidentity/Gitblob/sourcechecks','238predicate rechecking','Sameprogram pathreplay','782review file/cached arithmeticchecks']},
 'numerical_observations':{
    'd_star':raw['second_order']['jet_chain']['upper_root']['d_dimensionless'],'d_zero':raw['second_order']['jet_chain']['lower_root']['d_dimensionless'],
    'response_star_s-4':raw['second_order']['jet_chain']['upper_root']['response_s-4'],'response_zero_s-4':raw['second_order']['jet_chain']['lower_root']['response_s-4'],
    'maximum_scaled_kernel_expression_error':raw['maximum_scaled_kernel_expression_error'],'maximum_scaled_independent_envelope_error':raw['maximum_scaled_independent_envelope_error'],
    'frozen_algebra_tolerance':'1E-60','frozen_stored_response_tolerance':'1E-65','scaled_denominator':'ExplicitfixedS_j/sigma when supplied; scaleNone=max(1,absactual,absexpected); constant comparisons supplymax(absactual,absexpected).',
    'delta005':raw['delta_005_comparison'],'d_signs_or_improvement_used_as_acceptance':False},
 'execution_observations':{
    'first':{'start_utc':first['start_utc'],'end_utc':first['end_utc'],'wall_seconds':first['wall_seconds'],'exit':first['exit_code'],'summary':raw['summary']},
    'replay':{'start_utc':replay['started_utc'],'end_utc':replay['ended_utc'],'wall_seconds':replay['wall_seconds'],'exit':replay['actual_exit_code'],'same_bytes':True,'same_parsed_JSON':True,'runtime_file_count':26,'files_with_manifest':27,'independent_physical_credit':0,'same_host_python_program':True},
    'total':summary['total_execution'],'forbidden_counts_zero':True,'basis':'Actualretainedraw/receipts/commands and staticprogramreview. No OSwide tracing or reviewer physics rerun.'},
 'gate_dimensions':{
    'evidence':'Actualfixedsource-to-claim chain, first/replay raw, hashes, preregistration and saved reviewerchecks support specifiedclaims.',
    'physical_math_validity':'Conditionalmathvalidity approved; physicaladmission remainsHOLD.',
    'novelty':'No priority/novelty claim promoted; primaryliterature read only as standardbackground.',
    'testability':'Independentalgebra, exactknownlimit and fixedcriteria have actualresults; futureprofilequestion remainsseparate.',
    'robustness':'Internalimplementation consistency strong at givenpoints; uncertainty and shareddependencies remainexplicit.',
    'tractability':'Two boundednewprogram runs complete within fixednodes/budgets; no broadcampaignneeded.',
    'assumptions':'Support,mean,J,source-real,uniformprofile,fixedactualW,exactinteriorroot and inheritedstrictderivatives retained.',
    'original_motivation':'Explains the second-order contribution left after PHYS28linear sensitivity using PHYS27existingwidthroots.',
    'aggregate_score_used':False},
 'read_scope_manifest':read_manifest,
 'reviewer_execution':{'preparation':rec('independent/REVIEWER_PREPARATION.json'),'static_audit':rec('independent/STATIC_CACHED_REVIEW.json'),'execution_receipt':execution,
    'actual_counts':audit['scientific_execution_counts'],'retained_cached_audit_invocations':1,'recursive_review':False,'candidate_payload_mutations':0,
    'review_scope_is_NOT_independent_physics':True},
 'narrative':rec('independent/DECISION_REVIEW_KO.md'),
 'protected':{'physical':'HOLD','original_interval':'[160,161] FAIL','tick':160,'auxiliary_escape':'FAIL','HH':'OFF','RCT':'OFF','CR':'OFF','precision_atomic':'PARKED','production_source_default_runtime_changes':0},
 'next':{'task':'PHYS30','status':'PROPOSED_NOT_RUN','question':'Fixed symmetric profile second-order dependence on secondmoment, preserving sameouter support and centerinterval.','new_theorem_or_calculation_promoted':False},
 'pending_operations_after_gate':['Owner records decision/closeout and actualpublication/delivery receipts.','Owner completes full finalarchive and finalartifact identity checks; this reviewer assessed existingportable stage, not futurefinalarchive.','Owner verifies actual remote Gitpublication if performed. No suchsuccesspreclaimed here.'],
 'stop_decision':'Stop all further PHYS29 scientific execution, roots/replays or broadcampaigns. Preserve report correction and approvedscope; finish owner reporting/closeout only.',
 'self_hash_cycle':'ThisdecisiondoesnotembeditsownSHA. Parent/finalmanifest may bind its actualbytes after creation.'}

decision_record = write('DECISION_REVIEW.json',decision)
print(json.dumps({'decision':'PROMOTE_SCOPED','fatal_issue_count':0,'candidate119_and_addendum5_unchanged':True,
    'candidate_identity_observation_utc':audit['ended_utc'],
    'artifacts':[decision_record,rec('independent/DECISION_REVIEW_KO.md'),read_manifest,execution,final_identity,
                 rec('independent/review_cached_evidence.py'),rec('independent/STATIC_CACHED_REVIEW.json')],
    'reviewer_scientific_execution_counts':audit['scientific_execution_counts']},ensure_ascii=False))
