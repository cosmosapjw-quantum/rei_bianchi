"""Positive two-moment exponential reference-bin reconstruction.

Research-only source-free Bianchi-I signed-threshold adapter, not an
activation of the PR150 cold H/He production solver.  Metric (-,+,+,+):
ds2=-c2 dt2+a2(e^{-2b} dx_perp2+e^{4b} dz2), s=dot(b).
"""
from dataclasses import dataclass
from math import exp, expm1, isfinite, sqrt

@dataclass(frozen=True)
class Partition:
    active_n: float
    passive_n: float
    active_u: float
    passive_u: float
    slope: float

def unit_mean(t):
    """Mean y of exp(t*y) on [0,1]."""
    if t < 0.0:
        return 1.0-unit_mean(-t)
    if t == 0.0:
        return 0.5
    if t < 0.01:
        return 0.5+t/12.0-t**3/720.0+t**5/30240.0-t**7/1209600.0
    if t > 700.0:
        return 1.0-1.0/t
    return 1.0-1.0/t+1.0/expm1(t)

def fit_slope(fraction):
    """Monotonic bisection on the exact exponential moment constraint."""
    if not isfinite(fraction) or not 0.0 <= fraction <= 1.0:
        raise ValueError("normalized moment outside support")
    if fraction == 0.5:
        return 0.0
    if fraction == 0.0:
        return float("-inf")
    if fraction == 1.0:
        return float("inf")
    mirrored=fraction < 0.5
    goal=1.0-fraction if mirrored else fraction
    low=0.0
    high=2.0
    while unit_mean(high)<goal:
        high*=2.0
        if high > 1.e17:
            raise ArithmeticError("unrepresentable boundary moment")
    for _ in range(90):
        middle=(low+high)*0.5
        if unit_mean(middle)<goal:
            low=middle
        else:
            high=middle
    return -(low+high)*0.5 if mirrored else (low+high)*0.5

def photon_ratio(delta_b,mu0):
    if not (isfinite(delta_b) and isfinite(mu0) and -1.0 <= mu0 <= 1.0):
        raise ValueError("invalid photon direction or shear")
    t=(1.0-mu0*mu0)*exp(2.0*delta_b)
    a=mu0*mu0*exp(-4.0*delta_b)
    if not isfinite(t+a) or t+a<=0:
        raise ValueError("unrepresentable metric")
    return sqrt(t+a)

def photon_mu2(delta_b,mu0):
    rr=photon_ratio(delta_b,mu0)
    return mu0*mu0*exp(-4*delta_b)/(rr*rr)

def threshold_q(a,chi_eV,delta_b,mu0):
    if not (isfinite(a) and a>0 and isfinite(chi_eV) and chi_eV>0):
        raise ValueError("positive finite a and chi required")
    return a*chi_eV/photon_ratio(delta_b,mu0)

def threshold_velocity(delta_b,mu0,signed_s_over_h):
    if not isfinite(signed_s_over_h):
        raise ValueError("invalid shear")
    return 1.0-signed_s_over_h*(1.0-3.0*photon_mu2(delta_b,mu0))

def _tail(t,r):
    """Stable mass fraction of reconstructed positive density y>=r."""
    if r<=0.0:return 1.0
    if r>=1.0:return 0.0
    if t==0.0:return 1.0-r
    if t>0.0:
        return -expm1(-t*(1-r))/-expm1(-t)
    return exp(t*r)*(-expm1(t*(1-r)))/(-expm1(t))

def _head(t,r):
    if r<=0.0:return 0.0
    if r>=1.0:return 1.0
    if t==0.0:return r
    if t>0.0:
        return exp(-t*(1-r))*(-expm1(-t*r))/-expm1(-t)
    return -expm1(t*r)/-expm1(t)

def split_parent(n,u,lo,hi,cut,slope=None):
    """Partition one immutable source-free q-cell by the moving cut.

    n: photons/reference H; u: reference energy moment eV/H; q in eV.
    Reapply to the same parent after each geometry step, including blue shifts.
    """
    if not all(isfinite(x) for x in (n,u,lo,hi,cut)):
        raise ValueError("nonfinite moments")
    if n<0 or lo<0 or hi<=lo or u<0:
        raise ValueError("invalid source moment domain")
    if n==0:
        if u!=0:raise ValueError("nonzero energy with zero number")
        return Partition(0.0,0.0,0.0,0.0,0.0)
    lower=n*lo
    upper=n*hi
    if not lower<=u<=upper:
        raise ValueError("inconsistent parent support")
    if slope is None:
        fraction=(u/n-lo)/(hi-lo)
        slope=fit_slope(fraction)
    if cut<=lo:return Partition(n,0.0,u,0.0,slope)
    if cut>hi:return Partition(0.0,n,0.0,u,slope)
    if slope==float("inf"):
        return Partition(n,0.0,u,0.0,slope)
    if slope==float("-inf"):
        return Partition(0.0,n,0.0,u,slope)
    r=(cut-lo)/(hi-lo)
    tail=_tail(slope,r)
    head=_head(slope,r)
    # Compute the minority from its direct positive integral, and the
    # majority as complement. Never subtract two nearly equal energies to
    # reconstruct a vanishing minority; it can become spuriously negative.
    if tail<=head:
        an=n*tail
        pn=n-an
        au=an*(cut+(hi-cut)*unit_mean(slope*(1.0-r))) if an>0 else 0.0
        pu=u-au
    else:
        pn=n*head
        an=n-pn
        pu=pn*(lo+(cut-lo)*unit_mean(slope*r)) if pn>0 else 0.0
        au=u-pu
    if au<0 or pu<0:
        raise ArithmeticError("floating-point cut lost positive moment")
    return Partition(an,pn,au,pu,slope)

def flux_on_cut(n,lo,hi,cut,slope,dlogcut_dx):
    """Analytic active->passive number/reference-energy face flux per d ln a."""
    if not (n>=0 and lo<cut<hi and isfinite(dlogcut_dx)):
        raise ValueError("interior cut, positive source, finite speed required")
    y=(cut-lo)/(hi-lo)
    if abs(slope)<0.01:
        norm=1.0+slope*0.5+slope*slope/6.0+slope**3/24.0
        dens=exp(slope*y)/norm
    elif slope>0:
        dens=slope*exp(slope*(y-1.0))/-expm1(-slope)
    else:
        dens=(-slope)*exp(slope*y)/-expm1(slope)
    transfer=n*dens*cut*dlogcut_dx/(hi-lo)
    return transfer,cut*transfer
