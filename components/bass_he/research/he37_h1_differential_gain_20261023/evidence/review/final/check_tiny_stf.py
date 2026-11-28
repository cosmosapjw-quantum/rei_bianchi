"""One targeted call: tiny diagonal STF must survive the isotropic sum.

No prior suite, model diagnostic, IVP, benchmark, or render is replayed.
The new control resolves the specific cancellation risk in net_source lines
195--203. Author files are read only and bytecode writes are disabled.
"""
from pathlib import Path
from decimal import Decimal, localcontext
import datetime
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "TINY_STF_OBSERVATION.json"
if OUT.exists():
    raise SystemExit("Existing targeted evidence must be reused")
PACKAGE = Path('/tmp/he37_net_bridge')
SOURCE = PACKAGE / 'h1_net/net_source.py'
EXPECTED = '34147e2a6b7644b5509189037e26d6f9f469bd618588fb2266c7225027d8e379'
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(SOURCE) == EXPECTED
sys.path.insert(0, str(PACKAGE))
import numpy as np
from h1_net import h1_ci_source, ALL_RETAINED_THERMAL, NEUTRAL_21_STATE_CENSUS

result = {
    'purpose': 'Preserve a tiny diagonal electron STF when full isotropic S cannot resolve it',
    'source_sha256': EXPECTED,
    'script_sha256': digest(__file__),
    'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'new_h1_ci_source_calls': 1,
    'new_provider_temperature_evaluations': 1,
    'old_suite_replays': 0,
    'model_diagnostic_replays': 0,
    'IVPs': 0,
    'benchmarks': 0,
    'renders': 0,
}
try:
    y = np.zeros(21)
    y[1], y[2] = .7, .3
    pi = np.diag([1.e-200, -1.e-200, 0.])
    out = h1_ci_source(20000., y, 1.e6, pi,
        thermal_inventory_scope=ALL_RETAINED_THERMAL,
        charge_census_scope=NEUTRAL_21_STATE_CENSUS)
    with localcontext() as ctx:
        ctx.prec = 80
        ref = float(-Decimal.from_float(out.nH_m3)
                    * Decimal.from_float(out.kappa2_m3_s)
                    * Decimal.from_float(float(pi[0,0])))
    relative = abs(float(out.J[0,0]) / ref - 1.)
    assert out.J[0,0] != 0 and out.J[1,1] == -out.J[0,0]
    assert relative < 2.e-15
    assert out.J[2,2] == 0
    result.update({
        'status': 'PASS', 'input_pi_diagonal_Pa': np.diag(pi).tolist(),
        'returned_J_diagonal_Pa_s': np.diag(out.J).tolist(),
        'donor_projected_J_diagonal_Pa_s': np.diag(out.event_tensor_source.J).tolist(),
        'returned_S_diagonal_Pa_s': np.diag(out.S).tolist(),
        'source_scale': float(np.max(np.abs(out.S))),
        'expected_J00_decimal_product_rounded_binary64': ref,
        'relative_J00_error': relative,
        'electron_grad_relative_norm': out.electron_grad_relative_norm,
        'Q_W_m3': out.Q,
        'model_identity': out.model_identity,
        'interpretation': 'Use the returned direct J. Reprojecting the rounded full S cannot recover a diagonal STF far below its isotropic scale.',
    })
except Exception as exc:
    result.update({'status': 'FAIL', 'exception': type(exc).__name__, 'message': str(exc)})
    raise
finally:
    with OUT.open('x') as f:
        json.dump(result, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
print(json.dumps(result, indent=2))
