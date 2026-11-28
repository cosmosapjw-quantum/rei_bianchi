"""Source-labelled early-Universe EM opacity and fast deuteron electron drag.

All outputs are physical predictions conditional on a specified homogeneous,
fully ionized flat FLRW radiation+baryon model. This is NOT a sourced high-E
photon injection history or a complete energy deposition/thermal heating solver.
"""
import math
from functools import lru_cache
import numpy as np
from scipy import constants as c
from scipy.special import erf, zeta
from scipy.integrate import quad

# SI source constants; MeV for photon and nuclear energies; cgs where indicated.
ELECTRON_MEV = c.physical_constants['electron mass energy equivalent in MeV'][0]
DEUTERON_MEV = 1875.61294500  # prior PR126, original table masses converted to modern values
ALPHA_MEV = 3727.3794118
HC_MEV_CM = (c.hbar*c.c)/(1e6*c.e) * 100.0
T0_K = 2.7255
KBT0_MEV = c.k*T0_K / (1e6*c.e)
SIGMA_T_CM2 = c.physical_constants['Thomson cross section'][0] * 1e4
N_B0_CM3 = 2.515e-7 # PDG Astrophysical Constants
Y_P = 0.2448
H0_KM_S_MPC = 67.4
H0_S = H0_KM_S_MPC*1e3/(c.parsec*1e6)
h = H0_KM_S_MPC/100
OM_M = 0.315
OM_GAMMA = (2.473e-5)/(h*h) * (T0_K/2.7255)**4
NEFF = 3.046
OM_R = OM_GAMMA*(1 + 0.2271*NEFF)
OM_L = 1-OM_M-OM_R
Q_MEV = 2*DEUTERON_MEV-ALPHA_MEV
# Original constrained Rice 2000 source fit, PR128, not a pointwise measurement.
SIGMA_RICE_NB = ((150.,190.,8.29),(190.,250.,4.34))
GAMMA_E_MEV = [150.,170.,190.,220.,250.]
D_E_MEV = [50.,75.,100.,125.,150.]
REDSHIFTS = [1.0e4, 3.0e4, 1.0e5, 2.0e5, 3.0e5, 5.0e5, 1.0e6,2.0e6, 5.0e6,1.0e7,2.0e7]


def state(z):
    if z <= 0: raise ValueError('positive z required')
    z1 = 1+z
    return dict(z=z,T_K=T0_K*z1,kBT_MeV=KBT0_MEV*z1,
        n_b_cm3=N_B0_CM3*z1**3,
        n_e_cm3=N_B0_CM3*(1-Y_P/2)*z1**3,
        n_H_cm3=N_B0_CM3*(1-Y_P)*z1**3,
        n_alpha_cm3=N_B0_CM3*Y_P/4*z1**3,
        H_s_inv=H0_S*math.sqrt(OM_R*z1**4 + OM_M*z1**3 + OM_L))


def bw_sigma_cm2(beta):
    """Breit-Wheeler total gamma+gamma -> e+e- cross section, Gould & Schreder (1967)."""
    b=np.asarray(beta, dtype=float)
    b=np.clip(b,0,1-1e-15)
    term=(3-b**4)*np.log1p(2*b/(1-b)) - 2*b*(2-b*b)
    res=(3/16)*SIGMA_T_CM2*(1-b*b)*term
    return res if np.ndim(beta)>0 else float(res)

@lru_cache(None)
def gauss_nodes(n):
    t,w=np.polynomial.legendre.leggauss(n)
    return (t+1)/2,w/2


def bb_pair_rate_s(E_MeV,z,nx=128,nu=96):
    """gamma-gamma attenuation frequency for a test photon in isotropic Planck CMB.
    n_gamma(epsilon,z) = epsilon^2 / (pi^2 (hbar c)^3)/[exp(epsilon/kT)-1].
    Gamma=c int d epsilon n int_0^1 2u sigma_BW(E,epsilon,u) du,
    u=(1-cos theta)/2, E epsilon u >= (m_e c^2)^2.
    """
    if E_MeV <= 0: raise ValueError('positive test gamma energy required')
    kbt=state(z)['kBT_MeV']
    xmin=ELECTRON_MEV**2/(E_MeV*kbt)
    if xmin>700: return 0.0
    xx,wx=gauss_nodes(nx)
    # integrate above exact pair threshold; Planck exponentially cut off.
    x = xmin + 65.0*xx
    y,wu=gauss_nodes(nu)
    umin=(xmin/x)[:,None]
    # Squared coordinates resolve the threshold sqrt(1-xmin/(x*u)).
    u=umin+(1-umin)*y[None,:]**2
    beta=np.sqrt(np.maximum(0,1-xmin/(x[:,None]*u)))
    angular=np.sum(2*u*bw_sigma_cm2(beta)*(1-umin)*(2*y)[None,:]*wu[None,:],axis=1)
    # x^2/(e^x-1) stable for x>1.
    planck=np.exp(-x)/(-np.expm1(-x))
    integral=65*np.sum(wx*x*x*planck*angular)
    n_pref = kbt**3 / (math.pi**2*HC_MEV_CM**3)
    return float(c.c*100*n_pref*integral)


