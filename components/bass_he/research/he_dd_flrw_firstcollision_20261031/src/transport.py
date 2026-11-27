"""Source-anchored, model-conditional first-collision Green's kernel (NOT full cascade).

Four channels: BW on exact thermal Planck CMB, KN on approximately stationary
fully-ionized electrons, high-energy point-nucleus unscreened BH Born on H/He,
and He4(gamma,dd) Rice2000 fitted bin MODEL. E(z)=E_inj*(1+z)/(1+z_inj).

All rates are in local comoving alpha rest frame. A Compton collision does not
annihilate the photon; this solves only the probability of the FIRST collision.
This does not close the global gamma transport or source normalization/heat.
"""
import math
import numpy as np
from scipy import constants as c
from scipy.integrate import solve_ivp, quad
from physics_pr131 import (
    ELECTRON_MEV, SIGMA_T_CM2, GAMMA_E_MEV, Q_MEV, ALPHA_MEV,
    DEUTERON_MEV, bb_pair_rate_s, he_dd_rate_per_photon, state,
)

RE = c.physical_constants['classical electron radius'][0]*100.0  # cm
ALPHA_QED = c.alpha
C_CM_S=c.c*100
K_MIN=150.0


def sigma_kn(E_MeV):
    """Total Klein-Nishina, unpolarized e- at rest, exact tree-level QED."""
    if E_MeV<=0: raise ValueError('E_gamma must be positive')
    x=E_MeV/ELECTRON_MEV
    bracket=(1+x)/x**3*(2*x*(1+x)/(1+2*x)-math.log1p(2*x)) + math.log1p(2*x)/(2*x) - (1+3*x)/(1+2*x)**2
    return 0.75*SIGMA_T_CM2*bracket


def sigma_kn_independent(E_MeV):
    """Independent angular integral of differential KN; numerical validation."""
    x=E_MeV/ELECTRON_MEV
    def dsig(mu):
        k=1/(1+x*(1-mu))
        return math.pi*RE**2*k*k*(k+1/k-(1-mu*mu))
    return quad(dsig,-1,1,epsrel=1e-11,epsabs=1e-38,limit=500)[0]


def sigma_bh_born_unscreened(E_MeV,Z):
    """Asymptotic high-energy unscreened (bare ion) BH sigma, born point nucleus.
    Racah/BH: alpha Z^2 r_e^2[(28/9) ln(2E/m_e c^2)-218/27].
    E >=150 MeV, only H and He nuclei. Neglect O(m_e/E), O(Z alpha) etc.
    Not valid for neutral atomic screened tabulations or near threshold.
    """
    if E_MeV<150 or Z not in (1,2):
        raise ValueError('validated domain 150..250 MeV; Z=1 or 2')
    return ALPHA_QED*Z*Z*RE*RE*((28/9)*math.log(2*E_MeV/ELECTRON_MEV)-218/27)


def four_channel_rates(E_MeV,z):
    if E_MeV<150-1e-8 or E_MeV>250:raise ValueError('only modeled 150..250 MeV')
    E=max(150,E_MeV)
    a=state(z)
    return dict(
        bw=bb_pair_rate_s(E,z),
        kn=a['n_e_cm3']*C_CM_S*sigma_kn(E),
        bh=a['n_H_cm3']*C_CM_S*sigma_bh_born_unscreened(E,1)+a['n_alpha_cm3']*C_CM_S*sigma_bh_born_unscreened(E,2),
        dd=he_dd_rate_per_photon(E,z),
    )


