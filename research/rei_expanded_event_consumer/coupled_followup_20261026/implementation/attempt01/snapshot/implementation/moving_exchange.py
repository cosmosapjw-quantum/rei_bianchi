"""Signed moving-cell exchange and an explicit tagged energy coordinate.

Moment balance supplies no thermalization or time-step positivity claim.
Source packets, full stopping and spatial expansion work remain other owners.
"""
import math


def finite(value,name):
    try:value=float(value)
    except (TypeError,ValueError,OverflowError) as exc:raise ValueError('NONFINITE_'+name) from exc
    if not math.isfinite(value):raise ValueError('NONFINITE_'+name)
    return value


def finite_volume_exchange(centres,counts,centre_velocities,edge_fluxes,cutoff):
    e=tuple(finite(v,'CENTRE') for v in centres);n=tuple(finite(v,'COUNT') for v in counts)
    edot=tuple(finite(v,'CENTRE_VELOCITY') for v in centre_velocities)
    F=tuple(finite(v,'RELATIVE_EDGE_FLUX') for v in edge_fluxes);c=finite(cutoff,'CUTOFF')
    m=len(e)
    if not m or len(n)!=m or len(edot)!=m or len(F)!=m+1:raise ValueError('CELL_EDGE_DIMENSIONS')
    if c<=0 or e[0]<=c or any(a>=b for a,b in zip(e,e[1:])) or any(v<0 for v in n):raise ValueError('ORDERED_POSITIVE_ENERGY_AND_COUNTS_REQUIRED')
    if F[-1]!=0:raise ValueError('NONZERO_UPPER_BOUNDARY_NOT_SUPPORTED')
    ndot=tuple(F[i]-F[i+1] for i in range(m));Phi=-F[0]
    mesh_work=sum(v*x for v,x in zip(edot,n))
    Udot=sum(v*x for v,x in zip(e,ndot))+mesh_work
    Ih=(c-e[0])*Phi+sum((e[i]-e[i-1])*F[i] for i in range(1,m))+mesh_work
    bathU=c*Phi-Ih
    if not all(math.isfinite(v) for v in ndot+(Phi,mesh_work,Udot,Ih,bathU)):raise ValueError('NONFINITE_EXCHANGE_OUTPUT')
    return {'count_rhs':ndot,'Phi':Phi,'resolved_Udot':Udot,'same_current_moment':Ih,
      'mesh_work':mesh_work,'reservoir_Ndot':Phi,'reservoir_Udot':bathU,
      'thermal_heat':None,'irreversible_assimilation':False,'time_step_positivity_proven':False}


def electron_thermal_cutoff(theta,kappa,Nthermal,Nedge,jedge,I,*,I_theta_dot=0.):
    theta=finite(theta,'THETA');kappa=finite(kappa,'KAPPA');Nt=finite(Nthermal,'THERMAL_COUNT')
    Ne=finite(Nedge,'EDGE_DENSITY');j=finite(jedge,'EDGE_CURRENT');I0=finite(I,'MOMENT_INTERCEPT');L=finite(I_theta_dot,'MOMENT_THETA_DOT_COEFFICIENT')
    if theta<=0 or kappa<=0 or Nt<=0 or Ne<0:raise ValueError('THERMAL_CLOSURE_INPUT_DOMAIN')
    c=kappa*theta;h=1.5*theta;C=1.5*Nt;Ceff=C-kappa*(c-h)*Ne+L
    if not math.isfinite(Ceff) or Ceff<=0:raise ValueError('NONPOSITIVE_EFFECTIVE_CAPACITY')
    theta_dot=(-(c-h)*j-I0)/Ceff;cutoff_dot=kappa*theta_dot
    Phi=cutoff_dot*Ne-j;actual_I=I0+L*theta_dot;bathU=c*Phi-actual_I
    factor=C/Ceff
    if not all(math.isfinite(v) for v in (c,h,C,theta_dot,cutoff_dot,Phi,actual_I,bathU,factor)):raise ValueError('NONFINITE_THERMAL_CLOSURE_OUTPUT')
    return {'cutoff':c,'mean_thermal_energy':h,'C':C,'Ceff':Ceff,'theta_dot':theta_dot,
      'cutoff_dot':cutoff_dot,'Phi':Phi,'same_current_moment':actual_I,
      'reservoir_Ndot':Phi,'reservoir_Udot':bathU,'conditioning_C_over_Ceff':factor,
      'thermal_heat':None,'closure':'conditional_pure_electron_Maxwell','actual_endpoint_activation':False}


def tag_native_bed_pair(E,W,*,input_kind):
    if input_kind!='NATIVE_BED_KINETIC_eV':raise ValueError('EXPLICIT_NATIVE_KINETIC_SEMANTICS_REQUIRED')
    E=finite(E,'NATIVE_INCIDENT_ENERGY');W=finite(W,'NATIVE_EJECTED_ENERGY')
    Bnative=13.6057;delta=.0057;Btag=13.6
    if not Bnative<E<=150 or W<0 or 2*W+Bnative>E:raise ValueError('NATIVE_BED_PAIR_OUTSIDE_DOMAIN')
    tagged=(W+delta,E-Bnative-W+delta)
    return {'xi_input':E+delta,'xi_outputs':tagged,'ledger_binding':Btag,
      'coordinate_kind':'CHARGE_GAUGE_TAGGED_ENERGY_eV','delta':delta,
      'true_kinetic_input':E,'true_kinetic_outputs':tuple(v-delta for v in tagged),
      'old_source_activation':False,'physical_source_remap_admitted':False,'thermal_heat':None}
