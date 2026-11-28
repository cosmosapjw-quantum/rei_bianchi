"""Bounded R10 research prototype: exact inverse-Laplace derivative weights.

This module does not edit or replace production code, generate O/H/D matrices,
or promote any scientific claim gate. Run with --parent PATH --output PATH.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import platform
import sys
import time
from pathlib import Path

try:
    import mpmath as mp
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent/'deps'))
    import mpmath as mp
import numpy as np
import scipy
from scipy.special import eval_hermite
from threadpoolctl import threadpool_limits


def exact_weights(t, w, mu=1.0):
    """Return U_i and V_i, i=0..8, including positive-axis quadrature weights.

    H_n are physicists' Hermite polynomials. All arrays here are real.
    This finite-order implementation is intended for the frozen B96--B192 nodes.
    """
    t = np.asarray(t, dtype=float)
    w = np.asarray(w, dtype=float)
    if t.shape != w.shape or np.any(t <= 0) or not np.isfinite(t).all() or not np.isfinite(w).all():
        raise ValueError('finite positive nodes and matching finite weights required')
    x = mu / (2 * np.sqrt(t))
    scale = 1 / (2 * np.sqrt(t))
    base = w * np.exp(-x*x) / (np.sqrt(np.pi) * np.sqrt(t))
    ladder = np.stack([base * eval_hermite(i, x) * scale**i for i in range(10)])
    return ladder[1:], ladder[:-1]


def contract(U, V, C):
    return np.stack([np.stack([left.T @ C[:, :, k] @ right for k in range(9)])
                     for left, right in ((U, U), (V, U), (U, V))])


def stats(a, b):
    difference = np.abs(a-b)
    idx = np.unravel_index(np.argmax(difference), difference.shape)
    norm = float(np.max(np.abs(b)))
    return {'max_abs_difference': float(np.max(difference)),
            'argmax': [int(x) for x in idx],
            'reference_max_abs': norm,
            'normalized_linf_difference': float(np.max(difference) / norm) if norm else 0.0,
            'max_imaginary_a': float(np.max(np.abs(np.imag(a)))),
            'max_imaginary_b': float(np.max(np.abs(np.imag(b))))}


def timing(fn, repeats):
    for _ in range(3):
        fn()
    times, cpu_times = [], []
    for _ in range(repeats):
        start = time.perf_counter()
        cpu_start = time.process_time()
        fn()
        cpu_times.append(time.process_time()-cpu_start)
        times.append(time.perf_counter()-start)
    return {'median_seconds': float(np.median(times)), 'minimum_seconds': min(times),
            'median_process_cpu_seconds': float(np.median(cpu_times)),
            'repeats': repeats}


def mp_density(t, i, kind):
    t = mp.mpf(t)
    if kind == 'U':
        f = lambda mu: mu * mp.exp(-mu*mu/(4*t))/(2*mp.sqrt(mp.pi)*t**mp.mpf('1.5'))
    else:
        f = lambda mu: mp.exp(-mu*mu/(4*t))/(mp.sqrt(mp.pi)*mp.sqrt(t))
    return (-1)**i * mp.diff(f, mp.mpf(1), i)


def derivative_controls(t, w, exact, fft):
    mp.mp.dps = 90
    controls = []
    for kind_index, kind in enumerate(('U', 'V')):
        for i in range(9):
            indices = {0, 1, len(t)//8, len(t)//2, len(t)-2, len(t)-1,
                       int(np.argmax(abs(exact[kind_index][i]-fft[kind_index][i]))),
                       int(np.argmax(abs(exact[kind_index][i])))}
            for j in sorted(indices):
                reference = mp_density(mp.mpf(float(t[j])), i, kind) * mp.mpf(float(w[j]))
                ex_error = abs(mp.mpf(float(exact[kind_index][i, j]))-reference)
                ff = fft[kind_index][i, j]
                fft_error = abs(mp.mpc(float(ff.real), float(ff.imag))-reference)
                controls.append({'kind': kind, 'degree': i, 'node_index': j, 't': float(t[j]),
                                 'reference_mp': mp.nstr(reference, 32),
                                 'exact_abs_error': float(ex_error),
                                 'fft_abs_error': float(fft_error),
                                 'exact_rel_error': float(ex_error/abs(reference)) if reference and abs(reference)>mp.mpf('1e-280') else None,
                                 'fft_rel_error': float(fft_error/abs(reference)) if reference and abs(reference)>mp.mpf('1e-280') else None})
    return {'precision_decimal_digits': 90, 'method': 'mpmath.diff of defining elementary density',
            'count': len(controls),
            'max_exact_abs_error': max(c['exact_abs_error'] for c in controls),
            'max_fft_abs_error': max(c['fft_abs_error'] for c in controls),
            'max_exact_rel_error_for_nonunderflow_reference': max(c['exact_rel_error'] or 0 for c in controls),
            'max_fft_rel_error_for_nonunderflow_reference': max(c['fft_rel_error'] or 0 for c in controls),
            'controls': controls}


def integral_controls():
    # Independent moment target: r^i exp(-mu r) and r^(i-1) exp(-mu r).
    # Integrand uses explicit Hermite evaluation, not differentiation.
    mp.mp.dps = 60
    results = []
    for r in map(mp.mpf, ('0.25', '1', '3')):
        for kind in ('U', 'V'):
            for i in (0, 1, 2, 5, 8):
                order = i + (kind == 'U')
                def integrand(t):
                    x = 1/(2*mp.sqrt(t))
                    return mp.exp(-x*x-t*r*r)*mp.hermite(order, x)/(mp.sqrt(mp.pi*t)*(2*mp.sqrt(t))**order)
                computed = mp.quad(integrand, [0, mp.mpf('0.01'), mp.mpf('0.1'), 1, 10, mp.inf])
                reference = r**(i-(kind == 'V')) * mp.exp(-r)
                results.append({'kind': kind, 'degree': i, 'r': str(r),
                                'computed': mp.nstr(computed, 32), 'reference': mp.nstr(reference, 32),
                                'absolute_error': float(abs(computed-reference)),
                                'relative_error': float(abs((computed-reference)/reference))})
    return {'precision_decimal_digits': 60, 'count': len(results),
            'max_relative_error': max(c['relative_error'] for c in results), 'controls': results}


def donor_point_controls(t, C, exact, fft):
    # Donor polynomial evaluation, deliberately independent of Gaussian radial kernels.
    out = []
    for r1, r2, r12 in ((.25,.25,.25), (1,1,1), (3,2,2), (8,7,4), (20,18,8)):
        e1, e2 = np.exp(-t*r1*r1), np.exp(-t*r2*r2)
        exact_i = exact[0] @ e1
        exact_j = exact[0] @ e2
        fft_i = fft[0] @ e1
        fft_j = fft[0] @ e2
        kp = r12**np.arange(9)
        polynomial = np.einsum('i,ijk,j,k', r1**np.arange(9), C, r2**np.arange(9), kp)
        reference = np.exp(-r1-r2)*polynomial
        ex = np.einsum('i,ijk,j,k', exact_i, C, exact_j, kp)
        ff = np.einsum('i,ijk,j,k', fft_i, C, fft_j, kp)
        out.append({'r1': r1, 'r2': r2, 'r12': r12, 'reference': float(reference),
                    'exact_weight_result': float(ex), 'fft_weight_result_real': float(ff.real),
                    'fft_weight_result_imag': float(ff.imag), 'exact_abs_error': float(abs(ex-reference)),
                    'fft_abs_error': float(abs(ff-reference)), 'fft_vs_exact_abs': float(abs(ff-ex))})
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--parent', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    parent = args.parent.resolve()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(parent/'src'))
    blocks = importlib.import_module('r10_blocks')
    with np.load(parent/'inputs/FROZEN_INPUTS.npz', allow_pickle=False) as data:
        C = data['C']
    source_paths = ('src/r10_blocks.py', 'src/r10_kernel.py', 'inputs/FROZEN_INPUTS.npz')
    hashes = {p: hashlib.sha256((parent/p).read_bytes()).hexdigest() for p in source_paths}
    result = {'status': 'RESEARCH_PROTOTYPE_ONLY__NO_PRODUCTION_GATE_PROMOTION',
              'parent': str(parent), 'parent_sha256': hashes,
              'runtime': {'python': platform.python_version(), 'numpy': np.__version__,
                          'scipy': scipy.__version__, 'mpmath': mp.__version__,
                          'BLAS_threads_for_benchmark': 1},
              'C_shape': list(C.shape), 'C_nonzero': int(np.count_nonzero(C)),
              'method': 'physicists-Hermite closed form at mu=1; no Cauchy contour',
              'grids': {}}
    with threadpool_limits(limits=1):
        for n in (96,128,192):
            t, w = blocks.nodes(n)
            ex = exact_weights(t, w)
            ff = (blocks.cauchy_U(t, w), blocks.cauchy_U(t, w, 'wm1'))
            ce, cf = contract(*ex, C), contract(*ff, C)
            exact_time = timing(lambda: exact_weights(t,w), 60)
            fft_time = timing(lambda: (blocks.cauchy_U(t,w),blocks.cauchy_U(t,w,'wm1')), 30)
            exact_contract_time = timing(lambda: contract(*ex,C), 15)
            fft_contract_time = timing(lambda: contract(*ff,C), 15)
            grid = {'minimum_node': float(t.min()), 'maximum_node': float(t.max()),
                    'U_by_degree': [stats(ff[0][i], ex[0][i]) for i in range(9)],
                    'V_by_degree': [stats(ff[1][i], ex[1][i]) for i in range(9)],
                    'contracted_by_kind_and_k': {name: [stats(cf[j,k],ce[j,k]) for k in range(9)]
                                                  for j,name in enumerate(('UU','VU','UV'))},
                    'all_contractions': stats(cf,ce),
                    'timing': {'exact_weights': exact_time, 'fft_weights': fft_time,
                               'weight_speedup_median': fft_time['median_seconds']/exact_time['median_seconds'],
                               'exact_real_contractions': exact_contract_time,
                               'fft_complex_contractions': fft_contract_time,
                               'contraction_speedup_median': fft_contract_time['median_seconds']/exact_contract_time['median_seconds']},
                    'donor_point_controls': donor_point_controls(t,C,ex,ff)}
            if n in (128,192):
                grid['high_precision_derivative_controls'] = derivative_controls(t,w,ex,ff)
            result['grids'][str(n)] = grid
            print('GRID', n, 'weight_speedup', grid['timing']['weight_speedup_median'],
                  'max_contraction_difference', grid['all_contractions']['max_abs_difference'], flush=True)
        result['inverse_laplace_moment_controls'] = integral_controls()
    result['parent_hashes_unchanged'] = all(hashlib.sha256((parent/p).read_bytes()).hexdigest()==v for p,v in hashes.items())
    out = args.output/'EXACT_LAPLACE_WEIGHT_DIAGNOSTIC.json'
    out.write_text(json.dumps(result, indent=2)+'\n')
    print('WROTE',out,flush=True)
    print('MOMENT_MAX_RELATIVE_ERROR', result['inverse_laplace_moment_controls']['max_relative_error'])
    print('PARENT_HASHES_UNCHANGED',result['parent_hashes_unchanged'])


if __name__ == '__main__':
    main()
