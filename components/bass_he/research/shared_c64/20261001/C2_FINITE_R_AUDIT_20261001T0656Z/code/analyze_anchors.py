"""Hash-checked C2 spherical anchors; reconstruction only, no eigensolves.

The C1b R=2 numbers are reused as recorded. New R=.5 and R=8 archived
coefficients are evaluated with the pinned HPC sparse direct operators.
Their fixed physical-O convention is L_O = L_B + ZA*R/(ZA+ZB)*p_x.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def atomic_create_json(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name+f'.{os.getpid()}.tmp')
    with temp.open('xb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.link(temp, path)
    finally:
        temp.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hpc-parent', type=Path, default=ROOT.parent/'BASS_HE_NCP64_OPTIMIZATION_20261001_v1')
    parser.add_argument('--c1b-parent', type=Path, default=ROOT.parent/'BASS_HE_C1B_REFERENCE_CONVERGENCE_20261001_v1')
    parser.add_argument('--prolate-root', type=Path, default=ROOT/'evidence'/'PROLATE_MPI')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--allow-pending', action='store_true')
    args = parser.parse_args()
    if os.environ.get('OPENBLAS_NUM_THREADS') != '1' or os.environ.get('OMP_NUM_THREADS') != '1':
        raise RuntimeError('Run with OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1')
    sys.path[:0] = [str(args.hpc_parent/'code'), str(args.hpc_parent/'reference')]
    import numpy as np
    from optimized_solver import PartialWaveState
    from fast_observables import direct_observables

    contract = read_json(ROOT/'CONTRACT.json')
    criteria = contract['criteria']
    sources = {name: sha(args.hpc_parent/name) for name in (
        'code/optimized_solver.py', 'code/fast_observables.py',
        'reference/partialwave_centered.py')}
    audit = {
        'schema': 'c2-spherical-anchors-v1',
        'contract_sha256': sha(ROOT/'CONTRACT.json'),
        'analysis_code_sha256': sha(Path(__file__)),
        'operator': 'HPC fast_observables.direct_observables; radial quadrature 14; exact sparse angular selection; independent momentum derivative',
        'source_sha256': sources,
        'phase_convention': 'Archived positive nine-point meridional phase, verified without changing coefficients; same C1b convention.',
        'comparison': 'signed physical charge-center O matrix elements; no absolute-value phase fitting',
        'new_eigensolves_performed_by_analysis': 0,
        'R2_eigensolves_rerun': False,
        'claim_scope': 'empirical independent discretization checks only; no continuum enclosure or global-R certificate',
        'new_anchors': [],
        'independent_comparisons': [],
    }
    selected = {}
    for R, tag in ((0.5, 'R0p5'), (8.0, 'R8')):
        rows = []
        for lmax in contract['independent_spherical_anchors']['lmax']:
            states, state_identities = [], []
            for m in (0, 1):
                folder = ROOT/'evidence'/'SPHERICAL_MPI'/f'{tag}_l{lmax}_m{m}'
                result_path = folder/'RESULT.json'
                result = read_json(result_path)
                assert result['status'] == 'PASS'
                for name, digest in sources.items():
                    assert result['code_sha256'][name] == digest, name
                state_path = folder/result['state_file']
                assert sha(state_path) == result['state_sha256']
                assert state_path.stat().st_size == result['state_bytes']
                p = result['parameters']
                assert p['R'] == R and p['m'] == m and p['lmax'] == lmax
                assert p['center'] == 'B'
                with np.load(state_path, allow_pickle=False) as arrays:
                    state = PartialWaveState(R, 1., 2., m, arrays['ls'], arrays['boundaries'],
                        p['degree'], arrays['coefficients'], result['energy'], result['residual'],
                        result['mass_norm'], 0., result['metadata'])
                radius = max(0.1, min(1., float(state.boundaries[-1])/4))
                phase = float(np.sum(state.evaluate(np.full(9, radius), np.linspace(-0.8, 0.8, 9))[0]))
                if not np.isfinite(phase) or phase <= 0:
                    raise ArithmeticError('Archived state fails the fixed C1b phase convention')
                state.phase_probe = phase
                states.append(state)
                state_identities.append({'path': state_path.relative_to(ROOT).as_posix(),
                    'sha256': sha(state_path), 'result_sha256': sha(result_path),
                    'phase_probe': phase, 'algebraic_residual': result['residual'],
                    'mass_norm': result['mass_norm']})
            row = {'R': R, 'lmax': lmax, 'energies': [s.energy for s in states],
                'direct': direct_observables(*states, quadrature=14), 'states': state_identities}
            rows.append(row)
        increments = {k: abs(rows[1]['direct'][k]-rows[0]['direct'][k]) for k in (
            'L_O_over_minus_i_hbar', 'L_center_over_minus_i_hbar',
            'p_x_over_minus_i_hbar', 'dipole_x')}
        audit['new_anchors'].append({'R': R, 'levels': rows, 'l72_to_l96_abs': increments,
            'energy_l72_to_l96_abs': [abs(b-a) for a, b in zip(rows[0]['energies'], rows[1]['energies'])],
            'increment_gate_threshold': criteria['independent_spherical_increment_abs'],
            'L_O_increment_gate_pass': increments['L_O_over_minus_i_hbar'] <= criteria['independent_spherical_increment_abs']})
        selected[R] = rows[-1]

    frozen_path = ROOT/'provenance'/'C1B_R2_ANCHOR.json'
    frozen = read_json(frozen_path)
    parent_anchor = args.c1b_parent/'evidence'/'B_l96.json'
    assert sha(frozen_path) == sha(parent_anchor), 'C1b reused evidence differs from parent'
    previous_path = args.c1b_parent/'evidence'/'B_l72.json'
    previous = read_json(previous_path)
    increment = abs(frozen['direct']['L_O_over_minus_i_hbar']-previous['direct']['L_O_over_minus_i_hbar'])
    audit['reused_R2'] = {'source': frozen_path.relative_to(ROOT).as_posix(),
        'sha256': sha(frozen_path), 'parent_l72_sha256': sha(previous_path),
        'l72_to_l96_L_O_abs': increment,
        'increment_gate_pass': increment <= criteria['independent_spherical_increment_abs'],
        'recomputed_operators': False, 'rerun_eigensolves': False}
    selected[2.] = {'energies': [s['energy'] for s in frozen['states']], 'direct': frozen['direct']}
    for R, tag in ((0.5, 'R0p5'), (2., 'R2'), (8., 'R8')):
        prolate_path = args.prolate_root/f'{tag}_base'/'RESULT.json'
        if not prolate_path.is_file():
            if not args.allow_pending:
                raise FileNotFoundError(prolate_path)
            audit['independent_comparisons'].append({'R': R, 'status': 'PENDING_PROLATE_BASE'})
            continue
        prolate = read_json(prolate_path)
        assert prolate['status'] == 'PASS' and prolate['parameters']['R'] == R
        scalar = prolate['operators']['direct']['24']
        energy_abs = [abs(a-b) for a, b in zip(selected[R]['energies'], prolate['energies'])]
        direct = selected[R]['direct']
        discrepancies = {k: abs(direct[skey]-scalar[pkey]) for k, skey, pkey in (
            ('L_O_abs', 'L_O_over_minus_i_hbar', 'L_O_bar'),
            ('L_B_abs', 'L_center_over_minus_i_hbar', 'L_B_bar'),
            ('p_x_abs', 'p_x_over_minus_i_hbar', 'p_x_bar'),
            ('dipole_x_abs', 'dipole_x', 'dipole_x'))}
        gates = {'energies': max(energy_abs) <= criteria['independent_spherical_energy_abs'],
            'L_O': discrepancies['L_O_abs'] <= criteria['independent_spherical_L_O_abs']}
        audit['independent_comparisons'].append({'R': R, 'status': 'PASS' if all(gates.values()) else 'FAIL',
            'prolate_result_path': str(prolate_path.relative_to(ROOT)), 'prolate_result_sha256': sha(prolate_path),
            'energy_abs': energy_abs, **discrepancies, 'gates': gates})
    audit['all_anchor_gates_pass'] = (all(row['L_O_increment_gate_pass'] for row in audit['new_anchors'])
        and audit['reused_R2']['increment_gate_pass']
        and all(row['status'] == 'PASS' for row in audit['independent_comparisons']))
    if args.output:
        atomic_create_json(args.output, audit)
    print(json.dumps(audit, indent=2, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
