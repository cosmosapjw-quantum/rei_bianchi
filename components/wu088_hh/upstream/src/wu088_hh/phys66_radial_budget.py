"""PHYS66: coefficient-wise analytic radial errors, not total numerical error.

Uses byte-pinned upstream PR114 finite 0..L (L<=64) Coulomb-ratio proof.
No angular truncation, ODE, quadrature, or roundoff bound is supplied here.
Atomic radii r/a0; every physical Born contribution is measured in a0^-1.
"""
from __future__ import annotations
from fractions import Fraction as F
from functools import lru_cache
from math import comb
from pathlib import Path
import hashlib

from .phys65_exterior_bounds import (B, DELTA, SOURCE_SHA, ratio_certificate,
                                     exp_negative_upper, source_guard)
UPSTREAM_COMMIT='bad80f7729015c84c8dde27f1b1dec3a1f8b2c9f'
UPSTREAM_BLOB='935d8ec1b765e5f1bd7c6ad0d95c9c74acf33512'

def _integer(x,low,high,name):
    if type(x) is not int or not low<=x<=high:
        raise ValueError(f'{name}: integer {low}..{high} required')
    return x

def exact(x):
    if isinstance(x,bool) or isinstance(x,float):
        raise ValueError('certificate input must be exact int, Fraction or decimal string')
    return F(x)

def error_weights(orders:int)->list[F]:
    """[x^(n-1)] 1/(2 sqrt(1-x)-1); positive rational recurrence."""
    _integer(orders,1,5,'orders')
    out=[F(1)]
    for n in range(1,orders):
        out.append(sum((F(comb(2*j,j), (j+1)*4**j)*out[n-1-j]
                        for j in range(n)),F(0)))
    return out

@lru_cache(maxsize=65)
def _constants(max_ell:int):
    _integer(max_ell,0,64,'max_ell')
    c=max(ratio_certificate(l)['trace_bound'] for l in range(max_ell+1))
    gamma=F(c*c);a=gamma*DELTA/2;b=gamma/4;chi=4*a*b
    if not 0<chi<F(1,2):raise ArithmeticError('source contraction not established')
    return c,gamma,a,b,chi

def coefficient_bounds(max_ell:int,outer,orders:int=3)->dict:
    """Bounds on exact mathematical D_n minus exact screen-cut D_(n,T).

    Alpha_n = Cat(n-1) a chi^(n-1)/4^(n-1) in weighted sup norm.
    Beta_n(T)=a h_(n-1) chi^(n-1) exp[-2(T-B)] in unweighted sup.
    Every right hand side returned is rational and upward enclosing.
    """
    T=exact(outer)
    if not B<=T<=100:raise ValueError('outer radius 27..100 required')
    h=error_weights(orders);c,gamma,a,b,chi=_constants(max_ell)
    decay=exp_negative_upper(2*(T-B))
    rows=[]
    for n in range(1,orders+1):
        alpha=F(comb(2*n-2,n-1),n*4**(n-1))*a*chi**(n-1)
        beta=a*h[n-1]*chi**(n-1)*decay
        rows.append(dict(order=n,weighted_coefficient_bound=alpha,
                         radial_cutoff_bound=beta,error_weight=h[n-1]))
    return dict(schema='PHYS66_RADIAL_COEFFICIENT_BOUND_V1',max_ell=max_ell,
                outer=T,orders=orders,gamma=gamma,a=a,b=b,chi=chi,
                continuum_born_remainder=a*chi**orders/(1-chi),
                continuum_response_radial_bound=a*(1-chi)/(1-2*chi)*decay,
                terms=rows,source_sha256=SOURCE_SHA,
                upstream_commit=UPSTREAM_COMMIT,upstream_blob=UPSTREAM_BLOB,
                scope='EXACT_CONTINUUM_FINITE_L_RADIAL_COMPONENT_ONLY',
                numerical_error_bound=None,excluded_angular_error_bound=None,
                total_numerical_error_certified=False,HH_R10='OFF')

def certificate(source: str|Path,max_ell:int=64,outer='65',orders:int=3)->dict:
    source_guard(source)
    # Exact byte identity of the reused proof implementation is an executable prerequisite.
    p=Path(__file__).with_name('phys65_exterior_bounds.py');b=p.read_bytes()
    identity=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    if identity!=UPSTREAM_BLOB:raise ValueError('upstream PR114 code bytes changed')
    return coefficient_bounds(max_ell,outer,orders)

def plan_radius(max_ell:int,targets:dict,start:int=35,stop:int=80)->dict:
    """Choose an integer radius meeting analytic radial component targets ONLY."""
    _integer(start,27,100,'start');_integer(stop,start,100,'stop')
    if not targets:raise ValueError('at least one exact absolute target required')
    clean={_integer(k,1,5,'target order'):exact(v) for k,v in targets.items()}
    if any(v<=0 for v in clean.values()):raise ValueError('strictly positive targets')
    order=max(clean)
    for T in range(start,stop+1):
        cert=coefficient_bounds(max_ell,T,order)
        if all(cert['terms'][n-1]['radial_cutoff_bound']<=v for n,v in clean.items()):
            return dict(status='ANALYTIC_RADIAL_TARGETS_MET',max_ell=max_ell,
                        outer=T,targets=clean,certificate=cert,
                        total_numerical_error_certified=False)
    return dict(status='NO_RADIUS_WITHIN_SEARCH',max_ell=max_ell,outer=None,
                targets=clean,search=[start,stop],total_numerical_error_certified=False)

def to_jsonable(obj):
    """Lossless bounded base16 integer encoding; no process-wide digit-limit change."""
    if isinstance(obj,F):
        return {'type':'rational-hex-v1','numerator_hex':format(obj.numerator,'x'),
                'denominator_hex':format(obj.denominator,'x')}
    if isinstance(obj,dict):return {str(k):to_jsonable(v) for k,v in obj.items()}
    if isinstance(obj,(list,tuple)):return [to_jsonable(v) for v in obj]
    return obj

def from_rational(obj):
    if not isinstance(obj,dict) or obj.get('type')!='rational-hex-v1':
        raise ValueError('expected lossless rational-hex-v1')
    return F(int(obj['numerator_hex'],16),int(obj['denominator_hex'],16))

def numeric_summary(cert):
    return dict(max_ell=cert['max_ell'],outer=float(cert['outer']),
                gamma=float(cert['gamma']),chi=float(cert['chi']),
                radial_by_order=[float(x['radial_cutoff_bound']) for x in cert['terms']],
                born_remainder=float(cert['continuum_born_remainder']),
                total_numerical_error_certified=False)
