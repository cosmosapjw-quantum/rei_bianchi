"""HH-F1 producer reference. No physical adoption, integrator, or cosmology.

Intervals enclose the explicitly declared exact-decimal fit, not empirical model
error or the compiled libm result. Contexts are local and independent of callers.
Only decimal strings, integers and Decimal inputs are accepted, never floats.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import (Decimal as D, Context, DecimalException, ROUND_FLOOR,
                     ROUND_CEILING, ROUND_HALF_EVEN, Underflow, Subnormal)
import argparse
import json
import re
from pathlib import Path

class ProviderError(ValueError):
    """Invalid input, undefined operation, or unsupported reference use."""

PRECISION = 80
SPECS = {'GRACKLE_3_4_1_K57': ('1.2e-17','1.2','157800'),
         'GLOVER2015_KS91_EQ14': ('4.65e-21','1.5','157800')}
ALIASES = {'LCS91':'GRACKLE_3_4_1_K57',
           'KS92_corrected_Glover15':'GLOVER2015_KS91_EQ14'}
NUMBER = re.compile(r'^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$')

def number(value):
    if isinstance(value,bool) or not isinstance(value,(str,int,D)):
        raise ProviderError('DECIMAL_STRING_OR_INTEGER_REQUIRED')
    s=str(value)
    if len(s)>256 or not NUMBER.fullmatch(s):
        raise ProviderError('INVALID_OR_OVERSIZED_NUMBER')
    x=D(s)
    if not x.is_finite() or abs(x.adjusted())>1000:
        raise ProviderError('NUMERIC_REPRESENTATION_RANGE_NOT_PHYSICAL_DOMAIN')
    return x

def context(rounding=ROUND_HALF_EVEN):
    c=Context(prec=PRECISION, rounding=rounding, Emin=-999999,Emax=999999)
    c.traps[Underflow]=True
    c.traps[Subnormal]=True
    return c

@dataclass(frozen=True)
class I:
    lo:D
    hi:D
    def __post_init__(self):
        if not self.lo.is_finite() or not self.hi.is_finite() or self.lo>self.hi:
            raise ProviderError('INVALID_INTERVAL')
    @classmethod
    def point(cls,x):
        v=number(x); return cls(v,v)
    def __add__(self,y):
        y=as_i(y)
        return I(context(ROUND_FLOOR).add(self.lo,y.lo),
                 context(ROUND_CEILING).add(self.hi,y.hi))
    def __neg__(self):
        return I(self.hi.copy_negate(), self.lo.copy_negate())
    def __sub__(self,y):return self+-as_i(y)
    def __mul__(self,y):
        y=as_i(y); corners=[(a,b) for a in (self.lo,self.hi) for b in (y.lo,y.hi)]
        return I(min(context(ROUND_FLOOR).multiply(a,b) for a,b in corners),
                 max(context(ROUND_CEILING).multiply(a,b) for a,b in corners))
    def __truediv__(self,y):
        y=as_i(y)
        if y.lo<=0<=y.hi:raise ProviderError('DIVISION_INTERVAL_CONTAINS_ZERO')
        inv=I(context(ROUND_FLOOR).divide(D(1),y.hi),
              context(ROUND_CEILING).divide(D(1),y.lo))
        return self*inv
    def ln(self):
        if self.lo<=0:raise ProviderError('LOG_DOMAIN')
        c=context()
        return I(c.next_minus(c.ln(self.lo)),c.next_plus(c.ln(self.hi)))
    def exp(self):
        # Explicit computational cap only; do not silently underflow to zero.
        if self.lo<D('-100000') or self.hi>D('100000'):
            raise ProviderError('NUMERIC_EXP_RANGE_UNAVAILABLE')
        c=context()
        return I(c.next_minus(c.exp(self.lo)),c.next_plus(c.exp(self.hi)))
    def json(self):return [str(self.lo),str(self.hi)]

def as_i(x):return x if isinstance(x,I) else I.point(x)

def canonical(provider):
    if not isinstance(provider,str):raise ProviderError('UNKNOWN_PROVIDER')
    v=ALIASES.get(provider,provider)
    if v not in SPECS:raise ProviderError('UNKNOWN_PROVIDER')
    return v

def analytic(provider,lower,upper):
    """Positive analytic extension; caller controls branch ownership."""
    a,p,b=(I.point(s) for s in SPECS[canonical(provider)])
    def at(t):return a*((p*I.point(t).ln())-b/I.point(t)).exp()
    # k is increasing for p>0,B>0. Use endpoints instead of a wide natural form.
    kr=I(at(lower).lo,at(upper).hi)
    inv=I.point(1)/I(lower,upper); inv2=inv*inv; inv3=inv2*inv; inv4=inv2*inv2
    first=p*inv+b*inv2
    # Algebraically positive form avoids needless cancellation for p>1.
    second=p*(p-1)*inv2+I.point(2)*b*(p-1)*inv3+b*b*inv4
    return kr,kr*first,kr*second

def evaluate_reference(provider,lower_T_K,upper_T_K=None):
    """Piecewise numeric fit enclosure only. Every response admission is false."""
    ident=canonical(provider)
    lo=number(lower_T_K); hi=lo if upper_T_K is None else number(upper_T_K)
    if lo<=0 or hi<lo:raise ProviderError('POSITIVE_ORDERED_TEMPERATURE_REQUIRED')
    cut=D(3000); crossing=ident=='GRACKLE_3_4_1_K57' and lo<=cut<=hi
    pieces=[]
    if ident=='GRACKLE_3_4_1_K57' and lo<=cut:
        pieces.append({'branch':'ARTIFICIAL_FLOOR', 'temperature_K':[str(lo),str(min(hi,cut))],
                       'left_closed':True,'right_closed':True,
                       'rate_cm3_s':['1E-20','1E-20'],
                       'd1_cm3_s_K':None if crossing else ['0','0'],
                       'd2_cm3_s_K2':None if crossing else ['0','0'],
                       'open_interior_derivatives':['0','0']})
    if ident!='GRACKLE_3_4_1_K57' or hi>cut:
        low=max(lo,cut) if ident=='GRACKLE_3_4_1_K57' else lo
        try:k,d1,d2=analytic(ident,low,hi)
        except DecimalException as e:raise ProviderError('NUMERIC_ENCLOSURE_UNAVAILABLE:'+type(e).__name__) from e
        pieces.append({'branch':'ANALYTIC','temperature_K':[str(low),str(hi)],
                       'left_closed':not(ident=='GRACKLE_3_4_1_K57' and low==cut),
                       'right_closed':True,'rate_cm3_s':k.json(),
                       'd1_cm3_s_K':d1.json(),'d2_cm3_s_K2':d2.json()})
    hull=I(min(D(q['rate_cm3_s'][0]) for q in pieces),max(D(q['rate_cm3_s'][1]) for q in pieces))
    return {'schema':'wu088.hh_fit_reference.v1','canonical_provider':ident,
            'requested_provider':provider,'input_T_K':[str(lo),str(hi)],
            'rate_cm3_s':hull.json(),'rate_m3_s':(hull*'1e-6').json(),
            'pieces':pieces,'boundary_status':'NONSMOOTH_3000K' if crossing else 'SMOOTH_ANALYTIC' if pieces[0]['branch']=='ANALYTIC' else 'FLOOR_INTERIOR',
            'derivatives_global':None if crossing else {'d1':pieces[0]['d1_cm3_s_K'],'d2':pieces[0]['d2_cm3_s_K2']},
            'numerical_error_kind':'OUTWARD_ENCLOSURE_OF_EXACT_DECIMAL_FIT_ONLY',
            'physical_uncertainty_kind':'UNQUANTIFIED_EMPIRICAL_MODEL_ERROR',
            'distribution_assumptions':'SCALAR_COMMON_T_ISOTROPIC_MAXWELL_REFERENCE',
            'domain':{'physical_consumer_domain':None,'computational_input_only':True},
            'extrapolation_status':'PHYSICAL_SUPPORT_NOT_ADMITTED',
            'admission':False,'decimal_precision':PRECISION}

def rate_source(rate,density_m3,chi_J):
    """Local reference source. Chi comes from caller; no cosmology/constants chosen."""
    if not isinstance(rate,dict):raise ProviderError('RATE_RESPONSE_REQUIRED')
    expected=evaluate_reference(rate.get('requested_provider'),*rate.get('input_T_K',[]))
    if rate!=expected:raise ProviderError('RATE_RESPONSE_MODIFIED')
    n=number(density_m3); chi=number(chi_J)
    if n<0 or chi<=0:raise ProviderError('NONNEGATIVE_DENSITY_AND_POSITIVE_CHI_REQUIRED')
    k=I(*(D(v) for v in rate['rate_m3_s']))
    event=k*I.point(n)*I.point(n)  # Grackle network convention: no extra 1/2.
    q=event*I.point(chi)
    return {'species_order':['HI','HII','Hminus','e_free'],
            'stoichiometry':[-1,1,0,1],'electron_delta_per_event':1,
            'pair_convention':'GRACKLE_NETWORK_R_EQUALS_K_NHI_SQUARED',
            'event_rate_m3_s':event.json(),
            'species_sources_m3_s':[(-event).json(),event.json(),['0','0'],event.json()],
            'thermal_J_m3_s':(-q).json(),'binding_J_m3_s':q.json(),
            'energy_sum_J_m3_s':['0','0'],
            'conservation_basis':'CONTRACT_COEFFICIENTS_CONTRACTED_BEFORE_INTERVAL_SUM',
            'chi_J':str(chi),'density_m3':str(n),'admission':False}

CONSUMER_FIELDS=('temperature_K','density_m3','redshift','source_sed',
                 'distribution','observable_budget','constants_registry',
                 'consumer_commit','consumer_adapter_path','domain_receipt',
                 'process_owner','threshold_owner','thermal_energy_owner',
                 'binding_energy_owner','numerical_tolerance')
def application_gate(contract):
    """Missing-field inventory, NOT verification of receipt or physical authority."""
    if not isinstance(contract,dict):raise ProviderError('CONTRACT_OBJECT_REQUIRED')
    def empty(x):
        return x is None or x=='' or x=={} or x==[] or (isinstance(x,dict) and any(empty(v) for v in x.values()))
    missing=[k for k in CONSUMER_FIELDS if k not in contract or empty(contract[k])]
    return {'ready_for_consumer_review':not missing,'physical_admission':False,
            'status':'WAITING_ON_REI_DOMAIN' if missing else 'FIELDS_PRESENT_NOT_AUTHORITY_VERIFIED',
            'missing':missing,'canonical_dependency':'REI-F07',
            'authority_verification_performed':False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--provider',required=True);p.add_argument('--lower',required=True)
    p.add_argument('--upper');p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    try:
        result=evaluate_reference(a.provider,a.lower,a.upper)
        # Exclusive creation: a diagnostic never overwrites accepted evidence.
        with a.out.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    except (ProviderError,OSError) as e:p.exit(2,str(e)+'\n')
if __name__=='__main__':main()
