#!/usr/bin/env python3
"""Fixed-shape NumPy and JAX thermal balance backends.

The NumPy implementation is the independent array oracle used by the optimized
physical step.  The JAX implementation is compiled once for a locked batch
shape and serves as a parity/performance candidate.  Both implement the exact
R2B-R2 resolved thermal balance with explicit k_B and eV-to-erg conversion.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

KB_ERG = 1.380649e-16
EV_ERG = 1.602176634e-12


def _thermal_rhs_numpy(
    log_temperature: np.ndarray,
    populations: np.ndarray,
    volume: np.ndarray,
    photoheat: np.ndarray,
    hubble: np.ndarray,
) -> np.ndarray:
    T = np.exp(np.asarray(log_temperature, dtype=float))
    pop = np.asarray(populations, dtype=float)
    nhi, nhii, nhei, nheii, nheiii = pop.T
    ne = (nhii + nheii + 2.0 * nheiii) / volume
    ll_h = 315614.0 / T
    ll_hei = 570670.0 / T
    ll_heii = 1263030.0 / T
    rec_h = 3.435e-30 * T * ll_h**1.970 / (1.0 + (ll_h / 2.250) ** 0.376) ** 3.720
    rec_heii = KB_ERG * T * (1.26e-14 * ll_hei**0.750)
    rec_heiii = 8.0 * 3.435e-30 * T * ll_heii**1.970 / (1.0 + (ll_heii / 2.250) ** 0.376) ** 3.720
    exc_h = 7.5e-19 * np.exp(-118348.0 / T) / (1.0 + np.sqrt(T / 1.0e5))
    exc_heii = 5.54e-17 * T**-0.397 * np.exp(-473638.0 / T) / (1.0 + np.sqrt(T / 1.0e5))
    ff = 1.42e-27 * np.sqrt(T) * (1.1 + 0.34 * np.exp(-(5.5 - np.log10(T)) ** 2 / 3.0))
    beta_hi = 5.835e-11 * np.sqrt(T) * np.exp(-157804.0 / T)
    beta_hei = 2.71e-11 * np.sqrt(T) * np.exp(-285331.0 / T)
    beta_heii = 5.707e-12 * np.sqrt(T) * np.exp(-631495.0 / T)
    cool = (
        ne * nhii * rec_h
        + ne * nheii * rec_heii
        + ne * nheiii * rec_heiii
        + ne * nhi * exc_h
        + ne * nheii * exc_heii
        + ne * nhi * beta_hi * 13.598 * EV_ERG
        + ne * nhei * beta_hei * 24.587 * EV_ERG
        + ne * nheii * beta_heii * 54.416 * EV_ERG
        + ne * (nhii + nheii + 4.0 * nheiii) * ff
    )
    nh = nhi + nhii
    nhe = nhei + nheii + nheiii
    particles = nh + nhe + nhii + nheii + 2.0 * nheiii
    expansion = 3.0 * hubble * KB_ERG * T * particles
    return photoheat - cool - expansion


def thermal_terms_numpy(
    log_temperature: np.ndarray,
    populations: np.ndarray,
    volume: np.ndarray,
    hubble: np.ndarray | float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return positive cooling and expansion-work rates for ledger ownership."""
    logt=np.asarray(log_temperature,dtype=float)
    pop=np.asarray(populations,dtype=float)
    vol=np.asarray(volume,dtype=float)
    H=np.broadcast_to(np.asarray(hubble,dtype=float),logt.shape)
    zero=np.zeros_like(logt)
    total_loss=-_thermal_rhs_numpy(logt,pop,vol,zero,H)
    T=np.exp(logt)
    nhi,nhii,nhei,nheii,nheiii=pop.T
    particles=(nhi+nhii)+(nhei+nheii+nheiii)+nhii+nheii+2.0*nheiii
    expansion=3.0*H*KB_ERG*T*particles
    cooling=total_loss-expansion
    return cooling,expansion


