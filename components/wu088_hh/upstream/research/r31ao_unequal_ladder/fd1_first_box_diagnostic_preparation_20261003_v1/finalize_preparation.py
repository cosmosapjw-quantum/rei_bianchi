"""Seal preparation evidence; no scientific callbacks or integrations."""
from support import *
import stat,zipfile,ast

def main():
 proposal=c.load(E/'DIAGNOSTIC_PROPOSAL.json');c.check_seal(proposal,'proposal_sha256')
 from diagnostic_adapter import preflight,unconsumed
 preflight(proposal,proposal['proposal_sha256']);unconsumed(proposal)
 preserved=json.loads((E/'PRESERVATION_BEFORE.json').read_text());changes=[]
 for row in preserved:
  p=Path(row['path'])
  if not p.exists() and not p.is_symlink():changes.append(dict(path=str(p),reason='absent'));continue
  s=p.lstat();actual=dict(mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns)
  if row['kind']=='symlink':actual.update(target=str(p.readlink()))
  else:actual.update(bytes=s.st_size,sha256=sha(p))
  for k,v in actual.items():
   if row[k]!=v:changes.append(dict(path=str(p),field=k,before=row[k],after=v))
 assert not changes,changes[:10]
 claims=[x for x in preserved if x['path'].endswith('.claim')]
 write(E/'OLD_SCOPE_AND_FILE_PRESERVATION.json',dict(status='PASS',protected_entries=len(preserved),changed_entries=changes,prior_failed_backend_R1_R2_and_FD1_v1_v2_preserved=True,byte_mode_mtime_and_symlink_preservation=True,old_registry=proposal['old_registry'],old_scope_consumed=True,old_scope_reused=False,diagnostic_scope_consumed=False,claims=claims,claim_process_or_race_cause_inferred=False,accepted=24,total=289,missing_unbounded=265,epsilon_C=None,epsilon_R=None,B22='OPEN_UNDETERMINED',scientific_admission=False,production_admission=False))
 checks=c.load(E/'SYNTHETIC_AND_REFUSAL_VERIFICATION.json');live=c.load(E/'LIVE_POLICY_PROBE.json')
 assert checks['unique_checks']==18 and checks['new_HH_evaluations']==checks['new_integrations']==0 and live['status']=='PASS'
 for name in ('live_gate_probe.py','finalize_preparation.py'):ast.parse((R/name).read_text())
 assert subprocess.run(['/bin/sh','-n',str(R/'live_gate_probe.sh')]).returncode==0
 write(E/'SOURCE_DELTA.json',dict(kind='ADDITIVE_DIAGNOSTIC_SIDECAR_AND_ORCHESTRATION',diagnostic_source_sha256=proposal['diagnostic_source_sha256'],source_files=proposal['source_files'],coordinator_only_files=[ref(R/n) for n in ('live_gate_probe.py','live_gate_probe.sh','finalize_preparation.py')],original_pipeline_identity_claimed=False,original_numeric_sources_and_flags_unchanged=True,backend_rebuilds=0,original_worker_rebuilds=0,integrator_translation_unit_linked=False,details=['Only first-box arithmetic copied from pinned FLINT quad_simple; no f/integration invoked during preparation.','Original log2 map, original margin block and original cached/reference numerical source are inherited without mutation.','Private read-only host ancestor mount replaces inaccessible /proc/1/root reads; fresh outside-to-inside PID/namespace lineage replaces inaccessible capabilities0 /proc/1/ns/mnt read.','Future unit wall bound RuntimeMaxSec=60 is part of the proposal; per-query limits are 10 seconds and 1024MiB.','One durable future diagnostic registry is anchored outside FD1 workspace copies.']))
 write(E/'AUTHORITY_CHECK.json',dict(preparation_authorized=True,authority='Latest explicit user preparation message and verified detailed prompt',detailed_prompt=ref(Path(c.load(E/'CLOUD_INTAKE.json')['artifacts'][0]['local']['path'])),four_HH_callbacks_authorized=False,old_six_cell_authorization_not_reused=True,old_scope_consumed=True,future_scope_consumed=False,future_proposal_self_sha256=proposal['proposal_sha256'],future_proposal_file=ref(E/'DIAGNOSTIC_PROPOSAL.json'),minimum_next_action='Separate later explicit human authorization bound to this exact proposal, four fixed callback keys, zero integration and resource policy; then fresh live revalidation.'))
 write(E/'NO_HH_EVALUATION_AUDIT.json',dict(HH_evaluations=0,integrations=0,science_dispatch_count=0,old_runtime_run_calls=0,future_run_authorized_calls=0,future_consume_calls=0,new_diagnostic_registry_absent=True,new_diagnostic_output_absent=True,geometry_descriptions=2,geometry_capture_is_not_field_callback=True,synthetic_recorder_calls_are_not_HH=True,wrong_native_scope_command_refused_before_loading_HH=True,command_log=ref(E/'COMMANDS.jsonl'),old40_contract_suite_rerun=False,old_review_queue_synthetic_experiment_rerun=False,unique_current_checks=18,prior_FD1_checks_not_added_to_current_count=True))
 absent=[dict(path=proposal['future_registry'],reason='Diagnostic scope unconsumed; no authorization and no dispatch'),dict(path=proposal['future_output_root'],reason='Future diagnostic not executed'),dict(path=str(E/'FD1_DIAGNOSTIC_OUTSIDE.json'),reason='Future authorized launcher not called'),dict(path=str(E/'AUTHORIZATION_RECORD.json'),reason='No later exact four-callback scientific authorization supplied')]
 assert all(not Path(x['path']).exists() for x in absent)
 write(E/'ABSENT_FILES.json',dict(files=absent,actual_HH_observations='absent: prohibited in this preparation stage',future_RUN_STARTED_RETURN_and_raw='absent: diagnostic not started'))
 write(E/'COMPILER_DIAGNOSTICS.json',dict(exit_status=0,warning_count=0,stderr=ref(E/'sidecar_compile_link.stderr.log'),compiler=proposal['build_file'],original_flags_preserved=True))
 write(E/'STAGE_LEDGER.json',dict(input_retrieval='VERIFIED',review_manifest='165_PAYLOADS_VERIFIED',source_and_consumed_pilot='PRESERVED',live_cgroup_ancestor_caps_and_headroom='PASS',sidecar_build_and_loader='PASS',current_synthetic_and_refusal_checks=18,proposal='SEALED',publication='PENDING_EXTERNAL_RECEIPT',dual_backup='PENDING_EXTERNAL_RECEIPT',HH_evaluations=0,integrations=0))
 result=dict(status='READY_FOR_EXACT_DIAGNOSTIC_AUTHORIZATION',detail_prompt_status='DIAGNOSTIC_READY_AWAITING_EXACT_AUTHORIZATION',proposal=ref(E/'DIAGNOSTIC_PROPOSAL.json'),proposal_self_sha256=proposal['proposal_sha256'],query_scope_sha256=proposal['queries']['query_scope_sha256'],sidecar_source_sha256=proposal['diagnostic_source_sha256'],sidecar_build_self_sha256=proposal['build_self_sha256'],HH_evaluations=0,integrations=0,science_dispatch_count=0,scope_consumed=False,original_six_cell_scope_consumed=True,accepted=24,missing_unbounded=265,epsilon_C=None,epsilon_R=None,B22='OPEN_UNDETERMINED',scientific_admission=False,production_admission=False,actual_future_execution_untested=True,requires_separate_exact_human_authorization=True)
 write(E/'FD1_HANDOFF_RETURN.json',result)
 report=f'''# WU088_HH FD1 첫 box 진단 준비 반환

상태: READY_FOR_EXACT_DIAGNOSTIC_AUTHORIZATION. HH 평가 0회, 적분 0회, science dispatch 0회. 기존 수락 24/289와 누락 265 unbounded를 유지했다. epsilon_C/R=null, B22=OPEN_UNDETERMINED, scientific/production admission=false다. 최초 HH callback의 nonfinite 원인은 아직 관측하지 않았다.

원격 successor {HEAD}의 START_PROMPT와 지정 상세 prompt를 실제로 읽었다. 상세 prompt 7884 bytes/SHA256 23d414ceba6555eadc5f340279679c318962cf9c60685b8ca59214cc1cc827fa, 검토 ZIP 5255001 bytes/SHA256 4f3673e48c97663101cb8cd644bc7c7e889727baa383d58305c2a4c246485471를 확인했다. 양 provider metadata를 대조하고 Dropbox에서 artifact당 한 번 다운로드했다. 검토 ZIP 165 payload와 CRC/manifest를 검증했다. 원 pilot ZIP은 기존 검증된 local bytes를 재사용했다. 사용자 재업로드와 provider 중복 다운로드는 없었다.

최종 workspace는 {R}다. 원 numeric source, signed ordered107, precision128, frozen input/geometry/margin과 기존 성공 backend/worker/compiler flags를 보존하고 별도 sidecar만 compile/link했다. FLINT3.4.0/GMP/MPFR 및 system-library linkage는 기존 worker와 일치한다. 적분 translation unit은 연결하지 않았고 dynamic symbols에 acb_calc_integrate 참조가 없다. compiler exit0, 경고0이다.

Q272와 Q000의 outer arb dump는 원 failure_samples[0]의 real `-f -1 30000001 -1d`, imag `0 0 0 0`을 그대로 사용한다. 첫 inner box는 고정 FLINT quad_simple 산술로 만들고 원 log_map을 통해 물리 box를 기술했다. 두 geometry description은 field callback이 아니다. 원 margin 1/536870912와 원 signed107 순서를 입력 파싱으로 대조했다. 실제 HH 호출은 없었다.

최종 source에 대해 fresh/stale/duplicate/uncharged recorder, 범위 밖 query와 잘못된 hash, raw/source/binary/logbox/coefficient 및 관측 binding 변경, 누락 승인·중복 campaign 거절 등 18개 고유 검사가 통과했다. 기존 40개 검사나 검토 queue 실험을 새 검사로 세거나 재실행하지 않았다. 최종 live gate는 실제 전용 unit의 memory.max=34359738368, cpu.max=400000 100000, affinity64, 조상 quota/사용량/6GiB 여유, capabilities0, NoNewPrivs1, UID0와 private read-only cgroup view에서 통과했다. UID0 경로를 별도 비root UID 검증으로 부르지 않는다. 미래 unit 전체 wall60초와 query당10초/1024MiB 제한을 proposal에 결속했다. 향후 승인 직전에는 다시 실제 PID·namespace·자원·loader를 검사한다.

FD1 v1의 /proc/1/root 조상 읽기 EACCES와 v2의 /proc/1/ns/mnt capabilities0 EACCES, 초기 성공 sidecar 및 모든 로그는 그대로 보존했다. 최종 v3는 작업 private namespace 안에서 host cgroup view를 read-only bind하고 fresh outside/inside PID·namespace 소속을 대조한다. 시스템 전역 mount·계정·패키지는 변경하지 않았다. 소스가 바뀐 준비 continuation만 새 prefix에서 수행했으며 원 backend/worker 재빌드는 0회다. 현재 검사수에는 이전 준비 검사를 합산하지 않았다.

보호된 기존 파일/링크 {len(preserved)}개에 대해 bytes/SHA/mode/mtime/target 변화가 없었다. 소비된 6셀 registry, RUN_STARTED/EXECUTION_BINDING/raw/RETURN, 원 PREPARED와 실패 backend tree, B22 claim을 보존했다. claim 존재만으로 process/race 원인을 추론하지 않았다. R31AK frozen, z0.75 holdout, B128/B160 consumed, B192 reuse를 유지했다. Bianchi/rei_bianchi 및 다른 원자 repo는 변경하지 않았다.

최종 proposal self SHA256: `{proposal['proposal_sha256']}`
proposal file SHA256: `{sha(E/'DIAGNOSTIC_PROPOSAL.json')}`
query scope SHA256: `{proposal['queries']['query_scope_sha256']}`
sidecar source SHA256: `{proposal['diagnostic_source_sha256']}`
sidecar build self SHA256: `{proposal['build_self_sha256']}`

제안 후보는 Q272_cached, Q272_reference, Q000_cached, Q000_reference 각각1회, 총4 field callback, 적분0회, 단일worker이며 자동 retry가 없다. diagnostic registry와 output은 absent다. 이번 준비 요청이나 기존 6셀 승인은 이 후보의 과학 승인이 아니다. 실제 future run/consume/HH 경로는 시험 호출하지 않았다. 다음 최소 조치는 이 exact proposal과 고정4회·예산에 대한 별도 명시적 사용자 승인이다. 이후 결과가 불충분하면 UNRESOLVED로 멈추며 적분·다른 box·coverage를 추가하지 않는다.

같은 research branch의 additive/non-force publication 및 Drive/Dropbox create-only 결과 ZIP/보고서 백업은 별도 DELIVERY_RECEIPT에 실제 ACK/object/metadata와 최종 commit을 기록한다. 출력 검증 tier는 ACK+metadata이며 실제 다운로드 검증이 없는 출력의 RESTORE_VERIFIED는 false다. 입력 Dropbox object의 RESTORE_VERIFIED와 구분한다.
'''
 (E/'WORK_REPORT_KO.md').write_text(report)
 references=[]
 for version in ('fd1_prep_20261003_v1','fd1_prep_20261003_v2'):
  p=OLD/version
  for name in ('diagnostic.cpp','diagnostic_adapter.py','build/BUILD.json','evidence/DIAGNOSTIC_PROPOSAL.json'):
   references.append(ref(p/name))
 write(E/'PRIOR_FD1_CONTINUATIONS.json',dict(prior_files=references,prior_proposals_superseded_unpublished_and_unapproved=True,prior_trees_not_mutated=True,reason='Actual metadata-only gate failures; no HH evaluation/retry'))
 print(json.dumps(result))
if __name__=='__main__':main()
