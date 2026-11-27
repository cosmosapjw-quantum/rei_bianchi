"""Sparse stochastic propagation and finite reaction observables, not elastic scattering."""
from __future__ import annotations
import numpy as np


def transition_probabilities(delta,velocities,*,exponent_factor):
    d=np.asarray(delta,float);v=np.asarray(velocities,float)
    if exponent_factor not in (1,2):raise ValueError('explicit exponent factor 1 or 2 required')
    if np.any(~np.isfinite(d)) or np.any(d<0) or np.any(~np.isfinite(v)) or np.any(v<=0):
        raise ValueError('finite delta>=0 and velocity>0 required')
    return np.exp(-exponent_factor*d/v[...,None])


def apply_eq50(probabilities,events,P_rot,initial):
    """Exact Eq50 column action. Each event is zero-based (i,j,absorbing_j).

    Event updates cost O(batch*K*columns); the retained dense P_rot action costs
    O(batch*d^2*columns), versus constructing dense O(batch*K*d^3) products.
    No Markov/coherence approximation beyond the chosen source probability model.
    """
    p=np.asarray(probabilities,float);rot=np.asarray(P_rot,float);init=np.asarray(initial,float)
    if p.ndim!=2 or p.shape[1]!=len(events) or rot.ndim!=3 or rot.shape[0]!=p.shape[0]:raise ValueError('batch shape mismatch')
    dim=rot.shape[-1]
    if rot.shape[1]!=dim or init.ndim!=2 or init.shape[0]!=dim:raise ValueError('matrix shape mismatch')
    if np.any(~np.isfinite(p)) or np.any(p<0) or np.any(p>1) or np.any(~np.isfinite(rot)) or np.any(~np.isfinite(init)):raise ValueError('invalid probabilities')
    if np.any(rot<-1e-13) or np.max(abs(rot.sum(1)-1))>2e-10:raise ValueError('P_rot must be column stochastic')
    y=np.broadcast_to(init,(len(p),*init.shape)).copy()
    def update(k):
        i,j,sink=events[k]
        if not(0<=i<dim and 0<=j<dim and i!=j):raise ValueError('event index out of range')
        q=p[:,k,None];yi=y[:,i].copy();yj=y[:,j].copy()
        if sink:
            y[:,i]=(1-q)*yi;y[:,j]=yj+q*yi
        else:
            y[:,i]=(1-q)*yi+q*yj;y[:,j]=(1-q)*yj+q*yi
    for k in reversed(range(len(events))):update(k)
    y=rot@y
    for k in range(len(events)):update(k)
    return y


def integrate_transitions(rho,P):
    """Finite sampled off-diagonal area and loss; atomic length squared.

    Diagonal survival probabilities approach 1 and do not define elastic cross
    sections here. Loss is summed off-diagonals to avoid catastrophic 1-Pii
    cancellation. An explicit density/amplitude model is needed for elastic data.
    """
    r=np.asarray(rho,float);p=np.array(P,dtype=float,copy=True)
    if r.ndim!=1 or len(r)<2 or np.any(~np.isfinite(r)) or r[0]<0 or np.any(np.diff(r)<=0):raise ValueError('ordered finite rho grid required')
    if p.ndim!=3 or p.shape[0]!=len(r) or p.shape[-1]!=p.shape[-2] or np.any(~np.isfinite(p)):raise ValueError('finite square matrices required')
    if np.any(p<-1e-13) or np.max(abs(p.sum(1)-1))>2e-10:raise ValueError('matrices must be column stochastic')
    idx=np.arange(p.shape[-1]);p[:,idx,idx]=0
    areas=2*np.pi*np.trapezoid(p*r[:,None,None],r,axis=0)
    return dict(offdiagonal_area_a0sq=areas,reaction_loss_area_a0sq=areas.sum(0),
                elastic_cross_section_available=False,tail_certified=False,
                claim='SAMPLED_FINITE_REACTION_OBSERVABLE_NOT_PHYSICAL_PRODUCTION')


def channel_partition(population,labels):
    p=np.asarray(population,float)
    if p.ndim!=1 or len(p)!=len(labels) or np.any(~np.isfinite(p)) or np.any(p<0):raise ValueError('invalid population')
    allowed={'bound','sink'}
    if any(x.get('kind') not in allowed for x in labels):raise ValueError('disjoint bound/sink labels required')
    if any(x['kind']=='sink' and x.get('n') is not None for x in labels):raise ValueError('sink cannot also be a bound shell')
    return dict(bound_total=float(sum(x for x,l in zip(p,labels) if l['kind']=='bound')),
                sink_total=float(sum(x for x,l in zip(p,labels) if l['kind']=='sink')))
