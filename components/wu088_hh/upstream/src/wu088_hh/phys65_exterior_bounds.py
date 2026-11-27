"""Exact finite-L, full-radial Coulomb-ratio and screened Riccati bounds.

Atomic-coordinate SSOT: k=7/10, B=27, V=2(1+1/d)exp(-2d),
 d=|x-(7/10)zhat|. No floating special function is used in certificates.
Bounds control continuum radial cutoff/Born tails, NOT angular truncation,
ODE/quadrature/roundoff errors or the full source-driven scattering rate.
"""
from __future__ import annotations
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
from math import ceil
import hashlib

B, K, DELTA = F(27), F(7, 10), F(3, 10**23)
SOURCE_SHA = 'f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d'

def source_guard(source: str | Path) -> str:
    digest = hashlib.sha256(Path(source).read_bytes()).hexdigest()
    if digest != SOURCE_SHA:
        raise ValueError('immutable original source SHA256 mismatch')
    return digest

def exp_upper(x: F, terms: int = 60) -> F:
    """Upward rational exp(x); positive Taylor + geometric remainder."""
    x = F(x)
    if x < 0 or type(terms) is not int or terms < 1 or x >= terms + 2:
        raise ValueError('positive Taylor requires 0<=x<terms+2')
    term = total = F(1)
    for j in range(1, terms + 1):
        term *= x / j
        total += term
    return total + term * x / (terms + 1) / (1 - x / (terms + 2))

def exp_negative_upper(x: F) -> F:
    """exp(-x) <= reciprocal finite positive Taylor sum, all rational."""
    x = F(x)
    if x < 0:
        raise ValueError('exponent must be nonnegative')
    n = max(160, ceil(2*x) + 20)
    term = total = F(1)
    for j in range(1, n + 1):
        term *= x / j
        total += term
    return 1 / total

def q_radial(ell: int, r: F) -> F:
    return K*K + 2/r - F(ell*(ell+1))/(r*r)

@lru_cache(maxsize=65)
def _ratio_certificate(ell: int) -> dict:
    """Prove |H_l(t)/H_l(r)|^2 <= trace_bound^2 for t>=r>=27.

    q>0: E'=q'|h|², (E/q)'=-q'|h'|²/q² and E(infty)=2k².
    Forbidden part: positive backward scalar transfer + Gram determinant1.
    Full derivation is in research/hh_phys65_20261018/r5/PROOF.md.
    """
    if type(ell) is not int or not 0 <= ell <= 64:
        raise ValueError('certificate scope is integer ell=0..64')
    lam = F(ell*(ell+1))
    def allowed(r):
        qmin = min(q_radial(ell, r), K*K)
        qmax = q_radial(ell, max(r, lam)) if lam else q_radial(ell, r)
        if qmin <= 0:
            raise ArithmeticError('allowed patch needs positive energy floor')
        return 2*qmax/qmin, qmin, qmax
    if q_radial(ell, B) > 0:
        raw, qmin, qmax = allowed(B)
        return {'ell':ell,'anchor':B,'allowed_start':B,'qmin':qmin,
                'qmax':qmax,'lognorm_upper':F(0),'exponent':F(0),
                'trace_raw_upper':raw,'trace_bound':ceil(raw),'forbidden':False}
    # Exact bisection: largest 1/16-grid point whose q<=0.
    left, right = int(16*B), 16*(ell+2)*2
    while q_radial(ell, F(right,16)) <= 0:
        right *= 2
    while right-left > 1:
        mid = (left+right)//2
        if q_radial(ell,F(mid,16)) <= 0:
            left = mid
        else:
            right = mid
    anchor = F(left,16)
    assert q_radial(ell,anchor) <= 0 < q_radial(ell,anchor+F(1,16))
    candidates = []
    for j in range(2,13):
        end = anchor + F(j,4)
        raw, qmin, qmax = allowed(end)
        def mu(r): return abs(lam/r**2-2/r)/(2*K)
        pts = [anchor,end]
        if anchor <= lam <= end:
            pts.append(lam)
        bound_mu = max(map(mu,pts))
        exponent = 2*bound_mu*(end-anchor)
        raw *= exp_upper(exponent)
        candidates.append({'ell':ell,'anchor':anchor,'allowed_start':end,
                           'qmin':qmin,'qmax':qmax,'lognorm_upper':bound_mu,
                           'exponent':exponent,'trace_raw_upper':raw,
                           'trace_bound':ceil(raw),'forbidden':True})
    return min(candidates,key=lambda r:(r['trace_bound'],r['trace_raw_upper']))

def ratio_certificate(ell: int) -> dict:
    """Return an independent copy; cached exact evidence cannot be mutated."""
    return dict(_ratio_certificate(ell))

def _components(max_ell: int, orders: int, outer: F) -> tuple:
    if type(max_ell) is not int or not 0 <= max_ell <= 64:
        raise ValueError('max_ell must be integer 0..64')
    if type(orders) is not int or not 1 <= orders <= 5:
        raise ValueError('orders must be integer 1..5')
    outer = F(outer)
    if not B <= outer <= 100:
        raise ValueError('outer radius must be 27..100')
    rows = [ratio_certificate(l) for l in range(max_ell+1)]
    c = max(row['trace_bound'] for row in rows)
    gamma = c*c
    a, b = gamma*DELTA/2, F(gamma,4)
    q = 4*a*b
    if not 0 < q < F(1,2):
        raise ArithmeticError('continuum contraction not established')
    tail = a*q**orders/(1-q)
    radial = a*(1-q)/(1-2*q)*exp_negative_upper(2*(outer-B))
    return rows, c, gamma, a, b, q, tail, radial

def certificate(source: str | Path, max_ell: int=64,
                orders: int=3, outer: F=F(39)) -> dict:
    digest = source_guard(source)
    rows,c,gamma,a,b,q,tail,radial = _components(max_ell,orders,outer)
    # Source V <=delta e^-2(r-B); verify its exact endpoint majorant.
    source_upper = 2*(1+F(10,263))*exp_negative_upper(F(263,5))
    assert source_upper < DELTA
    return {'schema':'PHYS65_EXTERIOR_BOUNDS_V1',
            'status':'DERIVED_FINITE_L_FULL_RADIAL_ANALYTIC_BOUNDS',
            'source_sha256':digest,'max_ell':max_ell,'orders':orders,
            'outer':str(F(outer)),'kappa':'7/10','E_Hartree':'49/200',
            'trace_bound_max':c,'gamma':gamma,
            'source_multiplier_upper':str(source_upper),
            'delta_upper':str(DELTA),'forcing_a':str(a),'bilinear_b':str(b),
            'catalan_q':str(q),'born_tail_after_N':str(tail),
            'radial_screen_cutoff_bound':str(radial),
            'analytic_sum_bound':str(tail+radial),
            'numeric_display':{'q':float(q),'born_tail':float(tail),
                               'radial_cutoff':float(radial)},
            'm_scope':'every signed m in the finite full 0..L projection',
            'radial_scope':'original screen for all r>=27; cutoff comparison at outer',
            'excluded_angular_error':None,'numerical_discretization_error':None,
            'numerical_discretization_certified':False,'total_error_certified':False,
            'HH_R10':'OFF',
            'mode_certificates':[{k:(str(v) if isinstance(v,F) else v)
                                 for k,v in row.items()} for row in rows]}
