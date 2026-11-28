"""Paired source differences for a shared exact-decimal HH fit; no history/admission.

The stable formula preserves the correlation of the two evaluations. The two
states are exact decimal inputs, not uncertainty boxes. Empirical fit uncertainty
is not included. Units: T in K, n in m^-3, chi in J.
"""
from __future__ import annotations
from fractions import Fraction as F
from decimal import Decimal as D, DecimalException, ROUND_FLOOR, ROUND_CEILING
import argparse
import json
from pathlib import Path
from hh_external import I, ProviderError, number, context, canonical, SPECS, analytic

LOG_TERMS = 80
EXPM1_TERMS = 64
ZERO = I.point(0)
ONE = I.point(1)
CUT = D(3000)
FLOOR = I.point('1e-20')


def rational(x: F) -> I:
    """Enclose one exact rational without rounding its integer operands."""
    a, b = D(x.numerator), D(x.denominator)
    return I(context(ROUND_FLOOR).divide(a, b),
             context(ROUND_CEILING).divide(a, b))


def _abs_upper(x: I) -> D:
    return max(x.lo.copy_abs(), x.hi.copy_abs())


def _power(x: I, n: int) -> I:
    # Only small fixed nonnegative powers are used internally.
    out = ONE
    for _ in range(n):
        out = out*x
    return out


def log_ratio(T_a, T_b) -> I:
    """Enclose ln(T_b/T_a), including differences below the work precision."""
    a, b = number(T_a), number(T_b)
    if a <= 0 or b <= 0:
        raise ProviderError('POSITIVE_TEMPERATURE_REQUIRED')
    if a == b:
        return ZERO
    q = (F(b)-F(a))/(F(b)+F(a))
    if abs(q) <= F(1,4):
        z = rational(q)
        z2 = z*z
        term, total = z, ZERO
        for j in range(LOG_TERMS):
            total = total + term/I.point(2*j+1)
            term = term*z2
        r = I(_abs_upper(z), _abs_upper(z))
        tail = I.point(2)*_power(r,2*LOG_TERMS+1)/(
            I.point(2*LOG_TERMS+1)*(ONE-r*r))
        err = I(tail.hi.copy_negate(), tail.hi)
        return I.point(2)*total+err
    # Far from equality, independent logarithms do not subtract close numbers.
    return I.point(b).ln()-I.point(a).ln()


def expm1_enclosure(x: I) -> I:
    """Enclose exp(x)-1 with a fixed series near zero, not rounded exp minus 1."""
    if not isinstance(x,I):
        raise ProviderError('INTERVAL_REQUIRED')
    if x.lo == 0 and x.hi == 0:
        return ZERO
    if _abs_upper(x) <= D('0.5'):
        term, total = x, ZERO
        for j in range(1,EXPM1_TERMS+1):
            total = total+term
            term = term*x/I.point(j+1)
        # term encloses x^65/65!. Subsequent ratios are <= (1/2)/66.
        tail = I(_abs_upper(term), _abs_upper(term))*I.point(132)/I.point(131)
        return total+I(tail.hi.copy_negate(),tail.hi)
    return x.exp()-ONE


def _analytic_pair(ident: str, a: D, b: D):
    ka = analytic(ident,a,a)[0]
    if a == b:
        return ka,ZERO,ZERO
    _, ps, bs = SPECS[ident]
    d = I.point(ps)*log_ratio(a,b) + I.point(bs)*rational((F(b)-F(a))/(F(a)*F(b)))
    return ka,ka*expm1_enclosure(d),d


def _rate_pair(ident: str, a: D, b: D):
    af = ident=='GRACKLE_3_4_1_K57' and a<=CUT
    bf = ident=='GRACKLE_3_4_1_K57' and b<=CUT
    if af and bf:
        return FLOOR,ZERO,{'branch_event':'SAME_ARTIFICIAL_FLOOR',
            'jump_cm3_s':['0','0'],'smooth_increment_cm3_s':['0','0'],
            'log_rate_ratio':None}
    if not af and not bf:
        ka,delta,d = _analytic_pair(ident,a,b)
        return ka,delta,{'branch_event':'SAME_ANALYTIC_BRANCH',
            'jump_cm3_s':['0','0'],'smooth_increment_cm3_s':delta.json(),
            'log_rate_ratio':d.json()}
    # Crossing the original discontinuity. Include the jump explicitly;
    # do not continue a smooth derivative through 3000 K.
    high = b if af else a
    kc,smooth,_ = _analytic_pair(ident,CUT,high)
    jump = kc-FLOOR
    if af:
        ka,delta = FLOOR,jump+smooth
    else:
        ka = analytic(ident,a,a)[0]
        delta = -(jump+smooth)
        jump,smooth = -jump,-smooth
    return ka,delta,{'branch_event':'CROSSES_DISCONTINUOUS_3000K',
        'jump_cm3_s':jump.json(),'smooth_increment_cm3_s':smooth.json(),
        'log_rate_ratio':None}


