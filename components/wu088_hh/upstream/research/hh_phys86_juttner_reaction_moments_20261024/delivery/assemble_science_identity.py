"""Metadata-only scoped identity assembly under the root scientific decision."""
from pathlib import Path
import copy,datetime,hashlib,json
U=Path('/workspace/scratch/ebcaaaa20861/WU088_HH/research/hh_phys86_juttner_reaction_moments_20261024')
A=Path('/workspace/scratch/ebcaaaa20861/wu_phys86_20261024/artifacts')
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
def sha(b): return hashlib.sha256(b).hexdigest()
def identity(p):
 b=(U/p).read_bytes();return {'path':p,'bytes':len(b),'sha256':sha(b)}
def write(p,x):
 target=U/p
 if target.exists(): raise FileExistsError(str(target))
 target.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 return identity(p)
decision_path='results/ROOT_SCIENTIFIC_DECISION.json'
decision=json.loads((U/decision_path).read_text());manifest=json.loads((U/'implementation/IMPLEMENTATION_FREEZE_MANIFEST.json').read_text())
if decision['decision']!='PASS_SCOPED': raise ValueError('Root decision is not PASS_SCOPED')
fixed={'CONTRACT.json','theory/JUTTNER_REACTION_MOMENTS_KO.md','implementation/IMPLEMENTATION_FREEZE_MANIFEST.json',*manifest['files'].keys(),'reviews/THEORY_REVIEW.json','reviews/CODE_REVIEW.json','reviews/ACTUAL_RAW_REVIEW.json',decision_path}
for kind in ['recovery','moments']:
 for name in ['TOOL_REQUEST_ARGUMENTS.json','RAW_WOLFRAM_RESPONSE.json','EXACT_PAYLOAD.txt','COMPLETE_CERTIFICATE.json','PARSE_AND_SCOPE_RECEIPT.json']:
  fixed.add('results/attempt_'+kind+'/'+name)
fixed_files=[identity(p) for p in sorted(fixed)]
descriptor={'schema':'PHYS86_SCOPED_REFERENCE_SCIENCE_DESCRIPTOR_V1','identity_kind':'SCOPED_EXACT_REFERENCE_SCIENCE','scope':copy.deepcopy(decision['admission_ceiling']),'parent_final_HEAD':decision['parent_final_HEAD'],'execution_source_commit':decision['execution_source_commit'],'execution_source_tree':decision['execution_source_tree'],'root_scientific_decision':identity(decision_path),'fixed_files':fixed_files}
science_sha=sha(canonical(descriptor))
science_file=write('results/SCIENCE_IDENTITY.json',{'descriptor':descriptor,'scientific_identity_SHA256':science_sha})
status=copy.deepcopy(decision)
status['root_decision_schema']=status['schema'];status['schema']='PHYS86_RESULT_STATUS_V1'
status.update({'scientific_reference':'PASS_SCOPED','scientific_completion_claim':True,'scientific_completion_scope':'conditional reference unit only','completed_science_identity':science_sha,'HH_R10':'OFF','production_admission':'NOT_ISSUED'})
status_file=write('results/RESULT_STATUS.json',status)
evidence_descriptor={'schema':'PHYS86_SCOPED_REFERENCE_EVIDENCE_DESCRIPTOR_V1','identity_kind':'SCOPED_REFERENCE_SCIENCE_AND_EVIDENCE','status':copy.deepcopy(status),'science_identity_file':science_file,'fixed_files':fixed_files+[status_file]}
evidence_sha=sha(canonical(evidence_descriptor))
evidence_file=write('results/EVIDENCE_IDENTITY.json',{'descriptor':evidence_descriptor,'evidence_identity_SHA256':evidence_sha})
receipt={'schema':'PHYS86_SCIENCE_IDENTITY_METADATA_ASSEMBLY_RECEIPT_V1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'activity':'metadata-only byte reads/hash/canonical JSON assembly','source_root_decision':identity(decision_path),'canonical_method':"json.dumps(descriptor,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')",'science_fixed_file_count':len(fixed_files),'evidence_fixed_file_count':len(evidence_descriptor['fixed_files']),'scientific_identity_SHA256':science_sha,'evidence_identity_SHA256':evidence_sha,'written_files':[science_file,status_file,evidence_file],'new_evaluator_calls':0,'new_local_scientific_execution':0,'new_tests':0,'Git_actions':0,'upload_actions':0,'decision_authority':'root scientific decision preserved; no new scientific admission by assembler'}
(A/'SCIENCE_IDENTITY_ASSEMBLY_RECEIPT.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(receipt))
