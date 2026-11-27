"""Run ONLY the named exact toy fixtures and emit measured JSON to stdout."""
from dataclasses import asdict
from fractions import Fraction as F
import json
import platform
import tracemalloc

from .engine import Interval as I,Rectangle as R,Caps,Budget,integrate_range,DomainFailure,RangeClaim
from .toys import point,polynomial_range,constant_range,nested_range


def rectangle_json(rect):
    if rect is None: return None
    return {'real':[str(rect.real.lo),str(rect.real.hi)],'imag':[str(rect.imag.lo),str(rect.imag.hi)],
            'max_width':str(rect.max_width)}


def measure(name,caps,callback_factory,z,expected=None):
    tracemalloc.start()
    budget=Budget(caps)
    result=integrate_range(callback_factory(budget),I(0,1),z,budget=budget)
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {'name':name,'scope':'SYNTHETIC_ONLY','caps':{k:str(v) if isinstance(v,F) else v for k,v in asdict(caps).items()},
            'status':result.status,'reason':result.reason,'enclosure':rectangle_json(result.enclosure),
            'expected_independent_exact':rectangle_json(expected),
            'contains_expected':result.enclosure.contains(expected) if result.enclosure is not None and expected is not None else None,
            'metrics':dict(result.metrics,python_tracemalloc_peak_bytes=peak,
                           tracemalloc_scope='Python allocation peak during this case; not process RSS or hard memory cap'),
            'no_live_budget_state_remaining':budget.live_panels==0 and budget.live_state_bytes==0}


def main():
    cases=[]
    for width in (F(1,16),F(1,64),F(1,256)):
        cases.append(measure('toy_real_t_squared_width_'+str(width),Caps(target_width=width),
                             lambda b:polynomial_range,point(1),point(F(1,3))))
    cases.append(measure('toy_uniform_complex_parameter_box',Caps(target_width=F(3,4)),
                         lambda b:polynomial_range,R(I(1,2),I(-1,1)),R(I(F(1,3),F(2,3)),I(F(-1,3),F(1,3)))))
    cases.append(measure('toy_nested_uniform_integral',Caps(target_width=F(1,16),max_evaluations=15000,max_panels=1024),
                         lambda b:lambda t,z:nested_range(t,z,b),point(0),point(F(1,6))))
    cases.append(measure('toy_evaluation_cap',Caps(target_width=F(1,1000),max_evaluations=1),
                         lambda b:polynomial_range,point(1),point(F(1,3))))
    cases.append(measure('toy_width_floor',Caps(target_width=F(1,10)),
                         lambda b:constant_range,R(I(0,1),I(0,0)),R(I(0,1),I(0,0))))
    def bad(t,z): raise DomainFailure('synthetic domain refusal')
    cases.append(measure('toy_domain_failure',Caps(),lambda b:bad,point(1)))
    def midpoint(t,z): return RangeClaim(point(F(1,6)),t,z,False,'explicit_midpoint_only_refusal')
    cases.append(measure('toy_midpoint_only_refusal',Caps(),lambda b:midpoint,R(I(0,1),I(0,0))))
    success=all(c['contains_expected'] is not False and c['no_live_budget_state_remaining'] for c in cases)
    expected_statuses=['TARGET_WIDTH_MET']*5+['CERTIFICATE_INCONCLUSIVE_RESOURCE_LIMIT','CERTIFICATE_INCONCLUSIVE_WIDTH','CALLBACK_DOMAIN_FAILURE','INVALID_RANGE_CONTRACT']
    success=success and [c['status'] for c in cases]==expected_statuses
    print(json.dumps({'schema':'WU088_R31AO_SYNTHETIC_INTERIOR_PILOT_V1','python':platform.python_version(),
        'verified':success,'cases':cases,'HH_inputs_evaluated':False,'HH_feasibility':'UNMEASURED',
        'numerical_certificate_runs':0,'science_commands':0,'native_builds':0},indent=2))
    if not success: raise SystemExit(1)


if __name__=='__main__': main()
