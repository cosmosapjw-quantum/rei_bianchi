"""Build FD1 sidecar and exercise synthetic/metadata refusals only."""
from support import *
from observe import observation
from diagnostic_adapter import QUERY_KEYS,preflight,unconsumed,exact_geometry,authorization_check
import copy,ast
SOURCE_NAMES=('diagnostic.cpp','diagnostic_adapter.py','support.py','observe.py','prepare_sidecar.py','queries_generated.hpp','original_margin.inc','QUERIES.json','preparation_namespace.sh','authorized_namespace.sh','ancestor_probe.py','ancestor_probe.sh')
def reject(name,fn,results):
 try:fn()
 except (ValueError,OSError,KeyError) as exc:results.append(dict(name=name,status='REJECTED_BEFORE_HH',reason=str(exc)))
 else:raise AssertionError('failed to reject '+name)
def main():
 inside=observation();write(E/'PREPARATION_RUNTIME.json',inside);admission=a.resources()
 assert admission['memory_max_bytes']==34359738368 and admission['cpu_quota']==400000
 status=dict(line.split(':',1) for line in inside['status'].splitlines() if ':' in line)
 assert all(status[k].strip()=='0000000000000000' for k in ('CapPrm','CapEff','CapBnd','CapAmb')) and status['NoNewPrivs'].strip()=='1'
 outside=c.load(E/'FD1_PREP_OUTSIDE.json');assert outside['ppid']==inside['pid'] and outside['namespace']['mnt']!=inside['namespace']['mnt'] and inside['membership']=='0::/\n'
 c.verify_snapshot(REPO)
 original=c.load(WORKER/'BUILD.json');a.validate_build(REPO,WORKER,original['manifest_sha256'])
 d=a.driver(REPO);frozen,gate=d.dependencies();input_bytes=Path(c.load(PILOT/'PREPARED.json')['input_npz']).read_bytes()
 record=frozen.decode_npz(input_bytes,expected_archive_sha256=c.INPUT_SHA,scope='FROZEN107_PINNED')
 generated=frozen.generate_cpp(record,source_archive_bytes=input_bytes)
 assert generated.encode()==(WORKER/'frozen107_generated.hpp').read_bytes() and sha(WORKER/'frozen107_generated.hpp')==original['generated_header_sha256']
 ordered=[]
 for index,coefficient in enumerate(record['fields']['C']['values']):
  if coefficient!='0':ordered.append([index//81,(index//9)%9,index%9,coefficient])
 assert len(ordered)==107
 numeric=[L/'ncp64_acceleration_20261001_v1/native_cache/cached_callback.cpp',L/'ncp64_acceleration_20261001_v1/native_cache/cached_callback.hpp',L/'gap_closure_20261001_g0_g6_v1/validated_callback/callback.cpp',L/'gap_closure_20261001_g0_g6_v1/validated_callback/callback.hpp',L/'gap_closure_20261001_g0_g6_v1/validated_callback/assembly.cpp',L/'gap_closure_20261001_g0_g6_v1/validated_callback/assembly.hpp',L/'wide_domain_20261001_v1/range_native_driver/log_map.hpp',L/'wide_domain_20261001_v1/range_native_driver/range_petras.hpp',L/'wide_domain_20261001_v1/range_native_driver/primitive_worker.cpp',WORKER/'frozen107_generated.hpp',WORKER/'build_identity.hpp']
 sources=[ref(R/n) for n in SOURCE_NAMES];digest=c.digest(dict(additive_sources=sources,inherited_numeric_files=[ref(p) for p in numeric]));(R/'diagnostic_identity.hpp').write_text('#pragma once\n#define FD1_DIAGNOSTIC_SOURCE_SHA256 "'+digest+'"\n')
 out=R/'build';out.mkdir(exist_ok=False);binary=out/'fd1_diagnostic';compiler=original['compiler']['path'];assert sha(compiler)==original['compiler']['sha256']
 command=[compiler,*original['flags'],'-I'+str(R),'-I'+str(WORKER),'-I'+str(L/'gap_closure_20261001_g0_g6_v1/validated_callback'),'-I'+str(L/'ncp64_acceleration_20261001_v1/native_cache'),'-I'+str(L/'wide_domain_20261001_v1/range_native_driver'),'-I'+str(BACKEND/'prefix/include'),str(R/'diagnostic.cpp'),str(numeric[0]),str(numeric[4]),'-L'+str(BACKEND/'prefix/lib'),'-Wl,-rpath,'+str(BACKEND/'prefix/lib'),'-lflint','-lmpfr','-lgmp','-o',str(binary)]
 write(E/'SIDECAR_BUILD_ATTEMPT.json',dict(command=command,source_sha256=digest,sidecar_only=True,backend_rebuilds=0,original_worker_rebuilds=0,HH_evaluations=0,integrations=0,automatic_retry=False))
 env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','LD_LIBRARY_PATH':str(BACKEND/'prefix/lib'),'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1'}
 assert run('sidecar_compile_link',command,timeout=180,env=env)==0
 assert run('sidecar_ldd',['/usr/bin/ldd',str(binary)],timeout=15,env=env)==0
 backend=gate.verify_backend(BACKEND/'BACKEND_BUILD_PROVENANCE.json',BACKEND/'prefix');linkage=gate.verify_linkage((E/'sidecar_ldd.stdout.log').read_text(),{n:x['binary_path'] for n,x in backend['libraries'].items()})
 assert linkage==original['linkage']
 assert run('sidecar_dynamic_symbols',['/usr/bin/nm','-D',str(binary)],env=env)==0
 assert 'acb_calc_integrate' not in (E/'sidecar_dynamic_symbols.stdout.log').read_text()
 build=c.seal(dict(schema='WU088_FD1_DIAGNOSTIC_SIDECAR_BUILD_V1',binary=ref(binary),command=command,flags=original['flags'],compiler=ref(compiler),compiler_version=subprocess.check_output([compiler,'--version'],text=True).splitlines()[0],diagnostic_source_sha256=digest,additive_source_files=sources,identity_header=ref(R/'diagnostic_identity.hpp'),inherited_numeric_files=[ref(p) for p in numeric],linkage=linkage,old_worker_build=ref(WORKER/'BUILD.json'),backend_provenance=ref(BACKEND/'BACKEND_BUILD_PROVENANCE.json'),HH_evaluations=0,integrations=0,backend_or_original_worker_rebuilt=False),'build_sha256');write(out/'BUILD.json',build)
 native_tests=[]
 cases=[('finite',0),('failure',0),('stale',64),('duplicate',64),('uncharged',64)]
 for mode,expected in cases:
  label='synthetic_recorder_'+mode;rc=run(label,[str(binary),'--synthetic',mode],timeout=10,env=env);assert rc==expected
  if rc==0:
   data=c.load(E/(label+'.stdout.log'));assert data['HH_evaluations']==0 and data['integrations']==0 and data['synthetic_callback_calls']==1
   r=data['record'];assert r['callback_invocations']==1 and r['before']['calls']==r['before']['failures']==0 and r['before']['last_error']=='' and not any(r['before']['cache'].values())
   if mode=='finite':assert r['physical_output_finite'] and not r['fresh_failure'] and r['after']['last_error']==''
   else:assert not r['physical_output_finite'] and r['fresh_failure'] and r['after']['last_error']=='FRESH_SYNTHETIC_REFUSAL' and r['after']['cache']['terms_started']==1
  else:assert 'FD1_REJECTED:' in (E/(label+'.stderr.log')).read_text()
  native_tests.append(dict(test='synthetic_'+mode,expected_exit=expected,actual_exit=rc,HH_evaluations=0,integrations=0))
 assert run('refuse_query_outside_scope',[str(binary),'--geometry','Q999'],env=env)==64
 assert run('refuse_native_scope_hash',[str(binary),'--hh-single','Q272','cached','0'*64],env=env)==64
 native_tests.extend([dict(test='outside_query',actual_exit=64,HH_evaluations=0),dict(test='wrong_native_scope_hash',actual_exit=64,HH_evaluations=0)])
 geometry={};queries=c.load(R/'QUERIES.json')
 for q in queries['queries']:
  assert run('geometry_'+q['query_id'],[str(binary),'--geometry',q['query_id']],timeout=10,env=env)==0
  g=c.load(E/('geometry_'+q['query_id']+'.stdout.log'));assert g['HH_evaluations']==0 and g['integrations']==0 and g['record'] is None and g['kind']=='GEOMETRY_ONLY_NO_FIELD_CALLBACK' and g['ordered_terms']==ordered
  assert g['margin']==str(d.real_domain_margin(__import__('fractions').Fraction(g['a']),__import__('fractions').Fraction(g['b']),q['physical_parent_window']))
  assert g['outer_log_box']==q['outer_log2_u_dump']
  expected='27 0 20000001 -1d' if q['cell_id']==272 else '-f -1 30000001 -1d';assert g['inner_log_box']==dict(real=expected,imag='0 0 0 0')
  assert g['diagnostic_source_sha256']==digest;geometry[q['query_id']]=g
 write(E/'QUERY_GEOMETRY_AND_INPUT_IDENTITY.json',dict(geometry=geometry,canonical_ordered_term_sha256=c.digest(ordered),terms=107,negative_terms=sum(__import__('fractions').Fraction(t[3])<0 for t in ordered),margin_independently_checked_by_original_driver=True,original_FLINT_first_box_constructor=True,outer_raw_sample_exact=True,HH_evaluations=0,integrations=0,geometry_capture_is_not_HH_callback=True))
 h=a.host(REPO,OLD/'runtime_work/host');h.identity()
 inherited=[ref(p) for p in numeric]+[ref(WORKER/'BUILD.json'),ref(WORKER/'primitive_worker'),ref(BACKEND/'BACKEND_BUILD_PROVENANCE.json'),ref(PILOT/'PREPARED.json'),ref(PILOT/'COVERAGE.json'),ref(PILOT/'RETURN.json'),ref(PILOT/'EXECUTION_BINDING.json'),ref(Path(c.load(PILOT/'PREPARED.json')['input_npz']))]
 for q in queries['queries']:
  inherited.extend([ref(PILOT/f"raw/{q['cell_id']:03d}.json"),ref(PILOT/f"raw/{q['cell_id']:03d}.json.stdout"),ref(PILOT/f"plans/{q['cell_id']:03d}.json")])
 registry=NODE/'run_registry/91f8f304f2c0aa8668a1d8bc18b1972348768772fa308d8b3c9483cc8c254a5b.json'
 proposal=c.seal(dict(schema='WU088_FD1_DIAGNOSTIC_PROPOSAL_V1',status='READY_FOR_EXACT_DIAGNOSTIC_AUTHORIZATION',detail_prompt_status='DIAGNOSTIC_READY_AWAITING_EXACT_AUTHORIZATION',science_authorized=False,HH_evaluations=0,integrations=0,queries=queries,future_query_keys=list(QUERY_KEYS),source_files=sources+[ref(R/'diagnostic_identity.hpp')],inherited_files=inherited,binary=ref(binary),build_file=ref(out/'BUILD.json'),build_self_sha256=build['build_sha256'],diagnostic_source_sha256=digest,geometry=geometry,old_registry=ref(registry),old_scope_consumed=True,old_scope_reused=False,diagnostic_scope_consumed=False,future_registry=str(OLD/'fd1_diagnostic_registry'/('scope_'+queries['query_scope_sha256']+'.json')),future_output_root=str(R/'diagnostic_run'),host_build_dir=str(OLD/'runtime_work/host'),host_identity=h.identity(),future_resource_policy=dict(unit='wu088-fd1-diagnostic.service',memory_max_bytes=34359738368,cpu_quota=400000,cpu_period=100000,reserve_bytes=6442450944,workers=1,query_wall_seconds=10,query_memory_mib=1024,total_wall_seconds=60,automatic_retry=False,max_field_callbacks=4,max_integrations=0,private_mount_cgroup_view=True,read_only_host_ancestor_view=str(R/'host_cgroup_view'),unit_runtime_max_seconds=60,capabilities_zero=True,NoNewPrivs=1,UID=0,nonroot_UID_validation=False,outside_observation_file=str(E/'FD1_DIAGNOSTIC_OUTSIDE.json')),native_commands=[[str(binary),'--hh-single',qid,impl,queries['query_scope_sha256']] for qid,impl in (x.split('_') for x in QUERY_KEYS)],future_execution_blueprint=['systemd-run','--user','--unit=wu088-fd1-diagnostic','--wait','--pipe','--property=MemoryMax=34359738368','--property=CPUQuota=400%','--property=RuntimeMaxSec=60',str(R/'authorized_namespace.sh'),'EXACT_PROPOSAL_SELF_SHA256','LATER_EXPLICIT_AUTHORIZATION_RECORD_PATH','LATER_AUTHORIZATION_SELF_SHA256'],requires_separate_human_authorization=True,requires_fresh_PID_namespace_cgroup_ancestor_headroom_and_loader_revalidation=True,accepted_cells=24,missing_cells_unbounded=265,epsilon_C=None,epsilon_R=None,B22='OPEN_UNDETERMINED',scientific_admission=False,production_admission=False),'proposal_sha256')
 write(E/'DIAGNOSTIC_PROPOSAL.json',proposal)
 preflight(proposal,proposal['proposal_sha256']);unconsumed(proposal)
 rejected=[]
 def changed(field,value):
  bad=copy.deepcopy(proposal);bad[field]=value;bad=c.seal({k:v for k,v in bad.items() if k!='proposal_sha256'},'proposal_sha256');return lambda:preflight(bad,bad['proposal_sha256'])
 bad=copy.deepcopy(queries);bad['queries'][0]['parent_raw_sha256']='0'*64;reject('parent_raw_changed',changed('queries',bad),rejected)
 bad=copy.deepcopy(queries);bad['queries'][0]['outer_log2_u_dump']['real']='-f -1 0 0';reject('outer_log_box_changed',changed('queries',bad),rejected)
 bad=copy.deepcopy(queries);bad['coefficient_semantics']='ABSOLUTE_COEFFICIENTS';reject('signed_coefficient_semantics_changed',changed('queries',bad),rejected)
 bad=copy.deepcopy(proposal['source_files']);bad[0]['sha256']='0'*64;reject('source_hash_changed',changed('source_files',bad),rejected)
 bad=copy.deepcopy(proposal['binary']);bad['sha256']='0'*64;reject('binary_hash_changed',changed('binary',bad),rejected)
 reject('missing_new_human_authorization',lambda:authorization_check(proposal,E/'ABSENT_AUTHORIZATION.json','0'*64),rejected)
 tests=R/'synthetic_tests';tests.mkdir();write(tests/'ALREADY_STARTED.json',dict(synthetic_fixture_only=True,HH_evaluations=0));bad=copy.deepcopy(proposal);bad['future_registry']=str(tests/'ALREADY_STARTED.json');reject('duplicate_campaign',lambda:unconsumed(bad),rejected)
 for field in ('inner_log_box','outer_log_box','margin','ordered_terms'):
  good=geometry['Q272'];bad=copy.deepcopy(good);bad[field]='CHANGED_METADATA_ONLY';reject('observed_'+field+'_changed',lambda bad=bad,good=good:exact_geometry(bad,good),rejected)
 for name in ('diagnostic_adapter.py','prepare_sidecar.py','support.py','observe.py'):ast.parse((R/name).read_text())
 for name in ('preparation_namespace.sh','authorized_namespace.sh'):assert subprocess.run(['/bin/sh','-n',str(R/name)]).returncode==0
 assert not Path(proposal['future_registry']).exists() and not Path(proposal['future_output_root']).exists() and not (E/'FD1_DIAGNOSTIC_OUTSIDE.json').exists()
 write(E/'SYNTHETIC_AND_REFUSAL_VERIFICATION.json',dict(status='PASS',native_recorder_and_refusal_checks=native_tests,metadata_rejections=rejected,unique_checks=len(native_tests)+len(rejected),geometry_descriptions=2,geometry_is_not_field_evaluation=True,new_HH_evaluations=0,new_integrations=0,actual_authorized_run_test_calls=0,old_validator_or_solver_replays=0,old40_suite_rerun=False,synth_fixtures_contain_no_frozen_input_evaluation=True))
 write(E/'PREPARATION_RESULT.json',dict(status='READY_FOR_EXACT_DIAGNOSTIC_AUTHORIZATION',proposal_self_sha256=proposal['proposal_sha256'],proposal_byte_identity=ref(E/'DIAGNOSTIC_PROPOSAL.json'),HH_evaluations=0,integrations=0,backend_or_worker_rebuilds=0,diagnostic_scope_consumed=False,old_scope_consumed=True,accepted_cells=24))
 print(json.dumps(dict(status='READY_FOR_EXACT_DIAGNOSTIC_AUTHORIZATION',proposal_self_sha256=proposal['proposal_sha256'],new_HH_evaluations=0,new_integrations=0)))
if __name__=='__main__':
 try:main()
 except Exception as exc:
  import traceback;traceback.print_exc();write(E/'PREPARATION_FAILURE.json',dict(status='BLOCKED',error=str(exc),error_type=type(exc).__name__,HH_evaluations=0,integrations=0,backend_or_worker_rebuilds=0,no_auto_retry=True));raise
