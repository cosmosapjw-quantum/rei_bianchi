from pathlib import Path
import json, hashlib, zipfile, shutil, datetime

BASE=Path('/workspace/scratch/603081e41728')
P=BASE/'phys29'; OLD=BASE/'phys28'
def sha(b): return hashlib.sha256(b).hexdigest()
def write(rel,x):
    p=P/rel; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
for d in ['contributions/theory','contributions/numerics','claims','evidence','independent','portability','report','figures','next','state']:
    (P/d).mkdir(parents=True,exist_ok=True)
archive=BASE/'REI_PHYS28_SMALL_WIDTH_THRESHOLD_SENSITIVITY_20261011.zip'
assert sha(archive.read_bytes())=='872a685e0c18eff7d617d7bd169a8bcca22118d6b32be11d153b8e4a51244062'
m=json.loads((OLD/'MANIFEST.json').read_text())
with zipfile.ZipFile(archive) as z:
    names=z.namelist(); manifestname=next(n for n in names if n.endswith('/MANIFEST.json') or n=='MANIFEST.json')
    prefix=manifestname[:-len('MANIFEST.json')]
    assert z.read(manifestname)==(OLD/'MANIFEST.json').read_bytes()
    rows=[]
    for e in m['files']:
        b=z.read(prefix+e['path']); local=(OLD/e['path']).read_bytes()
        ok=len(b)==e['bytes'] and sha(b)==e['sha256'] and b==local
        assert ok,e['path']
        rows.append({'path':e['path'],'bytes':len(b),'sha256':sha(b),'archive_and_local_match':ok})
    assert len(names)==96 and len(rows)==95
