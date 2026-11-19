#!/usr/bin/env python3
"""Owner consumes admitted native D01 data at the original physical targets.

Data admission and a numerical-accuracy claim remain separate decisions.
No native evolution is performed and no additional refinement is authorized.
"""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
FRACTIONS = ['x_HI', 'x_HII', 'x_HeI', 'x_HeII', 'x_HeIII']
FIELDS = FRACTIONS + ['xe_per_H', 'temperature_K']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def maximum(rows, column):
    row = max(rows, key=lambda r: abs(r[column]))
    return {'sample_index': int(row['sample_index']), 'coordinate': row['coordinate'],
            'signed_difference': row[column], 'absolute_difference': abs(row[column])}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('results', type=Path)
    parser.add_argument('audit', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    assert not args.output.exists()
    audit = json.loads(args.audit.read_text())
    summary = json.loads((args.results / 'SUMMARY.json').read_text())
    assert audit['verdict'] in ['ADMIT_T1_TWO_CASE_NATIVE_HISTORY_AND_SAMPLED_D01_ONLY',
                                'ADMIT_DURABLE_COMMON_PREFIX_D01_ONLY']
    assert audit['comparison_summary_sha256'] == sha(args.results / 'SUMMARY.json')
    lock_path = REPO / 'research/rei_axbi_owner_loop_20261115/ORIGINAL_SCENARIO_LOCK.json'
    lock = json.loads(lock_path.read_text())
    target = lock['pre_run_accuracy']['empirical_full_history_fraction_absolute_target']
    paired_target = lock['pre_run_accuracy']['paired_numerical_target_fraction']
    assert target == .001 and paired_target == .1
    modes = {}
    for mode in ['fixed_a', 'fixed_t']:
        path = args.results / ('comparison_' + mode + '.csv.gz')
        assert audit['mode_checks'][mode]['CSV_sha256'] == sha(path)
        with gzip.open(path, 'rt') as stream:
            rows = [{k: float(v) for k, v in row.items()} for row in csv.DictReader(stream)]
        fields = {}
        for field in FIELDS:
            reported = summary['modes'][mode]['observables'][field]
            floor = reported['original_response_floor']
            above = [r for r in rows if abs(r[field + '_response_T1']) >= floor]
            exceed = [r for r in above if abs(r[field + '_D01_pair']) >
                      paired_target * abs(r[field + '_response_T1'])]
            pair_peak = maximum(rows, field + '_D01_pair')
            row = rows[pair_peak['sample_index']]
            states = {}
            for case in ['ZERO', 'PLUS']:
                column = field + '_D01_' + case
                states[case] = maximum(rows, column)
                if field in FRACTIONS:
                    states[case]['samples_above_original_fraction_variation_scale'] = sum(
                        abs(r[column]) > target for r in rows)
                    states[case]['sampled_max_over_original_fraction_variation_scale'] = (
                        states[case]['absolute_difference'] / target)
            status = ('NO_ABOVE_FLOOR_T1_SAMPLES' if not above else
                      'TWO_LEVEL_CHANGE_EXCEEDS_PAIRED_TARGET' if exceed else
                      'TWO_LEVEL_CHANGE_BELOW_PAIRED_TARGET_ON_REPRESENTED_ABOVE_FLOOR_SAMPLES')
            fields[field] = {
                'individual_state_changes': states, 'paired_change_peak': pair_peak,
                'at_paired_change_peak': {suffix: row[field + '_' + suffix] for suffix in
                                        ['response_T0', 'response_T1', 'D01_ZERO', 'D01_PLUS']},
                'original_response_floor': floor, 'T1_samples_above_floor': len(above),
                'above_floor_samples_exceeding_original_paired_change_scale': len(exceed),
                'two_level_variation_status': status,
                'accuracy_or_detection_admission': 'UNRESOLVED_PENDING_APPLICABLE_THREE_LEVEL_EVIDENCE',
            }
        modes[mode] = {'sample_count': len(rows), 'observables': fields}
    result = {
        'schema': 'REI_AX11_T1_OWNER_CONSUMPTION_V1',
        'goal': 'REI-AXBI-GOAL-20261014',
        'scenario': 'PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1',
        'named_owner_consumer': 'rei_bianchi scientific admission owner / AX11',
        'data_admission': audit['verdict'],
        'baseline_admission_preserved': 'PASS_SCOPED_CONDITIONAL_FIVE_CASE_BASELINE',
        'baseline_source_pin': summary['baseline_source_pin'],
        'original_fraction_variation_scale': target,
        'original_paired_change_scale_fraction': paired_target,
        'modes': modes,
        'milestones': summary['milestones'],
        'upward_crossing_counts': summary['upward_crossing_counts'],
        'error_assignment': 'D01 is the observed two-level variation. Neither level is assigned the true error from D01 alone.',
        'sampling_scope': 'Original1001 queries when represented; maxima refer to saved common samples, not a continuous supremum.',
        'next_physical_obligation': 'Native full-IC T2 ZERO/PLUS paired D12 under a separately bound finite allocation; retain separated energy and angular obligations.',
        'new_execution_authorized_by_this_record': False,
        'other_required_observables': 'Raw histories and all scientific outputs remain preserved. This consumer quantifies seven gas observables and crossings; remaining original observables stay open for full AX11.',
        'review_provenance': audit['review_provenance'],
        'audit_sha256': sha(args.audit),
        'summary_sha256': sha(args.results / 'SUMMARY.json'),
        'original_scenario_lock_sha256': sha(lock_path),
        'script_sha256': sha(Path(__file__)),
        'full_AX11_complete': False, 'new_completed_nodes': 0,
        'original_DAG': '10/17', 'expansion_DAG': '28/88',
    }
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'data_admission': result['data_admission'],
                      'original_DAG': '10/17', 'expansion_DAG': '28/88'}))


if __name__ == '__main__':
    main()
