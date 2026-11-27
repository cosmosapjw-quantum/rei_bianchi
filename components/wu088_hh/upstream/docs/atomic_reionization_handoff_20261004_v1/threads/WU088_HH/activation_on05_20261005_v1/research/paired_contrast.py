"""Exact differences of recorded floats; these are not continuum-error bounds."""
from fractions import Fraction
import math

def _exact(value):
    if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value):
        raise ValueError('FINITE_OBSERVABLE_REQUIRED')
    return Fraction(value)

def contrast(on,off):
    """Subtract before any reporting roundoff, with ON minus OFF convention."""
    return _exact(on)-_exact(off)

def refinement(on_coarse,off_coarse,on_fine,off_fine):
    coarse=contrast(on_coarse,off_coarse);fine=contrast(on_fine,off_fine)
    difference=fine-coarse
    return {'coarse':coarse,'fine':fine,'difference':difference,
            'on_increment':contrast(on_fine,on_coarse),
            'off_increment':contrast(off_fine,off_coarse),
            'relative_change':abs(difference/fine) if fine else None}

def assert_matched(on,off):
    """Require identical physical/control inputs; only HH identity may differ."""
    if on.get('mode') not in ('LCS','KS') or off.get('mode')!='OFF':
        raise ValueError('MATCHED_MODE_REQUIRED')
    omitted={'mode','research_model'}
    a={k:v for k,v in on.items() if k not in omitted}
    b={k:v for k,v in off.items() if k not in omitted}
    if a!=b:raise ValueError('MATCHED_INPUT_MISMATCH')
    return 'MATCHED_INPUTS'
