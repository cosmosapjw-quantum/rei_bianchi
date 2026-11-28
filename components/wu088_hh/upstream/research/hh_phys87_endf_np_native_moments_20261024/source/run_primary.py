#!/usr/bin/env python3
"""Create exactly one complete PHYS87 primary record; --resume is read-only reuse.

Only the leased, explicitly dispatched primary is allowed to call run_primary.
Resume performs byte identities/output hashes before any numerical import.
"""
from pathlib import Path
import argparse
import csv
import datetime
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback

sys.dont_write_bytecode = True
UNIT = Path(__file__).resolve().parents[1]
CONTRACT_SHA = '464df6f83a7ac8bd64813dc9da3ca34f19398a2f970f3d69c706e3d089f6fd38'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        while data := f.read(256*1024):
            h.update(data)
    return h.hexdigest()


def identity():
    paths = [UNIT/'CONTRACT.json', UNIT/'theory/NATIVE_FINITE_T_MOMENTS_KO.md',
             UNIT/'source_data/n-001_H_001.endf', UNIT/'source_data/SOURCE_TABLE.json']
    paths += sorted((UNIT/'source').rglob('*.py'))
    if sha(UNIT/'CONTRACT.json') != CONTRACT_SHA:
        raise ValueError('FROZEN_CONTRACT_REVISION2_MISMATCH')
    descriptor = {'schema': 'PHYS87_PRIMARY_FROZEN_DEPENDENCIES_V1',
                  'files': {str(p.relative_to(UNIT)): {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in paths},
                  'integration_plan': '4T x16/32 full +4 FD scalar order32; no other thermal integrals',
                  'source_native_finite_window': True}
    canonical = json.dumps(descriptor, sort_keys=True, separators=(',', ':')).encode()
    return {'descriptor': descriptor, 'sha256': hashlib.sha256(canonical).hexdigest()}


def write_json(path, obj):
    with Path(path).open('x') as f:
        json.dump(obj, f, indent=2, allow_nan=False); f.write('\n')


def file_record(path):
    return {'filename': Path(path).name, 'bytes': Path(path).stat().st_size, 'sha256': sha(path)}


def resume(output, binding):
    manifest = json.loads((output/'OUTPUT_MANIFEST.json').read_text())
    result = json.loads((output/'RESULT.json').read_text())
    if manifest['frozen_identity'] != binding or result['frozen_identity'] != binding:
        raise ValueError('RESUME_FROZEN_IDENTITY_MISMATCH')
    if result['status'] != 'PRIMARY_COMPLETED_AWAITING_INDEPENDENT_REVIEW':
        raise ValueError('RESUME_REQUIRES_COMPLETE_PASSED_PRIMARY')
    if not manifest['files']:
        raise ValueError('RESUME_OUTPUT_MANIFEST_EMPTY')
    for record in manifest['files']:
        filename = record['filename']
        if Path(filename).name != filename or filename == 'OUTPUT_MANIFEST.json':
            raise ValueError('INVALID_OUTPUT_MANIFEST_ENTRY')
        if file_record(output/filename) != record:
            raise ValueError('RESUME_COMPLETED_OUTPUT_BYTES_MISMATCH:'+filename)
    return {'status': 'SKIP', 'scientific_callbacks': 0, 'thermal_integrations': 0,
            'old_science_replays': 0, 'files_rewritten': 0, 'result_path': str(output/'RESULT.json'),
            'frozen_identity_sha256': binding['sha256']}


def run_primary(output, binding, state):
    from native_moments import (NativeSource, NativeThermalIntegrator, conditional_angular_case,
        owner_row, source_kinematics, temperature, DomainError, SOURCE_NATIVE, ROUTES)
    import numpy as np
    contract = json.loads((UNIT/'CONTRACT.json').read_text())
    criteria = contract['acceptance']; checks = []; guard_rows = []
    def check(label, passed, observed=None, criterion=None):
        checks.append({'label': label, 'pass': bool(passed), 'observed': observed, 'criterion': criterion})
    def reject(label, call):
        try:
            call()
            record = {'label': label, 'rejected': False, 'exception': None}
        except DomainError as exc:
            record = {'label': label, 'rejected': True, 'exception': type(exc).__name__, 'reason': str(exc)}
        except Exception as exc:
            record = {'label': label, 'rejected': False, 'exception': type(exc).__name__, 'reason': str(exc)}
        guard_rows.append(record); check('guard:'+label, record['rejected'], record)
    source = NativeSource(UNIT/'source_data/n-001_H_001.endf', UNIT/'source_data/SOURCE_TABLE.json')
    positivity = source.positivity_witness()
    check('source_exact_row_count', len(source.rows) == contract['source']['MF3_MT102_points'], len(source.rows), 153)
    check('exact_153_quadratic_minima_positive', len(positivity['knots']) == 153,
          {'knots': len(positivity['knots']), 'cells': len(positivity['cells'])}, 'strict exact Fraction minima >0')
    integrator = NativeThermalIntegrator(source); state['integrator'] = integrator
    knot_sigma, knot_a1, knot_a2 = source.evaluate(source.energies)
    knot_exact = (np.array_equal(knot_sigma, np.asarray(source.sigma_values)) and
                  np.array_equal(knot_a1, np.asarray(source.a1_values)) and
                  np.array_equal(knot_a2, np.asarray(source.a2_values)))
    check('source_knots_exact', knot_exact, bool(knot_exact), criteria['source_knots_exact'])
    full = []
    for t in contract['physical_model']['primary_T_K']:
        for order in (16, 32):
            full.append(integrator.integrate(t, order))
    comparisons = []
    for t in contract['physical_model']['primary_T_K']:
        a = next(r for r in full if r['T_K'] == t and r['order'] == 16)
        b = next(r for r in full if r['T_K'] == t and r['order'] == 32)
        relative = {key: abs(a[key]-b[key])/abs(b[key]) for key in
                    ('kappa_cm3_per_s', 'mean_Kin_eV', 'mean_Egamma_eV', 'mean_Kd_eV')}
        comparisons.append({'T_K': t, 'relative_16_vs32': relative})
        for key, value in relative.items():
            check('quadrature:'+str(t)+':'+key, value <= criteria['quadrature_relative_rate_and_means'], value,
                  criteria['quadrature_relative_rate_and_means'])
    angular = []
    for energy in contract['numerical_plan']['conditional_angular_cases']['E_lab_eV']:
        for beta in contract['numerical_plan']['conditional_angular_cases']['boost_beta']:
            for axis in contract['numerical_plan']['conditional_angular_cases']['c_axis']:
                row = conditional_angular_case(source, energy, beta, axis); angular.append(row)
                name = 'angular:'+str(energy)+':'+str(beta)+':'+str(axis)
                check(name+':polynomial_moments', row['maximum_scaled_residual'] <= criteria['angular_relative_or_scaled_tolerance'],
                      row['maximum_scaled_residual'], criteria['angular_relative_or_scaled_tolerance'])
                check(name+':event_energy', row['maximum_event_closure_abs_eV'] <= criteria['energy_closure_abs_eV'],
                      row['maximum_event_closure_abs_eV'], criteria['energy_closure_abs_eV'])
    owner_rows = []
    for row in full:
        check('mean_energy_closure:'+str(row['T_K'])+':'+str(row['order']),
              abs(row['energy_identity_residual_eV']) <= criteria['energy_closure_abs_eV'],
              row['energy_identity_residual_eV'], criteria['energy_closure_abs_eV'])
        check('centered_variance_positive:'+str(row['T_K'])+':'+str(row['order']),
              all(row[k] > 0 for k in ('variance_Kin_eV2', 'variance_Egamma_eV2', 'variance_Kd_eV2')),
              {k: row[k] for k in ('variance_Kin_eV2', 'variance_Egamma_eV2', 'variance_Kd_eV2')}, 'strict >0')
        if row['order'] != 32:
            continue
        for h in (0, 1):
            for route in ROUTES:
                owned = owner_row(row, h, route); owner_rows.append(owned)
                label = 'owner:'+str(row['T_K'])+':'+str(h)+':'+route
                check(label+':energy', abs(owned['energy_closure_eV']) <= criteria['energy_closure_abs_eV'],
                      owned['energy_closure_eV'], criteria['energy_closure_abs_eV'])
                counts = owned['count_columns']
                check(label+':counts', counts['thermal']+counts['fast']+1 == 0 and counts['free_electron'] == 0,
                      counts, 'one capture, no free-electron incidence')
                radiation = owned['energy_columns_eV']
                check(label+':exclusive_radiation',
                      (radiation['radiation_injected'] == 0) != (radiation['radiation_escape'] == 0),
                      [radiation['radiation_injected'], radiation['radiation_escape']], 'exactly one owned photon column')
    fd_rates, fd_comparisons = [], []
    step = 2**-8
    for t in (10000.0, 100000000.0):
        low = integrator.integrate(t*math.exp(-step), 32, rate_only=True)
        high = integrator.integrate(t*math.exp(step), 32, rate_only=True)
        fd_rates += [low, high]
        fd = math.log(high['kappa_cm3_per_s']/low['kappa_cm3_per_s'])/(2*step)
        native = next(r for r in full if r['T_K'] == t and r['order'] == 32)['selected_log_rate_slope']
        residual = fd-native
        fd_comparisons.append({'T_K': t, 'hlog': step, 'FD_log_rate_slope': fd,
                               'selected_energy_log_rate_slope': native, 'residual': residual})
        check('FD_log_rate_slope:'+str(t), abs(residual) <= criteria['FD_log_rate_slope_abs'],
              residual, criteria['FD_log_rate_slope_abs'])
    adopted = next(r for r in full if r['T_K'] == 10000 and r['order'] == 32)
    reject('energy_below_support', lambda: source.evaluate([1e-6]))
    reject('energy_above_support', lambda: source.evaluate([20000001.0]))
    reject('energy_nan', lambda: source.evaluate([math.nan]))
    reject('energy_inf', lambda: source.evaluate([math.inf]))
    reject('T_below_frozen_domain', lambda: temperature(254.0))
    reject('T_above_frozen_domain', lambda: temperature(101000001.0))
    reject('T_nan', lambda: temperature(math.nan))
    reject('T_inf', lambda: temperature(math.inf))
    reject('T_bool', lambda: temperature(True))
    reject('bare_source_network', lambda: source.evaluate([1.0], 'BARE_NUCLEAR_NETWORK'))
    reject('bare_kinematic_network', lambda: source_kinematics([1.0], 'BARE_NUCLEAR_NETWORK'))
    reject('bare_owner_network', lambda: owner_row(adopted, 0, ROUTES[0], 'BARE_NUCLEAR_NETWORK'))
    reject('owner_two', lambda: owner_row(adopted, 2, ROUTES[0]))
    reject('owner_fraction', lambda: owner_row(adopted, 0.5, ROUTES[0]))
    reject('owner_bool', lambda: owner_row(adopted, True, ROUTES[0]))
    reject('conflicting_radiation', lambda: owner_row(adopted, 0, 'both'))
    reject('mu_outside_domain', lambda: source.angular_pdf(1.0, 2.0))
    reject('mu_nonfinite', lambda: source.angular_pdf(1.0, math.nan))
    reject('negative_boost', lambda: conditional_angular_case(source, 1.0, -0.1, 0.0))
    reject('superluminal_boost', lambda: conditional_angular_case(source, 1.0, 1.0, 0.0))
    reject('axis_outside_domain', lambda: conditional_angular_case(source, 1.0, 0.2, 2.0))
    reject('integration_invalid_order', lambda: integrator.integrate(10000.0, 17))
    reject('integration_invalid_T', lambda: integrator.integrate(0.0, 32))
    reject('integration_bare_network', lambda: integrator.integrate(10000.0, 32, convention='BARE_NUCLEAR_NETWORK'))
    check('campaign_exact_planned_integration_counts',
          len(integrator.integration_calls) == 12 and len(full) == 8 and len(fd_rates) == 4,
          {'total': len(integrator.integration_calls), 'full': len(full), 'FD_scalar': len(fd_rates)},
          'contract8full+4FDscalar; no unplanned integrations')
    check('campaign_conditional_and_owner_counts', len(angular) == 18 and len(owner_rows) == 16,
          {'conditional_cases': len(angular), 'adopted_owner_rows': len(owner_rows)}, '18conditional/16adopted-owner')
    failed = [c for c in checks if not c['pass']]
    report = {'schema': 'PHYS87_SOURCE_NATIVE_FINITE_WINDOW_PRIMARY_V1',
              'status': 'PRIMARY_COMPLETED_AWAITING_INDEPENDENT_REVIEW' if not failed else 'PRIMARY_COMPLETED_CHECK_FAILURE',
              'frozen_identity': binding,
              'scope': 'Source-native evaluated n+atomic-H1 finite source-window moments; no tail/continuum/uncertainty or consumer admission',
              'thermal_results': full, 'owner_rows': owner_rows, 'angular_cases': angular,
              'quadrature_comparisons': comparisons, 'finite_difference_rates': fd_rates,
              'finite_difference_comparisons': fd_comparisons,
              'bessel_exact_coefficients': integrator.bessel.exact_coefficient_record(),
              'source_native_knots': [{'En_eV': str(r.energy), 'sigma_barn': str(r.sigma), 'a1': str(r.a1), 'a2': str(r.a2)} for r in source.rows],
              'checks': checks, 'failures': failed, 'guard_controls': guard_rows,
              'counts': {'thermal_integrations': len(integrator.integration_calls), 'full_moment_integrations': len(full),
                         'FD_scalar_integrations': len(fd_rates), 'native_intervals_per_integral': 152,
                         'source_knots': len(source.rows), 'exact_positive_knots': len(positivity['knots']),
                         'convex_interpolation_cells': len(positivity['cells']), 'angular_cases': len(angular),
                         'adopted_owner_rows': len(owner_rows), 'guards': len(guard_rows),
                         'assertions': len(checks), 'passed_assertions': sum(c['pass'] for c in checks)},
              'integration_call_ledger': integrator.integration_calls,
              'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'platform': platform.platform(),
                          'affinity_cpus': sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None},
              'resource_cost': 'Actual hard caps, child CPU/wall and lease observations belong to outer leased attempt receipt',
              'old_PHYS85_86_callbacks': 0, 'new_ODE': 0, 'network_rate_activation': 0, 'fast_stopping': 0,
              'source_covariance_propagated': False, 'physical_CI': False,
              'HH_R10': 'OFF', 'production_admission': 'NOT_ISSUED', 'scientific_admission': 'PENDING_ROOT_AND_INDEPENDENT_RAW_REVIEW'}
    write_json(output/'POSITIVITY_WITNESS.json', positivity)
    write_json(output/'RESULT.json', report)
    with (output/'THERMAL_MOMENTS.csv').open('x', newline='') as f:
        fields = ['T_K', 'order', 'kappa_cm3_per_s', 'mean_Kin_eV', 'mean_Egamma_eV', 'mean_Kd_eV',
                  'variance_Kin_eV2', 'variance_Egamma_eV2', 'variance_Kd_eV2', 'selected_log_rate_slope',
                  'energy_identity_residual_eV', 'underflowed_boltzmann_points']
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); writer.writeheader(); writer.writerows(full)
    with (output/'OWNER_ROWS.csv').open('x', newline='') as f:
        fields = ['T_K', 'order', 'h', 'radiation_route', 'thermal', 'fast', 'nuclear_rest', 'atomic_binding',
                  'radiation_injected', 'radiation_escape', 'energy_closure_eV', 'Cv_Tdot_over_R_eV']
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for row in owner_rows:
            writer.writerow({k: v for k, v in {**row, **row['energy_columns_eV']}.items() if k in fields})
    with (output/'ANGULAR_CASES.csv').open('x', newline='') as f:
        fields = ['E_lab_eV', 'boost_beta', 'c_axis', 'a1', 'a2', 'mean_nu', 'second_nu', 'mean_Egamma_eV',
                  'mean_Kd_eV', 'variance_Egamma_eV2', 'maximum_scaled_residual', 'maximum_event_closure_abs_eV']
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); writer.writeheader(); writer.writerows(angular)
    write_json(output/'OUTPUT_MANIFEST.json', {'schema': 'PHYS87_COMPLETE_PRIMARY_OUTPUT_BYTES_V1',
               'frozen_identity': binding, 'files': [file_record(p) for p in sorted(output.iterdir()) if p.is_file()],
               'self_exclusion': 'OUTPUT_MANIFEST excludes its own bytes; verifies every prior immutable output'})
    return {'status': report['status'], 'counts': report['counts'], 'result_sha256': sha(output/'RESULT.json'),
            'result_path': str(output/'RESULT.json'), 'scientific_admission': report['scientific_admission']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args(); output = args.output.resolve()
    binding = identity()
    if args.resume:
        print(json.dumps(resume(output, binding))); return 0
    output.mkdir(parents=True, exist_ok=False)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    write_json(output/'ATTEMPT.json', {'schema': 'PHYS87_CREATE_ONLY_PRIMARY_ATTEMPT_V1',
               'started_utc': started, 'frozen_identity': binding,
               'count_limit': {'thermal_integrations': 12}, 'automatic_retry': 0})
    state = {}
    try:
        receipt = run_primary(output, binding, state)
        print(json.dumps(receipt, allow_nan=False))
        return 0 if receipt['status'] == 'PRIMARY_COMPLETED_AWAITING_INDEPENDENT_REVIEW' else 1
    except BaseException as exc:
        failure = {'schema': 'PHYS87_PRIMARY_FAILURE_PRESERVED_V1', 'status': 'FAILED_FIRST_ATTEMPT_PRESERVED',
                   'exception': type(exc).__name__, 'reason': str(exc), 'traceback': traceback.format_exc(),
                   'frozen_identity': binding, 'started_utc': started,
                   'integration_calls': state['integrator'].integration_calls if 'integrator' in state else [],
                   'automatic_retries': 0, 'scientific_admission': 'NOT_ISSUED'}
        write_json(output/'FAILURE.json', failure)
        print(json.dumps({'status': failure['status'], 'exception': type(exc).__name__, 'reason': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
