"""Recompute compact scientific comparisons without solving an ODE or writing files."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from igm_compare import allowance, compare_rows, read_csv

def read(path):
    return json.loads((HERE / path).read_text())

def verify():
    expected = read('cache/IDENTITY_BRIDGE_REVIEW.json')['scientific_comparisons']
    candidate = read_csv(HERE / 'spectral/candidate1024-union.csv')
    results = []
    for item in expected:
        label = item['label']
        ref = read_csv(HERE / f'spectral/reference{label}-union.csv')
        result = compare_rows(candidate, ref)
        assert result['passed'] and result['row_count'] == 121
        assert len(result['fields']) == 37
        assert max(v['max_allowance_ratio'] for v in result['fields'].values()) == item['max_field_allowance_ratio']
        assert result['fields']['Gamma_heii']['max_allowance_ratio'] == item['Gamma_heii_max_allowance_ratio']
        assert result['budgets'] == item['budgets']
        results.append({'reference':label, 'fields':37, 'passed':True})
    coarse = read_csv(HERE / 'long-flrw/radau-p64-o2/history.csv')
    fine = read_csv(HERE / 'long-flrw/radau-p128-o2/history.csv')
    result = compare_rows(coarse, fine)
    recorded = read('long-flrw/ASSESSMENT.json')['comparison']
    for key in result:
        if key != 'fields':
            assert result[key] == recorded[key], key
    for field, values in result['fields'].items():
        saved = recorded['fields'][field]
        assert values == {key:saved[key] for key in values}, field
        i = values['worst_row']
        assert saved['worst_ln_a'] == coarse[i]['ln_a']
        assert saved['worst_z'] == coarse[i]['z']
        assert saved['actual_at_worst'] == coarse[i][field]
        assert saved['reference_at_worst'] == fine[i][field]
        assert saved['signed_difference_at_worst'] == coarse[i][field] - fine[i][field]
        assert saved['allowance_at_worst'] == allowance(field, fine[i][field])
    assert not result['passed']
    failed = sorted(k for k,v in result['fields'].items() if v['max_allowance_ratio'] > 1)
    assert len(failed) == 8
    bridge = read('cache/IDENTITY_BRIDGE.json')
    assert bridge['decision'] == 'ACCEPT_SHORT_FIXTURE_IDENTITY_BRIDGE'
    assert bridge['whole_trajectory_file_pairs_identical'] == 9
    print(json.dumps({'short_fixture':results,'long_history_failing_fields':failed,'long_history_acceptance':False},indent=2))

if __name__ == '__main__':
    verify()
