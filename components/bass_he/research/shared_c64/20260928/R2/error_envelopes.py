"""Research-only fixed-trace bounds and synthetic stochastic identities.

Bounds are for the supplied finite Simpson sum in exact arithmetic. They do not
include spectral, quadrature, homotopy or floating-point errors. No production
BASS_HE function or numerical tolerance is changed.
"""
from numbers import Integral
import math
import numpy as np


def _real(x, name, positive=False):
    if isinstance(x, (bool, np.bool_)) or not np.isscalar(x) or np.iscomplexobj(x):
        raise ValueError(f'{name} must be real')
    x=float(x)
    if not math.isfinite(x) or x<0 or (positive and x==0):
        raise ValueError(f'{name} must be finite and nonnegative (positive if requested)')
    return x


def _trace(R, gap, dR, rho):
    rho=_real(rho,'rho')
    R=np.asarray(R,complex);gap=np.asarray(gap,complex);dR=np.asarray(dR,complex)
    if R.ndim!=1 or len(R)<9 or (len(R)-1)%2 or R.shape!=gap.shape or R.shape!=dR.shape:
        raise ValueError('equal length even-panel one-dimensional trace required')
    if any(np.any(~np.isfinite(x)) for x in (R,gap,dR)):
        raise ValueError('finite trace required')
    if np.min(R.real)<=rho or np.any(R.imag<0):
        raise ValueError('upper-half-plane chart requires Re(R)>rho')
    n=len(R)-1;w=np.ones(n+1);w[1:-1:2]=4.;w[2:-1:2]=2.;w/=3*n
    return R,gap,dR,w,rho


def action_jet(R, gap, dR, rho):
    """Return complex A, dA/drho, d2A/drho2 of the SAME finite trace sum."""
    R,gap,dR,w,rho=_trace(R,gap,dR,rho)
    z=(rho/R)**2;u=1-z;base=w*gap*dR
    k0=1/np.sqrt(u)
    k1=(rho/R**2)*u**(-1.5)
    k2=(1+2*z)/(R**2*u**2.5)
    return tuple(complex(np.sum(base*k)) for k in (k0,k1,k2))


def interpolation_bound(R, gap, dR, lo, hi):
    """Uniform complex linear-interpolation error on [lo,hi], trace-only."""
    lo=_real(lo,'lo');hi=_real(hi,'hi')
    if hi<lo:raise ValueError('ordered interval required')
    R,gap,dR,w,_=_trace(R,gap,dR,hi)
    rmin=float(np.min(abs(R)));q=(hi/rmin)**2
    L=float(np.sum(w*abs(gap*dR)))
    curvature=L/rmin**2*(1+2*q)/(1-q)**2.5
    return float((hi-lo)**2*curvature/8)


def gap_error_bound(R, dR, errors, rho_max):
    """Bound delta A for pointwise gap errors on an UNCHANGED contour."""
    errors=np.asarray(errors,float)
    R,_,dR,w,rho_max=_trace(R,errors,dR,rho_max)
    if np.any(errors<0):raise ValueError('nonnegative gap-error radii required')
    q=(rho_max/float(np.min(abs(R))))**2
    return float(np.sum(w*abs(dR)*errors)/np.sqrt(1-q))


def certified_mesh(R, gap, dR, rho_max, absolute_tolerance, max_intervals=4096):
    """Bisection until every trace-only linear-interpolation bound is small.

    This is not a rigorous floating-point interval implementation. The name
    refers only to the analytical finite-trace bound, not physical certification.
    """
    rho_max=_real(rho_max,'rho_max',True)
    tol=_real(absolute_tolerance,'absolute_tolerance',True)
    if isinstance(max_intervals,bool) or not isinstance(max_intervals,Integral) or max_intervals<1:
        raise ValueError('positive integer max_intervals required')
    _trace(R,gap,dR,rho_max)
    todo=[(0.,rho_max)];leaves=[]
    while todo:
        lo,hi=todo.pop();b=interpolation_bound(R,gap,dR,lo,hi)
        if b<=tol:leaves.append((lo,hi,b))
        else:
            if len(leaves)+len(todo)+2>max_intervals:
                raise RuntimeError('interpolation interval budget exhausted')
            mid=lo+(hi-lo)/2
            if not lo<mid<hi:raise RuntimeError('floating-point mesh stagnation')
            todo.extend([(mid,hi),(lo,mid)])
    leaves.sort();nodes=[leaves[0][0]]+[x[1] for x in leaves]
    values=[action_jet(R,gap,dR,r)[0] for r in nodes]
    return dict(nodes=nodes,values=values,interval_bounds=[x[2] for x in leaves],
                bound_scope='FIXED_DISCRETE_TRACE_ONLY_NOT_TOTAL_ERROR')


def _event(dim,p,event):
    i,j,sink=event
    if any(isinstance(k,bool) or not isinstance(k,Integral) for k in (i,j)) or not(0<=i<dim and 0<=j<dim) or i==j:
        raise ValueError('distinct in-range integer indices required')
    if not isinstance(sink,(bool,np.bool_)):raise ValueError('boolean sink required')
    T=np.eye(dim);T[i,i]=1-p;T[j,i]=p
    if not sink:T[i,j]=p;T[j,j]=1-p
    return T


def hybrid_telescope(probabilities, approximate, events, initial, observable):
    """Exact hybrid telescope: original downstream, approximate upstream.

    Educational dense reference, not a production transport optimization. Event
    coefficients are stochastic probabilities; no atomic rate is supplied.
    """
    p=np.asarray(probabilities,float);q=np.asarray(approximate,float)
    y=np.asarray(initial,float);w=np.asarray(observable,float)
    if p.ndim!=1 or p.shape!=q.shape or len(p)!=len(events) or y.ndim!=1 or w.shape!=y.shape or len(y)<2:
        raise ValueError('compatible nonempty state/event vectors required')
    if any(np.any(~np.isfinite(a)) for a in (p,q,y,w)) or np.any((p<0)|(p>1)) or np.any((q<0)|(q>1)):
        raise ValueError('finite stochastic probabilities required')
    if np.any(y<0) or abs(float(y.sum())-1)>1e-12 or np.any((w<0)|(w>1)):
        raise ValueError('normalized initial probability and bounded observable required')
    Ts=[_event(len(y),v,e) for v,e in zip(p,events)]
    Qs=[_event(len(y),v,e) for v,e in zip(q,events)]
    adj=[None]*len(p);row=w.copy()
    for e in range(len(p)-1,-1,-1):adj[e]=row.copy();row=row@Ts[e]
    ya=y.copy();contributions=[]
    for e,(i,j,sink) in enumerate(events):
        local=ya[i] if sink else ya[i]-ya[j]
        contributions.append(float((p[e]-q[e])*(adj[e][j]-adj[e][i])*local))
        ya=Qs[e]@ya
    return dict(direct_difference=float(row@y-w@ya),signed_contributions=contributions,
                weighted_bound=float(np.sum(abs(np.array(contributions)))),
                global_bound=float(np.sum(abs(p-q))))
