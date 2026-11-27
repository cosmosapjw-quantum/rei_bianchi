"""Scoped adaptive Eq. (54) helpers for the audited Nmax=3 research lane.

This module keeps source-convention alternatives explicit.  It integrates only
finite off-diagonal indexed-state probabilities.  It does not define an elastic
cross section, complete branch enumeration, or a production physical channel map.
"""
from __future__ import annotations
import numpy as np
from arseny_reimpl.eq50_scoped import ordered_scoped_branches,branch_state_indices
from arseny_reimpl.cross_section import projectile_velocity_au
from arseny_reimpl.rotational import s_sigma_boundary
from arseny_reimpl.state_index import state_index
from .rotation import full_rotation_batch
from .transport import apply_eq50

BRANCHES=ordered_scoped_branches()


class DeltaSurrogate:
    """Local cubic interpolation of geometry-only Delta in u=rho^2.

    Anchors must cover rho=0 through the intended support endpoint.  This is a
    numerical accelerator, not an analytic error bound; callers must validate
    it against exact held-out geometry before using it for scientific claims.
    """
    def __init__(self,anchors):
        self._data={}
        for name,rows in anchors.items():
            rows=list(rows)
            if len(rows)<4:raise ValueError('at least four anchors required per branch')
            rho=np.asarray([x[0] for x in rows],float);delta=np.asarray([x[1] for x in rows],float)
            order=np.argsort(rho);rho=rho[order];delta=delta[order]
            if np.any(~np.isfinite(rho)) or np.any(~np.isfinite(delta)) or np.any(rho<0) or np.any(delta<0):
                raise ValueError('finite nonnegative rho/delta anchors required')
            if rho[0]!=0 or np.any(np.diff(rho)<=0):raise ValueError('anchors must uniquely cover from rho=0')
            self._data[str(name)]=(rho*rho,delta,float(rho[-1]))
    @staticmethod
    def _one(u,v,x):
        i=int(np.searchsorted(u,x));lo=max(0,min(i-2,len(u)-4));idx=np.arange(lo,lo+4)
        xx=u[idx];center=float(xx.mean());scale=max(float(np.ptp(xx)),np.finfo(float).tiny)
        coef=np.polynomial.polynomial.polyfit((xx-center)/scale,v[idx],3)
        return float(np.polynomial.polynomial.polyval((x-center)/scale,coef))
    def evaluate(self,name,rhos):
        try:u,v,rmax=self._data[str(name)]
        except KeyError as exc:raise KeyError(f'unknown surrogate branch {name}') from exc
        r=np.asarray(rhos,float)
        if np.any(~np.isfinite(r)) or np.any(r<0):raise ValueError('finite rho>=0 required')
        if np.any(r>rmax):raise ValueError('surrogate coverage exceeded')
        out=np.array([self._one(u,v,float(x*x)) for x in r.ravel()]).reshape(r.shape)
        if np.any(~np.isfinite(out)) or np.any(out<0):raise ValueError('nonphysical surrogate prediction')
        return out
INITIAL_INDEX_ZERO_BASED=2  # united-atom 2p sigma, paper Eq.49 j=3
NMAX=3
DIM=state_index(NMAX,NMAX-1,NMAX-1)


def surrogate_geometry_mapping(surrogate,rhos):
    r=np.asarray(rhos,float)
    if r.ndim!=1 or np.any(~np.isfinite(r)) or np.any(r<0):
        raise ValueError('finite one-dimensional rho>=0 required')
    out={}
    for b in BRANCHES:
        mask=r<=b.support_cutoff
        if not np.any(mask):continue
        vals=surrogate.evaluate(b.name,r[mask])
        for rho,delta in zip(r[mask],vals):
            out[(b.name,float(rho))]={'delta':float(delta),'source':'LOCAL_CUBIC_SURROGATE_IN_U_RHO2'}
    return out


def validate_delta_surrogate(surrogate,exact_rows):
    per={};count=0;mx=0.0
    for row in exact_rows:
        name=str(row['branch']);rho=float(row['rho']);exact=float(row['delta'])
        pred=float(np.asarray(surrogate.evaluate(name,[rho]))[0])
        rel=abs(pred-exact)/max(abs(exact),np.finfo(float).tiny)
        per.setdefault(name,[]).append(dict(rho=rho,exact_delta=exact,surrogate_delta=pred,relative_error=rel))
        mx=max(mx,rel);count+=1
    if count==0:raise ValueError('at least one exact validation row required')
    return dict(count=count,max_relative_error=float(mx),per_branch=per,
                error_claim='HELD_OUT_NUMERICAL_VALIDATION_NOT_GLOBAL_BOUND')


def support_cutoffs(*,rotation_cut_scale=1.0):
    if not np.isfinite(rotation_cut_scale) or rotation_cut_scale<=0:
        raise ValueError('finite positive rotation_cut_scale required')
    cuts=[0.,s_sigma_boundary(1)*rotation_cut_scale,s_sigma_boundary(2)*rotation_cut_scale]
    cuts.extend(b.support_cutoff for b in BRANCHES)
    return sorted(set(float(x) for x in cuts))


