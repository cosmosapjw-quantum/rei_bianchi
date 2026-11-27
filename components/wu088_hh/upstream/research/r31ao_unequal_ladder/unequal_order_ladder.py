from __future__ import annotations
import math

N1,N2,N3=128.0,160.0,192.0
THRESHOLD=math.log(N2/N1)/math.log(N3/N2)
A=math.log(N2/N1)
B=math.log(N3/N2)

def ratio_model(p: float) -> float:
    p=float(p)
    if not math.isfinite(p) or p<=0:
        raise ValueError("p must be positive finite")
    return math.expm1(A*p)/(-math.expm1(-B*p))

def _log_ratio_model(p):
    x=A*p
    numerator_log=x+math.log1p(-math.exp(-x)) if x>50 else math.log(math.expm1(x))
    return numerator_log-math.log(-math.expm1(-B*p))

def solve_positive_order(observed_ratio: float, *, tol: float=1e-13, max_iter: int=200) -> float:
    rho=float(observed_ratio)
    if not math.isfinite(rho) or rho<=THRESHOLD:
        raise ValueError("no positive-p solution under the conditional power model")
    if not math.isfinite(tol) or tol<=0 or type(max_iter) is not int or max_iter<=0:
        raise ValueError("positive finite solver tolerance and iteration budget required")
    target_log=math.log(rho)
    lo=0.0
    hi=1.0
    while _log_ratio_model(hi) < target_log:
        hi*=2.0
    for _ in range(max_iter):
        mid=(lo+hi)/2
        if mid==0:
            mid=math.nextafter(0.0,1.0)
        if hi-lo <= tol*max(mid,math.nextafter(0.0,1.0)):
            return mid
        below=ratio_model(mid)<rho if A*mid<700 else _log_ratio_model(mid)<target_log
        if below:
            lo=mid
        else:
            hi=mid
    return (lo+hi)/2

def conditional_errors(d128160: float, d160192: float):
    d12=float(d128160); d23=float(d160192)
    if not all(math.isfinite(x) and x>0 for x in (d12,d23)):
        raise ValueError("positive finite increments required")
    rho=d12/d23
    p=solve_positive_order(rho)
    return {
        "rho_norm":rho,
        "p_conditional":p,
        "E192_conditional":d23/((N3/N2)**p-1.0),
        "E160_conditional":d23/(1.0-(N2/N3)**p),
        "rigorous":False,
        "stable_error_direction_required":True,
    }

def authority_ladder():
    return {
        "orders":[128,160,192],
        "ratios":[160/128,192/160],
        "equal_ratio":False,
        "OD_source_guard_allows":True,
        "JVP_frozen_grids_present":True,
        "exact_weight_declared_range_includes_all":True,
        "source_modification_required":False,
        "science_execution_authorized":False,
    }
