"""Three-window endpoint-only probe for the single canonical primitive index 0.

No interior/native producer, geometry/order change, final D goal or certificate.
Default is plan-only. All plans and execution scopes are written before work.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys
import time

PLANNER_SHA256='fe979174ac77d962dc9877a7ea39c01950421011e495134b52745bba44a5b4e0'
PLANNER_PATH=Path(__file__).with_name('planner.py')
if hashlib.sha256(PLANNER_PATH.read_bytes()).hexdigest()!=PLANNER_SHA256:
    raise RuntimeError('frozen endpoint planner source mismatch')
import planner as p

CANDIDATES=(
    ('W1',{'l_t':'1/16','T_t':'256','l_u':'1/16','T_u':'256'}),
    ('W2',{'l_t':'1/64','T_t':str(1<<64),'l_u':'1/64','T_u':str(1<<64)}),
    ('W3',{'l_t':'1/256','T_t':str(1<<192),'l_u':'1/256','T_u':str(1<<192)}),
)


def pow2(k):return Q(1<<k) if k>=0 else Q(1,1<<(-k))


def binary_bracket(token):
    """Exact rational comparison, not a host-float rendering of the bound."""
    q=Q(token)
    if q<0:raise ValueError('negative upper bound')
    if q==0:return {'lower':'0','upper':'0','upper_strict':False}
    e=q.numerator.bit_length()-q.denominator.bit_length()
    if q<pow2(e):e-=1
    assert pow2(e)<=q<pow2(e+1)
    return {'lower':'2^'+str(e),'upper':'2^'+str(e+1),'upper_strict':True}


def file_identity(path):
    path=Path(path).resolve();data=path.read_bytes()
    return {'path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}


def probe(npz,output_dir,*,execute=False,baseline_plan=None,baseline_result=None):
    started=time.monotonic_ns();npz=Path(npz).resolve();output_dir=Path(output_dir).resolve()
    if output_dir.exists():raise p.EndpointError('create-only probe directory already exists')
    if bool(baseline_plan)!=bool(baseline_result):raise p.EndpointError('both baseline paths required')
    data=p.archive_bytes(npz)
    record=p.adapter.decode_npz(data,expected_archive_sha256=p.adapter.FROZEN107_ARCHIVE_SHA256,scope='FROZEN107_PINNED')
    baseline=None
    if baseline_plan:
        bp=p.read_json(baseline_plan);p.validate_plan(bp,source_archive_bytes=data)
        br=p.validate_result(bp,p.read_json(baseline_result))
        if br['status']!='CONDITIONAL_TAIL_BOUND' or br['index']!=0:raise p.EndpointError('completed baseline task 0 required')
        baseline={'plan':file_identity(baseline_plan),'result':file_identity(baseline_result),
                  'window':br['window'],'endpoint_radius':br['endpoint_radius'],
                  'bound_binary_bracket':binary_bracket(br['endpoint_radius'])}
    plans=[]
    for name,window in CANDIDATES:
        # Fixed positive dyadic windows satisfy the real endpoint theorem.
        assert all(Q(window[k])>0 for k in window)
        assert Q(window['l_t'])<Q(window['T_t']) and Q(window['l_u'])<Q(window['T_u'])
        plan=p.build_plan(record,window,precision_bits=128,panels=4,
            caps={'wall_seconds':30,'memory_bytes':512*1024**2},source_archive_bytes=data)
        plans.append((name,plan))
    scope={'schema':'WU088_ENDPOINT_CUTOFF_PROBE_SCOPE_V1','scope':'FROZEN107_PINNED_ENDPOINT_ONLY',
        'execute_requested':execute,'input':file_identity(npz),'input_record_sha256':record['canonical_record_sha256'],
        'planner':file_identity(PLANNER_PATH),'probe':file_identity(__file__),
        'task_index':0,'precision_bits':128,'panels':4,'max_attempts':3,
        'per_attempt_wall_seconds':30,'per_attempt_address_space_bytes':512*1024**2,
        'total_wall_budget_seconds':90,
        'remaining_budget_rule':'Skip any attempt unless at least 31 seconds remain in the declared 90-second probe budget.',
        'candidates':[{'name':name,'window':plan['window'],'plan_sha256':plan['plan_sha256']} for name,plan in plans],
        'validity':'All cutoffs are finite positive dyadics with lower < upper; C_F/endpoint majorants apply on the positive real domain.',
        'design_caveat':'Large upper cutoffs enlarge the compact-interior problem. Smaller lower cutoffs tighten analytic-domain margins. No feasible interior width/cost is established.',
        'baseline':baseline,'interior_evaluations':0,'native_runs':0,'producer_runs':0,
        'new_order_or_geometry':False,'comparator_runs':0,'final_D_radius_goal':None,'scientific_admission':False}
    output_dir.mkdir(parents=True,exist_ok=False)
    p.write_new(output_dir/'SCOPE.json',scope)
    for name,plan in plans:p.write_new(output_dir/(name+'_PLAN.json'),plan)
    summary={'schema':'WU088_ENDPOINT_CUTOFF_PROBE_RESULT_V1','scope_sha256':p.digest(scope),
        'status':'PLANNED_ONLY','attempts':[],'baseline':baseline,'scientific_admission':False,
        'evidence_contract':p.EVIDENCE_CONTRACT,'validation_level':p.VALIDATION_LEVEL,
        'actual_endpoint_attempts':0,'interior_evaluations':0,'final_D_epsilon':None}
    if execute:
        for name,plan in plans:
            remaining=90*10**9-(time.monotonic_ns()-started)
            if remaining<31*10**9:
                summary['attempts'].append({'name':name,'status':'SKIPPED_GLOBAL_WALL_BUDGET','window':plan['window']})
                continue
            # The prewritten plan is the full exact source/work scope of this attempt.
            result=p.run_task(output_dir/(name+'_PLAN.json'),0,output_dir/(name+'_RESULT.json'),
                npz_path=npz,execute_pinned=True)
            summary['actual_endpoint_attempts']+=1
            entry={'name':name,'window':plan['window'],'plan_sha256':plan['plan_sha256'],
                   'status':result['status'],'result_sha256':result['result_sha256'],
                   'engine_calls':result['engine_calls'],'elapsed_ns':result['elapsed_ns'],
                   'endpoint_radius':result['endpoint_radius'],'reason':result['reason']}
            if result['status']=='CONDITIONAL_TAIL_BOUND':
                entry['bound_binary_bracket']=binary_bracket(result['endpoint_radius'])
                if baseline and Q(baseline['endpoint_radius'])>0:
                    ratio=Q(result['endpoint_radius'])/Q(baseline['endpoint_radius'])
                    entry['bound_to_baseline_exact_ratio']=str(ratio)
                    entry['ratio_binary_bracket']=binary_bracket(str(ratio))
            summary['attempts'].append(entry)
        summary['status']='BOUNDED_ENDPOINT_PROBE_OBSERVED'
    summary['total_elapsed_ns']=time.monotonic_ns()-started
    summary['within_90_second_budget']=summary['total_elapsed_ns']<=90*10**9
    if not summary['within_90_second_budget']:summary['status']='INCONCLUSIVE_GLOBAL_RESOURCE_LIMIT'
    p.write_new(output_dir/'RESULT.json',summary)
    return summary


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--npz',required=True);cli.add_argument('--output-dir',required=True)
    cli.add_argument('--baseline-plan');cli.add_argument('--baseline-result')
    cli.add_argument('--execute',action='store_true')
    args=cli.parse_args()
    result=probe(args.npz,args.output_dir,execute=args.execute,
                 baseline_plan=args.baseline_plan,baseline_result=args.baseline_result)
    # Compact console record; exact potentially long rationals live in RESULT.json.
    print(json.dumps({'status':result['status'],'actual_endpoint_attempts':result['actual_endpoint_attempts'],
        'total_elapsed_ns':result['total_elapsed_ns'],'within_90_second_budget':result['within_90_second_budget'],
        'attempts':[{k:v for k,v in item.items() if k in ('name','status','bound_binary_bracket','ratio_binary_bracket','elapsed_ns','engine_calls')}
                    for item in result['attempts']]},sort_keys=True))
    return 0 if result['within_90_second_budget'] else 2


if __name__=='__main__':
    try:raise SystemExit(main())
    except (p.EndpointError,ValueError,OSError) as exc:
        print(json.dumps({'status':'ENDPOINT_PROBE_REFUSED','reason':str(exc),'scientific_admission':False}),file=sys.stderr)
        raise SystemExit(2)
