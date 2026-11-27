"""One-case independent closure probe for B10 perfect-square shortcut."""
import inspect
import json
from pathlib import Path
from fractions import Fraction
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from exact_gram.engine import Limits, ResourceLimit, sqrt_interval, _sqrt
src, start = inspect.getsourcelines(_sqrt)
allocation_line = start + next(i for i,line in enumerate(src) if 'pn, pd = isqrt' in line)
observed = {'scope':'SYNTHETIC_ONLY_ONE_CASE','input':'2**200',
            'max_work_bits':8,'isqrt_or_square_shortcut_reached':False}
def trace(frame,event,arg):
    if frame.f_code is _sqrt.__code__ and event=='line' and frame.f_lineno==allocation_line:
        observed['isqrt_or_square_shortcut_reached']=True
    return trace
sys.settrace(trace)
try:
    sqrt_interval(Fraction(2**200), limits=Limits(max_work_bits=8))
    observed['termination']='RETURNED'
except ResourceLimit as exc:
    observed['termination']='RESOURCE_LIMIT'
    observed['message']=str(exc)
finally:
    sys.settrace(None)
assert observed['termination']=='RESOURCE_LIMIT'
assert observed['isqrt_or_square_shortcut_reached'] is False
observed['status']='PASS_FINDING_CLOSED'
print(json.dumps(observed,indent=2))
