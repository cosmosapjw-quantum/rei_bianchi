"""PHYS60 C5-C8 *real-positive-energy* outgoing finite angular first Born.

Physical original V_lj=2<Y_lm|S(r,mu)|Y_jm>, s=|r-0.7zhat|.
First Born bilinear: integral_B^infty P_l^+(r) V_lj(r) P_j^+(r) dr.
NO complex conjugation on P^+ in reciprocity; no rigorous quadrature
remainder or all-infinite angular outgoing DtN is claimed. Also no sigma(E).
"""
from __future__ import annotations
from pathlib import Path
from functools import lru_cache
import json
import mpmath as mp
import numpy as np
from .phys60_finite_jost import source_sha_guard, angular_real_block, hplus, FROZEN_SHA

SCHEMA='WU088_HH_PHYS60_C5C8_POSITIVE_E_COMPLEX_BORN_V1'
B=27.

def radii_rule(n:int,end:float=39.):
    if type(n)!=int or not 8<=n<=100 or not isinstance(end,(int,float)) or not np.isfinite(end) or not 27<end<=55:
        raise ValueError('finite radial GL nodes and end in (27,55]')
    x,w=np.polynomial.legendre.leggauss(n)
    return B+(end-B)/2*(x+1),(end-B)/2*w

def first_born_raw(ell_out:int=21,ell_in:int=20,m:int=0,
                   radial_nodes:int=26,angular_nodes:int=192,end:float=39.,dps:int=55,
                   incoming:bool=False)->dict:
    """Independent radial GL physical screened Born, complex-symmetric channel.

    For the (21,20) test the first Born is the derivative at λ=0 of the
    finite L>=21 Galerkin outgoing DtN for H_C+λ V. Not all L finite
    first Born integrals are fully matched to a true driven regular origin.
    """
    if type(ell_out)!=int or type(ell_in)!=int or min(ell_out,ell_in)<0 or max(ell_out,ell_in)>80 or type(m)!=int or abs(m)>min(ell_out,ell_in):
        raise ValueError('valid signed-m partial waves')
    if type(angular_nodes)!=int or not 64<=angular_nodes<=512:raise ValueError('angular quadrature 64..512')
    if type(dps)!=int or not 35<=dps<=120:raise ValueError('dps 35..120')
    rr,wr=radii_rule(radial_nodes,end)
    ells=(ell_out,ell_in) if ell_out!=ell_in else (ell_out,)
    with mp.workdps(dps):
        hb_out=hplus(ell_out,B,dps);hb_in=hplus(ell_in,B,dps)
        acc=mp.mpc(0)
        for r,w in zip(rr,wr):
            actual_V=angular_real_block(float(r),ells,m,angular_nodes)
            vij=actual_V[0,1] if len(ells)==2 else actual_V[0,0]
            hout=hplus(ell_out,float(r),dps)/hb_out
            hin=hplus(ell_in,float(r),dps)/hb_in
            if incoming:
                hout=mp.conj(hout);hin=mp.conj(hin)
            acc+=mp.mpf(str(w))*mp.mpf(str(vij))*hout*hin
        return {"ell_out":ell_out,"ell_in":ell_in,"signed_m":m,
          "angular_nodes":angular_nodes,"radial_nodes":radial_nodes,
          "radius_Bohr_interval":[B,float(end)],"dps":dps,"incoming":incoming,
          "real_Born":mp.nstr(mp.re(acc),27),"imag_Born":mp.nstr(mp.im(acc),27),
          "complex_abs_Born":mp.nstr(abs(acc),27),
          "status":"NONCERTIFYING_FINITE_RADIUS_COMPLEX_BORN_FIRST_ORDER_ONLY"}

def simple_born_reciprocity_test()->dict:
    a=first_born_raw(21,20,0,18,128,39,50)
    b=first_born_raw(20,21,0,18,128,39,50)
    x=complex(float(a['real_Born']),float(a['imag_Born']))
    y=complex(float(b['real_Born']),float(b['imag_Born']))
    return {"forward":a,"transposed":b,"relative_difference":abs(x-y)/abs(x),
            "transpose_not_adjoint":True,"numeric_only":True}


def outgoing_dtn_cf(l:int,r:float=27.,depth:int=768)->complex:
    """Independent DLMF §33.8.2 finite-depth outgoing H+'/H+ diagnostic.

    The infinite CF converges for rho>0; finite depth agreement is a
    numerical cross-check ONLY, not a certified truncation error bound.
    """
    if type(l)!=int or not 0<=l<=150 or not isinstance(r,(float,int)) or not np.isfinite(r) or r<27 or type(depth)!=int or not 128<=depth<=4096:
        raise ValueError('finite L/r/depth positive reference')
    k=.7;eta=-10/7;rho=k*r
    a=l+1+1j*eta;b=-l+1j*eta
    tail=0j
    for n in range(depth,0,-1):
        tail=((a+n-1)*(b+n-1))/(2*(rho-eta+1j*n)+tail)
    return k*(1j*(1-eta/rho)+1j*tail/rho)


def exact_exterior_screen_tail_L1(T:int=39,terms:int=160):
    """Rigorous rational upper on integral_T^inf ||V(r)||dr.

    This is MULTIPLIER radial-L1, NOT a first Born radial tail bound
    because the two outgoing Coulomb Poisson factors must be bounded.
    """
    from fractions import Fraction as F
    from .phys60_finite_jost import B,screen_delta_upper,exp_lower_positive
    if type(T)!=int or not 27<=T<=55:raise ValueError('integer truncation radius 27..55')
    return screen_delta_upper()/(2*exp_lower_positive(F(2*(T-27)),terms))

def make_witness(source:Path)->dict:
    sha=source_sha_guard(source)
    grid=[]
    for m in (0,1,2):
        for nr,na in ((10,96),(18,128),(26,192),(34,256)):
            grid.append(first_born_raw(21,20,m,nr,na,end=39,dps=55))
    guard=first_born_raw(21,20,0,26,192,end=45,dps=55)
    # 39 vs 45 uses independent integration; numerical tail checks only.
    return {'schema':SCHEMA,'source_sha256':sha,'energy_hartree':'49/200',
       'physical_screen':'original full displaced 2(1+s^-1) exp(-2s), no radial average',
       'positive_energy_reference':'Coulomb H+=G+iF; P_l=H_l^+(k*r)/H_l^+(k*27)',
       'original_P20_Q21_m_grid':grid,'r45_comparison_m0':guard,
       'reciprocity':'positive-energy outgoing Born uses complex-bilinear H+*H+, NOT hermitian Hminus*Hplus',
       'rigorous_full_finite_L_Jost_from_R5':True,
       'first_Born_linear_response_finite_L':True,
       'numerical_Born_remainder':'NOT_CERTIFIED',
       'radial_tail_r_gt_end':'NOT_CERTIFIED_FOR_THIS_COMPLEX_BORN',
       'certified_screen_multiplier_radial_L1_tail_T39_fraction':str(exact_exterior_screen_tail_L1(39)),
       'independent_coulomb_cf_diagnostics':{str(l):{'finite_depth_768':str(outgoing_dtn_cf(l,27.,768)),'finite_depth_1152':str(outgoing_dtn_cf(l,27.,1152))} for l in (20,21,28)},
       'L_to_infinity_uniform':'NOT_PROVED',
       'full_Z_Splus':'NOT_PROVED',
       'HH_R10':'OFF'}
