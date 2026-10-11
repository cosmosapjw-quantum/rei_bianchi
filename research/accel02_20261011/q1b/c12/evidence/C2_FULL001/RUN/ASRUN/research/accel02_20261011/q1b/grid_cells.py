"""Frozen Q1B fixed-covector cell pair. No transported quadrature nodes."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent


def grid_array_sha256(edges, mu, weights):
    h = hashlib.sha256()
    for values in (edges, mu, weights):
        a = np.asarray(values, dtype='<f8')
        h.update(np.asarray(a.shape, dtype='<i8').tobytes())
        h.update(a.tobytes())
    return h.hexdigest()


def build_grid(uvb_table, q_max_eV, member=1):
    if member not in (1, 2) or not np.isfinite(q_max_eV) or q_max_eV <= 50000.:
        raise ValueError('Q1B_GRID_DOMAIN')
    e = uvb_table.energies_eV
    profiles = uvb_table.spectra[::-1]
    unequal = (np.diff(e) == 0) & np.any(profiles[:-1] != profiles[1:], axis=1)
    jumps = e[:-1][unequal]
    jumps = jumps[(jumps >= 10.) & (jumps <= q_max_eV)]
    base = np.geomspace(10., q_max_eV, 65)
    base[0], base[-1] = 10., q_max_eV
    features = np.r_[jumps, [13.60, 24.59, 54.42, 50000.]]
    coarse = np.unique(np.r_[base, features])
    edges = coarse
    if member == 2:
        edges = np.empty(2*len(coarse)-1)
        edges[::2] = coarse
        edges[1::2] = np.exp(.5*(np.log(coarse[:-1])+np.log(coarse[1:])))
    mu, weights = np.polynomial.legendre.leggauss(2)
    weights /= 2.
    if not np.all(np.diff(edges) > 0):
        raise ValueError('Q1B_GRID_NONPOSITIVE_CELL')
    return {
        'schema': 'rei.q1b.fixed_cell_grid.v1',
        'member': 'C'+str(member),
        'energy_cells': len(edges)-1,
        'angular_ordinates': 2,
        'total_cells': 2*(len(edges)-1),
        'state_per_cell': ['N_reference_cm^-3', 'U_eV_reference_cm^-3'],
        'construction': '64 log-q base intervals union all unequal duplicate UVB jumps in domain, sigma thresholds13.60/24.59/54.42, initial50000eV; C2 bisects each C1 log-q cell',
        'base_intervals': 64,
        'q_edges_eV': edges.tolist(),
        'initial_mu': mu.tolist(),
        'angular_weights': weights.tolist(),
        'initial_UVB_unequal_jump_edges_eV': jumps.tolist(),
        'native_cross_section_thresholds_eV': [13.60, 24.59, 54.42],
        'native_source_duplicate_eV': 54.37903440052643,
        'native_source_duplicate_note': 'Its two emissivity ordinates are equal; same location is an unequal UVB jump and remains distinct from54.42eV sigma threshold.',
        'uvb_sha256': uvb_table.source_sha256,
        'arrays_sha256': grid_array_sha256(edges, mu, weights),
        'hash_encoding': 'ordered q_edges,initial_mu,weights; each little-endian int64 shape then little-endian float64 data',
        'frozen': True,
        'scope': 'new numerical candidate; no ODE or spectral admission from grid construction',
    }


def load_grid(path):
    value = json.loads(Path(path).read_text())
    actual = grid_array_sha256(value['q_edges_eV'], value['initial_mu'], value['angular_weights'])
    if actual != value['arrays_sha256']:
        raise ValueError('Q1B_GRID_IDENTITY')
    return value


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--n1', type=Path, default=HERE.parent/'n1')
    p.add_argument('--output-dir', type=Path, default=HERE)
    args = p.parse_args()
    sys.path.insert(0, str(args.n1.resolve()))
    from provider import HistoryProvider
    provider = HistoryProvider(r=0.)
    outputs = [args.output_dir/'GRID_C1.json', args.output_dir/'GRID_C2.json']
    if any(x.exists() for x in outputs):
        raise FileExistsError('Frozen grids are create-only')
    for member, path in enumerate(outputs, 1):
        grid = build_grid(provider.tables['uvb'], provider.q_max_eV, member)
        grid['provider_identity'] = provider.identity
        grid['grid_implementation_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        path.write_text(json.dumps(grid, indent=2, allow_nan=False)+'\n')
        print(json.dumps({'path': str(path), 'energy_cells': grid['energy_cells'],
                          'arrays_sha256': grid['arrays_sha256']}), flush=True)


if __name__ == '__main__':
    main()
