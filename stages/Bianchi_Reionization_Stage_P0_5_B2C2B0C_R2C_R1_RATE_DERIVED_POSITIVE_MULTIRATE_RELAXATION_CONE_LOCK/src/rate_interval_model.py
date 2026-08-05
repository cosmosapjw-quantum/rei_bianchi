"""Rate-evidence primitives for the R2C-R1 preflight.

The functions in this module only derive rate evidence from inherited endpoint
states and explicit source terms.  They do not inspect cone-feasibility
results and they never fit one rate per node.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Mapping

import numpy as np

MPC_CM = 3.085677581491367e24
MYR_S = 1.0e6 * 365.25 * 86400.0
C_LIGHT_CM_S = 2.99792458e10
K_B_ERG_PER_K = 1.380649e-16
EV_ERG = 1.602176634e-12
H0_S_INV = 67.4 * 1.0e5 / MPC_CM
OMEGA_M = 0.315
OMEGA_L = 0.685
GROUP_EXCESS_EV = np.array([2.9240084038128336, 15.498762259794773])


@dataclass(frozen=True)
class RateInterval:
    family: str
    k_min_myr_inv: float
    k_max_myr_inv: float
    status: str
    identifiability: str
    endpoint_changed: bool
    usable: bool
    evidence_myr_inv: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def alpha_b_hii(temperature_k: float | np.ndarray) -> np.ndarray | float:
    """Canonical B2C0 case-B HII recombination coefficient [cm^3 s^-1]."""
    t = np.asarray(temperature_k, dtype=float)
    if np.any(~np.isfinite(t)) or np.any(t <= 0.0):
        raise ValueError("temperature must be finite and positive")
    lam = 315614.0 / t
    out = 2.753e-14 * lam**1.5 / (1.0 + (lam / 2.740) ** 0.407) ** 2.242
    return float(out) if out.ndim == 0 else out


def beta_hi(temperature_k: float | np.ndarray) -> np.ndarray | float:
    """Canonical collisional HI ionization coefficient [cm^3 s^-1]."""
    t = np.asarray(temperature_k, dtype=float)
    if np.any(~np.isfinite(t)) or np.any(t <= 0.0):
        raise ValueError("temperature must be finite and positive")
    out = 5.835e-11 * np.sqrt(t) * np.exp(-157804.0 / t)
    return float(out) if out.ndim == 0 else out


def hydrogen_cooling_coefficients(temperature_k: float | np.ndarray) -> dict[str, np.ndarray | float]:
    """Pure-H cooling coefficients [erg cm^3 s^-1], inherited verbatim."""
    t = np.asarray(temperature_k, dtype=float)
    if np.any(~np.isfinite(t)) or np.any(t <= 0.0):
        raise ValueError("temperature must be finite and positive")
    lam = 315614.0 / t
    rec = 3.435e-30 * t * lam**1.970 / (1.0 + (lam / 2.250) ** 0.376) ** 3.720
    excitation = 7.5e-19 * np.exp(-118348.0 / t) / (1.0 + np.sqrt(t / 1.0e5))
    coll_ion = np.asarray(beta_hi(t)) * 13.598 * EV_ERG
    free_free = 1.42e-27 * np.sqrt(t) * (
        1.1 + 0.34 * np.exp(-((5.5 - np.log10(t)) ** 2) / 3.0)
    )
    result = {
        "recombination": rec,
        "excitation": excitation,
        "collisional_ionization": coll_ion,
        "free_free": free_free,
    }
    if t.ndim == 0:
        return {key: float(value) for key, value in result.items()}
    return result


def hubble_s_inv(z: float) -> float:
    zf = float(z)
    if not math.isfinite(zf) or zf <= -1.0:
        raise ValueError("z must be finite and greater than -1")
    return H0_S_INV * math.sqrt(OMEGA_M * (1.0 + zf) ** 3 + OMEGA_L)


def _positive_finite_vector(value: Any, name: str, *, allow_zero: bool = True) -> np.ndarray:
    arr = np.asarray(value, dtype=float)
    if arr.ndim != 1 or np.any(~np.isfinite(arr)):
        raise ValueError(f"{name} must be a finite vector")
    if np.any(arr < 0.0) or (not allow_zero and np.any(arr <= 0.0)):
        raise ValueError(f"{name} has invalid sign")
    return arr


def secant_turnover_myr_inv(previous: float, target: float, dt_myr: float) -> float:
    """Symmetric extensive secant turnover [Myr^-1]."""
    y0 = float(previous)
    y1 = float(target)
    dt = float(dt_myr)
    if not all(math.isfinite(v) for v in (y0, y1, dt)) or dt <= 0.0:
        raise ValueError("finite endpoint values and positive dt are required")
    scale = 0.5 * (abs(y0) + abs(y1))
    if scale == 0.0:
        return 0.0
    return abs(y1 - y0) / (dt * scale)


def derive_positive_interval(
    *,
    family: str,
    estimates_myr_inv: Mapping[str, float],
    endpoint_changed: bool,
    dt_myr: float,
    identifiability: str,
) -> RateInterval:
    """Freeze the closed hull of positive evidence without expansion factors."""
    dt = float(dt_myr)
    if not math.isfinite(dt) or dt <= 0.0:
        raise ValueError("dt_myr must be finite and positive")
    evidence = {str(k): float(v) for k, v in estimates_myr_inv.items()}
    if any((not math.isfinite(v)) or v < 0.0 for v in evidence.values()):
        raise ValueError("rate evidence must be finite and nonnegative")
    positive = [v for v in evidence.values() if v > 0.0]
    if not positive:
        if endpoint_changed:
            return RateInterval(
                family=family,
                k_min_myr_inv=math.nan,
                k_max_myr_inv=math.nan,
                status="UNIDENTIFIABLE_REQUIRED_RATE",
                identifiability=identifiability,
                endpoint_changed=True,
                usable=False,
                evidence_myr_inv=evidence,
            )
        reference = 1.0 / dt
        return RateInterval(
            family=family,
            k_min_myr_inv=reference,
            k_max_myr_inv=reference,
            status="DYNAMICALLY_IRRELEVANT",
            identifiability=identifiability,
            endpoint_changed=False,
            usable=True,
            evidence_myr_inv=evidence,
        )
    lo = min(positive)
    hi = max(positive)
    status = "SINGLE_SCALE_IDENTIFIED" if lo == hi else "IDENTIFIED_INTERVAL"
    return RateInterval(
        family=family,
        k_min_myr_inv=lo,
        k_max_myr_inv=hi,
        status=status,
        identifiability=identifiability,
        endpoint_changed=bool(endpoint_changed),
        usable=True,
        evidence_myr_inv=evidence,
    )


def family_attenuation_inverse(k_myr_inv: float, dt_myr: float) -> float:
    """Return a=[1-exp(-k dt)]^-1, with stable small-argument behavior."""
    k = float(k_myr_inv)
    dt = float(dt_myr)
    if not math.isfinite(k) or not math.isfinite(dt) or k <= 0.0 or dt <= 0.0:
        raise ValueError("positive finite k and dt are required")
    lam = -math.expm1(-k * dt)
    return 1.0 / lam


def macro_process_evidence(
    *,
    mass: Any,
    x_hii: Any,
    temperature_k: Any,
    n_h_cm3: Any,
    capacity: Any,
    current: Any,
    phi: Any,
    transfer_positive: Any,
    transfer_negative: Any,
    z: float,
    transfer_x_hii: float,
    transfer_temperature_k: float,
) -> dict[str, float]:
    """Derive macro-shared physical turnover evidence [Myr^-1].

    Source terms retain their inherited cgs/comoving dimensions until divided
    by the corresponding extensive store.  The result is a rate, converted to
    Myr^-1 only at the final step.
    """
    m = _positive_finite_vector(mass, "mass")
    x = _positive_finite_vector(x_hii, "x_hii")
    t = _positive_finite_vector(temperature_k, "temperature_k", allow_zero=False)
    nh = _positive_finite_vector(n_h_cm3, "n_h_cm3")
    cap = _positive_finite_vector(capacity, "capacity")
    tp = _positive_finite_vector(transfer_positive, "transfer_positive")
    tn = _positive_finite_vector(transfer_negative, "transfer_negative")
    j = np.asarray(current, dtype=float)
    ph = _positive_finite_vector(phi, "phi", allow_zero=False)
    if any(v.shape != m.shape for v in (x, t, nh, cap, tp, tn)):
        raise ValueError("node vectors must have identical shape")
    if np.any(x > 1.0) or j.shape != (m.size, ph.size) or np.any(~np.isfinite(j)) or np.any(j < 0.0):
        raise ValueError("invalid ionization or current shape/sign")

    total_m = float(np.sum(m))
    if total_m <= 0.0:
        raise ValueError("macro mass must be positive")
    ionized = m * x
    thermal = 1.5 * K_B_ERG_PER_K * m * t
    total_i = float(np.sum(ionized))
    total_u = float(np.sum(thermal))
    total_c = float(np.sum(cap))
    group_j = np.sum(j, axis=0)
    total_j = float(np.sum(group_j))
    gross_transfer = float(np.sum(tp + tn))

    recombination_node = np.asarray(alpha_b_hii(t)) * nh * x**2 * m
    collisional_node = np.asarray(beta_hi(t)) * nh * x * (1.0 - x) * m
    recombination = float(np.sum(recombination_node))
    collisional = float(np.sum(collisional_node))

    heating = EV_ERG * float(np.sum(j * GROUP_EXCESS_EV[None, :]))
    coeff = hydrogen_cooling_coefficients(t)
    cooling_node = (
        np.asarray(coeff["recombination"]) * nh * x**2 * m
        + np.asarray(coeff["excitation"]) * nh * x * (1.0 - x) * m
        + np.asarray(coeff["collisional_ionization"]) * nh * x * (1.0 - x) * m
        + np.asarray(coeff["free_free"]) * nh * x**2 * m
    )
    cooling = float(np.sum(cooling_node))
    expansion = float(np.sum(3.0 * hubble_s_inv(z) * K_B_ERG_PER_K * t * (1.0 + x) * m))
    transfer_thermal = 1.5 * K_B_ERG_PER_K * gross_transfer * float(transfer_temperature_k)

    neutral = max(float(np.sum(m - ionized)), np.finfo(float).tiny * total_m)
    mass_rate = gross_transfer / total_m
    ion_activity = total_j + recombination + collisional + gross_transfer * float(transfer_x_hii)
    ion_rate = ion_activity / total_m
    thermal_activity = heating + cooling + expansion + transfer_thermal
    thermal_rate = thermal_activity / max(total_u, np.finfo(float).tiny)
    neutral_driver = (total_j + recombination + collisional + gross_transfer) / neutral

    group_abs_rates = []
    for group_total, group_phi in zip(group_j, ph, strict=True):
        kappa_cMpc_inv = float(group_total / group_phi)
        group_abs_rates.append(C_LIGHT_CM_S * (1.0 + float(z)) * kappa_cMpc_inv / MPC_CM)

    result_s_inv = {
        "M": mass_rate,
        "I": ion_rate,
        "U": thermal_rate,
        "C": max(mass_rate, ion_rate, thermal_rate, neutral_driver),
        "J_G1": group_abs_rates[0],
        "J_G2a": group_abs_rates[1],
    }
    return {key: max(0.0, float(value) * MYR_S) for key, value in result_s_inv.items()}