def component_labels(energies,exponent_factors=(1,2),*,initial_index=INITIAL_INDEX_ZERO_BASED):
    E=np.asarray(energies,float)
    if E.ndim!=1 or len(E)==0 or np.any(~np.isfinite(E)) or np.any(E<=0):
        raise ValueError('positive finite energies required')
    labels=[]
    for factor in exponent_factors:
        if factor not in (1,2):raise ValueError('explicit exponent factor 1 or 2 required')
        for energy in E:
            for j in range(DIM):
                if j==initial_index:continue
                labels.append(dict(exponent_factor=int(factor),energy_keV_u=float(energy),final_state_index=j+1))
    return labels


def assemble_initial_column_batch(geometry,energies,rhos,*,exponent_factors=(1,2),
                                  rotation_steps=32,rotation_cut_scale=1.0):
    """Assemble both printed exponent lanes from shared geometry.

    Returns probabilities with axes (rho, exponent_factor, energy, final_state)
    plus a flattened off-diagonal component vector for adaptive Eq54 integration.
    """
    E=np.asarray(energies,float);r=np.asarray(rhos,float)
    if E.ndim!=1 or len(E)==0 or np.any(~np.isfinite(E)) or np.any(E<=0):
        raise ValueError('positive finite energies required')
    if r.ndim!=1 or len(r)==0 or np.any(~np.isfinite(r)) or np.any(r<0):
        raise ValueError('finite rho>=0 required')
    factors=tuple(exponent_factors)
    if not factors or any(x not in (1,2) for x in factors):raise ValueError('explicit exponent factors 1/2 required')
    nr=len(r);ne=len(E);nb=len(BRANCHES)
    delta=np.zeros((nr,nb));active=np.zeros((nr,nb),bool)
    for ir,rho in enumerate(r):
        for k,b in enumerate(BRANCHES):
            if rho<=b.support_cutoff:
                active[ir,k]=True
                try:rec=geometry[(b.name,float(rho))]
                except KeyError as exc:raise KeyError(f'missing active geometry {b.name} rho={rho!r}') from exc
                d=float(rec['delta'])
                if not np.isfinite(d) or d<0:raise ValueError('finite nonnegative delta required')
                delta[ir,k]=d
    batchE=np.tile(E,nr);batchR=np.repeat(r,ne)
    prot=full_rotation_batch(NMAX,batchE,batchR,steps=rotation_steps,R_cut_scale=rotation_cut_scale)
    velocities=np.array([projectile_velocity_au(x) for x in batchE])
    d=np.repeat(delta,ne,axis=0);mask=np.repeat(active,ne,axis=0)
    events=[]
    for b in BRANCHES:
        i,j=branch_state_indices(b);events.append((i-1,j-1,b.state_b[0]==NMAX))
    initial=np.eye(DIM)[:,[INITIAL_INDEX_ZERO_BASED]]
    lanes=[]
    for factor in factors:
        p=np.where(mask,np.exp(-factor*d/velocities[:,None]),0.)
        y=apply_eq50(p,events,prot,initial)[...,0].reshape(nr,ne,DIM)
        lanes.append(y)
    probs=np.stack(lanes,axis=1)
    if np.max(np.abs(probs.sum(-1)-1))>3e-10 or np.min(probs)<-2e-13:
        raise ArithmeticError('initial-column stochasticity/range failure')
    keep=np.arange(DIM)!=INITIAL_INDEX_ZERO_BASED
    components=probs[...,keep].reshape(nr,-1)
    return dict(probabilities=probs,components=components,
                labels=component_labels(E,factors),energies_keV_u=E,
                exponent_factors=factors,initial_state_index=INITIAL_INDEX_ZERO_BASED+1,
                rotation_cut_scale=float(rotation_cut_scale))


def decode_component_integral(vector,energies,exponent_factors=(1,2),*,initial_index=INITIAL_INDEX_ZERO_BASED):
    vec=np.asarray(vector,float);labels=component_labels(energies,exponent_factors,initial_index=initial_index)
    if vec.ndim!=1 or len(vec)!=len(labels) or np.any(~np.isfinite(vec)):
        raise ValueError('component integral shape mismatch')
    out={str(int(f)):{str(float(e)):dict(indexed_transition_areas_a0sq={}) for e in np.asarray(energies,float)}
         for f in exponent_factors}
    for value,label in zip(vec,labels):
        lane=out[str(label['exponent_factor'])][str(label['energy_keV_u'])]
        lane['indexed_transition_areas_a0sq'][str(label['final_state_index'])]=float(value)
    for factor in out.values():
        for lane in factor.values():
            lane['reaction_loss_area_a0sq']=float(sum(lane['indexed_transition_areas_a0sq'].values()))
    return out
