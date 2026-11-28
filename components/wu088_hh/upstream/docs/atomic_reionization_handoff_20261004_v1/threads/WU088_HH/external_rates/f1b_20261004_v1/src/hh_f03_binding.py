"""HH-F1B: hypothetical atomic source in the actual F03 seven coordinates.

This module does not call or modify rei_bianchi, integrate a history, authorize
an empirical fit, or change the F03 fixture whose HH process is disabled.
Inputs are exact decimal points. Output intervals enclose the declared fit and
algebra only, NOT state-box, empirical-model, libm, or integration errors.
"""
from __future__ import annotations
from fractions import Fraction as F
from decimal import Decimal as D, DecimalException, ROUND_FLOOR, ROUND_CEILING
import argparse
import json
from pathlib import Path
from hh_external import I, number, canonical, SPECS, analytic, context, ProviderError

COORDINATES=['x_HII','x_HeII','x_HeIII','u_erg_cm3','N0_proper_cm3','N1_proper_cm3','N2_proper_cm3']
MODEL_KEYS={'n_h_cm3','n_he_cm3','kb_erg_k','chi_erg'}
ZERO=I(D(0),D(0))

def rat(x):
    """Public values retain the inherited exact-decimal input contract."""
    return F(number(x))

def interval(q:F)->I:
    """Outward conversion of an internal exact rational, including zero."""
    if q==0:return ZERO
    return I(context(ROUND_FLOOR).divide(D(q.numerator),D(q.denominator)),
             context(ROUND_CEILING).divide(D(q.numerator),D(q.denominator)))

def scale(k:I,q:F)->I:
    return ZERO if q==0 else k*interval(q)

def inputs(model,state):
    if not isinstance(model,dict) or set(model)!=MODEL_KEYS:
        raise ProviderError('EXACT_MODEL_FIELDS_REQUIRED')
    if not isinstance(state,(list,tuple)) or len(state)!=7:
        raise ProviderError('F03_SEVEN_COORDINATES_REQUIRED')
    nH,nHe,kb,chi=[rat(model[k]) for k in ('n_h_cm3','n_he_cm3','kb_erg_k','chi_erg')]
    v=list(map(rat,state));h,he1,he2,u=v[:4]
    if nH<0 or nHe<0 or nH+nHe<=0 or kb<=0 or chi<=0:
        raise ProviderError('MODEL_POSITIVITY')
    if not 0<=h<=1 or he1<0 or he2<0 or he1+he2>1 or u<=0 or min(v[4:])<0:
        raise ProviderError('POINT_OUTSIDE_SOURCE_DOMAIN_OR_ZERO_TEMPERATURE')
    P=nH*(1+h)+nHe*(1+he1+2*he2)
    T=2*u/(3*kb*P)
    return nH,nHe,kb,chi,v,P,T

