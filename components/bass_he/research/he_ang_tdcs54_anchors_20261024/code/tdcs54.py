"""Jones2000 sparse reported TDCS diagnostics, Eqs1-8; no event provider.

Fraction values are authoritative. No old scientific module is imported.
The conditional printing model is restricted to this table's positive endpoints.
"""
from decimal import Decimal, InvalidOperation, localcontext
from fractions import Fraction
import math
import re

UNIT='source_atomic_units_TDCS_area_per_energy_per_solid_angle_squared'
COLUMNS=('CDW_EIS_TDCS_au','CCC99_TDCS_au','experiment_TDCS_au')
ROW_KEYS={'incident_energy_eV','slow_energy_eV','fast_angle_counterclockwise_deg',
          'source_lobe','slow_angle_clockwise_deg',*COLUMNS}
_DECIMAL=re.compile(r'\+?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z')


class ContractError(ValueError):pass


def exact(value, *, zero_allowed=False):
    if isinstance(value,bool) or isinstance(value,float):
        raise ContractError('bool and float inputs are not exact source inputs')
    if isinstance(value,Fraction):result=value
    elif isinstance(value,int):result=Fraction(value)
    elif isinstance(value,str) and _DECIMAL.fullmatch(value):
        try:result=Fraction(Decimal(value))
        except (InvalidOperation,ValueError,OverflowError) as exc:
            raise ContractError('finite exact decimal input required') from exc
    else:raise ContractError('positive exact decimal string, integer or Fraction required')
    if result<0 or (result==0 and not zero_allowed):
        raise ContractError('strictly positive value required')
    return result


def _values(values):
    if not isinstance(values,(list,tuple)) or not values:
        raise ContractError('nonempty sequence of exact positive values required')
    return [exact(x) for x in values]


def _delta(delta):
    delta=exact(delta,zero_allowed=True)
    if delta>=1:raise ContractError('delta must satisfy0<=delta<1')
    return delta


def _bounds(scale_min,scale_max):
    if scale_min is None and scale_max is None:return None
    if scale_min is None or scale_max is None:raise ContractError('both scale bounds required')
    low,high=exact(scale_min),exact(scale_max)
    if low>high:raise ContractError('reversed scale bounds')
    return low,high


def ratio_profile(theory_values,nominal_values):
    model,data=_values(theory_values),_values(nominal_values)
    if len(model)!=len(data):raise ContractError('theory/data sizes differ')
    ratios=[m/d for m,d in zip(model,data)]
    return {'ratios':ratios,'minimum':min(ratios),'maximum':max(ratios),'count':len(ratios)}


def feasible_scale_interval(ratios,delta,scale_min=None,scale_max=None):
    ratios=_values(ratios);delta=_delta(delta);bounds=_bounds(scale_min,scale_max)
    low,high=max(ratios)/(1+delta),min(ratios)/(1-delta)
    free_low,free_high=low,high
    if bounds:low,high=max(low,bounds[0]),min(high,bounds[1])
    feasible=low<=high
    witness=low if feasible else None
    return {'free_lower':free_low,'free_upper':free_high,'lower':low,'upper':high,
            'feasible':feasible,'witness_scale':witness,
            'witness_u':[r/witness for r in ratios] if feasible else None,
            'meaning':'nominated deterministic sensitivity, not statistical rejection'}


def minimax_profile(ratios,scale_min=None,scale_max=None):
    ratios=_values(ratios);bounds=_bounds(scale_min,scale_max)
    low,high=min(ratios),max(ratios)
    optimum=(high+low)/2;delta=(high-low)/(high+low)
    constrained=min(bounds[1],max(bounds[0],optimum)) if bounds else optimum
    q=max(abs(r/constrained-1) for r in ratios)
    return {'free_scale':optimum,'free_delta':delta,'constrained_scale':constrained,
            'constrained_delta':q,'witness_u':[r/constrained for r in ratios],
            'constrained_q_at_least_one':q>=1}


def pair_contrast(m_first,m_second,d_first,d_second,delta):
    mf,ms,df,ds=map(exact,(m_first,m_second,d_first,d_second));delta=_delta(delta)
    rm,rd=mf/ms,df/ds;q=rm/rd
    lower,upper=(1-delta)/(1+delta),(1+delta)/(1-delta)
    return {'theory_ratio':rm,'nominal_ratio':rd,'scale_free_Q':q,
            'two_point_minimum_delta':abs(q-1)/(q+1),
            'Q_lower':lower,'Q_upper':upper,
            'nominal_ratio_sensitivity_lower':rd*lower,
            'nominal_ratio_sensitivity_upper':rd*upper}


