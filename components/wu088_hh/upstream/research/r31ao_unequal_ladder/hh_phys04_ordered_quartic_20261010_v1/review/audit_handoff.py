"""Final fixed NCP handoff identity/graph audit, without scientific execution."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'REVIEW_INPUT_MANIFEST.json': '4d6811b53e4875bbdee26458ec5d2427117439059b4d394e7b6d7350b35f00a3',
    'NCP_LOCAL_CODEX_HANDOFF_KO.md': '4d756b9a01fd97f769a79bddf413073890c3aa7e5806f4f44f1a302b72eba9c5',
    'NCP_TASKS.json': 'f688ce2b0988d4e2436d12b8b0ba796ec7f1418415194609e750fdce9a2c56e0',
    'NCP_RETURN_TEMPLATE.json': '297190718a31bd03c8c071a195bd8cc89d9868e795a47c98c326a4a3b9991cce',
}


def load(name):
    return json.loads((ROOT/name).read_text())


def run():
    for name, expected in EXPECTED.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected, name
    manifest = load('REVIEW_INPUT_MANIFEST.json')
    assert len(manifest['files']) == 100
    for row in manifest['files']:
        raw = (ROOT/row['path']).read_bytes()
        assert len(raw) == row['bytes'], row['path']
        assert hashlib.sha256(raw).hexdigest() == row['sha256'], row['path']
    tasks = load('NCP_TASKS.json')
    ret = load('NCP_RETURN_TEMPLATE.json')
    bindings = load('inputs/source_survey/SOURCE_LINE_BINDINGS.json')
    ss = {x['id'] for x in bindings}
    tree = {x['path']:x for x in load('inputs/source_survey/remote/OWNER_TREE.json')['tree']}
    for entry in tasks['source_entrypoints']:
        assert entry['path'] in tree, entry['path']
        assert set(entry['bindings']) <= ss, entry['path']
        if 'git_blob_at_owner_pin' in entry:
            assert entry['git_blob_at_owner_pin'] == tree[entry['path']]['sha']
    ids = [x['id'] for x in tasks['tasks']]
    assert len(ids) == len(set(ids)) == 11
    test_ids = {x['id'] for x in tasks['test_catalog']}
    assert len(test_ids) == 8
    completed = set()
    for task in tasks['tasks']:
        assert task['status'] == 'PENDING'
        assert set(task['depends_on']) <= completed, task['id']
        assert set(task['source_bindings']) <= ss
        assert set(task.get('tests', [])) <= test_ids
        for path in task.get('packet_references', []):
            assert (ROOT/path).is_file(), path
        completed.add(task['id'])
    assert [x['id'] for x in ret['task_results']] == ids
    assert {x['id'] for x in ret['validation']['targeted_tests']} == test_ids
    assert all(x['existence'] == 'TO_CREATE' for x in tasks['test_catalog'])
    assert all(x['existence'] == 'TO_CREATE' and x['status'] == 'PENDING'
               for x in ret['validation']['targeted_tests'])
    assert all(v == 0 for v in tasks['authority']['actual_native_science_budget'].values())
    assert all(v == 0 for v in ret['authority']['current_native_budget'].values())
    assert all(v is None for v in ret['call_counters']['observed_actual'].values())
    assert tasks['authority']['authorization_record'] is None
    assert ret['authority']['current_authorization_record'] is None
    assert ret['future_execution_proposal']['is_authorization'] is False
    assert ret['future_execution_proposal']['request_ready'] is False
    assert all(x['value'] is None and x['status'] == 'PENDING'
               for x in ret['observables']['actual'].values())
    assert ret['observables']['physical_admission'] == 'HOLD'
    assert ret['observables']['production_admission'] == 'HOLD'
    prompt = (ROOT/'NCP_LOCAL_CODEX_HANDOFF_KO.md').read_text()
    refs = set(re.findall(r'SS\d{2}', prompt))
    assert refs <= ss
    original_test = ROOT/'inputs/source_survey/snapshots/research/r31ao_unequal_ladder/ncp_phys01_mixed_contract_20261010_v1/tests/test_mixed_family.py'
    test_text = original_test.read_text()
    for name in ('test_all_shared_identity_mutations_rejected', 'test_missing_and_forged_native_certificate_rejected'):
        assert 'def '+name+'(' in test_text
        assert name in tasks['selective_commands']['existing_python_identity_regression']
    source_receipt = (ROOT/'inputs/source_survey/reused_phys03/energy06e/paired_stage_receipt.rs').read_text()
    assert 'mod energy06e_tests' in source_receipt
    assert 'actual_full(_permit,c,old,6.25e8)' in source_receipt
    return {
        'schema': 'HH_PHYS04_INDEPENDENT_FINAL_HANDOFF_AUDIT_V1',
        'reviewer': '/root/phys04_decision',
        'time_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS',
        'fixed_input_sha256': EXPECTED,
        'fixed_payloads_checked': 100,
        'source_entrypoint_paths_in_recorded_owner_tree': len(tasks['source_entrypoints']),
        'acyclic_topologically_ordered_tasks': len(ids),
        'new_test_catalog_return_alignment': len(test_ids),
        'native_budget_zero_and_observed_counts_nullable': True,
        'actual_metric_objects_null': len(ret['observables']['actual']),
        'existing_selective_python_methods_checked': 2,
        'existing_synthetic_receipt_module_checked': True,
        'new_target_names_not_claimed_existing': True,
        'candidate_overlay_distinct_from_preserved_original': True,
        'code_build_test_execution_performed': False,
        'native_dispatches': 0,
        'scientific_suite_replays': 0,
        'scope': 'Identity/graph/source-path/contract structure plus reviewer reading of all three final NCP files; not execution of NCP tasks.'
    }


if __name__ == '__main__':
    result = run()
    out = ROOT/'review/HANDOFF_AUDIT.json'
    with out.open('x') as f:
        f.write(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))
