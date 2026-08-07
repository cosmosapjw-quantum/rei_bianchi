#!/usr/bin/env python3
"""Positive full-OTS H/He chemistry and resolved thermal microphysics.

All material quantities are extensive per comoving Mpc^3 node measure.  Local
collisional/recombination rates are evaluated from proper number densities and
then multiplied by the node proper volume.  Externally supplied photo rates are
already owner-correct absorbed-photon event rates.  No subgrid source exists in
this interface.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np

KB_ERG = 1.380649e-16
EV_ERG = 1.602176634e-12
MPC_CM = 3.085677581491367e24

# Verner cross sections used by the inherited Friedrich-style full-OTS algebra.
SIGMA_OTS_H24 = 1.2391519584513023e-18
SIGMA_OTS_HEI24 = 7.43469869411065e-18
SIGMA_OTS_H41 = 2.884642817876362e-19
SIGMA_OTS_HEI41 = 3.0402144676144673e-18
SIGMA_OTS_H54 = 1.2306959247142394e-19
SIGMA_OTS_HEI54 = 1.6907806870529807e-18
SIGMA_OTS_HEII54 = 1.5872802575386495e-18


@dataclass(frozen=True)
class MaterialBatch:
    N_HI: np.ndarray
    N_HII: np.ndarray
    N_HeI: np.ndarray
    N_HeII: np.ndarray
    N_HeIII: np.ndarray
    U_resolved: np.ndarray
    T_K: np.ndarray

    @classmethod
    def from_fractions(
        cls,
        *,
        N_H: np.ndarray,
        N_He: np.ndarray,
        x_HII: np.ndarray,
        x_HeI: np.ndarray,
        x_HeII: np.ndarray,
        x_HeIII: np.ndarray,
        T_K: np.ndarray,
    ) -> "MaterialBatch":
        nh = np.asarray(N_H, dtype=float)
        nhe = np.asarray(N_He, dtype=float)
        xh = np.asarray(x_HII, dtype=float)
        hei = np.asarray(x_HeI, dtype=float)
        heii = np.asarray(x_HeII, dtype=float)
        heiii = np.asarray(x_HeIII, dtype=float)
        temp = np.asarray(T_K, dtype=float)
        shape = nh.shape
        if any(a.shape != shape for a in (nhe, xh, hei, heii, heiii, temp)):
            raise ValueError("material fields must have one common shape")
        if np.any(~np.isfinite(nh)) or np.any(~np.isfinite(nhe)) or np.any(nh <= 0.0) or np.any(nhe <= 0.0):
            raise ValueError("nuclei totals must be finite and positive")
        if np.any(~np.isfinite(temp)) or np.any(temp <= 0.0):
            raise ValueError("temperature must be finite and positive")
        if np.any((xh <= 0.0) | (xh >= 1.0)):
            raise ValueError("hydrogen fraction must be strictly interior")
        if np.any((hei <= 0.0) | (heii <= 0.0) | (heiii <= 0.0)):
            raise ValueError("helium fractions must be strictly positive")
        if np.max(np.abs(hei + heii + heiii - 1.0)) > 2e-12:
            raise ValueError("helium fractions do not close")
        nhi = nh * (1.0 - xh)
        nhii = nh - nhi
        nhei = nhe * hei
        nheii = nhe * heii
        nheiii = nhe - nhei - nheii
        ne = nhii + nheii + 2.0 * nheiii
        particles = nh + nhe + ne
        u = 1.5 * KB_ERG * particles * temp
        return cls(nhi, nhii, nhei, nheii, nheiii, u, temp)

    @property
    def N_H(self) -> np.ndarray:
        return self.N_HI + self.N_HII

    @property
    def N_He(self) -> np.ndarray:
        return self.N_HeI + self.N_HeII + self.N_HeIII

    @property
    def size(self) -> int:
        return int(np.asarray(self.N_HI).size)


@dataclass(frozen=True)
class PhotoInputs:
    HI: np.ndarray
    HeI: np.ndarray
    HeII: np.ndarray
    heating_erg_s: np.ndarray

    @classmethod
    def zeros(cls, size: int) -> "PhotoInputs":
        z = np.zeros(int(size), dtype=float)
        return cls(z.copy(), z.copy(), z.copy(), z.copy())

    def validate(self, size: int) -> None:
        for name in ("HI", "HeI", "HeII", "heating_erg_s"):
            value = np.asarray(getattr(self, name), dtype=float)
            if value.shape != (int(size),):
                raise ValueError(f"photo input {name} has wrong shape")
            if np.any(~np.isfinite(value)) or np.any(value < 0.0):
                raise ValueError(f"photo input {name} must be finite and nonnegative")


def _sigmoid_np(x: np.ndarray) -> np.ndarray:
    return np.exp(-np.logaddexp(0.0, -np.asarray(x, dtype=float)))


def state_to_coordinates(state: MaterialBatch) -> np.ndarray:
    nh, nhe = state.N_H, state.N_He
    xh = state.N_HII / nh
    hei = state.N_HeI / nhe
    heii = state.N_HeII / nhe
    heiii = state.N_HeIII / nhe
    if np.any((xh <= 0.0) | (xh >= 1.0)) or np.any((hei <= 0.0) | (heii <= 0.0) | (heiii <= 0.0)):
        raise ValueError("coordinate transform requires strictly interior fractions")
    return np.column_stack(
        [
            np.log(xh) - np.log1p(-xh),
            np.log(heii) - np.log(hei),
            np.log(heiii) - np.log(hei),
            np.log(state.T_K),
        ]
    )


def coordinates_to_state(q: np.ndarray, *, N_H: np.ndarray, N_He: np.ndarray) -> MaterialBatch:
    coord = np.asarray(q, dtype=float)
    nh, nhe = np.asarray(N_H, dtype=float), np.asarray(N_He, dtype=float)
    if coord.ndim == 1:
        coord = coord[None, :]
    if coord.shape != (nh.size, 4) or nhe.shape != nh.shape:
        raise ValueError("coordinate or nuclei shape mismatch")
    xh = _sigmoid_np(coord[:, 0])
    logits = np.column_stack([np.zeros(nh.size), coord[:, 1], coord[:, 2]])
    shift = np.max(logits, axis=1, keepdims=True)
    expv = np.exp(logits - shift)
    he = expv / np.sum(expv, axis=1, keepdims=True)
    temp = np.exp(coord[:, 3])
    return MaterialBatch.from_fractions(
        N_H=nh,
        N_He=nhe,
        x_HII=xh,
        x_HeI=he[:, 0],
        x_HeII=he[:, 1],
        x_HeIII=he[:, 2],
        T_K=temp,
    )


def _lambda_hi(T: Any) -> Any:
    return 315614.0 / T


def _lambda_hei(T: Any) -> Any:
    return 570670.0 / T


def _lambda_heii(T: Any) -> Any:
    return 1263030.0 / T


def _alpha_b_hii(T: Any) -> Any:
    ll = _lambda_hi(T)
    return 2.753e-14 * ll**1.5 / (1.0 + (ll / 2.740) ** 0.407) ** 2.242


def _alpha_a_heii(T: Any) -> Any:
    ll = _lambda_hei(T)
    base = 3.0e-14 * ll**0.654
    dr = 1.9e-3 * T**-1.5 * jnp.exp(-473638.0 / T) * (1.0 + 0.3 * jnp.exp(-94728.0 / T))
    gate = jax.nn.sigmoid((T - 1.5e4) / 250.0)
    return base + gate * dr


def _alpha_b_heii(T: Any) -> Any:
    ll = _lambda_hei(T)
    base = 1.26e-14 * ll**0.750
    dr = 1.9e-3 * T**-1.5 * jnp.exp(-473638.0 / T) * (1.0 + 0.3 * jnp.exp(-94728.0 / T))
    gate = jax.nn.sigmoid((T - 1.5e4) / 250.0)
    return base + gate * dr


def _alpha_a_heiii(T: Any) -> Any:
    ll = _lambda_heii(T)
    return 2.0 * 1.269e-13 * ll**1.503 / (1.0 + (ll / 0.522) ** 0.470) ** 1.923


def _alpha_b_heiii(T: Any) -> Any:
    ll = _lambda_heii(T)
    return 2.0 * 2.753e-14 * ll**1.5 / (1.0 + (ll / 2.740) ** 0.407) ** 2.242


def _alpha_heiii_n2(T: Any) -> Any:
    return 3.4e-13 * (T / 1.0e4) ** -0.6


def _beta_hi(T: Any) -> Any:
    return 5.835e-11 * jnp.sqrt(T) * jnp.exp(-157804.0 / T)


def _beta_hei(T: Any) -> Any:
    return 2.71e-11 * jnp.sqrt(T) * jnp.exp(-285331.0 / T)


def _beta_heii(T: Any) -> Any:
    return 5.707e-12 * jnp.sqrt(T) * jnp.exp(-631495.0 / T)


def _decode_jax(q: Any, nh: Any, nhe: Any) -> tuple[Any, ...]:
    xh = jax.nn.sigmoid(q[0])
    he = jax.nn.softmax(jnp.array([0.0, q[1], q[2]], dtype=q.dtype))
    T = jnp.exp(q[3])
    nhi = nh * (1.0 - xh)
    nhii = nh - nhi
    nhei = nhe * he[0]
    nheii = nhe * he[1]
    nheiii = nhe - nhei - nheii
    ne_count = nhii + nheii + 2.0 * nheiii
    U = 1.5 * KB_ERG * (nh + nhe + ne_count) * T
    return nhi, nhii, nhei, nheii, nheiii, U, T


def _population_rhs_single(
    q: Any,
    nh: Any,
    nhe: Any,
    volume: Any,
    photo_hi: Any,
    photo_hei: Any,
    photo_heii: Any,
) -> Any:
    nhi, nhii, nhei, nheii, nheiii, _U, T = _decode_jax(q, nh, nhe)
    ne = (nhii + nheii + 2.0 * nheiii) / volume

    rates = [
        photo_hi + nhi * ne * _beta_hi(T),
        photo_hei + nhei * ne * _beta_hei(T),
        photo_heii + nheii * ne * _beta_heii(T),
    ]
    vectors = [
        jnp.array([-1.0, 1.0, 0.0, 0.0, 0.0]),
        jnp.array([0.0, 0.0, -1.0, 1.0, 0.0]),
        jnp.array([0.0, 0.0, 0.0, -1.0, 1.0]),
    ]

    floor = 1e-300
    op_h24 = nhi / volume * SIGMA_OTS_H24
    op_he24 = nhei / volume * SIGMA_OTS_HEI24
    y = op_h24 / (op_h24 + op_he24 + floor)
    op_h41 = nhi / volume * SIGMA_OTS_H41
    op_he41 = nhei / volume * SIGMA_OTS_HEI41
    zfrac = op_h41 / (op_h41 + op_he41 + floor)
    op_h54 = nhi / volume * SIGMA_OTS_H54
    op_he54 = nhei / volume * SIGMA_OTS_HEI54
    op_heii54 = nheii / volume * SIGMA_OTS_HEII54
    total54 = op_h54 + op_he54 + op_heii54 + floor
    y2a = op_heii54 / total54
    y2b = op_he54 / total54

    p_exc = 0.96
    l_cas, m_cas = 1.425, 0.737
    vT = jax.nn.sigmoid((T - 2.0e4) / 4.0e3)
    fH = 1.0 - jnp.exp(-100.0 * nhi / nh)
    w = (l_cas - m_cas) + m_cas * y
    A_H = vT * w + (1.0 - vT) * fH * zfrac
    A_HeI = vT * m_cas * (1.0 - y) + (1.0 - vT) * fH * (1.0 - zfrac)

    aA2, aB2 = _alpha_a_heii(T), _alpha_b_heii(T)
    aA3, aB3 = _alpha_a_heiii(T), _alpha_b_heiii(T)
    aN2 = jnp.minimum(_alpha_heiii_n2(T), aB3)
    aCas = jnp.maximum(aB3 - aN2, 0.0)
    rates += [
        nhii * ne * _alpha_b_hii(T),
        nheii * ne * jnp.maximum(aA2 - aB2, 0.0),
        nheii * ne * aB2,
        nheiii * ne * jnp.maximum(aA3 - aB3, 0.0),
        nheiii * ne * aN2,
        nheiii * ne * aCas,
    ]
    vectors += [
        jnp.array([1.0, -1.0, 0.0, 0.0, 0.0]),
        jnp.array([-y, y, y, -y, 0.0]),
        jnp.array([-p_exc, p_exc, 1.0, -1.0, 0.0]),
        jnp.array([-(1.0-y2a-y2b), 1.0-y2a-y2b, -y2b, 1.0+y2b-y2a, -1.0+y2a]),
        jnp.array([-1.0, 1.0, 0.0, 1.0, -1.0]),
        jnp.array([-A_H, A_H, -A_HeI, 1.0+A_HeI, -1.0]),
    ]
    out = jnp.zeros(5, dtype=q.dtype)
    for rate, vector in zip(rates, vectors):
        out = out + rate * vector
    return out


def _thermal_rhs_from_populations_single(
    log_temperature: Any,
    populations: Any,
    volume: Any,
    photoheat: Any,
    hubble: Any,
) -> Any:
    """Resolved thermal rate at fixed material populations.

    `populations` are extensive counts per comoving Mpc^3 node measure, while
    `volume` is the node proper volume in cm^3.  Consequently `ne` is cm^-3
    and each cooling term is erg s^-1 cMpc^-3.  The logarithmic temperature
    coordinate keeps the thermal solve strictly inside T>0 without clipping.
    """
    T = jnp.exp(log_temperature)
    nhi, nhii, nhei, nheii, nheiii = populations
    ne = (nhii + nheii + 2.0 * nheiii) / volume
    llH, llHeII = _lambda_hi(T), _lambda_heii(T)
    recH = 3.435e-30 * T * llH**1.970 / (1.0 + (llH / 2.250) ** 0.376) ** 3.720
    recHeII = KB_ERG * T * (1.26e-14 * _lambda_hei(T) ** 0.750)
    recHeIII = 8.0 * 3.435e-30 * T * llHeII**1.970 / (1.0 + (llHeII / 2.250) ** 0.376) ** 3.720
    excH = 7.5e-19 * jnp.exp(-118348.0 / T) / (1.0 + jnp.sqrt(T / 1.0e5))
    excHeII = 5.54e-17 * T**-0.397 * jnp.exp(-473638.0 / T) / (1.0 + jnp.sqrt(T / 1.0e5))
    ff = 1.42e-27 * jnp.sqrt(T) * (
        1.1 + 0.34 * jnp.exp(-(5.5 - jnp.log10(T)) ** 2 / 3.0)
    )
    cool = (
        ne * nhii * recH
        + ne * nheii * recHeII
        + ne * nheiii * recHeIII
        + ne * nhi * excH
        + ne * nheii * excHeII
        + ne * nhi * _beta_hi(T) * 13.598 * EV_ERG
        + ne * nhei * _beta_hei(T) * 24.587 * EV_ERG
        + ne * nheii * _beta_heii(T) * 54.416 * EV_ERG
        + ne * (nhii + nheii + 4.0 * nheiii) * ff
    )
    nh = nhi + nhii
    nhe = nhei + nheii + nheiii
    particles = nh + nhe + nhii + nheii + 2.0 * nheiii
    expansion = 3.0 * hubble * KB_ERG * T * particles
    return photoheat - cool - expansion


def _thermal_rhs_single(
    q: Any,
    nh: Any,
    nhe: Any,
    volume: Any,
    photoheat: Any,
    hubble: Any,
) -> Any:
    nhi, nhii, nhei, nheii, nheiii, _U, T = _decode_jax(q, nh, nhe)
    return _thermal_rhs_from_populations_single(
        jnp.log(T),
        jnp.array([nhi, nhii, nhei, nheii, nheiii], dtype=q.dtype),
        volume,
        photoheat,
        hubble,
    )


def _thermal_balance_single(
    log_temperature: Any,
    populations: Any,
    volume: Any,
    photoheat: Any,
    hubble: Any,
    parent_energy: Any,
    dt: Any,
) -> Any:
    """Backward-Euler thermal balance at fixed post-chemistry populations."""
    T = jnp.exp(log_temperature)
    nhi, nhii, nhei, nheii, nheiii = populations
    particles = (nhi + nhii) + (nhei + nheii + nheiii) + nhii + nheii + 2.0 * nheiii
    energy = 1.5 * KB_ERG * particles * T
    rhs = _thermal_rhs_from_populations_single(
        log_temperature, populations, volume, photoheat, hubble
    )
    return energy - parent_energy - dt * rhs


_batch_rhs = jax.jit(jax.vmap(_population_rhs_single, in_axes=(0,0,0,0,0,0,0)))


def full_ots_population_rhs(
    state: MaterialBatch, *, proper_volume_cm3: np.ndarray, photo: PhotoInputs
) -> np.ndarray:
    photo.validate(state.size)
    volume = np.asarray(proper_volume_cm3, dtype=float)
    if volume.shape != (state.size,) or np.any(~np.isfinite(volume)) or np.any(volume <= 0.0):
        raise ValueError("proper volume must be finite and positive")
    q = state_to_coordinates(state)
    return np.asarray(
        _batch_rhs(
            jnp.asarray(q), jnp.asarray(state.N_H), jnp.asarray(state.N_He),
            jnp.asarray(volume), jnp.asarray(photo.HI), jnp.asarray(photo.HeI), jnp.asarray(photo.HeII)
        )
    )

@dataclass(frozen=True)
class LinearizedUpdate:
    state: MaterialBatch
    feasible: np.ndarray
    minimum_species: np.ndarray
    hydrogen_residual: np.ndarray
    helium_residual: np.ndarray
    thermal_rhs_erg_s: np.ndarray
    thermal_balance_relative_residual: np.ndarray
    thermal_bracketed: np.ndarray


def _linear_matrix_single(
    q: Any,
    nh: Any,
    nhe: Any,
    volume: Any,
    photo_hi: Any,
    photo_hei: Any,
    photo_heii: Any,
) -> Any:
    """Frozen-coefficient full-OTS event matrix at one Picard iterate."""
    nhi, nhii, nhei, nheii, nheiii, _U, T = _decode_jax(q, nh, nhe)
    ne = (nhii + nheii + 2.0 * nheiii) / volume
    floor_h = jnp.maximum(nh * 1e-300, 1e-300)
    floor_he = jnp.maximum(nhe * 1e-300, 1e-300)

    rates_per_source = [
        photo_hi / jnp.maximum(nhi, floor_h) + ne * _beta_hi(T),
        photo_hei / jnp.maximum(nhei, floor_he) + ne * _beta_hei(T),
        photo_heii / jnp.maximum(nheii, floor_he) + ne * _beta_heii(T),
    ]
    sources = [0, 2, 3]
    vectors = [
        jnp.array([-1.0, 1.0, 0.0, 0.0, 0.0]),
        jnp.array([0.0, 0.0, -1.0, 1.0, 0.0]),
        jnp.array([0.0, 0.0, 0.0, -1.0, 1.0]),
    ]

    floor = 1e-300
    op_h24 = nhi / volume * SIGMA_OTS_H24
    op_he24 = nhei / volume * SIGMA_OTS_HEI24
    y = op_h24 / (op_h24 + op_he24 + floor)
    op_h41 = nhi / volume * SIGMA_OTS_H41
    op_he41 = nhei / volume * SIGMA_OTS_HEI41
    zfrac = op_h41 / (op_h41 + op_he41 + floor)
    op_h54 = nhi / volume * SIGMA_OTS_H54
    op_he54 = nhei / volume * SIGMA_OTS_HEI54
    op_heii54 = nheii / volume * SIGMA_OTS_HEII54
    total54 = op_h54 + op_he54 + op_heii54 + floor
    y2a = op_heii54 / total54
    y2b = op_he54 / total54

    p_exc = 0.96
    l_cas, m_cas = 1.425, 0.737
    vT = jax.nn.sigmoid((T - 2.0e4) / 4.0e3)
    fH = 1.0 - jnp.exp(-100.0 * nhi / nh)
    w = (l_cas - m_cas) + m_cas * y
    A_H = vT * w + (1.0 - vT) * fH * zfrac
    A_HeI = vT * m_cas * (1.0 - y) + (1.0 - vT) * fH * (1.0 - zfrac)

    aA2, aB2 = _alpha_a_heii(T), _alpha_b_heii(T)
    aA3, aB3 = _alpha_a_heiii(T), _alpha_b_heiii(T)
    aN2 = jnp.minimum(_alpha_heiii_n2(T), aB3)
    aCas = jnp.maximum(aB3 - aN2, 0.0)
    rates_per_source += [
        ne * _alpha_b_hii(T),
        ne * jnp.maximum(aA2 - aB2, 0.0),
        ne * aB2,
        ne * jnp.maximum(aA3 - aB3, 0.0),
        ne * aN2,
        ne * aCas,
    ]
    sources += [1, 3, 3, 4, 4, 4]
    vectors += [
        jnp.array([1.0, -1.0, 0.0, 0.0, 0.0]),
        jnp.array([-y, y, y, -y, 0.0]),
        jnp.array([-p_exc, p_exc, 1.0, -1.0, 0.0]),
        jnp.array([-(1.0-y2a-y2b), 1.0-y2a-y2b, -y2b, 1.0+y2b-y2a, -1.0+y2a]),
        jnp.array([-1.0, 1.0, 0.0, 1.0, -1.0]),
        jnp.array([-A_H, A_H, -A_HeI, 1.0+A_HeI, -1.0]),
    ]
    matrix = jnp.zeros((5, 5), dtype=q.dtype)
    for rate, source, vector in zip(rates_per_source, sources, vectors):
        matrix = matrix.at[:, source].add(rate * vector)
    return matrix


_batch_linear_matrix = jax.jit(
    jax.vmap(_linear_matrix_single, in_axes=(0,0,0,0,0,0,0))
)
_batch_thermal_rhs = jax.jit(
    jax.vmap(_thermal_rhs_single, in_axes=(0,0,0,0,0,0))
)
_batch_thermal_balance = jax.jit(
    jax.vmap(_thermal_balance_single, in_axes=(0,0,0,0,0,0,0))
)


def _material_from_populations(pop: np.ndarray, U: np.ndarray) -> MaterialBatch:
    populations = np.asarray(pop, dtype=float)
    energy = np.asarray(U, dtype=float)
    nh = populations[:, 0] + populations[:, 1]
    nhe = populations[:, 2] + populations[:, 3] + populations[:, 4]
    ne = populations[:, 1] + populations[:, 3] + 2.0 * populations[:, 4]
    particles = nh + nhe + ne
    T = 2.0 * energy / (3.0 * KB_ERG * particles)
    return MaterialBatch(
        N_HI=populations[:, 0],
        N_HII=populations[:, 1],
        N_HeI=populations[:, 2],
        N_HeII=populations[:, 3],
        N_HeIII=populations[:, 4],
        U_resolved=energy,
        T_K=T,
    )


def blend_material_states(a: MaterialBatch, b: MaterialBatch, weight_b: float) -> MaterialBatch:
    """Convex damping inside the positive material cone; not clipping."""
    w = float(weight_b)
    if not (0.0 < w <= 1.0):
        raise ValueError("damping weight must lie in (0,1]")
    pop_a = np.column_stack([a.N_HI, a.N_HII, a.N_HeI, a.N_HeII, a.N_HeIII])
    pop_b = np.column_stack([b.N_HI, b.N_HII, b.N_HeI, b.N_HeII, b.N_HeIII])
    pop = (1.0 - w) * pop_a + w * pop_b
    U = (1.0 - w) * a.U_resolved + w * b.U_resolved
    return _material_from_populations(pop, U)




def _solve_positive_implicit_thermal(
    *,
    populations: np.ndarray,
    parent_energy: np.ndarray,
    parent_temperature: np.ndarray,
    proper_volume_cm3: np.ndarray,
    photoheat_erg_s: np.ndarray,
    hubble_s_inv: float,
    dt_seconds: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Solve the scalar thermal backward-Euler equation in log(T).

    A sign-preserving bracket is constructed independently for every node and
    then bisected.  This is a root solve on the positive thermal cone, not a
    post-step projection.  The fixed material populations make the thermal
    equation one dimensional even though the outer chemistry/opacity problem
    remains nonlinear.
    """
    pop = np.asarray(populations, dtype=float)
    U0 = np.asarray(parent_energy, dtype=float)
    T0 = np.asarray(parent_temperature, dtype=float)
    volume = np.asarray(proper_volume_cm3, dtype=float)
    heat = np.asarray(photoheat_erg_s, dtype=float)
    size = len(pop)
    if pop.shape != (size, 5):
        raise ValueError("thermal populations must have shape (N,5)")
    if any(a.shape != (size,) for a in (U0, T0, volume, heat)):
        raise ValueError("thermal arrays have inconsistent shape")

    # At T->0, cooling and expansion vanish and F(T)<0 for positive U0 or heat.
    # At high T, U + dt(cooling+expansion) dominates.  The generous logarithmic
    # bracket is expanded only where needed; no physical state is modified.
    log_lo = np.log(np.maximum(T0 * 1.0e-12, 1.0e-8))
    log_hi = np.log(np.maximum(T0 * 10.0, 1.0e8))
    H = np.full(size, float(hubble_s_inv))
    dt = np.full(size, float(dt_seconds))

    def balance(log_t: np.ndarray) -> np.ndarray:
        return np.asarray(
            _batch_thermal_balance(
                jnp.asarray(log_t),
                jnp.asarray(pop),
                jnp.asarray(volume),
                jnp.asarray(heat),
                jnp.asarray(H),
                jnp.asarray(U0),
                jnp.asarray(dt),
            )
        )

    f_lo = balance(log_lo)
    f_hi = balance(log_hi)
    for _ in range(24):
        need = ~(np.isfinite(f_hi) & (f_hi >= 0.0))
        if not np.any(need):
            break
        log_hi = np.where(need, log_hi + math.log(10.0), log_hi)
        f_hi = balance(log_hi)
    bracketed = (
        np.isfinite(f_lo)
        & np.isfinite(f_hi)
        & (f_lo <= 0.0)
        & (f_hi >= 0.0)
    )

    # Unbracketed rows are left at the parent temperature for diagnostics and
    # are marked infeasible by the caller; they are never accepted or clipped.
    lo = log_lo.copy()
    hi = log_hi.copy()
    for _ in range(72):
        mid = 0.5 * (lo + hi)
        f_mid = balance(mid)
        move_lo = np.isfinite(f_mid) & (f_mid <= 0.0)
        lo = np.where(bracketed & move_lo, mid, lo)
        hi = np.where(bracketed & ~move_lo, mid, hi)
    log_root = 0.5 * (lo + hi)
    temperature = np.where(bracketed, np.exp(log_root), T0)
    particles = (
        pop[:, 0] + pop[:, 1]
        + pop[:, 2] + pop[:, 3] + pop[:, 4]
        + pop[:, 1] + pop[:, 3] + 2.0 * pop[:, 4]
    )
    energy = 1.5 * KB_ERG * particles * temperature
    balance_value = balance(np.log(temperature))
    scale = np.maximum.reduce(
        [np.abs(energy), np.abs(U0), np.abs(float(dt_seconds) * heat), np.full(size, 1.0e-300)]
    )
    relative = np.abs(balance_value) / scale
    rhs = (energy - U0) / max(float(dt_seconds), 1.0e-300)
    if float(dt_seconds) == 0.0:
        rhs = np.zeros(size)
        relative = np.zeros(size)
    return energy, temperature, rhs, relative, bracketed


