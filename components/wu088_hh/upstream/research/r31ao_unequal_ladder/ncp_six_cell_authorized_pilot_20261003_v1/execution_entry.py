"""Only identity/live revalidation and one original adapter CLI invocation.

No build, prepare, run/worker/consume function call or alternate dispatcher.
"""
from pathlib import Path
import os,json,sys,subprocess,traceback
from common import *
from observe import observation
def static_checks(proposal_path=PROPOSAL,authorization_path=E/'AUTHORIZATION_RECORD.json'):
 q=c.load(proposal_path);c.check_seal(q,'proposal_sha256')
 if q['proposal_sha256']!=PROPOSAL_SHA or sha(proposal_path)!=PROPOSAL_BYTES_SHA:raise ValueError('proposal self/file byte identity changed')
 auth=c.load(authorization_path);c.check_seal(auth,'authorization_sha256')
 expected_auth=json.loads((E/'AUTHORIZATION_IDENTITY.json').read_text())
 if ref(authorization_path)!=expected_auth:raise ValueError('authorization record changed')
 if ref(R/'AUTHORIZATION_USER_MESSAGE_KO.md')!=auth['user_message']:raise ValueError('authorization original text changed')
 if auth['proposal_self_sha256']!=PROPOSAL_SHA or auth['proposal_file_sha256']!=PROPOSAL_BYTES_SHA or auth['scope_sha256']!=SCOPE_SHA or auth['prepared_self_sha256']!=PREPARED_SHA or auth['worker_build_self_sha256']!=BUILD_SHA:raise ValueError('authorization scope binding changed')
 if auth['cell_ids']!=[275,67,288,272,16,0] or auth['limits']!=c.LIMITS or auth['science_authorization'] is not True:raise ValueError('authorization policy mismatch')
 refs=[]
 def walk(x):
  if isinstance(x,dict):
   if {'path','sha256','bytes'}<=set(x):
    target=Path(x['path'])
    if not target.is_absolute():target=PILOT/target
    observed=ref(target)
    if observed['sha256']!=x['sha256'] or observed['bytes']!=x['bytes']:raise ValueError('proposal referenced file changed: '+x['path'])
    refs.append(dict(proposal_reference=x,observed=observed))
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 walk(q)
 p=a.load_prepared(PILOT,PREPARED_SHA)
 if p['scope']['scope_sha256']!=SCOPE_SHA or p['local_plans']!=q['local_plans'] or p['files']!=q['prepared_payloads'] or a.code_identity()!=q['runtime_code_identity']:raise ValueError('prepared/plans/source mismatch')
 if p['scope']['pilot_cell_ids']!=auth['cell_ids'] or p['scope']['limits']!=c.LIMITS:raise ValueError('plan scope policy mismatch')
 for item in p['local_plans']:
  plan=c.load(PILOT/f"plans/{item['cell_id']:03d}.json");c.check_seal(plan,'plan_sha256')
  if plan['plan_sha256']!=item['plan_sha256']:raise ValueError('local plan self identity mismatch')
 f=q['future_execution_path']
 if f!={'adapter':str(NODE/'runtime_adapter.py'),'action':'run','root':str(PILOT),'expected':PREPARED_SHA,'build':q['build_dir'],'build_sha':BUILD_SHA,'host_build':q['host_build_dir'],'namespace_setup':'Same private remount and capability/no-new-privileges policy; recreate/reobserve task before exact authorization/run'}:raise ValueError('future CLI binding changed')
 m=a.validate_build(REPO,Path(f['build']),BUILD_SHA)
 if m['source']!=q['native_source']:raise ValueError('numeric source identity changed')
 h=a.host(REPO,Path(f['host_build']))
 if h.identity()!=q['host_identity']:raise ValueError('host launcher/source identity mismatch')
 inv=registry_inventory();assert_unconsumed(inv)
 return q,p,m,h,dict(status='ALL_STATIC_IDENTITIES_MATCH',proposal=ref(PROPOSAL),proposal_self_sha256=PROPOSAL_SHA,authorization=ref(authorization_path),referenced_files_verified=refs,plans=p['local_plans'],source_snapshot_files=len(c.load(NODE/'SOURCE_LOCK.json')['files']),worker_binary=ref(Path(f['build'])/'primitive_worker'),backend_and_system_linkage=m['linkage'],host_identity=h.identity(),registry=inv,successful_build_reused=True,no_rebuild=True)
