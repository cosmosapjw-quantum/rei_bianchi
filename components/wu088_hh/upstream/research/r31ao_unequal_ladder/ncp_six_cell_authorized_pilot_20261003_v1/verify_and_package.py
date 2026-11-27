"""Read-only post-run validation, preservation, reporting and local packaging."""
from common import *
import zipfile,shutil,datetime,jsonschema
def main():
 q=c.load(PROPOSAL);c.check_seal(q,'proposal_sha256');assert sha(PROPOSAL)==PROPOSAL_BYTES_SHA
 result=c.load(PILOT/'RETURN.json');binding=c.load(PILOT/'EXECUTION_BINDING.json');c.check_seal(binding,'binding_sha256')
 p,b=a.load_binding(PILOT,result['binding_sha256']);m=a.validate_build(REPO,q['build_dir'],BUILD_SHA);h=a.host(REPO,q['host_build_dir']);d=a.driver(REPO)
 live=c.load(E/'LIVE_REVALIDATION.json');c.check_seal(live,'live_revalidation_sha256')
 assert live['proposal_self_sha256']==PROPOSAL_SHA and b['prepared_sha256']==PREPARED_SHA and b['scope_sha256']==SCOPE_SHA and b['build_sha256']==BUILD_SHA and b['host_identity']==q['host_identity'] and b['resource_admission']==live['resources']['admission']
 assert result['dispatched_cell_ids']==list(c.PILOT_IDS) and result['native_dispatch_attempts']==6 and result['native_observed']==6 and result['status']=='STOPPED_FIRST_REJECTION'
 assert len(result['returns'])==6 and len({x['cell_id'] for x in result['returns']})==6
 registry_path=NODE/'run_registry'/(SCOPE_SHA+'.json');registry=c.load(registry_path);started=c.load(PILOT/'RUN_STARTED.json')
 assert registry==started and registry['binding_sha256']==b['binding_sha256'] and registry['prepared_root']==str(PILOT)
 baseline,baseline_coverage,baseline_ledger=c.replay_baseline(REPO)
 assert baseline==c.load(PILOT/'BASELINE_CELLS.json') and baseline_coverage==c.load(PILOT/'BASELINE_COVERAGE.json')
 records=list(baseline);accepted=[];rejected=[];timeline=[];native_receipts=[]
 for i in c.PILOT_IDS:
  ad=PILOT/f'attempts/{i:03d}';ret=c.load(ad/'RETURN.json');dispatch=c.load(ad/'DISPATCH.json');worker=c.load(ad/'WORKER_STARTED.json')
  assert ret==next(v for v in result['returns'] if v['cell_id']==i)
  assert dispatch==dict(cell_id=i,binding_sha256=b['binding_sha256'],charged_evaluations=200000)
  assert worker['cell_id']==i and worker['binding_sha256']==b['binding_sha256']
  rawpath=PILOT/f'raw/{i:03d}.json';raw=c.load(rawpath);c.check_seal(raw,'result_sha256');assert ref(rawpath)==ret['raw']
  w=raw['wrapper'];plan=c.load(PILOT/f'plans/{i:03d}.json');native=d.parse_json(Path(str(rawpath)+'.stdout').read_bytes())
  for key,value in dict(index=0,task_sha256=plan['tasks'][0]['task_sha256'],plan_sha256=plan['plan_sha256'],archive_sha256=c.INPUT_SHA,input_record_sha256=c.RECORD_SHA,build_source_sha256=c.SOURCE_SHA,precision_bits=128,accepted_component_radius_exp=-57).items():assert native[key]==value
  assert w['build_manifest_sha256']==BUILD_SHA and w['binary_sha256']==m['binary_sha256'] and w['archive_sha256']==c.INPUT_SHA and w['input_record_sha256']==c.RECORD_SHA and w['native_limits']==c.LIMITS and w['backend_provenance_sha256']==m['backend_provenance_sha256'] and w['linkage']==m['linkage']
  h.validate_receipt(w['process_host'],command=w['command'],limits=c.LIMITS,output_path=rawpath)
  assert w['process_host']['timed_out'] is False and w['native_execution_observed'] is True
  for suffix in ('stdout','stderr'):assert sha(Path(str(rawpath)+'.'+suffix))==w['native_'+suffix+'_sha256']
  if ret['accepted']:
   cell=a.normalize(PILOT,p,b,i);assert cell==c.load(PILOT/f'normalized/{i:03d}.json');records.append(cell);accepted.append(i)
   assert ret['worker_returncode']==0 and native['status']=='RADIUS_MET'
  else:
   assert not (PILOT/f'normalized/{i:03d}.json').exists() and raw['schema']=='WU088_LOG2_NATIVE_INTERIOR_REJECTION_V1'
   assert native==d.parse_json(raw['native_stdout'].encode()) and native['status']=='INTEGRATOR_NO_CONVERGENCE' and native['accepted'] is False and native['rectangle'] is None and ret['worker_returncode']==2
   try:d.validate_result(native,plan=plan,task=plan['tasks'][0],manifest=m,limits=c.LIMITS)
   except ValueError as exc:original_validator_rejection=str(exc)
   else:raise AssertionError('original validator admitted rejected output')
   rejected.append(dict(cell_id=i,classification='NUMERICAL_INCONCLUSIVE_INTEGRATOR_NO_CONVERGENCE',native_status=native['status'],native_exit=w['returncode'],worker_exit=ret['worker_returncode'],host_timed_out=False,worker_timed_out=ret['timed_out'],rectangle=None,dispatched_evaluations=native['dispatched_evaluations'],integration_calls=native['integration_calls'],flint_status=native['flint_status'],diagnostic_counters=native['diagnostics']['counters'],original_validator_rejection=original_validator_rejection,source_or_theory_error_established=False,implementation_error_established=False,resource_limit_exhaustion_established=False))
  assert ret['timed_out'] is False
  timeline.append(dict(cell_id=i,dispatch_mtime_ns=(ad/'DISPATCH.json').stat().st_mtime_ns,worker_started_mtime_ns=(ad/'WORKER_STARTED.json').stat().st_mtime_ns,return_mtime_ns=(ad/'RETURN.json').stat().st_mtime_ns,worker_pid=worker['pid'],native_pid=w['process_host']['native_process_pid'],accepted=ret['accepted']))
  native_receipts.append(dict(cell_id=i,raw=ref(rawpath),native_status=native['status'],native_wall_ns=w['elapsed_wall_ns'],host= w['process_host']))
 coverage=c.sum_cells(records);actual=c.load(PILOT/'COVERAGE.json');c.check_seal(actual,'coverage_sha256');assert coverage==actual and coverage['accepted_cell_count']==24 and len(coverage['missing_cell_ids'])==265
 assert accepted==[275,67,288,16] and [r['cell_id'] for r in rejected]==[272,0]
 first=min(x['return_mtime_ns'] for x in timeline if not x['accepted']);assert all(x['dispatch_mtime_ns']<first for x in timeline)
 events=sorted([(x['dispatch_mtime_ns'],1) for x in timeline]+[(x['return_mtime_ns'],-1) for x in timeline]);active=0;peak=0
 for t,delta in events:active+=delta;peak=max(peak,active)
 assert peak<=2 and active==0
 schema=c.load(NODE/'EXTERNAL_RETURN.schema.json');jsonschema.Draft202012Validator(schema).validate(result)
 write(E/'RAW_BINDING_AND_COVERAGE_VERIFICATION.json',dict(status='PASS',original_normalize_replay_accepted=accepted,original_validator_refused_rejected=rejected,baseline_20_raw_replay_only=True,new_science_during_validation=0,native_receipts=native_receipts,coverage=ref(PILOT/'COVERAGE.json'),accepted_cells=24,missing_cells=265,missing_domain_contribution=coverage['missing_domain_contribution'],external_RETURN_schema='PASS',scope_consumed=True,registry=ref(registry_path)))
 write(E/'DISPATCH_TIMELINE.json',dict(timeline=timeline,first_rejection_cell=272,first_rejection_RETURN_mtime_ns=first,all_dispatches_before_first_observed_rejection=True,cell0_already_inflight_at_first_rejection=True,no_dispatch_after_first_observed_rejection=True,max_inflight_from_observed_file_timeline=peak,no_retry=True,all_inflight_drained=True,limitation='File timestamps corroborate original source-bound queue; they are not independent kernel scheduling attestation'))
 prior=c.load(E/'PRESERVATION_BEFORE.json') if (E/'PRESERVATION_BEFORE.json').stat().st_size<16*1024**2 else json.loads((E/'PRESERVATION_BEFORE.json').read_text())
 changes=[]
 for row in prior:
  f=Path(row['path']);st=f.lstat();now=dict(path=str(f),mtime_ns=st.st_mtime_ns,mode=st.st_mode&0o777)
  if f.is_symlink():now.update(kind='symlink',target=os.readlink(f))
  else:now.update(kind='file',bytes=st.st_size,sha256=sha(f))
  if now!=row:changes.append(dict(before=row,after=now))
 assert not changes
 claims=[dict(**ref(Path(x['path'])),mtime_ns=x['mtime_ns'],PID_text=Path(x['path']).read_text()) for x in prior if x['path'].endswith(('/105.json.claim','/057.json.claim'))]
 assert any(x['PID_text']=='51' for x in claims) and any(x['PID_text']=='74' for x in claims)
 write(E/'PRESERVATION_AFTER.json',dict(original_items_verified=len(prior),changes=changes,claims=claims,claim_process_or_race_cause_inferred=False,PREPARED=ref(PILOT/'PREPARED.json'),proposal=ref(PROPOSAL),old_failure_trees_and_R1_R2_preserved=True))
 running=[]
 for proc in Path('/proc').glob('[0-9]*'):
  try:
   comm=(proc/'comm').read_text().strip()
   if comm=='primitive_worker':running.append(dict(pid=int(proc.name),comm=comm))
  except OSError:pass
 assert not running
 unit=subprocess.run(['systemctl','--user','show',UNIT,'-p','Result','-p','ExecMainStatus','-p','MemoryPeak','-p','CPUUsageNSec','-p','InvocationID','-p','ControlGroup'],capture_output=True,text=True)
 write(E/'UNIT_FINAL_OBSERVATION.json',dict(command=unit.args,exit_status=unit.returncode,stdout=unit.stdout,stderr=unit.stderr,running_primitive_workers=running,limitation='Transient leaf removed after completed service; MemoryPeak is the systemd-reported value, not an independent whole-campaign profiler'))
 inventory=registry_inventory();write(E/'RECOVERY_INVENTORY_AFTER.json',inventory);assert inventory['scope_consumed'] is True
 absent=[]
 for i in (272,0):absent.append(dict(path=str(PILOT/f'normalized/{i:03d}.json'),status='absent',reason='Native numerical nonconvergence; original validator rejected and no valid rectangle'))
 absent.append(dict(path='/sys/fs/cgroup/'+UNIT+'/memory.events_after_exit',status='absent',reason='Transient unit leaf removed after drained completion; live pre-execution events preserved'))
 write(E/'ABSENT_FILES.json',absent)
 write(E/'AUTHORITY_CHECK.json',dict(status='EXACT_USER_SCIENCE_AUTHORIZATION_MATCHED',authorization=ref(E/'AUTHORIZATION_RECORD.json'),original_user_message=ref(R/'AUTHORIZATION_USER_MESSAGE_KO.md'),proposal_self_sha256=PROPOSAL_SHA,proposal=ref(PROPOSAL),prepared_self_sha256=PREPARED_SHA,scope_sha256=SCOPE_SHA,worker_build_self_sha256=BUILD_SHA,live_revalidation=ref(E/'LIVE_REVALIDATION.json'),execution_binding=ref(PILOT/'EXECUTION_BINDING.json'),binding_self_sha256=b['binding_sha256'],registry=ref(registry_path),invocations=1,science_dispatch_count=6,scope_consumed=True,no_retry=True,scope_expansion=False))
 summary=dict(schema='WU088_NCP_HANDOFF_RETURN_V1',status='PILOT_STOPPED_FIRST_REJECTION',original_status=result['status'],science_dispatch_count=6,source_bound_native_observed=6,scope_consumed=True,accepted_new_cells=accepted,rejected_cells=rejected,accepted_cell_count=24,missing_cell_count=265,missing_contribution='UNBOUNDED_NOT_ZERO',epsilon_C=None,epsilon_R=None,B22='OPEN_UNDETERMINED',scientific_admission=False,production_admission=False,proposal_self_sha256=PROPOSAL_SHA,authorization=ref(E/'AUTHORIZATION_RECORD.json'),live_revalidation=ref(E/'LIVE_REVALIDATION.json'),binding_self_sha256=b['binding_sha256'],original_RETURN=ref(PILOT/'RETURN.json'),COVERAGE=ref(PILOT/'COVERAGE.json'),campaign_wall_seconds=result['campaign_wall_ns']/1e9,adapter_exit_status=2,no_auto_retry=True,backend_rebuilds=0,original_items_preserved=len(prior),absence_evidence=ref(E/'ABSENT_FILES.json'),next_action='Review preserved numerical nonconvergence evidence for cells272/0 and four newly validated rectangles; this exact six-cell scope is consumed and must not be rerun or expanded',R31AK='frozen',z075='holdout',B128_B160='consumed',B192='reuse',full_domain_D_epsilon_sigma_k_production_authorized=False)
 write(E/'NCP_HANDOFF_RETURN.json',summary)
 report=f'''# WU088_HH 고정 6셀 pilot 반환\n\n종료 상태: **PILOT_STOPPED_FIRST_REJECTION**. 사용자 원문 승인에 결속된 scope를 원 runtime_adapter CLI로 1회 실행했으며, native dispatch/관측은 6회, scope_consumed=true다. 재빌드·재시도·scope 확대는 없었다.\n\n|셀|원 native 결과|원 validator 결과|평가 수|적분 호출|\n|---:|---|---|---:|---:|\n'''
 for i in c.PILOT_IDS:
  n=d.parse_json((PILOT/f'raw/{i:03d}.json.stdout').read_bytes());report+=f"|{i}|{n['status']}|{'수락' if i in accepted else '거절'}|{n['dispatched_evaluations']}|{n['integration_calls']}|\n"
 report+=f'''\n기존20셀과 새 수락4셀을 원 exact coverage 산술로 대조해 **24/289**, missing265를 확인했다. 미계산 기여는 unbounded이며 0이 아니다. epsilon_C/R=null, B22=OPEN_UNDETERMINED, scientific/production admission=false를 유지한다. endpoint·normalization·전체 D·full49·sigma/k·trajectory를 인증하지 않는다.\n\n272와 0은 native exit2/INTEGRATOR_NO_CONVERGENCE, rectangle=null, FLINT status2다. 272의 inner_no_convergence109, 0의124가 보고되었다. Host/worker wall timeout은 없었고, inner_resource_limit 및 inner_invalid_contract 카운터는0이었다. 이는 현재 고정 예산에서 수치 결과가 결정되지 않은 상태다. 근본 source/theory/구현 오류 또는 정확한 실패 원인은 이 반환만으로 확정하지 않는다. Native stderr는 비어 있다. 원 adapter의 전체 exit2는 거절을 반영한다.\n\n첫 거절은272의 RETURN이며, 0은 그 전에 이미 dispatch되어 회수됐다. 승인 순서[275,67,288,272,16,0], 동시 worker2, 각 셀1회, 최대6회를 지켰다. 첫 거절 관측 후 dispatch는 없고 inflight를 모두 회수했다. campaign wall={result['campaign_wall_ns']/1e9:.6f}초(준비/preflight 제외).\n\n실행 identity\n\n- Remote/preparation HEAD: {HEAD}. 과거 commit reset 없음.\n- Proposal self SHA256: {PROPOSAL_SHA}\n- Proposal file SHA256: {PROPOSAL_BYTES_SHA}\n- PREPARED self SHA256: {PREPARED_SHA}\n- Scope SHA256: {SCOPE_SHA}\n- Worker build self SHA256: {BUILD_SHA}\n- 실제 EXECUTION_BINDING self SHA256: {b['binding_sha256']}\n- Live revalidation self SHA256: {live['live_revalidation_sha256']}\n\n새 unit의 실제 memory.max34359738368, cpu.max400000/100000, affinity64와 원6GiB/2CPU gate, 조상 제한·현재 사용량·host 가용 여유를 관측했다. Private mount/cgroup view와 read-only cgroup mount, UID0 capabilities0, NoNewPrivs1을 확인했고 원 host launcher child의 동일 소속·namespace와 seccomp nofork 검증을 통과했다. UID0 경로를 비root 검증으로 주장하지 않는다. cgroup-v2 hierarchy root의 제한 인터페이스 부재는 absent 그대로 기록했으며 숫자를 주입하지 않았다. 단위 한도는 RAM 예약이나 모든 escape/경주를 독립 검증했다는 뜻이 아니다. 단위 종료로 leaf가 제거된 후의 live 수치는 재구성하지 않았다.\n\n원 serializer self-hash와 별도 file bytes, 원 SOURCE_LOCK1834개,6개 plan/input/native source, adapter, host launcher, worker binary, backend/system-library linkage를 실행 전 대조했다. 성공 backend/worker를 재빌드하지 않았다. 승인 누락·proposal self/file hash 변경·소비 scope의4개 거절 검사는 dispatch 없이 수행했다. 새 helper의 초기 상대경로 처리 오류를 고쳐 검증했으며, 그 실패 때 run/worker/consume 호출은0회였다. 원40개 suite를 새 검사로 세거나 재실행하지 않았다.\n\n원 raw/sidecar/host receipt/source binding을 읽어4개 결과를 원 normalize로 다시 검증하고,2개 실패를 원 validator가 거절함을 확인했다. 기존20셀 replay는 원 raw 읽기와 산술만 수행했다. 새 과학 실행은 하지 않았다. 원 EXTERNAL_RETURN schema 검증도 통과했다.\n\n기존 자료 {len(prior)}개에서 bytes/SHA/mode/mtime/symlink 변경0. 원 실패 tree·R1/R2 결과·PREPARED·입력·20셀·B22 105/057 claim bytes/SHA/mtime/PID51/74를 보존했다. claim 존재로 process/race 원인을 확정하지 않았다. 기존 registry 부재를 확인한 후 원 adapter가 정확한 scope marker를 영구 생성했다. 새 directory/이름으로 소비를 우회하지 않는다. R31AK frozen,z0.75 holdout,B128/B160 consumed,B192 reuse를 유지했고 다른 저장소는 수정하지 않았다.\n\n반환 파일\n\nAUTHORIZATION_RECORD 및 원문, LIVE_REVALIDATION, 원 EXECUTION_BINDING/RUN_STARTED, PREPARED·6plans·baseline,6raw/sidecars,6attempts/worker 로그/RETURN,4normalized,COVERAGE와 원 RETURN, registry, 명령/exit logs 및 hash manifest를 패키지에 포함한다. 과거 성공 build와 전체 source/cache는 기존 검증 package를 참조하며 중복 다운로드하지 않았다. 누락 normalized272/000과 종료 후 cgroup leaf는 ABSENT_FILES에 사유를 기록했다.\n\n결과는 같은 branch의 새 continuation 경로에 additive/non-force 게시하고, ZIP·보고서·분리 receipt를 기존 Drive/Dropbox에 create-only 백업한다. ACK+name/size/object identity metadata tier를 사용하고 output RESTORE_VERIFIED=false로 기록한다. Provider의 ACK/metadata는 content restore 증거와 구분한다. 게시/백업의 실제 ID·HEAD·bytes/SHA는 DELIVERY_INDEX/분리 receipt에 기록한다.\n\n다음 최소 action은 보존된 실패2셀의 수치 evidence와 새4셀의 원시 rectangle을 검토하는 것이다. 이번 승인된 scope는 소비되었으며 재실행하거나 추가 셀을 계산하지 않고 종료한다.\n'''
 (E/'WORK_REPORT_KO.md').write_text(report)
 shutil.copy2(NODE/'EXTERNAL_RETURN.schema.json',E/'EXTERNAL_RETURN.schema.json')
 # Direct ZIP reads avoid scattering copies of canonical runtime/input files.
 payload={}
 for f in sorted(E.iterdir()):
  if f.is_file():payload['evidence/'+f.name]=f
 for f in sorted(R.glob('*.py')):payload['launcher/'+f.name]=f
 for name in ('namespace_entry.sh','AUTHORIZATION_USER_MESSAGE_KO.md'):payload['launcher/'+name]=R/name
 for f in sorted(PILOT.rglob('*')):
  if f.is_file():payload['pilot/'+str(f.relative_to(PILOT))]=f
 payload['registry/'+registry_path.name]=registry_path
 for name,original in [('proposal/BINDING_PROPOSAL.json',PROPOSAL),('identities/WORKER_BUILD.json',Path(q['build_dir'])/'BUILD.json'),('identities/HOST_BUILD.json',Path(q['host_build_dir'])/'BUILD.json'),('identities/BACKEND_BUILD_PROVENANCE.json',Path(q['backend_provenance']['path'])),('source/SOURCE_LOCK.json',NODE/'SOURCE_LOCK.json'),('source/runtime_adapter.py',NODE/'runtime_adapter.py'),('source/coverage_contract.py',NODE/'coverage_contract.py')]:payload[name]=original
 files=[dict(archive_path=arc,**ref(f),mtime_ns=f.stat().st_mtime_ns,mode=f.stat().st_mode&0o777) for arc,f in payload.items()]
 write(E/'FILE_MANIFEST.json',dict(schema='WU088_PILOT_RESULT_MANIFEST_V1',files=files,self_excluded=True,archive_exact_payload_paths=True));payload['evidence/FILE_MANIFEST.json']=E/'FILE_MANIFEST.json'
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');z=R/('WU088_HH_NCP_SIX_CELL_PILOT_'+stamp+'.zip')
 with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,strict_timestamps=False) as out:
  for arc,f in payload.items():out.write(f,arc)
 with zipfile.ZipFile(z) as archive:
  assert archive.testzip() is None and set(archive.namelist())==set(payload)
  for row in files:
   data=archive.read(row['archive_path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
 report_path=R/(z.stem+'_REPORT_KO.md');shutil.copy2(E/'WORK_REPORT_KO.md',report_path)
 local=dict(package=dict(name=z.name,**ref(z)),report=dict(name=report_path.name,**ref(report_path)),manifest=ref(E/'FILE_MANIFEST.json'),payload_files_verified=len(payload),status=summary['status'],proposal_self_sha256=PROPOSAL_SHA,binding_sha256=b['binding_sha256'],science_dispatch_count=6,scope_consumed=True,accepted_cells=24,missing_cells_unbounded=265)
 write(R/'LOCAL_PACKAGE_IDENTITY.json',local);print(json.dumps(local))
if __name__=='__main__':main()
