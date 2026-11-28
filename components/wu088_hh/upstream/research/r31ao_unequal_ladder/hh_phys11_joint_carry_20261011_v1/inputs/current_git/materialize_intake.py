"""Materialize read-only connector intake and bind reused PHYS10 bytes; no science."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[1]
OLD = WORKSPACE / 'HH_PHYS10_20261011_v1'
PAYLOAD = HERE / 'FETCHED_INTAKE_INTERMEDIATE.json'
raw = json.loads(PAYLOAD.read_text())
now = datetime.now(timezone.utc).isoformat()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()

def put_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

for key, value in raw['observations'].items():
    put_json(HERE / 'observations' / (key + '.json'), value)

fetched = []
for item in raw['files']:
    data = item['content'].encode('utf-8')
    assert len(data) == item['expected_bytes'], item['path']
    assert blob(data) == item['git_blob_sha'], item['path']
    dest = HERE / 'files' / 'repo' / item['path']
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('xb') as stream:
        stream.write(data)
    old_path = (OLD / 'inputs/current_return/files/repo/AGENTS.md'
                if item['path'] == 'AGENTS.md'
                else OLD / 'inputs/current_repo' / item['path'])
    assert old_path.read_bytes() == data, ('baseline changed', item['path'])
    fetched.append({'path': 'files/repo/' + item['path'],
                    'repository_path': item['path'], 'source_commit': raw['head'],
                    'source_url': item['source_url'], 'bytes': len(data),
                    'sha256': sha(data), 'git_blob_sha': item['git_blob_sha'],
                    'git_blob_verified': True, 'same_as_PHYS10_baseline': True,
                    'previous_local_path': str(old_path)})

tree = raw['observations']['PHYS10_CORE_TREE']
assert tree['sha'] == 'b7592637e565666ad92047b7ea25067a4d6bd34b'
assert not tree['truncated']
ladder = raw['observations']['LADDER_TREE_RELEVANT']
assert next(x for x in ladder['tree'] if x['path'] == 'hh_phys10_gas_photon_20261011_v1')['sha'] == tree['sha']
reuse = []
for item in tree['tree']:
    if item['type'] != 'blob':
        continue
    local = OLD / item['path']
    data = local.read_bytes()
    assert len(data) == item['size'], item['path']
    assert blob(data) == item['sha'], item['path']
    reuse.append({'local_path': str(local), 'relative_path': item['path'],
                  'repository_path': 'research/r31ao_unequal_ladder/hh_phys10_gas_photon_20261011_v1/' + item['path'],
                  'source_commit': raw['head'], 'bytes': len(data),
                  'sha256': sha(data), 'git_blob_sha': item['sha'],
                  'git_blob_verified': True, 'disposition': 'REUSE_EXISTING_COMPLETE_BYTES'})
remote_paths = {x['relative_path'] for x in reuse}
extra = sorted(str(p.relative_to(OLD)) for p in OLD.rglob('*') if p.is_file() and str(p.relative_to(OLD)) not in remote_paths)
assert sha((OLD / 'MANIFEST.json').read_bytes()) == '14635f20b0553871bfdd3ad9a7893bfc526021477dab8bc5bac52891db1134c1'
put_json(HERE / 'FETCHED_FILE_IDENTITY_MANIFEST.json', {'schema': 'WU088_HH_PHYS11_FETCHED_CONTEXT_IDENTITY_V1', 'completed_utc': now, 'files': fetched, 'file_count': len(fetched), 'all_git_blob_verified': True})
put_json(HERE / 'LOCAL_REUSE_MANIFEST.json', {'schema': 'WU088_HH_PHYS11_LOCAL_REUSE_IDENTITY_V1', 'completed_utc': now, 'source_commit': raw['head'], 'source_subtree': tree['sha'], 'files': reuse, 'file_count': len(reuse), 'bytes': sum(x['bytes'] for x in reuse), 'all_git_blob_verified': True, 'untracked_local_files_not_adopted': extra, 'scientific_reexecution': False})

old_decision = json.loads((OLD / 'review/DECISION.json').read_text())
old_tasks = json.loads((OLD / 'NCP_TASKS.json').read_text())
old_run = json.loads((OLD / 'evidence/ledger_first/EXECUTION.json').read_text())
old_intake = json.loads((OLD / 'inputs/current_return/SOURCE_INTAKE_SUMMARY.json').read_text())
refs = raw['observations']['ALL_BRANCH_REFS']['refs']
assert next(x for x in refs if x['ref'] == 'refs/heads/codex/hh-phys08-ncp-20261011')['sha'] == '5288fd50148755f5ed37391e3dcb612d8d51f130'
assert next(x for x in refs if x['ref'] == 'refs/heads/codex/hh-phys09-ncp-20261011')['sha'] == 'e6a72c3df5803b5b23f9a38918dad6a1eba7e1f7'
assert old_decision['decision'] == 'PROMOTE_SCOPED'
assert old_tasks['heavy_queue'] == [] and old_tasks['launch'] is False
summary = {
    'schema': 'WU088_HH_PHYS11_CURRENT_SOURCE_INTAKE_V1', 'completed_utc': now,
    'status': 'PHYS10_COMPLETE_SCOPED_REUSABLE_NO_NEW_NCP10_GIT_RETURN_OBSERVED',
    'repository': raw['repository'],
    'recommended_parent': {'branch': 'research/hh-phys10-gas-photon-ledger-20261011', 'head': raw['head'], 'root_tree': raw['observations']['BASE_COMMIT']['tree']['sha'], 'core_commit': 'c9fc72d92dc008f1be20a1e00839a422d0ce29ce', 'core_subtree': tree['sha'], 'core_path': 'research/r31ao_unequal_ladder/hh_phys10_gas_photon_20261011_v1', 'delivery_subtree': '5c40df1f0bd0b25d8395e6c741dc291fd963b535', 'PR': raw['observations']['PR43']},
    'search_scope': {'all_branch_ref_count': len(refs), 'phys10_branch_refs': [x for x in refs if 'phys10' in x['ref'].lower()], 'latest_updated_PR_count': 12, 'new_NCP10_Git_return_observed': False, 'backups_or_other_threads_searched_by_this_agent': False, 'bounded_observation_not_global_absence_proof': True},
    'previous_work': {'PHYS08': {'state': 'REUSED_EXISTING_COMPLETE', 'head': old_intake['ncp08']['head']}, 'PHYS09': {'state': 'REUSED_EXISTING_COMPLETE', 'head': old_intake['ncp09']['head']}, 'PHYS10': {'state': 'REUSED_EXISTING_COMPLETE', 'decision': old_decision['decision'], 'run_id': old_run['run_id'], 'elapsed_seconds': old_run['elapsed_seconds'], 'max_rss_KiB': old_run['ru_maxrss_KiB_linux'], 'exit_code': old_run['exit_code'], 'evidence_original': 'HH_PHYS10_20261011_v1/evidence/ledger_first/EXECUTION.json', 'replay': False}},
    'inherited_NCP_queue': {'heavy_queue': [], 'launch': False, 'empty_return': old_tasks['return_when_empty']},
    'identity': {'fetched_context_files': len(fetched), 'verified_reusable_PHYS10_files': len(reuse), 'verified_reusable_PHYS10_bytes': sum(x['bytes'] for x in reuse), 'changed_current_AGENTS_or_mandatory_baseline_documents': 0, 'manifest_sha256': sha((OLD / 'MANIFEST.json').read_bytes()), 'file_identity_is_not_scientific_or_native_authority': True},
    'read_only_intake': {'remote_mutations': 0, 'scientific_source_or_runtime_calls': 0, 'compiler_build_gate_consumer_replays': 0, 'candidate_derivation_or_test_design': False, 'eligible_noncreator_final_reviewer': True},
    'model_routing': {'host_label': 'GPT-6 Astra Pro', 'exact_router_alias': 'MODEL_UNRESOLVED_PRO_ALIAS_ABSENT', 'workflow': 'previously_selected_verified_Astra_v4_model_independent_continuation', 'model_identity_attestation': False, 'model_switched': False},
    'claim_ceiling_preserved': old_decision['claim_ceiling'],
    'context_read_note': 'AGENTS and four mandatory baseline documents read at fixed current commit. Research PROJECT_INSTRUCTIONS, START_HERE, MODEL_ROUTING and coding AGENTS, START_HERE read from already verified Astra v4 packages. Initial optional research/AGENTS.md read returned absent; canonical research entry is PROJECT_INSTRUCTIONS.md and was read.'
}
put_json(HERE / 'SOURCE_INTAKE_SUMMARY.json', summary)
PAYLOAD.unlink()
print(json.dumps({'status': summary['status'], 'fetched': len(fetched), 'reused_files': len(reuse), 'reused_bytes': sum(x['bytes'] for x in reuse), 'untracked_local_files_not_adopted': extra, 'head': raw['head']}, ensure_ascii=False))
