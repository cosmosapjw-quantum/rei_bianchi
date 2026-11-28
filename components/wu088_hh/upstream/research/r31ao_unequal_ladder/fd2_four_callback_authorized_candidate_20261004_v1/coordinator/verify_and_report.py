"""Verify saved FD2 results, not a callback or dispatch entrypoint."""
from pathlib import Path
import sys,json,stat,datetime,subprocess
from fractions import Fraction
TASK=Path(__file__).resolve().parent;E=TASK/'evidence';PREP=TASK.parent/'fd2_prep_20261004_v2'
sys.path.insert(0,str(PREP))
from support import c,ref,sha,write,OLD,PILOT,REPO
from diagnostic_adapter import preflight,authorization_check,validate_observation,verify_refs,QUERY_KEYS
def dyadic(m,e):
 return Fraction(m*(1<<e),1) if e>=0 else Fraction(m,1<<(-e))
def saved_width(dump):
 # Exact integer decoding of saved Arb serialization; no native evaluation.
 m,e,r,re=(int(x,16) for x in dump.split());mid=dyadic(m,e);rad=dyadic(r,re)
 return dict(original_dump=dump,midpoint_mantissa=m,midpoint_exp2=e,radius_mantissa=r,radius_exp2=re,component_width_mantissa=2*r,component_width_exp2=re,contains_zero=abs(mid)<=rad,interpretation='Exact dyadics from saved Arb dump; no enclosure modification')
def preservation(rows):
 changes=[]
 for row in rows:
  p=Path(row['path']);s=p.lstat();v=dict(mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns)
  if row['kind']=='symlink':v['target']=str(p.readlink())
  else:v.update(bytes=s.st_size,sha256=sha(p))
  if any(row[k]!=value for k,value in v.items()):changes.append(dict(path=str(p),differences={k:value for k,value in v.items() if row[k]!=value}))
 return changes
