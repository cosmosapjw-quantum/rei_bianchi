#!/usr/bin/env python3
"""Mechanical saved-array audit. No Hamiltonian/solver or external calls."""
import argparse
import datetime
import importlib.util
import json
from pathlib import Path

import numpy as np


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def complex_value(value):
    return {'real': float(np.real(value)), 'imag': float(np.imag(value))}


def archive_values(attempt):
    receipt = json.loads((attempt / 'receipt.json').read_text())
    with (attempt / 'data.npz').open('rb') as f, np.load(f, allow_pickle=False) as data:
        ci, cf, q = data['CI_parent'], data['CI_daughter_ground'], data['CI_complement']
        A = np.vdot(cf, ci)
        p, complement = float(abs(A) ** 2), float(np.vdot(q, q).real)
        values = {
            'CI_parent_norm2': complex_value(np.vdot(ci, ci)),
            'CI_daughter_norm2': complex_value(np.vdot(cf, cf)),
            'parent_norm_error': float(abs(np.vdot(ci, ci) - 1)),
            'daughter_norm_error': float(abs(np.vdot(cf, cf) - 1)),
            'rdm1_parent_trace': complex_value(np.trace(data['rdm1_parent'])),
            'rdm1_daughter_trace': complex_value(np.trace(data['rdm1_daughter'])),
            'parent_rdm_trace_error': float(abs(np.trace(data['rdm1_parent']) - 3)),
            'daughter_rdm_trace_error': float(abs(np.trace(data['rdm1_daughter']) - 3)),
            'A_ground': complex_value(A), 'P_ground': p,
            'complement_norm2': complement,
            'q_identity_error_l2': float(np.linalg.norm(q - (ci - A * cf))),
            'q_daughter_overlap_abs': float(abs(np.vdot(cf, q))),
            'closure_error': abs(p + complement - 1),
            'receipt_P_difference': abs(p - receipt['P_ground']),
            'receipt_A_real_difference': abs(float(A.real) - receipt['A_ground_real']),
            'receipt_complement_difference': abs(complement - receipt['unresolved_excitation_including_bound_probability']),
            'arrays': {key: {'shape': list(data[key].shape), 'dtype': str(data[key].dtype),
                             'finite': bool(np.all(np.isfinite(data[key])))} for key in data.files},
        }
    moments = {key: receipt[key] for key in ('daughter_energy_mean_Eh',
               'daughter_energy_second_moment_Eh2', 'daughter_energy_variance_Eh2') if key in receipt}
    if all(key in moments for key in ('daughter_energy_mean_Eh', 'daughter_energy_second_moment_Eh2', 'daughter_energy_variance_Eh2')):
        moments['variance_arithmetic_difference_Eh2'] = (
            moments['daughter_energy_second_moment_Eh2'] - moments['daughter_energy_mean_Eh'] ** 2
            - moments['daughter_energy_variance_Eh2'])
    return {
        'path': str(attempt), 'case_id': receipt['case']['id'], 'case': receipt['case'],
        'receipt_status': receipt['status'],
        'receipt_finite_model_numerics_passed': receipt['finite_model_numerics_passed'],
        'receipt_retained_rank': receipt.get('retained_ao_rank'),
        'receipt_parent_energy_Eh': receipt.get('parent', {}).get('E_BO_Eh'),
        'receipt_daughter_energy_Eh': receipt.get('daughter', {}).get('E_BO_Eh'),
        'receipt_parent_checks': receipt.get('parent', {}).get('checks'),
        'receipt_daughter_checks': receipt.get('daughter', {}).get('checks'),
        'receipt_moments_diagnostics_only': moments,
        'saved_array_recomputation': values,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit3', type=Path, required=True)
    parser.add_argument('--unit2', type=Path, required=True)
    parser.add_argument('--collector-code', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location('frozen_c10_collector', args.collector_code)
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    source = args.unit2 / 'code/microphysics_driver_v6.py'
    contract = args.unit2 / 'CONTRACT_MICROPHYSICS_V6_THREEE.json'
    target = args.unit3 / 'attempts/000'
    gates = collector.validate(target / 'receipt.json', target / 'input.json', source, contract)
    write(args.out / 'C10_FROZEN_GATE_VALIDATION.json', gates)
    target_values = archive_values(target)
    write(args.out / 'AUG_TZ_SAVED_ARRAY_AUDIT.json', target_values)
    old = []
    for case_id in ('quench_Li_Be_union_DZ', 'quench_Li_Be_union_aug_DZ'):
        attempt = args.unit2 / 'ncp_results/runs/extension_v4' / case_id
        values = archive_values(attempt)
        values['data_sha256_observed'] = collector.sha(attempt / 'data.npz')
        values['receipt_sha256_observed'] = collector.sha(attempt / 'receipt.json')
        old.append(values)
    write(args.out / 'PREVIOUS_DZ_AUGDZ_SAVED_ARRAY_AUDIT.json', old)
    current_p = target_values['saved_array_recomputation']['P_ground']
    comparisons = []
    for previous in old:
        old_p = previous['saved_array_recomputation']['P_ground']
        comparisons.append({'previous_case': previous['case_id'], 'previous_P': old_p,
                            'aug_TZ_P': current_p, 'aug_TZ_minus_previous_P': current_p - old_p,
                            'absolute_delta_P': abs(current_p - old_p),
                            'relative_delta_P': (current_p - old_p) / old_p,
                            'claim': 'descriptive basis comparison only; no new convergence tolerance or admission'})
    write(args.out / 'BASIS_PROBABILITY_COMPARISON.json', comparisons)
    summary = {
        'observed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'mechanical local intake; no NCP connection, solver replay, or Hamiltonian action',
        'source_sha256': collector.sha(source), 'contract_sha256': collector.sha(contract),
        'receipt_sha256': collector.sha(target / 'receipt.json'),
        'data_sha256': collector.sha(target / 'data.npz'),
        'frozen_gate_count': len(gates['gates']),
        'frozen_gate_failures': [gate for gate in gates['gates'] if not gate['pass']],
        'frozen_gate_check_passed': gates['passed'],
        'saved_array_values': target_values['saved_array_recomputation'],
        'recorded_moment_diagnostics': target_values['receipt_moments_diagnostics_only'],
        'basis_probability_comparisons': comparisons,
        'recorded_NCP_inspection': json.loads((args.unit3 / 'inspection.json').read_text())['runtime_class'],
        'local_NCP_runtime_reinspection': 'not performed',
        'original_H_residual': 'recorded solver gate only; not independently recomputed without integrals',
        'AO_metric_orthogonality': 'recorded solver gate only; not independently recomputed without AO metric',
        'scientific_admission': 'Astra/root decision; no expanded physical claim',
    }
    write(args.out / 'NUMERICAL_INTAKE_SUMMARY.json', summary)
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False))
    return 0 if gates['passed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