def source_angle_vectors(fast_ccw_deg,slow_cw_deg):
    fast=exact(fast_ccw_deg,zero_allowed=True);slow=exact(slow_cw_deg,zero_allowed=True)
    if fast>360 or slow>360:raise ContractError('source angle must lie in0..360degrees')
    f,s=math.radians(float(fast)),math.radians(float(slow))
    nf=[math.sin(f),0.,math.cos(f)];ns=[-math.sin(s),0.,math.cos(s)]
    total=(fast+slow)%360
    return {'fast_direction':nf,'slow_direction':ns,
            'dot':math.fsum(x*y for x,y in zip(nf,ns)),
            'small_pair_angle_deg':min(total,360-total),
            'slow_polar_angle_deg':min(slow,360-slow),
            'convention':'beam+z, fastCCW toward+x, slowCW in xz plane',
            'finite_mass_frame_transform':False}


def conditional_printing_ratio_interval(model,nominal,printed_ratio,half_width=Fraction(1,200)):
    m,d,p=map(exact,(model,nominal,printed_ratio));h=exact(half_width,zero_allowed=True)
    if min(m,d,p)<=h:
        raise ContractError('printing diagnostic restricted to this table with all nominal endpoints>h')
    lower,upper=(m-h)/(d+h),(m+h)/(d-h)
    pl,pu=p-h,p+h
    lo,hi=max(lower,pl),min(upper,pu)
    return {'nominal_recomputed_ratio':m/d,'printed_ratio':p,'residual':m/d-p,
            'ratio_lower':lower,'ratio_upper':upper,'printed_lower':pl,'printed_upper':pu,
            'overlap_lower':lo,'overlap_upper':hi,'compatible':lo<=hi,
            'scope':'conditional nearest0.01 printing model; no experimental error model'}


def validate_source_rows(rows,metadata):
    if not isinstance(rows,list) or len(rows)!=8:raise ContractError('exactly8reported feature rows required')
    if not isinstance(metadata,dict) or metadata.get('unit')!=UNIT or metadata.get('representation')!='already_reported_TDCS':
        raise ContractError('source unit and already-reported representation required')
    if metadata.get('nucleus')!='infinite_mass_source' or metadata.get('physical_provider_admitted') is not False:
        raise ContractError('infinite-mass sparse-source boundary required')
    located=[];binary=[]
    expected=[('4','binary_peak',''),('4','recoil_comparison_at210','210'),
              ('10','binary_peak',''),('10','recoil_comparison_at210','210'),
              ('16','binary_peak',''),('16','recoil_peak',''),
              ('23','binary_peak',''),('23','recoil_peak','')]
    for i,(row,(fa,lobe,sa)) in enumerate(zip(rows,expected)):
        if not isinstance(row,dict) or set(row)!=ROW_KEYS or any(not isinstance(v,str) for v in row.values()):
            raise ContractError('original source columns and literal strings required')
        if exact(row['incident_energy_eV'])!=Fraction(272,5) or exact(row['slow_energy_eV'])!=5:
            raise ContractError('source energies differ')
        if (row['fast_angle_counterclockwise_deg'],row['source_lobe'],row['slow_angle_clockwise_deg'])!=(fa,lobe,sa):
            raise ContractError('source feature order/location changed; unknown angles stay absent')
        for key in COLUMNS:exact(row[key])
        if sa:located.append(i)
        if lobe=='binary_peak':binary.append(i)
    return {'groups':{'located_anchors_2':located,'binary_peak_heights_4':binary,
                      'all_reported_features_8':list(range(8))},
            'located_points':2,'located_cross_section_values':6,'source_values':24,
            'physical_provider_admitted':False,'fast_energy':'NOT_EVALUATED'}


def serialized(value):
    if isinstance(value,Fraction):
        with localcontext() as ctx:
            ctx.prec=40
            display=Decimal(value.numerator)/Decimal(value.denominator)
        if not display.is_finite():raise ContractError('nonfinite display decimal')
        return {'numerator':str(value.numerator),'denominator':str(value.denominator),'decimal':str(display)}
    if isinstance(value,dict):return {k:serialized(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [serialized(v) for v in value]
    if isinstance(value,float) and not math.isfinite(value):raise ContractError('nonfinite geometry output')
    return value
