"""HH-F1R: interval jets of declared fits, not a physical provider or ODE solver.

Coordinates are n=n_HI [m^-3] and y=ln(T/T_ref), T_ref fixed. Source convention
is R=k*n^2 (Grackle k57), with no further unordered-pair factor. Returned
intervals enclose exact-decimal model arithmetic only, not empirical errors.
"""
from __future__ import annotations
import argparse
import json
from decimal import Decimal as D, DecimalException
from fractions import Fraction
from pathlib import Path
from hh_external import I, SPECS, ProviderError, number, canonical, evaluate_reference


def _i(a):
    return I(*(D(x) for x in a))


def _exp(x):
    return I.point(1) if x.lo==0 and x.hi==0 else x.exp()


def _metadata():
    return {'admission':False, 'physical_domain':None,
            'numerical_error_kind':'OUTWARD_ENCLOSURE_OF_EXACT_DECIMAL_FIT_ONLY',
            'physical_uncertainty_kind':'UNQUANTIFIED_EMPIRICAL_MODEL_ERROR',
            'coordinates':['n_HI_m^-3','ln(T/T_ref), fixed T_ref'],
            'pair_convention':'GRACKLE_NETWORK_R_EQUALS_K_NHI_SQUARED',
            'rate_provider_origin':'REUSE_PINNED_F1_UNCHANGED',
            'consumer_dependency':'REI-F07'}


def log_jet(provider, lower_T_K, upper_T_K=None):
    """Enclose k and d^j k/dy^j, j=1..3, on each F1 branch.

    Boundary contact suppresses a global smooth jet, even at a single point.
    One-sided pieces remain available; they are not a Taylor certificate across
    the discontinuity. No change to the parent F1 rate evaluator is made.
    """
    result=evaluate_reference(provider,lower_T_K,upper_T_K)
    p=I.point(SPECS[result['canonical_provider']][1])
    b=I.point(SPECS[result['canonical_provider']][2])
    pieces=[]
    try:
        for piece in result['pieces']:
            k=_i(piece['rate_cm3_s'])
            if piece['branch']=='ARTIFICIAL_FLOOR':
                vals=[k,I.point(0),I.point(0),I.point(0)]
            else:
                x=b/I(*(D(t) for t in piece['temperature_K']))
                x2=x*x
                P1=p+x
                P2=p*p+(I.point(2)*p-1)*x+x2
                P3=p*p*p+(I.point(3)*p*p-I.point(3)*p+1)*x+(I.point(3)*p-3)*x2+x2*x
                vals=[k,k*P1,k*P2,k*P3]
            pieces.append({'branch':piece['branch'],
                           'temperature_K':piece['temperature_K'],
                           'left_closed':piece['left_closed'],
                           'right_closed':piece['right_closed'],
                           'dlogT_cm3_s':[v.json() for v in vals],
                           'dlogT_m3_s':[(v*'1e-6').json() for v in vals],
                           'derivative_scope':'OPEN_BRANCH_OR_ONE_SIDED_EXTENSION'})
    except DecimalException as e:
        raise ProviderError('JET_NUMERIC_ENCLOSURE_UNAVAILABLE:'+type(e).__name__) from e
    smooth=result['boundary_status']!='NONSMOOTH_3000K'
    return dict(_metadata(),schema='wu088.hh_logjet.v1',canonical_provider=result['canonical_provider'],
                input_T_K=result['input_T_K'],boundary_status=result['boundary_status'],
                pieces=pieces, global_dlogT_m3_s=pieces[0]['dlogT_m3_s'] if smooth else None,
                physical_source_support='NOT_ADMITTED')


def _smooth(provider,lo,hi=None):
    j=log_jet(provider,lo,hi)
    if j['global_dlogT_m3_s'] is None:
        raise ProviderError('NONSMOOTH_3000K_NO_GLOBAL_TAYLOR_JET')
    return j,[_i(x) for x in j['global_dlogT_m3_s']]


def _density_chi(n,chi):
    n=number(n); chi=number(chi)
    if n<0:
        raise ProviderError('NEGATIVE_DENSITY')
    if chi<=0:
        raise ProviderError('POSITIVE_CALLER_BOUND_CHI_REQUIRED')
    return n,chi


def source_jet(provider,T_K,n_HI_m3,chi_J):
    """Point-input value, gradient, Hessian and third tensor for R(n,y).

    A caller must bind chi to its own registry before physical adoption. No
    density logarithm or division by n is used, so n=0 is well defined.
    """
    n,chi=_density_chi(n_HI_m3,chi_J)
    j,K=_smooth(provider,T_K)
    N=I.point(n); n2=N*N
    R=n2*K[0]
    grad={'n':I.point(2)*N*K[0],'y':n2*K[1]}
    hess={'nn':I.point(2)*K[0],'ny':I.point(2)*N*K[1],'yy':n2*K[2]}
    third={'nnn':I.point(0),'nny':I.point(2)*K[1],
           'nyy':I.point(2)*N*K[2],'yyy':n2*K[3]}
    return dict(_metadata(),schema='wu088.hh_sourcejet.v1',canonical_provider=j['canonical_provider'],
                input_T_K=str(number(T_K)),input_n_HI_m3=str(n),chi_J=str(chi),
                boundary_status=j['boundary_status'],value=R.json(),
                gradient={k:v.json() for k,v in grad.items()},
                hessian={k:v.json() for k,v in hess.items()},
                third={k:v.json() for k,v in third.items()},
                units={'value':'m^-3 s^-1','n':'s^-1','y':'m^-3 s^-1',
                       'nn':'m^3 s^-1','ny':'s^-1','yy':'m^-3 s^-1',
                       'nny':'m^3 s^-1','nyy':'s^-1','yyy':'m^-3 s^-1'},
                species_order=['HI','HII','Hminus','e_free'],stoichiometry=[-1,1,0,1],
                derivative_source_coefficients={'species':['-1','1','0','1'],
                                                'thermal':str(chi.copy_negate()),'binding':str(chi)},
                invariant_contractions={'H_nuclei':0,'charge':0,'thermal_plus_binding':0})