def _balance_numpy(log_temperature, populations, volume, photoheat, hubble, parent_energy, dt):
    T = np.exp(np.asarray(log_temperature, dtype=float))
    pop = np.asarray(populations, dtype=float)
    nhi, nhii, nhei, nheii, nheiii = pop.T
    particles = (nhi + nhii) + (nhei + nheii + nheiii) + nhii + nheii + 2.0 * nheiii
    energy = 1.5 * KB_ERG * particles * T
    rhs = _thermal_rhs_numpy(log_temperature, pop, volume, photoheat, hubble)
    return energy - parent_energy - dt * rhs


@dataclass(frozen=True)
class ThermalRootResult:
    energy: np.ndarray
    temperature: np.ndarray
    rhs: np.ndarray
    relative_residual: np.ndarray
    bracketed: np.ndarray


class NumpyThermalBackend:
    name = "NUMPY_ARRAY_ORACLE"
    compile_count = 0

    def evaluate(self, log_temperature, populations, volume, photoheat, hubble, parent_energy, dt):
        return _balance_numpy(
            np.asarray(log_temperature, dtype=float),
            np.asarray(populations, dtype=float),
            np.asarray(volume, dtype=float),
            np.asarray(photoheat, dtype=float),
            np.asarray(hubble, dtype=float),
            np.asarray(parent_energy, dtype=float),
            np.asarray(dt, dtype=float),
        )

    def solve(
        self,
        *,
        populations: np.ndarray,
        parent_energy: np.ndarray,
        parent_temperature: np.ndarray,
        volume: np.ndarray,
        photoheat: np.ndarray,
        hubble: np.ndarray | float,
        dt: np.ndarray | float,
    ) -> ThermalRootResult:
        pop = np.asarray(populations, dtype=float)
        n = pop.shape[0]
        arrays = [np.asarray(v, dtype=float) for v in (parent_energy, parent_temperature, volume, photoheat)]
        if pop.shape != (n, 5) or any(v.shape != (n,) for v in arrays):
            raise ValueError("thermal batch has inconsistent shape")
        H = np.broadcast_to(np.asarray(hubble, dtype=float), (n,)).copy()
        step = np.broadcast_to(np.asarray(dt, dtype=float), (n,)).copy()
        U0, T0, vol, heat = arrays
        log_lo = np.log(np.maximum(T0 * 1.0e-12, 1.0e-8))
        log_hi = np.log(np.maximum(T0 * 10.0, 1.0e8))
        f_lo = self.evaluate(log_lo, pop, vol, heat, H, U0, step)
        f_hi = self.evaluate(log_hi, pop, vol, heat, H, U0, step)
        for _ in range(24):
            need = ~(np.isfinite(f_hi) & (f_hi >= 0.0))
            if not np.any(need):
                break
            log_hi = np.where(need, log_hi + np.log(10.0), log_hi)
            f_hi = self.evaluate(log_hi, pop, vol, heat, H, U0, step)
        bracketed = np.isfinite(f_lo) & np.isfinite(f_hi) & (f_lo <= 0.0) & (f_hi >= 0.0)
        lo = log_lo.copy(); hi = log_hi.copy()
        for _ in range(72):
            mid = 0.5 * (lo + hi)
            f_mid = self.evaluate(mid, pop, vol, heat, H, U0, step)
            move_lo = np.isfinite(f_mid) & (f_mid <= 0.0)
            lo = np.where(bracketed & move_lo, mid, lo)
            hi = np.where(bracketed & ~move_lo, mid, hi)
        log_root = 0.5 * (lo + hi)
        temperature = np.where(bracketed, np.exp(log_root), T0)
        nhi, nhii, nhei, nheii, nheiii = pop.T
        particles = (nhi+nhii)+(nhei+nheii+nheiii)+nhii+nheii+2*nheiii
        energy = 1.5 * KB_ERG * particles * temperature
        balance = self.evaluate(np.log(temperature), pop, vol, heat, H, U0, step)
        scale = np.maximum.reduce([np.abs(energy), np.abs(U0), np.abs(step*heat), np.full(n,1e-300)])
        relative = np.abs(balance) / scale
        rhs = np.divide(energy-U0, step, out=np.zeros(n), where=step != 0.0)
        relative = np.where(step == 0.0, 0.0, relative)
        return ThermalRootResult(energy, temperature, rhs, relative, bracketed)


