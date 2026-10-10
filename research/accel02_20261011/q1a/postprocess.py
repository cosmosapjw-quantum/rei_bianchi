#!/usr/bin/env python3
"""Reconstruct Q1A saved-state moments; SIGMA calls only, no ODE or RHS.

The copied grid, geometry and event implementations are bound to IDENTITY.json.
No current midpoint-grid factory is consulted and no photon state is remapped.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
EV = 1.602176634e-12
C = 29979245800.
CHI = np.array([13.598434599702, 24.587389011, 54.41776])
AS_RUN_BINDINGS = {
    'base_driver_as_run.py': 'base_sha',
    'driver_as_run.py': 'driver_sha',
    'fixed_grid_as_run.py': 'grid_factory_sha',
    'characteristics_as_run.py': 'characteristics_sha',
    'events_as_run.py': 'events_sha',
    'GRID.json': 'grid_sha',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def moments(run, n1dir, preflight=None):
    run, n1dir = Path(run), Path(n1dir)
    identity, result = read(run/'IDENTITY.json'), read(run/'RESULT.json')
    if result['status'] != 'COMPUTED_NOT_REVIEWED' or len(result['history']) != 129:
        raise ValueError('REQUIRES_COMPLETED_129_EPOCH_SAVED_RUN')
    checks = {name+'_bytes': sha(run/name) == identity[key]
              for name, key in AS_RUN_BINDINGS.items()}
    checks['n1_bytes'] = sha(n1dir/'provider.py') == identity['n1_sha']
    binary = n1dir/'native/target/release/rei_n1_native'
    checks['binary_bytes'] = sha(binary) == identity['native_sha']
    if not all(checks.values()):
        raise ValueError(f'IDENTITY_MISMATCH:{checks}')

    # events_as_run imports characteristics by this exact module name.
    char = module('characteristics', run/'characteristics_as_run.py')
    events = module('q1a_saved_events', run/'events_as_run.py')
    factory = module('q1a_saved_grid_factory', run/'fixed_grid_as_run.py')
    n1 = module('q1a_saved_n1', n1dir/'provider.py')
    provider = n1.HistoryProvider(identity['args']['shear'])
    grid = factory.FixedCharacteristics(run/'GRID.json', char)
    preflight = Path(preflight) if preflight is not None else HERE/'evidence/PREFLIGHT.json'
    geometry_evidence = read(preflight)
    geometry_rows = [r for r in geometry_evidence['grids'].values()
                     if r['grid_arrays_sha256'] == identity['grid_arrays_sha256']]
    if len(geometry_rows) != 1:
        raise ValueError('PREFLIGHT_GRID_BINDING')
    geometry_row = geometry_rows[0]
    checks['geometry_preflight_schema'] = geometry_evidence['schema'] == 'rei.q1a.preflight.v1'
    checks['geometry_grid_file_identity'] = geometry_row['grid_sha256'] == identity['grid_sha']
    checks['geometry_grid_factory_identity'] = geometry_evidence['grid_factory_sha256'] == identity['grid_factory_sha']
    checks['geometry_base_identity'] = geometry_evidence['base_sha256'] == identity['base_sha']
    checks['geometry_native_identity'] = geometry_evidence['native_sha256'] == identity['native_sha']
    geometry_pass = bool(np.isfinite(geometry_row['geometry_max'])
        and geometry_row['geometry_max'] <= 1e-11 and geometry_row['gates']['geometry'] is True)
    checks['source_input_bytes'] = provider.identity == identity['input_identity']
    checks['grid_source_identity'] = grid.record['input_identity'] == identity['input_identity']
    checks['grid_order_identity'] = grid.record['order'] == identity['grid_order']
    checks['grid_factory_identity'] = grid.record['implementation_sha256'] == identity['grid_factory_sha']
    checks['grid_arrays_declared_identity'] = grid.record['arrays_sha256'] == identity['grid_arrays_sha256']
    expected = grid.make_grid(identity['args']['energy'], identity['args']['angle'], provider.q_max_eV)
    with np.load(run/'history.npz', allow_pickle=False) as data:
        u = data['u']
        states = data['scaled_states'] * data['scales']
        q, mu, weights = (data[k] for k in ('q', 'mu', 'weights'))
    checks['saved_grid_exact'] = all(np.array_equal(a, b) for a, b in zip((q, mu, weights), expected))
    checks['saved_arrays_sha256'] = factory.arrays_sha((q, mu, weights)) == identity['grid_arrays_sha256']
    checks['saved_epoch_exact'] = np.array_equal(u, np.linspace(0., 1., 129))
    checks['json_epoch_exact'] = np.array_equal(u*provider.end_time_s, [r['time_s'] for r in result['history']])
    checks['saved_state_shape'] = states.shape == (129, len(q)+10)
    checks['saved_finite'] = bool(np.isfinite(states).all())
    checks['result_node_count'] = result['n_nodes'] == len(q)
    bounds = np.asarray(read(run/'EVENTS.json')['boundaries'], dtype=float)
    checks['event_boundaries'] = bool(bounds.ndim == 1 and len(bounds) >= 2
        and np.isfinite(bounds).all() and bounds[0] == 0. and bounds[-1] == 1.
        and np.all(np.diff(bounds) > 0.) and len(bounds)-1 == identity['segment_count']
        and result['completed_segments'] == identity['segment_count'])
    if not all(checks.values()):
        raise ValueError(f'GRID_OR_SAVED_STATE_MISMATCH:{checks}')
    knots = np.array(sorted(set([10., 13.60, 24.59, 54.42, 50000.]
                                + events.native_jump_energies(provider.tables['emissivity']))))
    extended = np.r_[0., knots, np.inf]
    rows, max_shift = [], 0.
    native = n1.Native(binary)
    try:
        for uu, state in zip(u, states):
            segment = max(0, min(len(bounds)-2, int(np.searchsorted(bounds, uu, side='left'))-1))
            middle = .5*(bounds[segment]+bounds[segment+1])
            gm = provider.geometry(float(middle*provider.end_time_s))
            em = char.geometry_nodes(q, mu, gm)[0]
            cell = np.searchsorted(knots, em, side='right')
            lo, hi = extended[cell], extended[cell+1]
            t = float(uu*provider.end_time_s)
            geom = provider.geometry(t)
            energy, _, ratio = char.geometry_nodes(q, mu, geom)
            ee = energy.copy()
            low, high = ee <= lo, ee >= hi
            ee[low] = np.nextafter(lo[low], np.inf)
            ee[high] = np.nextafter(hi[high], 0.)
            shift = float(np.max(abs(ee-energy)/energy))
            max_shift = max(max_shift, shift)
            if shift > 64*np.finfo(float).eps:
                raise ValueError('EVENT_SPECTRAL_CELL_MISMATCH')
            inside, active = (em > 10.) & (em < 50000.), em < 50000.
            source = np.zeros(len(q))
            source[inside] = provider.tables['emissivity'].photon_emission_log(ee[inside], geom['z'])*weights[inside]/ratio[inside]**3
            sigma = np.zeros((len(q), 3))
            sigma[active] = native.call('SIGMA', ee[active]).reshape(-1, 3)
            energy_state = state[4:4+len(q)]
            number = energy_state/ee
            volume = geom['a_rel']**3
            h, he1, he2 = state[:3]
            absorbers = np.array([geom['nH']*(1-h), geom['nHe']*(1-he1-he2), geom['nHe']*he1])
            gamma = C*(number@sigma)/volume
            excess = C*EV*np.sum(number[:, None]*sigma*(ee[:, None]-CHI), axis=0)/volume
            heat = absorbers*excess
            counters = state[4+len(q):]
            rows.append(dict(time_s=t, z=geom['z'],
                source_number_ref_cm3_s=float(source.sum()),
                source_energy_ref_erg_cm3_s=float(EV*np.dot(source, ee)),
                source_number_proper_cm3_s=float(source.sum()/volume),
                source_energy_proper_erg_cm3_s=float(EV*np.dot(source, ee)/volume),
                cumulative_source_number_ref_cm3=float(counters[4]),
                cumulative_source_energy_ref_erg_cm3=float(counters[2]),
                radiation_energy_ref_erg_cm3=float(EV*energy_state.sum()),
                radiation_energy_proper_erg_cm3=float(EV*energy_state.sum()/volume),
                photoheat_HI_per_absorber_erg_s=float(excess[0]),
                photoheat_HeI_per_absorber_erg_s=float(excess[1]),
                photoheat_HeII_per_absorber_erg_s=float(excess[2]),
                photoheat_HI_proper_erg_cm3_s=float(heat[0]),
                photoheat_HeI_proper_erg_cm3_s=float(heat[1]),
                photoheat_HeII_proper_erg_cm3_s=float(heat[2]),
                total_photoheat_proper_erg_cm3_s=float(heat.sum()),
                GammaHI_s=float(gamma[0]), GammaHeI_s=float(gamma[1]),
                GammaHeII_s=float(gamma[2]), photon_cm3=float(number.sum()/volume)))
    finally:
        native.close()
    reconstructed = {}
    reconstruction_pass = True
    for key in ('GammaHI_s', 'GammaHeI_s', 'GammaHeII_s', 'photon_cm3'):
        new = np.array([r[key] for r in rows])
        old = np.array([r[key] for r in result['history']])
        scale, error = float(max(abs(old))), float(max(abs(new-old)))
        reconstructed[key] = error/scale if scale else error
        reconstruction_pass = reconstruction_pass and (error/scale <= 1e-13 if scale else error == 0.)
    if not reconstruction_pass:
        raise ValueError(f'SAVED_OBSERVABLE_RECONSTRUCTION_MISMATCH:{reconstructed}')
    files = ['IDENTITY.json', 'RESULT.json', 'history.npz', 'EVENTS.json', *AS_RUN_BINDINGS]
    return dict(status='POSTPROCESSED_NO_ODE_NO_PROMOTION', run=run.name,
        saved_file_sha256={name: sha(run/name) for name in files},
        implementation_sha256=sha(__file__), identity_checks=checks,
        geometry_preflight=dict(relative_path=os.path.relpath(preflight.resolve(), run.resolve()),
            sha256=sha(preflight), grid_arrays_sha256=identity['grid_arrays_sha256'],
            grid_sha256=identity['grid_sha'], geometry_max=geometry_row['geometry_max'],
            frozen_budget=1e-11, passed=geometry_pass),
        original_observable_reconstruction_scaled_errors=reconstructed,
        max_one_sided_relative_energy_shift=max_shift,
        native_calls='SIGMA only; no RHS',
        units='cgs; reference initial physical cm^3; proper = reference/a_rel^3; cumulative source counters integrate per reference cm^3',
        heat_definition='Primary photoelectron excess power c sum_i N_i sigma_ia (E_i-chi_a) EV/a_rel^3 per absorber; total proper heat=sum_a n_abs,a H_a. Excludes cooling, Compton, CI and expansion.',
        spectral_field_target=1e-3,
        accepted_gas_domain=result['checks'].get('accepted_gas_domain', 'NOT_MEASURED'),
        history=rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('--n1', type=Path, default=HERE.parent/'n1')
    parser.add_argument('--preflight', type=Path, default=HERE/'evidence/PREFLIGHT.json')
    args = parser.parse_args()
    output = args.run/'MOMENTS.json'
    if output.exists():
        raise FileExistsError(output)
    result = moments(args.run, args.n1, args.preflight)
    with output.open('x') as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write('\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'history'}, indent=2))


if __name__ == '__main__':
    main()
