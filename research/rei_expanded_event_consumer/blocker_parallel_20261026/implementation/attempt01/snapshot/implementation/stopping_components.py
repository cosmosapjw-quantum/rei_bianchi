"""Declared warm EE coefficients and native hydrogen BED energy sharing.

No integration, source-atom scan, heating value or old-network activation.
The Maxwell bath, prescribed Coulomb logarithm and native binding energy
remain explicit model choices.
"""
import math

KB=1.380649e-23; EV_J=1.602176634e-19; E_CHARGE=1.602176634e-19; ELECTRON_MASS=9.1093837139e-31
EPSILON0=8.8541878188e-12; B_NATIVE=13.6057


def _finite(value,name,*,positive=False):
    try:value=float(value)
    except (TypeError,ValueError,OverflowError) as exc:raise ValueError('INVALID_'+name) from exc
    if not math.isfinite(value) or (value<=0 if positive else value<0):raise ValueError('INVALID_'+name)
    return value


def ee_coefficients(E_eV,T_K,n_e_m3,lnLambda):
    E=_finite(E_eV,'EE_ENERGY',positive=True);T=_finite(T_K,'TEMPERATURE',positive=True)
    ne=_finite(n_e_m3,'THERMAL_DENSITY');log=_finite(lnLambda,'COULOMB_LOG',positive=True)
    if not .011<=E<=150.:raise ValueError('EE_QUERY_ENERGY_OUTSIDE_DECLARED_DOMAIN')
    theta=KB*T/EV_J;x=E/theta;root=math.sqrt(x)
    Gamma=4*math.pi*ne*(E_CHARGE**2/(4*math.pi*EPSILON0))**2*log/ELECTRON_MASS**2
    b0=ELECTRON_MASS*Gamma/(EV_J*math.sqrt(2*EV_J*E/ELECTRON_MASS))
    gaussian=2*root*math.exp(-x)/math.sqrt(math.pi)
    F=math.erf(root)-gaussian
    D=theta*b0*F;A=b0*(gaussian-F)
    if not all(math.isfinite(v) for v in (theta,A,D,b0)) or D<0:
        raise ValueError('INVALID_EE_DERIVED_COEFFICIENT')
    return {'A_eV_s':A,'D_eV2_s':D,'b0_eV_s':b0,'theta_eV':theta,
            'variance_rate_eV2_s':2*D,'bath_energy_rule':'minus_same_kinetic_moment',
            'thermal_heat':None,'conditional_Maxwell_bath':True}


def ee_flux(E_eV,T_K,n_e_m3,lnLambda,N,Nprime):
    coefficients=ee_coefficients(E_eV,T_K,n_e_m3,lnLambda)
    if not math.isfinite(N) or not math.isfinite(Nprime):raise ValueError('NONFINITE_DISTRIBUTION')
    return -coefficients['D_eV2_s']*(Nprime+(1/coefficients['theta_eV']-1/(2*E_eV))*N)


def bed_total_support(E_eV):
    E=_finite(E_eV,'INCIDENT_ENERGY')
    if E>150.:raise ValueError('BED_INCIDENT_OUTSIDE_DECLARED_DOMAIN')
    return {'zero_total_channel':E<=B_NATIVE,'W_interval_eV':(0.,max(0.,(E-B_NATIVE)/2))}


def _bed_domain(E_eV,W_eV):
    E=_finite(E_eV,'INCIDENT_ENERGY');W=_finite(W_eV,'EJECTED_ENERGY')
    if not B_NATIVE<=E<=150. or 2*W+B_NATIVE>E:
        raise ValueError('BED_DIFFERENTIAL_QUERY_OUTSIDE_DECLARED_DOMAIN')
    return E,W


def bed_sdcs_m2_per_eV(E_eV,W_eV):
    E,W=_bed_domain(E_eV,W_eV)
    t=E/B_NATIVE;w=W/B_NATIVE;y=1/(1+w);a=1+w;b=t-w
    S=4*math.pi*.52918**2
    polynomial=-.0224728*y**2+1.177455*y**3-.4626461*y**4+.08906479*y**5
    kernel=.955*S/(B_NATIVE*(t+2))*((2-.4343)*(a*a+b*b-a*b)/(a*a*b*b)+math.log(t)*polynomial/a)
    if not math.isfinite(kernel) or kernel<0:raise ValueError('INVALID_BED_DERIVED_KERNEL')
    return kernel*1e-20


def paired_event(E_eV,W_eV,*,ledger_binding_eV=B_NATIVE,pair_factor=1):
    E,W=_bed_domain(E_eV,W_eV)
    if ledger_binding_eV!=B_NATIVE:raise ValueError('NATIVE_BINDING_CONVENTION_MISMATCH')
    if pair_factor!=1:raise ValueError('PAIRED_EVENT_ALREADY_COUNTS_BOTH_ELECTRONS')
    if E==B_NATIVE:raise ValueError('ZERO_WIDTH_THRESHOLD_HAS_NO_FINITE_EVENT')
    return {'output_energies_eV':(W,E-B_NATIVE-W),'number_delta':1,'HI_delta':-1,
      'HII_delta':1,'fast_electron_charge_delta':-1,'binding_gain_eV':B_NATIVE,
      'kinetic_loss_eV':B_NATIVE,'thermal_heat':None,'extra_factor_2':False,
      'old_network_activation':False}
