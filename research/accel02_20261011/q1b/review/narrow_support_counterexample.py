"""Independent affine-kernel check; no native provider, history or old test replay."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from reconstruction import reconstruct, opacity_moments


def run():
    rows = []
    for eps in [1e-4, 1e-6, 1e-8, 1e-10, 1e-12, 1e-14]:
        a = 50000.
        b = a * (1 + eps)
        N = R = 1.
        U = a + (b - a) / 3
        exact = (U / R - a * N) / (b - a)
        row = dict(relative_width=eps, a=a, b=b, N=N, U=U, R=R,
                   affine_kernel='(q-a)/(b-a)', exact_K0=exact)
        try:
            cell = reconstruct(N, U, R, a, b)
            out = opacity_moments(cell, lambda q: (q-a)/(b-a),
                                  orders=(64, 128), rtol=1e-7)
            error = abs(out['K0'] - exact) / exact
            row.update(p=cell.p, result=out, K0_relative_error=error,
                       acceptance='PASS_AFFINE_IDENTITY' if error <= 1e-7
                       else 'FALSE_SUCCESS_AFFINE_IDENTITY_VIOLATION')
        except Exception as exc:
            row.update(exception=type(exc).__name__, message=str(exc),
                       acceptance='EXPLICIT_FAILURE_NOT_FALSE_SUCCESS')
        rows.append(row)
    return dict(schema='rei.q1b.independent_narrow_support.v1',
                source_sha256=hashlib.sha256((HERE.parent/'reconstruction.py').read_bytes()).hexdigest(),
                derivation='For any distribution with moments N,Q, integral [(q-a)/(b-a)]F dlnq=(Q-a*N)/(b-a). No power-law oracle is needed.',
                physical_ODE_calls=0, native_calls=0, old_test_replays=0,
                cases=rows)


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, allow_nan=False))
