"""Independent positive LRS Bianchi-I spectral threshold characteristic oracle.

This is a conditional reference problem, NOT the native reionization solver:
a_perp=a exp(-b), a_parallel=a exp(2b), b=(s/H) ln(a/a0);
non-tilted homogeneous absorber n_i=n_i0 exp(-3 x),
sigma_i=sigma_i0 (E_i/E)^3 above the ionization threshold,
and prescribed H(x)/H0. No scattering, emission, gas feedback or line RT.

The comoving initial-ray photon weight is conserved without absorption.
Energies and ledgers are in eV per initial comoving photon-weight volume.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, exp, expm1, fsum, isfinite, sqrt
from typing import Callable, Iterable

# Positive 8-point Gauss-Legendre nodes and weights on [-1,1].
GAUSS8 = (
    (-0.9602898564975363, 0.1012285362903763),
    (-0.7966664774136267, 0.2223810344533745),
    (-0.5255324099163290, 0.3137066458778873),
    (-0.1834346424956498, 0.3626837833783620),
    (0.1834346424956498, 0.3626837833783620),
    (0.5255324099163290, 0.3137066458778873),
    (0.7966664774136267, 0.2223810344533745),
    (0.9602898564975363, 0.1012285362903763),
)


@dataclass(frozen=True)
class Ray:
    energy0_ev: float
    mu0: float
    photons0: float
    s_over_h: float

    def __post_init__(self) -> None:
        if not (isfinite(self.energy0_ev) and self.energy0_ev > 0):
            raise ValueError("initial energy must be finite and positive")
        if not (isfinite(self.mu0) and -1 <= self.mu0 <= 1):
            raise ValueError("initial direction cosine must lie in [-1,1]")
        if not (isfinite(self.photons0) and self.photons0 >= 0):
            raise ValueError("initial photon weight must be finite and nonnegative")
        # This precisely ensures d ln E/dx < 0 for every direction.
        if not (isfinite(self.s_over_h) and -0.5 < self.s_over_h < 1.0):
            raise ValueError("requires monotone-redshift background -1/2 < s/H < 1")

    def geometry(self, x: float) -> tuple[float, float, float]:
        b = self.s_over_h * x
        transverse = (1.0 - self.mu0**2) * exp(2.0*b)
        parallel = self.mu0**2 * exp(-4.0*b)
        factor = transverse + parallel
        energy = self.energy0_ev * exp(-x) * sqrt(factor)
        mu = self.mu0 * exp(-2.0*b) / sqrt(factor)
        return energy, mu, factor

    def drift_positive(self, x: float) -> float:
        _, mu, _ = self.geometry(x)
        return 1.0 + self.s_over_h * (3.0*mu**2 - 1.0)


@dataclass(frozen=True)
class Species:
    name: str
    threshold_ev: float
    opacity_at_threshold: float

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("species name is required")
        if not (isfinite(self.threshold_ev) and self.threshold_ev > 0):
            raise ValueError("threshold energy must be finite and positive")
        if not (isfinite(self.opacity_at_threshold) and self.opacity_at_threshold >= 0):
            raise ValueError("dimensionless c*n0*sigma0/H0 must be nonnegative")


@dataclass(frozen=True)
class Result:
    ray: Ray
    x_end: float
    photons_end: float
    energy_end_ev: float
    mu_end: float
    absorbed_counts: dict[str, float]
    heat_ev: dict[str, float]
    absorbed_energy_ev: dict[str, float]
    redshift_work_ev: float
    threshold_events: dict[str, float]
    substeps: int

    @property
    def photon_number_residual(self) -> float:
        return self.ray.photons0 - self.photons_end - fsum(self.absorbed_counts.values())

    @property
    def energy_residual_ev(self) -> float:
        return (self.ray.photons0 * self.ray.energy0_ev
                - self.photons_end * self.energy_end_ev
                - fsum(self.absorbed_energy_ev.values()) - self.redshift_work_ev)


@dataclass(frozen=True)
class AngularMoments:
    energy_ev: float
    p_parallel_ev: float
    p_transverse_ev: float
    pi_ev: float


def angular_moments(rays: Iterable[Result]) -> AngularMoments:
    items = tuple(rays)
    energy = fsum(r.photons_end * r.energy_end_ev for r in items)
    parallel = fsum(r.photons_end * r.energy_end_ev * r.mu_end**2 for r in items)
    transverse = (energy - parallel) / 2.0
    return AngularMoments(energy, parallel, transverse, parallel - transverse)


def _gauss8(a: float, b: float, f: Callable[[float], float]) -> float:
    if b == a:
        return 0.0
    midpoint, half = (a+b)/2.0, (b-a)/2.0
    return half * fsum(w * f(midpoint + half*t) for t, w in GAUSS8)


def _threshold_crossing(ray: Ray, x_end: float, energy_threshold: float) -> float | None:
    if ray.energy0_ev <= energy_threshold or ray.geometry(x_end)[0] >= energy_threshold:
        return None
    lo, hi = 0.0, x_end
    # Monotone-redshift interval ensures a single crossing.
    for _ in range(75):
        mid = 0.5*(lo+hi)
        if mid == lo or mid == hi:
            break
        if ray.geometry(mid)[0] > energy_threshold:
            lo = mid
        else:
            hi = mid
    return 0.5*(lo+hi)


def propagate(
    ray: Ray,
    species: Iterable[Species],
    x_end: float,
    *,
    hubble_ratio: Callable[[float], float] | None = None,
    subdivisions: int = 1,
    max_step_optical_depth: float = 0.35,
    max_substeps: int = 4096,
) -> Result:
    """Advance one photon characteristic, splitting all crossed thresholds.

    Exact positive photon-count update within each threshold-active interval.
    Heating and cosmological shear/redshift work use independent, positive GL8
    characteristic quadratures. No residual is 'closed' by subtractive assignment.
    """
    if not (isfinite(x_end) and x_end >= 0):
        raise ValueError("x_end must be finite and nonnegative")
    if subdivisions < 1 or max_substeps < 1 or max_step_optical_depth <= 0:
        raise ValueError("invalid quadrature/step budget")
    if abs(ray.s_over_h*x_end) > 20:
        raise ValueError("large shear exponent outside validated range")

    items = tuple(species)
    names = [sp.name for sp in items]
    if len(set(names)) != len(names):
        raise ValueError("species names must be unique")
    hubble_ratio = hubble_ratio or (lambda x: 1.0)

    def common(x: float) -> float:
        _, _, f = ray.geometry(x)
        h = hubble_ratio(x)
        if not (isfinite(h) and h > 0):
            raise ValueError("H(x)/H0 must be finite positive")
        return f**(-1.5) / h

    eta = {sp.name: sp.opacity_at_threshold *
           (sp.threshold_ev/ray.energy0_ev)**3 for sp in items}
    events = {sp.name: crossing for sp in items
              if (crossing := _threshold_crossing(ray, x_end, sp.threshold_ev)) is not None}
    edges = sorted(set([0.0, x_end, *events.values()]))
    counts = {sp.name: 0.0 for sp in items}
    heats = {sp.name: 0.0 for sp in items}
    absorbed_energy = {sp.name: 0.0 for sp in items}
    photons = ray.photons0
    work = 0.0
    used_steps = 0

    for a, b in zip(edges[:-1], edges[1:]):
        middle_energy = ray.geometry((a+b)/2.0)[0]
        active = [sp for sp in items if middle_energy > sp.threshold_ev and eta[sp.name] > 0]
        total_eta = fsum(eta[sp.name] for sp in active)
        tau_entire = total_eta * _gauss8(a, b, common)
        nsteps = max(subdivisions, ceil(tau_entire / max_step_optical_depth))
        if used_steps+nsteps > max_substeps:
            raise ValueError("optical-depth substep budget exceeded")
        for j in range(nsteps):
            left = a + (b-a)*j/nsteps
            right = a + (b-a)*(j+1)/nsteps
            tau = total_eta * _gauss8(left, right, common)
            start_photons = photons
            photons = start_photons * exp(-tau)
            removed = start_photons * (-expm1(-tau))
            if total_eta:
                for sp in active:
                    counts[sp.name] += removed * eta[sp.name] / total_eta

            def attenuation(y: float) -> float:
                return exp(-total_eta*_gauss8(left, y, common))

            for sp in active:
                # E(y)>=E_threshold throughout this event-split interval.
                deposited = _gauss8(
                    left, right,
                    lambda y: (attenuation(y) * common(y) *
                               max(0.0, ray.geometry(y)[0] - sp.threshold_ev))
                )
                dh = start_photons * eta[sp.name] * deposited
                heats[sp.name] += dh
                # Threshold/binding energy and excess kinetic energy are kept separate.
                # Number is updated with expm1, not an energy-integral approximation.
                dcount = removed * eta[sp.name] / total_eta
                absorbed_energy[sp.name] += sp.threshold_ev*dcount + dh

            work += start_photons * _gauss8(
                left, right,
                lambda y: attenuation(y) * ray.geometry(y)[0] * ray.drift_positive(y)
            )
            used_steps += 1

    end_energy, end_mu, _ = ray.geometry(x_end)
    return Result(ray, x_end, photons, end_energy, end_mu,
                  counts, heats, absorbed_energy, work, events, used_steps)
