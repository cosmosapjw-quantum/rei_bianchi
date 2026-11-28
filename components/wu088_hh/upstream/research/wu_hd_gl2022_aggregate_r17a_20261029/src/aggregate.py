"""R17A: exact *printed* SQM reactive thermal total audit; never source-state admission.

Only article text: 205K and 295K, not the original GL2022 native supplementary.
Single finite result; no interpolation or physical-rate callback.
"""
from __future__ import annotations
import hashlib
import json
import re
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

class SourceIdentityError(ValueError):
    pass

ALLOWED_T = (205, 295)
EXPECTED = {
    205: (Fraction(121,100), Fraction(11,10), Fraction(1,5)),
    295: (Fraction(221,100), Fraction(17,10), Fraction(1,5)),
}
EXPECTED_DOI = '10.1063/5.0128598'
EXPECTED_REACTION = 'H+ + HD -> D+ + H2'
FIT_ALPHA = Fraction(857,100)
FIT_GAMMA = 405
SI_PER_PRINTED_UNIT = Fraction(1,10**16)
REQUIRED_TOP = {'schema', 'data_class', 'article', 'points', 'printed_global_fit', 'not_presumed', 'provenance', 'native_reactive_supplement'}
EXACT_DECIMAL = re.compile(r'^[+]?(?:[0-9]+)(?:\.[0-9]+)?$')

def fraction_decimal(t: object) -> Fraction:
    if type(t) is not str or len(t)>32 or not EXACT_DECIMAL.fullmatch(t):
        raise SourceIdentityError('ASCII nonnegative finite printed decimal string required, no float or exponent')
    i, _, tail = t.partition('.')
    if not tail: return Fraction(int(i),1)
    return Fraction(int(i+tail),10**len(tail))

def rational_text(v: Fraction) -> str:
    return str(v.numerator) if v.denominator==1 else f'{v.numerator}/{v.denominator}'

def validated_printed_data(obj: object) -> list[tuple[int,Fraction,Fraction,Fraction]]:
    if type(obj) is not dict or set(obj)!=REQUIRED_TOP: raise SourceIdentityError('transcription schema keys changed')
    if obj['schema']!='WU_HD_GL2022_PUBLISHED_AGGREGATE_EXTRACT_V1' or obj['data_class']!='PUBLISHED_REACTIVE_THERMAL_TOTAL_NOT_STATE_RESOLVED':
        raise SourceIdentityError('incorrect source tier')
    a=obj['article']
    if (type(a) is not dict or a.get('doi')!=EXPECTED_DOI or a.get('method')!='SQM'
        or a.get('reaction')!=EXPECTED_REACTION or a.get('printed_rate_unit')!='1e-10 cm^3 s^-1'
        or a.get('location')!='Sec. III A, Fig. 5 and adjacent prose'):
        raise SourceIdentityError('wrong article/reactive channel/method/unit/tier')
    supp=obj['native_reactive_supplement']
    if type(supp) is not dict or supp.get('status')!='HTTP_403_NOT_DOWNLOADED' or supp.get('SHA256') is not None:
        raise SourceIdentityError('native source bytes not present; only known HTTP403 blocker allowed')
    f=obj['printed_global_fit']
    if (type(f) is not dict or fraction_decimal(f.get('alpha_in_1e-10_cm3_s'))!=FIT_ALPHA
        or fraction_decimal(f.get('gamma_K'))!=FIT_GAMMA
        or f.get('form')!='alpha*exp(-gamma/T)'):
        raise SourceIdentityError('frozen author fit changed')
    if type(obj['points']) is not list or len(obj['points'])!=2: raise SourceIdentityError('exactly two printed points required')
    out=[]
    for p,t in zip(obj['points'],ALLOWED_T):
        if type(p) is not dict or set(p)!={'T_K','k_SQM_printed','k_experiment_printed','experimental_printed_halfwidth'}:
            raise SourceIdentityError('source row field set changed')
        if fraction_decimal(p['T_K'])!=t: raise SourceIdentityError('printed source T/order changed')
        row=tuple(fraction_decimal(p[k]) for k in ('k_SQM_printed','k_experiment_printed','experimental_printed_halfwidth'))
        if row!=EXPECTED[t]: raise SourceIdentityError('printed source values changed')
        out.append((t,*row))
    return out

def evaluate_transcription(obj: dict, raw_bytes: bytes) -> dict:
    values=validated_printed_data(obj)
    rows=[]
    for T,k,obs,hw in values:
        diff=k-obs
        with localcontext() as c:
            c.prec=100
            fit=Decimal(FIT_ALPHA.numerator)/Decimal(FIT_ALPHA.denominator)*(-Decimal(FIT_GAMMA)/Decimal(T)).exp()
            fit_ratio=fit/(Decimal(k.numerator)/Decimal(k.denominator))
        rows.append({
            'T_K':T,'SQM_printed_1e-10_cm3_s':rational_text(k),
            'experiment_printed_1e-10_cm3_s':rational_text(obs),
            'experimental_halfwidth_printed':rational_text(hw),
            'SQM_SI_m3_s':rational_text(k*SI_PER_PRINTED_UNIT),
            'experiment_SI_m3_s':rational_text(obs*SI_PER_PRINTED_UNIT),
            'difference_SI_m3_s':rational_text(diff*SI_PER_PRINTED_UNIT),
            'difference_printed_units':rational_text(diff),
            'difference_over_printed_halfwidth_NOT_SIGMA':rational_text(diff/hw),
            'author_fit_at_T_printed_units_Decimal100':str(fit),
            'author_fit_to_printed_SQM_ratio_Decimal100':str(fit_ratio)
        })
    return {
        'schema':'WU_R17A_PRINTED_AGGREGATE_RESULT_V1',
        'transcription_sha256':hashlib.sha256(raw_bytes).hexdigest(),
        'article_doi':EXPECTED_DOI,
        'data_tier':'PUBLISHED_AGGREGATE_TWO_POINT_DIAGNOSTIC_ONLY',
        'rows':rows,
        'source_rows_native_reactive':0,
        'source_native_file_SHA256':None,
        'state_resolved_admitted':False,
        'physical_consumption_admitted':False,
        'statistics_probability_or_sigma_admitted':False,
        'interpolation_or_extrapolation_admitted':False,
        'DAG_WU':'33/48','DAG_REI':'28/88','new_science_nodes':0,
        'blockers':['GL2022 reactive native state table original bytes missing','named consumer/density/clock missing','independent source-row reviewer missing']
    }

def read_evaluate(path: Path) -> dict:
    raw=path.read_bytes()
    if len(raw)>65536: raise SourceIdentityError('bounded source JSON size exceeded')
    return evaluate_transcription(json.loads(raw),raw)