def bw_pair_quad_independent(E_MeV,z):
    """Independent nested quadrature with linear u (not squared transform)."""
    kbt=state(z)['kBT_MeV']; xmin=ELECTRON_MEV**2/(E_MeV*kbt)
    if xmin>700: return 0.0
    def fsigma(u,x):
        t=1-xmin/(x*u)
        return 2*u*bw_sigma_cm2(math.sqrt(max(t,0)))
    def fx(x):
        u0=xmin/x
        inner=quad(fsigma,u0,1,args=(x,),epsrel=1e-8,epsabs=1e-33,limit=100)[0]
        return x*x/math.expm1(x)*inner
    integ=quad(fx,xmin,xmin+65,epsrel=1e-8,epsabs=1e-33,limit=100)[0]
    return c.c*100*kbt**3/(math.pi**2*HC_MEV_CM**3)*integ


def gg_number_density(z):
    kbt=state(z)['kBT_MeV']
    return 2*zeta(3)*kbt**3/(math.pi**2*HC_MEV_CM**3)


def he_dd_rate_per_photon(E_MeV,z):
    for lo,hi,s in SIGMA_RICE_NB:
        if lo<=E_MeV<(hi if hi!=250 else hi+1e-14):
            return state(z)['n_alpha_cm3']*(c.c*100)*s*1e-33
    raise ValueError('source bin model only defined for E=150..250 MeV')


def d_beta(E_MeV):
    if E_MeV<0: raise ValueError('D kinetic energy >=0')
    return math.sqrt(1-(DEUTERON_MEV/(DEUTERON_MEV+E_MeV))**2)


def d_electron_drag(E_MeV,z):
    """Leading-log Maxwellian electron drag with explicit static/dynamic screening.
    Diagnostic electron friction ONLY, not complete BPS next-order plasma
    stopping, D-on-ion nuclear reactions, escape, or deposited thermal heat.
    Coulomb loss: 4 pi n_e (e^2/4pi eps0)^2 ln Lambda/(m_e v) F(v/sqrt(2 kT/m_e)).
    """
    if E_MeV <= 0: raise ValueError('positive fast D required')
    s=state(z); beta=d_beta(E_MeV); v=beta*c.c
    ne=s['n_e_cm3']*1e6; kT_J=s['kBT_MeV']*1e6*c.e
    vth=math.sqrt(kT_J/c.m_e)
    x=v/(math.sqrt(2)*vth)
    F=math.erf(x)-2/math.sqrt(math.pi)*x*math.exp(-x*x)
    e2=c.e*c.e/(4*math.pi*c.epsilon_0) # J*m
    lamD=math.sqrt(c.epsilon_0*kT_J/(ne*c.e**2))
    wp=math.sqrt(ne*c.e**2/(c.epsilon_0*c.m_e))
    b_cl=e2/(c.m_e*v*v); b_q=c.hbar/(2*c.m_e*v)
    bmin=max(b_cl,b_q)
    ln_static=math.log(lamD/bmin)
    ln_dynamic=math.log(max(lamD,v/wp)/bmin)
    gamma_ee = e2 / (kT_J*(3/(4*math.pi*ne))**(1/3)) # classical plasma coupling
    lead=4*math.pi*ne*e2*e2/(c.m_e*v)*F/(1e6*c.e)
    dE_static=lead*ln_static
    dE_dynamic=lead*ln_dynamic
    return dict(E_d_MeV=E_MeV,z=z,beta_d=beta,n_e_cm3=s['n_e_cm3'],
         kBT_MeV=s['kBT_MeV'],thermal_F=F,lambda_D_cm=100*lamD,
         b_min_cm=100*bmin,lnLambda_static=ln_static,lnLambda_dynamic=ln_dynamic,
         plasma_coupling_gamma=gamma_ee,
         dE_dt_e_static_MeV_s=dE_static,
         dE_dt_e_dynamic_MeV_s=dE_dynamic,
         t_loss_e_static_s=E_MeV/dE_static,
         t_loss_e_dynamic_s=E_MeV/dE_dynamic,
         t_loss_e_dynamic_over_Hubble=(E_MeV/dE_dynamic)*s['H_s_inv'])


def born_d_pair_kinetics(E_MeV,mu):
    if E_MeV<Q_MEV: raise ValueError('below threshold')
    s=ALPHA_MEV*ALPHA_MEV+2*ALPHA_MEV*E_MeV
    delta=E_MeV/2*math.sqrt(1-4*DEUTERON_MEV**2/s)
    midpoint=(E_MeV-Q_MEV)/2
    return midpoint+delta*mu,midpoint-delta*mu
