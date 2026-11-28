"""One host scalar/read-only suite and separate sidecar build; no full field."""
from support import *
from diagnostic_adapter import live_gate,preflight,unconsumed
import ast
SOURCE_NAMES=('support.py','observe.py','prepare_candidate.py','diagnostic.cpp','diagnostic_adapter.py','QUERIES.json','queries_generated.hpp','original_margin.inc','preparation_namespace.sh','authorized_namespace.sh')
def main():
 runtime_policy=c.load(FD1/'evidence/DIAGNOSTIC_PROPOSAL.json')['future_resource_policy'].copy()
 runtime_policy.update(unit='wu088-fd2-prep-v2.service',outside_observation_file=str(E/'FD2_PREP_OUTSIDE.json'),read_only_host_ancestor_view=str(R/'host_cgroup_view'))
 live=live_gate(dict(future_resource_policy=runtime_policy));write(E/'FRESH_PREPARATION_RUNTIME.json',dict(live=live,metadata_only_gate=True,full_candidate_field_callbacks=0,integrations=0,UID0_not_nonroot_validation=True))
 _,gate=a.driver(REPO).dependencies();backend=gate.verify_backend(BACKEND/'BACKEND_BUILD_PROVENANCE.json',BACKEND/'prefix')
 original=c.load(WORKER/'BUILD.json');a.validate_build(REPO,WORKER,original['manifest_sha256'])
 oldproposal=c.load(FD1/'evidence/DIAGNOSTIC_PROPOSAL.json');oldregistry=c.load(oldproposal['future_registry']);c.check_seal(oldregistry,'binding_sha256');assert c.load(Path(oldproposal['future_output_root'])/'RETURN.json')['scope_consumed']
 scalar_output=OLD/'fd2_prep_20261004_v1/scalar_tests'
 scalar=c.load(scalar_output/'FINAL_VERIFICATION.json');assert scalar['tests']==33 and scalar['failures']==0 and scalar['full_HH_field_callbacks']==scalar['integrations']==0 and scalar['source_sha256']==sha(REVIEW/'src/finite_m.hpp')
 write(E/'SCALAR_TEST_REUSE.json',dict(verified_once_on_this_host=ref(scalar_output/'FINAL_VERIFICATION.json'),commands=ref(scalar_output/'COMMANDS.json'),reexecution_count=0,source_unchanged=True,original_run_in_actual_private_cgroup_caps0=True))
 actual_test_compiler=Path('/usr/bin/g++').resolve();write(E/'HOST_SCALAR_TOOLCHAIN.json',dict(compiler=ref(actual_test_compiler),compiler_version=subprocess.check_output([str(actual_test_compiler),'--version'],text=True).splitlines()[0],test_flags=['-std=c++20','-O1','-fno-fast-math','-ffp-contract=off','-Wall','-Wextra','-Werror'],test_runner=ref(REVIEW/'run_tests.py'),sidecar_numeric_flags_separately_preserved=True))
 baseline=L/'gap_closure_20261001_g0_g6_v1/validated_callback';cache=CANDIDATE/'ncp64_acceleration_20261001_v1/native_cache';callback=CANDIDATE/'gap_closure_20261001_g0_g6_v1/validated_callback'
 candidate=[callback/'callback.cpp',callback/'callback.hpp',callback/'finite_m.hpp',cache/'cached_callback.cpp',cache/'cached_callback.hpp']
 inherited=[baseline/'assembly.cpp',baseline/'assembly.hpp',L/'wide_domain_20261001_v1/range_native_driver/log_map.hpp',L/'wide_domain_20261001_v1/range_native_driver/range_petras.hpp',WORKER/'frozen107_generated.hpp',WORKER/'build_identity.hpp']
 sources=[ref(R/n) for n in SOURCE_NAMES];digest=c.digest(dict(additive_sources=sources,candidate_include_closure=[ref(p) for p in candidate],inherited_numeric_files=[ref(p) for p in inherited]))
 (R/'diagnostic_identity.hpp').write_text('#pragma once\n#define FD2_CANDIDATE_SOURCE_SHA256 "'+digest+'"\n')
 out=R/'build';out.mkdir(exist_ok=False);binary=out/'fd2_candidate';compiler=original['compiler']['path'];assert sha(compiler)==original['compiler']['sha256']
 env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','LD_LIBRARY_PATH':str(BACKEND/'prefix/lib'),'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1'}
 compile_base=[compiler,*original['flags'],'-I'+str(R),'-I'+str(WORKER),'-I'+str(callback),'-I'+str(cache),'-I'+str(baseline),'-I'+str(L/'wide_domain_20261001_v1/range_native_driver'),'-I'+str(BACKEND/'prefix/include')]
 translation_units=[str(R/'diagnostic.cpp'),str(cache/'cached_callback.cpp'),str(baseline/'assembly.cpp')]
 assert run('candidate_dependency_closure',compile_base+['-MM',*translation_units],timeout=15,env=env)==0
 closure=(E/'candidate_dependency_closure.stdout.log').read_text()
 import re
 normalized={str(Path(t).resolve(strict=True)) for t in re.findall(r'/[^\s\\]+',closure)}
 assert str((callback/'callback.cpp').resolve()) in normalized and str((callback/'finite_m.hpp').resolve()) in normalized and str((baseline/'callback.cpp').resolve()) not in normalized
 write(E/'NORMALIZED_DEPENDENCY_CLOSURE.json',dict(paths=sorted(normalized),candidate_callback_proven=True,original_callback_TU_not_linked=True,raw_dependency_output_preserved=True))
 command=compile_base+translation_units+['-L'+str(BACKEND/'prefix/lib'),'-Wl,-rpath,'+str(BACKEND/'prefix/lib'),'-lflint','-lmpfr','-lgmp','-o',str(binary)]
 write(E/'CANDIDATE_BUILD_ATTEMPT.json',dict(command=command,attempts=1,candidate_source_sha256=digest,backend_original_worker_FD1_rebuilds=0,full_candidate_field_callbacks=0,integrations=0))
 assert run('candidate_compile_link',command,timeout=55,env=env)==0
 assert run('candidate_ldd',['/usr/bin/ldd',str(binary)],timeout=10,env=env)==0
 linkage=gate.verify_linkage((E/'candidate_ldd.stdout.log').read_text(),{n:x['binary_path'] for n,x in backend['libraries'].items()});assert linkage==original['linkage']
 assert run('candidate_dynamic_symbols',['/usr/bin/nm','-D',str(binary)],env=env)==0;assert 'acb_calc_integrate' not in (E/'candidate_dynamic_symbols.stdout.log').read_text()
 build=c.seal(dict(schema='WU088_FD2_CANDIDATE_FIELD_SIDECAR_BUILD_V1',binary=ref(binary),command=command,compiler=ref(compiler),flags=original['flags'],diagnostic_source_sha256=digest,candidate_source_sha256=digest,candidate_scalar_sha256=sha(callback/'finite_m.hpp'),source_files=sources,candidate_include_closure=[ref(p) for p in candidate],inherited_numeric_files=[ref(p) for p in inherited],identity_header=ref(R/'diagnostic_identity.hpp'),linkage=linkage,dependency_closure=ref(E/'candidate_dependency_closure.stdout.log'),backend_provenance=ref(BACKEND/'BACKEND_BUILD_PROVENANCE.json'),original_worker_build=ref(WORKER/'BUILD.json'),backend_original_worker_FD1_rebuilt=False,full_candidate_field_callbacks=0,integrations=0),'build_sha256');write(out/'BUILD.json',build)
 queries=c.load(R/'QUERIES.json');geometry={}
 for query in queries['queries']:
  qid=query['query_id'];assert run('candidate_geometry_'+qid,[str(binary),'--geometry',qid],env=env)==0
  g=c.load(E/('candidate_geometry_'+qid+'.stdout.log'));expected=oldproposal['geometry'][qid]
  for name in ('inner_log_box','outer_log_box','physical_t','physical_u','margin','a','b','ordered_terms'):assert g[name]==expected[name]
  assert g['HH_evaluations']==g['integrations']==0 and g['record'] is None and g['diagnostic_source_sha256']==digest;geometry[qid]=g
 write(E/'EXACT_GEOMETRY_PRESERVATION.json',dict(status='PASS',geometry=geometry,original_log_map_margin_signed107_and_boxes_preserved=True,metadata_descriptions=2,full_candidate_field_callbacks=0,integrations=0))
 # New saved-ball comparison seam only. No replay of FD1's 18 tests.
 checks=[]
 for name,args,expected_exit,overlap in [('same',['1 0 0 0','0 0 0 0','1 0 0 0','0 0 0 0'],0,True),('disjoint',['1 0 0 0','0 0 0 0','2 0 0 0','0 0 0 0'],0,False),('nonfinite',['0 -3 0 -1','0 0 0 0','1 0 0 0','0 0 0 0'],64,None)]:
  label='saved_ball_'+name;rc=run(label,[str(binary),'--compare-balls',*args],env=env);assert rc==expected_exit
  if overlap is not None:assert c.load(E/(label+'.stdout.log'))['overlap']==overlap
  checks.append(dict(name=name,exit_status=rc,expected_overlap=overlap,field_callbacks=0,integrations=0))
 write(E/'NEW_SAVED_OUTPUT_COMPARISON_CHECKS.json',dict(checks=checks,new_checks=3,not_counted_as_33_scalar_suite=True,old18_suite_rerun=False,synthetic_saved_ball_fixtures_only=True))
 h=a.host(REPO,OLD/'runtime_work/host');host=h.identity();inherited_refs=[ref(p) for p in inherited]+oldproposal['inherited_files']+[ref(Path(oldproposal['future_output_root'])/'RETURN.json'),ref(Path(oldproposal['future_output_root'])/'LIVE_BINDING.json'),ref(FD1/'evidence/DIAGNOSTIC_PROPOSAL.json'),ref(REVIEW/'RESULT.json'),ref(REVIEW/'DELIVERY_MANIFEST.json'),ref(REVIEW/'evidence/CANDIDATE_SOURCE_LINEAGE.json')]
 inherited_refs+=[ref(p) for p in candidate]
 for key in ('Q272_cached','Q272_reference','Q000_cached','Q000_reference'):inherited_refs.append(ref(Path(oldproposal['future_output_root'])/key/'OBSERVATION.json'))
 policy=oldproposal['future_resource_policy'].copy();policy.update(unit='wu088-fd2-candidate.service',read_only_host_ancestor_view=str(R/'host_cgroup_view'),outside_observation_file=str(E/'FD2_CANDIDATE_OUTSIDE.json'))
 proposal=c.seal(dict(schema='WU088_FD2_CANDIDATE_PROPOSAL_V1',status='READY_FOR_EXACT_FD2_CANDIDATE_AUTHORIZATION',science_authorized=False,full_candidate_field_callbacks=0,integrations=0,queries=queries,future_query_keys=oldproposal['future_query_keys'],source_files=sources+[ref(R/'diagnostic_identity.hpp')],inherited_files=inherited_refs,binary=ref(binary),build_file=ref(out/'BUILD.json'),build_self_sha256=build['build_sha256'],diagnostic_source_sha256=digest,candidate_source_sha256=digest,candidate_scalar_sha256=sha(callback/'finite_m.hpp'),candidate_domain=c.load(REVIEW/'RESULT.json')['candidate_domain'],geometry=geometry,parent_FD1_proposal_self_sha256=oldproposal['proposal_sha256'],parent_FD1_registry=ref(oldproposal['future_registry']),parent_FD1_scope_consumed=True,old_registry=oldproposal['old_registry'],old_six_cell_scope_consumed=True,new_candidate_scope_consumed=False,future_registry=str(OLD/'fd2_candidate_registry'/('scope_'+queries['query_scope_sha256']+'.json')),future_output_root=str(R/'candidate_run'),host_build_dir=str(OLD/'runtime_work/host'),host_identity=host,future_resource_policy=policy,native_commands=[[str(binary),'--hh-single',*key.split('_'),queries['query_scope_sha256']] for key in oldproposal['future_query_keys']],future_execution_blueprint=['systemd-run','--user','--unit=wu088-fd2-candidate','--wait','--pipe','--property=MemoryMax=34359738368','--property=CPUQuota=400%','--property=RuntimeMaxSec=60',str(R/'authorized_namespace.sh'),'EXACT_FD2_PROPOSAL_SELF_SHA256','LATER_EXPLICIT_FD2_AUTHORIZATION_RECORD_PATH','LATER_AUTHORIZATION_SELF_SHA256'],requires_separate_exact_human_authorization=True,authorization_kind='HUMAN_EXACT_FD2_CANDIDATE_AUTHORIZATION',requires_fresh_live_gate_and_loader_before_consumption=True,success_criteria=['Four fixed field observations with clean fresh finite physical/mapped outputs','Cached counters terms_started=terms_completed=107; reference source full-loop clean finite return witnesses107 ordered terms','Finite candidate cached/reference physical and mapped enclosures overlap; widths preserved','No old nonfinite FD1 overlap test and no cell or integral admission'],fresh_nonfinite_observation_policy='Preserve valid fresh observation and finish only remaining fixed comparisons through original sequential adapter behavior; never retry/add box/precision/queue',timeout_exit_or_binding_error_policy='Stop remaining dispatch and preserve partial results',read_only_output_comparison_mode='--compare-balls, original guarded host limits, zero field callbacks',actual_future_run_untested=True,accepted_cells=24,missing_cells_unbounded=265,epsilon_C=None,epsilon_R=None,B22='OPEN_UNDETERMINED',scientific_admission=False,production_admission=False,independent_scientific_review=False),'proposal_sha256')
 write(E/'FD2_CANDIDATE_PROPOSAL.json',proposal);preflight(proposal,proposal['proposal_sha256']);unconsumed(proposal)
 for name in SOURCE_NAMES:
  if name.endswith('.py'):ast.parse((R/name).read_text())
  elif name.endswith('.sh'):assert subprocess.run(['/bin/sh','-n',str(R/name)]).returncode==0
 write(E/'PREPARATION_RESULT.json',dict(status='READY_FOR_EXACT_FD2_CANDIDATE_AUTHORIZATION',proposal_self_sha256=proposal['proposal_sha256'],proposal_file=ref(E/'FD2_CANDIDATE_PROPOSAL.json'),query_scope_sha256=queries['query_scope_sha256'],candidate_source_sha256=digest,build_self_sha256=build['build_sha256'],binary=ref(binary),host_scalar_readonly_tests=33,failures=0,new_comparison_seam_checks=3,full_candidate_field_callbacks=0,integrations=0,scope_consumed=False))
 print(json.dumps(c.load(E/'PREPARATION_RESULT.json')))
if __name__=='__main__':
 try:main()
 except Exception as exc:
  import traceback;traceback.print_exc();write(E/'PREPARATION_FAILURE.json',dict(status='BLOCKED',error=str(exc),error_type=type(exc).__name__,no_auto_retry=True,full_candidate_field_callbacks=0,integrations=0));raise
