#!/usr/bin/env python3
"""Data-only D8 byte/semantic/provenance reconciliation; no numerical solver."""
import argparse, copy, hashlib, json, pathlib

PUBLISHED = '9c7a3c74cff48bb76d00c6af9795783aae2a7bb4a1e455d07cc1dd89b51e71e8'
REVIEWED = '643cea016e4bf35968f947aea3519bd292c434094a6e7430e8b9c2fb203318ce'
CASE_C = '1c39be4e6a5b7a7862d97efda76ea24b5b88a07db2696ffe76fe4b6cbf9c2e91'
KEYS = ('historical_execution_exit', 'historical_execution_status',
        'initial_matter_stress_interpretation', 'initial_matter_stress_observed',
        'saved_raw_data_only_recovery_exit', 'saved_raw_data_only_recovery_status',
        'solver_metadata_fields_unrecorded')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def encoded(obj):
    return (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def verify(root, reconstructed):
    data = (root / 'D8_RESULT.json').read_bytes()
    assert sha(data) == PUBLISHED, 'published result bytes changed'
    published = json.loads(data)
    historical = copy.deepcopy(published)
    additions = {'/execution_provenance_note': historical.pop('execution_provenance_note')}
    case = next(c for c in historical['cases'] if c['case_id'] == CASE_C)
    for key in KEYS:
        additions['/cases/c/' + key] = case.pop(key)
    recreated = encoded(historical)
    assert sha(recreated) == REVIEWED, 'reconstructed bytes do not match original review'
    assert reconstructed.read_bytes() == recreated, 'reconstructed artifact differs'
    old_review = json.loads((root / 'INDEPENDENT_REVIEW.json').read_text())
    assert old_review['reviewed_result_sha256'] == REVIEWED
    assert old_review['reviewed_analysis_sha256'] == sha((root / 'analyze_d8.py').read_bytes())
    assert canonical(historical) != canonical(published), 'provenance additions are semantic changes'
    restored = copy.deepcopy(historical)
    restored['execution_provenance_note'] = additions['/execution_provenance_note']
    c = next(c for c in restored['cases'] if c['case_id'] == CASE_C)
    for key in KEYS:
        c[key] = additions['/cases/c/' + key]
    assert restored == published, 'changes beyond eight additive provenance fields'
    checks = []
    for c in published['cases']:
        receipt_dir = root / 'raw_cases' / c['case_id']
        inp = json.loads((receipt_dir / 'INPUT.json').read_text())
        receipt = json.loads((receipt_dir / 'RESULT.json').read_text())
        assert inp['config'] == c['config'] == receipt['config']
        assert receipt['raw_sha256'] == c['raw_sha256']
        assert receipt['raw_bytes'] == c['raw_bytes']
        assert c['stored_sample_count'] == 153 and c['z4_sample_index'] == 120
        assert len(c['strict_adjacent_sign_change_brackets']) == 1
        bracket = c['strict_adjacent_sign_change_brackets'][0]
        assert bracket['index_pair'][1] == bracket['index_pair'][0] + 1
        assert bracket['S_F_signed'][0] > 0 > bracket['S_F_signed'][1]
        checks.append({'case_id': c['case_id'], 'raw_sha256': c['raw_sha256'],
                       'indices': bracket['index_pair'], 'bracket': bracket['redshift_descending']})
    failure = json.loads((root / 'raw_cases' / CASE_C / 'RESULT.serialization_failure.json').read_text())
    assert failure['exit'] == additions['/cases/c/historical_execution_exit'] == 124
    assert failure['status'] == additions['/cases/c/historical_execution_status'] == 'FAILED_WORKER_EXIT'
    return {'status': 'PASS_BYTE_SEMANTIC_PROVENANCE_RECONCILIATION',
            'published_sha256': PUBLISHED, 'reconstructed_reviewed_sha256': REVIEWED,
            'historical_artifact_is_reconstructed_not_retrieved': True,
            'full_json_semantically_equal': False, 'changed_existing_fields': 0,
            'added_provenance_fields': additions,
            'old_numeric_config_bracket_raw_identity_fields_preserved': True,
            'receipt_bound_cases': checks, 'raw_npz_bytes_independently_reverified': False,
            'new_solver_calls': 0, 'scientific_admission_expanded': False}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-dir', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parent.parent)
    ap.add_argument('--reconstructed', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parent / 'REVIEWED_RESULT_RECONSTRUCTED.json')
    args = ap.parse_args()
    print(json.dumps(verify(args.input_dir, args.reconstructed), indent=2, sort_keys=True, allow_nan=False))
