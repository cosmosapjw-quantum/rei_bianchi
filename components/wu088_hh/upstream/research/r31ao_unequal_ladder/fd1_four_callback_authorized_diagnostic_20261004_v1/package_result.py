"""Package sealed observation bytes once; no execution or callback path."""
import sys,json,datetime,zipfile,hashlib,stat
from pathlib import Path
TASK=Path(__file__).resolve().parent;E=TASK/'evidence';PREP=TASK.parent/'fd1_prep_20261003_v3'
sys.path.insert(0,str(PREP))
from support import c,ref,sha,write
def main():
 proposal=c.load(PREP/'evidence/DIAGNOSTIC_PROPOSAL.json');root=Path(proposal['future_output_root'])
 assert c.load(E/'FD1_HANDOFF_RETURN.json')['valid_observations']==4 and c.load(root/'RETURN.json')['scope_consumed']
 write(E/'SAMPLING_LIMITATIONS.json',dict(requested_poll_delay_seconds=.005,actual_period_includes_proc_directory_scan=True,no_matching_native_proc_snapshot_captured=True,exact_reason_not_instrumented=True,short_lived_calls_consistent_with_missing_samples=True,native_execution_proven_by_original_adapter_PID_markers_and_raw=True,per_native_timing_is_file_event_window=True,absent_measurements_not_filled_with_zero=True))
 write(E/'RECOVERY_INVENTORY.json',dict(preparation_commit='5b95029d9473429bd934a8f525ebdc0b32e716ac',canonical_execution_root=str(root),registry=ref(proposal['future_registry']),LIVE_BINDING=ref(root/'LIVE_BINDING.json'),fresh_outside_observation=ref(PREP/'evidence/FD1_DIAGNOSTIC_OUTSIDE.json'),final_RETURN=ref(root/'RETURN.json'),canonical_proposal=ref(PREP/'evidence/DIAGNOSTIC_PROPOSAL.json'),scope_consumed=True,old_six_cell_scope_consumed=True,valid_field_callbacks=4,integrations=0,science_dispatch_sequence=proposal['future_query_keys'],original_backend_worker_sidecar_rebuilt=False,recovery_rule='Read completed results; never retry this consumed scope under any new directory/name',input_package=c.load(E/'CLOUD_INTAKE.json')))
 write(E/'FILE_IDENTITY_REFS.json',dict(source_files=proposal['source_files'],inherited_files=proposal['inherited_files'],sidecar=proposal['binary'],sidecar_build=proposal['build_file'],host_identity=proposal['host_identity'],proposal_self_sha256=proposal['proposal_sha256'],query_scope_sha256=proposal['queries']['query_scope_sha256'],sidecar_source_sha256=proposal['diagnostic_source_sha256'],sidecar_build_self_sha256=proposal['build_self_sha256'],static_and_loader_checked_before_actual_run=True))
 with (E/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps(dict(command=['python3','-B',str(Path(__file__))],exit_status=0,action='ZIP CRC and every manifest payload SHA verification; no scientific execution'))+'\n')
 members={}
 for p in E.iterdir():
  if p.is_file() and p.name!='FILE_MANIFEST.json':members['evidence/'+p.name]=p
 for p in TASK.iterdir():
  if p.is_file() and p.suffix in ('.py','.md'):members['coordinator/'+p.name]=p
 for p in root.rglob('*'):
  if p.is_file():members['diagnostic_run/'+str(p.relative_to(root))]=p
 members['diagnostic_registry/'+Path(proposal['future_registry']).name]=Path(proposal['future_registry'])
 members['fresh_outside/FD1_DIAGNOSTIC_OUTSIDE.json']=PREP/'evidence/FD1_DIAGNOSTIC_OUTSIDE.json'
 for name in ('diagnostic.cpp','diagnostic_adapter.py','authorized_namespace.sh','support.py','observe.py','QUERIES.json','queries_generated.hpp','original_margin.inc','diagnostic_identity.hpp','build/BUILD.json','evidence/DIAGNOSTIC_PROPOSAL.json'):
  members['reference/'+name]=PREP/name
 manifest=dict(schema='WU088_FD1_EXECUTION_PAYLOAD_MANIFEST_V1',files=[dict(path=n,bytes=p.stat().st_size,sha256=sha(p),mode=stat.S_IMODE(p.stat().st_mode)) for n,p in sorted(members.items())],self_excluded='FILE_MANIFEST.json',field_callbacks=4,integrations=0,diagnosis='UNRESOLVED')
 write(E/'FILE_MANIFEST.json',manifest)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');zp=TASK/('WU088_HH_FD1_FOUR_CALLBACK_RESULT_'+stamp+'.zip')
 with zipfile.ZipFile(zp,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for n,p in sorted(members.items()):z.write(p,'WU088_HH_FD1_FOUR_CALLBACK_RESULT/'+n)
  z.write(E/'FILE_MANIFEST.json','WU088_HH_FD1_FOUR_CALLBACK_RESULT/FILE_MANIFEST.json')
 with zipfile.ZipFile(zp) as z:
  assert z.testzip() is None and len(z.namelist())==len(members)+1
  for row in manifest['files']:
   data=z.read('WU088_HH_FD1_FOUR_CALLBACK_RESULT/'+row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
 report=TASK/('WU088_HH_FD1_FOUR_CALLBACK_REPORT_KO_'+stamp+'.md');report.write_bytes((E/'WORK_REPORT_KO.md').read_bytes())
 package=dict(status='UNRESOLVED',ZIP=ref(zp),report=ref(report),payloads=len(members),FILE_MANIFEST=ref(E/'FILE_MANIFEST.json'),CRC_and_all_payload_SHA_verified=True,valid_observations=4,field_callbacks=4,integrations=0,scope_consumed=True,output_RESTORE_VERIFIED=False)
 write(TASK/'delivery_evidence/LOCAL_PACKAGE.json',package);print(json.dumps(package))
if __name__=='__main__':main()
