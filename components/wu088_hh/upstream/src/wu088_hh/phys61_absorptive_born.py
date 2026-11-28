"""PHYS61 C5-C8: original noncentral complex-energy first Born and rigorous remainder.

Scope: fixed Im E=1/100>0 Hartree; NOT real-axis Coulomb outgoing
limiting absorption. Infinite angular operator error rigorously bounded using
PHYS61 R5; finite GL quadrature is independently NONCERTIFYING.
"""
from __future__ import annotations
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import math
import numpy as np
import mpmath as mp
from scipy.special import gammaln, lpmv
from numpy.polynomial.legendre import leggauss
from .phys61_absorptive_dtn import (B,R,TAU_DEFAULT,V_DELTA_UP,uniform_bounds,
                                        source_gate,exponential_positive_partial)

def born_remainder_exact(tau:F=TAU_DEFAULT)->dict:
    p=uniform_bounds(tau)
    cp=F(p['poisson_norm_upper']); q=F(p['screened_neumann_q_upper'])
    delta=V_DELTA_UP
    # U_S-U_C=G_C V (I-G_C V)^-1 P_C; true ALL angular loops remain.
    err=delta*cp*cp*q/(1-q)
    assert err>0
    return {'all_angular_Born_remainder_X_to_Xstar':str(err),
            'rational_proved_lt_6e_minus40':err<F(6,10**40),
            'one_raw_P20_Q21_residual_upper':str(22*err),
            'raw_P20_Q21_lt_1p32e_minus38':22*err<F(132,10**40),
            'source_delta_upper':str(delta),
            'noncertifying_numeric_policy':'finite_r_GL_is_not_a_certified_complex_Born',
            'spectral_scope':'ONLY_Z_49_OVER_200_PLUS_I_OVER_100'}

def born_tail_r39_exact(tau:F=TAU_DEFAULT,terms:int=80)->dict:
    p=uniform_bounds(tau);cp=F(p['poisson_norm_upper']); q=V_DELTA_UP
    # sup_{r>=39}V <=delta exp[-2(39-27)]=delta e^-24
    if type(terms) is not int or terms<50:raise ValueError('must certify exp24 lower')
    exp24_lower=exponential_positive_partial(F(24),terms)
    tail=q*cp*cp/exp24_lower
    return {'operator_X_to_Xstar_born_tail_bound':str(tail),
            'operator_bound_lt_2e_minus29':tail<F(2,10**29),
            'raw_20_21_bound_sqrt462_lt22':str(22*tail),
            'raw_lt_44e_minus29':22*tail<F(44,10**29),
            'domain':'r>=39 (missing from finite numerical GL integral)',
            'rational_exp24_Taylor_order':terms}


def physical_screen_angular_coupling(r:float,m:int,nodes:int=128)->float:
    """Original displaced 2S radial angular matrix element (21,m),(20,m).

    All integration here finite Gaussian quadrature only: NONCERTIFYING.
    """
    if not 27<=r<=60 or type(m) is not int or abs(m)>20 or nodes not in (64,96,128,192,256):
        raise ValueError('invalid radial/angle/orbital grid')
    mu,w=leggauss(nodes)
    ma=abs(m)
    bp=[]
    for ell in (20,21):
        norm=np.sqrt((2*ell+1)/2*np.exp(gammaln(ell-ma+1)-gammaln(ell+ma+1)))
        bp.append(norm*lpmv(ma,ell,mu))
    s=np.sqrt(r*r+float(R)**2-2*r*float(R)*mu)
    original_screen=2*(1+1/s)*np.exp(-2*s)
    return float(np.dot(w,bp[0]*original_screen*bp[1]))


def complex_coulomb_k(dps=40):
    with mp.workdps(dps):
        kk=mp.sqrt(mp.mpf(49)/100+mp.j/mp.mpf(50))
        return kk,-1/kk


@lru_cache(maxsize=8192)
def central_outgoing_complex(l:int,r:float,dps:int=40)->complex:
    """Numerically evaluated genuine upper-half-plane Coulomb H+=G+iF normalized at B.

    Preserving the complex k and eta=-1/k is essential. Floats NONCERTIFYING.
    """
    if type(l) is not int or l<0 or l>80 or not 27<=r<=300 or not 30<=dps<=100:
        raise ValueError('invalid l,r,dps')
    with mp.workdps(dps):
        k,eta=complex_coulomb_k(dps)
        def h(rad):return mp.coulombg(l,eta,k*rad)+mp.j*mp.coulombf(l,eta,k*rad)
        res=h(mp.mpf(str(r)))/h(mp.mpf(27))
        return complex(res)


