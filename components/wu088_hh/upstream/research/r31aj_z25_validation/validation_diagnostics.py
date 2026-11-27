"""R31AJ secondary norm diagnostics; never invokes a scientific producer.

The existing R31AI primary verdict/rule is not modified. All reference-error
bounds below are conditional inputs, not estimates derived from residuals.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from numbers import Real
from pathlib import Path

import numpy as np

TOLERANCE = 1e-10


def _nonnegative(x, name):
    if isinstance(x, (bool, np.bool_)) or not isinstance(x, Real):
        raise ValueError(name + ' must be a nonnegative finite real')
    x = float(x)
    if not math.isfinite(x) or x < 0:
        raise ValueError(name + ' must be a nonnegative finite real')
    return x


def _pair(xs, name):
    if not isinstance(xs, (list, tuple, np.ndarray)) or len(xs) != 2:
        raise ValueError(name + ' must contain [K,Dmax]')
    return [_nonnegative(x, name) for x in xs]


def margin_bounds(adaptive_errors, global_errors, reference_bounds=None):
    """Enclose true fixed-model margins by observed margin +/- 2*epsilon.

    Sign convention: positive global_error - adaptive_error favors adaptive.
    The optional conditional verdict is secondary; it does not replace the
    frozen primary verdict. Missing reference bounds stay missing, never zero.
    """
    a = _pair(adaptive_errors, 'adaptive_errors')
    g = _pair(global_errors, 'global_errors')
    delta = [gi-ai for gi, ai in zip(g,a)]
    result = {'observed_margins': delta, 'lower': None, 'upper': None,
              'conditional_pareto_support': None,
              'reference_bound_status': 'UNAVAILABLE',
              'source_accuracy_certified': False,
              'primary_rule_modified': False}
    if reference_bounds is None:
        return result
    eps = _pair(reference_bounds, 'reference_bounds')
    low = [d-2*x for d,x in zip(delta,eps)]
    high = [d+2*x for d,x in zip(delta,eps)]
    result.update(lower=low, upper=high,
        conditional_pareto_support=all(d >= -TOLERANCE for d in low)
                                   and any(d > TOLERANCE for d in low),
        reference_bound_status='SUPPLIED_BUT_NOT_CERTIFIED_BY_THIS_HELPER')
    return result


def block_error_bounds(eps_col, eps_row):
    """Map supplied block reference bounds to [epsilon_K,epsilon_Dmax]."""
    c = _nonnegative(eps_col, 'eps_col')
    r = _nonnegative(eps_row, 'eps_row')
    return [c/2+r/2, max(c,r)]


def strict_common_radius(adaptive_errors, global_errors):
    """Sufficient open radius for BOTH margins > tolerance; not maximal Pareto radius.

    This is a sensitivity budget, NOT a bound on the actual source error.
    It keeps the two model predictions fixed while perturbing their reference.
    """
    d = margin_bounds(adaptive_errors,global_errors)['observed_margins']
    r = min((x-TOLERANCE)/2 for x in d)
    return r if r > 0 else None


def midpoint_values(o0,o1,d0,d1,k0,k1,h):
    """Derived midpoint form of existing cubic-O/linear-K cell, not a new model."""
    h = _nonnegative(h, 'h')
    if h == 0:
        raise ValueError('h must be positive')
    mats = [np.asarray(a) for a in (o0,o1,d0,d1,k0,k1)]
    if any(a.ndim != 2 or a.shape != mats[0].shape or not np.isfinite(a).all() for a in mats):
        raise ValueError('six aligned finite matrix blocks required')
    o0,o1,d0,d1,k0,k1 = mats
    overlap = (o0+o1)/2 + h*(d0-d1)/8
    derivative = 3*(o1-o0)/(2*h) - (d0+d1)/4
    k = (k0+k1)/2
    return overlap,derivative,derivative/2+k,(derivative/2-k).conj().T,k


def canonical_scope_bytes(obj):
    """ASCII-only JSON with no floating numbers; decimal quantities are strings.

    This project-specific format is not claimed to be RFC 8785. No newline.
    """
    def check(x):
        if x is None or type(x) in (bool,int):
            return
        if type(x) is str and x.isascii():
            return
        if type(x) is list:
            for v in x: check(v)
            return
        if type(x) is dict:
            if any(type(k) is not str or not k.isascii() for k in x):
                raise ValueError('scope keys must be ASCII strings')
            for v in x.values(): check(v)
            return
        raise ValueError('scope permits ASCII strings, integers, booleans, null, lists and objects only')
    check(obj)
    return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')


def replay():
    z35a = [.06617406868623811,.06827426878354666]
    z35g = [.2504316158571644,.26534506458633733]
    return {
        'schema':'WU088_R31AJ_VALIDATION_DIAGNOSTICS_V1',
        'z25_direct_output_accessed':False,
        'new_science_node_count':0,
        'z25_model_only_half_gaps_per_ta':[.1912237840334797/2,.20561180584475613/2],
        'separation_guarantees_winner':False,
        'z25_validation_scope':'UNCHANGED_CENTRAL_CELL_NOT_REFINEMENT_GAIN_AT_END_CELLS',
        'historical_z35':{
            'source':'research/r31ah_post_z35/authorized_z35_20260930/Z35_COMPARISON.json',
            'source_blob':'42477aee71e947731ba214da9f3ae4e818a98e59',
            'margins':margin_bounds(z35a,z35g),
            'both_strict_common_reference_radius_open_per_ta':strict_common_radius(z35a,z35g),
            'radius_is_actual_source_error_bound':False},
        'missing_z25_reference_error_bound':'UNAVAILABLE_NOT_REPLACED_BY_TOLERANCE_OR_IDENTITY_RESIDUAL',
        'primary_rule_modified':False,
        'full_cell_admitted':False,'production_admitted':False,
        'native_evaluations':0}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    args = ap.parse_args()
    data = (json.dumps(replay(),indent=2,allow_nan=False)+'\n').encode()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('xb') as f:
        f.write(data); f.flush(); os.fsync(f.fileno())
    print(json.dumps({'out':str(args.out),'sha256':hashlib.sha256(data).hexdigest()}))


if __name__ == '__main__':
    main()
