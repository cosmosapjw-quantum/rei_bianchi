"""Manufactured spline parity; no eigensolve and no scientific convergence claim."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'code'))
sys.path.insert(0, str(ROOT.parent/'BASS_HE_C1_ELECTRONIC_ARCHITECTURE_20261001_v1/code'))
import prolate_fast as fast
import coupling as reference
from spheroidal import _Axis, SpheroidalState, SpheroidalConfig


def pair():
    result = []
    for m in (0, 1):
        cfg = SpheroidalConfig(degree=3, radial_elements=6, angular_elements=5,
                               quadrature_order=8, radial_extent=7.)
        radial = _Axis(np.linspace(1, 8, 7), 3, 8, m, True)
        angular = _Axis(np.linspace(-1, 1, 6), 3, 8, m, False)
        cr = np.exp(-np.arange(radial.mass.shape[0])*.25)*(1+.1*m)
        ca = 1+.05*np.arange(angular.mass.shape[0])
        result.append(SpheroidalState(2., 1., 2., m, cfg, -2.5+1.6*m,
                      0., 0., .71+.3*m, -1., {}, cr, ca, radial, angular))
    return result


def outputs():
    g, b = pair()
    return {k: fn(g, b, order=8, backend='native') for k, fn in
            [('direct', fast.direct), ('torque', fast.torque)]}


def main():
    if '--thread-child' in sys.argv:
        print(json.dumps(outputs(), sort_keys=True))
        return
    checks = {}
    g, b = pair()
    xi = np.linspace(1.001, 7.999, 73)
    eta = np.linspace(-.999, .999, 73)
    checks['scalar_spline_evaluate_max_abs'] = max(float(np.max(np.abs(a-c))) for s in (g,b)
        for a,c in zip(s.evaluate(xi, eta), fast.evaluate(s, xi, eta)))
    checks['endpoint_values_finite'] = bool(np.all(np.isfinite(fast.values(b, [1, 8], [-1, 1]))))
    differences = {}
    for lane in ('direct', 'torque'):
        ref = getattr(reference, lane)(g,b,order=8)
        for backend in ('python', 'native'):
            got = getattr(fast, lane)(g,b,order=8,backend=backend)
            differences[lane+'_'+backend] = {k: abs(v-got[k]) for k,v in ref.items()
                                            if isinstance(v, float)}
    checks['reference_parity_max_abs'] = max(v for lane in differences.values() for v in lane.values())
    checks['parity_tolerance'] = 1e-11
    checks['dark'] = [fast.dark(g,b,order=8,phi_nodes=n) for n in (32,64)]
    invalids = [lambda: fast.direct(g,b,backend='fallback'),
                lambda: fast.direct(g,b,order=True),
                lambda: fast.values(b, [0.9], [0.]),
                lambda: fast.evaluate(b, [1.], [0.])]
    checks['invalid_inputs_fail_closed'] = []
    for fn in invalids:
        try:
            fn()
        except ValueError:
            checks['invalid_inputs_fail_closed'].append(True)
        else:
            checks['invalid_inputs_fail_closed'].append(False)
    old = os.environ.get('BASS_PROLATE_EXPECTED_SHA256')
    os.environ['BASS_PROLATE_EXPECTED_SHA256'] = '0'*64
    try:
        fast.native_identity()
    except RuntimeError:
        checks['wrong_expected_sha_rejected'] = True
    else:
        checks['wrong_expected_sha_rejected'] = False
    finally:
        if old is None:
            os.environ.pop('BASS_PROLATE_EXPECTED_SHA256')
        else:
            os.environ['BASS_PROLATE_EXPECTED_SHA256'] = old
    child_outputs = []
    for threads in (1, 2):
        env = dict(os.environ, OMP_NUM_THREADS=str(threads), OPENBLAS_NUM_THREADS='1')
        child_outputs.append(subprocess.check_output([sys.executable, __file__, '--thread-child'], env=env, text=True))
    checks['native_threads_1_2_bitwise_same_json'] = child_outputs[0] == child_outputs[1]
    checks['passed'] = (checks['scalar_spline_evaluate_max_abs'] < 1e-11 and
        checks['endpoint_values_finite'] and checks['reference_parity_max_abs'] < 1e-11 and
        all(checks['invalid_inputs_fail_closed']) and checks['wrong_expected_sha_rejected'] and
        checks['native_threads_1_2_bitwise_same_json'] and
        all(abs(d['L_dark_O_bar']) < 1e-12 for d in checks['dark']))
    result = {'scope':'manufactured finite spline states; no eigensolves', 'checks':checks,
              'differences':differences, 'native_identity':fast.native_identity()}
    output = ROOT/'review/PROLATE_OPTIMIZATION_MANUFACTURED.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(checks, indent=2))
    assert checks['passed']

if __name__ == '__main__':
    main()