def taylor_step(provider,T0_K,n0_m3,delta_y,delta_n_m3,chi_J):
    """Second-order source Taylor enclosure along a prescribed state segment.

    This is NOT a time step. n(s)=n0+s*dn, T(s)=T0*exp(s*dy), 0<=s<=1.
    Bounds are conditional on the path staying on one smooth fit branch. The
    function computes both a polynomial+remainder enclosure and a direct
    endpoint image; it does not intersect them or clip a negative lower bound.
    """
    n,chi=_density_chi(n0_m3,chi_J)
    t=number(T0_K); dy=number(delta_y); dn=number(delta_n_m3)
    if t<=0:
        raise ProviderError('POSITIVE_TEMPERATURE_REQUIRED')
    # Fraction validates the endpoint exactly, independently of Decimal context.
    if Fraction(n)+Fraction(dn)<0:
        raise ProviderError('NEGATIVE_DENSITY_ENDPOINT')
    N=I.point(n); X=I.point(dn); Y=I.point(dy); C=I.point(chi)
    try:
        nt=N+X
        nr=N+I(min(D(0),dn),max(D(0),dn))
        tr=I.point(t)*_exp(I(min(D(0),dy),max(D(0),dy)))
        jt,Kpath=_smooth(provider,tr.lo,tr.hi)
        center=source_jet(provider,t,n,chi)
        base=_i(center['value'])
        grad={k:_i(v) for k,v in center['gradient'].items()}
        hess={k:_i(v) for k,v in center['hessian'].items()}
        poly=(base+grad['n']*X+grad['y']*Y+
              hess['nn']*X*X/2+hess['ny']*X*Y+hess['yy']*Y*Y/2)
        ax=I.point(dn.copy_abs()); ay=I.point(dy.copy_abs()); nm=I.point(nr.hi)
        # Kj upper bounds are nonnegative for both supported p>1 families.
        Ksup=[I.point(max(v.lo.copy_abs(),v.hi.copy_abs())) for v in Kpath]
        bound=ax*ax*ay*Ksup[1]+nm*ax*ay*ay*Ksup[2]+nm*nm*ay*ay*ay*Ksup[3]/6
        eps=bound.hi
        whole=poly+I(eps.copy_negate(),eps)
        endpoint_t=I.point(t)*_exp(Y)
        direct_k=_i(evaluate_reference(provider,endpoint_t.lo,endpoint_t.hi)['rate_m3_s'])
        direct=nt*nt*direct_k
        energy_eps=(I.point(eps)*C).hi
        species=[-whole,whole,I.point(0),whole]
    except DecimalException as e:
        raise ProviderError('TAYLOR_NUMERIC_ENCLOSURE_UNAVAILABLE:'+type(e).__name__) from e
    return dict(_metadata(),schema='wu088.hh_source_taylor.v1',canonical_provider=canonical(provider),
                state_segment={'T0_K':str(t),'n0_m3':str(n),'delta_y':str(dy),
                               'delta_n_m3':str(dn),'chi_J':str(chi),'time_step':False},
                path_temperature_K=tr.json(),path_density_m3=nr.json(),
                boundary_status=jt['boundary_status'],log_derivative_sup_m3_s=[str(v.hi) for v in Ksup],
                taylor_polynomial_m3_s=poly.json(),event_remainder_abs_upper_m3_s=str(eps),
                endpoint_enclosure_m3_s=whole.json(),direct_endpoint_image_m3_s=direct.json(),
                species_order=['HI','HII','Hminus','e_free'],
                species_endpoint_enclosures=[v.json() for v in species],
                thermal_endpoint_J_m3_s=(-whole*C).json(),binding_endpoint_J_m3_s=(whole*C).json(),
                thermal_binding_remainder_abs_upper_J_m3_s=str(energy_eps),
                conservation_residuals={'H_nuclei':['0','0'],'charge':['0','0'],'thermal_plus_binding':['0','0']},
                residual_basis='CONTRACT_BEFORE_INTERVAL_SPLIT; not a sum of independent marginal intervals',
                assumptions=['fixed provider and constants','linear density/log-temperature state segment',
                             'nonnegative density along segment','one smooth fit branch',
                             'scalar common-temperature Maxwell model only'],
                claim_ceiling='FIT_SOURCE_TAYLOR_ONLY; NOT_FULL_REI_RESIDUAL_OR_ODE_ERROR')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider',required=True)
    parser.add_argument('--T',required=True)
    parser.add_argument('--n',required=True)
    parser.add_argument('--chi',required=True)
    parser.add_argument('--dy',required=True)
    parser.add_argument('--dn',required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    try:
        result=taylor_step(args.provider,args.T,args.n,args.dy,args.dn,args.chi)
        with args.out.open('x',encoding='utf-8') as file:
            json.dump(result,file,ensure_ascii=False,indent=2,allow_nan=False);file.write('\n')
    except (ProviderError,DecimalException,OSError) as exc:
        parser.exit(2,str(exc)+'\n')


if __name__=='__main__':main()