class JaxThermalBackend:
    name = "JAX_STATIC_SHAPE_CANDIDATE"

    def __init__(self) -> None:
        import jax
        jax.config.update("jax_enable_x64", True)
        import jax.numpy as jnp
        self.jax = jax
        self.jnp = jnp
        self.compile_count = 0
        self._shape: tuple[tuple[int, ...], ...] | None = None

        def balance(log_temperature, populations, volume, photoheat, hubble, parent_energy, dt):
            T = jnp.exp(log_temperature)
            nhi, nhii, nhei, nheii, nheiii = populations.T
            ne = (nhii+nheii+2*nheiii)/volume
            llh=315614.0/T; llhei=570670.0/T; llheii=1263030.0/T
            rec_h=3.435e-30*T*llh**1.970/(1+(llh/2.250)**0.376)**3.720
            rec_heii=KB_ERG*T*(1.26e-14*llhei**0.750)
            rec_heiii=8*3.435e-30*T*llheii**1.970/(1+(llheii/2.250)**0.376)**3.720
            exc_h=7.5e-19*jnp.exp(-118348.0/T)/(1+jnp.sqrt(T/1e5))
            exc_heii=5.54e-17*T**-0.397*jnp.exp(-473638.0/T)/(1+jnp.sqrt(T/1e5))
            ff=1.42e-27*jnp.sqrt(T)*(1.1+0.34*jnp.exp(-(5.5-jnp.log10(T))**2/3.0))
            beta_hi=5.835e-11*jnp.sqrt(T)*jnp.exp(-157804.0/T)
            beta_hei=2.71e-11*jnp.sqrt(T)*jnp.exp(-285331.0/T)
            beta_heii=5.707e-12*jnp.sqrt(T)*jnp.exp(-631495.0/T)
            cool=(ne*nhii*rec_h+ne*nheii*rec_heii+ne*nheiii*rec_heiii+ne*nhi*exc_h+
                  ne*nheii*exc_heii+ne*nhi*beta_hi*13.598*EV_ERG+
                  ne*nhei*beta_hei*24.587*EV_ERG+ne*nheii*beta_heii*54.416*EV_ERG+
                  ne*(nhii+nheii+4*nheiii)*ff)
            particles=(nhi+nhii)+(nhei+nheii+nheiii)+nhii+nheii+2*nheiii
            rhs=photoheat-cool-3*hubble*KB_ERG*T*particles
            energy=1.5*KB_ERG*particles*T
            return energy-parent_energy-dt*rhs
        self._compiled = jax.jit(balance)
        self.root_compile_count = 0
        self.device_get_count = 0
        self.root_iterations = 41
        self._root_shape: tuple[tuple[int, ...], ...] | None = None

        def solve_root(populations, parent_energy, parent_temperature, volume, photoheat, hubble, dt):
            n = parent_energy.shape[0]
            log_lo = jnp.log(jnp.maximum(parent_temperature * 1.0e-12, 1.0e-8))
            log_hi = jnp.log(jnp.maximum(parent_temperature * 10.0, 1.0e8))
            f_lo = balance(log_lo, populations, volume, photoheat, hubble, parent_energy, dt)
            f_hi0 = balance(log_hi, populations, volume, photoheat, hubble, parent_energy, dt)

            def expand(_i, carry):
                hi, f_hi = carry
                need = ~(jnp.isfinite(f_hi) & (f_hi >= 0.0))
                next_hi = jnp.where(need, hi + jnp.log(10.0), hi)
                next_f = balance(next_hi, populations, volume, photoheat, hubble, parent_energy, dt)
                return next_hi, jnp.where(need, next_f, f_hi)

            log_hi2, f_hi = jax.lax.fori_loop(0, 24, expand, (log_hi, f_hi0))
            bracketed = jnp.isfinite(f_lo) & jnp.isfinite(f_hi) & (f_lo <= 0.0) & (f_hi >= 0.0)

            def bisect(_i, carry):
                lo, hi = carry
                mid = 0.5 * (lo + hi)
                f_mid = balance(mid, populations, volume, photoheat, hubble, parent_energy, dt)
                move_lo = jnp.isfinite(f_mid) & (f_mid <= 0.0)
                lo2 = jnp.where(bracketed & move_lo, mid, lo)
                hi2 = jnp.where(bracketed & ~move_lo, mid, hi)
                return lo2, hi2

            lo, hi = jax.lax.fori_loop(0, self.root_iterations, bisect, (log_lo, log_hi2))
            log_root = 0.5 * (lo + hi)
            temperature = jnp.where(bracketed, jnp.exp(log_root), parent_temperature)
            nhi, nhii, nhei, nheii, nheiii = populations.T
            particles = (nhi + nhii) + (nhei + nheii + nheiii) + nhii + nheii + 2.0 * nheiii
            energy = 1.5 * KB_ERG * particles * temperature
            residual = balance(jnp.log(temperature), populations, volume, photoheat, hubble, parent_energy, dt)
            scale = jnp.maximum(jnp.maximum(jnp.abs(energy), jnp.abs(parent_energy)),
                                jnp.maximum(jnp.abs(dt * photoheat), jnp.full((n,), 1.0e-300)))
            relative = jnp.where(dt == 0.0, 0.0, jnp.abs(residual) / scale)
            rhs = jnp.where(dt == 0.0, 0.0, (energy - parent_energy) / dt)
            return energy, temperature, rhs, relative, bracketed

        self._compiled_root = jax.jit(solve_root)

    @classmethod
    def from_repo(cls, _repo_root: Path) -> "JaxThermalBackend":
        return cls()

    def _arrays(self, args):
        return tuple(np.asarray(v, dtype=float) for v in args)

    def warmup(self, *args) -> None:
        arrays = self._arrays(args)
        shapes = tuple(a.shape for a in arrays)
        if self._shape is None:
            self._shape = shapes
            out = self._compiled(*[self.jnp.asarray(a) for a in arrays])
            out.block_until_ready()
            self.compile_count = 1
        elif shapes != self._shape:
            raise ValueError("thermal candidate batch shape changed after compile lock")

    def evaluate(self, *args) -> np.ndarray:
        arrays = self._arrays(args)
        shapes = tuple(a.shape for a in arrays)
        if self._shape is None:
            self.warmup(*arrays)
        elif shapes != self._shape:
            raise ValueError("thermal candidate batch shape changed after compile lock")
        out = self._compiled(*[self.jnp.asarray(a) for a in arrays])
        return np.asarray(out)

    def solve(
        self,
        *,
        populations: np.ndarray,
        parent_energy: np.ndarray,
        parent_temperature: np.ndarray,
        volume: np.ndarray,
        photoheat: np.ndarray,
        hubble: np.ndarray | float,
        dt: np.ndarray | float,
    ) -> ThermalRootResult:
        pop=np.asarray(populations,dtype=float)
        n=pop.shape[0]
        U0=np.asarray(parent_energy,dtype=float)
        T0=np.asarray(parent_temperature,dtype=float)
        vol=np.asarray(volume,dtype=float)
        heat=np.asarray(photoheat,dtype=float)
        H=np.broadcast_to(np.asarray(hubble,dtype=float),(n,)).copy()
        step=np.broadcast_to(np.asarray(dt,dtype=float),(n,)).copy()
        arrays=(pop,U0,T0,vol,heat,H,step)
        shapes=tuple(a.shape for a in arrays)
        if pop.shape!=(n,5) or any(a.shape!=(n,) for a in arrays[1:]):
            raise ValueError("thermal root batch has inconsistent shape")
        if self._root_shape is None:
            self._root_shape=shapes
            device=self._compiled_root(*[self.jnp.asarray(a) for a in arrays])
            self.jax.block_until_ready(device)
            self.root_compile_count=1
        elif shapes != self._root_shape:
            raise ValueError("thermal root batch shape changed after compile lock")
        else:
            device=self._compiled_root(*[self.jnp.asarray(a) for a in arrays])
        host = self.jax.device_get(device)
        self.device_get_count += 1
        energy, temperature, rhs, relative, bracketed = tuple(
            np.asarray(x) for x in host
        )
        return ThermalRootResult(energy,temperature,rhs,relative,bracketed)
