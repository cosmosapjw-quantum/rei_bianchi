"""Exact moments of the pinned HM12 interpolation on new fixed q cells.

S_N=w_mu R^-3 integral s_log dlnE;
S_U=w_mu R^-3 integral E s_log dlnE and S_Q=S_U/R.
R=E/q is angle dependent. Arrays are ordered (angle, energy_cell).
This is a source/IC component only, not a photon closure or coupled solver.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import numpy as np

HERE = Path(__file__).resolve().parent
EV_ERG = 1.602176634e-12


def table_cell_moments(table, z, q_edges, R, angular_weights, band=(10., 50000.)):
    """Return N,U_eV,Q_eV moments for a UVB or emissivity table.

    Units are cm^-3 (UVB) or cm^-3 s^-1 (emissivity), referred to the
    initial volume; U/Q additionally carry eV. UVB IC is used at R=1 only
    by CellSource.initial. Temporary physical-band intersections never
    delete stored photons below10eV. Integrals retain native one-sided jumps.

    Shares _z_profile, proper_photon_factor and analytic exponential weights
    with HM12Table.moment. It avoids its repeated all-native-segment scan;
    it is not an independent physical/interpolation reference.
    """
    edges = np.asarray(q_edges, dtype=float)
    R, w = np.asarray(R, dtype=float), np.asarray(angular_weights, dtype=float)
    band = np.asarray(band, dtype=float)
    if (edges.ndim != 1 or len(edges) < 2 or not np.isfinite(edges).all()
            or np.any(edges <= 0) or np.any(np.diff(edges) <= 0)):
        raise ValueError('Q1B_SOURCE_EDGES')
    if (R.ndim != 1 or w.ndim != 1 or R.shape != w.shape or not R.size
            or not np.isfinite(R).all() or not np.isfinite(w).all()
            or np.any(R <= 0) or np.any(w < 0)):
        raise ValueError('Q1B_SOURCE_ANGLE_FACTORS')
    if band.shape != (2,) or not np.isfinite(band).all() or band[1] < band[0]:
        raise ValueError('Q1B_SOURCE_BAND')
    table._checked_energies(band)
    native, profile = table.energies_eV, table._z_profile(float(z))
    factor = table.proper_photon_factor(float(z))
    weights_function = sys.modules[type(table).__module__]._exponential_linear_weights
    N = np.zeros((len(R), len(edges)-1))
    U = np.zeros_like(N)
    for a, (r, weight) in enumerate(zip(R, w)):
        prefactor = weight / r**3 * factor
        if weight == 0:
            continue
        for cell, (ql, qr) in enumerate(zip(edges[:-1], edges[1:])):
            lo, hi = max(r*ql, band[0]), min(r*qr, band[1])
            if hi <= lo:
                continue
            begin = max(0, int(np.searchsorted(native, lo, side='right'))-1)
            end = min(len(native)-1, int(np.searchsorted(native, hi, side='left')))
            termsN, termsU = [], []
            for i in range(begin, end):
                left, right = max(lo, native[i]), min(hi, native[i+1])
                if right <= left:
                    continue
                width = math.log(native[i+1]/native[i])
                t0, t1 = math.log(left/native[i])/width, math.log(right/native[i])/width
                f0 = (1.-t0)*profile[i]+t0*profile[i+1]
                f1 = (1.-t1)*profile[i]+t1*profile[i+1]
                dx = math.log(right/left)
                w0, w1 = weights_function(dx)
                termsN.append(dx*(f0+f1)*.5)
                termsU.append(dx*left*(f0*w0+f1*w1))
            N[a, cell] = prefactor*math.fsum(termsN)
            U[a, cell] = prefactor*math.fsum(termsU)
    if not np.isfinite(N).all() or not np.isfinite(U).all() or np.any(N < 0) or np.any(U < 0):
        raise FloatingPointError('Q1B_SOURCE_NONFINITE_OR_NEGATIVE_NO_CLIPPING')
    return {'N': N, 'U_eV': U, 'Q_eV': U/R[:, None], 'R': R.copy()}


class CellSource:
    """Unchanged physical provider bound to an immutable fixed-cell grid."""
    def __init__(self, provider, grid):
        from grid_cells import grid_array_sha256
        if grid_array_sha256(grid['q_edges_eV'], grid['initial_mu'], grid['angular_weights']) != grid['arrays_sha256']:
            raise ValueError('Q1B_SOURCE_GRID_IDENTITY')
        self.provider = provider
        self.edges = np.array(grid['q_edges_eV'])
        self.mu = np.array(grid['initial_mu'])
        self.weights = np.array(grid['angular_weights'])
        for a in (self.edges, self.mu, self.weights):
            a.flags.writeable = False

    def _band(self, band):
        value = self.provider.photon_band_eV if band is None else tuple(band)
        if len(value) != 2 or value[0] < self.provider.photon_band_eV[0] or value[1] > self.provider.photon_band_eV[1]:
            raise ValueError('Q1B_SOURCE_PHYSICAL_BAND')
        return value

    def source(self, t, band=None):
        geometry = self.provider.geometry(float(t))
        _, _, R = self.provider.ray(np.ones(len(self.mu)), self.mu, float(t))
        return table_cell_moments(self.provider.tables['emissivity'], geometry['z'],
                                  self.edges, R, self.weights, self._band(band))

    def initial(self, band=None):
        return table_cell_moments(self.provider.tables['uvb'], self.provider.z_initial,
                                  self.edges, np.ones(len(self.mu)), self.weights, self._band(band))


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _metric(actual, reference, subset):
    a, b = np.asarray(actual)[subset], np.asarray(reference)[subset]
    amplitude = float(np.max(np.abs(b)))
    absolute = float(np.max(np.abs(a-b)))
    error = absolute/amplitude if amplitude else (0. if absolute == 0 else None)
    return {'reference_amplitude_on_this_epoch_set': amplitude,
            'max_absolute_error': absolute, 'normalized_error': error,
            'target': 1e-12, 'pass': bool(error is not None and error <= 1e-12),
            'zero_reference_requires_exact_zero': True}


def check_saved_reference(args):
    """Partition-new-cells check against already saved Q0 values; no Q0 rerun."""
    from grid_cells import load_grid
    sys.path.insert(0, str(args.n1.resolve()))
    from provider import HistoryProvider
    start = time.monotonic()
    paths = [args.output, args.output.with_name('SOURCE_C1.npz'), args.output.with_name('SOURCE_C2.npz')]
    if any(x.exists() for x in paths):
        raise FileExistsError('Source evidence is create-only')
    saved = json.loads(args.saved_reference.read_text())
    provider = HistoryProvider(r=0.)
    if saved['source_implementation_sha256']['hm12_data.py'] != provider.identity['hm12_data.py']:
        raise ValueError('Q1B_SAVED_REFERENCE_PROVIDER_IDENTITY')
    rows = saved['exact_source_history']
    if len(rows) != 129 or rows[0]['time_s'] != 0.:
        raise ValueError('Q1B_SAVED_REFERENCE_EPOCHS')
    uvb_ref = saved['runs']['EVENT_COUPLED002']['initial_UVB_moment_comparison']
    bands = saved['bands_eV']
    output = {'schema': 'rei.q1b.source_ic_cells.v1', 'created_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'LOCAL_SOURCE_IC_ONLY_NOT_ODE_ADMISSION',
              'target': 1e-12, 'model_identity': 'UNKNOWN',
              'execution': {'old_RUN002_EVENT003_Q0_replays': 0, 'coupled_ODE': 0,
                            'native_calls': 0, 'new_cell_integrations': True},
              'input_identity': {'saved_reference_sha256': _digest(args.saved_reference),
                                 'provider': provider.identity,
                                 'source_cells.py': _digest(__file__),
                                 'grid_cells.py': _digest(HERE/'grid_cells.py'),
                                 'test_source_cells.py': _digest(HERE/'test_source_cells.py')},
              'reference_independence': 'Saved Q0 HM12Table.moment values are not recomputed. New cell sums share pinned data, redshift interpolation and analytic exponential weights with that reference; manufactured constant/log-linear/jump fixtures independently test the integral formulas. This is neither independent physical data nor a continuum certificate.',
              'units': {'N': 'reference cm^-3 (IC) or reference cm^-3 s^-1 (source)',
                        'U_eV': 'eV times N units', 'Q_eV': 'U_eV/R',
                        'energy_comparison': 'erg using EV_ERG=1.602176634e-12'},
              'scope': 'FLRW r=0, 129 saved epochs and65 even-index subset; source threshold selections are not opacity or photoheat moments',
              'members': {}}
    for label in ('C1', 'C2'):
        grid_path = args.grid_dir/('GRID_'+label+'.json')
        grid = load_grid(grid_path)
        source = CellSource(provider, grid)
        approx = {field: [] for field in rows[0] if field.endswith(('_ref', '_proper'))}
        full_N, full_U = [], []
        initial_values, initial_metrics = {}, {}
        for band_name, band in bands.items():
            ini = source.initial(band)
            for quantity, val in [('number', float(ini['N'].sum())), ('energy', float(ini['U_eV'].sum())*EV_ERG)]:
                field = band_name+'_'+quantity
                initial_values[field] = val
                initial_metrics[field] = _metric([val], [uvb_ref[field]['exact_declared_interpolation']], slice(None))
        max_z_error, max_Ra_error = 0., 0.
        for index, row in enumerate(rows):
            g = provider.geometry(row['time_s'])
            max_z_error = max(max_z_error, abs(g['z']-row['z']))
            for band_name, band in bands.items():
                result = source.source(row['time_s'], band)
                max_Ra_error = max(max_Ra_error, float(np.max(np.abs(result['R']*g['a_rel']-1))))
                if band_name == 'full':
                    full_N.append(result['N'])
                    full_U.append(result['U_eV'])
                values = {'number': float(result['N'].sum()), 'energy': float(result['U_eV'].sum())*EV_ERG}
                for quantity, value in values.items():
                    approx[band_name+'_'+quantity+'_ref'].append(value)
                    approx[band_name+'_'+quantity+'_proper'].append(value/g['a_rel']**3)
            if index % 32 == 0:
                print(json.dumps({'member': label, 'completed_epoch': index+1,
                                  'elapsed_s': time.monotonic()-start}), flush=True)
        metrics = {}
        for epoch_set, subset in [('shared129', slice(None)), ('shared65', slice(None, None, 2))]:
            metrics[epoch_set] = {field: _metric(values, [row[field] for row in rows], subset)
                                  for field, values in approx.items()}
        initial = source.initial()
        npz_path = args.output.with_name('SOURCE_'+label+'.npz')
        with npz_path.open('xb') as handle:
            np.savez_compressed(handle, times_s=[row['time_s'] for row in rows],
                                redshifts=[row['z'] for row in rows], source_N=full_N,
                                source_U_eV=full_U, initial_N=initial['N'], initial_U_eV=initial['U_eV'],
                                q_edges_eV=source.edges, initial_mu=source.mu,
                                angular_weights=source.weights)
        result = {'grid_sha256': _digest(grid_path), 'grid_arrays_sha256': grid['arrays_sha256'],
                  'energy_cells': grid['energy_cells'], 'total_cells': grid['total_cells'],
                  'source_metrics': metrics, 'initial_values': initial_values,
                  'initial_metrics': initial_metrics, 'source_sums': approx,
                  'max_geometry_z_minus_saved': max_z_error, 'max_R_a_minus_one': max_Ra_error,
                  'raw_arrays': {'path': str(npz_path.relative_to(HERE)), 'sha256': _digest(npz_path)}}
        result['pass'] = bool(max_z_error == 0. and max_Ra_error <= 1e-14
                              and all(m['pass'] for s in metrics.values() for m in s.values())
                              and all(m['pass'] for m in initial_metrics.values()))
        output['members'][label] = result
    output['pass'] = all(x['pass'] for x in output['members'].values())
    output['elapsed_s'] = time.monotonic()-start
    output['outcome'] = 'PASS_LOCAL_SOURCE_IC' if output['pass'] else 'FAIL_LOCAL_SOURCE_IC_NO_ODE'
    with args.output.open('x') as handle:
        json.dump(output, handle, indent=2, allow_nan=False)
        handle.write('\n')
    print(json.dumps({'outcome': output['outcome'], 'elapsed_s': output['elapsed_s']}), flush=True)
    return 0 if output['pass'] else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--n1', type=Path, default=HERE.parent/'n1')
    p.add_argument('--grid-dir', type=Path, default=HERE)
    p.add_argument('--saved-reference', type=Path, default=HERE.parent/'recovery/Q0_SOURCE_ATTRIBUTION.json')
    p.add_argument('--output', type=Path, default=HERE/'evidence/SOURCE_IC_CELL_CHECK.json')
    raise SystemExit(check_saved_reference(p.parse_args()))
