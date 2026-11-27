"""Future FD2 candidate boundary. Preparation never calls run_authorized or consume.

The coordinator must first receive a separate exact human authorization and
record its original text. Neither this proposal nor JSON data creates authority.
"""
from support import *
import argparse
QUERY_KEYS=('Q272_cached','Q272_reference','Q000_cached','Q000_reference')
def verify_refs(rows):
 for row in rows:
  if ref(row['path'])!=row:raise ValueError('static file identity changed: '+row['path'])
def preflight(proposal,expected):
 c.check_seal(proposal,'proposal_sha256')
 if proposal['proposal_sha256']!=expected or proposal['science_authorized'] is not False:raise ValueError('proposal identity/authority mismatch')
 queries=c.load(R/'QUERIES.json');c.check_seal(queries,'query_scope_sha256')
 if queries!=proposal['queries'] or proposal['future_query_keys']!=list(QUERY_KEYS):raise ValueError('exact query geometry/coefficient semantics changed')
 if queries['max_field_callbacks']!=4 or queries['max_integrations']!=0 or queries['primitive_index']!=0 or queries['precision_bits']!=128 or queries['coefficient_semantics']!='ORIGINAL_SIGNED_ORDERED107':raise ValueError('diagnostic scope changed')
 verify_refs(proposal['source_files']);verify_refs(proposal['inherited_files'])
 if ref(R/'build/fd2_candidate')!=proposal['binary'] or ref(R/'build/BUILD.json')!=proposal['build_file']:raise ValueError('sidecar binary/build record changed')
 build=c.load(R/'build/BUILD.json');c.check_seal(build,'build_sha256')
 _,gate=a.driver(REPO).dependencies();backend=gate.verify_backend(BACKEND/'BACKEND_BUILD_PROVENANCE.json',BACKEND/'prefix')
 ld=subprocess.run(['/usr/bin/ldd',str(R/'build/fd2_candidate')],env={'PATH':'/usr/bin:/bin','LD_LIBRARY_PATH':str(BACKEND/'prefix/lib')},capture_output=True,text=True,timeout=15,check=True)
 if gate.verify_linkage(ld.stdout,{n:x['binary_path'] for n,x in backend['libraries'].items()})!=build['linkage']:raise ValueError('backend/system-library loader identity changed')
 for q in queries['queries']:
  if sha(PILOT/f"raw/{q['cell_id']:03d}.json")!=q['parent_raw_sha256']:raise ValueError('parent raw identity changed')
  parent=c.load(PILOT/f"plans/{q['cell_id']:03d}.json")
  if parent['plan_sha256']!=q['parent_plan_sha256'] or parent['window']!=q['physical_parent_window']:raise ValueError('parent plan/window changed')
 verify_refs([proposal['parent_FD1_registry']])
 c.check_seal(c.load(proposal['parent_FD1_registry']['path']),'binding_sha256')
 if c.load(PILOT/'COVERAGE.json')['accepted_cell_count']!=24 or ref(proposal['old_registry']['path'])!=proposal['old_registry']:raise ValueError('consumed pilot/coverage/registry changed')
 return queries,build
def authorization_check(proposal,path,expected_auth):
 auth=c.load(path);c.check_seal(auth,'authorization_sha256')
 if auth['authorization_sha256']!=expected_auth or auth.get('kind')!='HUMAN_EXACT_FD2_CANDIDATE_AUTHORIZATION' or auth.get('source')!='EXPLICIT_LATER_USER_MESSAGE':raise ValueError('new explicit human authorization required')
 if auth.get('proposal_sha256')!=proposal['proposal_sha256'] or auth.get('query_scope_sha256')!=proposal['queries']['query_scope_sha256'] or auth.get('query_keys')!=list(QUERY_KEYS) or auth.get('max_field_callbacks')!=4 or auth.get('integrations')!=0 or auth.get('resource_policy')!=proposal['future_resource_policy']:raise ValueError('new diagnostic authorization scope mismatch')
 verify_refs([auth['user_message']]);return auth
