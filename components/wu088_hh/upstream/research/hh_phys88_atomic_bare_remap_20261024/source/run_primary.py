#!/usr/bin/env python3
"""PHYS88 create-only primary; --resume checks saved identity without science."""
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
import traceback

sys.dont_write_bytecode = True
UNIT = Path(__file__).resolve().parents[1]
CONTRACT_SHA = '8f45d6a70d7cf7ffcc556b74636f25087167a3372f781eee4078f5dd00e4154d'
DEPENDENCIES = ['CONTRACT.json', 'theory/ATOMIC_BARE_REMAP_KO.md',
    'theory/POSITIVE_BRANCH_CLOSURE_KO.md', 'source_data/SOURCE_CONTRACT.json',
    'source_data/n-001_H_001.endf', 'source_data/SOURCE_TABLE.json',
    'source_data/PHYS85_FROZEN_INPUTS.json', 'source_data/PHYS87_POSITIVITY_WITNESS.json',
    'source_data/PHYS87_RESULT_BASELINE.json']


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        while chunk := f.read(256*1024):
            h.update(chunk)
    return h.hexdigest()


def identity():
    if sha(UNIT/'CONTRACT.json') != CONTRACT_SHA:
        raise ValueError('FROZEN_CONTRACT_REVISION3_MISMATCH')
    paths = [UNIT/p for p in DEPENDENCIES]+sorted((UNIT/'source').rglob('*.py'))
    descriptor = {'schema': 'PHYS88_PRIMARY_FROZEN_DEPENDENCIES_V1',
        'files': {str(p.relative_to(UNIT)): {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in paths},
        'integration_plan': '2maps x4T xGL16/32full +2maps x2FDscalar=20; nooldcallbacks',
        'conditional_source_native_finite_window': True}
    canonical = json.dumps(descriptor, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    return {'descriptor': descriptor, 'sha256': hashlib.sha256(canonical).hexdigest()}


def write_json(path, obj):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, allow_nan=False); f.write('\n')


def file_record(path):
    return {'filename': Path(path).name, 'bytes': Path(path).stat().st_size, 'sha256': sha(path)}


def resume(output, binding):
    manifest = json.loads((output/'OUTPUT_MANIFEST.json').read_text())
    result = json.loads((output/'RESULT.json').read_text())
    if manifest['frozen_identity'] != binding or result['frozen_identity'] != binding:
        raise ValueError('RESUME_FROZEN_IDENTITY_MISMATCH')
    if result['status'] != 'PRIMARY_COMPLETED_AWAITING_INDEPENDENT_REVIEW':
        raise ValueError('RESUME_REQUIRES_COMPLETE_PASSED_PRIMARY')
    expected_names = {'ATTEMPT.json', 'RESULT.json', 'THERMAL_MOMENTS.csv', 'OWNER_ROWS.csv',
                      'RELABEL_EVENTS.csv', 'BARE_EVENTS.csv'}
    if {r['filename'] for r in manifest['files']} != expected_names:
        raise ValueError('RESUME_COMPLETE_OUTPUT_SET_MISMATCH')
    for record in manifest['files']:
        if file_record(output/record['filename']) != record:
            raise ValueError('RESUME_COMPLETED_OUTPUT_BYTES_MISMATCH:'+record['filename'])
    return {'status': 'SKIP', 'scientific_callbacks': 0, 'thermal_integrations': 0,
        'old_science_replays': 0, 'files_rewritten': 0, 'result_rewrite': 0,
        'result_path': str(output/'RESULT.json'), 'frozen_identity_sha256': binding['sha256']}


def write_csv(path, rows, fields):
    with path.open('x', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader(); writer.writerows(rows)


def run_primary(output, binding, state):
    from atomic_bare_remap import (NativeSource, MassConvention, ConditionalMap, BareThermalIntegrator,
        DomainError, MAPS, ROUTES, FIELDS, temperature, owner_row, relabel_event, bare_event)
    import numpy as np
    contract = json.loads((UNIT/'CONTRACT.json').read_text())
    criteria, plan = contract['acceptance'], contract['numerical_plan']
    checks, guards, full, fd_rates, owner_rows, relabel, bare = [], [], [], [], [], [], []
    state.update(checks=checks, guards=guards, thermal_results=full, finite_difference_rates=fd_rates,
                 owner_rows=owner_rows, relabel_events=relabel, bare_events=bare)
    def check(label, passed, observed, criterion):
        checks.append({'label': label, 'pass': bool(passed), 'observed': observed, 'criterion': criterion})
    def reject(label, call):
        try:
            call(); row = {'label': label, 'rejected': False, 'exception': None}
        except Exception as exc:
            row = {'label': label, 'rejected': isinstance(exc, DomainError),
                   'exception': type(exc).__name__, 'reason': str(exc)}
        guards.append(row); check('guard:'+label, row['rejected'], row, 'explicit DomainError refusal')
    masses = MassConvention(contract['mass_inputs'])
    for label, residual in masses.residuals.items():
        check('exact_mass:'+label, residual == 0, str(residual), 'exact rational zero on displayed nominal inputs')
    source = NativeSource(UNIT/'source_data/n-001_H_001.endf', UNIT/'source_data/SOURCE_TABLE.json')
    witness_sha = sha(UNIT/'source_data/PHYS87_POSITIVITY_WITNESS.json')
    check('reused_positivity_witness_identity', witness_sha ==
          '4197ca1b9453e8a58b92e8619ed57c5a17db4a97857c32042691acc8b0d23c82', witness_sha, 'unchanged PHYS87 witness; callbacks0')
    witness = json.loads((UNIT/'source_data/PHYS87_POSITIVITY_WITNESS.json').read_text())
    baseline = json.loads((UNIT/'source_data/PHYS87_RESULT_BASELINE.json').read_text())
    check('reused_parent_RESULT_identity', sha(UNIT/'source_data/PHYS87_RESULT_BASELINE.json') ==
          'aaf3a145c24a57a467886ad7d6422f04805be50e389c254d2f12d8049a18b874',
          sha(UNIT/'source_data/PHYS87_RESULT_BASELINE.json'), 'saved bytes; no parent integration')
    mapped = {name: ConditionalMap(source, masses, name, conditional_transport=True) for name in MAPS}
    integrators = {name: BareThermalIntegrator(q) for name, q in mapped.items()}
    state['integrators'] = integrators
    mapping_rows = []
    es = np.asarray(source.energies)
    for name, mp in mapped.items():
        kin = mp.kinematics(es)
        recovered = mp.native_from_bare(kin['Eb_eV'])
        residuals = np.abs(recovered-es)/es
        rows = [{'index1': i+1, 'native_Es_eV': float(es[i]), 'bare_Eb_eV': float(kin['Eb_eV'][i]),
                 'K_eV': float(kin['K_eV'][i]), 'dK_dlogEs_eV': float(kin['dK_dlogEs_eV'][i]),
                 'recovered_native_Es_eV': float(recovered[i]), 'roundtrip_relative': float(residuals[i])}
                for i in range(len(es))]
        mapping_rows.append({'map': name, 'bare_support_eV': mp.bare_support(), 'knots': rows})
        check('mapping_roundtrip:'+name, bool((residuals <= 3e-15).all()), float(np.max(residuals)),
              'abs(recoveredEs-originalEs)/originalEs<=3e-15 on153positiveknots')
        check('mapping_positive_jacobian:'+name, bool((kin['dK_dlogEs_eV'] > 0).all()),
              float(np.min(kin['dK_dlogEs_eV'])), 'strictly positive derivative; analytic full-domain proof in frozen theory')
        sigma, c1, c2 = mp.evaluate_native(es)
        check('native_literal_knots:'+name, bool(np.array_equal(sigma, np.asarray(source.sigma_values)) and
            np.array_equal(c1, np.asarray(source.a1_values)) and np.array_equal(c2, np.asarray(source.a2_values))),
            len(source.rows), 'native153originalsigma/a1/a2 literals preserved; no mapped-knot reinterpolation')
        for t in plan['T_K']:
            for order in plan['primary_orders']:
                full.append(integrators[name].integrate(t, order))
    comparisons = []
    for name in MAPS:
        for t in plan['T_K']:
            a = next(r for r in full if r['map'] == name and r['T_K'] == t and r['order'] == 16)
            b = next(r for r in full if r['map'] == name and r['T_K'] == t and r['order'] == 32)
            relative = {key: abs(a[key]-b[key])/abs(b[key]) for key in FIELDS}
            comparisons.append({'map': name, 'T_K': t, 'relative_16_vs32': relative})
            for key, value in relative.items():
                check('quadrature:'+name+':'+str(t)+':'+key,
                      value <= criteria['quadrature_relative_rate_means'], value, criteria['quadrature_relative_rate_means'])
    fd_comparisons = []
    for name in MAPS:
        step = 2**-8; t = plan['FD']['T_K']
        low = integrators[name].integrate(t*math.exp(-step), 32, rate_only=True)
        high = integrators[name].integrate(t*math.exp(step), 32, rate_only=True)
        fd_rates.extend([low, high])
        slope = math.log(high['kappa_cm3_per_s']/low['kappa_cm3_per_s'])/(2*step)
        analytic = next(r for r in full if r['map'] == name and r['T_K'] == t and r['order'] == 32)['selected_log_rate_slope']
        residual = slope-analytic
        fd_comparisons.append({'map': name, 'T_K': t, 'hlog': step, 'FD_log_rate_slope': slope,
                               'selected_energy_log_rate_slope': analytic, 'residual': residual})
        check('FD:'+name, abs(residual) <= criteria['FD_log_rate_slope_abs'], residual, criteria['FD_log_rate_slope_abs'])
    event_plan = plan['relabel_and_bare_event_cases']
    for energy in event_plan['native_Es_eV']:
        for beta in event_plan['normal_boost_beta']:
            for mu in event_plan['COM_photon_mu']:
                label = str(energy)+':'+str(beta)+':'+str(mu)
                row = relabel_event(masses, energy, beta, mu); relabel.append(row)
                check('relabel:'+label, row['relabel_max_abs_eV'] <= criteria['relabel_carrier_abs_eV'],
                      row['relabel_max_abs_eV'], criteria['relabel_carrier_abs_eV'])
                for particle, shell in row['mass_shells'].items():
                    check('relabel_shell:'+label+':'+particle,
                          shell['scaled_residual'] <= criteria['mass_shell_scaled_residual'],
                          shell, criteria['mass_shell_scaled_residual'])
                for name in MAPS:
                    row = bare_event(mapped[name], energy, beta, mu); bare.append(row)
                    check('bare_four_vector:'+name+':'+label,
                          row['four_vector']['scaled_residual'] <= criteria['bare_4vector_scaled_residual'],
                          row['four_vector'], criteria['bare_4vector_scaled_residual'])
                    for particle, shell in row['mass_shells'].items():
                        check('bare_shell:'+name+':'+label+':'+particle,
                              shell['scaled_residual'] <= criteria['mass_shell_scaled_residual'],
                              shell, criteria['mass_shell_scaled_residual'])
    for row in full:
        label = row['map']+':'+str(row['T_K'])+':'+str(row['order'])
        check('mean_energy:'+label, abs(row['energy_identity_residual_eV']) <= criteria['owner_energy_closure_abs_eV'],
              row['energy_identity_residual_eV'], criteria['owner_energy_closure_abs_eV'])
        variance = {k: row[k] for k in ('variance_Kin_eV2', 'variance_Egamma_eV2', 'variance_Kd_eV2')}
        check('centered_variances:'+label, all(math.isfinite(v) and v >= 0 for v in variance.values()), variance, 'finite>=0')
        if row['order'] == 32:
            for h in (0, 1):
                for route in ROUTES:
                    owned = owner_row(row, masses, h, route); owner_rows.append(owned)
                    name = label+':'+str(h)+':'+route
                    check('owner_energy:'+name, abs(owned['energy_closure_eV']) <= criteria['owner_energy_closure_abs_eV'],
                          owned['energy_closure_eV'], criteria['owner_energy_closure_abs_eV'])
                    counts = owned['count_columns']; energy_columns = owned['energy_columns_eV']
                    check('owner_counts:'+name, counts['thermal']+counts['fast'] == -1 and counts['free_electron'] == 0,
                          counts, 'one capture; thermal h-2,fast1-h,electron0')
                    check('owner_photon_exclusive:'+name,
                        (energy_columns['radiation_injected'] == 0) != (energy_columns['radiation_escape'] == 0),
                        energy_columns, 'exactlyonephotonowner; no duplicateQheat')
    sample = next(r for r in full if r['map'] == MAPS[0] and r['order'] == 32)
    mp, engine = mapped[MAPS[0]], integrators[MAPS[0]]
    reject('missing_map', lambda: ConditionalMap(source, masses, conditional_transport=True))
    reject('unknown_map', lambda: ConditionalMap(source, masses, 'FIXED_AMPLITUDE', conditional_transport=True))
    reject('missing_conditional_opt_in', lambda: ConditionalMap(source, masses, MAPS[0]))
    reject('conditional_opt_in_not_bool', lambda: ConditionalMap(source, masses, MAPS[0], conditional_transport=1))
    for name, value in [('below', 1e-6), ('above', 20000001.0), ('nan', math.nan), ('inf', math.inf), ('bool', True)]:
        reject('native_energy_'+name, lambda v=value: mp.evaluate_native([v]))
    for name in MAPS:
        obj = mapped[name]; lo, hi = obj.bare_support()
        for label, value in [('below', lo/2), ('above', hi*2), ('nan', math.nan), ('inf', math.inf), ('bool', True)]:
            reject('bare_energy_'+name+'_'+label, lambda q=obj, v=value: q.native_from_bare([v]))
    for label, value in [('below', 254), ('above', 101000001), ('nan', math.nan), ('inf', math.inf), ('bool', True)]:
        reject('temperature_'+label, lambda v=value: temperature(v, masses))
    for label, value in [('two', 2), ('fraction', .5), ('bool', True)]:
        reject('owner_'+label, lambda v=value: owner_row(sample, masses, v, ROUTES[0]))
    reject('both_photon_routes', lambda: owner_row(sample, masses, 0, 'both'))
    reject('order17', lambda: engine.integrate(10000, 17))
    reject('rate_only_not_bool', lambda: engine.integrate(10000, 32, rate_only=1))
    reject('production_map', lambda: ConditionalMap(source, masses, MAPS[0], conditional_transport=True, production=True))
    reject('production_integral', lambda: engine.integrate(10000, 32, production=True))
    reject('production_owner', lambda: owner_row(sample, masses, 0, ROUTES[0], production=True))
    reject('production_event', lambda: bare_event(mp, 1, .2, 0, production=True))
    reject('event_superluminal', lambda: bare_event(mp, 1, 1, 0))
    reject('event_mu_outside', lambda: bare_event(mp, 1, .2, 2))
    calls = [r for obj in integrators.values() for r in obj.integration_calls]
    counts = {'thermal_integrations': len(calls), 'full_moment_integrations': len(full),
        'FD_scalar_integrations': len(fd_rates), 'source_relabel_cases': len(relabel),
        'bare_event_cases': len(bare), 'adopted_owner_rows': len(owner_rows),
        'native_source_knots': len(source.rows), 'native_intervals_per_integral': 152,
        'reused_positive_knots': len(witness['knots']), 'reused_convex_cells': len(witness['cells']),
        'new_positivity_callbacks': 0, 'guards': len(guards)}
    check('frozen_campaign_scope', [len(full), len(fd_rates), len(relabel), len(bare), len(owner_rows)] == [16, 4, 18, 36, 32],
          counts, '16full4scalar18relabel36bare32owner; scope receipt not scientific oracle')
    failed = [q for q in checks if not q['pass']]
    counts.update(assertions=len(checks), passed_assertions=sum(q['pass'] for q in checks), failed_assertions=len(failed))
    report = {'schema': 'PHYS88_CONDITIONAL_BARE_FINITE_WINDOW_PRIMARY_V1',
        'status': 'PRIMARY_COMPLETED_AWAITING_INDEPENDENT_REVIEW' if not failed else 'PRIMARY_COMPLETED_CHECK_FAILURE',
        'frozen_identity': binding, 'mass_convention': masses.record(), 'mapping_knots': mapping_rows,
        'thermal_results': full, 'finite_difference_rates': fd_rates, 'finite_difference_comparisons': fd_comparisons,
        'quadrature_comparisons': comparisons, 'source_relabel_events': relabel, 'bare_events': bare,
        'owner_rows': owner_rows, 'checks': checks, 'failures': failed, 'guard_controls': guards, 'counts': counts,
        'integration_call_ledger': calls, 'bessel_exact_coefficients': engine.bessel.exact_coefficient_record(),
        'parent_saved_order32_rows': [r for r in baseline['thermal_results'] if r['order'] == 32],
        'parent_positivity_sha256': witness_sha, 'parent_positivity_recomputed': False,
        'scope': 'Conditional nominal LAB_ANCHORED/FIXED_COM_K bare finite source window; empirical kernel equivalence OPEN',
        'map_difference_is_physical_uncertainty_interval': False,
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__,
                    'affinity_cpus': sorted(os.sched_getaffinity(0))},
        'old_PHYS78_87_science_callbacks': 0, 'new_ODE': 0, 'network_rate_activation': 0, 'fast_stopping': 0,
        'source_covariance_propagated': False, 'physical_CI': False, 'HH_R10': 'OFF',
        'production_admission': 'NOT_ISSUED', 'scientific_admission': 'PENDING_ROOT_AND_INDEPENDENT_RAW_REVIEW'}
    write_json(output/'RESULT.json', report)
    write_csv(output/'THERMAL_MOMENTS.csv', full, ['map', 'T_K', 'order', *FIELDS,
        'variance_Kin_eV2', 'variance_Egamma_eV2', 'variance_Kd_eV2', 'selected_log_rate_slope', 'energy_identity_residual_eV'])
    write_csv(output/'OWNER_ROWS.csv', [{**r, **r['energy_columns_eV']} for r in owner_rows],
        ['map', 'T_K', 'order', 'h', 'radiation_route', 'thermal', 'fast', 'nuclear_rest', 'atomic_binding',
         'radiation_injected', 'radiation_escape', 'energy_closure_eV', 'Cv_Tdot_over_R_eV'])
    write_csv(output/'RELABEL_EVENTS.csv', relabel,
        ['native_Es_eV', 'normal_boost_beta', 'COM_photon_mu', 'C_eV', 'reservoir_delta_eV', 'relabel_max_abs_eV'])
    write_csv(output/'BARE_EVENTS.csv', [{**r, 'scaled_four_vector_residual': r['four_vector']['scaled_residual']} for r in bare],
        ['map', 'native_Es_eV', 'bare_Eb_eV', 'normal_boost_beta', 'COM_photon_mu', 'scaled_four_vector_residual', 'carrier_added'])
    write_json(output/'OUTPUT_MANIFEST.json', {'schema': 'PHYS88_COMPLETE_PRIMARY_OUTPUT_BYTES_V1',
        'frozen_identity': binding, 'files': [file_record(p) for p in sorted(output.iterdir()) if p.is_file()],
        'self_exclusion': 'OUTPUT_MANIFEST excludes ownbytes; binds allprioroutputs'})
    return {'status': report['status'], 'counts': counts, 'result_sha256': sha(output/'RESULT.json'),
            'result_path': str(output/'RESULT.json'), 'scientific_admission': report['scientific_admission']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True); p.add_argument('--resume', action='store_true')
    args = p.parse_args(); output = args.output.resolve()
    if output != UNIT/'results/primary001':
        raise ValueError('FROZEN_SINGLE_PRIMARY001_OUTPUT_PATH_REQUIRED')
    binding = identity()
    if args.resume:
        print(json.dumps(resume(output, binding))); return 0
    output.mkdir(parents=True, exist_ok=False)
    write_json(output/'ATTEMPT.json', {'schema': 'PHYS88_CREATE_ONLY_PRIMARY_ATTEMPT_V1',
        'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'frozen_identity': binding, 'thermal_integration_limit': 20, 'automatic_retry': 0})
    state = {}
    try:
        receipt = run_primary(output, binding, state); print(json.dumps(receipt, allow_nan=False))
        return 0 if receipt['status'] == 'PRIMARY_COMPLETED_AWAITING_INDEPENDENT_REVIEW' else 1
    except BaseException as exc:
        integrators = state.pop('integrators', {})
        failure = {'schema': 'PHYS88_PRIMARY_FAILURE_PRESERVED_V1', 'status': 'FAILED_FIRST_ATTEMPT_PRESERVED',
            'exception': type(exc).__name__, 'reason': str(exc), 'traceback': traceback.format_exc(),
            'frozen_identity': binding, 'partial_saved_observations': state,
            'integration_calls': [q for obj in integrators.values() for q in obj.integration_calls],
            'automatic_retries': 0, 'scientific_admission': 'NOT_ISSUED'}
        write_json(output/'FAILURE.json', failure)
        print(json.dumps({'status': failure['status'], 'reason': str(exc)})); return 1


if __name__ == '__main__':
    raise SystemExit(main())
