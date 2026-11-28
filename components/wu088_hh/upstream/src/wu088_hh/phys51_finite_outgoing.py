"""PHYS51 finite high-angular outgoing Coulomb + physical off-centre screened theorem.

This is the band 21<=ell<=28 (ALL m) and r>=27 a0 only.
The original real screen S=(1+1/s) exp(-2s), s=|x-(7/10) zhat|.
A rigorous rational majorant yields a weighted Volterra contraction for
the FULL angular projected multiplication P_band S P_band (not central-only).
The screened outgoing Jost boundary matrix is invertible by real-potential
current conservation. No claim is made for the infinite angular complement,
a boundary inverse *norm*, low-channel forcing, sigma(E), or HH_R10.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import isqrt
import hashlib
from pathlib import Path
import mpmath as mp

from .phys46_volterra import exp_positive_rational_upper
from .phys33_coupled_source import exp_negative_bounds, outward_decimal
from .phys49_dirichlet_collar import FROZEN_SHA

SCHEMA="WU088_HH_PHYS51_FINITE_HIGH_BAND_SCREENED_OUTGOING_V1"
K=F(7,10)
R=F(7,10)
B=F(27)
C=F(4,5)
LOW=21
HIGH=28

def lognorm_max(lo:int, hi:int, T:int)->F:
    """Logarithmic Euclidean norm of (u,u'/k) on [27,T].

    A=[[0,k],[-q/k,0]], mu_2(A)=|k-q/k|/2,
    q=k^2+2/r-ell(ell+1)/r^2. The high band ensures
    ell(ell+1)/r^2-2/r>0 and decreasing for r in [B,T].
    """
    if not 21<=lo<=hi<=64 or not 35<=T<=60:
        raise ValueError("validated high-band and finite patch only")
    if T>=lo*(lo+1)//2:
        raise ValueError("monotone centrifugal interval required")
    return (F(hi*(hi+1),B*B)-F(2,B))/(2*K)

def _energy_patch(T:int,lo:int,hi:int,terms:int)->dict:
    if not 40<=T<=50:
        raise ValueError("bounded energy patch 40..50")
    if not 21<=lo<=hi<=64:
        raise ValueError("finite high Coulomb band")
    if not 128<=terms<=256:
        raise ValueError("exact exponential series precision")
    mu=lognorm_max(lo,hi,T)
    if not F(0)<mu<C:
        raise ArithmeticError("backward propagator rate not certified")
    L=hi*(hi+1)
    Tq=F(T)
    qmin=K*K+2/Tq-F(L,T*T)
    # q_l(r) has one maximum at r=L, and tends to k². At T
    # qmin is the uniform positive lower bound across all ell and r>=T.
    if not 0<qmin<K*K:
        raise ArithmeticError("oscillatory positive-energy patch required")
    variation=F(2,T)+F(L,T*T)
    z=variation/qmin
    emax=exp_positive_rational_upper(z,128)
    M2=2*K*K*emax*(1/qmin+1/(K*K))
    m=isqrt(M2.numerator//M2.denominator)+1
    if m*m<=M2:
        m+=1
    assert F(m*m)>M2
    # w(r)=M exp(C(T-r)) on B<=r<=T; M after T.
    # ||V|| <= S(r-R), including ALL m and the full noncentral screen.
    p1=2*(B-R)-2*C*(Tq-B)
    p2=2*(Tq-R)
    if not p1>0 or not p2>0:
        raise ArithmeticError("positive exponential majorant")
    s1=exp_negative_bounds(p1,terms)[1]
    s2=exp_negative_bounds(p2,terms)[1]
    qb=F(m*m)/K*(1+1/(B-R))*(s1/(1+C)+s2)
    return {
        "T":T,"M":m,"M2_required":M2,"qmin":qmin,
        "variation":variation,"exp_energy_upper":emax,
        "lognorm_max":mu,"p1":p1,"p2":p2,
        "q_upper_exact":qb,
    }

def finite_band_screened_jost(frozen:str|Path,
        lo:int=LOW,hi:int=HIGH,patches:tuple[int,...]=(42,43,44,45,46),
        terms:int=192,digits:int=24)->dict:
    """Rigorous contraction certificate in all-m finite high angular band.

    Coulomb |H_l+| and |H_l+'|/k have rational energy envelope w(r);
    |K_l(r,t)| <=w(r)w(t)/k. The physical screen compression has
    operator norm <=(1+1/(r-R)) exp[-2(r-R)]. Thus the outgoing
    Volterra map obeys ||V||_w <= q<1, for all m in the band.
    For the Hermitian real screen, constant current at infinity is
    k||a||², proving the Jost boundary matrix at r=B is injective,
    hence invertible in finite dimension. No quantitative inverse norm.
    """
    p=Path(frozen)
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    if digest != FROZEN_SHA:
        raise ValueError("original immutable 1386 complex128 input mismatch")
    if not 21<=lo<=hi<=28 or type(lo) is not int or type(hi) is not int:
        raise ValueError("scoped finite source-aligned band 21..28")
    if not patches or any(type(t) is not int or t<40 or t>50 for t in patches):
        raise ValueError("bounded patch range required")
    if len(set(patches))!=len(patches) or not 16<=digits<=27:
        raise ValueError("distinct patches and outward decimal digits")
    rows=[_energy_patch(t,lo,hi,terms) for t in patches]
    best=min(rows,key=lambda x:(x["q_upper_exact"],x["T"]))
    q=best["q_upper_exact"]
    if not 0<q<F(1,2):
        raise ArithmeticError("screened Volterra contraction not established")
    alpha=q/(1-q)
    return {
        "schema":SCHEMA,
        "source_sha256":digest,
        "physical_screen":"(1+1/s)exp(-2s), s=|r n - (7/10) zhat|",
        "exterior_radius_Bohr":"27",
        "angular_band_inclusive":[lo,hi],
        "all_m":True,
        "n_channels":(hi+1)**2-lo**2,
        "kappa":"7/10","Coulomb_eta":"-10/7",
        "radial_equation":"u''+[k²+2/r-ell(ell+1)/r²]u+2 P_band S P_band u=0",
        "certified_patch_T_Bohr":best["T"],
        "energy_uniform_floor_exact":str(best["qmin"]),
        "qprime_variation_upper_exact":str(best["variation"]),
        "lognorm_mu_bound_exact":str(best["lognorm_max"]),
        "lognorm_chosen_C_exact":str(C),
        "integer_energy_amplitude_M":best["M"],
        "M2_exact_rational_upper":str(best["M2_required"]),
        "w":"M exp[(4/5)(T-r)] on 27<=r<=T; M on r>=T",
        "exponential_exponents_exact":[str(best["p1"]),str(best["p2"])],
        "screened_Volt_q_exact_rational_upper":str(q),
        "screened_Volt_q_outward":outward_decimal(q,digits,True),
        "Neumann_relative_weighted_solution_error_upper":
            outward_decimal(alpha,digits,True),
        "Jost_boundary_matrix_invertible":
            True,
        "Jost_invertibility_proof":
            "For real Hermitian projected S, J(r)=Im(u^dagger u') "
            "is constant. At infinity J=k||a||²>0 for outgoing "
            "nonzero a; if u(B)=0 then J(B)=0, contradiction.",
        "screened_DtN_imaginary_form":
            "Im <g,Z_out(B)g> = k||U(B)^(-1)g||² > 0 for g!=0",
        "coupling_with_PHYS50":
            "On T=27 interface: (Lambda_D g)_T-Z_out(27)g_T="
            "forcing_boundary_correction; g_B and physical forcing UNKNOWN",
        "status":"RIGOROUS_FINITE_HIGH_21_TO_28_ALL_M_HOMOGENEOUS_OUTGOING",
        "not_certified":[
            "infinite ell>=21 outgoing operator or a uniform inverse norm",
            "full physical low/high Schur coupling and driven xi=F*y-phi",
            "origin regularity, incoming adjoint and physical sigma(E)",
            "Maxwellian k_HH(T) and rei_bianchi HH_R10 adoption"
        ],
        "patch_comparison":[{
            "T":a["T"],"M":a["M"],
            "q_outward":outward_decimal(a["q_upper_exact"],digits,True)
        } for a in rows],
    }

def coulomb_impedance_rows(ells:tuple[int,...]=(21,24,28),
                           radius:int=27,dps:int=70)->list[dict]:
    """Non-interval reference only. Exact flux identity checked with mpmath."""
    if not ells or any(type(l) is not int or l<21 or l>28 for l in ells):
        raise ValueError("reference high band 21..28")
    if not 27<=radius<=40 or not 48<=dps<=110:
        raise ValueError("boundary / high precision")
    with mp.workdps(dps):
        k=mp.mpf(7)/10
        eta=-1/k
        rho=k*radius
        cache={}
        for l in set(ells)|{l+1 for l in ells}:
            cache[l]=mp.coulombg(l,eta,rho)+1j*mp.coulombf(l,eta,rho)
        rows=[]
        for l in ells:
            h=cache[l]
            # DLMF §33.4.4, no noisy finite differences.
            hprime=((l+1)/rho+eta/(l+1))*h \
                   -mp.sqrt(1+(eta/(l+1))**2)*cache[l+1]
            z=k*hprime/h
            w=mp.im(mp.conj(h)*hprime)
            exactflux=k/abs(h)**2
            tol=mp.power(10,-dps+15)
            if abs(w-1)>tol or abs(mp.im(z)-exactflux)>tol:
                raise ArithmeticError("Coulomb Wronskian/current failed")
            if mp.im(z)<=0:
                raise ArithmeticError("incoming/outgoing sign swapped")
            rows.append({
                "ell":l,"radius_Bohr":radius,"eta":"-10/7",
                "z_re_per_Bohr":mp.nstr(mp.re(z),35),
                "z_im_per_Bohr":mp.nstr(mp.im(z),35),
                "wronskian_Im_conjH_dH":mp.nstr(w,35),
                "normal_current_k_over_H2":mp.nstr(exactflux,35),
            })
        return rows
