"""PHYS59 C5-C8: source-scoped FULL original m=0 off-shell DtN Born witness.

Actual physical off-centre S(r,cosθ) with no spherical replacement.
At E=-49/200 Hartree, the negative-energy Coulomb decaying radial
Poisson profile is WhittakerW_{1/kappa,ell+1/2}(2kappa*r) normalized at
r=B=27. This is NOT the positive-energy outgoing Coulomb H^(+).

Uses high precision Whittaker for radial p_l, independent floating
Gauss-Legendre to construct original screened noncentral V21,20(r),
then radial GL quadrature of the first-Born boundary DtN element.
These numerical quadratures are NONCERTIFYING. Independent exact
Fraction energy and operator Born remainder are rigorous:
  ||(Z_S^- - Z_C^-) - P_C^* V P_C||_(X->X*) < 7e-45,
  |D21,20 - Born21,20| < 154e-45 for raw unweighted e_l boundary.
No positive-energy scattering or k_HH production gate is admitted.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from math import isfinite
import mpmath as mp

from .phys59_negative_exterior import (
    KAPPA, B, R, DELTA_UP, BETA_CERT, TRACE_ENERGY_UP,
    original_sha_guard, m0_l20_l21_dtn_lower
)

SCHEMA="WU088_HH_PHYS59_C5_C8_OFFSHELL_BORN_INTERVAL_WITNESS_V1"


def born_remainder_fraction_certification()->dict:
    """Exact operator remainder, all-angular, whole physical noncentral V."""
    q = DELTA_UP / BETA_CERT
    assert q<F(1,10**20)
    # ||P_C||² <=C/beta=3, ||G_C V|| <=delta/beta.
    op_rem = (TRACE_ENERGY_UP / BETA_CERT)*DELTA_UP*q/(1-q)
    assert op_rem < F(7,10**45)
    # e20 norm_X=sqrt(21), e21 norm_X=sqrt(22), sqrt(462)<22.
    raw = 22*op_rem
    assert raw < F(154,10**45)
    return {"zero_boundary_neumann_q_exact_upper":str(q),
            "allangular_Born_operator_remainder_exact_upper":str(op_rem),
            "allangular_Born_operator_remainder_simple":"<7/10^45",
            "raw_offdiagonal_ell21_ell20_m0_remainder_exact_upper":str(raw),
            "raw_offdiagonal_remainder_simple":"<154/10^45",
            "strictly_offshell_energy_Hartree":"-49/200",
            "P_Q_retained":True}


def central_decaying_poisson(ell:int,r,*,dps:int=70):
    if type(ell) is not int or not 0<=ell<=250 or not 50<=dps<=180:
        raise ValueError("valid nonnegative angular index and dps")
    with mp.workdps(dps):
        rad=mp.mpf(str(r))
        if rad < mp.mpf(27):raise ValueError("r>=27 Bohr")
        kap=mp.mpf(7)/10
        par=1/kap
        def wh(s):return mp.whitw(par,ell+mp.mpf(1)/2,2*kap*s)
        val=wh(rad)/wh(mp.mpf(27))
        if not (mp.isfinite(val) and val>0):raise ArithmeticError("nonpositive Coulomb offshell Poisson profile")
        return +val


def physical_2S_angular_matrix_element(ell:int,ellp:int,m:int,r:float,nodes:int=192)->float:
    import numpy as np
    from scipy.special import gammaln,lpmv
    if any(type(x) is not int for x in (ell,ellp,m,nodes)) or nodes<64 or nodes>512 or min(ell,ellp)<abs(m) or not isfinite(r) or not 27<=r<=70:
        raise ValueError("original noncentral angular matrix input invalid")
    mu,w=np.polynomial.legendre.leggauss(nodes)
    ma=abs(m)
    def b(l):
        return np.sqrt((2*l+1)/2*np.exp(gammaln(l-ma+1)-gammaln(l+ma+1)))*lpmv(ma,l,mu)
    rr=float(R)
    s=np.sqrt(r*r+rr*rr-2*r*rr*mu)
    pot=2*(1+1/s)*np.exp(-2*s)
    return float(np.dot(w*pot,b(ell)*b(ellp)))


def first_born_21_20_gl(n_rad:int=24,n_ang:int=192,length_Bohr:float=12.0,dps:int=75)->dict:
    """NONCERTIFYING finite radial+angular GL quadrature; rigorous tail bound separate."""
    import numpy as np
    if type(n_rad) is not int or not 8<=n_rad<=128 or type(n_ang) is not int or not 64<=n_ang<=512 or not 6<=length_Bohr<=30 or not 50<=dps<=180:
        raise ValueError("bounded radial/angle/precision setup")
    nodes,w=np.polynomial.legendre.leggauss(n_rad)
    r=27+.5*length_Bohr*(nodes+1)
    total=mp.mpf(0)
    with mp.workdps(dps):
        for rad,ww in zip(r,w):
            p20=central_decaying_poisson(20,float(rad),dps=dps)
            p21=central_decaying_poisson(21,float(rad),dps=dps)
            v=physical_2S_angular_matrix_element(21,20,0,float(rad),n_ang)
            total+=mp.mpf(str(ww))*mp.mpf(str(v))*p20*p21
        total*=mp.mpf(str(length_Bohr))/2
        # Rigorous |tail| ≤delta exp[-(2+2sqrt(beta_C))*L]/(2+2sqrt(beta_C))
        beta=mp.mpf(1123)/2700
        lam=2+2*mp.sqrt(beta)
        tail_bound=mp.mpf(3)/10**23*mp.exp(-lam*mp.mpf(str(length_Bohr)))/lam
        return {"n_rad":n_rad,"n_ang":n_ang,"radial_upper_Bohr":27+length_Bohr,
                "born_GL_noncertifying":mp.nstr(total,40),
                "rigorous_radial_tail_bound_decimal":mp.nstr(tail_bound,18),
                "rigorous_radial_tail_bound_analytic":"(3/10^23)*exp[-(2+2sqrt(1123/2700))*L]/(2+2sqrt(1123/2700))",
                "BORN_IS_NOT_FULL_SCREENED_DTN":True,
                "physics":"E_NEGATIVE_OFFSHELL_NOT_SCATTERING"}


def numerical_witness(source:str|Path)->dict:
    src=original_sha_guard(source)
    rem=born_remainder_fraction_certification()
    # Small independent grid refinement. Local run is light, no NCP required.
    rows=[first_born_21_20_gl(n,ang,12,75) for n,ang in ((10,96),(18,128),(26,192),(34,256))]
    with mp.workdps(65):
        a=mp.mpf(rows[-1]["born_GL_noncertifying"])
        b=mp.mpf(rows[-2]["born_GL_noncertifying"])
        if a<=0 or abs(a-b)/a>mp.mpf('0.0002'):
            raise ArithmeticError("noncertifying Born refinement unstable")
        ratio=abs(a-b)/a
    return {"schema":SCHEMA,"original_SHA256":src,
            "source":"original off-centre full V=2S and full m0 P20/Q21",
            "rigorous_Born_remainder":rem,
            "rigorous_positive_DtN_lower":m0_l20_l21_dtn_lower()["strict_full_original_screened_Zminus_PQ_lower_exact"],
            "GL_radial_angular_noncertifying_rows":rows,
            "finest_refinement_relative":mp.nstr(ratio,15),
            "not_admitted":["positive real scattering energy outgoing Z_S^+","physical sigma(E)","Maxwellian k_HH(T)"],
            "HH_R10":"OFF"}
