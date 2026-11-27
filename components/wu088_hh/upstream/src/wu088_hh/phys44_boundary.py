"""PHYS44: source-locked finite-radius Coulomb reference boundary and origin diagnostics.

Original WU088_HH source field is y in eta = F*y, F=exp(exp(-s)).
The exact central Coulomb outgoing DtN is a REFERENCE, not the exact
two-centre SCREENED exterior DtN nor an admitted HH cross section.
The screened V tail is bounded independently; missing exterior
resolvent and incoming adjoint prevent scattering-rate promotion.

All original archived radial coefficients are reconstructed as *exact
binary64 rationals*. Frobenius and tail envelopes are exact Fraction.
CoulombH outgoing logarithmic derivatives use 60+dps mpmath; these
numerical values are independently checked but not interval certified.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as Q
from multiprocessing import get_context
from pathlib import Path
from math import factorial
from time import perf_counter
import hashlib
import mpmath as mp

from .phys33_coupled_source import exp_negative_bounds,outward_decimal
from .phys33_residual import ceil_sqrt_fixed
from .phys33_moments import _floor_sqrt_fixed
from .phys33_full_coupled_shell import _physical_radial_data

R=Q(7,10)
K=Q(7,10)
B=Q(20)
L_MAX=20
ORIG_SOURCE="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
SCHEMA="WU088_HH_PHYS44_COULOMB_REFERENCE_BOUNDARY_V1"


def _mpq(q:Q)->mp.mpf:
    return mp.mpf(q.numerator)/q.denominator


def _exp_positive_tail(z:Q,n:int)->Q:
    """Majorant exp(z)-sum_(m<=n) z^m/m!, 0<=z<n+2."""
    if z<0 or n<0 or z>=n+2:raise ValueError("positive Taylor tail ratio")
    return z**(n+1)/Q(factorial(n+1))/(1-z/Q(n+2))


def _exp_n_weighted_tail(z:Q,n:int)->Q:
    """Exact positive upper of sum_(m>n) m*z^m/m!."""
    if z<0 or n<1 or z>=n+1:raise ValueError("positive weighted Taylor tail")
    return z**(n+1)/Q(factorial(n))/(1-z/Q(n+1))


def regular_coulomb_origin(ell:int,r0:Q,degree:int=18,digits:int=20)->dict:
    """Rigorous logarithmic derivative for central homogeneous Coulomb regular u.

    u_reg=r^(ell+1) sum_n a_n r^n with a_0=1 and
    n(n+2ell+1)a_n+2a_(n-1)+kappa²a_(n-2)=0.
    Induction shows |a_n|<=2^n/n! at kappa²=49/100.
    This is a reference basis only: actual off-centre forcing is not zero.
    """
    if type(ell) is not int or ell<0 or ell>L_MAX or not isinstance(r0,Q) or not Q(0)<r0<Q(1,100) or not 4<=degree<=64:
        raise ValueError("valid ell, positive small exact radius, and degree")
    a=[Q(1)]
    for n in range(1,degree+1):
        x=2*a[n-1]+(K*K*a[n-2] if n>=2 else Q(0))
        a.append(-x/Q(n*(n+2*ell+1)))
    s=sum((v*r0**n for n,v in enumerate(a)),Q(0))
    ds=sum((Q(ell+1+n)*v*r0**n for n,v in enumerate(a)),Q(0))
    z=2*r0
    e=_exp_positive_tail(z,degree)
    d=Q(ell+1)*e+_exp_n_weighted_tail(z,degree)
    s0,s1=s-e,s+e
    d0,d1=ds-d,ds+d
    if s0<=0 or d0<=0:
        raise ArithmeticError("regular Coulomb origin positive envelope not verified")
    lo=d0/(r0*s1)
    hi=d1/(r0*s0)
    return {
        "ell":ell,"radius_a0":str(r0),"polynomial_degree":degree,
        "reference_Coulomb_u_prime_over_u_per_a0_bracket":[
            outward_decimal(lo,digits,False),outward_decimal(hi,digits,True)],
        "Taylor_absolute_state_remainder_upper":outward_decimal(e,digits+2,True),
        "Taylor_absolute_derivative_numerator_remainder_upper":outward_decimal(d,digits+2,True),
        "exact_recursion":"n(n+2l+1)a_n+2a_(n-1)+kappa^2 a_(n-2)=0, a_0=1",
        "not_admitted":"actual two-centre inhomogeneous origin continuation"
    }


def _mp_complex(x:Q,y:Q)->mp.mpc:
    return mp.mpc(_mpq(x),_mpq(y))


def _coulomb_h(l:int,eta:mp.mpf,rho:mp.mpf)->mp.mpc:
    # Outgoing H_l^(+)=G_l + i F_l.
    return mp.coulombg(l,eta,rho)+1j*mp.coulombf(l,eta,rho)


def _coulomb_piece(job:tuple)->list[dict]:
    indices,dps=job
    with mp.workdps(dps):
        k=mp.mpf(7)/10
        rho=mp.mpf(14)
        eta=-1/k
        h={l:_coulomb_h(l,eta,rho) for l in
           sorted(set(indices)|{l+1 for l in indices})}
        records=[]
        for ell in indices:
            fac=mp.sqrt(1+(eta/mp.mpf(ell+1))**2)
            dl=((mp.mpf(ell+1)/rho)+eta/(ell+1))*h[ell]-fac*h[ell+1]
            z=k*dl/h[ell]
            w=mp.im(mp.conj(h[ell])*dl)
            flux=k/abs(h[ell])**2
            if abs(w-1)>mp.mpf(10)**(-dps+12) or abs(mp.im(z)-flux)>mp.mpf(10)**(-dps+12):
                raise ArithmeticError("Coulomb outgoing Wronskian normalization broken")
            if mp.im(z)<=0:raise ArithmeticError("outgoing channel flux not positive")
            records.append({
                "ell":ell,
                "coulomb_eta":"-10/7","rho":"14",
                "outgoing_z_re_per_a0":mp.nstr(mp.re(z),min(dps-12,42)),
                "outgoing_z_im_per_a0":mp.nstr(mp.im(z),min(dps-12,42)),
                "Wronskian_im_conjugateH_dH":mp.nstr(w,min(dps-12,42)),
                "channel_current_im_z":mp.nstr(flux,min(dps-12,42)),
            })
        return records


def outward_coulomb_reference(dps:int=64,workers:int=1)->list[dict]:
    if dps<36 or dps>120 or workers not in (1,2,3,4):
        raise ValueError("controlled precision/process count")
    groups=[list(range(w,L_MAX+1,workers)) for w in range(workers)]
    if workers==1:
        out=[_coulomb_piece((groups[0],dps))]
    else:
        with ProcessPoolExecutor(max_workers=workers,mp_context=get_context("forkserver")) as pool:
            out=list(pool.map(_coulomb_piece,[(g,dps) for g in groups]))
    ret=sorted((x for g in out for x in g),key=lambda x:x["ell"])
    if [z["ell"] for z in ret]!=list(range(L_MAX+1)):
        raise ArithmeticError("21 original Coulomb modes not covered")
    return ret


def boundary_reference(frozen:str|Path,dps:int=64,workers:int=1,
                       origin_degree:int=18,digits:int=20)->dict:
    tic=perf_counter()
    source=Path(frozen)
    identity=hashlib.sha256(source.read_bytes()).hexdigest()
    if identity!=ORIG_SOURCE:raise ValueError("frozen 1386 source identity mismatch")
    # The original saved r[0] is exact IEEE binary64, not 1/10000 rational.
    import numpy as np
    with np.load(source,allow_pickle=False) as z:
        origin_radius=Q(*float(z["r"][0]).as_integer_ratio())
    interior,origin_sha,origin_panel=_physical_radial_data(source,origin_radius)
    exterior,exterior_sha,exterior_panel=_physical_radial_data(source,B)
    if identity!=origin_sha or identity!=exterior_sha or (origin_panel,exterior_panel)!=(0,5):
        raise ArithmeticError("wrong original radial endpoint selection")
    origin,ells=[],outward_coulomb_reference(dps,workers)
    with mp.workdps(dps):
        origin_frozen_diag=[]
        for ell,mode in enumerate(interior):
            rec=regular_coulomb_origin(ell,origin_radius,origin_degree,digits)
            origin.append(rec)
            re,im=mode
            v=_mp_complex(re[0],im[0]);w=_mp_complex(re[1],im[1])
            # Compute an exact-rational envelope of archived derivative mismatch
            mid=(Q(rec["reference_Coulomb_u_prime_over_u_per_a0_bracket"][0])+Q(rec["reference_Coulomb_u_prime_over_u_per_a0_bracket"][1]))/2
            half=(Q(rec["reference_Coulomb_u_prime_over_u_per_a0_bracket"][1])-Q(rec["reference_Coulomb_u_prime_over_u_per_a0_bracket"][0]))/2
            dr=re[1]-mid*re[0];di=im[1]-mid*im[0]
            mismatch=Q(ceil_sqrt_fixed(dr*dr+di*di,digits))
            state=Q(ceil_sqrt_fixed(re[0]*re[0]+im[0]*im[0],digits))
            origin_frozen_diag.append({
                "ell":ell,
                "frozen_r0_derivative_minus_regular_Coulomb_reference_upper":str(mismatch+half*state),
                "status":"REFERENCE_ONLY_ORIGINAL_INHOMOGENEOUS_ORIGIN_NOT_CERTIFIED",
            })
        exterior_records=[]
        norm_y2=norm_yp2=Q(0)
        mismatch2=mp.mpf(0)
        for ell,mode in enumerate(exterior):
            re,im=mode
            u=_mp_complex(re[0],im[0])
            up=_mp_complex(re[1],im[1])
            z=mp.mpc(ells[ell]["outgoing_z_re_per_a0"],
                     ells[ell]["outgoing_z_im_per_a0"])
            m=up-z*u
            mismatch2+=abs(m)**2
            norm_y2+=(re[0]*re[0]+im[0]*im[0])/B**2
            dre=re[1]/B-re[0]/B**2
            dim=im[1]/B-im[0]/B**2
            norm_yp2+=dre*dre+dim*dim
            exterior_records.append({
                **ells[ell],
                "frozen_reduced_u_boundary_mismatch_abs":mp.nstr(abs(m),min(dps-12,42)),
                "original_archived_u20_real":str(re[0]),
                "original_archived_u20_imag":str(im[0]),
            })
        reduction=mp.sqrt(mismatch2)
        y=Q(ceil_sqrt_fixed(norm_y2,digits))
        yp=Q(ceil_sqrt_fixed(norm_yp2,digits))
    dmin=B-R
    e1=exp_negative_bounds(dmin,192)[1]
    e2=exp_negative_bounds(2*dmin,192)[1]
    ee=exp_negative_bounds(B,192)[1]
    if e1>=1:raise ArithmeticError("screening factor not less than one")
    lift=e1/(1-e1)
    # F-1 <= q/(1-q), |partial_r F|<=q/(1-q), q=exp[-(B-R)].
    # eta=F*y. The *physical scattered* field is xi=F*y-phi.
    # Preserve these two distinct trace transformations explicitly.
    eta_delta_state=lift*y
    eta_delta_derivative=lift*(y+yp)
    xi_delta_state=eta_delta_state+2*ee
    xi_delta_derivative=eta_delta_derivative+2*ee
    screenedV=(1+1/dmin)*e2
    # Base h has -V_scr; equation for u has +2V_scr. Integrate
    # 2(1+1/(r-R))exp[-2(r-R)] dr <= (1+1/dmin)exp[-2dmin].
    screened_l1=screenedV
    return {
        "schema":SCHEMA,
        "frozen_source_sha256":identity,
        "frozen_original_complex_mode_values":1386,
        "physical_reference":"central Coulomb homogeneous baseline only (screened coupling and driven source excluded from its DtN)",
        "kappa":"7/10","reference_eta":"-10/7",
        "outer_radius_a0":"20","outer_panel":exterior_panel,
        "origin_radius_exact_binary64":str(origin_radius),
        "origin_panel":origin_panel,
        "origin_regular_Coulomb_reference":origin,
        "origin_actual_frozen_reference_mismatch":origin_frozen_diag,
        "outer_Coulomb_reference_outgoing":exterior_records,
        "outer_reduced_u20_minus_zc_u20_L2_diagnostic":mp.nstr(reduction,min(dps-12,42)),
        "outer_y_angular_L2_upper":str(y),
        "outer_derivative_y_angular_L2_upper":str(yp),
        "certified_screened_h_potential_sup_r_ge20_upper":outward_decimal(screenedV,digits,True),
        "certified_screened_u_equation_radial_L1_r_ge20_upper":outward_decimal(screened_l1,digits,True),
        "certified_F_minus_one_sup_r_ge20_upper":outward_decimal(lift,digits,True),
        "certified_eta_minus_y_surface_L2_upper":outward_decimal(eta_delta_state,digits,True),
        "certified_radial_derivative_eta_minus_y_surface_L2_upper":outward_decimal(eta_delta_derivative,digits,True),
        "certified_xi_minus_y_surface_L2_upper":outward_decimal(xi_delta_state,digits,True),
        "certified_radial_derivative_xi_minus_y_surface_L2_upper":outward_decimal(xi_delta_derivative,digits,True),
        "certified_xi_angular_l_gt20_leakage_surface_L2_upper":outward_decimal(eta_delta_state,digits,True),
        "certified_radial_derivative_xi_angular_l_gt20_leakage_surface_L2_upper":outward_decimal(eta_delta_derivative,digits,True),
        "angular_projection_proof":"(1-P_l<=20)(F*y-phi)=(1-P_l<=20)((F-1)*y); phi and original 21-mode y lie entirely in P_l<=20; orthogonal projection is contractive in L2(S2)",
        "arithmetic_status":"Frobenius and potential/lift bounds exact rational; Coulomb H outgoing z and frozen trace mismatch high precision numerical ONLY",
        "computational_budget":{"workers":workers,"mpmath_dps":dps,"origin_degree":origin_degree},
        "elapsed_s":perf_counter()-tic,
        "NOT_CERTIFIED":["full physical two-centre screened outgoing DtN",
                         "origin driven regular solution",
                         "original outgoing scattered xi=F*y-phi partial-wave DtN",
                         "continuous low Schur inverse/incoming adjoint",
                         "HH microscopic cross-section or thermal rate",
                         "rei_bianchi production activation"],
    }
