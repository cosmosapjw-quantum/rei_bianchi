"""Frozen 94-entry H order-comparison gate. Not a rigorous continuum error bound."""
from __future__ import annotations
import numpy as np

THRESHOLD_EH=np.longdouble('2e-7')

def compare_h(a:np.ndarray,b:np.ndarray) -> dict:
    a=np.asarray(a);b=np.asarray(b)
    if a.shape!=(47,2) or b.shape!=(47,2):raise ValueError('require exactly 47x2 H entries')
    if not np.isfinite(a).all() or not np.isfinite(b).all():raise ValueError('nonfinite H array')
    # No dtype conversion before subtraction or gate evaluation.
    delta=np.abs(b-a);ix=np.unravel_index(delta.argmax(),delta.shape)
    failures=int(np.count_nonzero(delta>THRESHOLD_EH))
    return dict(status='PASS_H_ORDER_COMPARISON' if not failures else 'FAIL_H_ORDER_COMPARISON',
                entries=94,threshold_Eh=float(THRESHOLD_EH),max_abs_H192_minus_H160_Eh=float(delta[ix]),
                worst_index=[int(k) for k in ix],failure_count=failures,
                rigorous_continuum_error_bound=False,full49_admitted=False,trajectory_admitted=False)
