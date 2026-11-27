"""Validate saved raw observations and preservation, without any callback."""
from pathlib import Path
import sys,json,stat,datetime,subprocess
TASK=Path(__file__).resolve().parent;E=TASK/'evidence';PREP=TASK.parent/'fd1_prep_20261003_v3'
sys.path.insert(0,str(PREP))
from support import c,ref,sha,write,OLD,PILOT,REPO
from diagnostic_adapter import preflight,authorization_check,validate_observation,QUERY_KEYS
def file_observation(p):
 s=p.stat();return dict(file=ref(p),mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns)
def main():
 proposal=c.load(PREP/'evidence/DIAGNOSTIC_PROPOSAL.json');queries,build=preflight(proposal,proposal['proposal_sha256'])
 auth=c.load(E/'AUTHORIZATION_RECORD.json');authorization_check(proposal,E/'AUTHORIZATION_RECORD.json',auth['authorization_sha256'])
 root=Path(proposal['future_output_root']);registry=c.load(proposal['future_registry']);c.check_seal(registry,'binding_sha256')
 binding=c.load(root/'LIVE_BINDING.json');c.check_seal(binding,'binding_sha256');assert registry==binding and binding['proposal_sha256']==proposal['proposal_sha256'] and binding['authorization_sha256']==auth['authorization_sha256'] and binding['query_scope_sha256']==queries['query_scope_sha256']
 outside=c.load(PREP/'evidence/FD1_DIAGNOSTIC_OUTSIDE.json');live=binding['live'];inside=live['observation']
 assert 'wu088-fd1-diagnostic.service' in outside['membership'] and outside['ppid']==inside['pid'] and inside['membership']=='0::/\n'
 assert all(outside['namespace'][k]!=inside['namespace'][k] for k in ('mnt','cgroup'))
 status=dict(line.split(':',1) for line in inside['status'].splitlines() if ':' in line)
 assert all(status[k].strip()=='0000000000000000' for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb')) and status['NoNewPrivs'].strip()=='1' and inside['uid']==0
 assert live['admission']['memory_max_bytes']==34359738368 and live['admission']['cpu_quota']==400000 and live['admission']['cpu_period']==100000 and live['effective_CPU']>=2 and live['host_MemAvailable']>=6442450944
 assert len(list(root.glob('*/CALL_STARTED.json')))==4
 returns=c.load(root/'RETURN.json');assert returns['scope_consumed'] is True and returns['integrations']==0 and returns['coverage_changes']==0 and len(returns['returns'])==4
 rows=[];files=[];previous_return=None;commands=[]
 for index,key in enumerate(QUERY_KEYS):
  directory=root/key;qid,impl=key.split('_');query=next(q for q in queries['queries'] if q['query_id']==qid)
  marker=c.load(directory/'CALL_STARTED.json');ret=c.load(directory/'RETURN.json');raw=c.load(directory/'native.stdout');observation=c.load(directory/'OBSERVATION.json')
  assert raw==observation and marker['query_key']==key and marker['proposal_sha256']==proposal['proposal_sha256'] and marker['binding_sha256']==binding['binding_sha256']
  assert marker['command']==ret['command']==proposal['native_commands'][index] and marker['max_field_callbacks']==1 and marker['integrations']==0 and marker['no_retry'] is True
  assert ret==returns['returns'][index] and ret['exit_status']==0 and ret['timed_out'] is False and ret['status']=='OBSERVED_NOT_SCIENTIFIC_ADMISSION'
  assert ret['stdout']==ref(directory/'native.stdout') and ret['stderr']==ref(directory/'native.stderr')
  validate_observation(observation,query,impl,proposal['geometry'][qid],queries['query_scope_sha256'],build['diagnostic_source_sha256'])
  r=observation['record'];assert r['callback_invocations']==observation['HH_evaluations']==1 and observation['integrations']==0
  started=(directory/'CALL_STARTED.json').stat().st_mtime_ns;ended=(directory/'RETURN.json').stat().st_mtime_ns
  assert ended>=started and (previous_return is None or started>=previous_return);previous_return=ended
  row=dict(query_key=key,native_pid=ret['native_pid'],exit_status=ret['exit_status'],timed_out=False,callback_invocations=1,integrations=0,before=r['before'],after=r['after'],fresh_failure=r['fresh_failure'],physical_callback_return=r['physical_callback_return'],physical_finite=r['physical_output_finite'],mapped_finite=observation['mapped_output_finite'],log_map_return=observation['log_map_return'],physical_output_dump=r['physical_output_dump'],mapped_output_dump=observation['mapped_output_dump'],inner_log_box=observation['inner_log_box'],outer_log_box=observation['outer_log_box'],physical_t=observation['physical_t'],physical_u=observation['physical_u'],margin=observation['margin'],marker_mtime_ns=started,return_mtime_ns=ended,marker_to_return_seconds=(ended-started)/1e9,timing_basis='Filesystem event window includes launch/wait/validation; not exact native wall time',raw=ref(directory/'native.stdout'))
  rows.append(row);files.extend(file_observation(p) for p in directory.iterdir());commands.append(dict(command=ret['command'],exit_status=0,native_pid=ret['native_pid'],via_original_adapter=True,direct_shell_invocation=False,no_retry=True,marker_mtime_ns=started,return_mtime_ns=ended))
 assert len({x['native_pid'] for x in rows})==4
 observed=c.load(E/'NATIVE_PROCESS_OBSERVATIONS.json')['processes']
 absent=[]
 for row in rows:
  if row['native_pid'] not in {x['pid'] for x in observed}:absent.append(dict(item='sampled /proc metadata for native PID '+str(row['native_pid']),reason='Short-lived native process completed between 5ms observation samples; original adapter PID, CALL_STARTED, raw stdout and RETURN prove execution. Exact per-native start/stop wall time was not recorded by original adapter.'))
 preserved=json.loads((E/'PRESERVATION_BEFORE.json').read_text());changes=[]
 for row in preserved:
  p=Path(row['path']);s=p.lstat();v=dict(mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns)
  if row['kind']=='symlink':v['target']=str(p.readlink())
  else:v.update(bytes=s.st_size,sha256=sha(p))
  if any(row[k]!=value for k,value in v.items()):changes.append(dict(path=str(p),differences={k:value for k,value in v.items() if row[k]!=value}))
 assert not changes
 claims=[dict(before=x,PID_string=Path(x['path']).read_text(),PID_is_not_running_process_assertion=True) for x in preserved if x['path'].endswith('/raw/105.json.claim') or x['path'].endswith('/raw/057.json.claim')]
 write(E/'OLD_STATE_PRESERVATION.json',dict(status='PASS',protected_entries=len(preserved),changed_entries=changes,B22_claims=claims,claim_process_or_race_cause_inferred=False,old_registry=proposal['old_registry'],old_scope_consumed=True,FD1_scope_consumed=True,proposal_file=ref(PREP/'evidence/DIAGNOSTIC_PROPOSAL.json'),accepted=24,missing_unbounded=265,epsilon_C=None,epsilon_R=None,B22='OPEN_UNDETERMINED',scientific_admission=False,production_admission=False,backend_worker_sidecar_rebuilds=0,other_repositories_modified=False))
 # Keep live/private loader checks separate from this post-run root-view readback.
 ldd=subprocess.run(['/usr/bin/ldd',proposal['binary']['path']],env={'PATH':'/usr/bin:/bin','LD_LIBRARY_PATH':str(OLD/'prep_r2/backend/prefix/lib')},capture_output=True,text=True,check=True)
 (E/'post_run_loader.stdout.log').write_text(ldd.stdout);(E/'post_run_loader.stderr.log').write_text(ldd.stderr)
 write(E/'LIVE_REVALIDATION.json',dict(status='PASS',binding_file=ref(root/'LIVE_BINDING.json'),binding_self_sha256=binding['binding_sha256'],outside_observation=ref(PREP/'evidence/FD1_DIAGNOSTIC_OUTSIDE.json'),fresh_PID=inside['pid'],fresh_namespaces=inside['namespace'],actual_private_live=binding['live'],live_loader_and_host_identity_checked_by_original_run_before_consumption=True,original_run_preflight=ref(PREP/'diagnostic_adapter.py'),post_run_loader_observation=ref(E/'post_run_loader.stdout.log'),post_run_loader_not_mislabeled_as_private_live_capture=True,UID=0,nonroot_UID_validation=False,dispatch_workers=1,original_resource_admission_capacity_concurrency=live['admission']['concurrency'],sequential_callback_order=list(QUERY_KEYS)))
 write(E/'RAW_OBSERVATION_AND_BINDING_VERIFICATION.json',dict(status='PASS',original_observation_validator_used=True,validator_only_not_HH_rerun=True,queries=rows,total_field_callbacks=4,total_integrations=0,sequential_single_worker=True,exact_input_geometry_margin_signed107_precision_preserved=True,native_exit_statuses=[0]*4,scope_consumed=True,all_native_outputs_bound=True,files=files))
 write(E/'QUERY_COMPARISON.json',dict(status='FOUR_VALID_DIAGNOSTIC_OBSERVATIONS',diagnosis='UNRESOLVED',rows=rows,observation='All four fresh errors are backend returned nonfinite enclosure; all physical/mapped outputs nonfinite.',cached_observation='Each cached call starts 2 terms, completes 1; left/right/spatial evaluations 1/1/2; cache hits 0/0/0.',reference_cache_counters='Zero because reference implementation does not use this CacheStats object; zero is not evidence of zero reference work.',not_inferred=['Cache bug','Mathematical divergence','Unique failing backend helper','Integral enclosure','New accepted cell'],integrations=0,coverage_changes=0))
 write(E/'ABSENT_FILES.json',dict(absent=absent,final_RETURN_present=True,all_four_OBSERVATION_and_CALL_STARTED_present=True,missing_data_not_replaced_with_zero=True))
 result=dict(status='UNRESOLVED',execution_status=returns['status'],execution_completed=True,valid_observations=4,field_callbacks=4,integrations=0,scope_consumed=True,automatic_retry=False,authorization_self_sha256=auth['authorization_sha256'],proposal_self_sha256=proposal['proposal_sha256'],query_scope_sha256=queries['query_scope_sha256'],live_binding_self_sha256=binding['binding_sha256'],diagnosis='Fresh first-callback backend nonfinite refusal observed in cached and reference implementations for both fixed boxes; specific helper/numerical cause unresolved.',accepted=24,missing_unbounded=265,epsilon_C=None,epsilon_R=None,B22='OPEN_UNDETERMINED',scientific_admission=False,production_admission=False,additional_science_authorized=False)
 write(E/'FD1_HANDOFF_RETURN.json',result)
 now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();report=f'''# WU088_HH FD1 고정 4회 진단 반환

반환 상태: UNRESOLVED. 실행 자체는 원 adapter의 DIAGNOSTIC_OBSERVATIONS_AWAITING_REVIEW로 완료됐다. 고정 순서 Q272_cached → Q272_reference → Q000_cached → Q000_reference, 각1회/총4 field callback, 적분0회다. 네 native exit0·timeout=false와 원 observation validator를 확인했다. FD1 scope는 영구 소비됐으며 원6셀 scope도 소비된 상태를 유지한다. 이 반환 뒤 추가 실행·retry·box 확대는 하지 않는다.

보고 시각: {now} (Asia/Seoul). 승인 사용자 원문을 별도 UTF-8 파일로 보존하고 원 seal 방식 AUTHORIZATION_RECORD를 만들었다. proposal self SHA {proposal['proposal_sha256']}, file SHA {sha(PREP/'evidence/DIAGNOSTIC_PROPOSAL.json')}, authorization self SHA {auth['authorization_sha256']}, live binding self SHA {binding['binding_sha256']}다. 원 proposal science_authorized=false와 모든 승인 static identity를 변경하지 않았다. 최신 remote 5b95029d9473429bd934a8f525ebdc0b32e716ac를 확인했고 기존 verified local package를 재사용하여 input download0이었다.

| Query | calls/failures 전→후 | fresh last_error | physical/mapped finite | cached terms started/completed | L/R/S eval | L/R/S hits |
|---|---|---|---|---|---|---|
| Q272_cached | 0/0→1/1 | backend returned nonfinite enclosure | false/false | 2/1 | 1/1/2 | 0/0/0 |
| Q272_reference | 0/0→1/1 | backend returned nonfinite enclosure | false/false | 0/0 | 0/0/0 | 0/0/0 |
| Q000_cached | 0/0→1/1 | backend returned nonfinite enclosure | false/false | 2/1 | 1/1/2 | 0/0/0 |
| Q000_reference | 0/0→1/1 | backend returned nonfinite enclosure | false/false | 0/0 | 0/0/0 | 0/0/0 |

호출 전 모든 last_error는 빈 문자열, Contract/CacheStats는0이었다. reference CacheStats 0은 reference가 해당 cache recorder를 사용하지 않기 때문이며 reference 계산0을 뜻하지 않는다. 네 physical callback return과 log map return은 모두0이나, 원 fail 경로는 indeterminate output과 failures/last_error를 기록한다. 따라서 shell/native exit0만으로 성공한 enclosure를 주장하지 않는다. 물리 및 mapped 출력 Arb dump는 real/imag 각각 `0 -3 0 -1`이다. 정확한 log/physical t,u box와 margin, signed107 순서는 원 stdout/OBSERVATION 및 QUERY_COMPARISON에 모두 보존했다.

두 cached 호출은 terms_started2/completed1 및 spatial eval2를 관측했다. 고정 source에서 이 카운터는 term 처리 도중의 조기 refusal과 정합한다. generic finite guard는 여러 helper가 사용하는 `backend returned nonfinite enclosure`를 발생시키므로 이 네 관측만으로 특정 backend helper, cache 버그 또는 수학적 발산을 확정하지 않는다. 첫 callback의 fresh refusal을 실제로 확인했으나 구체 원인은 UNRESOLVED다. 추가 instrumentation이나 callback을 자동 실행하지 않았다.

원 blueprint/authorized_namespace.sh → diagnostic_adapter.py run을1회 사용했다. 원 live_gate가 새 실제 unit의 memory.max34359738368/cpu.max400000 100000, unit wall60초, 원6GiB 여유와 유효CPU{live['effective_CPU']}, private mount/cgroup/read-only ancestor view, fresh PID{inside['pid']}, UID0/capabilities0/NoNewPrivs1을 관측하고 소비 전에 통과했다. Host MemAvailable는 {live['host_MemAvailable']} bytes였다. 실제 dispatch는 single worker·순차4회다. inherited a.resources의 concurrency2는 원 gate의 자원 capacity 값이며 FD1 병렬 dispatch 수가 아니다. UID0를 별도 비root UID 검증으로 부르지 않는다. Loader/host identity는 원 run의 private preflight가 검사했다. 별도 post-run ldd는 바깥 root view의 readback으로 구분한다.

전체 blueprint wrapper 관측 wall은 {c.load(E/'EXECUTION_COMMAND_RETURN.json')['elapsed_seconds']:.6f}초였다. unit manager는 runtime1.052초, memory peak24.0MiB를 보고했다. Native PID는 237609,237610,237611,237612다. 짧은 native process는5ms /proc 샘플 사이에서 끝나 process snapshot이 없다. 실행은 각 원 CALL_STARTED/native stdout/RETURN 및 PID로 입증된다. 각 marker→RETURN 시간은 파일 event 구간으로 기록하며 launch/wait/validation을 포함하므로 exact native wall로 부르지 않는다. 누락된 exact per-native start/stop 및 /proc snapshot은 ABSENT_FILES에 이유를 적었다.

기존 보호 파일/링크 {len(preserved)}개는 bytes/SHA/mode/mtime/target 변화0이다. 성공 backend·primitive worker·sidecar는 재빌드0회다. 원 PREPARED, 실패 tree,24수락셀,consumed6셀 registry, B22 105/057 claim bytes/SHA/mtime/PID 문자열을 보존했다. claim PID를 현재 process 상태로 추정하지 않는다. accepted24/289, missing265 unbounded, epsilon_C/R=null, B22 OPEN_UNDETERMINED, scientific/production admission=false를 유지한다. 이번 nonfinite 관측을 새 accepted cell·적분 enclosure로 집계하지 않는다. 원 scienceDB·Bianchi/rei_bianchi·다른repo를 변경하지 않았다. R31AK frozen/z0.75holdout/B128B160consumed/B192reuse를 유지한다.

승인원문/AUTHORIZATION_RECORD, fresh outside observation, LIVE_BINDING/registry, 네 CALL_STARTED/stdout/stderr/OBSERVATION/RETURN, 최종원 RETURN, 정확한 Arb dump, PID·command·event timing·hash manifest를 패키지로 반환한다. 같은 branch additive/non-force publication과 Drive/Dropbox create-only ZIP/보고서/receipt의 실제 ACK/object/metadata는 detached DELIVERY_RECEIPT에 기록한다. 출력 verification tier ACK+metadata와 실제 restore를 구분하며 출력 RESTORE_VERIFIED=false다.
'''
 (E/'WORK_REPORT_KO.md').write_text(report)
 write(E/'SOURCE_DELTA.json',dict(original_sidecar_source_binary_adapter_host_and_backend_unchanged=True,original_proposal_unchanged=True,execution_coordinator_files=[ref(TASK/n) for n in ('preflight_authorization.py','invoke_original_blueprint_once.py','verify_and_report.py')],new_dispatcher=False,original_entrypoint_attempts=1,backend_worker_sidecar_rebuilds=0,scientific_parameter_changes=0))
 with (E/'COMMANDS.jsonl').open('a') as log:
  for row in commands:log.write(json.dumps(row)+'\n')
  log.write(json.dumps(dict(command=['python3','-B',str(Path(__file__))],exit_status=0,action='Read saved raw through original observation validator and verify preservation; no callback'))+'\n')
  log.write(json.dumps(dict(command=['/usr/bin/ldd',proposal['binary']['path']],exit_status=0,action='Post-run loader readback; no callback'))+'\n')
 print(json.dumps(result))
if __name__=='__main__':main()
