"""PHYS53: central Coulomb outgoing high-ell reference, not screened DtN.

DLMF 33.8.2 supplies a convergent continued fraction for H_l(+)'/H_l(+).
Finite-depth computation is numerical (not interval certified). At large ell
its imaginary part loses f64 relative precision; compute the outgoing current
separately as log10(k/|G+iF|**2) using multiprecision Coulomb functions.
Original H-H source remains h=-Delta/2-1/r-(1+1/s)exp(-2s), k=R=7/10.
"""
from __future__ import annotations
import hashlib
import math
from pathlib import Path
import mpmath as mp

KAPPA = 0.7
ETA = -10/7
FROZEN_SHA = 'f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d'
SCHEMA='WU088_HH_PHYS53_COULOMB_CF_V1'

def verify_original_source(path: str | Path) -> str:
    actual=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if actual != FROZEN_SHA:
        raise ValueError('immutable 1386-coefficient source SHA mismatch')
    return actual

def outgoing_cf(ell: int, radius: float, depth: int = 1024) -> complex:
    """DLMF 33.8.2 outgoing logarithmic derivative, units a0^-1.
    Backward truncation has no guaranteed finite-depth error bound.
    """
    if type(ell) is not int or ell < 0 or ell > 4096:
        raise ValueError('ell must be an integer from 0 to 4096')
    if not isinstance(radius,(int,float)) or not math.isfinite(radius) or not 20 <= radius <= 100:
        raise ValueError('finite exterior radius must be 20..100 a0')
    if type(depth) is not int or not 128 <= depth <= 8192:
        raise ValueError('depth 128..8192')
    rho=KAPPA*radius
    a=ell+1+1j*ETA
    b=-ell+1j*ETA
    tail=0j
    for n in range(depth,0,-1):
        tail=(a+n-1)*(b+n-1)/(2*(rho-ETA+1j*n)+tail)
    return KAPPA*(1j*(1-ETA/rho)+1j*tail/rho)

def depth_comparison(ell:int,radius:float, depths=(768,1152))->dict:
    if len(depths)!=2 or depths[0]>=depths[1]:
        raise ValueError('strict increasing depth pair required')
    a=outgoing_cf(ell,radius,depths[0]); b=outgoing_cf(ell,radius,depths[1])
    if not math.isfinite(b.real):
        raise ArithmeticError('complex outgoing ratio unresolved')
    return {'ell':ell,'radius_Bohr':float(radius),'re_per_Bohr':b.real,
            'im_f64_per_Bohr':b.imag,'depth_pair':list(depths),
            'complex_depth_delta':abs(a-b),
            'current_warning':'f64 imaginary part can round to zero or wrong sign; not an accepted high-ell current oracle'}

def mp_reference(ell:int,radius:float,dps:int=72)->dict:
    if type(ell) is not int or not 0<=ell<=4096 or type(dps) is not int or not 50<=dps<=200:
        raise ValueError('invalid ell or precision')
    if not isinstance(radius,(int,float)) or radius<=0 or not math.isfinite(radius):
        raise ValueError('finite positive radius')
    with mp.workdps(dps):
        k=mp.mpf(7)/10
        eta=-1/k
        rho=k*mp.mpf(str(radius))
        def h(n):return mp.coulombg(n,eta,rho)+mp.j*mp.coulombf(n,eta,rho)
        H=h(ell)
        Hp=((ell+1)/rho+eta/(ell+1))*H - mp.sqrt(1+(eta/(ell+1))**2)*h(ell+1)
        z=k*Hp/H
        j=k/abs(H)**2
        logj=mp.log10(j)
        if not mp.isfinite(z.real) or not mp.isfinite(logj) or j<=0:
            raise ArithmeticError('failed high-precision Coulomb reference')
        return {'ell':ell,'radius_Bohr':float(radius),
                're_per_Bohr':mp.nstr(mp.re(z),min(45,dps-12)),
                'im_per_Bohr':mp.nstr(mp.im(z),min(45,dps-12)),
                'log10_current_per_Bohr':mp.nstr(logj,min(45,dps-12)),
                'log10_abs_H':mp.nstr(mp.log10(abs(H)),min(45,dps-12)),
                'dps':dps,'physics_scope':'CENTRAL_COULOMB_ONLY'}

def asymptotic_log10_current(ell:int,radius:float)->float:
    """DLMF 33.5(iv), fixed rho,eta, ell→∞: asymptotic, not bound.
    G_l ~ exp(pi*eta/2)*(2l-1)!! / rho**l; j=k/(F²+G²).
    """
    if type(ell) is not int or ell<1 or ell>4096 or not 20<=radius<=100:
        raise ValueError('finite asymptotic input range')
    rho=KAPPA*radius
    log_df=math.lgamma(2*ell+1)-ell*math.log(2)-math.lgamma(ell+1)
    return (math.log(KAPPA)-math.pi*ETA+2*ell*math.log(rho)-2*log_df)/math.log(10)