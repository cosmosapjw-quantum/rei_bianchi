#!/usr/bin/env python3
"""Audit newly saved E13C4 evidence; does not execute a scientific solver."""
from decimal import Decimal as D
from pathlib import Path
import hashlib
import json
import sys

from directed_interval import IV, configure
from local_enclosure import atomic_json, SPECIES


def main():
    root = Path(__file__).resolve().parents[1]
    configure(80)
    tests = []
    def check(key, ok, detail=None):
        tests.append({'id': key, 'pass': bool(ok), 'detail': detail})
    datasets = {}
    for n, p in [(32, 60), (128, 60), (512, 60), (32, 80)]:
        d = json.loads((root / f'evidence/N{n}_P{p}.json').read_text())
        datasets[(n, p)] = d
        name = f'N{n}_P{p}'
        check(name + '_six_controls', len(d['controls']) == 6)
        check(name + '_actual_exit', json.loads((root / f'evidence/run_n{n}_p{p}/RUN.json').read_text())['actual_exit'] == 0)
        check(name + '_saved_reference_compatibility', not d['compatibility_failures'])
        check(name + '_saved_candidate_containment', not d['saved_firstvariation_containment_failures'])
        check(name + '_unchanged_as_run', d['source_unchanged_during_run'])
        check(name + '_declared_runtime_budget', d['elapsed_seconds'] <= 180 and d['peak_RSS_KiB'] <= 1048576)
        for path, digest in d['identity']['source_sha256_before_run'].items():
            check(name + '_producer_' + path, hashlib.sha256((root / path).read_bytes()).hexdigest() == digest)
        for row in d['controls']:
            key = name + '_' + '/'.join(map(str, row['key']))
            check(key + '_entire_domain_checks', row['domain']['gas_checked_evaluations'] == 2 * n and row['domain']['positive_rate_evaluations'] == 2 * n)
            check(key + '_positive_heat_weight', D(row['domain']['active_heat_weight_min_eV']) >= 0)
            check(key + '_coefficient_call_coverage', row['cell_coverage']['coefficient_evaluations'] == 2 * n)
            intervals = {k: IV(v['lo'], v['hi']) for k, v in row['exact_firstvariation_integral_enclosures'].items()}
            check(key + '_number_ledger_inclusion', (intervals['P1'] + intervals['A_total'] - intervals['QN']).contains(0))
            check(key + '_energy_ledger_inclusion', (intervals['P1_energy_eV'] + intervals['B_total_eV'] + intervals['Z_eV'] - intervals['QE_eV']).contains(0))
            for k, active in zip(SPECIES, row['frozen']['mask']):
                if not active:
                    for prefix in ('A', 'B', 'H'):
                        label = prefix + '_' + k + ('_eV' if prefix != 'A' else '')
                        check(key + '_inactive_exact_zero_' + label, intervals[label].lo == intervals[label].hi == D(row['analytic_truncation_upper'][label]) == 0)
            for lane, values in row['saved_candidate_comparison'].items():
                for label, v in values.items():
                    floor = D('1e-24') if 'eV' in label else D('1e-25')
                    if D(v['saved_reference_value']).copy_abs() < floor:
                        check(key + '_' + lane + '_' + label + '_floor_semantics', v['full_bound_over_saved_defect_abs_upper'] is None and v['relative_defect_status'] == 'UNRESOLVED_BELOW_FLOOR')
    refinement = []
    for case in range(6):
        rows = [datasets[(n, 60)]['controls'][case] for n in (32, 128, 512)]
        label = '/'.join(map(str, rows[0]['key']))
        bounds = [D(r['saved_candidate_comparison']['saved_E13C3_primary_GL12']['H_total_eV']['certified_candidate_to_true_defect_upper']) for r in rows]
        check(label + '_heat_full_bound_narrows', bounds[0] > bounds[1] > bounds[2])
        for observable in rows[0]['exact_firstvariation_integral_enclosures']:
            a = datasets[(32, 60)]['controls'][case]['exact_firstvariation_integral_enclosures'][observable]
            b = datasets[(32, 80)]['controls'][case]['exact_firstvariation_integral_enclosures'][observable]
            check(label + '_' + observable + '_60_80_overlap', max(D(a['lo']), D(b['lo'])) <= min(D(a['hi']), D(b['hi'])))
        refinement.append({'key': rows[0]['key'], 'heat_full_error_bound': {str(n): str(x) for n, x in zip((32, 128, 512), bounds)}})
    final = datasets[(512, 60)]
    summary = []
    for row in final['controls']:
        v = row['saved_candidate_comparison']['saved_E13C3_primary_GL12']['H_total_eV']
        summary.append({'key': row['key'], 'saved_signed_heat_defect_eV': v['saved_reference_value'],
                        'analytic_truncation_upper_eV': v['certified_truncation_upper'],
                        'candidate_numerical_upper_eV': v['certified_candidate_to_exact_firstvariation_upper'],
                        'full_candidate_error_upper_eV': v['certified_candidate_to_true_defect_upper'],
                        'bound_over_saved_heat_defect_abs': v['full_bound_over_saved_defect_abs_upper'],
                        'truncation_sharpness_vs_saved_gap': v['truncation_bound_over_observed_gap_upper']})
    out = {'schema': 'bass-he-e13c4-saved-evidence-audit-v1', 'audit_role': 'OWNER_EVIDENCE_AUDIT_NOT_INDEPENDENT_DECISION',
           'new_scientific_runs_by_this_command': 0, 'old_solver_runs': 0,
           'checks': tests, 'passed': sum(x['pass'] for x in tests), 'failed': sum(not x['pass'] for x in tests),
           'refinement': refinement, 'heat_summary': summary,
           'precision_control_concurrency': 'N32P80 overlapped N128P60; all three P60 primary runs sequential; timings are not controlled speedup benchmarks',
           'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    atomic_json(root / 'evidence/ACCEPTANCE.json', out)
    print(json.dumps({'passed': out['passed'], 'failed': out['failed'], 'new_scientific_runs': 0}))
    return 0 if out['failed'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