def flight(E_inj,z_inj,tau_stop=65,rtol=5e-9):
    """Integrate first collision along FLRW null-geodesic using cumulative optical depth tau.
    u = ln[(1+z_inj)/(1+z)], E=Einj exp(-u), dt=du/H(z).
    First-event probability P_j = integral_0^tau exp(-tau') Gamma_j/Gamma_tot dtau'.
    Output residual surviving until 150 MeV or survival bound e^-tau_stop.
    No scattering regeneration; KN first hit is NOT final absorption.
    """
    if not (150<E_inj<=250):raise ValueError('injection photon energy 150<E<=250 MeV')
    if z_inj<10000 or z_inj>1e6:raise ValueError('this reference FLRW cold-electron kernel z 1e4..1e6 only')
    u_end=math.log(E_inj/K_MIN)
    names=('bw','kn','bh','dd')
    def rates_and_fields(u):
        e=E_inj*math.exp(-u)
        z=(1+z_inj)*math.exp(-u)-1
        return e,z,four_channel_rates(max(K_MIN,e),z)
    def rhs(tau,y):
        u=y[0]; e,z,r=rates_and_fields(u); H=state(z)['H_s_inv']; rates=np.array([r[k] for k in names]); h=rates.sum()/H
        if h<=0: raise ArithmeticError('invalid opacity')
        frac=rates/rates.sum(); hit=math.exp(-tau)*frac
        birth=(e-Q_MEV)*hit[3]
        return np.r_[1/h,hit,birth,e*hit[3]]
    def stop(t,y):return y[0]-u_end
    stop.terminal=True;stop.direction=1
    # Different absolute scales preserve ultra-rare (~1e-18) DD channel accuracy.
    atol=[5e-15,4e-13,4e-13,4e-13,1e-29,1e-27,1e-27]
    sol=solve_ivp(rhs,(0,tau_stop),[0.,0.,0.,0.,0.,0.,0.],events=stop,rtol=rtol,atol=atol,method='DOP853',max_step=1.0)
    if not sol.success:raise RuntimeError(sol.message)
    tau_end=float(sol.t[-1]); y=sol.y[:,-1]; u=float(y[0]);
    survived=math.exp(-tau_end)
    reached_150=bool(len(sol.t_events[0]))
    names=('bw','kn','bh','dd')
    ps=dict(zip(names,map(float,y[1:5])))
    closure=sum(ps.values())+survived
    if abs(closure-1)>3e-9:raise AssertionError('first collision probability not normalized: '+str(closure))
    return dict(E_inj_MeV=E_inj,z_inj=z_inj,z_terminal=(1+z_inj)*math.exp(-u)-1,
                E_terminal_MeV=E_inj*math.exp(-u),u_end=u,tau_end=tau_end,
                terminal_reason='reached_150_MeV' if reached_150 else 'optical_depth_65_bound',
                P_reached_150_MeV_unhit=survived if reached_150 else None,
                P_unresolved_survival_upper_bound=0.0 if reached_150 else survived,
                P_BW_first=ps['bw'],P_KN_first=ps['kn'],P_BH_first=ps['bh'],P_dd_first=ps['dd'],
                P_no_collision_until_terminal=survived,
                P_first_normalization=closure,N_fastD_first_per_gamma=2*ps['dd'],
                kinetic_D_first_MeV_per_gamma=float(y[5]),
                average_dd_event_E_MeV=(float(y[6]/ps['dd']) if ps['dd']>0 else None),
                average_dd_event_K_pair_MeV=(float(y[5]/ps['dd']) if ps['dd']>0 else None),
                frame='local_comoving_alpha_rest_reference_FLRW',
                sigma_dd_kind='Rice2000_bin_fit_piecewise_model',
                BH_kind='unscreened_high_E_Born_nuclear_H_He',
                KN_kind='stationary_electron_first_scattering',
                source_kind='unit_delta_injection_scenario_not_measured_cosmic_history')


def toy_constant_opacity_test(lambdas,u_end):
    """Exactly soluble sanity check: constant hazards per logarithmic redshift."""
    ls=np.asarray(lambdas,dtype=float);L=float(ls.sum());tau=L*u_end
    return [float(l/L*(-math.expm1(-tau))) for l in ls],math.exp(-tau)
