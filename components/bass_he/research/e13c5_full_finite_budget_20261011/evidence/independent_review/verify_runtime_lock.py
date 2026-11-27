#!/usr/bin/env python3
"""Independent identity and receipt audit; no wrapper or science execution."""
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

BASE = Path('/workspace/scratch/7fd51143e473/BASS_HE_E13C5_FULL_FINITE_BUDGET_20261011_v1')
OUT = BASE / 'evidence/independent_review'
EXPECTED_RUNNER = 'ab1b07c45136b77bf492148fa3e7560d2c2f02cb5650a6d0de5fc4fe00244a79'
EXPECTED_LOCK = 'cdfda6cd49eeb38518b2a41156a087f744e0985e0384bf628ca8b893dbec5b3a'
COUNTS = Counter()
FAILURES = []

def check(kind, good, detail):
    COUNTS[kind] += 1
    if not good:
        FAILURES.append({'category': kind, 'detail': detail})

def read(p):
    return json.loads((BASE / p).read_text())

def identity(p):
    h = hashlib.sha256()
    size = 0
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
            size += len(b)
    return {'bytes': size, 'sha256': h.hexdigest()}

def canonical_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()

def main():
    lock = read('RUN_LOCK.json')
    contract = read('SCIENTIFIC_CONTRACT.json')
    ncp = read('NCP_EXECUTION_CONTRACT.json')
    source = (BASE / 'code/ncp_budget_continue.py').read_text()
    tree = ast.parse(source)
    constants = {t.targets[0].id: ast.literal_eval(t.value) for t in tree.body if isinstance(t, ast.Assign) and isinstance(t.targets[0], ast.Name) and isinstance(t.value, ast.Constant)}
    check('runner_identity', identity(BASE / 'code/ncp_budget_continue.py')['sha256'] == EXPECTED_RUNNER, 'runner')
    check('lock_identity_and_source_binding', identity(BASE / 'RUN_LOCK.json')['sha256'] == constants['LOCK_SHA256'] == EXPECTED_LOCK, 'RUN_LOCK')
    locked = {}
    for name, expected in lock['files'].items():
        actual = identity(BASE / name)
        check('locked_file_identity', actual == expected, name)
        locked[name] = actual
    check('locked_file_count', len(locked) == 14, '14')
    check('input_flag_coverage', set(lock['input_map']) == {n.replace('_', '-') for n in contract['pinned_inputs']}, 'input_map')
    for flag, value in lock['input_map'].items():
        pin = {k: value[k] for k in ('bytes', 'sha256')}
        check('input_pin_binding', pin == contract['pinned_inputs'][flag.replace('-', '_')], flag)
        check('input_dependency_member_binding', value['dependency'] in lock['dependencies'] and not Path(value['member']).is_absolute() and '..' not in Path(value['member']).parts, flag)
    check('limits_same_contract', lock['limits'] == ncp['limits'], 'limits')
    check('runtime_declares_no_actual_ncp', ncp['actual_NCP_execution_in_Chat'] == lock['actual_NCP_execution_here'] == 'NOT_RUN', 'NCP')
    projection = read(lock['expected_projection']['path'])
    normalized = dict(projection)
    normalized['ranking_artifact'] = {k: v for k, v in projection['ranking_artifact'].items() if k not in ('bytes', 'sha256')}
    check('semantic_baseline_identity', canonical_hash(normalized) == lock['expected_projection']['semantic_sha256'] == ncp['parity']['semantic_sha256'], 'projection')
    csv = read('evidence/independent_review/RANKING_CSV_REVIEW.json')
    check('independently_reconstructed_csv_baseline', csv['decompressed_CSV'] == lock['expected_ranking_content'] == ncp['parity']['uncompressed_ranking_CSV'], 'CSV')
    check('only_transport_fields_normalized', ncp['parity']['only_normalized_transport_fields'] == ['ranking_artifact.bytes', 'ranking_artifact.sha256'], 'normalization')
    calls = [x for x in ast.walk(tree) if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and isinstance(x.func.value, ast.Name) and x.func.value.id == 'subprocess']
    check('one_subprocess_creation_site', len(calls) == 1 and calls[0].func.attr == 'Popen', 'AST')
    original = read('evidence/runtime_boundary/SYNTHETIC01/RESULTS.json')
    check('original_boundary_source_pin', identity(BASE / 'evidence/independent_review/NULL_BINDING_COUNTEREXAMPLE01/reviewed_runner_before_fix.py') == original['runner_identity'], 'before-source')
    check('boundary_controller_pin', identity(BASE / 'evidence/runtime_boundary/controls.py') == original['controller_identity'], 'controls-source')
    for c in original['checks']:
        check('original_boundary_case_recorded_pass', c['pass'] is True and c['synthetic'] is True, c['id'])
        if 'actual_status' in c:
            receipt = read('evidence/runtime_boundary/SYNTHETIC01/cases/' + c['id'] + '/OUT/RUN_RECEIPT.json')
            check('original_boundary_actual_receipt', receipt['status'] == c['actual_status'] and receipt['budget_invocations'] == c['budget_invocations'] and receipt['physics_invocations'] == 0 and receipt.get('error') == c.get('error'), c['id'])
    check('original_boundary_scope', original['check_count'] == original['passed'] == 21 and original['failed'] == 0 and original['actual_budget_science_replays'] == 0, '21 historical tests')
    before = (BASE / 'evidence/independent_review/NULL_BINDING_COUNTEREXAMPLE01/reviewed_runner_before_fix.py').read_text()
    check('only_focused_predicate_changed', source == before.replace('if result.get(key) != value:', 'if key not in result or result[key] != value:'), 'one-line diff')
    fixed = read('evidence/independent_review/NULL_BINDING_FOCUSED01/RESULTS.json')
    check('independent_focused_fix_cases', fixed['status'] == 'PASS' and fixed['check_count'] == 2 and all(c['pass'] for c in fixed['checks']) and fixed['runner_sha256'] == EXPECTED_RUNNER, 'fixed')
    receipt = read('evidence/runtime_boundary/ACTUAL_VERIFY_ONLY02/RUN_RECEIPT.json')
    check('final_actual_verify_only', receipt['status'] == 'VERIFY_ONLY_READY' and receipt['budget_invocations'] == receipt['physics_invocations'] == receipt['N512_invocations'] == receipt['full_first2_invocations'] == 0, 'verify-only')
    check('final_actual_source_before_after', receipt['source_sha256_before'] == receipt['source_sha256_after'] == EXPECTED_RUNNER and receipt['run_lock_sha256'] == EXPECTED_LOCK, 'verify-only source')
    check('final_actual_all_locked_before_after', receipt['locked_files_before'] == receipt['locked_files_after'] == locked, 'verify-only files')
    check('verify_only_not_numerical_or_provider_admission', receipt['accuracy'] == 'NOT_EVALUATED' and receipt['reduction'] == 'NOT_RUN' and receipt['host']['provider_verified'] is False, 'verify-only ceiling')
    result = {'schema': 'independent-runtime-lock-review-v1', 'created_utc': datetime.now(timezone.utc).isoformat(), 'status': 'PASS' if not FAILURES else 'FAIL', 'check_count': sum(COUNTS.values()), 'check_counts': dict(COUNTS), 'failed_count': len(FAILURES), 'failures': FAILURES, 'runner_identity': identity(BASE / 'code/ncp_budget_continue.py'), 'RUN_LOCK_identity': identity(BASE / 'RUN_LOCK.json'), 'locked_files': locked, 'actual_wrapper_execution_by_reviewer': 0, 'reviewer_function_only_repair_tests': 2, 'actual_NCP_execution': 'NOT_RUN', 'scope': 'Final source and exact lock identity, code audit, original recorded synthetic boundary evidence, focused one-line repair and final verify-only receipt; no actual full wrapper execute in Chat.'}
    with (OUT / 'RUNTIME_LOCK_REVIEW.json').open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps({k: result[k] for k in ('status', 'check_count', 'check_counts', 'failed_count', 'failures')}))

if __name__ == '__main__':
    main()