def born_first_grid(m:int,nrad:int,nang:int,dps:int=40)->complex:
    """NONCERTIFYING original positive-absorptive complex Born over [27,39]."""
    if nrad not in (10,14,20,28) or nang not in (64,96,128,192,256) or abs(m)>2:
        raise ValueError('bounded original P20-Q21 diagnostic grid only')
    xi,wi=leggauss(nrad)
    rr=33+6*xi;rw=6*wi
    val=0j
    for r,w in zip(rr,rw):
        v=physical_screen_angular_coupling(float(r),m,nang)
        p20=central_outgoing_complex(20,float(r),dps)
        p21=central_outgoing_complex(21,float(r),dps)
        val+=float(w)*p20*p21*v
    return val


def flux_identity_finite_interval(l:int,limit:float=31,nodes:int=36,dps:int=38)->dict:
    """NONCERTIFYING check of exact dissipative conservation on [27,limit].

    J(27)-J(limit)=tau integral_27^limit |p_l(r)|² dr, J=Im(p* p').
    """
    if type(l) is not int or l not in (0,20,21) or not 28<=limit<=38 or nodes not in (24,36,48):
        raise ValueError('bad finite flux diagnostic')
    with mp.workdps(dps):
        kk,eta=complex_coulomb_k(dps); hB=mp.coulombg(l,eta,kk*27)+mp.j*mp.coulombf(l,eta,kk*27)
        def h(rad):return mp.coulombg(l,eta,kk*rad)+mp.j*mp.coulombf(l,eta,kk*rad)
        def p(rad):return h(rad)/hB
        def dp(rad):
            # DLMF 33.4.4: H_l'(rho)=S_{l+1}H_l-R_{l+1}H_{l+1};
            # derivative of H_l(eta,k r) with respect to r includes k.
            rho=kk*rad
            hn=h(rad)
            hn1=mp.coulombg(l+1,eta,rho)+mp.j*mp.coulombf(l+1,eta,rho)
            rho_der=((l+1)/rho+eta/(l+1))*hn-mp.sqrt(1+eta**2/(l+1)**2)*hn1
            return kk*rho_der/hB
        jB=mp.im(mp.conj(p(mp.mpf(27)))*dp(mp.mpf(27)))
        C=mp.mpf(str(limit)); jC=mp.im(mp.conj(p(C))*dp(C))
        xs,ws=leggauss(nodes);tot=mp.mpf(0)
        for xx,ww in zip(xs,ws):
            rad=mp.mpf(27)+(C-27)*(mp.mpf(str(xx))+1)/2
            norm=abs(p(rad))**2
            tot+=mp.mpf(str(ww))*(C-27)/2*norm
        absorptive=mp.mpf(1)/50*tot
        residual=(jB-jC)-absorptive
        return {'ell':l,'J_B':str(jB),'J_C':str(jC),
                'tau_integral_abs_u_squared':str(absorptive),'residual_float':float(residual),
                'relative_residual':float(abs(residual)/max(abs(jB-jC),abs(absorptive))),
                'positive_J_B':jB>0}


def science_packet(source:str|Path)->dict:
    digest=source_gate(source)
    remainder=born_remainder_exact()
    tail=born_tail_r39_exact()
    assert remainder['rational_proved_lt_6e_minus40'] and tail['operator_bound_lt_2e_minus29']
    grids=[(10,64),(14,96),(20,128),(28,192)]
    runs=[]
    for nr,na in grids:
        vals=[born_first_grid(m,nr,na,35) for m in (0,1,2)]
        runs.append({'radial_GL_nodes':nr,'angular_GL_nodes':na,
                     'complex_firstBorn_P20_Q21_m0_m1_m2':[[v.real,v.imag] for v in vals]})
    flux=[flux_identity_finite_interval(l) for l in (0,20,21)]
    if any(q['relative_residual']>1e-8 or not q['positive_J_B'] for q in flux):
        raise ArithmeticError('genuine absorptive Coulomb flux residual failure')
    return {'schema':'WU088_HH_PHYS61_C5C8_COMPLEX_BORN_V1',
            'original_frozen_SHA256':digest,'r5_published_science':'absorptive all-angular DtN complex z only',
            'all_angular_exact_remainder':remainder,
            'all_angular_exact_finite_radial_tail':tail,
            'numerical_scoped_born':[{'m':m,'values':runs[-1]['complex_firstBorn_P20_Q21_m0_m1_m2'][m]} for m in (0,1,2)],
            'independent_grid_refinement':runs,
            'finite_interval_dissipative_flux':flux,
            'NOT_CERTIFIED':['real-axis positive scattering LAP','full exact Z_S at Im(z)=0',
                 'finite numerical GL error interval','source driven xi', 'sigma(E)','k_HH(T)'],
            'HH_R10':'OFF'}
