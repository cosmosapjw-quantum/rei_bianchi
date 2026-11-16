#!/usr/bin/env python3
"""Same-author adversarial semantic audit of actual exported T1 comparisons.

Uses CSV definitions and nuclei/charge identities directly, without importing
the producer, its interpolation routines, or its numerical summary functions.
This is not represented as an independent blind referee.
"""
import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

FHE = .2454 / (4 * (1 - .2454))
FIELDS = ['x_HI', 'x_HII', 'x_HeI', 'x_HeII', 'x_HeIII', 'xe_per_H', 'temperature_K']
UNIT = Path(__file__).resolve().parents[1]


def require(value, message):
    if not value:
        raise AssertionError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('results', type=Path)
    parser.add_argument('native_input', type=Path)
    parser.add_argument('closed_native_ledger', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    require(not args.output.exists(), 'OUTPUT_ALREADY_EXISTS')
    summary = json.loads((args.results / 'SUMMARY.json').read_text())
    native = json.loads(args.closed_native_ledger.read_text())
    extraction = json.loads((args.native_input / 'EXTRACTION_RECEIPT.json').read_text())
    grid = json.loads((UNIT / 'inputs/SAMPLING_GRID.json').read_text())
    require(native['status'] == 'T1_WAVE_FINISHED_WITH_RETAINED_OUTCOMES', 'UNCLOSED_NATIVE_LEDGER')
    require(summary['full_AX11_complete'] is False and summary['observed_order'] is None,
            'UNSUPPORTED_GLOBAL_CLAIM')
    mode_checks = {}
    for mode in ['fixed_a', 'fixed_t']:
        with gzip.open(args.results / f'comparison_{mode}.csv.gz', 'rt') as stream:
            rows = list(csv.DictReader(stream))
        require(len(rows) == summary['modes'][mode]['rows'], 'SAMPLE_COUNT')
        residuals = {}
        clock_max = 0.
        for i, text in enumerate(rows):
            row = {k: float(v) for k, v in text.items()}
            require(all(math.isfinite(v) for v in row.values()), 'NONFINITE_RESULT')
            require(row['sample_index'] == i, 'NONCANONICAL_SAMPLE_ORDER')
            if mode == 'fixed_a':
                require(row['T1_ZERO_a'] == row['T1_PLUS_a'], 'FIXED_A_MISMATCH')
            else:
                require(row['elapsed_time_s'] == grid['fixed_t'][i]['elapsed_time_s'],
                        'WRONG_REQUESTED_PROPER_TIME')
                clock_max = max(clock_max, abs(row['T1_ZERO_time_s'] - row['elapsed_time_s']),
                                abs(row['T1_PLUS_time_s'] - row['elapsed_time_s']))
            for field in FIELDS:
                for case in ['ZERO', 'PLUS']:
                    require(row[f'{field}_D01_{case}'] ==
                            row[f'{field}_T1_{case}'] - row[f'{field}_T0_{case}'], 'WRONG_STATE_DIFFERENCE')
                for k in [0, 1]:
                    require(row[f'{field}_response_T{k}'] ==
                            row[f'{field}_T{k}_PLUS'] - row[f'{field}_T{k}_ZERO'], 'WRONG_RESPONSE')
                require(row[field + '_D01_pair'] ==
                        row[field + '_response_T1'] - row[field + '_response_T0'], 'WRONG_PAIRED_DIFFERENCE')
            for suffix in ['T0_ZERO', 'T0_PLUS', 'T1_ZERO', 'T1_PLUS',
                           'D01_ZERO', 'D01_PLUS', 'response_T0', 'response_T1', 'D01_pair']:
                total = 1. if suffix.startswith(('T0_', 'T1_')) else 0.
                hi, hii, hei, heii, heiii, xe = [row[field + '_' + suffix] for field in FIELDS[:6]]
                values = {'H': abs(hi + hii - total), 'He': abs(hei + heii + heiii - total),
                          'charge': abs(xe - hii - FHE * (heii + 2 * heiii))}
                for name, value in values.items():
                    key = suffix + '_' + name
                    residuals[key] = max(residuals.get(key, 0.), value)
                    require(value <= 1e-12, 'NUCLEI_OR_CHARGE_IDENTITY:' + key)
        for field in FIELDS:
            reported = summary['modes'][mode]['observables'][field]
            for suffix in ['D01_ZERO', 'D01_PLUS', 'D01_pair', 'response_T0', 'response_T1']:
                maximum = max(abs(float(row[field + '_' + suffix])) for row in rows)
                require(maximum == reported[suffix]['sampled_max_abs'], 'WRONG_REPORTED_MAXIMUM')
        mode_checks[mode] = {'sample_count': len(rows), 'maximum_constraint_residuals': residuals,
                             'maximum_sampled_clock_roundtrip_residual_s': clock_max,
                             'clock_roundtrip_scope': 'Diagnostic of t -> ln(a) -> t binary64 interpolation; requested times are exact pinned coordinates, and this residual is not an evolution error bound.',
                             'CSV_sha256': sha(args.results / f'comparison_{mode}.csv.gz')}
    cases = {}
    for item in extraction['cases']:
        case = item['case']
        records = [r for r in native['records'] if r.get('name', '').startswith(case + '_segment_')]
        require(records and all(r['status'] == 'FINISHED' for r in records), 'UNFINISHED_CASE_RECORD')
        accepted = sum(r.get('accepted', 0) for r in records)
        require(accepted + 1 == item['composed_rows'], 'COUNT_RESET_OR_DUPLICATE_COMPOSITION')
        require(max(item['residuals'].values()) <= 1e-12, 'RAW_STATE_CONSTRAINT')
        for r in records:
            require(r['source_sha256'] == '57a2c412c70295cbce9db88b92fe2d716fa904997ba07dbed23ae555bfa03eed',
                    'SOURCE_IDENTITY_MISMATCH')
            metric = r['summary']['maximum_accepted_local_metric_this_segment']
            require(metric is None or metric <= 2.5e-6, 'LOCAL_TARGET_BREACH')
        endpoint = bool(item['endpoint_reached'])
        if endpoint:
            require(records[-1]['returncode'] == 0 and records[-1]['summary']['a_end'] == .2,
                    'FALSE_NATIVE_ENDPOINT')
        cases[case] = {'native_endpoint_reached': endpoint, 'accepted': accepted,
                       'segments': len(records), 'CPU_s': sum(r['CPU_s'] for r in records),
                       'process_wall_s': sum(r['wall_s'] for r in records)}
    require(set(cases) == {'ZERO', 'PLUS'}, 'MISSING_OWNER_CASE')
    counts = native['current_allocation_debit']
    limits = json.loads((UNIT / 'ALLOCATION.json').read_text())['caps']
    for key, cap in [('accepted', 'aggregate_accepted'), ('trials', 'aggregate_trials'),
                     ('RHS', 'aggregate_RHS'), ('CPU_s', 'aggregate_CPU_s'),
                     ('wall_s', 'aggregate_sum_job_wall_s')]:
        require(counts[key] <= limits[cap], 'ALLOCATION_BREACH:' + key)
    require('UNKNOWN' in native['historical_accumulated_cost'], 'UNKNOWN_COST_ERASED')
    all_endpoints = all(value['native_endpoint_reached'] for value in cases.values())
    verdict = 'ADMIT_T1_TWO_CASE_NATIVE_HISTORY_AND_SAMPLED_D01_ONLY' if all_endpoints else 'ADMIT_DURABLE_COMMON_PREFIX_D01_ONLY'
    result = {'verdict': verdict,
              'review_provenance': 'same-author adversarial semantic audit; not an independent blind referee',
              'mode_checks': mode_checks, 'cases': cases, 'native_debit': counts,
              'excluded_claims': ['D12', 'observed convergence order', 'certified evolution error bound',
                                  'continuous-domain supremum', 'full dt/dE/dmu gate',
                                  'full AX11 completion', 'AX12', 'five-case T1 refinement'],
              'interpretation_limits': ['Conservation alone does not bound thermal/ionization evolution error.',
                                        'Small paired D01 can conceal common-mode changes in both histories.',
                                        'T1 PCHIP differences are interpolation diagnostics, not additional evolved histories.'],
              'native_ledger_sha256': sha(args.closed_native_ledger),
              'comparison_summary_sha256': sha(args.results / 'SUMMARY.json'),
              'script_sha256': sha(Path(__file__)),
              'full_AX11_complete': False, 'new_completed_nodes': 0,
              'original_DAG': '10/17', 'expansion_DAG': '28/88'}
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'verdict': verdict, 'endpoint_count': sum(x['native_endpoint_reached'] for x in cases.values()),
                      'original_DAG': '10/17', 'expansion_DAG': '28/88'}))


if __name__ == '__main__':
    main()
