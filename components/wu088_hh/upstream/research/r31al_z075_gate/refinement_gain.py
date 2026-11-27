from __future__ import annotations
import math
from numbers import Real
import numpy as np

DEFAULT_TOL = 1e-10

def _positive(x, name):
    if isinstance(x, (bool, np.bool_)) or not isinstance(x, Real):
        raise ValueError(name+" must be positive finite real")
    x=float(x)
    if not math.isfinite(x) or x<=0:
        raise ValueError(name+" must be positive finite real")
    return x

def propagated_midpoint_correction(delta_O, delta_dotO, delta_K, H):
    H=_positive(H,"H")
    dO=np.asarray(delta_O); dd=np.asarray(delta_dotO); dK=np.asarray(delta_K)
    if dO.shape != dd.shape or dO.shape != dK.shape or dO.ndim != 2:
        raise ValueError("aligned matrix corrections required")
    if not all(np.isfinite(x).all() for x in (dO,dd,dK)):
        raise ValueError("finite matrix corrections required")
    out_O=dO/2+H*dd/16
    out_dot=-3*dO/H-dd/4
    out_K=dK/2
    return out_O,out_dot,out_dot/2+out_K,out_dot/2-out_K,out_K

def norm_bounds_from_z05_errors(E_O,E_dotO,E_K,H):
    H=_positive(H,"H")
    vals=[]
    for x,n in [(E_O,"E_O"),(E_dotO,"E_dotO"),(E_K,"E_K")]:
        if isinstance(x,bool) or not isinstance(x,Real) or not math.isfinite(float(x)) or float(x)<0:
            raise ValueError(n+" must be finite nonnegative real")
        vals.append(float(x))
    eo,ed,ek=vals
    oa=eo/2; ob=H*ed/16; da=3*eo/H; db=ed/4
    return {"O_lower":abs(oa-ob),"O_upper":oa+ob,
            "dotO_lower":abs(da-db),"dotO_upper":da+db,"K_exact":ek/2}

def pareto_verdict(refined, coarse, tol=DEFAULT_TOL):
    if len(refined)!=2 or len(coarse)!=2: raise ValueError("two primary errors required")
    r=[float(x) for x in refined]; c=[float(x) for x in coarse]; tol=float(tol)
    if not all(math.isfinite(x) and x>=0 for x in r+c) or not math.isfinite(tol) or tol<0:
        raise ValueError("finite nonnegative values required")
    rs=all(x<=y+tol for x,y in zip(r,c)) and any(x<y-tol for x,y in zip(r,c))
    cs=all(y<=x+tol for x,y in zip(r,c)) and any(y<x-tol for x,y in zip(r,c))
    if rs:return "REFINED_PARETO_SUPPORTED_AT_Z075"
    if cs:return "COARSE_PARETO_SUPPORTED_AT_Z075"
    return "REFINEMENT_TRADEOFF_UNRESOLVED"

def primary_information():
    dk=.3418463058618517; dd=.3504308143080971
    return {"DeltaK_per_ta":dk,"DeltaDmax_per_ta":dd,
            "S_design_only_per_ta":math.hypot(dk,dd),
            "K_half_gap_per_ta":dk/2,"Dmax_half_gap_per_ta":dd/2,
            "winner_prediction":False}