write('evidence/PHYS28_RECOVERY_INVENTORY.json',{'status':'LOCAL_ARCHIVE_AND_ALL_PAYLOAD_IDENTITIES_VERIFIED','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive':archive.name,'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive.read_bytes()),'zip_entries':len(names),'payload_count':len(rows),'remote_full_restore':False,'old_science_executions':0,'files':rows})
selected=[
 'PHYSICS_CONTRACT.json','SOURCE_MANIFEST.json','contributions/theory/DERIVATION_KO.md','contributions/theory/THEORY_CLAIMS.json',
 'contributions/numerics/small_width_sensitivity.py','contributions/numerics/PROTOCOL.json','contributions/numerics/SMALL_WIDTH_FIRST.json','contributions/numerics/EXECUTION.json',
 'independent/DECISION_REVIEW.json','independent/DECISION_REVIEW_KO.md','report/PHYS28_RESULTS_SUMMARY.json','next/PHYS29_NEXT_HANDOFF_KO.md','state/CLOSEOUT.json']
copies=[(OLD/s,Path('inputs/PHYS28')/s) for s in selected]
for prior,files in {
 'PHYS26':['PHYSICS_CONTRACT.json','contributions/theory/ENVELOPE_DERIVATION_KO.md','contributions/numerics/fixed_variance_envelope.py','contributions/numerics/PROTOCOL.json','contributions/numerics/FIXED_VARIANCE_ENVELOPE_FIRST.json'],
 'PHYS27':['PHYSICS_CONTRACT.json','contributions/theory/FINITE_WIDTH_DERIVATION_KO.md','contributions/numerics/finite_width_envelope.py','contributions/numerics/PROTOCOL.json','contributions/numerics/FINITE_WIDTH_FIRST.json']}.items():
    copies += [(OLD/'inputs'/prior/s,Path('inputs')/prior/s) for s in files]
copies += [(f,Path('inputs')/f.relative_to(OLD/'inputs')) for f in sorted((OLD/'inputs/pinned_source').rglob('*')) if f.is_file()]
copies += [(OLD/'inputs/PHYS22_INITIAL_COEFFICIENTS.json',Path('inputs/PHYS22_INITIAL_COEFFICIENTS.json'))]
copies += [(f,Path('inputs/inherited')/f.name) for f in sorted((OLD/'inputs/inherited').glob('*.json'))]
copies += [(BASE/'PHYS28_PUBLICATION_RECEIPT.json',Path('inputs/PHYS28_PUBLICATION_RECEIPT.json')),(BASE/'PHYS28_DELIVERY_ACK_OBSERVED.json',Path('inputs/PHYS28_DELIVERY_ACK_OBSERVED.json'))]
copied=[]
for src,rel in copies:
    dest=P/rel; dest.parent.mkdir(parents=True,exist_ok=True); b=src.read_bytes(); dest.write_bytes(b)
    copied.append({'path':str(rel),'source_path':str(src),'bytes':len(b),'sha256':sha(b),'byte_identical':dest.read_bytes()==b})
write('evidence/INHERITED_INPUT_MANIFEST.json',{'task':'REI-PHYS29-20261011','copy_count':len(copied),'old_main_replay':0,'files':copied})
remote=json.loads((P/'evidence/INTAKE_REMOTE.json').read_text()); oldsm=json.loads((OLD/'SOURCE_MANIFEST.json').read_text()); rmap={e['path']:e for e in remote['source_entries']}
files={}
for path,e in oldsm['files'].items():
    b=(P/'inputs/pinned_source'/path).read_bytes(); actual=rmap[path]; blob=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
    assert sha(b)==e['sha256'] and blob==actual['sha']==e['git_blob'] and len(b)==actual['size']==e['bytes'] and actual['mode']=='100644'
    files[path]={'path':path,'sha256':sha(b),'bytes':len(b),'git_blob':blob,'git_mode':actual['mode'],'current_remote_blob_match':True,'pass':True}
assert rmap['rust/rei_microphysics/src']['sha']==oldsm['scientific_src_tree']
assert not remote['target_prefix_entries'] and not remote['truncated']
write('SOURCE_MANIFEST.json',{'task':'REI-PHYS29-20261011','input_commit':remote['head'],'input_tree':remote['tree_sha'],'scientific_src_tree':rmap['rust/rei_microphysics/src']['sha'],'files':files})
oldc=json.loads((OLD/'PHYSICS_CONTRACT.json').read_text())
contract={
 'task':'REI-PHYS29-20261011','name':'SMALL_WIDTH_SECOND_ORDER_DECOMPOSITION','successor_of':'REI-PHYS28-20261011','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'INTAKE_FROZEN',
 'model':'GPT-6 Astra','model_basis':'Trusted developer designation GPT-6 Astra Pro; no model switch or performance claim',
 'harness':{'research_version':'4.0.0','coding_version':'4.0.0','research_sha256':'dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7','coding_sha256':'dc99e7ab2f9629dcce3ec0758d97e19acc5b645f86e208d1b338bb6430ff8d7a','templates_are_execution_evidence':False},
 'execution_location':'assistant cloud; within-thread contributors and distinct final reviewer; no heavy/local run',
 'input_commit':remote['head'],'input_tree':remote['tree_sha'],'scientific_src_tree':rmap['rust/rei_microphysics/src']['sha'],
 'primary_question':'Derive the one-sided second-order coefficients d_star,d_zero at fixed actual photon variance, decompose averaging, center-variance correction, support/center/probability motion and implicit-root terms; compare quadratic prediction with stored PHYS27 delta=.05 roots and PHYS28 residuals.',
 'mode':'local analytic derivation and bounded light numerical evaluation',
 'physical_interpretation':oldc['physical_interpretation'],'definitions':oldc['definitions'],'conventions':oldc['conventions'],'actual_initial_state':oldc['actual_initial_state'],'kernel':oldc['kernel'],'numerical_input':oldc['numerical_input'],
 'second_order':{'expansion':'W_j(delta)=w_j+c_j delta+d_j delta^2+o(delta^2), delta down to0 from physical positive side','coefficient_definition':'d_j=W_j_second(0)/2','units_d':'dimensionless (eV^2/eV^2)','implicit_formula_to_be_validated':'d=-(F_delta_delta+2 F_delta_W c+F_W_W c^2)/(2 F_W)','fixed_W':'V=W-delta^2/3, V_second(0)=-2/3','no_sign_precommitment':True,'regularity_required':'Establish one-sided C2/root existence at exact simple interior roots without out-of-support or negative physical widths','comparison':'stored PHYS26 roots, PHYS27 delta=.05 roots and PHYS28 coefficients/residuals; exact-root theorem vs stored-root numerical evaluation distinguished'},
 'inherited_claims':oldc['inherited_claims'],
 'prospective_numerics':{'precision_decimal_digits':80,'first_science_main_max':1,'new_physical_root_searches_max':0,'old_PHYS19_through_PHYS28_main_suite_root_replays_max':0,'first_joint_kernel_derivative_evaluations_max':24,'preferred_design':'four inherited nodes times two algebraic paths =8 joint evaluations; k,k_prime,k_second counted separately','new_program_distinct_path_replay_max':1,'replay_independent_physics_credit':0,'freeze_before_first_science':['input identities','code','protocol','paths','tolerances','counts'],'prohibited':['width or root sweep','root refinement','finite differences','quadrature','PHYS24/25 derivative-sign campaign','native','gas IVP','dense LP'],'failures':'Preserve all first failures and preexecution changes; no posthoc tolerance change or hidden extra run'},
 'claim_limits':['Fixed family/support/mean/J only','No numerical Taylor remainder bound or certified finite width of validity','One stored positive width is a diagnostic, not convergence certification','No arbitrary positive-width family nesting or global width monotonicity assumption','Two algebraic paths do not supply independent physical data or input uncertainty enclosure'],
 'final_gate':{'distinct_NONBLIND_reviewer_required':True,'reviewer_cannot_generate_candidate_or_design_validation':True,'portable_new_program_replay_required_if_code':True},
 'publication_authority':{'basis':'Current next-loop request and inherited session authorization; actual PHYS29 handoff section6','repository':remote['repository'],'branch':remote['branch'],'pr':83,'new_prefix':'docs/fastest_track_chat/REI-PHYS29-20261011/','additive_docs_only':True,'expected_head_nonforce_CAS':True,'preserve_existing_paths_and_scientific_source':True,'merge':False,'messages_to_others':False},
 'protected_state':{'physical':'HOLD','original_interval':'[160,161] FAIL','tick':160,'auxiliary_escape':'FAIL','HH':'OFF','RCT':'OFF','CR':'OFF','precision_atomic':'PARKED','production_source_default_runtime_changes':0}}
contract['definitions']['d_units']='dimensionless (eV^2 variance)/(eV half-width)^2'
write('PHYSICS_CONTRACT.json',contract)
write('state/TOOLING_EVENTS.json',{'task':'REI-PHYS29-20261011','science_main_count_at_event':0,'events':[{'kind':'read_path_error','path':'harness_phys27/MODEL_ROUTING.md','resolution':'read actual docs/MODEL_ROUTING.md'},{'kind':'read_path_error','path':'coding_harness_phys28/prompts/00_ultralight_work_run.md','resolution':'read actual prompts/00_ultralight.md'},{'kind':'read_path_error','path':'harness_phys27/policies/EVIDENCE_POLICY.md','resolution':'rg discovery then actual policies/EVIDENCE_AND_CITATION.md read'},{'kind':'read_path_error','path':'harness_phys27/prompts/phases/07_validation_design.md','resolution':'rg discovery then actual prompts/phases/07_verification_design.md read'}],'permission_failure':False,'scientific_failure':False})
print(json.dumps({'task':contract['task'],'inherited_payload_verified':len(rows),'copied_inputs':len(copied),'source_checks':len(files),'source_subtree_unchanged':True,'contract_sha256':sha((P/'PHYSICS_CONTRACT.json').read_bytes()),'new_science':0}))
