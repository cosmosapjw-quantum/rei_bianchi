"""RESEARCH-ONLY probes. No cloud mutation, scientific promotion or production API.

Common-contour equality requires analytic homotopy on the SAME spectral sheets.
The numerical code does not certify that topological hypothesis.
"""
from numbers import Integral
import math
import numpy as np

def _trace(R,gap,dR,rho):
    R=np.asarray(R,complex);gap=np.asarray(gap,complex);dR=np.asarray(dR,complex)
    if R.ndim!=1 or len(R)<9 or (len(R)-1)%2 or gap.shape!=R.shape or dR.shape!=R.shape:
        raise ValueError('equal-length one-dimensional even-panel traces required')
    if any(np.any(~np.isfinite(x)) for x in (R,gap,dR)) or not np.isfinite(rho) or rho<0:
        raise ValueError('finite trace and nonnegative rho required')
    if np.min(R.real)<=rho or np.any(R.imag<0):
        raise ValueError('research chart requires Re R > rho throughout upper-half-plane contour')
    n=len(R)-1;w=np.ones(n+1);w[1:-1:2]=4;w[2:-1:2]=2;w/=3*n
    return R,gap,dR,w

def action_from_trace(R,gap,dR,rho):
    """Complex integral on the supplied trace; do NOT take absolute value early."""
    R,gap,dR,w=_trace(R,gap,dR,rho)
    kernel=1/np.sqrt(1-(rho/R)**2)
    return complex(np.sum(w*gap*dR*kernel))

def moment_action(R,gap,dR,rho,degree):
    """Even-rho polynomial and DISCRETE-trace truncation bound.

    Excludes spectral, quadrature, homotopy, and floating-point error.
    """
    R,gap,dR,w=_trace(R,gap,dR,rho)
    if isinstance(degree,bool) or not isinstance(degree,Integral) or degree<0:
        raise ValueError('nonnegative integer degree required')
    y=(rho/R)**2;c=1.;power=np.ones_like(y);poly=power.copy()
    for n in range(1,degree+1):
        c*= (2*n-1)/(2*n);power*=y;poly+=c*power
    q=float(np.max(abs(y)));cnext=c*(2*degree+1)/(2*degree+2)
    bound=float(np.sum(w*abs(gap*dR)))*cnext*q**(degree+1)/(1-q)
    return complex(np.sum(w*gap*dR*poly)),bound

def fair_slots(demands,threads,memory,cpu_capacity,memory_capacity,weights=None):
    """Integer weighted dominant-share greedy heuristic, not exact continuous DRF.

    Capacities are residual reservable budgets, not physical device sizes.
    Values are declared/profiler inputs, NOT inferred host measurements.
    """
    demands=list(demands);threads=list(threads);memory=list(memory)
    n=len(demands);weights=[1.]*n if weights is None else list(weights)
    if n==0 or any(len(x)!=n for x in (threads,memory,weights)):
        raise ValueError('equal nonempty resource vectors required')
    if cpu_capacity<=0 or memory_capacity<=0:raise ValueError('positive capacities required')
    if any(isinstance(d,bool) or not isinstance(d,Integral) or d<0 for d in demands):raise ValueError('integer demands required')
    if any(not math.isfinite(x) or x<=0 for a in (threads,memory,weights) for x in a):raise ValueError('positive finite resource/weight values required')
    a=[0]*n;cpu=0.;mem=0.
    while True:
        eligible=[i for i in range(n) if a[i]<demands[i] and cpu+threads[i]<=cpu_capacity and mem+memory[i]<=memory_capacity]
        if not eligible:return a
        i=min(eligible,key=lambda i:(max(a[i]*threads[i]/cpu_capacity,a[i]*memory[i]/memory_capacity)/weights[i],i))
        a[i]+=1;cpu+=threads[i];mem+=memory[i]

def can_admit_memory(current_ancestor,pending_not_yet_charged,new_reservation,hard_target,buffer):
    vals=[current_ancestor,pending_not_yet_charged,new_reservation,hard_target,buffer]
    if any(not math.isfinite(x) or x<0 for x in vals):raise ValueError('finite nonnegative budgets required')
    return current_ancestor+pending_not_yet_charged+new_reservation+buffer<=hard_target

def event_matrix(p,sink=False):
    if not np.isfinite(p) or not 0<=p<=1:raise ValueError('probability outside unit interval')
    return np.array([[1-p,0 if sink else p],[p,1 if sink else 1-p]],float)
