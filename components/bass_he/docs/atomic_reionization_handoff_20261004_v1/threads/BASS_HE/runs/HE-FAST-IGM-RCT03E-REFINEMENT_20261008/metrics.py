"""Finite-grid diagnostics, never a certified exact-flow error bound."""
from fractions import Fraction
import math
EPS=1.602176634e-12

def allowance_ratio(a,b,absolute,relative):
    if not all(math.isfinite(x) for x in (a,b,absolute,relative)) or absolute<=0 or relative<0:
        raise ValueError('finite values and positive absolute allowance required')
    return abs(a-b)/(absolute+relative*max(abs(a),abs(b)))

def observed_order(coarse_difference,fine_difference):
    if not (math.isfinite(coarse_difference) and math.isfinite(fine_difference)):
        raise ValueError('nonfinite differences')
    if coarse_difference<=0 or fine_difference<=0:return None
    return math.log2(coarse_difference/fine_difference)

def richardson2(coarse,fine):return (4*fine-coarse)/3

def mixed_defect(a00,a01,a10,a11):return a11-a10-a01+a00

def align(a,b):
    na,nb=len(a)-1,len(b)-1
    if na<=0 or nb<na or nb%na:raise ValueError('grids not nested')
    step=nb//na;fine=b[::step]
    if any(x['s']!=y['s'] for x,y in zip(a,fine)):
        raise ValueError('common epoch identity mismatch; no interpolation')
    return a,fine

def electron_delta(on,off,f=Fraction(3,38)):
    diff=lambda k:Fraction(on[k])-Fraction(off[k])
    return diff('x')+f*(diff('y')+2*diff('z'))

def energy_ev(erg_per_h):return erg_per_h/EPS

def diagnostic_pass(*ratios):
    return bool(ratios) and all(math.isfinite(x) and x>=0 for x in ratios) and sum(ratios)<=1
