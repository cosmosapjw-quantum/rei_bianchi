"""B1: reproject frozen REI cell measures; never rerun the history ODE.

The original model freezes density and H at every log-a midpoint and stores
delta_tau = c sigma_REI n_sum_mid integral(Q du) / H_mid.  On the same u cells,
prescribing the FLRW Q history on the Bianchi proper clock therefore multiplies
its cell depth by H_F_mid/H_B_mid.  This is a cell-measure transformation, not
pointwise interpolation of the N4 proper-time average ne_eff.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT / 'research/broad_history_20261010/evidence/RUN002'
SIGMA_REI_M2 = 6.6524587321e-29
SIGMA_BASS_M2 = 6.6524587e-29
C_M_S = 299792458.0
MPC_CM = 3.0856775814913673e24
EXPECTED_HISTORY_SHA256 = {
    'flrw': '93d16f478d2cc28b1f7b3d5287f07432b0e17107b3dd3f684890e77f6133cfa4',
    'rp01': 'a2dcad2a81c4ff46b39890366d6fa5c37341e027e741687e35311fbebe66cd17',
}


def _read_case(name: str, original: Path) -> tuple[dict, dict]:
    folder = original / f'{name}_n16384'
    raw = (folder / 'history.npz').read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_HISTORY_SHA256[name]:
        raise ValueError(f'FROZEN_HISTORY_IDENTITY_MISMATCH:{name}')
    config = json.loads((folder / 'COMPLETE.json').read_text())['identity']['config']
    with np.load(folder / 'history.npz', allow_pickle=False) as archive:
        arrays = {key: archive[key].copy() for key in archive.files}
    if any(a.shape != (16385,) or not np.isfinite(a).all() for a in arrays.values()):
        raise ValueError(f'FROZEN_HISTORY_SCHEMA:{name}')
    return arrays, config


def load_projection(original: Path | None = None) -> dict[str, np.ndarray]:
    original = ORIGINAL if original is None else Path(original)
    f, cf = _read_case('flrw', original)
    b, cb = _read_case('rp01', original)
    if cf['r'] != 0.0 or cb['r'] != 0.1:
        raise ValueError('FROZEN_CASE_ASSIGNMENT')
    if {k: v for k, v in cf.items() if k != 'r'} != {k: v for k, v in cb.items() if k != 'r'}:
        raise ValueError('PAIR_NON_SHEAR_CONFIG_DIFFERS')
    if not np.array_equal(f['x'], b['x']) or not np.array_equal(f['nH_cm3'], b['nH_cm3']):
        raise ValueError('COMMON_MEAN_A_OR_DENSITY_REQUIRED')
    u = f['x']
    if not (np.all(np.diff(u) > 0) and u[0] == 0.0 and f['z'][0] == 20.0 and f['z'][-1] == 4.0):
        raise ValueError('FROZEN_CHART_DOMAIN')
    a_i = 1.0 / (1.0 + cf['z_i'])
    a_mid = a_i * np.exp((u[:-1] + u[1:]) * 0.5)
    hf = 100.0 * cf['h'] * 1e5 / MPC_CM
    density_term = hf * hf * cf['omega_m']
    lambda_term = hf * hf * (1.0 - cf['omega_m'])
    h_f_mid = np.sqrt(lambda_term + density_term / a_mid**3)
    h_b_initial = np.sqrt((lambda_term + density_term / a_i**3) / (1.0 - cb['r']**2))
    s0 = cb['r'] * h_b_initial * a_i**3
    h_b_mid = np.sqrt(lambda_term + density_term / a_mid**3 + s0**2 / a_mid**6)
    ratio_sigma = SIGMA_BASS_M2 / SIGMA_REI_M2
    depth_f = ratio_sigma * np.diff(f['tau'])
    depth_b = ratio_sigma * np.diff(b['tau'])
    depth_f_on_b = depth_f * (h_f_mid / h_b_mid)
    if not all(np.all(a >= 0.0) for a in [depth_f, depth_b, depth_f_on_b]):
        raise ValueError('NONPOSITIVE_CELL_MEASURE')
    return {
        'u': u, 'z_mean': f['z'],
        'b_B': b['b'], 'b_F': f['b'],
        'Q_B': b['Q'], 'Q_F': f['Q'],
        't_B_s': b['t_s'], 't_F_s': f['t_s'],
        'dt_B_s': np.diff(b['t_s']), 'dt_F_s': np.diff(f['t_s']),
        'H_B_mid_s': h_b_mid, 'H_F_mid_s': h_f_mid,
        'depth_B': depth_b, 'depth_F': depth_f, 'depth_F_on_B': depth_f_on_b,
        'nH_cm3': f['nH_cm3'],
    }


def coarsen(data: dict[str, np.ndarray], nsteps: int) -> dict[str, np.ndarray]:
    """Aggregate adjacent original optical-depth measures without re-solving Q.

    Midpoint H is intentionally not exported as a coarsened point value.
    Finite-step splitting/order error belongs to the new transport experiment.
    """
    native_n = len(data['u']) - 1
    if isinstance(nsteps, bool) or not isinstance(nsteps, int) or nsteps < 1 or native_n % nsteps:
        raise ValueError('NSTEPS_MUST_DIVIDE_ORIGINAL_16384')
    stride = native_n // nsteps
    edges = np.arange(0, native_n + 1, stride)
    out = {k: data[k][edges].copy() for k in ['u', 'z_mean', 'b_B', 'b_F', 'Q_B', 'Q_F', 't_B_s', 't_F_s', 'nH_cm3']}
    out.update({k: data[k].reshape(nsteps, stride).sum(axis=1) for k in ['depth_B', 'depth_F', 'depth_F_on_B']})
    out['dt_B_s'] = np.diff(out['t_B_s'])
    out['dt_F_s'] = np.diff(out['t_F_s'])
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = load_projection()
    with args.output.open('xb') as stream:
        np.savez_compressed(stream, **data)
    raw = args.output.read_bytes()
    print(json.dumps({'status': 'FROZEN_CELL_PROJECTION_WRITTEN', 'output': str(args.output),
                      'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                      'new_ODE_calls': 0,
                      'tau_F': float(data['depth_F'].sum()),
                      'tau_B': float(data['depth_B'].sum()),
                      'tau_F_on_B': float(data['depth_F_on_B'].sum())}))


if __name__ == '__main__':
    main()
