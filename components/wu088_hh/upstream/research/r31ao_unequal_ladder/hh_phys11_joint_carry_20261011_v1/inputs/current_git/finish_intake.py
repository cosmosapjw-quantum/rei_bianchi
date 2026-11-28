"""Continue intake reporting after the preserved schema-key error; no re-materialization."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[1]
OLD = WORKSPACE / 'HH_PHYS10_20261011_v1'
PAYLOAD = HERE / 'FETCHED_INTAKE_INTERMEDIATE.json'
raw = json.loads(PAYLOAD.read_text())
now = datetime.now(timezone.utc).isoformat()

def read(path):
    return json.loads(path.read_text())

def put(path, obj):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

fetched = read(HERE / 'FETCHED_FILE_IDENTITY_MANIFEST.json')
reused = read(HERE / 'LOCAL_REUSE_MANIFEST.json')
decision = read(OLD / 'review/DECISION.json')
tasks = read(OLD / 'NCP_TASKS.json')
run = read(OLD / 'evidence/ledger_first/EXECUTION.json')
old_intake = read(OLD / 'inputs/current_return/SOURCE_INTAKE_SUMMARY.json')
refs = raw['observations']['ALL_BRANCH_REFS']['refs']
manifest_record = next(x for x in reused['files'] if x['relative_path'] == 'MANIFEST.json')
assert decision['decision'] == 'PROMOTE_SCOPED'
assert tasks['heavy_queue'] == [] and tasks['launch'] is False
summary = {
    'schema': 'WU088_HH_PHYS11_CURRENT_SOURCE_INTAKE_V1',
    'completed_utc': now,
    'status': 'PHYS10_COMPLETE_SCOPED_REUSABLE_NO_NEW_NCP10_GIT_RETURN_OBSERVED',
    'repository': raw['repository'],
    'recommended_parent': {'branch': 'research/hh-phys10-gas-photon-ledger-20261011', 'head': raw['head'], 'root_tree': raw['observations']['BASE_COMMIT']['tree']['sha'], 'core_commit': 'c9fc72d92dc008f1be20a1e00839a422d0ce29ce', 'core_subtree': reused['source_subtree'], 'core_path': 'research/r31ao_unequal_ladder/hh_phys10_gas_photon_20261011_v1', 'delivery_subtree': '5c40df1f0bd0b25d8395e6c741dc291fd963b535', 'PR': raw['observations']['PR43']},
    'search_scope': {'all_branch_ref_count': len(refs), 'phys10_branch_refs': [x for x in refs if 'phys10' in x['ref'].lower()], 'latest_updated_PR_count': 12, 'new_NCP10_Git_return_observed': False, 'backups_or_other_threads_searched_by_this_agent': False, 'bounded_observation_not_global_absence_proof': True},
    'previous_work': {'PHYS08': {'state': 'REUSED_EXISTING_COMPLETE', 'head': old_intake['ncp08']['commit']}, 'PHYS09': {'state': 'REUSED_EXISTING_COMPLETE', 'head': old_intake['ncp09']['commit']}, 'PHYS10': {'state': 'REUSED_EXISTING_COMPLETE', 'decision': decision['decision'], 'run_id': run['run_id'], 'elapsed_seconds': run['elapsed_seconds'], 'max_rss_KiB': run['ru_maxrss_KiB_linux'], 'exit_code': run['exit_code'], 'evidence_original': 'HH_PHYS10_20261011_v1/evidence/ledger_first/EXECUTION.json', 'replay': False}},
    'inherited_NCP_queue': {'heavy_queue': [], 'launch': False, 'empty_return': tasks['return_when_empty']},
    'identity': {'fetched_context_files': fetched['file_count'], 'verified_reusable_PHYS10_files': reused['file_count'], 'verified_reusable_PHYS10_bytes': reused['bytes'], 'changed_current_AGENTS_or_mandatory_baseline_documents': 0, 'manifest_sha256': manifest_record['sha256'], 'file_identity_is_not_scientific_or_native_authority': True},
    'read_only_intake': {'remote_mutations': 0, 'scientific_source_or_runtime_calls': 0, 'compiler_build_gate_consumer_replays': 0, 'candidate_derivation_or_test_design': False, 'eligible_noncreator_final_reviewer': True, 'preserved_intake_schema_error': 'MATERIALIZATION_FIRST_FAILURE.json', 'correction': 'finish_intake.py continued summary only from existing verified manifests'},
    'model_routing': {'host_label': 'GPT-6 Astra Pro', 'exact_router_alias': 'MODEL_UNRESOLVED_PRO_ALIAS_ABSENT', 'workflow': 'previously_selected_verified_Astra_v4_model_independent_continuation', 'model_identity_attestation': False, 'model_switched': False},
    'claim_ceiling_preserved': decision['claim_ceiling'],
    'context_read_note': 'AGENTS and all four mandatory baseline documents read at the fixed current commit. Research PROJECT_INSTRUCTIONS, START_HERE, MODEL_ROUTING and coding AGENTS, START_HERE read from verified Astra v4 packages. Initial optional research/AGENTS.md path was absent; canonical research entry PROJECT_INSTRUCTIONS.md was then read.'
}
put(HERE / 'SOURCE_INTAKE_SUMMARY.json', summary)
md = f'''# PHYS11 최신 Git·반환물 읽기 결과

기준은 PHYS10 PR43의 `{raw['head']}`이며, 현재 branch와 PR head가 일치한다. root tree는 `{summary['recommended_parent']['root_tree']}`, 연구 본문 subtree는 `{reused['source_subtree']}`다. 이 commit을 PHYS11의 additive parent로 사용할 수 있다.

51개 branch ref와 updated 내림차순 최근 PR 12개를 확인했다. PHYS10 이름을 가진 ref는 기존 연구 branch 하나이며 새 NCP10 Git 반환은 관측되지 않았다. 이 agent는 백업 및 다른 스레드를 검색하지 않았으므로 이 결과를 모든 저장 위치에서의 전역 부재로 해석하지 않는다.

현재 AGENTS와 필수 문서 네 개를 실제로 읽었다. 5개 문서 모두 원 Git blob/bytes가 일치하고 PHYS10에 보존된 같은 문서와도 같다. PHYS10의 {reused['file_count']}개 파일, {reused['bytes']:,} bytes를 고정 Git subtree의 원 blob과 대조했다. `LOCAL_REUSE_MANIFEST.json`의 경로를 그대로 재사용할 수 있다. 원 과학 실행·compiler·build·gate·consumer는 실행하지 않았다.

PHYS08/09 완료 반환의 branch identity도 그대로다. PHYS10 독립 결정은 PROMOTE_SCOPED이며, 기존 실행은 0.7208253940043505초 / 최대 RSS 23924 KiB / exit 0이다. 기존 heavy queue는 비어 있고 launch=false다. 이 intake 자체는 새로운 과학 결과나 native 권한을 생성하지 않는다.

기존 root/U/V/W/I의 null, native_authority=false, 실제 carry·history·시간/연속체 remainder·full49/production OPEN을 보존한다. 근거 수준과 byte identity는 분리한다.

문서화 serializer의 첫 시도는 기존 필드명 commit을 head로 읽어 KeyError가 발생했다. 그 전에 끝난 원 blob 검증·물질화와 두 manifest를 보존했고, 정확한 필드명을 읽어 요약만 이어서 작성했다. 실패 원문과 코드 및 수정 경로는 MATERIALIZATION_FIRST_FAILURE.json, materialize_intake.py, finish_intake.py에 남겼다. 과학 실행 실패나 과학 재시도는 아니다.

이 agent는 후보 과학 유도·구현·검증 설계를 맡지 않았으며, 동결 뒤 독립 최종 decision reviewer 역할을 맡을 수 있다.
'''
with (HERE / 'SOURCE_INTAKE_SUMMARY_KO.md').open('x', encoding='utf-8') as stream:
    stream.write(md)
PAYLOAD.unlink()
files = []
for p in sorted(HERE.rglob('*')):
    if p.is_file() and p.name != 'INTAKE_EVIDENCE_MANIFEST.json':
        data = p.read_bytes()
        files.append({'path': str(p.relative_to(HERE)), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
put(HERE / 'INTAKE_EVIDENCE_MANIFEST.json', {'schema': 'WU088_HH_PHYS11_INTAKE_EVIDENCE_MANIFEST_V1', 'completed_utc': now, 'files': files, 'file_count': len(files), 'bytes': sum(x['bytes'] for x in files), 'excludes': ['INTAKE_EVIDENCE_MANIFEST.json'], 'scientific_runtime_calls': 0, 'remote_mutations': 0})
print(json.dumps({'status': summary['status'], 'fetched_context_files': fetched['file_count'], 'reused_files': reused['file_count'], 'reused_bytes': reused['bytes'], 'intake_files': len(files), 'intake_bytes': sum(x['bytes'] for x in files), 'head': raw['head']}, ensure_ascii=False))
