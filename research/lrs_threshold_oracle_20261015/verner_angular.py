"""Verner-1996 donor-backed, positive H/He photon characteristics and angular cuts.

Independent conditional reference work. NOT a real reionization source solver.
Published donor https://www.pa.uky.edu/~verner/dima/photo//photo.dat
Verner et al. (1996), ApJ 465, 487, Eq. (1), Table 1.

All cross-section parameters are read from the unmodified primary ASCII table.
Absorber opacity is *dimensionless* c*n_i0*sigma_i(Ethreshold)/H0.
Energies in eV; fixed comoving absorber stock n_i=n_i0 exp(-3 X).
"""
from __future__ import annotations
from dataclasses import dataclass
from math import ceil, exp, expm1, fsum, isfinite, sqrt
from pathlib import Path
from typing import Callable, Iterable

from lrs_threshold_oracle import Ray, Result, _gauss8, _threshold_crossing

DONOR_PATH = Path(__file__).resolve().parent / "donors" / "verner1996_photo.dat"


@dataclass(frozen=True)
class VernerFit:
    symbol: str
    threshold_ev: float
    emax_ev: float
    e0_ev: float
    sigma0_mb: float
    ya: float
    power: float
    yw: float
    y0: float
    y1: float

    def sigma_mb(self, energy_ev: float) -> float:
        """Verner Eq. (1), zero strictly below threshold; only valid <= Emax."""
        if not isfinite(energy_ev) or energy_ev < 0:
            raise ValueError("photon energy must be finite and nonnegative")
        if energy_ev < self.threshold_ev:
            return 0.0
        if energy_ev > self.emax_ev:
            raise ValueError("Verner fit outside published Emax")
        x = energy_ev/self.e0_ev - self.y0
        y = sqrt(x*x + self.y1*self.y1)
        shape = ((x-1.0)**2 + self.yw**2) * y**(0.5*self.power-5.5)
        value = self.sigma0_mb*shape*(1.0+sqrt(y/self.ya))**(-self.power)
        if not isfinite(value) or value < 0:
            raise ArithmeticError("invalid fitted cross-section")
        return value

    @property
    def threshold_sigma_mb(self) -> float:
        return self.sigma_mb(self.threshold_ev)


def load_primary_fits(path: Path = DONOR_PATH) -> dict[str, VernerFit]:
    mapping = {(1,1): "HI", (2,2): "HeI", (2,1): "HeII"}
    result: dict[str, VernerFit] = {}
    for line in path.read_text(encoding="ascii").splitlines():
        terms = line.split()
        if not terms:
            continue
        if len(terms) != 11:
            raise ValueError("unexpected Verner table row width")
        z, n = int(terms[0]), int(terms[1])
        if (z,n) not in mapping:
            continue
        name = mapping[z,n]
        if name in result:
            raise ValueError("duplicate species row")
        result[name] = VernerFit(name, *(float(v) for v in terms[2:]))
    if set(result) != set(mapping.values()):
        raise ValueError("missing donor species")
    return result


@dataclass(frozen=True)
class Absorber:
    fit: VernerFit
    opacity_at_threshold: float

    def __post_init__(self):
        if not (isfinite(self.opacity_at_threshold) and
                self.opacity_at_threshold >= 0):
            raise ValueError("opacity must be finite and nonnegative")
        if self.fit.threshold_sigma_mb <= 0:
            raise ValueError("threshold cross section must be positive")


