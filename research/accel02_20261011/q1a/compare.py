#!/usr/bin/env python3
"""Compare immutable Q1A saved results, with frozen time/spectral gates.

No ODE is executed. A passing finite-grid comparison still requires independent
review; it is neither a continuum error bound nor an angular/BASS admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FIELDS = ['xHII', 'xHeII', 'xHeIII', 'T_K', 'ne_cm3', 'photon_cm3',
          'GammaHI_s', 'GammaHeI_s', 'GammaHeII_s']
MOMENTS = ['source_number_ref_cm3_s', 'source_energy_ref_erg_cm3_s',
           'source_number_proper_cm3_s', 'source_energy_proper_erg_cm3_s',
           'cumulative_source_number_ref_cm3', 'cumulative_source_energy_ref_erg_cm3',
           'radiation_energy_ref_erg_cm3', 'radiation_energy_proper_erg_cm3',
           'photoheat_HI_per_absorber_erg_s', 'photoheat_HeI_per_absorber_erg_s',
           'photoheat_HeII_per_absorber_erg_s', 'photoheat_HI_proper_erg_cm3_s',
           'photoheat_HeI_proper_erg_cm3_s', 'photoheat_HeII_proper_erg_cm3_s',
           'total_photoheat_proper_erg_cm3_s']
PROTECTED = ['base_sha', 'driver_sha', 'events_sha', 'characteristics_sha',
             'grid_factory_sha', 'n1_sha', 'native_sha', 'input_identity', 'semantics', 'grid_kind']
REQUIRED_CHECKS = ['whole_interval', 'sampled_positive', 'accepted_positive',
                   'accepted_finite', 'accepted_gas_domain', 'energy_ledger', 'number_ledger']


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def metric(coarse, fine, epochs, budget):
    """Each selected epoch set uses its own fine-history amplitude.

    For zero fine amplitude the displayed scaled_error retains the historical
    absolute-error fallback, while the actual gate requires exact zero error.
    """
    coarse, fine = np.asarray(coarse), np.asarray(fine)
    epochs = np.asarray(epochs)
    if coarse.shape != (129,) or fine.shape != (129,) or not np.isfinite(coarse).all() or not np.isfinite(fine).all():
        raise ValueError('NONFINITE_OR_NON129_FIELD')
    amplitude = float(np.max(abs(fine[epochs])))
    delta = abs(coarse[epochs]-fine[epochs])
    j = int(np.argmax(delta))
    error = float(delta[j])
    return dict(scaled_error=error/amplitude if amplitude else error,
        absolute_error=error, fine_whole_history_amplitude=amplitude,
        fine_all129_amplitude=float(np.max(abs(fine))), worst_epoch_index=int(epochs[j]),
        zero_fine_amplitude=amplitude == 0.,
        pass_budget=error/amplitude <= budget if amplitude else error == 0.)


def pair_identities(ai, bi, ag, bg, kind):
    checks = {key: ai[key] == bi[key] for key in PROTECTED}
    checks.update({'arg_'+key: ai['args'][key] == bi['args'][key]
                   for key in ('angle', 'shear', 'max_step')})
    for key in ('schema', 'panel_edges_eV', 'n_mu', 'construction', 'input_identity', 'implementation_sha256'):
        checks['grid_'+key] = ag[key] == bg[key]
    checks['fixed_q_composite_gauss'] = ai['grid_kind'] == bi['grid_kind'] == 'fixed_q_composite_gauss'
    if kind == 'spectral':
        checks['arg_rtol_equal'] = ai['args']['rtol'] == bi['args']['rtol']
        checks['prospective_order1_to_order2'] = ag['order'] == 1 and bg['order'] == 2
        checks['energy_count_doubles'] = bi['args']['energy'] == 2*ai['args']['energy']
        checks['different_grid_arrays'] = ai['grid_arrays_sha256'] != bi['grid_arrays_sha256']
    elif kind == 'time':
        for key in ('grid_sha', 'grid_arrays_sha256', 'grid_order'):
            checks['same_'+key] = ai[key] == bi[key]
        checks['same_energy_count'] = ai['args']['energy'] == bi['args']['energy']
        checks['strictly_tighter_rtol'] = 0. < bi['args']['rtol'] < ai['args']['rtol']
    else:
        raise ValueError('UNKNOWN_COMPARISON_KIND')
    return checks


def load_bound_run(run):
    result = read(run/'RESULT.json')
    identity = read(run/'IDENTITY.json')
    moments = read(run/'MOMENTS.json')
    grid = read(run/'GRID.json')
    if result['status'] != 'COMPUTED_NOT_REVIEWED' or moments['status'] != 'POSTPROCESSED_NO_ODE_NO_PROMOTION':
        raise ValueError('INCOMPLETE_RUN_OR_UNBOUND_MOMENTS:'+str(run))
    if not moments['identity_checks'] or not all(v is True for v in moments['identity_checks'].values()):
        raise ValueError('MOMENT_IDENTITY_FAILURE:'+str(run))
    required_files = {'IDENTITY.json', 'RESULT.json', 'history.npz', 'EVENTS.json',
        'driver_as_run.py', 'base_driver_as_run.py', 'fixed_grid_as_run.py',
        'characteristics_as_run.py', 'events_as_run.py', 'GRID.json'}
    if not required_files.issubset(moments['saved_file_sha256']):
        raise ValueError('INCOMPLETE_MOMENT_FILE_BINDING:'+str(run))
    for name, expected in moments['saved_file_sha256'].items():
        if sha(run/name) != expected:
            raise ValueError('STALE_MOMENT_INPUT:'+str(run/name))
    if sha(HERE/'postprocess.py') != moments['implementation_sha256']:
        raise ValueError('POSTPROCESS_IMPLEMENTATION_CHANGED:'+str(run))
    geometry = moments['geometry_preflight']
    preflight_path = run/geometry['relative_path']
    if sha(preflight_path) != geometry['sha256']:
        raise ValueError('GEOMETRY_PREFLIGHT_CHANGED:'+str(run))
    preflight = read(preflight_path)
    geometry_rows = [r for r in preflight['grids'].values()
                     if r['grid_arrays_sha256'] == identity['grid_arrays_sha256']]
    if (len(geometry_rows) != 1 or geometry['grid_arrays_sha256'] != identity['grid_arrays_sha256']
        or geometry['grid_sha256'] != identity['grid_sha']
        or geometry_rows[0]['grid_sha256'] != identity['grid_sha']
        or geometry_rows[0]['geometry_max'] != geometry['geometry_max']):
        raise ValueError('GEOMETRY_GRID_BINDING:'+str(run))
    if len(result['history']) != 129 or len(moments['history']) != 129:
        raise ValueError('REQUIRES_129_EPOCHS:'+str(run))
    tr = np.array([r['time_s'] for r in result['history']])
    tm = np.array([r['time_s'] for r in moments['history']])
    zr = np.array([r['z'] for r in result['history']])
    zm = np.array([r['z'] for r in moments['history']])
    if not np.array_equal(tr, tm) or not np.array_equal(zr, zm):
        raise ValueError('RESULT_MOMENT_EPOCH_MISMATCH:'+str(run))
    checks = {key: result['checks'].get(key) is True for key in REQUIRED_CHECKS}
    energy = max(result['max_endpoint_energy_ledger'], max(abs(r['energy_ledger_scaled']) for r in result['history']))
    number = max(result['max_endpoint_number_ledger'], max(abs(r['number_ledger_scaled']) for r in result['history']))
    checks['combined_energy_ledger'] = bool(np.isfinite(energy) and energy <= 1e-9)
    checks['combined_number_ledger'] = bool(np.isfinite(number) and number <= 1e-9)
    checks['combined_energy_report_exact'] = energy == result['max_energy_ledger']
    checks['combined_number_report_exact'] = number == result['max_number_ledger']
    checks['accepted_gas_moment_report'] = moments['accepted_gas_domain'] is True
    checks['geometry_preflight'] = bool(geometry['passed'] is True and geometry['frozen_budget'] == 1e-11
        and np.isfinite(geometry['geometry_max']) and geometry['geometry_max'] <= 1e-11
        and geometry_rows[0]['gates']['geometry'] is True)
    return result, identity, moments, grid, checks, dict(energy=energy, number=number)


def compare(coarse, fine, kind):
    ar, ai, am, ag, ac, al = load_bound_run(coarse)
    br, bi, bm, bg, bc, bl = load_bound_run(fine)
    identities = pair_identities(ai, bi, ag, bg, kind)
    times = np.array([r['time_s'] for r in ar['history']])
    tf = np.array([r['time_s'] for r in br['history']])
    if not np.isfinite(times).all() or not np.array_equal(times, tf):
        raise ValueError('SHARED_EPOCH_MISMATCH')
    if not np.array_equal([r['z'] for r in ar['history']], [r['z'] for r in br['history']]):
        raise ValueError('SHARED_REDSHIFT_MISMATCH')
    budget = 1e-3 if kind == 'spectral' else 2e-6
    comparisons = {}
    for count, epochs in [('129', np.arange(129)), ('65', np.arange(0, 129, 2))]:
        rows = {}
        for fields, left, right in [(FIELDS, ar, br), (MOMENTS, am, bm)]:
            for key in fields:
                value = metric([r[key] for r in left['history']], [r[key] for r in right['history']], epochs, budget)
                value.update(worst_time_s=float(times[value['worst_epoch_index']]),
                    worst_z=float(br['history'][value['worst_epoch_index']]['z']),
                    required_for_gate=kind == 'spectral' or key in FIELDS)
                rows[key] = value
        required = {key: value for key, value in rows.items() if value['required_for_gate']}
        comparisons[count] = dict(fields=rows,
            pass_required_fields=all(value['pass_budget'] for value in required.values()),
            pass_all_reported_fields=all(value['pass_budget'] for value in rows.values()),
            max_required_scaled_error=max(value['scaled_error'] for value in required.values()),
            max_all_scaled_error=max(value['scaled_error'] for value in rows.values()))
    checks = {'coarse': ac, 'fine': bc}
    passed = all(identities.values()) and all(all(v.values()) for v in checks.values()) and all(v['pass_required_fields'] for v in comparisons.values())
    prefix = 'SPECTRAL' if kind == 'spectral' else 'TIME'
    return dict(status=prefix+'_FIELDS_PASS_PENDING_INDEPENDENT_REVIEW' if passed else prefix+'_REFINEMENT_FAIL',
        kind=kind, passed_frozen_gates=passed,
        method='max_abs(coarse-fine) / max_abs(fine), each selected whole-history epoch set using its own fine amplitude; 65 retains original sampling and129 is additional. Exact zero fine amplitude requires exact zero difference.',
        frozen_field_budget=budget, required_fields=FIELDS+MOMENTS if kind == 'spectral' else FIELDS,
        diagnostic_only_fields=[] if kind == 'spectral' else MOMENTS,
        identity_checks=identities, native_checks=checks, combined_ledgers={'coarse': al, 'fine': bl},
        comparisons=comparisons,
        geometry_preflight={'coarse': am['geometry_preflight'], 'fine': bm['geometry_preflight']},
        coarse_all_accepted_gas_domain=ar['checks'].get('accepted_gas_domain', 'NOT_MEASURED'),
        fine_all_accepted_gas_domain=br['checks'].get('accepted_gas_domain', 'NOT_MEASURED'),
        angular_status='NOT_EVALUATED', continuum_error_bound='NOT_ESTABLISHED',
        scientific_ceiling='Conditional FLRW source-band-limited primary-only CaseA gas+photon history, isotropic CMB bath; no CR/RCT, Bianchi signal or observer visibility admission.',
        files={str(x): sha(x) for d in (coarse, fine) for x in [d/'RESULT.json', d/'IDENTITY.json', d/'history.npz', d/'MOMENTS.json', d/'GRID.json']},
        postprocess_code_sha256=sha(HERE/'postprocess.py'), comparison_code_sha256=sha(__file__))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('coarse', type=Path)
    parser.add_argument('fine', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--kind', choices=['spectral', 'time'], required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = compare(args.coarse, args.fine, args.kind)
    with args.output.open('x') as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write('\n')
    print(json.dumps(dict(status=result['status'], identity_checks=result['identity_checks'],
        native_checks=result['native_checks'],
        maxima={key: val['max_required_scaled_error'] for key, val in result['comparisons'].items()},
        failed_fields={key: [name for name, field in val['fields'].items() if field['required_for_gate'] and not field['pass_budget']]
                       for key, val in result['comparisons'].items()}), indent=2))
    return 0 if result['passed_frozen_gates'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
