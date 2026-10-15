"""Positive source-free H/He photochemistry coupled to exact LRS photon rays.

Independent reference; not the native REI solver. X=ln(a/a0).
All photon/atom stocks are comoving number densities relative to n_star.
Photon energy is eV, cross sections Mb (1 Mb = 1e-22 m^2).
rate_per_mb = c*n_star*1e-22 m^2/H0; rate_j(X) per dX equals
rate_per_mb exp(-3X) sigma_j(E(X)) / [H(X)/H0].

No recombination, sources, scattering, metric backreaction or temperature ODE.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import ceil, exp, expm1, fsum, isfinite
from typing import Callable, Sequence
from lrs_threshold_oracle import Ray, _threshold_crossing
from verner_angular import VernerFit, load_primary_fits

SPECIES = ("HI", "HII", "HeI", "HeII", "HeIII")
CHANNELS = ("HI", "HeI", "HeII")
TARGET = (0, 2, 3)
PRODUCT = (1, 3, 4)


def pair_exact(n: float, m: float, exposure: float) -> float:
    """Exact nonnegative absorption for pair dN/dX=dM/dX=-kNM.

    Stable against nearly equal stocks and saturating strong opacity.
    """
    if not all(isfinite(v) and v >= 0 for v in (n, m, exposure)):
        raise ValueError("pair quantities must be finite nonnegative")
    if not n or not m or not exposure:
        return 0.0
    small, large = min(n, m), max(n, m)
    difference = large - small
    if difference == 0.0:
        z = small * exposure
        absorbed = small * z / (1.0 + z)
    else:
        u = -expm1(-difference * exposure)
        absorbed = small * large * u / (difference + small * u)
    return min(small, max(0., absorbed))


@dataclass(frozen=True)
class Gas:
    HI: float
    HII: float
    HeI: float
    HeII: float
    HeIII: float

    def __post_init__(self):
        if not all(isfinite(x) and x >= 0 for x in self.as_tuple()):
            raise ValueError("gas comoving populations must be finite and nonnegative")

    def as_tuple(self):
        return (self.HI, self.HII, self.HeI, self.HeII, self.HeIII)

    @property
    def hydrogen(self):
        return self.HI + self.HII

    @property
    def helium(self):
        return self.HeI + self.HeII + self.HeIII

    @property
    def electrons(self):
        return self.HII + self.HeII + 2. * self.HeIII


@dataclass(frozen=True)
class CoupledResult:
    x_end: float
    initial: Gas
    final: Gas
    photon_initial: tuple[float, ...]
    photon_final: tuple[float, ...]
    absorbed: dict[str, float]
    binding_ev: float
    heat_ev: float
    expansion_work_ev: float
    photon_energy_initial_ev: float
    photon_energy_final_ev: float
    substeps: int
    threshold_events: int

    @property
    def photon_electron_residual(self):
        return fsum(self.photon_final) - fsum(self.photon_initial) + (
            self.final.electrons - self.initial.electrons)

    @property
    def energy_residual_ev(self):
        return self.photon_energy_initial_ev - fsum((
            self.photon_energy_final_ev, self.binding_ev,
            self.heat_ev, self.expansion_work_ev))

    @property
    def hydrogen_residual(self):
        return self.final.hydrogen - self.initial.hydrogen

    @property
    def helium_residual(self):
        return self.final.helium - self.initial.helium


def threshold_events(rays: Sequence[Ray], fits: dict[str, VernerFit],
                     end: float) -> tuple[float, ...]:
    edges = [0., end]
    for ray in rays:
        for name in CHANNELS:
            x = _threshold_crossing(ray, end, fits[name].threshold_ev)
            if x is not None:
                edges.append(x)
    edges.sort()
    out = [edges[0]]
    for x in edges[1:]:
        if x > out[-1] + 2e-14 * max(1., end):
            out.append(x)
    if out[-1] != end:
        out.append(end)
    return tuple(out)


def evolve(
    rays: Sequence[Ray], initial: Gas, end: float, *,
    rate_per_mb: float = 1., step_max: float = .025,
    hubble_ratio: Callable[[float], float] | None = None,
    fits: dict[str, VernerFit] | None = None,
    step_budget: int = 100000,
) -> CoupledResult:
    """Exact pair reaction flow + symmetric Strang composition + exact half-drifts.

    Conservation of discretized energy is by construction; independent
    direct continuous ODE and resolution convergence must validate accuracy.
    """
    if not rays or not isfinite(end) or end < 0:
        raise ValueError("require rays and a nonnegative finite endpoint")
    if not isfinite(rate_per_mb) or rate_per_mb < 0:
        raise ValueError("rate_per_mb must be finite nonnegative")
    if not isfinite(step_max) or step_max <= 0 or step_budget < 1:
        raise ValueError("invalid integration budget")
    if any(abs(ray.s_over_h - rays[0].s_over_h) > 1e-13 for ray in rays):
        raise ValueError("rays must share one homogeneous LRS background")
    fits = fits or load_primary_fits()
    if any(ray.energy0_ev > min(fits[k].emax_ev for k in CHANNELS) for ray in rays):
        raise ValueError("initial photon energies outside Verner fit range")
    hubble_ratio = hubble_ratio or (lambda x: 1.0)

    # Exactly equivalent characteristics share the same absorption rate.
    # Aggregate those photon counts before each nonlinear reaction map and
    # restore their common survival factor. This preserves FLRW angular
    # isotropy and LRS +/-mu reflection symmetry without a correction.
    buckets: dict[tuple[float, ...], list[int]] = {}
    for r,ray in enumerate(rays):
        key = (ray.energy0_ev,) if rays[0].s_over_h == 0 else (ray.energy0_ev, abs(ray.mu0))
        buckets.setdefault(key, []).append(r)
    groups = tuple(tuple(indices) for indices in buckets.values())

    phi = [ray.photons0 for ray in rays]
    start_photons = tuple(phi)
    gas = list(initial.as_tuple())
    binding = heat = work = 0.0
    absorbs = [0., 0., 0.]
    starting_energy = fsum(ray.energy0_ev * count for ray,count in zip(rays, phi))
    edges = threshold_events(rays, fits, end)
    used = 0
    for lower, upper in zip(edges[:-1], edges[1:]):
        nsteps = max(1, ceil((upper-lower)/step_max))
        if used + nsteps > step_budget:
            raise ValueError("substep budget exceeded")
        for istep in range(nsteps):
            a = lower + (upper-lower)*istep/nsteps
            b = lower + (upper-lower)*(istep+1)/nsteps
            mid = .5 * (a+b)
            dt = b-a
            H = hubble_ratio(mid)
            if not isfinite(H) or H <= 0:
                raise ValueError("H/H0 must be finite positive")
            ea = [ray.geometry(a)[0] for ray in rays]
            em = [ray.geometry(mid)[0] for ray in rays]
            eb = [ray.geometry(b)[0] for ray in rays]
            work += fsum(n * (left-center) for n,left,center in zip(phi,ea,em))
            scale = rate_per_mb * exp(-3.*mid) / H
            reactions = [(indices,j,scale*fits[name].sigma_mb(em[indices[0]]))
                         for indices in groups
                         for j,name in enumerate(CHANNELS)
                         if em[indices[0]] >= fits[name].threshold_ev]
            for order in (reactions, list(reversed(reactions))):
                for indices,j,k in order:
                    population = fsum(phi[r] for r in indices)
                    A = pair_exact(population, gas[TARGET[j]], .5*dt*k)
                    if not A:
                        continue
                    fraction_survives = 1.0-A/population
                    for r in indices:
                        phi[r] *= fraction_survives
                    gas[TARGET[j]] -= A
                    gas[PRODUCT[j]] += A
                    absorbs[j] += A
                    E_i = fits[CHANNELS[j]].threshold_ev
                    binding += E_i*A
                    heat += max(0., em[indices[0]]-E_i)*A
            work += fsum(n*(center-right) for n,center,right in zip(phi,em,eb))
            used += 1
    final_energy = fsum(n*ray.geometry(end)[0] for ray,n in zip(rays,phi))
    return CoupledResult(end,initial,Gas(*gas),start_photons,tuple(phi),
        dict(zip(CHANNELS,absorbs)),binding,heat,work,starting_energy,
        final_energy,used,max(0,len(edges)-2))