def propagate_verner(
    ray: Ray,
    absorbers: Iterable[Absorber],
    x_end: float,
    *,
    hubble_ratio: Callable[[float], float] | None = None,
    subdivisions: int = 1,
    max_step_tau: float = 0.35,
    max_substeps: int = 8192,
) -> Result:
    """Propagate along exact LRS ray with full Verner fits, no E^-3 shortcut.

    Counts (per species) are **independently integrated** rather than assigned
    by subtracting from N_end. Separate number/energy residuals falsify the
    quadrature. All absorbed counts and heat are nonnegative by construction.
    """
    items = tuple(absorbers)
    if len(set(ab.fit.symbol for ab in items)) != len(items):
        raise ValueError("duplicate absorber symbol")
    if not (isfinite(x_end) and x_end >= 0):
        raise ValueError("x_end must be nonnegative and finite")
    if subdivisions < 1 or max_substeps < 1 or max_step_tau <= 0:
        raise ValueError("invalid quadrature budget")
    if abs(ray.s_over_h*x_end) > 20:
        raise ValueError("background exponent outside reference scope")
    if any(ray.energy0_ev > ab.fit.emax_ev for ab in items):
        raise ValueError("initial photon energy exceeds donor Emax")
    hubble_ratio = hubble_ratio or (lambda x: 1.)
    at_threshold = tuple(ab.fit.threshold_sigma_mb for ab in items)
    events = {
        ab.fit.symbol: cross
        for ab in items
        if (cross := _threshold_crossing(ray,x_end,ab.fit.threshold_ev)) is not None
    }
    edges = sorted(set((0.,x_end,*events.values())))
    counts={ab.fit.symbol: 0. for ab in items}
    heats={ab.fit.symbol: 0. for ab in items}
    energies={ab.fit.symbol: 0. for ab in items}
    photons=ray.photons0
    work=0.
    used=0

    def rates(y: float) -> tuple[float, ...]:
        energy = ray.geometry(y)[0]
        h = hubble_ratio(y)
        if not isfinite(h) or h <= 0:
            raise ValueError("H/H0 must be finite and positive")
        return tuple(
            ab.opacity_at_threshold*exp(-3*y)/h *
            ab.fit.sigma_mb(energy)/sigma_th
            for ab,sigma_th in zip(items,at_threshold)
        )

    def rate_sum(y: float) -> float:
        return fsum(rates(y))

    for a,b in zip(edges[:-1],edges[1:]):
        total_tau = _gauss8(a,b,rate_sum)
        nstep=max(subdivisions,ceil(total_tau/max_step_tau))
        if used+nstep > max_substeps:
            raise ValueError("exceeded optical-depth step budget")
        for k in range(nstep):
            left=a+(b-a)*k/nstep
            right=a+(b-a)*(k+1)/nstep
            tau=_gauss8(left,right,rate_sum)
            start=photons
            photons=start*exp(-tau)

            def survival(y: float) -> float:
                return exp(-_gauss8(left,y,rate_sum))

            for j,ab in enumerate(items):
                def deposition(y: float):
                    v=survival(y)*rates(y)[j]
                    energy=ray.geometry(y)[0]
                    return v, v*max(0.,energy-ab.fit.threshold_ev)

                # One joint quadrature pass per channel, independently from
                # the total optical depth and the expansion/shear work.
                removed=_gauss8(left,right,lambda y: deposition(y)[0])
                heat=_gauss8(left,right,lambda y: deposition(y)[1])
                counts[ab.fit.symbol] += start*removed
                heats[ab.fit.symbol] += start*heat
                energies[ab.fit.symbol] += start*(ab.fit.threshold_ev*removed+heat)

            work += start*_gauss8(
                left,right,
                lambda y: (survival(y)*ray.geometry(y)[0]*
                           ray.drift_positive(y))
            )
            used += 1

    final_energy,final_mu,_=ray.geometry(x_end)
    return Result(ray,x_end,photons,final_energy,final_mu,
                  counts,heats,energies,work,events,used)


def exact_angular_cutpoints(
    energy0_ev: float, signed_s_over_h: float, x_end: float,
    thresholds_ev: Iterable[float],
) -> tuple[float,...]:
    """Analytic angle cutpoints E(x_end,mu0)=E_threshold.

    Valid for the constant signed-s/H monotone-redshift background.
    Produces sorted (-1,1) endpoints plus all internal ±mu critical values.
    """
    if not (isfinite(energy0_ev) and energy0_ev > 0 and
            isfinite(signed_s_over_h) and -.5 < signed_s_over_h < 1 and
            isfinite(x_end) and x_end >= 0):
        raise ValueError("invalid characteristic")
    b=signed_s_over_h*x_end
    if abs(b)<1e-14:
        return (-1.,1.)
    a=exp(2*b)
    c=exp(-4*b)
    denom=c-a
    cuts=[-1.,1.]
    for eth in thresholds_ev:
        if not isfinite(eth) or eth <= 0:
            raise ValueError("invalid threshold")
        q=((eth/energy0_ev)**2*exp(2*x_end)-a)/denom
        if 0. < q < 1.:
            u=sqrt(q)
            cuts.extend((-u,u))
    ordered=sorted(cuts)
    return tuple(v for i,v in enumerate(ordered)
                 if i==0 or v-ordered[i-1]>1e-13)


