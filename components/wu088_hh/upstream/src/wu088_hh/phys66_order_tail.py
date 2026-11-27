"""Order-specific continuum radial-cutoff bounds, not numerical error bars.

Inherit PR114's proved |H_l(t)/H_l(r)|²<=32400 for 0<=l<=64,
27<=r<=t<infinity. Original physical V=2(1+1/d)exp(-2d).
All quantities below use atomic radial coordinates and norm in a0^-1.
No angular cutoff, special-function, ODE, quadrature or roundoff error is
certified by these bounds. Fractions use a lossless hex JSON codec.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import comb, ceil
from pathlib import Path
from functools import lru_cache
import hashlib

B=F(27)
DELTA=F(3,10**23)
GAMMA=F(32400)
A=GAMMA*DELTA/2
BILINEAR=GAMMA/4
CHI=4*A*BILINEAR
SOURCE_SHA='f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d'
PARENT='bad80f7729015c84c8dde27f1b1dec3a1f8b2c9f'


def source_guard(source: str|Path)->str:
    digest=hashlib.sha256(Path(source).read_bytes()).hexdigest()
    if digest!=SOURCE_SHA:
        raise ValueError('immutable original source SHA256 mismatch')
    return digest


def catalan(n: int)->int:
    if type(n) is not int or not 0<=n<=20:
        raise ValueError('Catalan index must be integer 0..20')
    return comb(2*n,n)//(n+1)


def sensitivity_numbers(orders: int)->tuple[int,...]:
    """h0=1, hn=4 sum_(j=1..n) Cat_(j-1) h_(n-j)."""
    if type(orders) is not int or not 1<=orders<=10:
        raise ValueError('orders must be integer 1..10')
    h=[1]
    for n in range(1,orders):
        h.append(4*sum(catalan(j-1)*h[n-j] for j in range(1,n+1)))
    return tuple(h)


@lru_cache(maxsize=256)
def exponential_decay_upper(x: F)->F:
    """Rigorous e^-x upper: reciprocal of a positive Taylor lower sum."""
    x=F(x)
    if not 0<=x<=146:
        raise ValueError('certified radial exponent must be in [0,146]')
    terms=max(160,ceil(2*x)+20)
    t=s=F(1)
    for n in range(1,terms+1):
        t*=x/n
        s+=t
    return 1/s


def cutoff_bounds(source: str|Path, max_ell: int=64,
                  outer: int|str|F=65, orders: int=3)->dict:
    digest=source_guard(source)
    if type(max_ell) is not int or not 0<=max_ell<=64:
        raise ValueError('proved finite-cutoff scope is L=0..64')
    if isinstance(outer,(float,bool)):
        raise ValueError('exact cutoff required: int, decimal string or Fraction')
    outer=F(outer)
    if not B<=outer<=100:
        raise ValueError('outer radius must lie in [27,100]')
    h=sensitivity_numbers(orders)
    theta=exponential_decay_upper(2*(outer-B))
    e=[A**n*BILINEAR**(n-1)*h[n-1]*theta for n in range(1,orders+1)]
    # Compare exact original finite-L full exterior with exact finite-T
    # Born terms; this subtotal does NOT include numerical coefficients.
    born=A*CHI**orders/(1-CHI)
    return {
        'schema':'PHYS66_ORDER_CUTOFF_V1','parent_ratio_proof_commit':PARENT,
        'source_sha256':digest,'max_ell':max_ell,'outer':outer,'orders':orders,
        'gamma':GAMMA,'forcing_a':A,'bilinear_b':BILINEAR,'chi':CHI,
        'sensitivity_numbers':h,'order_cutoff_bounds':e,
        'higher_born_bound':born,
        'exact_series_analytic_subtotal':sum(e)+born,
        'radial_cutoff_scope':'exact physical Born terms D_n versus exact D_n,T; all signed m inside finite L',
        'unused_angular_modes_bound':None,'numerical_error_bound':None,
        'total_error_bound':None,'total_error_certified':False,'HH_R10':'OFF'
    }


def minimum_cutoff(source: str|Path, order: int, budget: F,
                   max_ell: int=64, stop: int=100)->int:
    """Smallest integer radius passing an absolute analytic component budget.

    A user-chosen budget is not an observed error or interval certificate.
    """
    budget=F(budget)
    if budget<=0 or type(stop) is not int or not 27<=stop<=100:
        raise ValueError('positive absolute budget and integer stop in [27,100]')
    for t in range(27,stop+1):
        if cutoff_bounds(source,max_ell,t,order)['order_cutoff_bounds'][order-1]<budget:
            return t
    raise ArithmeticError('component budget unmet within certified radial domain')


def json_safe(value):
    if isinstance(value,F):
        return {'codec':'rational-hex-v1','numerator_hex':hex(value.numerator),
                'denominator_hex':hex(value.denominator)}
    if isinstance(value,dict): return {k:json_safe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [json_safe(v) for v in value]
    return value


def decode_fraction(data: dict)->F:
    if not isinstance(data,dict) or data.get('codec')!='rational-hex-v1':
        raise ValueError('expected exact rational-hex-v1')
    return F(int(data['numerator_hex'],16),int(data['denominator_hex'],16))
