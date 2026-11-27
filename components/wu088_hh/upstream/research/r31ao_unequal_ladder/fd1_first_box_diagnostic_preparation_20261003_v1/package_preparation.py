"""Create a single closed payload ZIP. Delivery receipts stay outside it."""
from support import *
import zipfile,stat
def main():
 with (E/'COMMANDS.jsonl').open('a') as f:
  f.write(json.dumps(dict(command=['python3','-B',str(R/'finalize_preparation.py')],exit_status=1,stage='initial_coordinator_metadata_read',reason='Original science JSON reader rejects >16MiB preservation inventory; coordinator-only parsing fixed',science_calls=0))+'\n')
  f.write(json.dumps(dict(command=['python3','metadata_correction_helper'],exit_status=1,reason='Missing json import in metadata-only command recorder; no science calls or original changes'))+'\n')
  f.write(json.dumps(dict(command=['python3','-B',str(R/'package_preparation.py')],exit_status=0,stage='final_packaging_and_local_zip_manifest_verification',science_calls=0))+'\n')
 audit=c.load(E/'NO_HH_EVALUATION_AUDIT.json');audit['command_log']=ref(E/'COMMANDS.jsonl');(E/'NO_HH_EVALUATION_AUDIT.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
 repo=OLD/'repo';head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=repo,text=True).strip()
 running=[]
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:
   cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
   if ('primitive_worker' in cmd or 'runtime_adapter.py run' in cmd or 'fd1_diagnostic --hh-single' in cmd) and str(OLD) in cmd:running.append(dict(pid=int(proc.name),command=cmd))
  except OSError:pass
 # No shell/environment dumps: only actual science executable processes.
 running=[p for p in running if Path('/proc/'+str(p['pid'])+'/comm').read_text().strip() not in ('bash','timeout','python3')]
 write(E/'RECOVERY_INVENTORY.json',dict(repo_HEAD=head,repo_tree=tree,branch=BRANCH,PR='https://github.com/cosmosapjw-quantum/WU088_HH/pull/33',canonical_pilot=str(PILOT),canonical_runtime=str(OLD),canonical_FD1=str(R),verified_cache='/root/.cache/WU088_HH/sha256',recovery_roots=[str(OLD/'runtime_work'),str(OLD/'prep_r1'),str(OLD/'prep_r2'),str(OLD/'pilot_exec_20261003_v1'),str(OLD/'fd1_prep_20261003_v1'),str(OLD/'fd1_prep_20261003_v2')],input_identities=c.load(E/'CLOUD_INTAKE.json'),old_registry=c.load(E/'INTAKE_VERIFICATION.json')['old_registry'],old_scope_consumed=True,running_science_executable_processes=running,PID_claim_strings_not_live_process_assertions=True,actual_live_observation=ref(E/'LIVE_POLICY_PROBE.json'),resource_fixtures_used=False))
 assert not running
 coordinator={n:ref(R/n) for n in ('live_gate_probe.py','live_gate_probe.sh','finalize_preparation.py','package_preparation.py')}
 write(E/'COORDINATOR_IDENTITY.json',dict(files=coordinator,proposal_immutable=True,scientific_execution_authority=False))
 members={}
 for p in R.iterdir():
  if p.is_file() and p.suffix in ('.cpp','.hpp','.py','.sh','.inc','.json'):members['source/'+p.name]=p
 for p in E.iterdir():
  if p.is_file() and p.name!='FILE_MANIFEST.json':members['evidence/'+p.name]=p
 for p in (R/'build').iterdir():members['build/'+p.name]=p
 for v,logs in [('fd1_prep_20261003_v1',['actual_ancestor_and_total_wall_probe.stdout.log','actual_ancestor_and_total_wall_probe.stderr.log']),('fd1_prep_20261003_v2',['actual_live_gate_unit.stdout.log','actual_live_gate_unit.stderr.log','ancestor_probe_unit.stdout.log','ancestor_probe_unit.stderr.log'])]:
  for n in logs:members['prior_failures/'+v+'/'+n]=OLD/v/'evidence'/n
 for n in ('DIAGNOSTIC_QUERY_DESIGN.json','REVIEW_RESULT.json','FLINT_SOURCE_LOCK.json'):members['reference/'+n]=REVIEW/n
 members['reference/FD1_PROMPT_KO.md']=Path(c.load(E/'CLOUD_INTAKE.json')['artifacts'][0]['local']['path'])
 members['reference/REMOTE_START_PROMPT_KO.md']=repo/'research/r31ao_unequal_ladder/ncp_pilot_queue_review_20261003_v1/START_PROMPT_KO.md'
 manifest=dict(schema='WU088_FD1_PAYLOAD_MANIFEST_V1',files=[dict(path=n,bytes=p.stat().st_size,sha256=sha(p),mode=stat.S_IMODE(p.stat().st_mode)) for n,p in sorted(members.items())],self_excluded='FILE_MANIFEST.json',HH_evaluations=0,integrations=0)
 write(E/'FILE_MANIFEST.json',manifest)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');name='WU088_HH_FD1_PREPARATION_'+stamp+'.zip';zp=R/name
 with zipfile.ZipFile(zp,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for n,p in sorted(members.items()):z.write(p,'WU088_HH_FD1_PREPARATION/'+n)
  z.write(E/'FILE_MANIFEST.json','WU088_HH_FD1_PREPARATION/FILE_MANIFEST.json')
 with zipfile.ZipFile(zp) as z:
  assert z.testzip() is None and len(z.namelist())==len(members)+1
  for row in manifest['files']:
   b=z.read('WU088_HH_FD1_PREPARATION/'+row['path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
 report=R/('WU088_HH_FD1_PREPARATION_REPORT_KO_'+stamp+'.md');report.write_bytes((E/'WORK_REPORT_KO.md').read_bytes())
 package=dict(status='READY_FOR_EXACT_DIAGNOSTIC_AUTHORIZATION',ZIP=ref(zp),report=ref(report),payloads=len(members),manifest=ref(E/'FILE_MANIFEST.json'),local_ZIP_CRC_and_all_payload_SHA_verified=True,output_RESTORE_VERIFIED=False,proposal_self_sha256=c.load(E/'DIAGNOSTIC_PROPOSAL.json')['proposal_sha256'])
 write(R/'delivery_evidence/LOCAL_PACKAGE.json',package);print(json.dumps(package))
if __name__=='__main__':main()
