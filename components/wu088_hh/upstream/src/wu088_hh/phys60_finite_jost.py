"""PHYS60 R5 finite-angular *positive-energy* exact noncentral Jost theorem.

Finite arbitrary L / each m, all real original off-centre screened angular
matrix entries, no angular low/high coupling discarded. Jost Volterra existence
and outgoing-current strict boundary invertibility are mathematical theorems;
the numerical functions here only check their ingredients. There is NO uniform
L->infinity exterior Poisson/LAP bound in this module.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from functools import lru_cache
from hashlib import sha256
from math import exp, gamma, isfinite, pi, sqrt
import mpmath as mp
import numpy as np
from scipy.special import lpmv, gammaln
SCHEMA = 'WU088_HH_PHYS60_R5_FINITE_GALERKIN_REAL_ENERGY_JOST_V1'
FROZEN_SHA = 'f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d'
K=F(7,10)
ETA_C=F(-10,7)
R=F(7,10)
B=F(27)
PHYSICAL_E=F(49,200)  # Hartree; E=+k^2/2

def source_sha_guard(p: str|Path)->str:
    actual=sha256(Path(p).read_bytes()).hexdigest()
    if actual!=FROZEN_SHA:
        raise ValueError('immutable 1386 complex128 original NPZ SHA256 mismatch')
    return actual

def exp_lower_positive(q:F,n:int=160)->F:
    if not isinstance(q,F) or q<0 or type(n)!=int or not 32<=n<=512:
        raise ValueError('Fraction q>=0 and n in 32..512')
    t=F(1);s=F(1)
    for j in range(1,n+1):
        t*=q/j;s+=t
    return s

def screen_delta_upper()->F:
    """Physical V=2(1+1/s)e^-2s on all r>=27, exact upper."""
    d=2*(B-R)
    return 2*(1+1/(B-R))/exp_lower_positive(d,160)

def screen_at(r:float,mu:np.ndarray)->np.ndarray:
    if not np.isfinite(r) or r<float(B):raise ValueError('r>=27 required')
    a=np.asarray(mu,dtype=float)
    if np.any(~np.isfinite(a)) or np.any(np.abs(a)>1):raise ValueError('physical mu in [-1,1]')
    s=np.sqrt(r*r+float(R)**2-2*r*float(R)*a)
    return 2*(1+1/s)*np.exp(-2*s)

def angular_real_block(r:float,ells:tuple[int,...],m:int,nodes:int=192)->np.ndarray:
    """Real Hermitian physical all-n projected angular V=2S (noncertifying GL).
    Multiplication is diagonal in signed m; m and -m blocks coincide.
    """
    if type(m)!=int or not ells or any(type(l)!=int or l<abs(m) or l<0 or l>80 for l in ells) or len(set(ells))!=len(ells):
        raise ValueError('valid distinct finite angular channels')
    if type(nodes)!=int or not 64<=nodes<=512:raise ValueError('quadrature nodes 64..512')
    mu,w=np.polynomial.legendre.leggauss(nodes)
    v=screen_at(r,mu)
    ms=abs(m)
    basis=[]
    for l in ells:
        fac=np.sqrt((2*l+1)/2 * np.exp(gammaln(l-ms+1)-gammaln(l+ms+1)))
        basis.append(fac*lpmv(ms,l,mu))
    basis=np.asarray(basis,dtype=float)
    M=(basis*(w*v)[None,:])@basis.T
    return (M+M.T)*.5

@lru_cache(maxsize=4000)
def hplus(l:int,r:float,dps:int=60)->complex|mp.mpc:
    """Coulomb H+=G+iF at real positive-energy rho=k*r.
    A returned mp value is intended only for use within matching precision.
    """
    if type(l)!=int or not 0<=l<=200 or not isinstance(r,(int,float)) or not isfinite(r) or r<27:
        raise ValueError('finite mode and exterior r>=27')
    if type(dps)!=int or not 30<=dps<=150:raise ValueError('dps 30..150')
    with mp.workdps(dps):
        rho=mp.mpf(7)/10*mp.mpf(str(r));eta=mp.mpf(-10)/7
        return mp.mpc(mp.coulombg(l,eta,rho),mp.coulombf(l,eta,rho))

def hplus_derivative(l:int,r:float,dps:int=60)->mp.mpc:
    """Physical d/dr of outgoing H+, DLMF 33.4.4 recurrence."""
    with mp.workdps(dps):
        h=hplus(l,float(r),dps)
        hp=hplus(l+1,float(r),dps)
        rho=mp.mpf(7)/10*mp.mpf(str(r));eta=-mp.mpf(10)/7
        return (mp.mpf(7)/10)*(((l+1)/rho+eta/(l+1))*h-mp.sqrt(1+(eta/(l+1))**2)*hp)

def current_wronskian_check(l:int,r:float=27,dps:int=60)->dict:
    with mp.workdps(dps):
        H=hplus(l,r,dps);Hp=hplus_derivative(l,r,dps)
        residual=mp.im(mp.conj(H)*Hp)-mp.mpf(7)/10
        z=Hp/H
        return {'ell':l,'radius':r,'log10_flux_per_Bohr':mp.nstr(mp.log10(mp.im(z)),25),
                'real_impedance':mp.nstr(mp.re(z),28),
                'raw_wronskian_residual':mp.nstr(residual,10),
                'status':'NONCERTIFYING_MP_CHECK'}

def volterra_kernel(l:int,r:float,t:float,dps:int=60)->mp.mpc:
    """Real Coulomb Green Volterra row kernel K_l(r,t); r<=t.

    K=(H+(r)H-(t)-H-(r)H+(t))/(2ik), W(H-,H+)=2ik,
    K(t,t)=0 and dK/dr at r=t=+1; (d²+q)∫_r^∞ K V u=-Vu.
    """
    if r>t or r<27:raise ValueError('Volterra triangle 27<=r<=t')
    with mp.workdps(dps):
        a=hplus(l,float(r),dps); b=hplus(l,float(t),dps)
        return (a*mp.conj(b)-mp.conj(a)*b)/(2j*(mp.mpf(7)/10))

def make_r5_certificate(path:str|Path)->dict:
    actual=source_sha_guard(path)
    delta=screen_delta_upper()
    assert delta<F(3,10**23)
    return {
        'schema':SCHEMA,'frozen_npz_sha256':actual,
        'spectral_energy_hartree':str(PHYSICAL_E),'kappa':str(K),'coulomb_eta':str(ETA_C),
        'original_hamiltonian':'h=-Delta/2-1/r-(1+1/s) exp(-2s); s=|x-0.7 z|',
        'all_r_ge_B_upper_2S_fraction':str(delta),
        'uniform_source_bound':str(F(3,10**23)),
        'integral_tail_bound_at_B_fraction':str(delta/2),
        'finite_L_theorem':'For each finite L>=0, all signed m and l<=L, actual Galerkin screened V is real symmetric, integrable, and has Coulomb-modified outgoing Volterra-Jost U_L; boundary U_L(B) invertible by conserved positive flux; Z_L=Uprime(B)U(B)^-1, Im(g*Z_Lg)>0 for g!=0.',
        'volterra_convergence':'For each finite L, bounded Coulomb H± for r>=B imply a finite Volterra kernel C_L; iterates bounded by [C_L * integral ||V||]^n/n!. No uniform C_L as L->infty is claimed.',
        'Jost_normalization':'H_plus=G+iF; W_r(H_minus,H_plus)=+2i*kappa; outgoing current kappa*||a||²',
        'positive_energy_Green':'h^T (Z_S,L - Z_C,L) g = integral p_C^+(h)^T V p_S,L^+(g) dr, complex bilinear transpose; no conjugate; finite angular Galerkin only.',
        'P_Q_coupling':'P ell<=20 and Q ell>=21 retained inside any finite L>=21, m-conserved all m.',
        'no_uniform_infinite_L':'NOT_PROVED',
        'full_physical_all_angular_outgoing_DtN':'NOT_PROVED',
        'actual_xi_sigma_kHH':'NOT_PROVED','HH_R10':'OFF',
    }