def resource_checks(inside,outside):
 admission=a.resources()
 if admission!={'reserved_bytes':6442450944,'memory_max_bytes':34359738368,'cpu_quota':400000,'cpu_period':100000,'affinity_count':len(inside['affinity']),'concurrency':2}:raise ValueError('resource policy differs from approved R2')
 status=dict(line.split(':',1) for line in inside['status'].splitlines() if ':' in line)
 if any(status[k].strip()!='0000000000000000' for k in ('CapPrm','CapEff','CapBnd','CapAmb')) or status['NoNewPrivs'].strip()!='1':raise ValueError('capability/no-new-privileges policy mismatch')
 if inside['uid']!=0 or inside['gid']!=0 or outside['ppid']!=inside['pid']:raise ValueError('execution UID/PID lineage mismatch')
 if inside['namespace']['user']!=outside['namespace']['user'] or any(inside['namespace'][k]==outside['namespace'][k] for k in ('mnt','cgroup')):raise ValueError('private namespace policy mismatch')
 if inside['membership']!='0::/\n' or UNIT not in outside['membership']:raise ValueError('task membership mismatch')
 if Path('/sys/fs/cgroup/memory.max').read_text().strip()!='34359738368' or Path('/sys/fs/cgroup/cpu.max').read_text().strip()!='400000 100000':raise ValueError('adapter actual resource path mismatch')
 mount=next(line for line in inside['mountinfo'].splitlines() if line.split()[4]=='/sys/fs/cgroup')
 if 'ro' not in mount.split()[5].split(',') or ' - cgroup2 ' not in mount or any('shared:' in line for line in inside['mountinfo'].splitlines()):raise ValueError('private read-only cgroup mount policy mismatch')
 need=6*1024**3;headrooms=[];effective=float(len(inside['affinity']))
 for row in outside['ancestors']:
  if row['path']=='/sys/fs/cgroup' and all(row[k] is None for k in ('memory.max','memory.current','cpu.max')):
   # cgroup-v2 hierarchy root does not export per-cgroup limit interfaces.
   # Preserve observed absence; do not substitute finite fixture numbers.
   continue
  if row['memory.max'] is None or row['memory.current'] is None or row['cpu.max'] is None:raise ValueError('ancestor resource observation incomplete')
  lim=row['memory.max'].strip();cur=int(row['memory.current'])
  if lim!='max':headrooms.append(dict(path=row['path'],headroom=int(lim)-cur));
  quota,period=row['cpu.max'].split()
  if quota!='max':effective=min(effective,int(quota)/int(period))
 host_available=int(next(line.split()[1] for line in inside['meminfo'].splitlines() if line.startswith('MemAvailable:')))*1024
 live_headroom=34359738368-int(Path('/sys/fs/cgroup/memory.current').read_text())
 if effective<2 or live_headroom<need or host_available<need or any(x['headroom']<need for x in headrooms):raise ValueError('actual CPU/memory headroom below unchanged 6 GiB/two CPU gate')
 return dict(admission=admission,ancestor_memory_headrooms=headrooms,live_memory_headroom_bytes=live_headroom,host_MemAvailable_bytes=host_available,effective_CPU=effective,limit_is_RAM_reservation=False,nonroot_UID_validation=False)
def main():
 q,p,m,h,static=static_checks()
 inside=observation();outside=json.loads((E/'HOST_CGROUP_ANCESTORS.json').read_text());resources=resource_checks(inside,outside)
 probe=a.probe_host(h)
 with (E/'launcher_child.stdout.log').open('xb') as so,(E/'launcher_child.stderr.log').open('xb') as se:
  child=h._launch(['/usr/bin/python3','-B',str(R/'observe.py'),'child'],stdout=so,stderr=se,env={'PATH':'/usr/bin:/bin','PYTHONDONTWRITEBYTECODE':'1'},memory_mib=128,cpu_seconds=5,nofork=True);rc=child.wait(timeout=10)
 if rc!=0:raise ValueError('non-science launcher observation failed')
 child=json.loads((E/'launcher_child.stdout.log').read_text())
 if child['namespace']!=inside['namespace'] or child['membership']!=inside['membership']:raise ValueError('child namespace/membership mismatch')
 child_status=dict(line.split(':',1) for line in child['status'].splitlines() if ':' in line)
 if any(child_status[k].strip()!='0000000000000000' for k in ('CapPrm','CapEff','CapBnd','CapAmb')) or child_status['NoNewPrivs'].strip()!='1' or child_status['Seccomp'].strip()!='2':raise ValueError('child containment mismatch')
 # Fresh static identities and headroom again immediately before the original CLI.
 q,p,m,h,static=static_checks();inside=observation();resources=resource_checks(inside,outside)
 live=c.seal(dict(schema='WU088_SIX_CELL_LIVE_REVALIDATION_V1',status='PASS_BEFORE_SCOPE_CONSUMPTION',proposal_self_sha256=PROPOSAL_SHA,proposal_file_sha256=PROPOSAL_BYTES_SHA,authorization=ref(E/'AUTHORIZATION_RECORD.json'),static=static,unit=UNIT,inside=inside,outside=outside,resources=resources,child=child,probe=probe,launcher_sources=[ref(R/n) for n in ('namespace_entry.sh','execution_entry.py','common.py','observe.py')],science_dispatch_count_before_run=0,scope_consumed_before_run=False,UID0_capabilities_zero_not_nonroot_validation=True), 'live_revalidation_sha256')
 write(E/'LIVE_REVALIDATION.json',live)
 f=q['future_execution_path'];command=['/usr/bin/python3','-B',f['adapter'],f['action'],'--root',f['root'],'--expected',f['expected'],'--build',f['build'],'--build-sha',f['build_sha'],'--host-build',f['host_build']]
 write(E/'ADAPTER_INVOCATION.json',dict(proposal_self_sha256=PROPOSAL_SHA,live_revalidation=ref(E/'LIVE_REVALIDATION.json'),command=command,max_invocations=1,automatic_retry=False))
 rc=run('original_adapter_run',command,timeout=900,env={**os.environ,'PATH':'/usr/bin:/bin','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
 write(E/'ADAPTER_EXIT.json',dict(exit_status=rc,automatic_retry=False,original_RETURN_present=(PILOT/'RETURN.json').exists()))
 return rc
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as exc:
  traceback.print_exc();write(E/'EXECUTION_PRECHECK_FAILURE.json',dict(error_type=type(exc).__name__,error=str(exc),adapter_invoked=(E/'ADAPTER_INVOCATION.json').exists(),automatic_retry=False));raise
