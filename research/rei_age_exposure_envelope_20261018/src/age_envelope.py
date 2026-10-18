"""Conditional real-arithmetic photon/exposure comparison bounds.

N'=j-sum(k_i)N uses x=ln(a), photons per total H, and k_i=c*n_i*sigma_i/H.
Inputs must bound the functions on the WHOLE slab, not just at sample points.
Float64 output is NOT a directed-rounded interval or a native accuracy certificate.
"""
from dataclasses import dataclass
import math
from typing import Sequence

FIT_EV = (13.60, 24.59, 54.42)
BIND_EV = (13.598434599702, 24.587389011, 54.41776)
Bounds = tuple[float, float]


def interval(v: Sequence[float], name: str) -> Bounds:
    if len(v) != 2:
        raise ValueError(f'{name}: two endpoints required')
    lo, hi = map(float, v)
    if not (math.isfinite(lo) and math.isfinite(hi) and 0 <= lo <= hi):
        raise ValueError(f'{name}: finite 0 <= lower <= upper required')
    return lo, hi


def phi1(t: float) -> float:
    """(1-exp(-t))/t, continuous at t=0."""
    if not math.isfinite(t) or t < 0:
        raise ValueError('nonnegative finite optical depth required')
    if t < 0.01:
        return 1+t*(-1/2+t*(1/6+t*(-1/24+t*(1/120+t*(-1/720+t/5040)))))
    return -math.expm1(-t)/t


def phi2(t: float) -> float:
    """(1-phi1(t))/t, evaluated without tiny-depth cancellation."""
    if not math.isfinite(t) or t < 0:
        raise ValueError('nonnegative finite optical depth required')
    if t < 0.01:
        return .5+t*(-1/6+t*(1/24+t*(-1/120+t*(1/720+t*(-1/5040+t/40320)))))
    return (1-phi1(t))/t


def constant_flow(n: float, j: float, k: float, h: float) -> tuple[float, float]:
    """Exact frozen-flow endpoint and integral I_N=integral N dx."""
    for v in (n,j,k,h):
        if not math.isfinite(v) or v < 0:
            raise ValueError('finite nonnegative flow inputs required')
    tau=k*h
    if not math.isfinite(tau):
        raise OverflowError('optical depth overflow')
    end=math.fsum((n*math.exp(-tau),j*h*phi1(tau)))
    exposure=math.fsum((n*h*phi1(tau),j*h*h*phi2(tau)))
    if not math.isfinite(end+exposure):
        raise OverflowError('photon/exposure overflow')
    return end, exposure


@dataclass(frozen=True)
class SlabBounds:
    n: Bounds
    exposure: Bounds
    absorbed: tuple[Bounds, Bounds, Bounds]
    binding: Bounds
    heat: Bounds
    absorbed_energy: Bounds
    arithmetic: str = 'binary64_not_outward_certified'


def enclosure(n: Sequence[float], j: Sequence[float], rates: Sequence[Sequence[float]],
              h: float, energy: Sequence[float]) -> SlabBounds:
    """Enclose survivor, exposure and three species event/energy integrals.

    The original native chemistry owner is NOT replaced. This routine is a
    diagnostic supplied with actual interval bounds by a separate donor.
    An active-rate energy interval crossing a fit threshold must be split first.
    """
    n=interval(n,'N'); j=interval(j,'j'); e=interval(energy,'E')
    if not math.isfinite(h) or h <= 0 or len(rates)!=3:
        raise ValueError('positive finite width and exactly three rates required')
    r=tuple(interval(v,'k') for v in rates)
    for i,v in enumerate(r):
        if v[1]>0 and e[0]<FIT_EV[i]:
            tag='ACTIVE_RATE_BELOW_FIT' if e[1]<FIT_EV[i] else 'THRESHOLD_EVENT_UNSPLIT'
            raise ValueError(tag+f': species={i}')
    klo=math.fsum(v[0] for v in r); khi=math.fsum(v[1] for v in r)
    nl, il=constant_flow(n[0],j[0],khi,h)
    nu, iu=constant_flow(n[1],j[1],klo,h)
    ab=tuple((v[0]*il,v[1]*iu) for v in r)
    binding=tuple(math.fsum(BIND_EV[i]*ab[i][k] for i in range(3)) for k in (0,1))
    heat=tuple(math.fsum((e[k]-BIND_EV[i])*ab[i][k] for i in range(3) if r[i][1]>0)
               for k in (0,1))
    en=(e[0]*math.fsum(v[0] for v in ab),e[1]*math.fsum(v[1] for v in ab))
    values=(nl,nu,il,iu,*binding,*heat,*en,*(x for v in ab for x in v))
    if not all(math.isfinite(x) and x>=0 for x in values):
        raise OverflowError('invalid finite enclosure')
    return SlabBounds((nl,nu),(il,iu),ab,binding,heat,en)


def lrs_energy_bounds(e_birth: float, mu_birth: float, x_birth: float,
                      x_pair: Sequence[float], b_birth: float,
                      b_pair: Sequence[float]) -> Bounds:
    """Componentwise conservative E bounds on a prescribed LRS Bianchi-I slab.

    ds2=-c2dt2+a2[e^-2b dx_perp2+e^4b dz2]. b_pair bounds b over the
    entire x interval. x and b endpoints can be signed. No Einstein solve.
    """
    if len(x_pair)!=2 or len(b_pair)!=2:
        raise ValueError('two x and b endpoints required')
    xa,xb=map(float,x_pair); ba,bb=map(float,b_pair)
    vals=(e_birth,mu_birth,x_birth,xa,xb,b_birth,ba,bb)
    if not all(math.isfinite(v) for v in vals) or e_birth<0 or abs(mu_birth)>1:
        raise ValueError('invalid geometry input')
    if xa>xb or ba>bb or xa<x_birth:
        raise ValueError('ordered post-birth interval required')
    if e_birth==0:return (0.,0.)
    m=mu_birth*mu_birth; dl=ba-b_birth; du=bb-b_birth
    low=math.fsum(((1-m)*math.exp(2*dl),m*math.exp(-4*du)))
    high=math.fsum(((1-m)*math.exp(2*du),m*math.exp(-4*dl)))
    return (e_birth*math.exp(x_birth-xb)*math.sqrt(low),
            e_birth*math.exp(x_birth-xa)*math.sqrt(high))
