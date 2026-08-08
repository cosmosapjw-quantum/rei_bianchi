#!/usr/bin/env python3
"""Fast positive thermal SDIRK2 root with analytic log-temperature derivative.

The physical thermal balance and Alexander SDIRK2 tableau are identical to the
reference implementation.  The optimization only hoists population-dependent
coefficients and replaces fixed 80-step bisection by safeguarded Newton inside
the same positive log-temperature bracket, with bisection fallback.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

KB_ERG = 1.380649e-16
EV_ERG = 1.602176634e-12
GAMMA = 1.0 - 1.0 / math.sqrt(2.0)
LN10 = math.log(10.0)


@dataclass(frozen=True)
class FastThermalResult:
    energy: np.ndarray
    temperature: np.ndarray
    rhs: np.ndarray
    relative_residual: np.ndarray
    bracketed: np.ndarray
    iterations: int


@dataclass(frozen=True)
class FastSDIRK2ThermalResult:
    stage: FastThermalResult
    final: FastThermalResult


def _pop(populations: np.ndarray) -> np.ndarray:
    pop = np.asarray(populations, dtype=np.float64)
    if pop.ndim != 2 or pop.shape[1] != 5:
        raise ValueError('populations must have shape [N,5]')
    if np.any(~np.isfinite(pop)) or np.any(pop <= 0.0):
        raise ValueError('populations must be finite and strictly positive')
    return np.ascontiguousarray(pop)


def _vec(value, n: int, name: str, *, positive: bool = False) -> np.ndarray:
    arr = np.broadcast_to(np.asarray(value, dtype=np.float64), (n,)).copy()
    if np.any(~np.isfinite(arr)) or (positive and np.any(arr <= 0.0)):
        qualifier = 'positive ' if positive else ''
        raise ValueError(f'{name} must be finite {qualifier}with shape [N]')
    return arr


def particle_count(populations: np.ndarray) -> np.ndarray:
    pop = _pop(populations)
    nhi, nhii, nhei, nheii, nheiii = pop.T
    return (nhi + nhii) + (nhei + nheii + nheiii) + nhii + nheii + 2.0 * nheiii


def energy_from_temperature(populations: np.ndarray, temperature) -> np.ndarray:
    pop = _pop(populations)
    temp = _vec(temperature, pop.shape[0], 'temperature', positive=True)
    return 1.5 * KB_ERG * particle_count(pop) * temp


@dataclass(frozen=True)
class ThermalContext:
    photoheat: np.ndarray
    expansion_coefficient: np.ndarray
    energy_coefficient: np.ndarray
    factor_rec_h: np.ndarray
    factor_rec_heii: np.ndarray
    factor_rec_heiii: np.ndarray
    factor_exc_h: np.ndarray
    factor_exc_heii: np.ndarray
    factor_ion_h: np.ndarray
    factor_ion_hei: np.ndarray
    factor_ion_heii: np.ndarray
    factor_ff: np.ndarray

    @classmethod
    def build(cls, populations, volume, photoheat, hubble) -> 'ThermalContext':
        pop = _pop(populations)
        n = pop.shape[0]
        vol = _vec(volume, n, 'volume', positive=True)
        heat = _vec(photoheat, n, 'photoheat')
        H = _vec(hubble, n, 'hubble')
        nhi, nhii, nhei, nheii, nheiii = pop.T
        ne = (nhii + nheii + 2.0 * nheiii) / vol
        particles = particle_count(pop)
        return cls(
            photoheat=heat,
            expansion_coefficient=3.0 * H * KB_ERG * particles,
            energy_coefficient=1.5 * KB_ERG * particles,
            factor_rec_h=ne * nhii,
            factor_rec_heii=ne * nheii,
            factor_rec_heiii=ne * nheiii,
            factor_exc_h=ne * nhi,
            factor_exc_heii=ne * nheii,
            factor_ion_h=ne * nhi * 13.598 * EV_ERG,
            factor_ion_hei=ne * nhei * 24.587 * EV_ERG,
            factor_ion_heii=ne * nheii * 54.416 * EV_ERG,
            factor_ff=ne * (nhii + nheii + 4.0 * nheiii),
        )

    def rhs_and_derivative(self, log_temperature: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        x = np.asarray(log_temperature, dtype=np.float64)
        if x.shape != self.photoheat.shape or np.any(~np.isfinite(x)):
            raise ValueError('log_temperature must be finite with the context shape')
        T = np.exp(x)
        ll_h = 315614.0 / T
        ll_hei = 570670.0 / T
        ll_heii = 1263030.0 / T

        x_rec_h = (ll_h / 2.250) ** 0.376
        rec_h = 3.435e-30 * T * ll_h**1.970 / (1.0 + x_rec_h) ** 3.720
        dlog_rec_h = -0.970 + (3.720 * 0.376) * x_rec_h / (1.0 + x_rec_h)

        rec_heii = KB_ERG * T * (1.26e-14 * ll_hei**0.750)
        dlog_rec_heii = 0.250

        x_rec_heiii = (ll_heii / 2.250) ** 0.376
        rec_heiii = 8.0 * 3.435e-30 * T * ll_heii**1.970 / (1.0 + x_rec_heiii) ** 3.720
        dlog_rec_heiii = -0.970 + (3.720 * 0.376) * x_rec_heiii / (1.0 + x_rec_heiii)

        sqrt_t = np.sqrt(T / 1.0e5)
        exc_h = 7.5e-19 * np.exp(-118348.0 / T) / (1.0 + sqrt_t)
        dlog_exc_h = 118348.0 / T - 0.5 * sqrt_t / (1.0 + sqrt_t)

        exc_heii = 5.54e-17 * T**-0.397 * np.exp(-473638.0 / T) / (1.0 + sqrt_t)
        dlog_exc_heii = -0.397 + 473638.0 / T - 0.5 * sqrt_t / (1.0 + sqrt_t)

        beta_h = 5.835e-11 * np.sqrt(T) * np.exp(-157804.0 / T)
        beta_hei = 2.71e-11 * np.sqrt(T) * np.exp(-285331.0 / T)
        beta_heii = 5.707e-12 * np.sqrt(T) * np.exp(-631495.0 / T)
        dlog_beta_h = 0.5 + 157804.0 / T
        dlog_beta_hei = 0.5 + 285331.0 / T
        dlog_beta_heii = 0.5 + 631495.0 / T

        q = 5.5 - np.log10(T)
        gaussian = np.exp(-(q * q) / 3.0)
        gaunt = 1.1 + 0.34 * gaussian
        ff = 1.42e-27 * np.sqrt(T) * gaunt
        dlog_gaussian = 2.0 * q / (3.0 * LN10)
        dlog_ff = 0.5 + (0.34 * gaussian / gaunt) * dlog_gaussian

        terms = (
            self.factor_rec_h * rec_h,
            self.factor_rec_heii * rec_heii,
            self.factor_rec_heiii * rec_heiii,
            self.factor_exc_h * exc_h,
            self.factor_exc_heii * exc_heii,
            self.factor_ion_h * beta_h,
            self.factor_ion_hei * beta_hei,
            self.factor_ion_heii * beta_heii,
            self.factor_ff * ff,
        )
        slopes = (
            dlog_rec_h,
            dlog_rec_heii,
            dlog_rec_heiii,
            dlog_exc_h,
            dlog_exc_heii,
            dlog_beta_h,
            dlog_beta_hei,
            dlog_beta_heii,
            dlog_ff,
        )
        cooling = np.zeros_like(T)
        dcooling = np.zeros_like(T)
        for term, slope in zip(terms, slopes):
            cooling += term
            dcooling += term * slope
        expansion = self.expansion_coefficient * T
        rhs = self.photoheat - cooling - expansion
        derivative = -dcooling - expansion
        return rhs, derivative


def thermal_rhs_and_dlogT(log_temperature, populations, volume, photoheat, hubble):
    return ThermalContext.build(populations, volume, photoheat, hubble).rhs_and_derivative(
        np.asarray(log_temperature, dtype=np.float64)
    )


def _root(
    *, context: ThermalContext, parent_energy, parent_temperature, step,
    constant_rhs, rhs_weight: float,
    relative_tolerance: float = 1.0e-12,
    newton_max_iterations: int = 16,
    bisection_iterations: int = 48,
) -> FastThermalResult:
    n = context.photoheat.size
    U0 = _vec(parent_energy, n, 'parent_energy', positive=True)
    T0 = _vec(parent_temperature, n, 'parent_temperature', positive=True)
    dt = _vec(step, n, 'step', positive=True)
    constant = _vec(constant_rhs, n, 'constant_rhs')
    weight = float(rhs_weight)
    if not math.isfinite(weight) or weight < 0.0:
        raise ValueError('rhs_weight must be finite and nonnegative')

    def evaluate(logt: np.ndarray):
        rhs, drhs = context.rhs_and_derivative(logt)
        T = np.exp(logt)
        energy = context.energy_coefficient * T
        f = energy - U0 - dt * (constant + weight * rhs)
        df = energy - dt * weight * drhs
        scale = np.maximum.reduce([
            np.abs(energy), np.abs(U0), np.abs(dt * constant),
            np.abs(dt * weight * rhs), np.full(n, 1.0e-300),
        ])
        relative = np.abs(f) / scale
        return f, df, rhs, energy, relative

    lo = np.log(np.maximum(T0 * 1.0e-12, 1.0e-12))
    hi = np.log(np.maximum(T0 * 10.0, 1.0e8))
    flo, _, _, _, _ = evaluate(lo)
    fhi, _, _, _, _ = evaluate(hi)
    for _ in range(28):
        need = ~(np.isfinite(fhi) & (fhi >= 0.0))
        if not np.any(need):
            break
        hi = np.where(need, hi + math.log(10.0), hi)
        fhi, _, _, _, _ = evaluate(hi)
    bracketed = np.isfinite(flo) & np.isfinite(fhi) & (flo <= 0.0) & (fhi >= 0.0)

    x = np.minimum(np.maximum(np.log(T0), lo), hi)
    f, df, rhs, energy, relative = evaluate(x)
    total_iterations = 0
    for _ in range(newton_max_iterations):
        total_iterations += 1
        active = bracketed & np.isfinite(relative) & (relative > relative_tolerance)
        if not np.any(active):
            break
        safe_derivative = np.isfinite(df) & (np.abs(df) > 1.0e-300)
        proposal = x - np.divide(f, df, out=np.zeros_like(f), where=safe_derivative)
        use_newton = active & safe_derivative & np.isfinite(proposal) & (proposal > lo) & (proposal < hi)
        candidate = np.where(use_newton, proposal, 0.5 * (lo + hi))
        fc, dfc, rhsc, energyc, relativec = evaluate(candidate)
        move_lo = np.isfinite(fc) & (fc <= 0.0)
        lo = np.where(active & move_lo, candidate, lo)
        hi = np.where(active & ~move_lo, candidate, hi)
        x = np.where(active, candidate, x)
        f = np.where(active, fc, f)
        df = np.where(active, dfc, df)
        rhs = np.where(active, rhsc, rhs)
        energy = np.where(active, energyc, energy)
        relative = np.where(active, relativec, relative)

    for _ in range(bisection_iterations):
        active = bracketed & np.isfinite(relative) & (relative > relative_tolerance)
        if not np.any(active):
            break
        total_iterations += 1
        candidate = 0.5 * (lo + hi)
        fc, dfc, rhsc, energyc, relativec = evaluate(candidate)
        move_lo = np.isfinite(fc) & (fc <= 0.0)
        lo = np.where(active & move_lo, candidate, lo)
        hi = np.where(active & ~move_lo, candidate, hi)
        x = np.where(active, candidate, x)
        f = np.where(active, fc, f)
        df = np.where(active, dfc, df)
        rhs = np.where(active, rhsc, rhs)
        energy = np.where(active, energyc, energy)
        relative = np.where(active, relativec, relative)

    temperature = np.where(bracketed, np.exp(x), T0)
    final_rhs, _ = context.rhs_and_derivative(np.log(temperature))
    final_energy = context.energy_coefficient * temperature
    # Re-evaluate the exact final balance rather than trusting an iteration cache.
    final_f = final_energy - U0 - dt * (constant + weight * final_rhs)
    scale = np.maximum.reduce([
        np.abs(final_energy), np.abs(U0), np.abs(dt * constant),
        np.abs(dt * weight * final_rhs), np.full(n, 1.0e-300),
    ])
    final_relative = np.where(bracketed, np.abs(final_f) / scale, np.inf)
    return FastThermalResult(
        energy=np.where(bracketed, final_energy, U0),
        temperature=temperature,
        rhs=final_rhs,
        relative_residual=final_relative,
        bracketed=bracketed,
        iterations=total_iterations,
    )


def solve_sdirk2_fast(
    *, parent_populations, stage_populations, final_populations,
    parent_energy, parent_temperature, stage_volume, final_volume,
    stage_photoheat, final_photoheat, stage_hubble, final_hubble, dt,
) -> FastSDIRK2ThermalResult:
    p0 = _pop(parent_populations)
    ps = _pop(stage_populations)
    pf = _pop(final_populations)
    if p0.shape != ps.shape or p0.shape != pf.shape:
        raise ValueError('population shape mismatch')
    n = p0.shape[0]
    U0 = _vec(parent_energy, n, 'parent_energy', positive=True)
    T0 = _vec(parent_temperature, n, 'parent_temperature', positive=True)
    step = _vec(dt, n, 'dt', positive=True)
    stage_context = ThermalContext.build(ps, stage_volume, stage_photoheat, stage_hubble)
    stage = _root(
        context=stage_context,
        parent_energy=U0,
        parent_temperature=T0,
        step=GAMMA * step,
        constant_rhs=np.zeros(n, dtype=np.float64),
        rhs_weight=1.0,
    )
    final_context = ThermalContext.build(pf, final_volume, final_photoheat, final_hubble)
    final = _root(
        context=final_context,
        parent_energy=U0,
        parent_temperature=T0,
        step=step,
        constant_rhs=(1.0 - GAMMA) * stage.rhs,
        rhs_weight=GAMMA,
    )
    final = FastThermalResult(
        energy=final.energy,
        temperature=final.temperature,
        rhs=final.rhs,
        relative_residual=final.relative_residual,
        bracketed=final.bracketed & stage.bracketed,
        iterations=final.iterations,
    )
    return FastSDIRK2ThermalResult(stage=stage, final=final)