def unconsumed(proposal):
 if Path(proposal['future_registry']).exists() or Path(proposal['future_output_root']).exists():raise ValueError('diagnostic already started; recover without rerun')
def consume(path,obj):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('x') as f:json.dump(obj,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def exact_geometry(result,geometry):
 for k in ('inner_log_box','outer_log_box','physical_t','physical_u','margin','ordered_terms'):
  if result[k]!=geometry[k]:raise ValueError('exact geometry/margin/signed coefficients changed: '+k)
def validate_observation(result,query,implementation,geometry,query_scope,source_sha):
 if result.get('schema')!='WU088_FD2_CANDIDATE_FIRST_BOX_OBSERVATION_V1':raise ValueError('FD2 candidate output schema mismatch')
 expected=dict(query_id=query['query_id'],implementation=implementation,cell_id=query['cell_id'],parent_raw_sha256=query['parent_raw_sha256'],query_scope_sha256=query_scope,primitive_index=0,precision_bits=128,order=0,field='O',orbital='S',ia=0,ib=0,coefficient_semantics='ORIGINAL_SIGNED_ORDERED107',archive_sha256=c.INPUT_SHA,input_record_sha256=c.RECORD_SHA,original_build_source_sha256=c.SOURCE_SHA,diagnostic_source_sha256=source_sha,integrations=0,HH_evaluations=1)
 for k,v in expected.items():
  if result.get(k)!=v:raise ValueError('diagnostic output binding mismatch: '+k)
 exact_geometry(result,geometry);record=result['record']
 if record['before']['calls']!=0 or record['before']['failures']!=0 or record['before']['last_error'] or any(record['before']['cache'].values()):raise ValueError('stale callback Contract/CacheStats')
 if record['callback_invocations']!=1 or record['after']['calls']!=1:raise ValueError('single field callback contract changed')
 if record['fresh_failure']!=(record['after']['failures']>record['before']['failures']) or (record['after']['last_error'] and not record['fresh_failure']):raise ValueError('stale uncharged last_error refused')
 if result['scientific_admission'] is not False or result['production_admission'] is not False:raise ValueError('diagnostic observation cannot confer admission')
 return result
def live_gate(proposal):
 from observe import observation
 inside=observation();admission=a.resources();policy=proposal['future_resource_policy']
 if admission['memory_max_bytes']!=policy['memory_max_bytes'] or admission['cpu_quota']!=policy['cpu_quota'] or admission['cpu_period']!=policy['cpu_period']:raise ValueError('actual cgroup policy mismatch')
 status=dict(line.split(':',1) for line in inside['status'].splitlines() if ':' in line)
 if any(status[k].strip()!='0000000000000000' for k in ('CapPrm','CapEff','CapBnd','CapAmb')) or status['NoNewPrivs'].strip()!='1' or inside['uid']!=0:raise ValueError('approved UID0 capability policy mismatch')
 if inside['membership']!='0::/\n':raise ValueError('private cgroup view required')
 mount=next(x for x in inside['mountinfo'].splitlines() if x.split()[4]=='/sys/fs/cgroup')
 if 'ro' not in mount.split()[5].split(','):raise ValueError('private read-only cgroup mount required')
 view=next(x for x in inside['mountinfo'].splitlines() if x.split()[4]==str(R/'host_cgroup_view'))
 if 'ro' not in view.split()[5].split(','):raise ValueError('private read-only host ancestor view required')
 if subprocess.check_output(['systemctl','--user','show',policy['unit'],'--property=RuntimeMaxUSec','--value'],text=True).strip()!='1min':raise ValueError('actual 60-second total unit wall cap required')
 available=int(next(line.split()[1] for line in inside['meminfo'].splitlines() if line.startswith('MemAvailable:')))*1024
 if int(Path('/sys/fs/cgroup/memory.max').read_text())-int(Path('/sys/fs/cgroup/memory.current').read_text())<6442450944 or available<6442450944:raise ValueError('unchanged 6GiB headroom unavailable')
 ancestor=c.load(Path(policy['outside_observation_file']));effective=float(len(inside['affinity']));rows=[]
 if policy['unit'] not in ancestor['membership'] or ancestor['ppid']!=inside['pid']:raise ValueError('fresh unit/PID lineage mismatch')
 if any(ancestor['namespace'][k]==inside['namespace'][k] for k in ('mnt','cgroup')):raise ValueError('fresh private namespace lineage mismatch')
 for old in ancestor['ancestors']:
  path=R/'host_cgroup_view'/Path(old['path']).relative_to('/sys/fs/cgroup')
  if old['path']=='/sys/fs/cgroup':continue
  q,p=(path/'cpu.max').read_text().split();m=(path/'memory.max').read_text().strip();current=int((path/'memory.current').read_text());rows.append(dict(path=str(path),cpu_max=[q,p],memory_max=m,memory_current=current))
  if q!='max':effective=min(effective,int(q)/int(p))
  if m!='max' and int(m)-current<6442450944:raise ValueError('ancestor headroom unavailable')
 if effective<2:raise ValueError('two effective CPUs unavailable')
 return dict(observation=inside,admission=admission,fresh_ancestors=rows,host_MemAvailable=available,effective_CPU=effective,nonroot_UID_validation=False)
def run_authorized(proposal_path,expected,auth_path,auth_sha):
 # The current preparation never enters this function.
 proposal=c.load(proposal_path);queries,build=preflight(proposal,expected);auth=authorization_check(proposal,auth_path,auth_sha);unconsumed(proposal);live=live_gate(proposal)
 h=a.host(REPO,proposal['host_build_dir'])
 if h.identity()!=proposal['host_identity']:raise ValueError('host identity changed')
 a.probe_host(h);unconsumed(proposal);root=Path(proposal['future_output_root']);started=time.monotonic()
 binding=c.seal(dict(proposal_sha256=expected,authorization_sha256=auth_sha,query_scope_sha256=queries['query_scope_sha256'],live=live),'binding_sha256')
 consume(proposal['future_registry'],binding);root.mkdir(exist_ok=False);write(root/'LIVE_BINDING.json',binding);returns=[]
 for key in QUERY_KEYS:
  if time.monotonic()-started>=60:break
  qid,impl=key.split('_');query=next(q for q in queries['queries'] if q['query_id']==qid);out=root/key;out.mkdir(exist_ok=False)
  command=[proposal['binary']['path'],'--hh-single',qid,impl,queries['query_scope_sha256']]
  consume(out/'CALL_STARTED.json',dict(query_key=key,proposal_sha256=expected,binding_sha256=binding['binding_sha256'],command=command,max_field_callbacks=1,integrations=0,no_retry=True))
  with (out/'native.stdout').open('xb') as so,(out/'native.stderr').open('xb') as se:
   proc=h._launch(command,stdout=so,stderr=se,env={'PATH':'/usr/bin:/bin','LD_LIBRARY_PATH':str(BACKEND/'prefix/lib'),'OMP_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'},memory_mib=1024,cpu_seconds=10,nofork=True)
   timed=False
   try:rc=proc.wait(timeout=min(10,max(.001,60-(time.monotonic()-started))))
   except subprocess.TimeoutExpired:timed=True;proc.kill();rc=proc.wait()
  record=dict(query_key=key,native_pid=proc.pid,command=command,exit_status=rc,timed_out=timed,stdout=ref(out/'native.stdout'),stderr=ref(out/'native.stderr'),integrations=0,no_retry=True)
  validation_error=None
  if rc==0 and not timed:
   try:
    observation=c.load(out/'native.stdout');validate_observation(observation,query,impl,proposal['geometry'][qid],queries['query_scope_sha256'],build['diagnostic_source_sha256']);write(out/'OBSERVATION.json',observation);record['status']='OBSERVED_NOT_SCIENTIFIC_ADMISSION'
   except (ValueError,OSError,KeyError,TypeError) as exc:validation_error=str(exc);record['status']='UNRESOLVED_BINDING_ERROR';record['error']=validation_error
  else:record['status']='INCONCLUSIVE_EXECUTION_FAILURE'
  write(out/'RETURN.json',record);returns.append(record)
  if rc!=0 or timed or validation_error:break
 comparisons=[]
 for qid in ('Q272','Q000'):
  left_path=root/(qid+'_cached')/'OBSERVATION.json';right_path=root/(qid+'_reference')/'OBSERVATION.json'
  if not left_path.exists() or not right_path.exists():continue
  left=c.load(left_path);right=c.load(right_path)
  if not all(x['record']['physical_output_finite'] and x['mapped_output_finite'] for x in (left,right)):continue
  if left['record']['after']['cache']['terms_started']!=107 or left['record']['after']['cache']['terms_completed']!=107:raise ValueError('finite cached field must complete107 terms')
  if any(x['record']['after']['failures'] or x['record']['after']['last_error'] for x in (left,right)):raise ValueError('finite field must have clean complete loop return')
  for field in ('physical','mapped'):
   lb=left['record']['physical_output_dump'] if field=='physical' else left['mapped_output_dump'];rb=right['record']['physical_output_dump'] if field=='physical' else right['mapped_output_dump']
   command=[proposal['binary']['path'],'--compare-balls',lb['real'],lb['imag'],rb['real'],rb['imag']]
   compare_dir=root/('comparison_'+qid+'_'+field);compare_dir.mkdir(exist_ok=False)
   with (compare_dir/'stdout').open('xb') as so,(compare_dir/'stderr').open('xb') as se:
    process=h._launch(command,stdout=so,stderr=se,env={'PATH':'/usr/bin:/bin','LD_LIBRARY_PATH':str(BACKEND/'prefix/lib')},memory_mib=1024,cpu_seconds=10,nofork=True)
    try:rc=process.wait(timeout=min(10,max(.001,60-(time.monotonic()-started))))
    except subprocess.TimeoutExpired:process.kill();process.wait();raise ValueError('read-only comparison timed out; no retry')
   if rc:raise ValueError('read-only comparison failed; no retry')
   result=c.load(compare_dir/'stdout');comparisons.append(dict(query_id=qid,field=field,result=result,native_pid=process.pid,command=command,exit_status=rc,HH_evaluations=0,integrations=0))
 write(root/'CANDIDATE_ENCLOSURE_COMPARISON.json',dict(comparisons=comparisons,reference_107_term_completion_basis='Pinned source full loop and finite clean return; not a cache counter',accuracy_or_cell_admission=False))
 all_finite=len(returns)==4 and all((root/x['query_key']/'OBSERVATION.json').exists() and c.load(root/x['query_key']/'OBSERVATION.json')['mapped_output_finite'] and c.load(root/x['query_key']/'OBSERVATION.json')['record']['physical_output_finite'] for x in returns)
 candidate_consistent=all_finite and len(comparisons)==4 and all(x['result']['overlap'] for x in comparisons)
 write(root/'RETURN.json',dict(candidate_field_finite_and_107_complete_and_overlap=candidate_consistent,comparison_count=len(comparisons),status='FD2_CANDIDATE_OBSERVATIONS_AWAITING_REVIEW' if len(returns)==4 and all(x['status']=='OBSERVED_NOT_SCIENTIFIC_ADMISSION' for x in returns) else 'UNRESOLVED',returns=returns,scope_consumed=True,integrations=0,coverage_changes=0,scientific_admission=False,production_admission=False,no_retry=True))
 return 0 if len(returns)==4 and all(x['status']=='OBSERVED_NOT_SCIENTIFIC_ADMISSION' for x in returns) else 2
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['run']);ap.add_argument('--proposal',required=True);ap.add_argument('--expected',required=True);ap.add_argument('--authorization',required=True);ap.add_argument('--authorization-sha',required=True);args=ap.parse_args()
 try:raise SystemExit(run_authorized(args.proposal,args.expected,args.authorization,args.authorization_sha))
 except (ValueError,OSError,KeyError,TypeError) as exc:print(json.dumps(dict(status='BLOCKED',reason=str(exc),automatic_retry=False)),file=sys.stderr);raise SystemExit(2)