def _evaluate(model,state,provider):
    nH,nHe,kb,chi,v,P,T=inputs(model,state)
    ident=canonical(provider);h,he1,he2,u=v[:4];w=1-h
    temperature=interval(T)
    floor=ident=='GRACKLE_3_4_1_K57' and T<=3000
    boundary=ident=='GRACKLE_3_4_1_K57' and T==3000
    if floor:
        rate=I.point('1e-20');rho=F(0);P2=F(0)
    else:
        rate=analytic(ident,temperature.lo,temperature.hi)[0]
        p=F(SPECS[ident][1]);x=F(SPECS[ident][2])/T
        rho=p+x;P2=rho*rho-x
    # HH event convention: R=k*n_HI^2; no extra half, no division by nH.
    q_shape=nH*w*w
    c=[F(1),F(0),F(0),-chi*nH,F(0),F(0),F(0)]
    out={
        'schema':'wu088.hh_f03_atomic_reference.v1',
        'coordinates':COORDINATES,'canonical_provider':ident,
        'temperature_exact_K':str(T),'temperature_enclosure_K':temperature.json(),
        'branch':'NONSMOOTH_3000K' if boundary else 'ARTIFICIAL_FLOOR_INTERIOR' if floor else 'ANALYTIC',
        'rate_cm3_s':rate.json(),'source_per_H_s':scale(rate,q_shape).json(),
        'event_rate_cm3_s':scale(rate,nH*q_shape).json(),
        'rhs':[scale(rate,ci*q_shape).json() for ci in c],
        'rhs_factor_exact':[str(ci) for ci in c],
        'energy_null_coefficient':str(chi*nH*c[0]+c[3]),
        'extra_free_electron_rate_cm3_s':scale(rate,nH*q_shape).json(),
        'HH_photon_rate_cm3_s':['0','0'],'HH_escape_energy_rate':['0','0'],
        'process_id':'HI_HI_TO_HI_HII_E','pair_convention':'GRACKLE_NETWORK_NO_EXTRA_HALF',
        'consumer_admission':False,'empirical_error_bounded':False,
        'consumer_invoked':False,'state_box_enclosed':False,
        'claim':'EXACT_DECIMAL_POINT_FIT_ALGEBRA_ONLY_NOT_CONSUMER_REGRESSION',
        'scalar_gradient':None,'scalar_hessian':None,'HH_only_eigenvalue_per_s':None,
        'gradient_shape_exact':None,'hessian_shape_exact':None,
        'HH_only_eigenvalue_shape_exact':None,
    }
    if boundary:return out
    Pgrad=[nH,nHe,2*nHe,F(0),F(0),F(0),F(0)]
    a=[(F(1)/u if i==3 else F(0))-Pgrad[i]/P for i in range(7)]
    b=[[(Pgrad[i]*Pgrad[j]/(P*P))-(F(1)/(u*u) if i==j==3 else F(0))
         for j in range(7)] for i in range(7)]
    g=[nH*(-2*w*(i==0)+w*w*rho*a[i]) for i in range(7)]
    H=[[nH*(2*(i==0)*(j==0)-2*w*rho*((i==0)*a[j]+(j==0)*a[i])
             +w*w*(P2*a[i]*a[j]+rho*b[i][j])) for j in range(7)] for i in range(7)]
    lam=sum((g[i]*c[i] for i in range(7)),F(0))
    if lam>0:raise ProviderError('INTERNAL_HH_DISSIPATIVITY_INVARIANT')
    out.update(scalar_gradient=[scale(rate,x).json() for x in g],
        scalar_hessian=[[scale(rate,x).json() for x in row] for row in H],
        gradient_shape_exact=list(map(str,g)),hessian_shape_exact=[list(map(str,row)) for row in H],
        HH_only_eigenvalue_per_s=scale(rate,lam).json(),HH_only_eigenvalue_shape_exact=str(lam))
    return out

def evaluate(model,state,provider):
    try:return _evaluate(model,state,provider)
    except (DecimalException,OverflowError) as exc:
        raise ProviderError('NUMERIC_ENCLOSURE_UNAVAILABLE:'+type(exc).__name__) from exc

def direction(model,state,provider,delta_y,dt_s='0'):
    """Point JVP/Hessian-direction contraction and HH-only BE correction.

    These are additive terms, not the complete baseline residual/Jacobian.
    dt is not used to advance state, commit events, or authorize an ODE solve.
    """
    if not isinstance(delta_y,(list,tuple)) or len(delta_y)!=7:
        raise ProviderError('SEVEN_DIRECTION_COMPONENTS_REQUIRED')
    v=list(map(rat,delta_y));dt=rat(dt_s)
    if dt<0:raise ProviderError('NEGATIVE_DT')
    out=evaluate(model,state,provider)
    if out['scalar_gradient'] is None:raise ProviderError('NO_SMOOTH_JET_AT_3000K')
    g=list(map(F,out['gradient_shape_exact']));H=[list(map(F,row)) for row in out['hessian_shape_exact']]
    c=list(map(F,out['rhs_factor_exact']));k=I(*(D(x) for x in out['rate_cm3_s']))
    d1=sum((g[i]*v[i] for i in range(7)),F(0))
    d2=sum((H[i][j]*v[i]*v[j] for i in range(7) for j in range(7)),F(0))
    q=I(*(D(x) for x in out['source_per_H_s']))
    lam=F(out['HH_only_eigenvalue_shape_exact'])
    return {'schema':'wu088.hh_f03_point_direction.v1','Jv':[scale(k,ci*d1).json() for ci in c],
        'D2f_vv':[scale(k,ci*d2).json() for ci in c],
        'BE_residual_addition':[scale(q,-dt*ci).json() for ci in c],
        'BE_Jv_addition':[scale(k,-dt*ci*d1).json() for ci in c],
        'HH_only_BE_determinant':(I.point(1)-scale(k,dt*lam)).json(),
        'full_BE_invertibility_claim':False,'consumer_admission':False,
        'direction_units':'same as state coordinates; direction need not be a finite admissible step'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    try:
        data=json.loads(args.input.read_text())
        result=evaluate(data['model'],data['state'],data['provider'])
        if 'direction' in data:
            result['direction']=direction(data['model'],data['state'],data['provider'],data['direction'],data.get('dt_s','0'))
        with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    except (ProviderError,KeyError,ValueError,OSError) as exc:p.exit(2,str(exc)+'\n')
if __name__=='__main__':main()