def main():
 proposal=c.load(PREP/'evidence/FD2_CANDIDATE_PROPOSAL.json');queries,build=preflight(proposal,proposal['proposal_sha256'])
 verify_refs(build['candidate_include_closure']);verify_refs(build['inherited_numeric_files']);verify_refs([build['identity_header'],build['compiler']])
 for q in queries['queries']:c.check_seal(c.load(PILOT/f"plans/{q['cell_id']:03d}.json"),'plan_sha256')
 auth=c.load(E/'AUTHORIZATION_RECORD.json');authorization_check(proposal,E/'AUTHORIZATION_RECORD.json',auth['authorization_sha256'])
 authority=c.load(E/'AUTHORITY_CHECK.json');assert authority['proposal_file']==ref(PREP/'evidence/FD2_CANDIDATE_PROPOSAL.json')
 root=Path(proposal['future_output_root']);registry=c.load(proposal['future_registry']);c.check_seal(registry,'binding_sha256')
 binding=c.load(root/'LIVE_BINDING.json');c.check_seal(binding,'binding_sha256');assert registry==binding and binding['proposal_sha256']==proposal['proposal_sha256'] and binding['authorization_sha256']==auth['authorization_sha256'] and binding['query_scope_sha256']==queries['query_scope_sha256']
 outside=c.load(PREP/'evidence/FD2_CANDIDATE_OUTSIDE.json');live=binding['live'];inside=live['observation']
 assert 'wu088-fd2-candidate.service' in outside['membership'] and outside['ppid']==inside['pid'] and inside['membership']=='0::/\n'
 assert all(outside['namespace'][k]!=inside['namespace'][k] for k in ('mnt','cgroup'))
 status=dict(line.split(':',1) for line in inside['status'].splitlines() if ':' in line)
 assert all(status[k].strip()=='0000000000000000' for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb')) and status['NoNewPrivs'].strip()=='1' and inside['uid']==0
 assert live['admission']['memory_max_bytes']==34359738368 and live['admission']['cpu_quota']==400000 and live['admission']['cpu_period']==100000 and live['effective_CPU']>=2 and live['host_MemAvailable']>=6442450944
 assert len(list(root.glob('*/CALL_STARTED.json')))==4
 returns=c.load(root/'RETURN.json');assert returns['scope_consumed'] is True and returns['integrations']==0 and returns['coverage_changes']==0 and len(returns['returns'])==4
 rows=[];commands=[];previous_return=None
 for index,key in enumerate(QUERY_KEYS):
  directory=root/key;qid,impl=key.split('_');query=next(q for q in queries['queries'] if q['query_id']==qid)
  marker=c.load(directory/'CALL_STARTED.json');ret=c.load(directory/'RETURN.json');raw=c.load(directory/'native.stdout');observation=c.load(directory/'OBSERVATION.json')
  assert raw==observation and marker['query_key']==key and marker['proposal_sha256']==proposal['proposal_sha256'] and marker['binding_sha256']==binding['binding_sha256']
  assert marker['command']==ret['command']==proposal['native_commands'][index] and marker['max_field_callbacks']==1 and marker['integrations']==0 and marker['no_retry'] is True
  assert ret==returns['returns'][index] and ret['exit_status']==0 and ret['timed_out'] is False and ret['status']=='OBSERVED_NOT_SCIENTIFIC_ADMISSION'
  assert ret['stdout']==ref(directory/'native.stdout') and ret['stderr']==ref(directory/'native.stderr')
  validate_observation(observation,query,impl,proposal['geometry'][qid],queries['query_scope_sha256'],build['diagnostic_source_sha256'])
  r=observation['record'];assert r['callback_invocations']==observation['HH_evaluations']==1 and observation['integrations']==0
  assert r['after']['calls']==1 and r['after']['failures']==0 and r['after']['last_error']=='' and r['fresh_failure'] is False and r['physical_output_finite'] and observation['mapped_output_finite']
  assert r['physical_callback_return']==0 and observation['log_map_return']==0
  if impl=='cached':assert r['after']['cache']['terms_started']==r['after']['cache']['terms_completed']==107
  started=(directory/'CALL_STARTED.json').stat().st_mtime_ns;ended=(directory/'RETURN.json').stat().st_mtime_ns
  assert ended>=started and (previous_return is None or started>=previous_return);previous_return=ended
  row=dict(query_key=key,native_pid=ret['native_pid'],exit_status=ret['exit_status'],timed_out=False,callback_invocations=1,integrations=0,before=r['before'],after=r['after'],fresh_failure=r['fresh_failure'],physical_callback_return=r['physical_callback_return'],physical_finite=r['physical_output_finite'],mapped_finite=observation['mapped_output_finite'],log_map_return=observation['log_map_return'],physical_output_dump=r['physical_output_dump'],mapped_output_dump=observation['mapped_output_dump'],widths={field:{component:saved_width(dump) for component,dump in balls.items()} for field,balls in [('physical',r['physical_output_dump']),('mapped',observation['mapped_output_dump'])]},inner_log_box=observation['inner_log_box'],outer_log_box=observation['outer_log_box'],physical_t=observation['physical_t'],physical_u=observation['physical_u'],margin=observation['margin'],marker_mtime_ns=started,return_mtime_ns=ended,marker_to_return_seconds=(ended-started)/1e9,timing_basis='Filesystem event window includes launch/wait/validation; not exact native wall time',raw=ref(directory/'native.stdout'))
  rows.append(row);commands.append(dict(command=ret['command'],exit_status=0,native_pid=ret['native_pid'],via_original_adapter=True,direct_shell_invocation=False,no_retry=True,HH_evaluations=1,integrations=0,marker_mtime_ns=started,return_mtime_ns=ended))
 assert len({x['native_pid'] for x in rows})==4
 comparison=c.load(root/'CANDIDATE_ENCLOSURE_COMPARISON.json');comp=comparison['comparisons']
 assert [(x['query_id'],x['field']) for x in comp]==[(q,f) for q in ('Q272','Q000') for f in ('physical','mapped')]
 for item in comp:
  left=next(x for x in rows if x['query_key']==item['query_id']+'_cached');right=next(x for x in rows if x['query_key']==item['query_id']+'_reference');field=item['field']+'_output_dump';lb=left[field];rb=right[field]
  assert item['command']==[proposal['binary']['path'],'--compare-balls',lb['real'],lb['imag'],rb['real'],rb['imag']]
  assert item['exit_status']==0 and item['HH_evaluations']==item['integrations']==0
  raw=c.load(root/('comparison_'+item['query_id']+'_'+item['field'])/'stdout')
  assert raw==item['result'] and raw['overlap'] is True and raw['HH_evaluations']==raw['integrations']==0
  assert left[field]==right[field] and raw['left_contains_right'] and raw['right_contains_left']
  commands.append(dict(**item,via_original_adapter=True,direct_shell_invocation=False,no_retry=True))
 assert returns['candidate_field_finite_and_107_complete_and_overlap'] is True and returns['comparison_count']==4
 reference=next(x['path'] for x in build['candidate_include_closure'] if x['path'].endswith('validated_callback/callback.cpp'))
 src=Path(reference).read_text();assert 'for (const auto &term:terms)' in src and 'finite(sum); acb_set(out,sum.v); return 0;' in src
 reference_basis=dict(source=ref(reference),terms_each=107,basis='Pinned full ordered loop over preserved107 terms and clean finite return; reference cache counters are not instrumentation of loop completion',independent_scientific_review=False)
 preserved=json.loads((E/'PRESERVATION_BEFORE.json').read_text());changes=preservation(preserved);assert not changes
 claims=[dict(before=x,PID_string=Path(x['path']).read_text(),PID_is_not_running_process_assertion=True) for x in preserved if x['path'].endswith('/raw/105.json.claim') or x['path'].endswith('/raw/057.json.claim')]
 write(E/'OLD_STATE_PRESERVATION.json',dict(status='PASS',protected_entries=len(preserved),changed_entries=changes,B22_claims=claims,claim_process_or_race_cause_inferred=False,old_registry=proposal['old_registry'],parent_FD1_registry=proposal['parent_FD1_registry'],old_scopes_consumed=True,FD2_scope_consumed=True,proposal_file=ref(PREP/'evidence/FD2_CANDIDATE_PROPOSAL.json'),accepted=24,missing_unbounded=265,epsilon_C=None,epsilon_R=None,B22='OPEN_UNDETERMINED',scientific_admission=False,production_admission=False,backend_worker_sidecar_rebuilds=0,other_repositories_modified=False))
 ldd=subprocess.run(['/usr/bin/ldd',proposal['binary']['path']],env={'PATH':'/usr/bin:/bin','LD_LIBRARY_PATH':str(OLD/'prep_r2/backend/prefix/lib')},capture_output=True,text=True,check=True)
 (E/'post_run_loader.stdout.log').write_text(ldd.stdout);(E/'post_run_loader.stderr.log').write_text(ldd.stderr)
 write(E/'LIVE_REVALIDATION.json',dict(status='PASS',binding_file=ref(root/'LIVE_BINDING.json'),binding_self_sha256=binding['binding_sha256'],outside_observation=ref(PREP/'evidence/FD2_CANDIDATE_OUTSIDE.json'),fresh_PID=inside['pid'],fresh_namespaces=inside['namespace'],actual_private_live=binding['live'],live_loader_and_host_identity_checked_by_original_run_before_consumption=True,original_run_preflight=ref(PREP/'diagnostic_adapter.py'),post_run_loader_observation=ref(E/'post_run_loader.stdout.log'),post_run_loader_is_outside_root_view=True,UID=0,nonroot_UID_validation=False,dispatch_workers=1,original_resource_admission_capacity_concurrency=live['admission']['concurrency'],sequential_callback_order=list(QUERY_KEYS)))
 observed=c.load(E/'NATIVE_PROCESS_OBSERVATIONS.json')['processes'];observed_pids={x['pid'] for x in observed};absent=[]
 for row in rows+comp:
  if row['native_pid'] not in observed_pids:absent.append(dict(item='sampled /proc metadata for native PID '+str(row['native_pid']),reason='No matching sample was captured. Requested5ms delay plus /proc scan is not exact5ms period. Short-lived execution is established by original adapter PID, saved raw and RETURN/comparison; exact per-native timing is not instrumented.'))
 for item in comp:absent.append(dict(item='CALL_STARTED/individual RETURN/exact timing for comparison PID '+str(item['native_pid']),reason='Original read-only comparison path records PID/command/exit in aggregate comparison JSON and stdout/stderr, but does not emit these individual files/timestamps. No reconstruction as measured data.'))
 write(E/'ABSENT_FILES.json',dict(absent=absent,final_RETURN_present=True,all_four_OBSERVATION_and_CALL_STARTED_present=True,all_four_comparison_stdout_stderr_present=True,missing_data_not_replaced_with_zero=True,execution_status_unknown=False))
 write(E/'RAW_OBSERVATION_AND_BINDING_VERIFICATION.json',dict(status='PASS',original_observation_validator_used=True,validator_only_not_HH_rerun=True,queries=rows,total_field_callbacks=4,total_integrations=0,sequential_single_worker=True,exact_input_geometry_margin_signed107_precision_preserved=True,native_exit_statuses=[0]*4,scope_consumed=True,all_native_outputs_bound=True))
 write(E/'QUERY_COMPARISON.json',dict(status='FOUR_FINITE_CANDIDATE_FIELDS_AND_FOUR_SAVED_ENCLOSURE_OVERLAPS',rows=rows,comparisons=comp,cached_terms_started_and_completed=[107,107],reference_basis=reference_basis,physical_and_mapped_dumps_byte_equal_for_each_pair=True,widths_preserved=True,no_old_FD1_nonfinite_overlap_test=True,integrations=0,coverage_changes=0,accuracy_or_cell_admission=False))
 result=dict(status='FD2_CANDIDATE_FIELD_FINITE_AND_CONSISTENT_AWAITING_REVIEW',execution_status=returns['status'],execution_completed=True,valid_observations=4,field_callbacks=4,read_only_saved_ball_comparisons=4,integrations=0,scope_consumed=True,automatic_retry=False,candidate_field_finite_and_107_complete_and_overlap=True,authorization_self_sha256=auth['authorization_sha256'],proposal_self_sha256=proposal['proposal_sha256'],query_scope_sha256=queries['query_scope_sha256'],live_binding_self_sha256=binding['binding_sha256'],accepted=24,missing_unbounded=265,epsilon_C=None,epsilon_R=None,B22='OPEN_UNDETERMINED',scientific_admission=False,production_admission=False,integral_convergence_tested=False,accuracy_certified=False,additional_science_authorized=False)
 write(E/'FD2_HANDOFF_RETURN.json',result)
 table='\n'.join('| '+x['query_key']+' | 0/0 → 1/0 | empty | true/true | '+('107/107' if x['query_key'].endswith('_cached') else 'reference full loop')+' | '+str(x['native_pid'])+' |' for x in rows)
 widths='\n'.join('| '+x['query_key']+' | '+field+' | '+component+' | '+str(v['radius_mantissa'])+' × 2^('+str(v['radius_exp2'])+') | '+str(v['contains_zero'])+' |' for x in rows if x['query_key'].endswith('_cached') for field,balls in x['widths'].items() for component,v in balls.items())
 wrapper=c.load(E/'EXECUTION_COMMAND_RETURN.json')
 report=f'''# WU088_HH FD2 고정 후보 callback 반환

상태: {result['status']}. 원 최종 RETURN의 candidate_field_finite_and_107_complete_and_overlap=true를 각 raw/OBSERVATION, 107항 카운터, 원 reference source 전체 loop 및 저장 출력 비교로 검증했다. 네 field callback을 승인 순서로 각1회 실행했고 저장 구간 비교4회는 field0회 경로였다. 적분0회, retry0회이며 FD2 scope는 영구 소비됐다.

| Query | calls/failures 전→후 | fresh last_error | physical/mapped finite | terms 완료 근거 | native PID |
|---|---|---|---|---|---|
{table}

호출 전 Contract/CacheStats/last_error는 모두 fresh0/empty다. 호출 후 calls1/failures0, last_error empty, fresh_failure=false, physical callback/log map return0이다. cached 두 호출은 terms_started=terms_completed=107, L/R/S requests107/107/107, evaluations8/8/9, hits99/99/98이다. Reference CacheStats는 미사용0이며 0항 계산을 뜻하지 않는다. 원 source의 전체107 ordered-term loop와 clean finite return을 완료 근거로 기록했다.

Q272와 Q000 각각 cached/reference physical 및 mapped 구간 overlap을 원 --compare-balls로 확인했다. 네 비교 모두 overlap=true 및 양방향 contains=true이며 같은 쌍의 원 Arb dump가 byte 동일하다. 원 nonfinite FD1과 overlap을 강제하지 않았다. 모든 원 dump/box/log map/margin/signed107을 stdout/OBSERVATION 및 QUERY_COMPARISON에 보존했다.

유한성·구간 일관성을 확인했으나 구간 폭은 크다. 아래 수치는 저장 dump의 정확한 dyadic 반경이고 전체 component 폭은 반경의2배다. cached/reference 쌍의 폭은 동일하며 모든 component가0을 포함한다. 반경을 축소하거나 midpoint로 대체하지 않았다.

| Query | 출력 | component | 정확한 반경 | 0 포함 |
|---|---|---|---|---|
{widths}

관측 성공, 후보 field 유한성, 동일 입력의 cached/reference 구간 일관성과 적분 수렴은 서로 다른 판정이다. 이 고정 box 결과만으로 정확도, cell enclosure, 적분 수렴, 전체 도메인 또는 후보 promotion을 승인하지 않는다. 별도 독립 결정 review도 이번 반환으로 만들어지지 않는다.

최신 remote 및 preparation commit은6c4c85eef33ef4fe733716a76523476e4aab7eef였다. 승인 사용자 원문 UTF-8 {auth['user_message']['bytes']} bytes/SHA {auth['user_message']['sha256']}를 보존했다. AUTHORIZATION_RECORD self SHA {auth['authorization_sha256']}, proposal self SHA {proposal['proposal_sha256']}, file SHA {sha(PREP/'evidence/FD2_CANDIDATE_PROPOSAL.json')}, query scope {queries['query_scope_sha256']}, build self {build['build_sha256']}, candidate source {build['diagnostic_source_sha256']}, binary SHA {proposal['binary']['sha256']}다. 원 proposal science_authorized=false와 self-hash는 변경하지 않았다. 원 serializer/validator와 별도 byte identity를 대조했다. 기존 verified preparation ZIP을 재사용했고 양 provider metadata를 조회했으며 input download0이었다.

승인 blueprint의 마지막 세 인자만 교체하여 authorized_namespace.sh → diagnostic_adapter.py run을1회 호출했다. 새 unit의 실제 finite memory.max34359738368, cpu.max400000 100000, RuntimeMaxSec60, 원6GiB headroom 및 effective_CPU{live['effective_CPU']}를 원 live_gate가 소비 전에 관측했다. 새 private PID{inside['pid']}/mount·cgroup namespace/read-only ancestor view, UID0/capabilities0/NoNewPrivs1, loader/backend/system-library/host identity를 LIVE_BINDING에 결속했다. UID0를 비root 검증으로 부르지 않는다. live host MemAvailable={live['host_MemAvailable']} bytes, affinity count={live['admission']['affinity_count']}다. 원 capacity concurrency2와 이번 workers1 순차 dispatch를 구분한다. 각 query wall10초/memory1024MiB 및 원 host 제한, 전체 unit wall60초를 유지했다. 바깥 post-run ldd와 원 private preflight loader 검증은 구분한다.

원 blueprint wrapper wall={wrapper['elapsed_seconds']:.9f}초, manager Service runtime1.229초/CPU1.108초/peak23.8M/swap0B로 기록됐다. callback PID246264/246265/246267/246268, read-only comparison PID246269/246270/246271/246272다. /proc observer는 요청 delay5ms에 directory scan 시간이 추가되므로 exact5ms 주기로 부르지 않는다. 미관측 /proc 및 원 adapter가 기록하지 않은 exact native timing/개별 comparison marker는 ABSENT_FILES에 사유를 기록했다. callback marker→RETURN 시간은 launch/wait/validation을 포함한 파일 event 구간이다.

준비/33개 scalar suite/backend/primitive worker/FD1·FD2 sidecar 재빌드0회다. 증거 coordinator의 첫 사전 검사는 package 내 과거 FD1 marker를 광범위 검색하여 중단했으며 callback0/scope 미소비였다. marker proposal/scope를 대조해 archived consumed FD1 증거로 분류한 뒤 사전 검사를 완료했다. 실패 기록을 보존했고 원 adapter/source/proposal을 수정하거나 실행을 재시도하지 않았다. Provider metadata 직렬화의 첫 NameError도 science0인 coordinator 오류로 별도 보존했다.

기존 보호 파일/링크 {len(preserved)}개는 bytes/SHA/mode/mtime/target 변화0이다. 원 PREPARED/실패tree/DB/수락24셀/소비6셀·FD1 registry/원 backend·worker·FD1 binary, B22 105/057 claim bytes/SHA/mtime/PID 문자열을 보존했다. PID 문자열로 process/race 원인을 확정하지 않는다. accepted24/289, missing265 unbounded, epsilon_C/R=null, B22 OPEN_UNDETERMINED, scientific/production admission=false를 유지한다. 미계산 기여를0으로 놓지 않았으며 새 수락셀을 추가하지 않았다. R31AK frozen/z0.75holdout/B128B160consumed/B192reuse를 유지하고 Bianchi/rei_bianchi/다른repo를 변경하지 않았다.

승인 원문/봉인 기록, fresh outside/LIVE_BINDING/registry, 네 CALL_STARTED/stdout/stderr/OBSERVATION/RETURN, 네 비교 stdout/stderr/aggregate comparison, 최종원 RETURN, 실제 command/exit/PID/timing/hash manifest를 반환한다. 같은 branch additive/non-force publication과 Drive/Dropbox create-only ZIP/보고서/receipt의 ACK/object/metadata는 detached receipt로 기록한다. ACK+metadata와 실제 restore를 구분하며 출력 RESTORE_VERIFIED=false다. 이번 고정 후보 결과 뒤 추가 query·적분·재실행을 수행하지 않는다.
'''
 (E/'WORK_REPORT_KO.md').write_text(report)
 write(E/'SOURCE_DELTA.json',dict(original_candidate_source_binary_adapter_host_backend_and_proposal_unchanged=True,execution_coordinator_files=[ref(TASK/n) for n in ('preflight_authorization.py','invoke_original_blueprint_once.py','verify_and_report.py')],new_dispatcher=False,original_entrypoint_attempts=1,backend_worker_sidecar_rebuilds=0,scalar_suite_reruns=0,scientific_parameter_changes=0))
 with (E/'COMMANDS.jsonl').open('a') as log:
  for row in commands:log.write(json.dumps(row)+'\n')
  log.write(json.dumps(dict(command=['python3','-B',str(Path(__file__))],exit_status=0,action='Read saved outputs through original validator, verify107 completion/overlap and old preservation; field0'))+'\n')
  log.write(json.dumps(dict(command=['/usr/bin/ldd',proposal['binary']['path']],exit_status=0,action='Post-run outside loader readback; field0'))+'\n')
 print(json.dumps(result))
if __name__=='__main__':main()
