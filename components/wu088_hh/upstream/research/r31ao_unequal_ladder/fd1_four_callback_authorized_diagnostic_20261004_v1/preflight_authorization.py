"""Read-only FD1 binding checks and recording of the actual user authority."""
import sys,json,stat,datetime,subprocess,os
from pathlib import Path
TASK=Path(__file__).resolve().parent
PREP=TASK.parent/'fd1_prep_20261003_v3'
sys.path.insert(0,str(PREP))
from support import c,ref,sha,write,OLD,REPO,PILOT,NODE
from diagnostic_adapter import preflight,authorization_check,unconsumed,QUERY_KEYS
EXPECTED=dict(proposal='4f121182611c1609145728cbddfc5c346fdbbdf9c8424527b25534f282ad37be',proposal_file='73993d5f8b642874c521e646847c1f68fa604b4e15e0b641bea5f5e87241c79b',query='20ff5d09ea36b1a87489ea80961bb692161ff881fa4075c71637b81afc9cfc51',source='8850d822137bbe18109457349713682a1e8ae386d8553bb82c7f76630e327056',build='a65848adb48217b46499b400dfbce5775a912dfa0045c185b54cd8a35706bb79',binary='6f47315847a003a8da255bd60b6678a24acaaf813086f03bf00f9c4acb613478')
def main():
 e=TASK/'evidence';e.mkdir();(TASK/'delivery_evidence').mkdir()
 repo=OLD/'repo';head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/research/r31ao-unequal-order-ladder-20260930'],cwd=repo,text=True).split()[0]
 assert head==remote=='5b95029d9473429bd934a8f525ebdc0b32e716ac'
 assert subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True)==''
 proposal=c.load(PREP/'evidence/DIAGNOSTIC_PROPOSAL.json');c.check_seal(proposal,'proposal_sha256')
 assert sha(PREP/'evidence/DIAGNOSTIC_PROPOSAL.json')==EXPECTED['proposal_file'] and proposal['proposal_sha256']==EXPECTED['proposal'] and proposal['science_authorized'] is False
 queries,build=preflight(proposal,EXPECTED['proposal']);c.check_seal(queries,'query_scope_sha256');c.check_seal(build,'build_sha256')
 assert queries['query_scope_sha256']==EXPECTED['query'] and build['build_sha256']==EXPECTED['build'] and proposal['build_self_sha256']==EXPECTED['build'] and proposal['diagnostic_source_sha256']==build['diagnostic_source_sha256']==EXPECTED['source'] and sha(PREP/'build/fd1_diagnostic')==EXPECTED['binary']
 digest=c.digest(dict(additive_sources=build['additive_source_files'],inherited_numeric_files=build['inherited_numeric_files']));assert digest==EXPECTED['source']
 for q in queries['queries']:c.check_seal(c.load(PILOT/f"plans/{q['cell_id']:03d}.json"),'plan_sha256')
 host=__import__('support').a.host(REPO,proposal['host_build_dir']);assert host.identity()==proposal['host_identity']
 markers=[]
 for root in (OLD/'fd1_prep_20261003_v1',OLD/'fd1_prep_20261003_v2',PREP):
  for name in ('CALL_STARTED.json','LIVE_BINDING.json'):
   markers.extend(str(p) for p in root.rglob(name))
 assert not markers and not Path(proposal['future_registry']).exists() and not Path(proposal['future_output_root']).exists()
 unconsumed(proposal)
 pkg=PREP/'WU088_HH_FD1_PREPARATION_20261003T153408Z.zip';assert pkg.stat().st_size==4176233 and sha(pkg)=='295cbd7a58e441ce0a4372f9fa77c3ae034b1433003c16c68fe17ccc0e796da0'
 # Reuse verified local artifact. No cloud input retrieval or duplicate downloads.
 write(e/'CLOUD_INTAKE.json',dict(local_package=ref(pkg),selected_provider='LOCAL_VERIFIED_PACKAGE_REUSED',input_downloads=0,duplicate_downloads=0,Drive_id='1gsaNchJEhNMcTkuBTisdOYwzHi25vzP5',Dropbox_id='id:BSpOijBcT10AAAAAADx4Pg',new_provider_restore_verification=False,authenticated_provider_paths_inherited=True))
 auth=c.seal(dict(kind='HUMAN_EXACT_DIAGNOSTIC_AUTHORIZATION',source='EXPLICIT_LATER_USER_MESSAGE',proposal_sha256=EXPECTED['proposal'],query_scope_sha256=EXPECTED['query'],query_keys=list(QUERY_KEYS),max_field_callbacks=4,integrations=0,resource_policy=proposal['future_resource_policy'],user_message=ref(TASK/'AUTHORIZATION_USER_MESSAGE_KO.md')),'authorization_sha256')
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
   if exe in ('primitive_worker','fd1_diagnostic') or (exe.startswith('python') and any(x.endswith(b'/diagnostic_adapter.py') for x in argv) and b'run' in argv):active.append(int(p.name))
  except OSError:pass
 assert not active
 write(e/'AUTHORITY_CHECK.json',dict(status='EXACT_USER_AUTHORIZATION_AND_STATIC_IDENTITIES_VERIFIED',user_message=auth['user_message'],authorization_file=ref(e/'AUTHORIZATION_RECORD.json'),authorization_self_sha256=auth['authorization_sha256'],proposal_file=ref(PREP/'evidence/DIAGNOSTIC_PROPOSAL.json'),expected=EXPECTED,query_file=ref(PREP/'QUERIES.json'),build_file=ref(PREP/'build/BUILD.json'),sidecar_binary=ref(PREP/'build/fd1_diagnostic'),host_identity=host.identity(),remote_HEAD=remote,old_registry=proposal['old_registry'],old_scope_consumed=True,FD1_registry_and_output_absent=True,copy_markers=markers,running_diagnostic_processes=active,new_HH_evaluations=0,integrations=0,preparation_or_rebuild_entrypoints_called=False))
 blueprint=proposal['future_execution_blueprint'][:-3]+[EXPECTED['proposal'],str(e/'AUTHORIZATION_RECORD.json'),auth['authorization_sha256']]
 write(e/'EXACT_EXECUTION_COMMAND.json',dict(command=blueprint,adapter_run_attempt_budget=1,new_dispatcher=False,integrations=0,retry=False,expected_max_field_callbacks=4))
 print(json.dumps(dict(status='STATIC_AUTHORITY_VERIFIED_AWAITING_FRESH_ORIGINAL_LIVE_GATE',authorization_sha256=auth['authorization_sha256'],preserved_entries=len(old),command=blueprint)))
if __name__=='__main__':main()
