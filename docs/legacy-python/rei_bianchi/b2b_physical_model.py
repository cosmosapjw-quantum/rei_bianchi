"""P0.5-B2B physical-history extension of the durable B2A core.

The B2A monolithic residual is preserved verbatim in
``monolithic_model_b2a.py``.  This module adds only:

* source-spectrum lanes;
* a species-resolved neutral-front sink in the photon equations;
* an 8-dimensional transformed ODE for causal forward history generation;
* a 9-dimensional backward-Euler residual for timestep/branch audits.

No maintenance fitting, source-population calibration, or Bianchi geometry is
implemented in this stage.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping
import math

import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.interpolate import PchipInterpolator

from monolithic_model_b2a import (
    C_LIGHT,
    KB_ERG,
    MPC_CM,
    chemistry_rates,
    gamma_species,
    opacity_cMpc_inv,
    physical_vector,
    temperature,
    thermal_rate,
    transform_y_to_z,
    transform_z_to_y,
)

Array = jax.Array

H0 = 67.4 * 1.0e5 / MPC_CM
OMEGA_M = 0.315
OMEGA_L = 0.685
NH0 = 1.88e-7
YHE = 0.079

GROUPS = np.array(
    [
        [13.60, 24.59],
        [24.59, 39.50],
        [39.50, 54.42],
        [54.42, 100.0],
    ],
    dtype=float,
)
ENERGY_NODES = np.array([13.6, 14.48, 16.7, 20.05, 25.5, 39.5])
RAW_DENSITIES = np.array([-1.73, 0.0, 1.73])

VERNER = {
    "HI": (13.60, 0.4298, 5.475e4, 32.88, 2.963, 0.0, 0.0, 0.0),
    "HeI": (24.59, 13.61, 949.2, 1.469, 3.188, 2.039, 0.4434, 2.136),
    "HeII": (54.42, 1.720, 1.369e4, 32.88, 2.963, 0.0, 0.0, 0.0),
}


def hubble(z: float) -> float:
    return H0 * math.sqrt(OMEGA_M * (1.0 + z) ** 3 + OMEGA_L)


def verner_sigma(species: str, energy: float) -> float:
    eth, e0, sigma0, ya, pp, yw, y0, y1 = VERNER[species]
    if energy < eth:
        return 0.0
    x = energy / e0 - y0
    y = math.sqrt(x * x + y1 * y1)
    return (
        1.0e-18
        * sigma0
        * ((x - 1.0) ** 2 + yw * yw)
        * y ** (0.5 * pp - 5.5)
        / (1.0 + math.sqrt(y / ya)) ** pp
    )


@dataclass(frozen=True)
class SpectrumLane:
    name: str
    role: str
    shape: Callable[[float], float]
    source_max_eV: float
    within_group_shape: Callable[[float], float]
    source_fraction: np.ndarray
    sigma_HI: np.ndarray
    sigma_HeI: np.ndarray
    sigma_HeII: np.ndarray
    excess_HI: np.ndarray
    excess_HeI: np.ndarray
    excess_HeII: np.ndarray
    redshift_coeff: np.ndarray
    positivity_floor_fraction: float


def _power_shape(alpha: float) -> Callable[[float], float]:
    return lambda e: e**alpha


def _blackbody_number_shape(temperature_K: float) -> Callable[[float], float]:
    kT = 8.617333262e-5 * temperature_K

    def shape(e: float) -> float:
        x = e / kT
        if x > 700.0:
            return 0.0
        return e * e / math.expm1(x)

    return shape


def _integrate_shape(shape: Callable[[float], float], lo: float, hi: float) -> float:
    return quad(shape, lo, hi, epsabs=0.0, epsrel=2.0e-10, limit=400)[0]


def _group_sigma_excess(
    shape: Callable[[float], float], species: str, threshold: float
) -> tuple[np.ndarray, np.ndarray]:
    sigmas: list[float] = []
    excess: list[float] = []
    for lo, hi in GROUPS:
        norm = _integrate_shape(shape, float(lo), float(hi))
        if norm <= 0.0:
            # The source may be truncated, but an infinitesimal reservoir still
            # needs a within-group closure.  Use the declared within-group shape.
            sigmas.append(0.0)
            excess.append(0.0)
            continue
        sig = quad(
            lambda e: shape(e) * verner_sigma(species, e),
            float(lo),
            float(hi),
            epsabs=0.0,
            epsrel=2.0e-8,
            limit=400,
        )[0] / norm
        if sig > 0.0:
            heat = quad(
                lambda e: shape(e)
                * verner_sigma(species, e)
                * max(e - threshold, 0.0),
                float(lo),
                float(hi),
                epsabs=0.0,
                epsrel=2.0e-8,
                limit=400,
            )[0] / (norm * sig)
        else:
            heat = 0.0
        sigmas.append(sig)
        excess.append(heat)
    return np.asarray(sigmas), np.asarray(excess)


def _redshift_coeff(shape: Callable[[float], float]) -> np.ndarray:
    values = []
    for lo, hi in GROUPS:
        norm = _integrate_shape(shape, float(lo), float(hi))
        values.append(0.0 if norm <= 0.0 else lo * shape(float(lo)) / norm)
    return np.asarray(values)


def make_spectrum_lanes() -> dict[str, SpectrumLane]:
    specifications = {
        "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD": {
            "role": "PRIMARY_PHYSICAL_MFP_CONSISTENT",
            "shape": _power_shape(-2.5),
            "source_max": 54.42,
            "within": _power_shape(-2.5),
        },
        "CLOUDY_BLACKBODY_80000K": {
            "role": "STELLAR_HARD_AUDITOR",
            "shape": _blackbody_number_shape(8.0e4),
            "source_max": 100.0,
            "within": _blackbody_number_shape(8.0e4),
        },
        "CLOUDY_HARD_POWERLAW_FNU_MINUS_1P5": {
            "role": "HARD_POWERLAW_STRESS_AUDITOR",
            "shape": _power_shape(-2.5),
            "source_max": 100.0,
            "within": _power_shape(-2.5),
        },
        "B2A_E_MINUS_4_NUMERICAL": {
            "role": "NUMERICAL_AUDITOR_NOT_PHYSICAL_PRIOR",
            "shape": _power_shape(-4.0),
            "source_max": 100.0,
            "within": _power_shape(-4.0),
        },
    }

    lanes: dict[str, SpectrumLane] = {}
    floor = 1.0e-14
    for name, spec in specifications.items():
        source_weights = []
        for lo, hi in GROUPS:
            source_hi = min(float(hi), float(spec["source_max"]))
            if source_hi <= lo:
                source_weights.append(0.0)
            else:
                source_weights.append(_integrate_shape(spec["shape"], float(lo), source_hi))
        source_weights = np.asarray(source_weights, dtype=float)
        if source_weights.sum() <= 0.0:
            raise RuntimeError(f"No source photons for lane {name}")
        source_fraction = source_weights / source_weights.sum()

        s_hi, e_hi = _group_sigma_excess(spec["within"], "HI", 13.60)
        s_hei, e_hei = _group_sigma_excess(spec["within"], "HeI", 24.59)
        s_heii, e_heii = _group_sigma_excess(spec["within"], "HeII", 54.42)

        lanes[name] = SpectrumLane(
            name=name,
            role=str(spec["role"]),
            shape=spec["shape"],
            source_max_eV=float(spec["source_max"]),
            within_group_shape=spec["within"],
            source_fraction=source_fraction,
            sigma_HI=s_hi,
            sigma_HeI=s_hei,
            sigma_HeII=s_heii,
            excess_HI=e_hi,
            excess_HeI=e_hei,
            excess_HeII=e_heii,
            redshift_coeff=_redshift_coeff(spec["within"]),
            positivity_floor_fraction=floor,
        )
    return lanes


def project_reservoir(total_number: float, lane: SpectrumLane) -> np.ndarray:
    fraction = np.asarray(lane.source_fraction, dtype=float).copy()
    missing = fraction <= 0.0
    if np.any(missing):
        fraction[missing] = lane.positivity_floor_fraction
        fraction[~missing] *= (1.0 - fraction[missing].sum()) / fraction[~missing].sum()
    fraction /= fraction.sum()
    return total_number * fraction


def allocate_front_sink(
    h_rate: float,
    hei_rate: float,
    heii_rate: float,
    lane: SpectrumLane,
) -> tuple[np.ndarray, dict[str, float]]:
    """Allocate positive front costs to photon groups by source*cross-section.

    Negative species derivatives are retained in the diagnostic return but do
    not become negative photon sinks; recombination is handled by chemistry.
    """
    positive = np.array([max(h_rate, 0.0), max(hei_rate, 0.0), max(heii_rate, 0.0)])
    sigmas = [lane.sigma_HI, lane.sigma_HeI, lane.sigma_HeII]
    out = np.zeros(4)
    for rate, sigma in zip(positive, sigmas):
        weight = lane.source_fraction * sigma
        if weight.sum() <= 0.0:
            if rate > 0.0:
                # Fail closed for a species cost outside the source domain.
                raise RuntimeError(
                    f"Front cost {rate} cannot be allocated in lane {lane.name}"
                )
            continue
        out += rate * weight / weight.sum()
    return out, {
        "negative_HII_derivative": min(h_rate, 0.0),
        "negative_HeII_derivative": min(hei_rate, 0.0),
        "negative_HeIII_derivative": min(heii_rate, 0.0),
        "allocated_positive_total": float(out.sum()),
    }


def _q_history(z: float, midpoint: float = 6.58, width: float = 1.63) -> float:
    return 0.5 * (1.0 - math.tanh((z - midpoint) / width))


def _interpolate_density_weights(density_map: pd.DataFrame, z: float) -> np.ndarray:
    out = []
    for dens in sorted(density_map["density_sigma"].unique()):
        sub = density_map[np.isclose(density_map["density_sigma"], dens)].sort_values("z")
        out.append(np.interp(z, sub["z"], sub["effective_GH_weight"]))
    return np.asarray(out)


def build_opacity_fit(
    raw_table_path: Path,
    density_map_path: Path,
    z: float,
    lane: SpectrumLane,
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """Build log-Gamma12 -> log-kappa PCHIP coefficients at one redshift."""
    raw = np.loadtxt(raw_table_path)
    columns = ["z", "zre", "gamma", "density"] + [f"mfp_{e:g}" for e in ENERGY_NODES]
    frame = pd.DataFrame(raw, columns=columns)
    frame = frame[np.isclose(frame["z"], z)].copy()
    if frame.empty:
        raise RuntimeError(f"No raw opacity data at z={z}")

    density_map = pd.read_csv(density_map_path)
    dweights = _interpolate_density_weights(density_map, z)

    def zre_weights(nodes: np.ndarray) -> dict[float, float]:
        nodes = np.array(sorted(nodes), dtype=float)
        mids = 0.5 * (nodes[:-1] + nodes[1:])
        lo = np.r_[z, mids]
        hi = np.r_[mids, np.inf]
        mass = np.array([
            _q_history(a) - (0.0 if np.isinf(b) else _q_history(b))
            for a, b in zip(lo, hi)
        ])
        mass = np.maximum(mass, 0.0)
        mass /= mass.sum()
        return dict(zip(nodes, mass))

    rows = []
    for gamma in sorted(frame["gamma"].unique()):
        gframe = frame[np.isclose(frame["gamma"], gamma)]
        kappa_by_zre: dict[float, np.ndarray] = {}
        complete = []
        for zre in sorted(gframe["zre"].unique()):
            if zre < z:
                continue
            sub = gframe[np.isclose(gframe["zre"], zre)]
            vectors = []
            valid = True
            for dens in RAW_DENSITIES:
                row = sub[np.isclose(sub["density"], dens)]
                if len(row) != 1:
                    valid = False
                    break
                vectors.append(row.iloc[0, 4:].to_numpy(float))
            if valid:
                vec = np.asarray(vectors)
                kappa_by_zre[float(zre)] = np.sum(dweights[:, None] / vec, axis=0)
                complete.append(float(zre))
        if not complete:
            continue
        zw = zre_weights(np.asarray(complete))
        kappa = sum(zw[zr] * kappa_by_zre[zr] for zr in complete)
        rows.append([gamma, *kappa])

    op = np.asarray(rows)
    if len(op) < 5:
        raise RuntimeError(f"Insufficient opacity nodes at z={z}: {len(op)}")

    def discrete_weights(nodes: np.ndarray) -> np.ndarray:
        values = np.array([lane.within_group_shape(float(e)) for e in nodes])
        return values / values.sum()

    w1 = discrete_weights(ENERGY_NODES[:4])
    w2 = discrete_weights(ENERGY_NODES[4:])
    k1 = op[:, 1:5] @ w1
    k2 = op[:, 5:7] @ w2
    logg = np.log(op[:, 0])
    p1 = PchipInterpolator(logg, np.log(k1), extrapolate=True)
    p2 = PchipInterpolator(logg, np.log(k2), extrapolate=True)
    coeff = np.stack([p1.c, p2.c])
    table = pd.DataFrame(
        {
            "z": z,
            "Gamma12": op[:, 0],
            "kappa_G1_cMpc_inv": k1,
            "kappa_G2a_cMpc_inv": k2,
            "fit_G1_cMpc_inv": np.exp(p1(logg)),
            "fit_G2a_cMpc_inv": np.exp(p2(logg)),
        }
    )
    return logg, coeff, table


def make_params(
    *,
    z_cos: float,
    dt_seconds: float,
    lane: SpectrumLane,
    log_kappa_knots: np.ndarray,
    log_kappa_coeffs: np.ndarray,
    n_prev: np.ndarray,
    x_prev: np.ndarray,
    u_prev: float,
    front_sink_group: np.ndarray,
    scale_n: np.ndarray | None = None,
    scale_x: np.ndarray | None = None,
    scale_u: float | None = None,
    scale_gamma: float = 1.0e-13,
) -> dict[str, Array]:
    n_h = NH0 * (1.0 + z_cos) ** 3
    n_he = YHE * n_h
    cMpc_per_cm = MPC_CM / (1.0 + z_cos)

    return {
        "z_cos": jnp.array(z_cos),
        "dt": jnp.array(dt_seconds),
        "Hubble": jnp.array(hubble(z_cos)),
        "nH_phys": jnp.array(n_h),
        "nHe_phys": jnp.array(n_he),
        "source_fraction": jnp.asarray(lane.source_fraction),
        "redshift_coeff": jnp.asarray(lane.redshift_coeff),
        "sigma_HI": jnp.asarray(lane.sigma_HI),
        "sigma_HeI": jnp.asarray(lane.sigma_HeI),
        "sigma_HeII": jnp.asarray(lane.sigma_HeII),
        "log_kappa_knots": jnp.asarray(log_kappa_knots),
        "log_kappa_pchip_coeffs": jnp.asarray(log_kappa_coeffs),
        "sigma_ots_H24": jnp.array(verner_sigma("HI", 24.59)),
        "sigma_ots_HeI24": jnp.array(verner_sigma("HeI", 24.59)),
        "sigma_ots_H41": jnp.array(verner_sigma("HI", 40.8)),
        "sigma_ots_HeI41": jnp.array(verner_sigma("HeI", 40.8)),
        "sigma_ots_H54": jnp.array(verner_sigma("HI", 54.42)),
        "sigma_ots_HeI54": jnp.array(verner_sigma("HeI", 54.42)),
        "sigma_ots_HeII54": jnp.array(verner_sigma("HeII", 54.42)),
        "excess_HI_eV": jnp.asarray(lane.excess_HI),
        "excess_HeI_eV": jnp.asarray(lane.excess_HeI),
        "excess_HeII_eV": jnp.asarray(lane.excess_HeII),
        "front_sink_group": jnp.asarray(front_sink_group),
        "N_prev": jnp.asarray(n_prev),
        "x_prev": jnp.asarray(x_prev),
        "u_prev": jnp.array(u_prev),
        # If an explicit scale is supplied, preserve physically small/dormant
        # group scales.  Replacing them by 1 cMpc^-3 makes the log-N Jacobian
        # spuriously singular when a source lane is exactly truncated.
        "scale_N": jnp.asarray(
            np.maximum(n_prev, 1.0)
            if scale_n is None
            else np.maximum(np.asarray(scale_n, dtype=float), 1.0e-300)
        ),
        "scale_x": jnp.asarray(np.ones(3) if scale_x is None else scale_x),
        "scale_u": jnp.array(max(u_prev if scale_u is None else scale_u, 1.0e-300)),
        "scale_gamma": jnp.array(scale_gamma),
        "cMpc_per_cm": jnp.array(cMpc_per_cm),
    }


def photon_rates_history(
    state: Mapping[str, Array], emissivity: Array, p: Mapping[str, Array]
) -> Array:
    n = state["N"]
    kappa = opacity_cMpc_inv(state, p)
    absorption = C_LIGHT * (1.0 + p["z_cos"]) / MPC_CM * kappa
    red_out = p["Hubble"] * p["redshift_coeff"]
    rhs = (
        emissivity * p["source_fraction"]
        - p["front_sink_group"]
        - (absorption + red_out) * n
    )
    rhs = rhs.at[:3].add(red_out[1:] * n[1:])
    return rhs


def physical_rhs_history(
    state: Mapping[str, Array], emissivity: Array, p: Mapping[str, Array]
) -> Mapping[str, Array]:
    return {
        "N": photon_rates_history(state, emissivity, p),
        "x": chemistry_rates(state, p),
        "u": thermal_rate(state, p),
    }


def residual_history(z: Array, log_emissivity: Array, p: Mapping[str, Array]) -> Array:
    state = transform_z_to_y(z)
    emissivity = jnp.exp(log_emissivity)
    rhs = physical_rhs_history(state, emissivity, p)
    gamma_calc = gamma_species(state, p)[0]
    fN = (state["N"] - p["N_prev"] - p["dt"] * rhs["N"]) / p["scale_N"]
    fx = (
        jnp.array([state["xHII"], state["xHeII"], state["xHeIII"]])
        - p["x_prev"]
        - p["dt"] * rhs["x"]
    ) / p["scale_x"]
    fu = (state["u"] - p["u_prev"] - p["dt"] * rhs["u"]) / p["scale_u"]
    fg = (state["GammaHI"] - gamma_calc) / p["scale_gamma"]
    return jnp.concatenate([fN, fx, jnp.array([fu, fg])])


def transform_z8_to_state(z8: Array, p: Mapping[str, Array]) -> Mapping[str, Array]:
    n = jnp.exp(z8[:4])
    xh = jax.nn.sigmoid(z8[4])
    he = jax.nn.softmax(jnp.array([0.0, z8[5], z8[6]], dtype=z8.dtype))
    u = jnp.exp(z8[7])
    prefactor = C_LIGHT * (1.0 + p["z_cos"]) ** 3 / MPC_CM**3
    gamma = prefactor * jnp.sum(p["sigma_HI"] * n)
    return {
        "N": n,
        "xHII": xh,
        "xHeI": he[0],
        "xHeII": he[1],
        "xHeIII": he[2],
        "u": u,
        "GammaHI": gamma,
    }


def transform_state_to_z8(
    n: np.ndarray, x_hii: float, x_heii: float, x_heiii: float, u: float
) -> np.ndarray:
    x_hei = 1.0 - x_heii - x_heiii
    if np.any(np.asarray(n) <= 0.0) or min(x_hii, 1.0 - x_hii, x_hei, x_heii, x_heiii, u) <= 0.0:
        raise ValueError("Nonphysical state passed to transform_state_to_z8")
    return np.r_[
        np.log(n),
        math.log(x_hii / (1.0 - x_hii)),
        math.log(x_heii / x_hei),
        math.log(x_heiii / x_hei),
        math.log(u),
    ]


def z8_rhs(z8: Array, emissivity: Array, p: Mapping[str, Array]) -> Array:
    state = transform_z8_to_state(z8, p)
    rhs = physical_rhs_history(state, emissivity, p)
    n = state["N"]
    xh = state["xHII"]
    x1, x2, x3 = state["xHeI"], state["xHeII"], state["xHeIII"]
    dxh, dx2, dx3 = rhs["x"]
    dx1 = -dx2 - dx3
    return jnp.concatenate(
        [
            rhs["N"] / n,
            jnp.array([dxh / (xh * (1.0 - xh))]),
            jnp.array([dx2 / x2 - dx1 / x1, dx3 / x3 - dx1 / x1]),
            jnp.array([rhs["u"] / state["u"]]),
        ]
    )


def physical_state_from_z8(z8: np.ndarray, p: Mapping[str, Array]) -> dict[str, np.ndarray | float]:
    state = transform_z8_to_state(jnp.asarray(z8), p)
    return {
        "N": np.asarray(state["N"], dtype=float),
        "xHII": float(state["xHII"]),
        "xHeI": float(state["xHeI"]),
        "xHeII": float(state["xHeII"]),
        "xHeIII": float(state["xHeIII"]),
        "u": float(state["u"]),
        "GammaHI": float(state["GammaHI"]),
        "T": float(temperature(state, p)),
    }


def z9_from_state(state: Mapping[str, np.ndarray | float]) -> np.ndarray:
    return np.asarray(
        transform_y_to_z(
            jnp.asarray(state["N"]),
            jnp.array(state["xHII"]),
            jnp.array(state["xHeII"]),
            jnp.array(state["xHeIII"]),
            jnp.array(state["u"]),
            jnp.array(state["GammaHI"]),
        ),
        dtype=float,
    )
