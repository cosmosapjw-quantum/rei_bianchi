#!/usr/bin/env python3
"""PHYS30 immutable selected-input intake; metadata/bytes only, no science."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, zipfile

BASE=Path(__file__).resolve().parents[2]
ROOT=BASE/'phys30'
OLD=BASE/'phys29'
TASK='REI-PHYS30-20261011'
def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(p.read_bytes())
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    assert not p.exists(), str(p)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def record(p,root=BASE):
    b=p.read_bytes(); return {'path':p.relative_to(root).as_posix(),'bytes':len(b),'sha256':sha(b)}
remote=read(ROOT/'evidence/REMOTE_INTAKE.json')
assert remote['head']=='45bd460d779e5a189fc75663d4ae61249e514751'
assert remote['tree']=='7ca6547cd7be726f38738d7601f16486e10fbdba'
assert remote['scientific_src']['sha']=='cb69b4736dd046e4675557577eb8e0ead037d1f3'
assert remote['new_prefix_absent'] and remote['pr_draft'] and not remote['pr_merged']
prior=read(BASE/'PHYS29_PUBLICATION_RECEIPT.json')
ack=read(BASE/'PHYS29_DELIVERY_ACK_OBSERVED.json')
review=read(OLD/'independent/DECISION_REVIEW.json')
close=read(OLD/'state/CLOSEOUT.json')
assert prior['decision']==review['decision']==close['decision']=='PROMOTE_SCOPED'
assert review['fatal_issue_count']==0
assert ack['all_succeeded'] and ack['all_local_metadata_applied'] and ack['ordered_count']==7
assert sha((BASE/'PHYS29_PUBLICATION_RECEIPT.json').read_bytes())==ack['publication_receipt_sha256']
archive=BASE/prior['archive']['path']
assert record(archive)==prior['archive']
manifest=read(OLD/'MANIFEST.json')
assert record(OLD/'MANIFEST.json',OLD)==prior['final_package_verification']['manifest']
oldrows={r['path']:r for r in manifest['files']}
selected=[
 'PHYSICS_CONTRACT.json','SOURCE_MANIFEST.json',
 'next/PHYS30_NEXT_HANDOFF_KO.md',
 'state/CLOSEOUT.json','state/ADDENDUM_CLOSEOUT.json','state/RESEARCH_STATE.md',
 'report/reviewed/PHYS29_REPORT_KO.md','report/PHYS29_RESULTS_SUMMARY.json',
 'contributions/theory/DERIVATION_KO.md','contributions/theory/THEORY_CLAIMS.json','contributions/theory/PROVENANCE.json',
 'contributions/numerics/second_order_width.py','contributions/numerics/PROTOCOL.json',
 'contributions/numerics/SECOND_ORDER_FIRST.json','contributions/numerics/EXECUTION.json',
 'contributions/numerics/NUMERICS_NOTE_KO.md',
 'independent/DECISION_REVIEW.json','independent/DECISION_REVIEW_KO.md',
 'portability/REPLAY_RECEIPT.json',
 'inputs/PHYS22_INITIAL_COEFFICIENTS.json',
 'evidence/CANDIDATE_FROZEN.json','evidence/CANDIDATE_ADDENDUM_FROZEN.json',
 'evidence/HARNESS_APPLICATION.json','evidence/HARNESS_STRUCTURE_EXECUTION.json']
source=read(OLD/'SOURCE_MANIFEST.json')
selected += ['inputs/pinned_source/'+r for r in source['files']]
copies=[]
for rel in selected:
    p=OLD/rel; actual=record(p,OLD); expected=oldrows[rel]
    assert actual['bytes']==expected['bytes'] and actual['sha256']==expected['sha256'],rel
    dest=ROOT/'inputs/PHYS29'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists(): shutil.copy2(p,dest)
    assert dest.read_bytes()==p.read_bytes(), str(dest)
    copies.append({'source':record(p),'copy':record(dest,ROOT),'matched_prior_manifest':True})
for rel in ['PHYS29_PUBLICATION_RECEIPT.json','PHYS29_DELIVERY_ACK_OBSERVED.json']:
    p=BASE/rel;dest=ROOT/'inputs'/rel;assert not dest.exists();shutil.copy2(p,dest)
    copies.append({'source':record(p),'copy':record(dest,ROOT),'matched_prior_manifest':'detached receipt; prior ACK identity where applicable'})
source_checks=[]
byremote={r['path']:r for r in remote['source_entries']}
for rel,old in source['files'].items():
    b=(ROOT/'inputs/PHYS29/inputs/pinned_source'/rel).read_bytes()
    git=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    actual=byremote[rel]
    assert sha(b)==old['sha256'] and git==old['git_blob']==actual['sha'] and len(b)==actual['size'] and actual['mode']==old['git_mode']
    source_checks.append({'path':rel,'bytes':len(b),'sha256':sha(b),'git_blob':git,'git_mode':actual['mode'],'current_remote_identity_match':True})
write(ROOT/'SOURCE_MANIFEST.json',{'task':TASK,'input_commit':remote['head'],'input_tree':remote['tree'],'scientific_src_tree':remote['scientific_src']['sha'],'files':source_checks,'verification':'Current complete remote tree identities plus selected inherited local bytes; no duplicate download or native build.'})
oldcontract=read(OLD/'PHYSICS_CONTRACT.json')
contract={
 'task':TASK,'name':'SYMMETRIC_PROFILE_SECOND_ORDER_UNIVERSALITY','successor_of':'REI-PHYS29-20261011',
 'created_utc':datetime.now(timezone.utc).isoformat(),'status':'INTAKE_FROZEN',
 'model':'GPT-6 Astra','model_basis':'Trusted developer designation GPT-6 Astra Pro; no model switch or performance claim',
 'harness':oldcontract['harness'],'execution_location':'assistant cloud in this conversation; bounded contributors and distinct final reviewer',
 'input_commit':remote['head'],'input_tree':remote['tree'],'scientific_src_tree':remote['scientific_src']['sha'],
 'primary_question':'For a fixed symmetric probability profile on [-1,1] and the identical center interval, prove or refute invariance of c and dependence of d only on mu2.',
 'mode':'convergence; direct derivation with one cached-value numerical main and one replay',
 'physical_interpretation':oldcontract['physical_interpretation'],
 'conventions':oldcontract['conventions'],'actual_initial_state':oldcontract['actual_initial_state'],
 'kernel':oldcontract['kernel'],'numerical_input':dict(oldcontract['numerical_input'],J_source='inputs/PHYS29/inputs/PHYS22_INITIAL_COEFFICIENTS.json'),
 'definitions':{
  'a_eV':'13.61','b_eV':'24.58','m_eV':'18','L_eV':'4.39','H_eV':'6.58',
  'delta':'nonnegative outer halfwidth bound in eV; actual profile support may be narrower',
  'center_interval':'[a+delta,b-delta] identical for every profile, even mu2=0',
  'profile':'fixed nonnegative symmetric probability measure nu on [-1,1], independent of delta,W,center,branch',
  'mu1':'0','mu2':'integral z^2 dnu, dimensionless, 0<=mu2<=1',
  'center_variance':'V=W-mu2*delta^2','actual_variance':'W in eV^2; fixed in delta partials',
  'averaged_kernel':'f_delta_nu(c)=integral k(c+delta*z) dnu(z)',
  'ell':'L-delta','h':'H-delta',
  'A_plus':'[V*f_delta_nu(a+delta)+ell^2*f_delta_nu(m+V/ell)]/(ell^2+V)',
  'A_minus':'[h^2*f_delta_nu(m-V/h)+V*f_delta_nu(b-delta)]/(h^2+V)',
  'feasibility_to_derive':'mu2*delta^2 <= W <= (L-delta)*(H-delta)+mu2*delta^2',
  'expansion':'W_j(delta)=w_j+c_j*delta+d_j*delta^2+o(delta^2), d=W_second(0+)/2',
  'units_c':'eV','units_d':'dimensionless',
  'curvature_sum':'script-H = p*k_second(e)+q*k_second(x), distinct from H=b-m'},
 'candidate_relation_not_yet_approved':'c_nu=c_uniform; d_nu=d_uniform+(mu2-1/3)*(1-scriptH/(2*C)); K_nu=K_uniform+(mu2-1/3)*(scriptH-2*C)',
 'theory_obligations':['Convolution support and moments; common-profile mixture class identified','Average kernel regularity and inherited k_second>0,k_third<0 without assuming density smoothness','Center-moment Hermite extremizers rederived; no unrestricted photon-envelope claim','Physical one-sided C2 at exact simple interior root; no negative physical width','Complete fixed-W coefficient transfer, generalized nonzero A-level numerator correction','Quadratic limit, units, atomic/absolute-continuity boundary and limitations'],
 'inherited_premises':['k C3 on [a,b] with endpoint derivatives; inherited k_second>0 and k_third<0','Exact interior root premise conditional; inherited endpoint-sign numerical support is not interval certification','Stored references carry nonzero response A; no corrected root or certified root uncertainty'],
 'prospective_numerics':{
  'precision_decimal_digits':80,'first_science_main_max':1,'distinct_path_replay_max':1,
  'new_physical_kernel_or_derivative_evaluations_max':0,'new_physical_root_searches_or_refinements_max':0,
  'old_PHYS19_through_PHYS29_main_suite_root_import_max':0,
  'allowed':'Cached PHYS29 values in explicit algebra, uniform mu2=1/3 and triangular density 1-|z| mu2=1/6; exact rational moment and quadratic A=1 toy algebra within same main',
  'two_paths':'Affine transfer from cached PHYS29 d and independent bivariate degree2 response algebra using retained k,kprime,ksecond; shared physical input acknowledged',
  'tolerance_policy':'Freeze protocol before first main; dimensionless scaled tolerance1e-60; dimensional comparisons use fixed supplied scales, no posthoc change',
  'execution_counts':'Separate cached branch, exact profile moment, exact toy algebra counters; no accounting as physical kernel evaluation',
  'prohibited':['finite differences','quadrature','width/root sweep','derivative-sign campaign','native','gas IVP','dense LP','new finite-width physical root'],
  'replay_independent_physics_credit':0,'freeze_before_first':['inputs','code','protocol','tolerances','expected checks','counts','command'],
  'failures':'Keep first failures and preexecution edits; no hidden rerun or tolerance relaxation'},
 'claim_limits':['Fixed symmetric profile and common center interval only','No nonsymmetric or profile-dependent support expansion','Atomic profiles do not imply absolute continuous photon law','Same mu2 only gives equality through second order; no positive-width equality','No Taylor quantitative bound, valid-width certificate, global profile ordering or new physical admission','No root or J uncertainty enclosure; no independent physical credit'],
 'final_gate':oldcontract['final_gate'],
 'publication_authority':{'basis':'Current next-loop request plus actual PHYS30 handoff section6 and inherited same-branch additive docs authorization','repository':remote['repository'],'branch':remote['branch'],'pr':83,'new_prefix':remote['new_prefix'],'additive_docs_only':True,'expected_head_nonforce_CAS':True,'preserve_existing_paths_and_scientific_source':True,'merge':False,'messages_to_others':False},
 'protected_state':oldcontract['protected_state']}
write(ROOT/'PHYSICS_CONTRACT.json',contract)
readgroups=[('research','harness_phys27','recovered_inputs_phys27/physmath-research-harness-gpt6-astra-v4.0.0-20260908.zip','dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7',['START_HERE.md','PROJECT_INSTRUCTIONS.md','prompts/00_integrated_work_run.md','state/RESEARCH_STATE.md','docs/MODEL_ROUTING.md','policies/EVIDENCE_AND_CITATION.md','policies/STOP_RULES.md','prompts/phases/06_physics_math_validation.md','prompts/phases/07_verification_design.md','prompts/phases/08_external_decision_gate.md']),('coding','coding_harness_phys28','recovered_inputs_phys28/physmath-coding-harness-gpt6-astra-v4.0.0-20260908.zip','dc99e7ab2f9629dcce3ec0758d97e19acc5b645f86e208d1b338bb6430ff8d7a',['START_HERE.md','AGENTS.md','SCIENTIFIC_CONTRACT.md','VALIDATION_MATRIX.md','docs/MODEL_ROUTING.md','prompts/00_ultralight.md','README.md'])]
groups=[]
for kind,stage,archivepath,expected,files in readgroups:
    ar=BASE/archivepath;assert sha(ar.read_bytes())==expected
    rows=[]
    with zipfile.ZipFile(ar) as z:
        for rel in files:
            b=(BASE/stage/rel).read_bytes();assert b==z.read(rel),rel
            rows.append(dict(record(BASE/stage/rel),archive_entry=rel,staging_matches_archive=True,actual_read_scope='full current PHYS30 root turn; smaller retained-output redisplay when aggregate truncated'))
        groups.append({'kind':kind,'archive':record(ar),'archive_entries':len(z.namelist()),'read_files':rows})
write(ROOT/'evidence/HARNESS_APPLICATION.json',{'task':TASK,'status':'ACTUAL_READS_AND_MATCHED_EXISTING_STAGING','groups':groups,'templates_are_execution_evidence':False,'package_structure_gate':'Prior actual PHYS29 validator receipt retained; identical package bytes, no redundant structure run','scientific_main_invocations':0})
write(ROOT/'evidence/INPUT_MANIFEST.json',{'task':TASK,'status':'SELECTED_INHERITED_INPUTS_VERIFIED','file_count':len(copies),'files':copies,'prior_archive':record(archive),'prior_manifest':record(OLD/'MANIFEST.json'),'prior_decision':review['decision'],'prior_fatal_issues':0,'prior_delivery_ack_status':ack['status'],'verification_scope':'Prior outer archive SHA plus manifest-bound selected file copies and current remote source identities. No rerun of prior science, no new full restore.','old_science_invocations':0})
write(ROOT/'state/EXECUTION_LEDGER.json',{'task':TASK,'phase':'INTAKE_AND_DERIVATION','inherited_PHYS29_main':2,'inherited_PHYS29_joint_physical_evaluations':16,'new_first_main':0,'new_replay':0,'new_physical_kernel_or_derivatives':0,'new_physical_roots':0,'old_PHYS19_through_PHYS29_main_suite_import':0,'new_toy_algebra_evaluations':0,'note':'New optional cached main and exact toy algebra remain NOT_RUN until frozen owner-authorized invocation; old debit not reset.'})
print(json.dumps({'status':'PHYS30_INTAKE_FROZEN','copied_inputs':len(copies),'source_files':len(source_checks),'harness_files_checked':sum(len(g['read_files']) for g in groups),'contract':record(ROOT/'PHYSICS_CONTRACT.json',ROOT),'new_science':0},ensure_ascii=False))
