"""Two bounded exact checks for incomplete child subdivision semantics."""
from pathlib import Path
import json
from fractions import Fraction as F
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from interior_pilot.engine import Interval, Caps, Budget, ResourceLimit,integrate_range
from interior_pilot.toys import point,polynomial_range
results=[]
for fail_call in (3,5):
    count=[0]
    budget=Budget(Caps(target_width=F(1,1000)))
    def callback(t,z):
        count[0]+=1
        if count[0]==fail_call:raise ResourceLimit('SYNTHETIC_PENDING_RIGHT_CHILD')
        return polynomial_range(t,z)
    res=integrate_range(callback,Interval(0,1),point(1),budget=budget)
    assert res.status=='CERTIFICATE_INCONCLUSIVE_RESOURCE_LIMIT'
    assert res.enclosure.real.contains(F(1,3))
    assert res.enclosure.imag.contains(F(0))
    assert budget.live_panels==budget.live_state_bytes==0
    expected=Interval(0,1) if fail_call==3 else Interval(F(1,8),F(5,8))
    assert res.enclosure.real==expected
    results.append({'failed_callback':fail_call,'status':'PASS_LAST_COMPLETE_ENCLOSURE',
                    'enclosure_real':[str(expected.lo),str(expected.hi)],
                    'live_panels':budget.live_panels,'live_state_bytes':budget.live_state_bytes})
print(json.dumps({'scope':'BOUNDED_SYNTHETIC_ONLY','results':results},indent=2))
