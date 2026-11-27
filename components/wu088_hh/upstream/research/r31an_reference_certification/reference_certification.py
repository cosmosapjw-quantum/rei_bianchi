from __future__ import annotations
import math
from numbers import Real

RATIO = 4.0/3.0
ORDERS = (144,192,256)
TOL = 1e-10

def _positive(x,name):
    if isinstance(x,bool) or not isinstance(x,Real):
        raise ValueError(name+" must be positive finite real")
    x=float(x)
    if not math.isfinite(x) or x<=0:
        raise ValueError(name+" must be positive finite real")
    return x

def observed_order_equal_ratio(d_coarse,d_fine,r=RATIO):
    dc=_positive(d_coarse,"d_coarse")
    df=_positive(d_fine,"d_fine")
    r=_positive(r,"r")
    if r<=1:
        raise ValueError("r must exceed 1")
    return math.log(dc/df)/math.log(r)

def conditional_power_errors(d_fine,p,r=RATIO):
    """Conditional on Q_n=Q_inf+C n^-p with fixed matrix-error direction."""
    d=_positive(d_fine,"d_fine")
    p=_positive(p,"p")
    r=_positive(r,"r")
    if r<=1:
        raise ValueError("r must exceed 1")
    rho=r**(-p)
    return {
        "rho":rho,
        "E192_conditional":d/(1-rho),
        "E256_conditional":d*rho/(1-rho),
        "rigorous":False
    }

def conditional_geometric_tail(last_increment,q):
    """Rigorous only if the future contraction inequality is itself proven."""
    d=_positive(last_increment,"last_increment")
    q=float(q)
    if not math.isfinite(q) or not (0<=q<1):
        raise ValueError("q must be finite in [0,1)")
    return {
        "latest_tail_bound": d*q/(1-q),
        "previous_tail_bound": d/(1-q),
        "requires_certified_future_contraction":True
    }

def common_reference_radius(adaptive,other,tol=TOL):
    if len(adaptive)!=2 or len(other)!=2:
        raise ValueError("two primary errors required")
    a=[_positive(x,"adaptive") for x in adaptive]
    g=[_positive(x,"other") for x in other]
    tol=float(tol)
    if not math.isfinite(tol) or tol<0:
        raise ValueError("invalid tolerance")
    margins=[gi-ai for ai,gi in zip(a,g)]
    radius=min((m-tol)/2 for m in margins)
    return {
        "margins":margins,
        "strict_common_radius_open":radius if radius>0 else None,
        "radius_is_actual_source_error_bound":False
    }

def study_contract():
    return {
      "orders":list(ORDERS),
      "ratio":RATIO,
      "new_orders_required":[144,256],
      "existing_order":192,
      "same_geometry_z":"0.75",
      "required_blocks":["O","D_col","D_row","dotO"],
      "H_required":False,
      "full49_required":False,
      "science_execution_authorized":False,
      "three_order_result_is_rigorous_continuum_bound":False
    }