@dataclass(frozen=True)
class AngularSummary:
    surviving: float
    energy_ev: float
    pressure_parallel_ev: float
    absorbed: dict[str,float]
    heat_ev: dict[str,float]
    work_ev: float
    evaluated_rays: int
    accepted_panels: int
    boundaries: tuple[float,...]

    @property
    def pi_over_u(self) -> float:
        return (3*self.pressure_parallel_ev-self.energy_ev)/(2*self.energy_ev)


def _angular_vec(res: Result, names: tuple[str,...]) -> tuple[float,...]:
    u=res.photons_end*res.energy_end_ev
    return (res.photons_end,u,u*res.mu_end**2,
            *(res.absorbed_counts[n] for n in names),
            *(res.heat_ev[n] for n in names),
            res.redshift_work_ev)


def angular_verner(
    energy0_ev: float, signed_s_over_h: float,
    absorbers: Iterable[Absorber], x_end: float, *,
    rel_tol: float = 2e-8, abs_tol: float = 3e-11,
    split_at_thresholds: bool = True, max_depth: int = 8,
    gauss_low: int = 8, gauss_high: int = 16,
) -> AngularSummary:
    """Adaptive GL8/16 on EXACT threshold-cut panels, deterministic sums."""
    import numpy as np
    items=tuple(absorbers)
    names=tuple(ab.fit.symbol for ab in items)
    if rel_tol <= 0 or abs_tol <= 0 or max_depth < 0:
        raise ValueError("invalid adaptive tolerance")
    thresholds=(ab.fit.threshold_ev for ab in items)
    boundaries=(exact_angular_cutpoints(energy0_ev,signed_s_over_h,x_end,thresholds)
                if split_at_thresholds else (-1.,1.))
    gx_lo,gw_lo=np.polynomial.legendre.leggauss(gauss_low)
    gx_hi,gw_hi=np.polynomial.legendre.leggauss(gauss_high)
    evaluations=0
    accepted=0
    def integrate_panel(left: float,right: float, nodes,weights):
        nonlocal evaluations
        center=(right+left)/2.
        half=(right-left)/2.
        out=[]
        for mu,w in zip(nodes,weights):
            res=propagate_verner(Ray(energy0_ev,float(center+half*mu),1.,
                                    signed_s_over_h),items,x_end)
            v=_angular_vec(res,names)
            out.append(tuple(float(half*.5*w)*a for a in v))
            evaluations+=1
        return tuple(fsum(row[k] for row in out) for k in range(len(out[0])))

    def recurse(left,right,depth):
        nonlocal accepted
        lo=integrate_panel(left,right,gx_lo,gw_lo)
        hi=integrate_panel(left,right,gx_hi,gw_hi)
        good=all(abs(a-b) <= abs_tol*(right-left)/2 +
                 rel_tol*max(abs(a),abs(b)) for a,b in zip(lo,hi))
        if good:
            accepted+=1
            return hi
        if depth>=max_depth:
            raise RuntimeError("angular adaptive quadrature has not converged")
        mid=(left+right)/2.
        l=recurse(left,mid,depth+1)
        r=recurse(mid,right,depth+1)
        return tuple(fsum((a,b)) for a,b in zip(l,r))

    blocks=(recurse(a,b,0) for a,b in zip(boundaries[:-1],boundaries[1:]))
    sums=None
    all_blocks=list(blocks)
    sums=tuple(fsum(v[k] for v in all_blocks) for k in range(len(all_blocks[0])))
    n=len(names)
    return AngularSummary(sums[0],sums[1],sums[2],
                          dict(zip(names,sums[3:3+n])),
                          dict(zip(names,sums[3+n:3+2*n])),
                          sums[-1],evaluations,accepted,boundaries)
