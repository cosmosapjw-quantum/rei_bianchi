"""Exact audit of finite binary64 state/event records, not of continuous flow.

Each Python float is converted by its exact as_integer_ratio, never its decimal
appearance. Event/source quadrature and native arithmetic errors remain outside
this finite-record identity. Input callers own source and time identity checks.
"""
from fractions import Fraction
import math
from collections.abc import Sequence

def number(x: float) -> Fraction:
    if not isinstance(x,(int,float)) or not math.isfinite(x) or x < 0:
        raise ValueError('expected finite nonnegative binary64 record')
    return Fraction(float(x))

def ledger(states: Sequence[float], events: Sequence[Sequence[float]]) -> dict:
    if not states or len(states) != len(events)+1:
        raise ValueError('one event row required for each state transition')
    p=[number(x) for x in states]
    a=[sum((number(x) for x in row),Fraction()) for row in events]
    defects=[p[i]-p[i+1]-a[i] for i in range(len(a))]
    defect=p[0]-p[-1]-sum(a,Fraction())
    if defect != sum(defects,Fraction()):
        raise AssertionError('exact telescoping identity violated')
    return {'defect':defect,'sum_abs':sum(map(abs,defects),Fraction()),
            'defects':defects,'absorbed':sum(a,Fraction()),'initial':p[0],
            'final':p[-1],'positive':sum(x>0 for x in defects),
            'negative':sum(x<0 for x in defects)}
