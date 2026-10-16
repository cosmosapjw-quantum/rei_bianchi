import datetime
import hashlib
import json
import pathlib
import platform
import shutil
import time

root = pathlib.Path(__file__).resolve().parent
source = pathlib.Path('/root/full005-pair-controller/prior_actual_cached_001')
target = root / 'reused_actual_cached_001'
prior_path = root / 'research/flrw_full005_postprocess_20261015/completed_pair_20261016_001/results/POSTPROCESS_RECEIPT.json'
prior = json.loads(prior_path.read_text())
returned = json.loads((source / 'RETURN_CONTRACT.json').read_text())
receipt = json.loads((source / 'results/PAIR_DIAGNOSTICS_RECEIPT.json').read_text())
review = json.loads((source / 'INDEPENDENT_REVIEW.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(prior_path) == returned['input_receipt_sha256'] == receipt['prior_validated_receipt_sha256']
checks = []
for name, expected in returned['source_sha256'].items():
    path = root / ('research/flrw_full005_pair_diagnostics_20261016/' + name if '/' not in name else 'research/flrw_full005_postprocess_20261015/' + name)
    observed = sha(path)
    assert observed == expected, (path, observed, expected)
    checks.append(dict(kind='FROZEN_SOURCE_BYTE_IDENTITY', path=str(path), sha256=observed))
for name, expected in returned['outputs'].items():
    path = source / 'results' / name
    observed = sha(path)
    assert observed == expected, (path, observed, expected)
    checks.append(dict(kind='SAVED_OUTPUT_BYTE_READBACK', path=str(path), sha256=observed))
assert receipt['status'] == 'PAIR_DIAGNOSTICS_COMPLETE'
assert returned['exit_code'] == 0
assert review['decision'] == 'PASS_SCOPED_SAVED_FULL005_PL_DIAGNOSTICS_AND_PUBLICATION'
raw_root = pathlib.Path('/root/REI_FLRW_COVARIANT_20261015_005/full_campaign001')
inputs = []
for case in receipt['necessary_inputs']:
    old = next(c for c in prior['validated_complete_inputs'] if c['id'] == case['id'])
    for role, descriptor in case.items():
        if role == 'id':
            continue
        assert descriptor == old[role], (case['id'], role)
        path = raw_root / ('launches' if role == 'binding' else 'runs/' + case['id']) / pathlib.Path(descriptor['path']).name
        assert path.is_file(), path
        item = dict(case=case['id'], role=role, original_descriptor=descriptor,
                    ncp_path=str(path), exists=True, bytes=path.stat().st_size,
                    descriptor_relation='BYTE_IDENTICAL_EXPECTED_HASH_AND_ORIGINAL_PATH')
        if role in ('history', 'abundances'):
            item.update(current_bytes_rehashed=False,
                        identity_evidence='Reused successful inline-hashed actual execution and independent review; no raw stream replay')
        else:
            observed = sha(path)
            assert observed == descriptor['sha256'], (path, observed)
            item.update(current_bytes_rehashed=True, observed_sha256=observed)
        inputs.append(item)
for path in source.rglob('*'):
    if path.is_file():
        dest = target / path.relative_to(source)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            assert dest.read_bytes() == path.read_bytes(), dest
        else:
            shutil.copy2(path, dest)
baseline = 103.79374452296179
later = returned['wall_seconds_including_termination']
used = baseline + later
deadline = 1792122617.77407
budget_path = pathlib.Path('/root/REI_POSTPROCESS_20261015_001/FULL005_PAIR_CONTINUATION_BUDGET.json')
if budget_path.exists():
    previous = json.loads(budget_path.read_text())
    assert not previous.get('active'), previous
    assert previous.get('cumulative_wall_seconds', baseline) <= used + 1e-8, previous
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
budget = dict(status='REUSED_COMPLETED_ACTUAL_CACHED_001_NO_EXECUTION',
    code_commit='e881b38951bc896c29d5ea57bb8fb1f2803873e1',
    reused_result_commit='40f04078e35640acf3bd5f48fe609dbc2e6d8173',
    unchanged_deadline_epoch=deadline, deadline_reset=False,
    cumulative_wall_seconds=used, baseline_wall_seconds=baseline,
    later_execution_wall_seconds=later, new_execution_wall_seconds=0,
    remaining_wall_ceiling_seconds=300-used, original_wall_cap_seconds=300,
    active=False, active_allowance_seconds=0, stop_reserve_seconds=5,
    executed=False, solver_runs=0, renderer_runs=0, analyzer_launches_this_task=0,
    deduplication_key=returned['execution_receipt_sha256'],
    later_debit_evidence=str(target/'RETURN_CONTRACT.json'), recorded_utc=now)
budget_path.parent.mkdir(parents=True,exist_ok=True)
budget_path.write_text(json.dumps(budget,indent=2,allow_nan=False)+'\n')
(root/'CONTINUATION_STATUS.json').write_text(json.dumps(budget,indent=2,allow_nan=False)+'\n')
inventory = json.loads(pathlib.Path('/tmp/full005-pair-existing-record-paths.json').read_text())
inventory_note = dict(paths=inventory, scope='Known FULL005/postprocess/recovery/pair top-level roots; original /home/cosmosapjw absent',
    prior_local_failures='Owner22:32 and NCP23:28 historical failures precede completed baseline; duplicated snapshot receipts deduplicated; no additional post-baseline local launch located',
    later_completed_attempt='Owner actual_cached_001 at01:12:19Z–01:13:11Z, wall52.743859184s; debit once',
    unknown_aborted_attempts_found=False, wrapper='NOT_RUN; parent stop instruction arrived before any launch')
result = dict(status='PASS_MECHANICAL_REUSE_COMPLETED_ACTUAL_CACHED_001', recorded_utc=now,
    scientific_admission='Existing independent scoped decision reused; no new scientific decision',
    reused_independent_decision=review['decision'],
    current_executor=dict(role='parent-delegated bounded execution/reuse worker', requested_model='gpt-6.1-sol/high', observed_model='NOT_INDEPENDENTLY_OBSERVED'),
    historical_executor=dict(requested=returned['requested_execution_profile'], observed=returned['observed_execution_identity']),
    code_commit=budget['code_commit'], reused_result_commit=budget['reused_result_commit'],
    original_execution=returned, current_python=platform.python_version(),
    checks=checks, necessary_input_relations=inputs, inventory=inventory_note,
    budget_path=str(budget_path), budget=budget,
    analyzer_launches_this_task=0, wrapper_runs_this_task=0, raw_stream_reads_this_task=0,
    solver_runs_this_task=0, renderer_runs_this_task=0, ledger_reads_this_task=0, checkpoint_reads_this_task=0,
    artifact_root=str(target),
    claim_ceiling='Stored binary64 ln(a) PL difference only; no solver accuracy/convergence/physical error bound.',
    remaining_action='Parent read-only reuse review and authorized public-safe publication/backup; no numerical replay')
(root/'EXECUTION_REUSE_RECEIPT.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(dict(status=result['status'], receipt=str(root/'EXECUTION_REUSE_RECEIPT.json'), budget=str(budget_path), cumulative_wall_seconds=used, inputs=len(inputs), byte_checks=len(checks), new_analyzer_launches=0),allow_nan=False))
