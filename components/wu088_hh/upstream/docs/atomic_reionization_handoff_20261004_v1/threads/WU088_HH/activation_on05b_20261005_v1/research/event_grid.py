"""Immutable fixed-birth event union. No approximate event merging or new source."""
from __future__ import annotations
import math,bisect

def make_plan(end:float,dt:float,events:list[float],rate:float)->dict:
    if any(isinstance(v,bool) or not math.isfinite(v) for v in (end,dt,rate)) or min(end,dt)<=0 or rate<0:
        raise ValueError('EVENT_GRID_DOMAIN')
    if end/dt!=int(end/dt):raise ValueError('INTEGER_MACRO_GRID_REQUIRED')
    if any(not math.isfinite(v) for v in events):raise ValueError('FINITE_EVENT_REQUIRED')
    half=dt/2;births=[i*half for i in range(1,int(2*end/dt)+1)]
    base=[0.]+births;points=sorted(set(base+[float(e) for e in events if 0.<e<end]))
    # Any insertion marks the containing original accepted half, including its
    # last piece. This lets a finite arithmetic reserve be assigned explicitly.
    extra={bisect.bisect_left(base,e)-1 for e in points if e not in set(base)}
    segments=[]
    for a,b in zip(points,points[1:]):
        parent=bisect.bisect_right(base,a)-1
        segments.append({'t0':a,'t1':b,'birth_n':rate*half if b in set(births) else 0.,
                         'affected':parent in extra,'original_half':parent,'macro':parent//2})
    return {'end':end,'base_dt':dt,'points':points,'segments':segments,
            'affected_count':sum(s['affected'] for s in segments),'birth_times':births,
            'source_per_birth':rate*half,'fuzzy_event_merge':False}
