"""Opt-in block maximum of SciPy DOP853 embedded-error estimates.

Only _estimate_error_norm changes. Stage equations, dense interpolation and
initial-step selection are inherited unchanged from the installed SciPy.
"""
import hashlib
import inspect
import math

import numpy as np
import scipy
from scipy.integrate._ivp.rk import DOP853


def error_control_identity():
    source = inspect.getsource(DOP853._estimate_error_norm)
    return dict(scipy_version=scipy.__version__,
                scipy_estimator_sha256=hashlib.sha256(source.encode()).hexdigest(),
                estimator='DOP853._estimate_error_norm')


def validate_blocks(block_sizes, dimension):
    blocks = tuple(block_sizes)
    if (not blocks or any(isinstance(n, bool) or not isinstance(n, int) or n <= 0 for n in blocks)
            or sum(blocks) != dimension):
        raise ValueError('ERROR_BLOCK_PARTITION')
    return blocks


def production_blocks(dimension):
    if not isinstance(dimension, int) or dimension < 18:
        raise ValueError('PRODUCTION_COMPRESSED_DIMENSION')
    logs = dimension-18
    return (4,) + ((logs,) if logs else ()) + (1,)*14


def positive_product(factors):
    mantissa, exponent = 1., 0
    for value in factors:
        if value == 0:
            return 0.
        part, shift = math.frexp(value)
        mantissa *= part
        exponent += shift
    try:
        return math.ldexp(mantissa, exponent)
    except OverflowError:
        return math.inf


def block_error_norm(err5, err3, h, block_sizes):
    err5 = np.asarray(err5, dtype=float)
    err3 = np.asarray(err3, dtype=float)
    if err5.ndim != 1 or err3.shape != err5.shape:
        raise ValueError('ERROR_ARRAY_DIMENSION')
    blocks = validate_blocks(block_sizes, err5.size)
    if not math.isfinite(h) or not np.isfinite(err5).all() or not np.isfinite(err3).all():
        raise ValueError('NONFINITE_ERROR_ESTIMATE')
    result = 0.
    start = 0
    for size in blocks:
        a = err5[start:start+size]
        b = err3[start:start+size]
        scale = max(float(np.max(np.abs(a))), float(np.max(np.abs(b))))
        if scale:
            an = float(np.linalg.norm(a/scale))
            bn = float(np.linalg.norm(b/scale))
            # |h| A/sqrt(m(A+.01B)), A=||err5||², B=||err3||².
            value = positive_product((abs(h), scale, an/math.hypot(an, .1*bn), an/math.sqrt(size)))
            result = max(result, value)
        start += size
    return result


def make_block_dop853(block_sizes):
    """Bind an explicit complete partition to a solve_ivp method class."""
    blocks = tuple(block_sizes)

    class BlockDOP853(DOP853):
        def __init__(self, fun, t0, y0, t_bound, **kwargs):
            self.block_sizes = validate_blocks(blocks, len(y0))
            super().__init__(fun, t0, y0, t_bound, **kwargs)

        def _estimate_error_norm(self, K, h, scale):
            if not np.isfinite(scale).all() or np.any(scale <= 0):
                raise ValueError('ERROR_SCALE_DOMAIN')
            err5 = np.dot(K.T, self.E5)/scale
            err3 = np.dot(K.T, self.E3)/scale
            return block_error_norm(err5, err3, h, self.block_sizes)

    return BlockDOP853