def paired_reference(provider, T_a, n_a, T_b, n_b, chi_J):
    """Signed source at B minus A with exactly one shared named provider."""
    ident = canonical(provider)
    a,b,na,nb,chi = [number(x) for x in (T_a,T_b,n_a,n_b,chi_J)]
    if a<=0 or b<=0 or na<0 or nb<0 or chi<=0:
        raise ProviderError('POSITIVE_T_CHI_NONNEGATIVE_DENSITY_REQUIRED')
    try:
        ka,dk,parts = _rate_pair(ident,a,b)
        # Exact decimal differences are formed as rational numbers first.
        dn2 = rational((F(nb)-F(na))*(F(nb)+F(na)))
        nb2 = rational(F(nb)*F(nb))
        delta = (ka*dn2+nb2*dk)*I.point('1e-6')
        dq = delta*I.point(chi)
    except DecimalException as exc:
        raise ProviderError('NUMERIC_ENCLOSURE_UNAVAILABLE:'+type(exc).__name__) from exc
    return {'schema':'wu088.hh_paired_source_reference.v1',
        'canonical_provider':ident,'requested_provider':provider,
        'orientation':'B_MINUS_A','same_provider_realization':True,
        'state_a':{'T_K':str(a),'n_HI_m3':str(na)},
        'state_b':{'T_K':str(b),'n_HI_m3':str(nb)},'chi_J':str(chi),
        'branch_event':parts['branch_event'],'rate_decomposition':parts,
        'delta_rate_cm3_s':dk.json(),'delta_event_m3_s':delta.json(),
        'species_order':['HI','HII','Hminus','e_free'],
        'species_delta_sources_m3_s':[(-delta).json(),delta.json(),['0','0'],delta.json()],
        'thermal_delta_J_m3_s':(-dq).json(),'binding_delta_J_m3_s':dq.json(),
        'energy_sum_J_m3_s':['0','0'],
        'pair_convention':'GRACKLE_NETWORK_R_EQUALS_K_NHI_SQUARED',
        'correlation':'SHARED_EXACT_DECIMAL_FIT_AND_SIGNED_EVENT_DIFFERENCE',
        'numerical_error_kind':'OUTWARD_ENCLOSURE_OF_EXACT_DECIMAL_FIT_ONLY',
        'physical_uncertainty_kind':'NOT_BOUNDED',
        'physical_consumer_domain':None,'cosmological_history_difference':False,
        'admission':False,'decimal_precision':80}


def fixed_state_model_contrast(T_a,n_a,T_b,n_b,chi_J):
    """KS paired forcing minus LCS paired forcing at identical prescribed states.

Not the change of a cosmological signal: model-dependent histories are absent.
    """
    l = paired_reference('GRACKLE_3_4_1_K57',T_a,n_a,T_b,n_b,chi_J)
    k = paired_reference('GLOVER2015_KS91_EQ14',T_a,n_a,T_b,n_b,chi_J)
    delta = I(*(D(x) for x in k['delta_event_m3_s'])) - I(*(D(x) for x in l['delta_event_m3_s']))
    return {'schema':'wu088.hh_fixed_state_model_contrast.v1',
        'orientation':'KS_PAIR_MINUS_LCS_PAIR','components':{'LCS':l,'KS':k},
        'delta_pair_event_m3_s':delta.json(),
        'scope':'TWO_FIXED_STATES_NOT_REI_F09_HISTORY_ACCEPTANCE',
        'model_spread_is_physical_enclosure':False,'admission':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider',required=True)
    for name in ('T-a','n-a','T-b','n-b','chi'):
        parser.add_argument('--'+name,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    try:
        result = paired_reference(args.provider,args.T_a,args.n_a,args.T_b,args.n_b,args.chi)
        with args.out.open('x',encoding='utf-8') as stream:
            json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    except (ProviderError,OSError) as exc:
        parser.exit(2,str(exc)+'\n')
if __name__=='__main__':
    main()
