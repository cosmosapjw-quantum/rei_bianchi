"""G2 -> G3 -> epsilon -> real-rule integration on declared synthetic data.

This module has no file loader, HH execution mode, backend evaluator, approval
parser or scientific certificate issuer. A scope string is not provenance.
Actual admission requires external authenticated artifacts and remains open.
"""
from exact_raw_decoder import decode_npy_bytes, inspect_npy_header, DecodeError
from exact_gram.engine import (
    ContractError, DEFAULT_LIMITS, Limits, ResourceLimit, from_decoded,
    represented_gaps, source_error_bound_disk, propagate_epsilon,
    pareto_sufficient,
)

PipelineError = ContractError


def _keys(value, expected, label):
    if not isinstance(value,dict) or set(value)!=set(expected):
        raise PipelineError('exact '+label+' keys required')


def _decode(value, limits):
    try:
        header=inspect_npy_header(value)
        if header.element_count>limits.max_entries:
            raise ResourceLimit('synthetic input exceeds matrix entry budget')
        d=decode_npy_bytes(value,max_elements=limits.max_entries)
    except DecodeError as exc:
        # Length/type/ABI failures never become substitute numerical values.
        raise PipelineError('synthetic NPY admission failed: '+str(exc)) from exc
    if d.header.descr not in ('<c16','>c16'):
        raise PipelineError('integration fixture requires explicit complex128')
    return from_decoded(d,limits=limits),d.canonical_sha256


def evaluate_synthetic_bundle(raw, models, target_disks, *, scope,
                              precision=160, limits=DEFAULT_LIMITS):
    if scope!='SYNTHETIC_ONLY':
        raise PipelineError('no actual-HH mode; numerical authorization required')
    if not isinstance(limits,Limits):
        raise PipelineError('Limits object required')
    _keys(raw,('D_col','D_row'),'raw')
    _keys(target_disks,('D_col','D_row'),'target disk')
    _keys(models,('R31AK','R31Z','R31AD'),'frozen model')
    decoded_raw={};identities={}
    for key,value in raw.items():
        decoded_raw[key],identities['raw.'+key]=_decode(value,limits)
    decoded_models={}
    for name,fields in models.items():
        _keys(fields,('D_col','D_row','K'),'stored model')
        decoded_models[name]={}
        for key,value in fields.items():
            decoded_models[name][key],identities[name+'.'+key]=_decode(value,limits)
    gaps=represented_gaps(decoded_models,decoded_raw['D_col'],decoded_raw['D_row'],
                          precision=precision,limits=limits)
    ec=source_error_bound_disk(decoded_raw['D_col'],target_disks['D_col'],
                               precision=precision,limits=limits)
    er=source_error_bound_disk(decoded_raw['D_row'],target_disks['D_row'],
                               precision=precision,limits=limits)
    eps=propagate_epsilon(ec,er,limits=limits)
    comparisons={name:pareto_sufficient([gaps[name][m] for m in ('K','Dmax')],
                                      [eps[m] for m in ('K','Dmax')],limits=limits)
                 for name in ('PRIMARY','SECONDARY')}
    supported=all(v['status']=='CERTIFIED_REAL_PARETO_SUFFICIENT_CONDITION'
                  for v in comparisons.values())
    return {
        'scope':'DECLARED_SYNTHETIC_ARITHMETIC_ONLY',
        'status':'SYNTHETIC_REAL_RULE_SUPPORTED' if supported else 'SYNTHETIC_DECISION_BOUND_UNRESOLVED',
        'canonical_dyadic_hashes':identities,
        'represented_gaps':{name:{m:gaps[name][m].to_json() for m in ('K','Dmax')}
                            for name in ('PRIMARY','SECONDARY')},
        'epsilon_arithmetic':{'D_col':str(ec),'D_row':str(er),**{k:str(v) for k,v in eps.items()}},
        'comparisons':comparisons,
        'target_provenance_admitted':False,'machine_predicate_certified':False,
        'independent_review_admitted':False,'certified_epsilon':None,
        'certified_eta':None,'rigorous':False,'X0_X8_added':False,
        'actual_HH_execution_supported':False,
    }
