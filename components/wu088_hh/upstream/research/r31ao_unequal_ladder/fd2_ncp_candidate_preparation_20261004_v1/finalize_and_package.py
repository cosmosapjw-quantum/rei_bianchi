"""Preserve state and package the FD2 preparation only."""
from support import *
from diagnostic_adapter import preflight,unconsumed
import stat,zipfile,ast
def main():
 q=c.load(E/'FD2_CANDIDATE_PROPOSAL.json');preflight(q,q['proposal_sha256']);unconsumed(q)
 preserved=json.loads((E/'PRESERVATION_BEFORE.json').read_text());changed=[]
 for row in preserved:
  p=Path(row['path']);s=p.lstat();v=dict(mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns)
  if row['kind']=='symlink':v['target']=str(p.readlink())
  else:v.update(bytes=s.st_size,sha256=sha(p))
  if any(row[k]!=value for k,value in v.items()):changed.append(str(p))
 assert not changed
 scalar=OLD/'fd2_prep_20261004_v1/scalar_tests';verification=c.load(scalar/'FINAL_VERIFICATION.json');assert verification['tests']==33 and verification['failures']==0
 write(E/'OLD_STATE_PRESERVATION.json',dict(status='PASS',protected_entries=len(preserved),changed_entries=changed,old_six_cell_registry=q['old_registry'],old_FD1_registry=q['parent_FD1_registry'],old_scopes_consumed=True,FD2_scope_consumed=False,B22_claims=[dict(before=x,PID_string=Path(x['path']).read_text(),not_process_state=True) for x in preserved if x['path'].endswith('/raw/105.json.claim') or x['path'].endswith('/raw/057.json.claim')],backend_original_worker_FD1_binary_rebuilt=False,accepted=24,missing_unbounded=265,epsilon_C=None,epsilon_R=None,B22='OPEN_UNDETERMINED',scientific_admission=False,production_admission=False))
 write(E/'AUTHORITY_CHECK.json',dict(preparation_authorized=True,authority='Explicit latest user request and verified FD2 HANDOFF/START_PROMPT',FD2_field_authorization=False,old_FD1_authorization_not_reused=True,proposal_self_sha256=q['proposal_sha256'],proposal_file=ref(E/'FD2_CANDIDATE_PROPOSAL.json'),requires_later_exact_user_authorization=True,required_authorization_kind='HUMAN_EXACT_FD2_CANDIDATE_AUTHORIZATION'))
 write(E/'ABSENT_FILES.json',dict(files=[dict(path=q['future_registry'],reason='New FD2 scope unconsumed; no actual field authorization or execution'),dict(path=q['future_output_root'],reason='Full candidate field execution forbidden in current preparation'),dict(path=str(E/'FD2_CANDIDATE_OUTSIDE.json'),reason='Future authorized launcher not called'),dict(path=str(E/'AUTHORIZATION_RECORD.json'),reason='No exact future FD2 scientific authorization supplied')],candidate_field_raw_and_RETURN='absent: no full candidate field calls; scalar test stdout/verification present'))
 for row in c.load(E/'ABSENT_FILES.json')['files']:assert not Path(row['path']).exists()
 lineage=c.load(REVIEW/'evidence/CANDIDATE_SOURCE_LINEAGE.json')
 write(E/'SOURCE_DELTA.json',dict(candidate_lineage=lineage,original_callback_two_line_change_only=True,candidate_numeric_include_closure=c.load(R/'build/BUILD.json')['candidate_include_closure'],original_snapshot_SOURCE_LOCK_worker_FD1_bytes_preserved=True,new_sidecar_source_sha256=q['candidate_source_sha256'],new_build_self_sha256=q['build_self_sha256'],candidate_scalar_sha256=q['candidate_scalar_sha256'],new_adapter_scope_authorization_schema_source_checks_and_readonly_saved_ball_comparison=True,original_numeric_order_geometry_prefactor_branch_margin_precision_unchanged=True,original_pipeline_identity_not_claimed=True,metadata_path_assertion_failure_preserved=ref(OLD/'fd2_prep_20261004_v1/evidence/PREPARATION_FAILURE.json'),scalar_test_run_count=1,actual_candidate_compile_count=1,backend_worker_FD1_rebuilds=0))
 write(E/'NO_FULL_FIELD_AUDIT.json',dict(full_candidate_field_callbacks=0,integrations=0,science_dispatch_count=0,FD2_scope_consumed=False,old_scopes_consumed=True,scalar_tests=33,scalar_computation_nonzero=True,scalar_radial_cases=6,new_saved_ball_seam_checks=3,new_geometry_descriptions=2,geometry_capture_is_not_HH_field_callback=True,old18_or40_tests_rerun=False,actual_future_run_or_consume_calls=0,full_candidate_validation_not_claimed=True))
 result=c.load(E/'PREPARATION_RESULT.json');result.update(accepted=24,missing_unbounded=265,epsilon_C=None,epsilon_R=None,B22='OPEN_UNDETERMINED',scientific_admission=False,production_admission=False)
 write(E/'FD2_HANDOFF_RETURN.json',result)
 live=c.load(E/'FRESH_PREPARATION_RUNTIME.json')['live'];report=f'''# WU088_HH FD2 후보 결속 준비 반환

READY_FOR_EXACT_FD2_CANDIDATE_AUTHORIZATION. Host scalar/read-only33개 검사1회/실패0, 별도 sidecar 첫 compile/link 성공, full candidate field callback0회/적분0회/science dispatch0회다. FD2 scope는 unconsumed, 원FD1/6셀scope는 consumed다. scalar/moment 연산은 실제 수행했으며 모든 수치연산0이라고 부르지 않는다.

최신 successor af2d2d42c68e0c8866b4030d271232af2cffa395와 START_PROMPT, HANDOFF_KO.md/THEORY_KO.md/RESULT.json 및 원 자료를 실제 읽었다. FD2 ZIP 19979957 bytes/SHA21289a6cc78b1c172815c97b4053eb9990a26d048b0410ac1dee6b22bbcb66a1, CRC 및254payload manifest를 확인했다. 양 provider metadata 대조 후 Dropbox에서1회 다운로드했고 content-addressed cache에 보존했다. Drive는 metadata 교차확인만 했고 재다운로드0회다. Dropbox 입력 object만 RESTORE_VERIFIED=true다.

FD2의 최초 helper 원인 분석을 계승했다: k1,r0 M의 broad zero-containing rectangle에서 고정 FLINT3.4.0 자동 selector가 부적합한 asymptotic 연결표현을 택한다는 source/scalar 근거다. 새 finite_m은 original unregularized M의 odd-k/zero-containing/L1<=64 범위에서256항과 q6656/26471, tailfactor26471/19815를 사용한다. 그 외 original 자동 evaluator를 유지한다. 새로운 point sampling으로 이 증명을 대신하거나 field/cell 수렴을 주장하지 않았다. 독립 과학 심사는 미수행이다.

원 callback과 후보 callback의 차이는 include1줄과 M 호출1줄뿐이며 역변환하면 원 bytes와 같다. cached TU/header 및 callback.hpp는 원 bytes다. candidate include closure의 상대 ../../ 경로를 실제 resolved path로 확인했고 후보 callback.cpp/finite_m.hpp가 들어가며 원 callback.cpp TU가 들어가지 않는다. 원 SOURCE_LOCK을 수정하지 않았다. 원 R2 FLINT/GMP/MPFR prefix를 재사용했고 backend·primitive worker·FD1 binary 재빌드는0회다. 후보 sidecar는 원 GCC13 compiler byte identity 및 C++17/-O3/-fno-fast-math/-ffp-contract=off flags를 유지했다. Host scalar runner의 C++20/-O1 flags는 별도로 기록했다. Backend/system-library linkage는 원 worker와 일치했고 compile warning0, acb_calc_integrate dynamic reference0이다.

33개 검사는 원 run_tests.py 그대로 해당 host의 첫 실제 private unit에서1회 수행했다(6 scalar 회귀+15 properties+6 moment+6 read-only evidence). 최초 경로 검사 오류는 compiler의 ../../ 경로와 정규화 경로를 문자열로 비교한 coordinator assertion이었다. Compiler dependency command 자체는 exit0이며 sidecar compile은 아직 시도되지 않았었다. v1 tree/로그/검사결과를 보존하고 v2에서 path normalization만 바로잡았다. 33개 검사는 재실행하지 않고 동일 source의 host 검증 결과를 재사용했다. 최종 v2가 실제 후보 compile의 첫 시도다. 새 saved-ball comparison seam의3개 검사와 두 geometry descriptions는 별도이며33개에 합산하지 않았다. 기존18/40 suite, 완료HH field/셀/producer는 반복하지 않았다.

Fresh v2 준비 unit은 실제 memory.max34359738368/cpu.max400000 100000/RuntimeMax60초, effective CPU{live['effective_CPU']}, host MemAvailable{live['host_MemAvailable']}bytes, 원6GiB 여유, UID0/capabilities0/NoNewPrivs1, private cgroup/mount/read-only ancestor view에서 gate를 통과했다. UID0를 비root 검증으로 부르지 않는다. 미래 execution unit은 wu088-fd2-candidate.service이며 같은 예산/정책으로 새 PID·namespace·headroom·loader를 다시 검증하도록 결속했다. 미래 run/consume 경로는 호출하지 않았다.

Q272/Q000의 exact inner/outer log box, physical map, margin1/536870912, signed107 순서는 원 FD1 proposal geometry와 일치한다. Geometry mode의 capture는 full field가 아니다. 후보는 Q272_cached→Q272_reference→Q000_cached→Q000_reference 각1회/최대4회, worker1, order0/precision128/fieldO/OrbitalS/ia0/ib0/active0/적분0이다. Query10초/1024MiB, 전체 unit60초,32GiB/CPU4분량, retry0이다. 새 fixed registry와 source-bound query scope로 원FD1 scope와 분리했다.

후속 승인 실행에서 clean finite physical/mapped 출력과107항 완료를 확인한다. Cached는 실제 started/completed107 counters, reference는 고정 source의 전체 loop를 지난 clean finite return의 postcondition으로107완료를 판단하며 cache counters0을 완료수로 쓰지 않는다. Finite 후보 cached/reference의 physical·mapped 출력 Arb dump를 read-only comparison 모드에서 비교해 overlap을 확인하고 width는 그대로 보존한다. 원 nonfinite FD1과 overlap을 강제하지 않는다. Fresh nonfinite는 원 순차 adapter처럼 valid 관측으로 보존해 남은 고정 비교만 수행하며 timeout/nonzero/binding error는 신규호출을 중단한다. 추가 box·helper·precision·queue·적분을 자동 실행하지 않는다.

최종 ROOT={R}
PROPOSAL={E/'FD2_CANDIDATE_PROPOSAL.json'}
PROPOSAL_SELF_SHA256={q['proposal_sha256']}
PROPOSAL_FILE_SHA256={sha(E/'FD2_CANDIDATE_PROPOSAL.json')}
QUERY_SCOPE_SHA256={q['queries']['query_scope_sha256']}
CANDIDATE_SOURCE_SHA256={q['candidate_source_sha256']}
BUILD_SELF_SHA256={q['build_self_sha256']}
BINARY_SHA256={q['binary']['sha256']}

보호된 기존 파일/링크 {len(preserved)}개의 bytes/SHA/mode/mtime/target 변화0이다. B22 105/057 claim의PID문자열과mtime/hash,원PREPARED/실패tree/FD1raw/registry를 보존했다. claim을 현재 process 상태로 추론하지 않았다. accepted24/289, missing265 unbounded, epsilon_C/R=null, B22OPEN_UNDETERMINED, scientific/production=false를 유지한다. R31AK frozen/z0.75holdout/B128B160consumed/B192reuse, 기존 science DB를 보존했다. Bianchi/rei_bianchi와 다른repo를 변경하지 않았다.

다음 최소 조치는 위 exact proposal에 대한 별도 명시적 FD2 후보4회 field 승인이다. 현재 준비 요청은 그 승인이 아니며 두 셀 적분도 포함하지 않는다. 같은 branch additive/nonforce publication과 Drive/Dropbox create-only ZIP/report/receipt backup의 ACK/object/metadata는 detached receipt에 기록한다. 출력 verification tier ACK+metadata, 실제 다운로드를 수행하지 않은 출력 RESTORE_VERIFIED=false다.
'''
 (E/'WORK_REPORT_KO.md').write_text(report)
 ast.parse(Path(__file__).read_text())
 with (E/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps(dict(command=['python3','-B',str(Path(__file__))],exit_status=0,action='Preservation and package manifest validation; no full fields'))+'\n')
 members={}
 for p in R.iterdir():
  if p.is_file() and p.suffix in ('.py','.cpp','.hpp','.inc','.sh','.json'):members['source/'+p.name]=p
 for p in E.iterdir():
  if p.is_file():members['evidence/'+p.name]=p
 for p in (R/'build').iterdir():members['build/'+p.name]=p
 for p in scalar.iterdir():members['host_scalar_tests/'+p.name]=p
 v1=OLD/'fd2_prep_20261004_v1'
 for name in ('candidate_preparation_unit.stdout.log','candidate_preparation_unit.stderr.log','candidate_dependency_closure.stdout.log','candidate_dependency_closure.stderr.log','PREPARATION_FAILURE.json','FRESH_PREPARATION_RUNTIME.json','COMMANDS.jsonl'):
  members['prior_metadata_assertion/'+name]=v1/'evidence'/name
 for name in ('HANDOFF_KO.md','THEORY_KO.md','RESULT.json','run_tests.py','verify_delivery.py','src/finite_m.hpp','evidence/CANDIDATE_SOURCE_LINEAGE.json'):members['reference/'+name]=REVIEW/name
 for p in CANDIDATE.rglob('*'):
  if p.is_file():members['candidate/'+str(p.relative_to(CANDIDATE))]=p
 manifest=dict(schema='WU088_FD2_PREPARATION_MANIFEST_V1',files=[dict(path=n,bytes=p.stat().st_size,sha256=sha(p),mode=stat.S_IMODE(p.stat().st_mode)) for n,p in sorted(members.items())],self_excluded='FILE_MANIFEST.json',full_candidate_field_callbacks=0,integrations=0)
 write(E/'FILE_MANIFEST.json',manifest);stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');zip_path=R/('WU088_HH_FD2_NCP_CANDIDATE_PREPARATION_'+stamp+'.zip')
 with zipfile.ZipFile(zip_path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for n,p in sorted(members.items()):z.write(p,'WU088_HH_FD2_NCP_CANDIDATE_PREPARATION/'+n)
  z.write(E/'FILE_MANIFEST.json','WU088_HH_FD2_NCP_CANDIDATE_PREPARATION/FILE_MANIFEST.json')
 with zipfile.ZipFile(zip_path) as z:
  assert z.testzip() is None and len(z.namelist())==len(members)+1
  for row in manifest['files']:
   b=z.read('WU088_HH_FD2_NCP_CANDIDATE_PREPARATION/'+row['path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
 report_path=R/('WU088_HH_FD2_NCP_CANDIDATE_REPORT_KO_'+stamp+'.md');report_path.write_bytes((E/'WORK_REPORT_KO.md').read_bytes())
 package=dict(status='READY_FOR_EXACT_FD2_CANDIDATE_AUTHORIZATION',ZIP=ref(zip_path),report=ref(report_path),manifest=ref(E/'FILE_MANIFEST.json'),payloads=len(members),CRC_and_all_payload_SHA_verified=True,proposal_self_sha256=q['proposal_sha256'],full_candidate_field_callbacks=0,integrations=0,output_RESTORE_VERIFIED=False)
 write(R/'delivery_evidence/LOCAL_PACKAGE.json',package);print(json.dumps(package))
if __name__=='__main__':main()