def linearly_implicit_update(
    *,
    parent: MaterialBatch,
    coefficient_state: MaterialBatch,
    proper_volume_cm3: np.ndarray,
    photo: PhotoInputs,
    hubble_s_inv: float,
    dt_seconds: float,
) -> LinearizedUpdate:
    """One frozen-coefficient backward-Euler reaction/thermal Picard map.

    The five-species solve is implicit in all event extents at the current
    Picard coefficient state.  Positivity is a hard feasibility gate: no
    negative population or energy is projected back into the cone.
    """
    if parent.size != coefficient_state.size:
        raise ValueError("parent and coefficient state sizes differ")
    size = parent.size
    photo.validate(size)
    volume = np.asarray(proper_volume_cm3, dtype=float)
    if volume.shape != (size,) or np.any(~np.isfinite(volume)) or np.any(volume <= 0.0):
        raise ValueError("proper volume must be finite and positive")
    dt = float(dt_seconds)
    H = float(hubble_s_inv)
    if not math.isfinite(dt) or dt < 0.0 or not math.isfinite(H) or H < 0.0:
        raise ValueError("invalid timestep or Hubble rate")
    q = state_to_coordinates(coefficient_state)
    matrices = np.asarray(
        _batch_linear_matrix(
            jnp.asarray(q), jnp.asarray(parent.N_H), jnp.asarray(parent.N_He),
            jnp.asarray(volume), jnp.asarray(photo.HI), jnp.asarray(photo.HeI),
            jnp.asarray(photo.HeII),
        )
    )
    parent_pop = np.column_stack(
        [parent.N_HI, parent.N_HII, parent.N_HeI, parent.N_HeII, parent.N_HeIII]
    )
    lhs = np.eye(5)[None, :, :] - dt * matrices
    try:
        pop_new = np.linalg.solve(lhs, parent_pop[..., None])[..., 0]
    except np.linalg.LinAlgError:
        pop_new = np.stack(
            [np.linalg.lstsq(a, b, rcond=None)[0] for a, b in zip(lhs, parent_pop)]
        )
    min_species = np.min(pop_new, axis=1)
    h_res = (pop_new[:, 0] + pop_new[:, 1]) - parent.N_H
    he_res = (pop_new[:, 2] + pop_new[:, 3] + pop_new[:, 4]) - parent.N_He
    population_feasible = np.all(np.isfinite(pop_new), axis=1) & (min_species > 0.0)

    # Evaluate the positive thermal solve only on meaningful populations.  Bad
    # population rows use the parent values as a diagnostic placeholder and are
    # still marked infeasible; no projected row can enter an accepted state.
    parent_pop = np.column_stack(
        [parent.N_HI, parent.N_HII, parent.N_HeI, parent.N_HeII, parent.N_HeIII]
    )
    thermal_pop = np.where(population_feasible[:, None], pop_new, parent_pop)
    U_new, T_new, thermal, thermal_residual, bracketed = _solve_positive_implicit_thermal(
        populations=thermal_pop,
        parent_energy=np.asarray(parent.U_resolved),
        parent_temperature=np.asarray(parent.T_K),
        proper_volume_cm3=volume,
        photoheat_erg_s=np.asarray(photo.heating_erg_s),
        hubble_s_inv=H,
        dt_seconds=dt,
    )
    state = MaterialBatch(
        N_HI=pop_new[:, 0],
        N_HII=pop_new[:, 1],
        N_HeI=pop_new[:, 2],
        N_HeII=pop_new[:, 3],
        N_HeIII=pop_new[:, 4],
        U_resolved=U_new,
        T_K=T_new,
    )
    feasible = (
        population_feasible
        & bracketed
        & np.isfinite(U_new)
        & np.isfinite(T_new)
        & (U_new > 0.0)
        & (T_new > 0.0)
        & np.isfinite(thermal_residual)
        & (thermal_residual <= 1.0e-10)
    )
    return LinearizedUpdate(
        state=state,
        feasible=feasible,
        minimum_species=min_species,
        hydrogen_residual=h_res,
        helium_residual=he_res,
        thermal_rhs_erg_s=thermal,
        thermal_balance_relative_residual=thermal_residual,
        thermal_bracketed=bracketed,
    )
