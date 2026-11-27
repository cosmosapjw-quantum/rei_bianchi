"""Finite observer differences on exactly matched output clocks.

Input floats are stored binary64 values. No true-error enclosure is inferred.
"""
import math
ABS=1e-22
REL=1e-6
def ratio(a,b):
 if not all(math.isfinite(x) and x>=0 for x in (a,b)):raise ValueError('NONNEGATIVE_FINITE_RATE_REQUIRED')
 return abs(a-b)/(ABS+REL*max(abs(a),abs(b)))
def align(a,b):
 if len(a)<2 or len(b)<len(a):raise ValueError('INCOMPLETE_SERIES')
 for s in (a,b):
  xs=[r['s'] for r in s]
  if any(not math.isfinite(x) for x in xs) or any(v<=u for u,v in zip(xs,xs[1:])):raise ValueError('CLOCK')
 if a[0]['s']!=b[0]['s'] or a[-1]['s']!=b[-1]['s']:raise ValueError('DIFFERENT_TIME_WINDOWS')
 pos={r['s']:j for j,r in enumerate(b)}
 if any(r['s'] not in pos for r in a):raise ValueError('EXACT_COMMON_CLOCK_REQUIRED')
 return [(i,pos[r['s']]) for i,r in enumerate(a)]
def budget(ratios):
 if len(ratios)!=3 or any(not math.isfinite(x) or x<0 for x in ratios):raise ValueError('THREE_FINITE_NONNEGATIVE_AXES_REQUIRED')
 return sum(ratios)<=1.
def check_rows(rows,n):
 if len(rows)!=n+1 or [r['step'] for r in rows]!=list(range(n+1)):raise ValueError('INCOMPLETE_OR_WRONG_INDEX')
 if any(not math.isfinite(r['s']) for r in rows) or any(b['s']<=a['s'] for a,b in zip(rows,rows[1:])):raise ValueError('INVALID_CLOCK')
