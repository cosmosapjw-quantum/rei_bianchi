"""Bounded two-case observation of binary64 exponent-alignment cap ordering."""
import inspect
import json
from pathlib import Path
from fractions import Fraction
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from exact_gram.engine import Limits, ResourceLimit, round_binary64

src, start = inspect.getsourcelines(round_binary64)
alignment_line = start + next(i for i,line in enumerate(src) if 'if (n < (d<<e))' in line)
after_line = start + next(i for i,line in enumerate(src) if 'if e > 1023:' in line)
observations = []
for q in (Fraction(2**200), Fraction(1,2**200)):
    record = {'input':str(q), 'max_work_bits':8, 'alignment_line_reached':False,
              'post_alignment_line_reached':False}
    def observe(frame,event,arg):
        if frame.f_code is round_binary64.__code__ and event == 'line':
            if frame.f_lineno == alignment_line:
                n,d,e=(frame.f_locals[k] for k in ('n','d','e'))
                record.update(alignment_line_reached=True,
                              alignment_operand_bits=(d.bit_length()+e if e>=0 else n.bit_length()-e),
                              exponent=e)
            if frame.f_lineno == after_line:
                record['post_alignment_line_reached']=True
        return observe
    sys.settrace(observe)
    try:
        round_binary64(q,limits=Limits(max_work_bits=8))
        record['termination']='RETURNED'
    except ResourceLimit:
        record['termination']=('RESOURCE_LIMIT_AFTER_ALIGNMENT' if record['post_alignment_line_reached']
                               else 'RESOURCE_LIMIT_BEFORE_ALIGNMENT')
    finally:
        sys.settrace(None)
    observations.append(record)
print(json.dumps({'scope':'SYNTHETIC_ONLY_TWO_CASES', 'observations':observations},indent=2))
