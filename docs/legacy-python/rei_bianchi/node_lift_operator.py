"""Convex projection primitives for the R2B fixed-node lift.

All operators preserve externally locked totals.  They never infer cloud mass
from opacity and never clip an infeasible target into the feasible set.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import math
import numpy as np
from scipy.optimize import brentq, least_squares


def _as_1d(a: Any, name: str) -> np.ndarray:
    x=np.asarray(a,dtype=float)
    if x.ndim != 1 or not np.all(np.isfinite(x)):
        raise ValueError(f"{name} must be a finite one-dimensional array")
    return x


def positive_mass_projection(prior: Any, total: float) -> np.ndarray:
    """Return the I-projection onto ``sum(x)=total`` for a positive measure."""
    p=_as_1d(prior,"prior")
    total=float(total)
    if not math.isfinite(total) or total < 0.0:
        raise ValueError("total must be finite and nonnegative")
    if np.any(p < 0.0):
        raise ValueError("prior must be nonnegative")
    if total == 0.0:
        return np.zeros_like(p)
    s=float(p.sum())
    if s <= 0.0:
        raise ValueError("INFEASIBLE_ZERO_PRIOR_SUPPORT")
    return p*(total/s)


def bernoulli_kl_mean_projection(
    prior_x: Any, weights: Any, target_mean: float, *, tol: float=1e-13
) -> tuple[np.ndarray, dict[str, Any]]:
    """Binary relative-entropy projection onto a weighted mean constraint."""
    p=_as_1d(prior_x,"prior_x")
    w=_as_1d(weights,"weights")
    if p.shape != w.shape:
        raise ValueError("prior_x and weights must have identical shape")
    if np.any(w < 0.0) or float(w.sum()) <= 0.0:
        raise ValueError("weights must be nonnegative with positive sum")
    if np.any((p < 0.0)|(p > 1.0)):
        raise ValueError("Bernoulli prior must lie in [0,1]")
    target=float(target_mean)
    if not (0.0 <= target <= 1.0):
        raise ValueError("target_mean must lie in [0,1]")
    wn=w/float(w.sum())
    current=float(wn@p)
    if abs(current-target) <= tol:
        x=p.copy(); dual=0.0
    elif target == 0.0:
        x=np.zeros_like(p); dual=math.inf
    elif target == 1.0:
        x=np.ones_like(p); dual=-math.inf
    else:
        eps=np.finfo(float).eps
        pc=np.clip(p,eps,1.0-eps)
        logits=np.log(pc)-np.log1p(-pc)
        def mean_at(dual: float) -> float:
            y=logits-dual
            # stable sigmoid
            x=np.empty_like(y)
            pos=y>=0
            x[pos]=1.0/(1.0+np.exp(-y[pos]))
            ey=np.exp(y[~pos]); x[~pos]=ey/(1.0+ey)
            return float(wn@x)
        lo,hi=-1.0,1.0
        while mean_at(lo) < target: lo*=2.0
        while mean_at(hi) > target: hi*=2.0
        dual=float(brentq(lambda a:mean_at(a)-target,lo,hi,xtol=5e-15,rtol=4*np.finfo(float).eps,maxiter=200))
        y=logits-dual
        x=np.empty_like(y); pos=y>=0
        x[pos]=1.0/(1.0+np.exp(-y[pos])); ey=np.exp(y[~pos]); x[~pos]=ey/(1.0+ey)
    # binary KL; use limiting convention 0 log 0 = 0
    eps=np.finfo(float).tiny
    pc=np.clip(p,eps,1.0-eps); xc=np.clip(x,eps,1.0-eps)
    kl=float(np.sum(wn*(xc*np.log(xc/pc)+(1.0-xc)*np.log((1.0-xc)/(1.0-pc)))))
    residual=float(wn@x-target)
    return x,{'dual':dual,'target_mean':target,'achieved_mean':float(wn@x),'mean_residual':residual,'kl':max(0.0,kl) if kl>-1e-14 else kl}


def capacity_constrained_group_projection(
    prior_matrix: Any,
    group_totals: Any,
    row_capacity: Any,
    *,
    tol: float=1e-11,
    max_nfev: int=2000,
) -> tuple[np.ndarray, dict[str, Any]]:
    """I-project a nonnegative node×group prior onto column sums and row caps.

    KKT form: x_ig=q_ig exp(-mu_g-lambda_i), with
    lambda_i=max(0, log(sum_g q_ig exp(-mu_g)/c_i)).
    """
    prior=np.asarray(prior_matrix,dtype=float)
    totals=_as_1d(group_totals,"group_totals")
    caps=_as_1d(row_capacity,"row_capacity")
    if prior.ndim != 2 or prior.shape != (caps.size,totals.size):
        raise ValueError("prior_matrix shape must be (row_capacity.size, group_totals.size)")
    if not np.all(np.isfinite(prior)) or np.any(prior < 0.0):
        raise ValueError("prior_matrix must be finite and nonnegative")
    if np.any(totals < 0.0) or np.any(caps < 0.0):
        raise ValueError("totals and capacities must be nonnegative")
    total_required=float(totals.sum()); total_capacity=float(caps.sum())
    scale=max(1.0,total_required,total_capacity)
    if total_capacity + tol*scale < total_required:
        deficit=total_required-total_capacity
        raise ValueError(f"INFEASIBLE_TOTAL_CAPACITY required={total_required:.17e} capacity={total_capacity:.17e} deficit={deficit:.17e}")
    if total_required == 0.0:
        x=np.zeros_like(prior)
        cert={'status':'PASS_ZERO','mu':[0.0]*totals.size,'lambda':[0.0]*caps.size,'active_row_count':0,
              'max_column_relative_residual':0.0,'max_capacity_violation':0.0,
              'max_stationarity_residual':0.0,'max_complementarity_residual':0.0,'generalized_kl':0.0}
        return x,cert
    col_prior=prior.sum(axis=0)
    for g,t in enumerate(totals):
        if t>0.0 and col_prior[g]<=0.0:
            raise ValueError(f"INFEASIBLE_ZERO_GROUP_SUPPORT group={g}")
    # Column scaling changes KL only by a constant on the fixed-column set.
    q=np.zeros_like(prior)
    for g,t in enumerate(totals):
        if t>0.0: q[:,g]=prior[:,g]*(t/col_prior[g])
    S=total_required
    qn=q/S; tn=totals/S; cn=caps/S
    if np.all(qn.sum(axis=1) <= cn + tol):
        mu=np.zeros(totals.size); lamb=np.zeros(caps.size); xn=qn.copy(); solver_status='IDENTITY_FEASIBLE'
    else:
        def eval_mu(mu: np.ndarray):
            # Values encountered here stay moderate because q is column-normalized.
            u=qn*np.exp(np.clip(-mu,-700.0,700.0))[None,:]
            rows=u.sum(axis=1)
            lamb=np.zeros_like(rows)
            positive=(cn>0.0)&(rows>cn)
            lamb[positive]=np.log(rows[positive]/cn[positive])
            zero=(cn==0.0)&(rows>0.0)
            lamb[zero]=745.0
            x=u*np.exp(-lamb)[:,None]
            return x,lamb
        def residual(mu: np.ndarray):
            x,_=eval_mu(mu)
            return (x.sum(axis=0)-tn)/np.maximum(tn,1e-300)
        sol=least_squares(residual,np.zeros(totals.size),xtol=1e-14,ftol=1e-14,gtol=1e-14,max_nfev=max_nfev)
        mu=np.asarray(sol.x); xn,lamb=eval_mu(mu); solver_status=f"LEAST_SQUARES_{sol.status}"
        if (not sol.success) or float(np.max(np.abs(residual(mu))))>tol:
            raise ValueError(f"INFEASIBLE_OR_DUAL_SOLVER_FAILURE status={sol.status} residual={np.max(np.abs(residual(mu))):.3e}")
    x=xn*S
    row=x.sum(axis=1); col=x.sum(axis=0)
    col_rel=np.abs(col-totals)/np.maximum(np.abs(totals),1.0)
    cap_violation=np.maximum(row-caps,0.0)
    # stationarity relative to column-rescaled q
    mask=(x>0.0)&(q>0.0)
    st=np.zeros_like(x)
    if np.any(mask):
        st[mask]=np.log(x[mask]/q[mask]) + np.broadcast_to(mu,(caps.size,totals.size))[mask] + np.broadcast_to(lamb[:,None],x.shape)[mask]
    comp=np.asarray(lamb)*(caps-row)/S
    with np.errstate(divide='ignore',invalid='ignore'):
        term=np.where(x>0.0,x*np.log(x/np.where(q>0.0,q,1.0)),0.0)-x+q
    if np.any((x>0.0)&(q==0.0)): gkl=math.inf
    else: gkl=float(np.sum(term))
    cert={
      'status':'PASS','solver_status':solver_status,'mu':mu.tolist(),'lambda':np.asarray(lamb).tolist(),
      'active_row_count':int(np.count_nonzero(np.asarray(lamb)>1e-12)),
      'max_column_relative_residual':float(np.max(col_rel)) if col_rel.size else 0.0,
      'max_capacity_violation':float(np.max(cap_violation)) if cap_violation.size else 0.0,
      'max_stationarity_residual':float(np.max(np.abs(st[mask]))) if np.any(mask) else 0.0,
      'max_complementarity_residual':float(np.max(np.abs(comp))) if comp.size else 0.0,
      'generalized_kl':gkl,'total_required':total_required,'total_capacity':total_capacity,
      'minimum_capacity_slack':float(np.min(caps-row)) if caps.size else 0.0,
    }
    return x,cert


def signed_transfer_lift(rate: float, conditional_mass_prior: Any) -> tuple[np.ndarray,np.ndarray,np.ndarray]:
    """Lift a signed scalar rate as nonnegative positive/negative parts."""
    p=_as_1d(conditional_mass_prior,"conditional_mass_prior")
    if np.any(p<0.0) or float(p.sum())<=0.0:
        raise ValueError("conditional_mass_prior must be nonnegative with positive sum")
    rate=float(rate)
    if not math.isfinite(rate): raise ValueError("rate must be finite")
    w=p/float(p.sum())
    pos=w*max(rate,0.0); neg=w*max(-rate,0.0)
    return pos,neg,pos-neg
