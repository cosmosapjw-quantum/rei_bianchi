"""Read-only FD2 binding checks and recording of the actual user authority."""
import sys,json,stat,datetime,subprocess,os
from pathlib import Path
TASK=Path(__file__).resolve().parent
PREP=TASK.parent/'fd2_prep_20261004_v2'
sys.path.insert(0,str(PREP))
from support import c,ref,sha,write,OLD,REPO,PILOT,NODE
from diagnostic_adapter import preflight,authorization_check,unconsumed,QUERY_KEYS
EXPECTED=dict(proposal='c7bbb5cb80629d57553a06b835d6b8a81348a2c6f5a3a573cfa1fa9717b59692',proposal_file='4ab58ad2a1946f4541557e2969cb31ae5f9cedee3dc9f2a0f0b2fcaf6e67fb53',query='3aee33191de95106a62b2bdc91bc9487680701697a5123004ee03cbf1266e937',source='e508057f4a1dfb9422a0bb7b678072b08f77dcff54f4466c0fce1d57d375e14a',build='a8dcf6b1c41a3f3c54ef9fbe3f254bd4d30cc86901ad79abd0c7ddb68c6ec021',binary='e469a7d0af30d71ce870afce57c5a6512405e9bd7d96283bc1e26764c12c2072')
def main():
 e=TASK/'evidence';e.mkdir(exist_ok=True);(TASK/'delivery_evidence').mkdir(exist_ok=True)
 repo=OLD/'repo';head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/research/r31ao-unequal-order-ladder-20260930'],cwd=repo,text=True).split()[0]
 assert head==remote=='6c4c85eef33ef4fe733716a76523476e4aab7eef'
 assert subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True)==''
 proposal=c.load(PREP/'evidence/FD2_CANDIDATE_PROPOSAL.json');c.check_seal(proposal,'proposal_sha256')
 assert sha(PREP/'evidence/FD2_CANDIDATE_PROPOSAL.json')==EXPECTED['proposal_file'] and proposal['proposal_sha256']==EXPECTED['proposal'] and proposal['science_authorized'] is False
 queries,build=preflight(proposal,EXPECTED['proposal']);c.check_seal(queries,'query_scope_sha256');c.check_seal(build,'build_sha256')
 assert queries['query_scope_sha256']==EXPECTED['query'] and build['build_sha256']==EXPECTED['build'] and proposal['build_self_sha256']==EXPECTED['build'] and proposal['diagnostic_source_sha256']==build['diagnostic_source_sha256']==EXPECTED['source'] and sha(PREP/'build/fd2_candidate')==EXPECTED['binary']
 digest=c.digest(dict(additive_sources=build['source_files'],candidate_include_closure=build['candidate_include_closure'],inherited_numeric_files=build['inherited_numeric_files']));assert digest==EXPECTED['source']
 for q in queries['queries']:c.check_seal(c.load(PILOT/f"plans/{q['cell_id']:03d}.json"),'plan_sha256')
 host=__import__('support').a.host(REPO,proposal['host_build_dir']);assert host.identity()==proposal['host_identity']
 markers=[]
 for root in (OLD/'fd2_prep_20261004_v1',PREP):
  for name in ('CALL_STARTED.json','LIVE_BINDING.json'):
   markers.extend(str(p) for p in root.rglob(name))
 historical=[];current=[]
 for marker in markers:
  m=c.load(marker)
  if Path(marker).name=='LIVE_BINDING.json':
   c.check_seal(m,'binding_sha256')
   assert m['query_scope_sha256']=='20ff5d09ea36b1a87489ea80961bb692161ff881fa4075c71637b81afc9cfc51' and m['proposal_sha256']==proposal['parent_FD1_proposal_self_sha256']
  elif m.get('proposal_sha256')!=proposal['parent_FD1_proposal_self_sha256']:current.append(marker)
  historical.append(dict(file=ref(marker),classification='ARCHIVED_CONSUMED_FD1_EVIDENCE_NOT_FD2_START'))
 assert not current and not Path(proposal['future_registry']).exists() and not Path(proposal['future_output_root']).exists()
 unconsumed(proposal)
 pkg=PREP/'WU088_HH_FD2_NCP_CANDIDATE_PREPARATION_20261004T074747Z.zip';assert pkg.stat().st_size==4246085 and sha(pkg)=='cdde98085605babf968348e611b6a62e0cf49fe437d32b739c3d0be31a4b55be'
 # Reuse verified local artifact. No cloud input retrieval or duplicate downloads.
 write(e/'CLOUD_INTAKE.json',dict(local_package=ref(pkg),selected_provider='LOCAL_VERIFIED_PACKAGE_REUSED',input_downloads=0,duplicate_downloads=0,Drive_id='12aEsnLRCQ9VJDo8jkzR_auJ5lUrlUU4s',Dropbox_id='id:BSpOijBcT10AAAAAADx4_Q',new_provider_restore_verification=False,authenticated_provider_paths_inherited=True))
 auth=c.seal(dict(kind='HUMAN_EXACT_FD2_CANDIDATE_AUTHORIZATION',source='EXPLICIT_LATER_USER_MESSAGE',proposal_sha256=EXPECTED['proposal'],query_scope_sha256=EXPECTED['query'],query_keys=list(QUERY_KEYS),max_field_callbacks=4,integrations=0,resource_policy=proposal['future_resource_policy'],user_message=ref(TASK/'AUTHORIZATION_USER_MESSAGE_KO.md')),'authorization_sha256')
 write(e/'AUTHORIZATION_RECORD.json',auth);authorization_check(proposal,e/'AUTHORIZATION_RECORD.json',auth['authorization_sha256'])
 old=json.loads((PREP/'evidence/PRESERVATION_BEFORE.json').read_text())
 for p in PREP.rglob('*'):
  s=p.lstat()
  if p.is_symlink():old.append(dict(path=str(p),kind='symlink',target=str(p.readlink()),mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns))
  elif p.is_file():old.append(dict(path=str(p),kind='file',bytes=s.st_size,sha256=sha(p),mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns))
 write(e/'PRESERVATION_BEFORE.json',old)
 active=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   argv=(p/'cmdline').read_bytes().split(b'\0');exe=(p/'exe').resolve().name
   if exe in ('primitive_worker','fd1_diagnostic','fd2_candidate') or (exe.startswith('python') and any(x.endswith(b'/diagnostic_adapter.py') for x in argv) and b'run' in argv):active.append(int(p.name))
  except OSError:pass
 assert not active
 write(e/'AUTHORITY_CHECK.json',dict(status='EXACT_USER_AUTHORIZATION_AND_STATIC_IDENTITIES_VERIFIED',user_message=auth['user_message'],authorization_file=ref(e/'AUTHORIZATION_RECORD.json'),authorization_self_sha256=auth['authorization_sha256'],proposal_file=ref(PREP/'evidence/FD2_CANDIDATE_PROPOSAL.json'),expected=EXPECTED,query_file=ref(PREP/'QUERIES.json'),build_file=ref(PREP/'build/BUILD.json'),sidecar_binary=ref(PREP/'build/fd2_candidate'),host_identity=host.identity(),remote_HEAD=remote,old_registry=proposal['old_registry'],old_scope_consumed=True,FD2_registry_and_output_absent=True,copy_markers=historical,FD2_copy_markers=current,running_diagnostic_processes=active,new_HH_evaluations=0,integrations=0,preparation_or_rebuild_entrypoints_called=False))
 blueprint=proposal['future_execution_blueprint'][:-3]+[EXPECTED['proposal'],str(e/'AUTHORIZATION_RECORD.json'),auth['authorization_sha256']]
 write(e/'EXACT_EXECUTION_COMMAND.json',dict(command=blueprint,adapter_run_attempt_budget=1,new_dispatcher=False,integrations=0,retry=False,expected_max_field_callbacks=4))
 print(json.dumps(dict(status='STATIC_AUTHORITY_VERIFIED_AWAITING_FRESH_ORIGINAL_LIVE_GATE',authorization_sha256=auth['authorization_sha256'],preserved_entries=len(old),command=blueprint)))
if __name__=='__main__':main()
