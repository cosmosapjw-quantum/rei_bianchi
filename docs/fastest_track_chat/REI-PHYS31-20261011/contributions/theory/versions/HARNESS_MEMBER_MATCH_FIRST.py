from pathlib import Path
from zipfile import ZipFile
import hashlib,json
root=Path('/workspace/scratch/603081e41728/harness_phys27')
archive=Path('/workspace/scratch/603081e41728/recovered_inputs_phys27/physmath-research-harness-gpt6-astra-v4.0.0-20260908.zip')
rels=['START_HERE.md','PROJECT_INSTRUCTIONS.md','prompts/00_integrated_work_run.md','state/RESEARCH_STATE.md','policies/EVIDENCE_AND_CITATION.md','policies/PHASE_GATES.md','policies/STOP_RULES.md','policies/APPROVAL_BOUNDARIES.md','docs/MODEL_ROUTING.md','prompts/phases/01_research_contract.md','prompts/phases/06_physics_math_validation.md','prompts/phases/07_verification_design.md','prompts/phases/09_survivor_formalization.md']
with ZipFile(archive) as z:
 names=z.namelist()
 print(json.dumps({'archive':str(archive),'archive_bytes':archive.stat().st_size,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'member_roots':names[:3]},ensure_ascii=False))
 records=[]
 for rel in rels:
  matches=[n for n in names if n==rel or n.endswith('/'+rel)]
  assert len(matches)==1,(rel,matches)
  b=(root/rel).read_bytes();zb=z.read(matches[0]);assert b==zb
  records.append({'path':str(root/rel),'archive_member':matches[0],'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'mode':oct((root/rel).stat().st_mode & 0o777),'archive_byte_equal':True,'read_scope':'full semantic text read this role'})
 print(json.dumps(records,ensure_ascii=False,indent=2))

