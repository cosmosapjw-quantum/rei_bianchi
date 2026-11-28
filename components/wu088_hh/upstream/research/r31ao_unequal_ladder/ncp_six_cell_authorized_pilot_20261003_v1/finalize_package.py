"""Seal a final package after verification command logs have closed."""
from common import *
import zipfile,datetime,shutil
prior=json.loads((R/'LOCAL_PACKAGE_IDENTITY.json').read_text())
write(E/'PACKAGE_SEALING_AUDIT.json',dict(initial_package_snapshot=prior,initial_not_uploaded=True,reason='Initial archive was taken before its producing command finished appending stdout and COMMANDS.jsonl; final archive seals the completed logs',science_reruns=0,initial_local_zip_and_manifest_preserved=True))
payload={}
for f in sorted(E.iterdir()):
 if f.is_file() and f.name!='FILE_MANIFEST.json':payload['evidence/'+f.name]=f
for f in sorted(R.glob('*.py')):payload['launcher/'+f.name]=f
for name in ('namespace_entry.sh','AUTHORIZATION_USER_MESSAGE_KO.md'):payload['launcher/'+name]=R/name
for f in sorted(PILOT.rglob('*')):
 if f.is_file():payload['pilot/'+str(f.relative_to(PILOT))]=f
reg=NODE/'run_registry'/(SCOPE_SHA+'.json');payload['registry/'+reg.name]=reg
q=c.load(PROPOSAL)
for name,f in [('proposal/BINDING_PROPOSAL.json',PROPOSAL),('identities/WORKER_BUILD.json',Path(q['build_dir'])/'BUILD.json'),('identities/HOST_BUILD.json',Path(q['host_build_dir'])/'BUILD.json'),('identities/BACKEND_BUILD_PROVENANCE.json',Path(q['backend_provenance']['path'])),('source/SOURCE_LOCK.json',NODE/'SOURCE_LOCK.json'),('source/runtime_adapter.py',NODE/'runtime_adapter.py'),('source/coverage_contract.py',NODE/'coverage_contract.py')]:payload[name]=f
files=[dict(archive_path=arc,**ref(f),mtime_ns=f.stat().st_mtime_ns,mode=f.stat().st_mode&0o777) for arc,f in payload.items()]
write(E/'FILE_MANIFEST_FINAL.json',dict(schema='WU088_PILOT_FINAL_RESULT_MANIFEST_V1',files=files,self_excluded=True,completed_execution_and_verification_logs=True,previous_unuploaded_archive_retained_locally=True))
payload['evidence/FILE_MANIFEST_FINAL.json']=E/'FILE_MANIFEST_FINAL.json'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');z=R/('WU088_HH_NCP_SIX_CELL_PILOT_'+stamp+'.zip')
with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,strict_timestamps=False) as out:
 for arc,f in payload.items():out.write(f,arc)
with zipfile.ZipFile(z) as archive:
 assert archive.testzip() is None and set(archive.namelist())==set(payload)
 for row in files:
  data=archive.read(row['archive_path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
  assert sha(row['path'])==row['sha256'] and Path(row['path']).stat().st_mtime_ns==row['mtime_ns']
report=R/(z.stem+'_REPORT_KO.md');shutil.copy2(E/'WORK_REPORT_KO.md',report)
local=dict(package=dict(name=z.name,**ref(z)),report=dict(name=report.name,**ref(report)),manifest=ref(E/'FILE_MANIFEST_FINAL.json'),payload_files_verified=len(payload),status='PILOT_STOPPED_FIRST_REJECTION',proposal_self_sha256=PROPOSAL_SHA,binding_sha256=c.load(PILOT/'EXECUTION_BINDING.json')['binding_sha256'],science_dispatch_count=6,scope_consumed=True,accepted_cells=24,missing_cells_unbounded=265)
write(R/'FINAL_LOCAL_PACKAGE_IDENTITY.json',local);print(json.dumps(local))
