"""Conditional incoming-energy moments of the two exact HH fit models.

No inverse experimental reconstruction, physical cross-section provider, heat
partition, cosmological domain or admission is supplied. Exact rational outputs
use Kelvin-normalized temperature; raw-fit monotonicity witnesses reuse the
unchanged directed-Decimal F1 reference.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
from typing import Any
from hh_external import I, D, SPECS, ProviderError, canonical, number, evaluate_reference

class MomentError(ValueError):
    """Unsupported model interpretation or input; never replace by a zero rate."""

def rational(x:F) -> dict[str,str]:
    return {'numerator':str(x.numerator),'denominator':str(x.denominator)}

def _parameters(provider:str, temperature_K:Any):
    try:
        ident=canonical(provider)
        t=number(temperature_K)
    except ProviderError as exc:
        raise MomentError(str(exc)) from exc
    if t<=0:
        raise MomentError('POSITIVE_TEMPERATURE_REQUIRED')
    _,p,b=SPECS[ident]
    return ident,F(t),F(p),F(b)

def analytic_moments(provider:str, temperature_K:Any, *, quantity:str='incoming') -> dict:
    """Conditional collision-weighted moments, not energy deposited in the gas.

For exact analytic k=A*t^p*exp(-B/t), a=p+3/2 and the constructed kernel gives
(E-E0)/(kB*T) ~ Gamma(a,1). This does not give outgoing-electron distributions.
For the raw LCS floor branch, this analytic construction is explicitly refused.
"""
    if quantity!='incoming':
        raise MomentError('OUTGOING_PARTITION_OR_HEAT_NOT_DETERMINED')
    ident,t,p,b=_parameters(provider,temperature_K)
    if ident=='GRACKLE_3_4_1_K57' and t<=3000:
        raise MomentError('RAW_FLOOR_NOT_ANALYTIC_KERNEL')
    a=p+F(3,2)
    return {
        'schema':'wu088.hh_analytic_incoming_moment.v1',
        'provider':ident,'input_T_K':rational(t),'exponent_p':rational(p),
        'gamma_shape':rational(a),'activation_energy_over_kB_K':rational(b),
        'mean_energy_over_kB_K':rational(b+a*t),
        'mean_excess_energy_over_kB_K':rational(a*t),
        'mean_energy_over_kBT':rational(b/t+a),
        'variance_energy_over_kB2_K2':rational(a*t*t),
        'variance_energy_over_kBT2':rational(a),
        'kinetic_kernel_model':'EXACT_ANALYTIC_FIT_CONTINUATION_ONLY',
        'branch':'ANALYTIC_NOT_RAW_FLOOR',
        'assumptions':['nonrelativistic zero-drift isotropic Maxwell relative velocities',
                       'fixed temperature-independent nonnegative effective cross section',
                       'fixed initial and final state set',
                       'exact mathematical fit, not empirical error enclosure'],
        'pair_convention':'NETWORK_R_EQUALS_K_NHI_SQUARED; unordered event sigma would be twice effective sigma',
        'outgoing_electron_spectrum':None,'thermal_loss_per_event_J':None,
        'unavailable_reason':'INCOMING_MOMENTS_DO_NOT_FIX_OUTGOING_PARTITION_OR_COMMON_BATH_CLOSURE',
        'physical_domain':None,'cross_section_reconstructed_from_data':False,
        'admission':False,'production_admission':False,
        'evidence_kind':'DERIVED_EXACT_RATIONAL_FOR_DECLARED_FIT'
    }

def raw_monotonicity_witness(lower_T_K:Any='3000',upper_T_K:Any='3001') -> dict:
    """Check k(T)*T^(3/2) monotonicity across the unchanged raw LCS cutoff.

A strict descending pair rules out one nonnegative fixed Maxwell kernel over
that interval. Lack of a violation at other pairs is NOT an existence proof.
"""
    try:
        lo=number(lower_T_K);hi=number(upper_T_K)
        if not(0<lo<=D(3000)<hi):
            raise MomentError('ORDERED_CUTOFF_STRADDLING_PAIR_REQUIRED')
        out=[]
        for t in (lo,hi):
            result=evaluate_reference('GRACKLE_3_4_1_K57',t)
            k=I(*(D(v) for v in result['rate_cm3_s']))
            # t is T/(1 K); this dimensionless weighting preserves the ordering.
            scaled=k*(I.point('1.5')*I.point(t).ln()).exp()
            out.append({'input_T_K':str(t),'raw_rate_cm3_s':k.json(),
                        'weighted_rate_cm3_s':scaled.json(),
                        'branch_status':result['boundary_status']})
        left=I(*(D(v) for v in out[0]['weighted_rate_cm3_s']))
        right=I(*(D(v) for v in out[1]['weighted_rate_cm3_s']))
        ratio=left/right
    except ProviderError as exc:
        raise MomentError(str(exc)) from exc
    return {
        'schema':'wu088.hh_raw_maxwell_monotonicity_witness.v1',
        'provider':'GRACKLE_3_4_1_K57','weight':'(T / 1 K)^(3/2)',
        'values':out,'left_over_right':ratio.json(),
        'violates_nonnegative_fixed_kernel_necessary_condition':right.hi<left.lo,
        'condition':'T2>T1 implies T2^(3/2)*k(T2)>=T1^(3/2)*k(T1)',
        'claim':'If strict violation, the exact raw function has no single nonnegative temperature-independent Maxwell kernel on an interval covering the pair.',
        'nonviolation_is_kernel_admission':False,
        'original_floor_modified':False,'empirical_fit_error_included':False,
        'whole_Grackle_solver_error_claim':False,'admission':False
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['moments','cutoff-witness'],required=True)
    parser.add_argument('--provider',default='LCS91')
    parser.add_argument('--T')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    try:
        if args.mode=='moments':
            if args.T is None:raise MomentError('TEMPERATURE_REQUIRED')
            result=analytic_moments(args.provider,args.T)
        else:
            result=raw_monotonicity_witness()
        with args.out.open('x',encoding='utf-8') as f:
            json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    except (MomentError,OSError) as exc:
        parser.exit(2,str(exc)+'\n')

if __name__=='__main__':main()
