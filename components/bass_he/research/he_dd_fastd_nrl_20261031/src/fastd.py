"""Source-qualified finite-temperature *first-moment* FastD Coulomb stopping.

Physics: 2023 NRL Plasma Formulary p31 test-particle energy relaxation
nu_epsilon = 2[(m_D/m_beta)psi(x)-psi'(x)]nu0;
nu0 = 4*pi*n_beta*(Z_D Z_beta e^2/(4pi eps0))^2*lnLambda/(m_D^2*v^3).
It is an ensemble energy moment; the characteristic trajectory used here is a
conditional narrow-distribution approximation, not a Fokker-Planck kinetic solve.
Approximation: nonrelativistic K=0.5*m_D*v^2, Maxwellian fully ionized H/He
at same T_CMB(z), static Debye b_max, b_min=max(classical, quantum).
High-energy K>30 MeV is tagged EXTRAPOLATIVE_NONREL, never production heat.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from scipy import constants as c
from scipy.special import gammainc, zeta
from numpy.polynomial.legendre import leggauss

MEV_J=1e6*c.e
T0_K=2.7255
NB0_CM3=2.515e-7  # Source-locked to PR131 PDG/Planck2018 scenario
Y_HE=0.2448
MD=1875.61294500*MEV_J/c.c**2
MA=3727.3794118*MEV_J/c.c**2
H0=67.4*1e3/(1e6*c.parsec)
OM_M=0.315
h=0.674
OM_GAMMA=2.473e-5/h**2
OM_R=OM_GAMMA*(1+0.2271*3.046)
OM_L=1-OM_M-OM_R
ECOUL=c.e**2/(4*math.pi*c.epsilon_0)

@dataclass(frozen=True)
class Plasma:
    z: float
    T_K: float
    kBT_MeV: float
    n_b_m3: float
    n_e_m3: float
    n_p_m3: float
    n_a_m3: float
    H_s: float
    lambdaD_m: float


def plasma(z:float,y_he:float=Y_HE)->Plasma:
    if z<=0 or not (0<=y_he<=1): raise ValueError("redshift or helium fraction invalid")
    z1=1+z
    n_b=NB0_CM3*1e6*z1**3
    ne=(1-y_he/2)*n_b
    np_= (1-y_he)*n_b
    na=y_he*n_b/4
    kt=c.k*T0_K*z1
    # Coulomb static screening: each thermal charged species contributes Z^2 n.
    nsum=ne+np_+4*na
    ld=math.sqrt(c.epsilon_0*kt/(c.e**2*nsum))
    h0=H0*math.sqrt(OM_R*z1**4+OM_M*z1**3+OM_L)
    return Plasma(z,T0_K*z1,kt/MEV_J,n_b,ne,np_,na,h0,ld)


def psi(x:float)->tuple[float,float]:
    """NRL normalized Maxwellian Rosenbluth functions ψ(x), dψ/dx."""
    if x<0: raise ValueError("x nonnegative")
    if x==0: return 0.,0.
    return float(gammainc(1.5,x)),float(2/math.sqrt(math.pi)*math.sqrt(x)*math.exp(-x))


def spitzer_species(K_MeV:float,p:Plasma,species:str,log_mode:str="debye") -> dict:
    if K_MeV<=0:raise ValueError('K must be positive')
    if species not in ('electron','proton','alpha'):raise ValueError('unknown field species')
    mb,n,Z= {'electron':(c.m_e,p.n_e_m3,1),'proton':(c.m_p,p.n_p_m3,1),'alpha':(MA,p.n_a_m3,2)}[species]
    v=math.sqrt(2*K_MeV*MEV_J/MD)
    x=mb*v*v/(2*c.k*p.T_K)
    ps,dps=psi(x)
    mu=MD*mb/(MD+mb)
    vrel=math.sqrt(v*v+3*c.k*p.T_K/mb)
    bclass=Z*ECOUL/(mu*vrel*vrel)
    bquant=c.hbar/(2*mu*vrel)
    bmin=max(bclass,bquant)
    ln_debye=math.log(p.lambdaD_m/bmin)
    if log_mode=="debye": ln=ln_debye
    elif log_mode=="fixed20":ln=20.
    else:raise ValueError('bad log mode')
    if ln<=0: raise ValueError('strongly coupled / invalid Coulomb logarithm')
    nu0=4*math.pi*n*(Z*ECOUL)**2*ln/(MD*MD*v**3)
    nuE=2*((MD/mb)*ps-dps)*nu0
    # Energy moment loss -dK/dt = K nu_epsilon, may be negative near thermal equilibrium.
    dKdt=K_MeV*nuE
    return dict(field=species,x=x,psi=ps,dpsi=dps,lnLambda=ln,
                bmax_cm=p.lambdaD_m*100,bmin_cm=bmin*100,
                nuE_s=nuE,loss_MeV_s=dKdt,n_cm3=n*1e-6,
                nonrel_v_over_c=v/c.c,relativistic_exact_v_over_c=math.sqrt(1-(1+K_MeV/1875.612945)**-2))


def losses(K:float,p:Plasma,log_mode="debye") -> dict:
    vals={q:spitzer_species(K,p,q,log_mode) for q in ('electron','proton','alpha')}
    result={q:vals[q]['loss_MeV_s'] for q in vals}
    result['total']=sum(result.values())
    return result


def terminal(p:Plasma)->float:
    """Stop well above the thermal diffusion regime; species energy moments remain positive."""
    return max(0.001,30*p.kBT_MeV)


def integrate(K0:float,p:Plasma,order:int=160,log_mode="debye") -> dict:
    low=terminal(p)
    if K0<=low:raise ValueError('birth kinetic energy below deterministic stopping window')
    nodes,weights=leggauss(order)
    t0,t1=math.log(low),math.log(K0)
    t=.5*(t1+t0)+.5*(t1-t0)*nodes
    k=np.exp(t)
    dk=.5*(t1-t0)*k*weights
    e=np.empty(len(k)); pp=np.empty(len(k)); aa=np.empty(len(k))
    for i,ki in enumerate(k):
        x=losses(float(ki),p,log_mode)
        e[i],pp[i],aa[i]=x['electron'],x['proton'],x['alpha']
    tot=e+pp+aa
    if np.min(tot)<=0 or not np.all(np.isfinite(tot)):raise ValueError('non-positive or invalid stopping in chosen window')
    dt=dk/tot
    speed=np.sqrt(2*k*MEV_J/MD)
    T=float(np.sum(dt));L=float(np.dot(speed,dt))
    Qe=float(np.dot(e/tot,dk));Qp=float(np.dot(pp/tot,dk));Qa=float(np.dot(aa/tot,dk))
    # Column density of each target along the narrow-beam characteristic: cm^-2.
    Np=L*p.n_p_m3*1e-4
    Na=L*p.n_a_m3*1e-4
    return dict(z=p.z,K0_MeV=K0,K_terminal_MeV=low,deltaK_MeV=K0-low,
                Q_e_MeV=Qe,Q_p_MeV=Qp,Q_alpha_MeV=Qa,Q_ion_MeV=Qp+Qa,
                t_stop_s=T,L_path_m=L,stop_over_Hubble=T*p.H_s,
                path_over_Hubble_length=L*p.H_s/c.c,
                exposure_p_cm2=Np,exposure_alpha_cm2=Na,
                tau_reference_p_1mb=Np*1e-27,tau_reference_alpha_1mb=Na*1e-27,
                q_sum_residual_MeV=Qe+Qp+Qa-(K0-low),
                K_over_rest=K0/1875.612945,
                source_scope='EXPLORATORY_NONREL' if K0>30 else 'NONREL_LEADING_LOG',
                profile_order=order,log_mode=log_mode)


def energy_probe(p:Plasma,K:float)->dict:
    rates={sp:spitzer_species(K,p,sp) for sp in ('electron','proton','alpha')}
    return {"z":p.z,"K_MeV":K,"K_over_kBT":K/p.kBT_MeV,"loss_e_MeV_s":rates['electron']['loss_MeV_s'],
      "loss_p_MeV_s":rates['proton']['loss_MeV_s'],"loss_alpha_MeV_s":rates['alpha']['loss_MeV_s'],
      "ln_e":rates['electron']['lnLambda'],"ln_p":rates['proton']['lnLambda'],"ln_alpha":rates['alpha']['lnLambda'],
      "source_scope":'EXTRAPOLATIVE_NONREL' if K>30 else 'NONREL_LEADING_LOG'}

# Actual source-owned asymptotic daughter kinetic energies are author nominal PR129,
# not event-by-event 1965 detector measurements. Source SHA given in REPRODUCE.md.
NOMINAL_SOURCE_DAUGHTERS=[77.667738527,93.971292109,118.985783273,147.482229691]
BIRTH_ENERGIES=[0.1,1.,10.,30.,50.,100.]+NOMINAL_SOURCE_DAUGHTERS
REDSHIFTS=[1e4,3e4,1e5,3e5,1e6]
