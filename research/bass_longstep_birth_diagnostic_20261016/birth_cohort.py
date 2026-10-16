"""Independent positive frozen-opacity photochemistry birth-time oracle.

Research-only: non-tilted local photon number and species-aware energy ownership
at fixed geometry, photon energy and gas fractions during one proper-time slab.
No integration with REI native driver, cosmic redshift, photon source-age geometry,
or H/He recombination/thermal EOS. Source j >= 0 [photons / H / s],
λ_i >=0 [s^-1], old number >=0 [/H], dt>0 [s], E [eV].

The old native REI stage injects all S=j*dt before a backward Euler absorption
solve. Under fixed λ this corresponds to N_BE=(Nold+S)/(1+tau).
The continuum piecewise-constant frozen slab is instead
N_exact=Nold*exp(-tau)+S*phi1(-tau), tau=Σλ_i dt, phi1=(1-e^-tau)/tau.
Both are positive and conservative; discrete conservation is not error control.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Sequence

BINDING_EV = (13.598434599702, 24.587389011, 54.41776)


def phi1(tau: float) -> float:
    if not math.isfinite(tau) or tau < 0:
        raise ValueError("physical positive optical depth")
    if tau == 0:
        return 1.0
    if tau < 1e-4:
        # Horner expansion through τ^5; remainder bounded by τ^6/5040 here.
        return 1.0 + tau * (-0.5 + tau * (1 / 6 + tau * (-1 / 24 + tau * (1 / 120 - tau / 720))))
    return -math.expm1(-tau) / tau


def expected_bias(old: float, birth: float, tau: float) -> float:
    """N_BE - N_uniform-exact, cancellation-safe except near exact equilibrium.

    Strict algebra: [1/(1+τ)-e^-τ] * (Nold-S/τ).
    For τ=0 there is exactly no absorption and no bias.
    """
    if not all(math.isfinite(v) and v >= 0 for v in (old, birth, tau)):
        raise ValueError("physical nonnegative source/input")
    if tau == 0:
        return 0.0
    return (1 / (1 + tau) - math.exp(-tau)) * (old - birth / tau)


@dataclass(frozen=True)
class PacketStep:
    method: str
    survivor_old: float
    survivor_newborn: float
    injected_count: float
    initial_old: float
    photon_energy_ev: float
    absorbed_by_species: tuple[float, ...]
    binding_energy_ev_per_h: float
    gas_photoheat_ev_per_h: float
    photon_energy_out_ev_per_h: float
    photon_energy_in_ev_per_h: float

    @property
    def absorbed(self) -> float:
        return sum(self.absorbed_by_species)

    @property
    def survivor(self) -> float:
        return self.survivor_old + self.survivor_newborn

    @property
    def number_residual(self) -> float:
        return (self.initial_old + self.injected_count) - self.survivor - self.absorbed

    @property
    def energy_residual(self) -> float:
        return (self.photon_energy_in_ev_per_h - self.photon_energy_out_ev_per_h
                - self.binding_energy_ev_per_h - self.gas_photoheat_ev_per_h)


def frozen_packet(*, old: float, source_rate: float, dt: float,
                  lambdas: Sequence[float], energy_ev: float,
                  binding_ev: Sequence[float] = BINDING_EV,
                  method: str = "legacy_be") -> PacketStep:
    if method not in ("legacy_be", "uniform_exact", "be_old_uniform_birth"):
        raise ValueError("unknown method")
    if not all(math.isfinite(v) and v >= 0 for v in (old, source_rate, *lambdas)):
        raise ValueError("nonnegative rates, old photon count")
    if not math.isfinite(dt) or dt <= 0 or not math.isfinite(energy_ev) or energy_ev <= 0:
        raise ValueError("proper positive seconds and photon energy")
    if len(lambdas) != len(binding_ev) or len(lambdas) == 0:
        raise ValueError("species matching")
    for lam, cutoff in zip(lambdas, binding_ev):
        if not math.isfinite(cutoff) or cutoff <= 0 or (lam > 0 and energy_ev < cutoff):
            raise ValueError("positive absorption only above actual binding")
    birth = source_rate * dt
    total = sum(lambdas)
    tau = total * dt
    if not math.isfinite(tau) or not math.isfinite(birth):
        raise ValueError("finite counts/opacity")
    if method == "legacy_be":
        old_survival = old / (1 + tau)
        newborn_survival = birth / (1 + tau)
    elif method == "uniform_exact":
        old_survival = old * math.exp(-tau)
        newborn_survival = birth * phi1(tau)
    else:
        old_survival = old / (1 + tau)
        newborn_survival = birth * phi1(tau)
    absorbed = (old - old_survival) + (birth - newborn_survival)
    if total == 0:
        abs_species = tuple(0. for _ in lambdas)
    else:
        abs_species = tuple(absorbed * lam / total for lam in lambdas)
    # Energy has no redshift work because geometry and E are frozen in the slab.
    energy_in = (old + birth) * energy_ev
    energy_out = (old_survival + newborn_survival) * energy_ev
    binding = math.fsum(x * e for x, e in zip(abs_species, binding_ev))
    heat = math.fsum(x * (energy_ev - e) for x, e in zip(abs_species, binding_ev))
    return PacketStep(method, old_survival, newborn_survival, birth, old, energy_ev,
                      abs_species, binding, heat, energy_out, energy_in)
