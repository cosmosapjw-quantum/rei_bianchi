"""One unmodified Python scientific call per case."""
from __future__ import annotations
import time
from .contracts import CaseSpec, CaseOutcome, digest
from bass_he.replay_contract import BRANCHES, CONTROL_PAIR, WRONG_PAIR, CONTROL_SEED, SOURCE_DELTA, SOURCE_REL_LIMIT, EP_DISTANCE_LIMIT, RESIDUAL_LIMIT, SHEET_GAP_MIN

def jsonable(x):
    import numpy as np
    if isinstance(x, (complex,np.complexfloating)): return {'complex':[float(x.real),float(x.imag)]}
    if isinstance(x, np.ndarray): return [jsonable(v) for v in x.tolist()]
    if isinstance(x, np.generic): return jsonable(x.item())
    if isinstance(x, dict): return {k:jsonable(v) for k,v in x.items()}
    if isinstance(x, (list,tuple)): return [jsonable(v) for v in x]
    return x

def unjsonable(x):
    if isinstance(x, dict): return complex(*x['complex']) if set(x)=={'complex'} else {k:unjsonable(v) for k,v in x.items()}
    if isinstance(x, list): return [unjsonable(v) for v in x]
    return x

def run_case(spec: CaseSpec, on_call=None) -> CaseOutcome:
    from bass_he.spectral import find_exceptional_point
    from bass_he.sturm_geometry import contour_geometry
    f=spec.science_fields; kind=spec.kind; start=time.perf_counter()
    def call(name,fn,*args,**kw):
        if on_call:on_call(name)
        return fn(*args,**kw)
    if f['backend'] != 'python': return CaseOutcome('ENVIRONMENT_ERROR',{}, {'reason':'accelerator payload unavailable'})
    if kind == 'wrong_pair_check':
        try: call('find_exceptional_point',find_exceptional_point,*f['pair'], unjsonable(f['seed']), depth=f['depth'])
        except RuntimeError as exc:
            if 'pair membership' in str(exc): return CaseOutcome('WRONG_PAIR',{}, {'reason':str(exc),'elapsed_seconds':time.perf_counter()-start})
            raise
        return CaseOutcome('NUMERICAL_REJECTED',{}, {'reason':'wrong pair accepted'})
    if kind in ('control','endpoint'):
        ep=call('find_exceptional_point',find_exceptional_point,*f['pair'], unjsonable(f['seed']), depth=f['depth'])
        if kind == 'endpoint':
            distance=abs(ep['R']-unjsonable(f['seed']))
            good=distance <= EP_DISTANCE_LIMIT and ep['certificate']['simple_fold'] and ep['pair_membership']['passed']
            return CaseOutcome('PASS' if good else 'NUMERICAL_REJECTED', {'ep':jsonable(ep),'distance':float(distance)}, {'elapsed_seconds':time.perf_counter()-start})
        geo=call('contour_geometry',contour_geometry,ep,0.,panels=64)
        rel=abs(geo['delta']-SOURCE_DELTA)/SOURCE_DELTA
        good=rel <= SOURCE_REL_LIMIT and geo['max_spectral_residual'] <= RESIDUAL_LIMIT and ep['pair_membership']['passed']
        return CaseOutcome('PASS' if good else 'NUMERICAL_REJECTED', {'ep':jsonable(ep),'geometry':jsonable(geo),'relative_to_source':float(rel)}, {'elapsed_seconds':time.perf_counter()-start})
    ep=unjsonable(f['endpoint'])
    if digest(f['endpoint']) != f['certificate_sha256']: raise ValueError('endpoint certificate hash mismatch')
    if tuple(ep['state_a']) != tuple(f['pair'][0]) or tuple(ep['state_b']) != tuple(f['pair'][1]): raise ValueError('endpoint pair mismatch')
    geo=call('contour_geometry',contour_geometry,ep,f['rho'],panels=f['panels'])
    good=geo['delta'] > 0 and geo['max_spectral_residual'] <= RESIDUAL_LIMIT and geo['minimum_normalized_sheet_gap'] > SHEET_GAP_MIN
    return CaseOutcome('PASS' if good else 'NUMERICAL_REJECTED',jsonable(geo),{'elapsed_seconds':time.perf_counter()-start})
