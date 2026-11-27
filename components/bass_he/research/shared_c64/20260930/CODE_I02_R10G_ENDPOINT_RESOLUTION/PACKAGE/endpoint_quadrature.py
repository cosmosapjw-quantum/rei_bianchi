"""Bounded shared-vector GK15 endpoint refinement in q=asinh(rho/scale).

Only [0,B] is replaced; caller supplies immutable high/error for the other
intervals. Embedded errors and a successive-grid check are empirical diagnostics,
not certified continuum bounds. Query callbacks own geometry/source authority.
"""
from __future__ import annotations
import math
import numpy as np

X=np.array([.9914553711208126,.9491079123427585,.8648644233597691,
 .7415311855993945,.5860872354676911,.4058451513773972,.2077849550078985,0.])
WK=np.array([.02293532201052922,.06309209262997855,.1047900103222502,
 .1406532597155259,.1690047266392679,.1903505780647854,.2044329400752989,.2094821410847278])
WG=np.array([.1294849661688697,.2797053914892767,.3818300505051189,.4179591836734694])


def nodes(a,b):
    mid=.5*(a+b);half=.5*(b-a)
    return np.array([mid+sgn*half*x for x in X[:-1] for sgn in (-1,1)]+[mid])


def reduce(a,b,values):
    f=np.asarray(values,float)
    if f.ndim!=2 or len(f)!=15 or np.any(~np.isfinite(f)):
        raise ValueError('finite matrix of 15 quadrature values required')
    hi=WK[-1]*f[-1];lo=WG[-1]*f[-1]
    for j,w in enumerate(WK[:-1]):hi=hi+w*(f[2*j]+f[2*j+1])
    for w,j in zip(WG[:-1],(1,3,5)):lo=lo+w*(f[2*j]+f[2*j+1])
    return .5*(b-a)*hi,.5*(b-a)*abs(hi-lo)


def integrate_endpoint(evaluate,*,B:float,scale:float,tail,tail_error,
                       rtol:float=2e-4,atol:float=1e-10,max_leaves:int=8,checkpoint=None):
    """Replace first interval with shared q panels and bounded worst-first splitting.

    Start at 2 equal q panels. Stop after max_leaves (default8; <=210 evaluations).
    Acceptance requires BOTH current and preceding complete-grid estimates pass,
    and their component changes <=0.25 of current atol+rtol*abs(total).
    No clipping, alias-merging, extrapolation, tolerance relaxation or global
    refinement. Callback is evaluated batchwise; no endpoint rho=0 is requested.
    """
    par=np.asarray([B,scale,rtol,atol],float)
    if not np.all(np.isfinite(par)) or B<=0 or scale<=0 or rtol<=0 or atol<0:
        raise ValueError('invalid domain/tolerance')
    if type(max_leaves) is not int or not 2<=max_leaves<=8:raise ValueError('2<=max_leaves<=8')
    tail=np.asarray(tail,float);te=np.asarray(tail_error,float)
    if tail.ndim!=1 or te.shape!=tail.shape or not len(tail) or np.any(~np.isfinite(tail)) or np.any(~np.isfinite(te)) or np.any(te<0):
        raise ValueError('finite tail and nonnegative matched error required')
    end=float(np.arcsinh(B/scale));seen=set();evaluations=0;history=[]
    def make(specs):
        nonlocal evaluations
        qs=np.concatenate([nodes(a,b) for a,b in specs]);r=scale*np.sinh(qs)
        if np.any((r<=0)|(r>=B)):raise ValueError('ENDPOINT_QUERY_OUT_OF_RANGE')
        hx=[float(x).hex() for x in r]
        if len(set(hx))!=len(hx) or seen.intersection(hx):raise ValueError('QUERY_IDENTITY_COLLISION')
        seen.update(hx);values=np.asarray(evaluate(r),float);evaluations+=len(r)
        if values.shape!=(len(r),len(tail)) or np.any(~np.isfinite(values)) or np.min(values)<-2e-13:
            raise ValueError('finite nonnegative component integrands required')
        transformed=(math.pi*scale*scale*np.sinh(2*qs))[:,None]*values
        result=[]
        for k,(a,b) in enumerate(specs):
            h,e=reduce(a,b,transformed[15*k:15*k+15]);result.append({'a':a,'b':b,'high':h,'error':e})
        return result
    intervals=make([(0.,end/2),(end/2,end)]);previous=None
    while True:
        high=tail+sum((x['high'] for x in intervals),np.zeros_like(tail))
        error=te+sum((x['error'] for x in intervals),np.zeros_like(tail))
        tolerance=atol+rtol*abs(high)
        good=bool(np.all(error<=tolerance));change=None if previous is None else abs(high-previous[0])
        stable=bool(previous is not None and previous[1] and good and np.all(change<=.25*tolerance))
        history.append({'leaf_count':len(intervals),'evaluations':evaluations,'embedded_pass':good,
                        'max_normalized_embedded':float(np.max(error/np.maximum(tolerance,np.finfo(float).tiny))),
                        'max_normalized_change':None if change is None else float(np.max(change/np.maximum(tolerance,np.finfo(float).tiny)))})
        record={'status':'ENDPOINT_LOCAL_NUMERICAL_PASS' if stable else 'ENDPOINT_BUDGET_UNRESOLVED',
                'converged':stable,'stable_confirmation':stable,'integral':high.tolist(),
                'error_estimate':error.tolist(),'tolerance':tolerance.tolist(),
                'leaf_count':len(intervals),'evaluations':evaluations,'history':history.copy(),
                'q_intervals':[[x['a'].hex(),x['b'].hex()] for x in intervals],
                'new_query_hex':sorted(seen),'claim':'LOCAL_NUMERICAL_ESTIMATE_NOT_GLOBAL_OR_PHYSICAL_CERTIFICATE'}
        if checkpoint is not None:checkpoint(record)
        if stable or len(intervals)>=max_leaves:return record
        scores=[float(np.max(x['error']/np.maximum(tolerance,np.finfo(float).tiny))) for x in intervals]
        k=int(np.argmax(scores));old=intervals[k];mid=.5*(old['a']+old['b'])
        previous=(high.copy(),good)
        intervals[k:k+1]=make([(old['a'],mid),(mid,old['b'])])
