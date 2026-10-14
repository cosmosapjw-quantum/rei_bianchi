from pathlib import Path
import datetime,difflib,hashlib,json,os,re
base=Path('/workspace/scratch/603081e41728')
root=base/'phys31/contributions/theory'
def identity(p):
    b=p.read_bytes()
    return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'mode':format(p.stat().st_mode & 0o777,'04o')}
def write_new(p,text):
    with p.open('x',encoding='utf-8',newline='') as f:
        f.write(text)
catalog=json.loads((root/'PREPARATION_READ_CATALOG.json').read_text())
events=json.loads((root/'PRE_FREEZE_EVENTS.json').read_text())
claims=json.loads((root/'THEORY_CLAIMS.json').read_text())
derivation=(root/'DERIVATION_KO.md').read_text()
tags=re.findall(r'\\tag\{(T31\.\d+)\}',derivation)
assert len(tags)==len(set(tags))==51
assert claims['claim_count']==len(claims['claims'])==18
assert len({x['id'] for x in claims['claims']})==18
for row in claims['claims']:
    for eq in row['equations']:
        if eq.startswith('T31.'):
            assert eq in tags,(row['id'],eq)
sources=[]
for row in catalog['actual_source_reads']:
    p=base/row['path']
    rec={**row,**identity(p)}
    portable=base/'phys31'/row['portable_path']
    rec['portable_exists_at_provenance_write']=portable.is_file()
    if portable.is_file():
        rec['portable_identity']=identity(portable)
        rec['portable_bytes_equal']=p.read_bytes()==portable.read_bytes()
        assert rec['portable_bytes_equal'],(str(p),str(portable))
    sources.append(rec)
skills=[]
for row in catalog['actual_skill_reads']:
    p=Path(row['path'])
    skills.append({**row,**identity(p)})
first=(root/'versions/DERIVATION_DRAFT1_KO.md').read_text().splitlines(keepends=True)
final=derivation.splitlines(keepends=True)
diff=''.join(difflib.unified_diff(first,final,fromfile='versions/DERIVATION_DRAFT1_KO.md',tofile='DERIVATION_KO.md'))
write_new(root/'PREFREEZE_DRAFT_TO_FINAL.diff',diff)
artifact_paths=[
 'DERIVATION_KO.md','THEORY_CLAIMS.json','PREPARATION_READ_CATALOG.json',
 'PRE_FREEZE_EVENTS.json','PREFREEZE_DRAFT_TO_FINAL.diff',
 'versions/DERIVATION_DRAFT1_KO.md','versions/HARNESS_MEMBER_MATCH_FIRST.py',
 'write_provenance.py'
]
record={
 'schema':'rei-phys31-theory-provenance-v1',
 'task':'REI-PHYS31-20261011',
 'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'contributor':'/root/phys31_theory',
 'role':'THEORY_CANDIDATE_GENERATOR_NONBLIND',
 'status':'DERIVED_CANDIDATE_COMPLETE_FOR_OWNER_AND_DISTINCT_FINAL_REVIEW',
 'model':{'name':'GPT-6 Astra Pro','basis':'Trusted developer designation and full-history inherited executor; no change, runtime identity measurement or performance claim.'},
 'harness':catalog['harness_actual_identity_result'],
 'harness_actual_metadata_execution':catalog['harness_metadata_actual_execution'],
 'skill_actual_reads':skills,
 'scientific_contract_and_predecessor_reads':sources,
 'predecessor_decision_actually_consumed':catalog['previous_decision_consumed'],
 'final_derivation_self_read':catalog['own_full_derivation_read'],
 'static_document_consistency':{'equation_tags':len(tags),'duplicate_tags':0,'claims':len(claims['claims']),'duplicate_claim_ids':0,'all_explicit_equation_references_present':True,'scope':'Document structural metadata only; this does not certify proof validity.'},
 'actual_work':{
   'direct_derivation':True,
   'physical_right_C3_and_C4_root_proof':True,
   'equal_mu2_third_jet_proof':True,
   'quartic_profile_response_and_root_difference':True,
   'nonzero_A_numerator_identity':True,
   'positive_AC_pair_analytic_moments':True,
   'C3_sharpness_same_AC_pair_direct_counterexample':True,
   'possible_fifth_order_after_quartic_degeneracy_direct_counterexample':True,
   'contract_exact_toy_oracle_direct_algebra':True,
   'physical_source_formula_or_C4_verification':'Another contributor; not performed by this role',
   'physical_fourth_derivative_values':'Another contributor; not performed by this role'
 },
 'execution_counts':claims['execution'],
 'first_failure_and_changes':{
   'record':'PRE_FREEZE_EVENTS.json',
   'actual_first_metadata_failure_exit':events['events'][0]['actual_execution']['exit_code'],
   'actual_first_metadata_failure_chunk':events['events'][0]['actual_execution']['chunk_id'],
   'resolution_exit':events['events'][0]['resolution_exit'],
   'resolution_chunk':events['events'][0]['resolution_actual_chunk'],
   'metadata_failures':1,'absent_precreation_directory_probe':1,
   'draft_original':'versions/DERIVATION_DRAFT1_KO.md',
   'original_failed_metadata_script':'versions/HARNESS_MEMBER_MATCH_FIRST.py',
   'draft_diff':'PREFREEZE_DRAFT_TO_FINAL.diff',
   'science_failures':0,'science_retries':0,'tolerance_changes':0
 },
 'independence':{
   'NONBLIND':True,'same_model_family':True,'same_host':True,
   'parent_history_and_shared_evidence':True,
   'self_review_class':'THEORY_CONTRIBUTOR_SELF_CHECK',
   'independent_final_decision_by_this_role':False,
   'independent_physical_evidence_credit':0
 },
 'external_literature_actual_reads':[],
 'literature_scope':'The new formulas and counterexamples are direct derivations. Earlier references in predecessor documents are not claimed as this role external primary-source reads.',
 'candidate_artifact_identities':[identity(root/rel) for rel in artifact_paths],
 'protected':claims['protected'],
 'final_decision':'PENDING_DISTINCT_REVIEWER; this contributor does not promote its own candidate'
}
write_new(root/'PROVENANCE.json',json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'THEORY_METADATA_WRITTEN','science_executions':0,'output':identity(root/'PROVENANCE.json'),'artifacts':[identity(root/rel) for rel in ['DERIVATION_KO.md','THEORY_CLAIMS.json','PRE_FREEZE_EVENTS.json','PREFREEZE_DRAFT_TO_FINAL.diff']],'portable_source_copies_present':sum(r['portable_exists_at_provenance_write'] for r in sources),'source_records':len(sources),'harness_matches':record['harness']['matches'],'claim_count':len(claims['claims']),'equation_tags':len(tags)},ensure_ascii=False,indent=2))

