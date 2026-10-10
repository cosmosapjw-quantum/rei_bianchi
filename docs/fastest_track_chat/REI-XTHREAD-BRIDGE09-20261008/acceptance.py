"""Opt-in, exact-algebra acceptance of a parameter-family full/two-half proxy.

This consumes proved endpoint boxes. It does not prove the inputs, uniform
ledger bounds, the continuous solution, or compatibility with paired_trial.
"""
from __future__ import annotations
from fractions import Fraction as F
from copy import deepcopy
import math

class ContractError(ValueError):pass
LOCAL=F(2e-4); WIDTH=F(2e-3); LEDGER=F(1e-12)

def rational(x):
    if isinstance(x,bool):raise ContractError('BOOLEAN_INPUT')
    if isinstance(x,float) and not math.isfinite(x):raise ContractError('NONFINITE_INPUT')
    try:return F(x)
    except (ValueError,TypeError,OverflowError):raise ContractError('INVALID_NUMBER') from None

def checked_boxes(v):
    if not v:raise ContractError('EMPTY_OBSERVABLES')
    out=[]
    for row in v:
        if len(row)!=2:raise ContractError('INTERVAL_SHAPE')
        lo,hi=map(rational,row)
        if lo>hi:raise ContractError('REVERSED_INTERVAL')
        out.append((lo,hi))
    return out

def difference_bound(a,b):
    aa,bb=checked_boxes(a),checked_boxes(b)
    if len(aa)!=len(bb):raise ContractError('READOUT_SHAPE')
    return max(max(abs(x[0]-y[1]),abs(x[1]-y[0])) for x,y in zip(aa,bb))

def width_bound(a):return max(hi-lo for lo,hi in checked_boxes(a))

def validate_partition(nodes):
    n=tuple(map(rational,nodes))
    if len(n)<2 or any(b<=a for a,b in zip(n,n[1:])):raise ContractError('CLOCK_ORDER')
    return n

def evaluate(full:dict,fine:dict,plan:dict,point_ledger_bound)->dict:
    keys=('model','source_sha','input_family','birth_plan','source_weights','fields','start','end')
    if any(full.get(k)!=fine.get(k) for k in keys):raise ContractError('MISMATCHED_MODEL_SOURCE_INPUT_OR_BIRTH')
    if full['birth_plan']!=plan['birth_plan']:raise ContractError('PLAN_IDENTITY_MISMATCH')
    a,b=validate_partition(plan['full_mesh']),validate_partition(plan['fine_mesh'])
    if (a[0],a[-1])!=(b[0],b[-1]) or (a[0],a[-1])!=(rational(full['start']),rational(full['end'])):raise ContractError('MACRO_WINDOW_MISMATCH')
    if a==b:raise ContractError('VACUOUS_COMPARISON_MESH')
    if not set(a).issubset(b):raise ContractError('FINE_PARTITION_NOT_REFINEMENT')
    for t in plan['births']:
        if rational(t) not in a or rational(t) not in b:raise ContractError('BIRTH_NOT_A_COMMON_BOUNDARY')
    l=difference_bound(full['boxes'],fine['boxes']);w=width_bound(fine['boxes']);g=rational(point_ledger_bound)
    if g<0:raise ContractError('NEGATIVE_LEDGER_BOUND')
    if not(full.get('endpoint_inclusion_verified') and fine.get('endpoint_inclusion_verified')):raise ContractError('UNVERIFIED_ENDPOINT_INPUT')
    reasons=[]
    if l>=LOCAL:reasons.append('PARAMETER_DIFFERENCE_UPPER_NOT_BELOW_LOCAL_LIMIT')
    if w>=WIDTH:reasons.append('FINE_PUBLIC_WIDTH_NOT_BELOW_LIMIT')
    if g>LEDGER:reasons.append('POINT_LEDGER_LIMIT')
    return {'accepted':not reasons,'status':'SCOPED_PROXY_ACCEPT' if not reasons else 'NO_COMMIT_REJECT',
       'local_upper':l,'public_width_upper':w,'point_ledger_upper':g,'reasons':reasons,
       'fine_payload':deepcopy(fine.get('payload')) if not reasons else None,
       'input_correlation':'same-parameter diagonal is contained in the rectangular difference, not identified with it',
       'canonical_paired_trial':False,'uniform_parameter_ledger':False,'continuous_error':None,'restart_verified':False}

def transact(state:dict, full:dict, fine:dict,plan:dict,point_ledger_bound, *, late_guard=None)->dict:
    """Commit an archived fine endpoint only after all local checks succeed.

    This is a diagnostic adapter transaction, not a native restart decoder.
    """
    if state.get('time')!=full['start'] or state.get('birth_plan')!=full['birth_plan']:
        raise ContractError('STALE_TRANSACTION_PARENT')
    result=evaluate(full,fine,plan,point_ledger_bound)
    if not result['accepted']:return result
    candidate=deepcopy(state)
    candidate.update(time=fine['end'],payload=deepcopy(fine.get('payload')),
                     numerical_acceptance_profile='BRIDGE09_EVENT_AWARE_PROXY_V1')
    if late_guard is not None:late_guard(candidate)
    state.clear();state.update(candidate)
    return result
