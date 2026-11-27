"""Explicit-parameter Bell cross-section Maxwellian prototype; no network admission.

Bell et al. (1983), JPCRD 12, 891, DOI 10.1063/1.555700, Eqs. (1), (5), (8).
Parameters are dimensional coefficients in eV**2 cm**2, not Table 5 mantissas.
No species coefficients, isotope mapping, physical temperature-validity claim,
or chemical-potential / cooling adapter is supplied by this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
import sys
from typing import Literal

import numpy as np
from scipy.special import exp1, roots_laguerre

# Explicit SI constants. eV and k_B are exact; m_e is CODATA 2022.
EV_J = 1.602176634e-19
KB_J_K = 1.380649e-23
ELECTRON_MASS_KG = 9.1093837139e-31
KB_EV_K = KB_J_K / EV_J
VELOCITY_FACTOR = 100.0 * math.sqrt(8.0 * EV_J / (math.pi * ELECTRON_MASS_KG))
PHYSICAL_ADMISSION = "NOT_ISSUED"


class CrossSectionPositivityError(ValueError):
    """The explicit cross-section model is negative at an evaluated point."""


def _finite_real(value: object, name: str) -> float:
    if isinstance(value, (bool, np.bool_)):
        raise TypeError(f"{name} must be a real number, not bool")
    if not isinstance(value, (int, float, np.integer, np.floating)):
        raise TypeError(f"{name} must be a real scalar")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class BellParameters:
    threshold_eV: float
    A_eV2_cm2: float
    B_eV2_cm2: tuple[float, ...]
    source_label: str

    def __post_init__(self) -> None:
        threshold = _finite_real(self.threshold_eV, "threshold_eV")
        a = _finite_real(self.A_eV2_cm2, "A_eV2_cm2")
        if threshold <= 0.0 or a <= 0.0:
            raise ValueError("threshold_eV and A_eV2_cm2 must be positive")
        if not isinstance(self.B_eV2_cm2, tuple):
            raise TypeError("B_eV2_cm2 must be an explicit immutable tuple")
        if len(self.B_eV2_cm2) > 5:
            raise ValueError("Bell Eq. (1) prototype supports at most five B terms")
        b = tuple(_finite_real(x, f"B[{i + 1}]") for i, x in enumerate(self.B_eV2_cm2))
        if not isinstance(self.source_label, str) or not self.source_label.strip():
            raise ValueError("source_label must explicitly identify the supplied model")
        object.__setattr__(self, "threshold_eV", threshold)
        object.__setattr__(self, "A_eV2_cm2", a)
        object.__setattr__(self, "B_eV2_cm2", b)

    @property
    def coefficient_scale(self) -> float:
        return max((self.A_eV2_cm2, *(abs(x) for x in self.B_eV2_cm2)))


@dataclass(frozen=True)
class RateEstimate:
    order: int
    temperature_K: float
    threshold_over_kT: float
    log_rate_cm3_s: float
    rate_cm3_s: float
    rate_underflow: bool
    rate_subnormal: bool
    mean_incident_energy_eV: float
    mean_excess_energy_eV: float
    log_incident_energy_moment_eV_cm3_s: float
    incident_energy_moment_eV_cm3_s: float
    energy_moment_underflow: bool
    minimum_scaled_numerator_at_nodes: float
    positive_node_count: int


@dataclass(frozen=True)
class QuadratureAssessment:
    order32: RateEstimate
    order64: RateEstimate
    relative_rate_difference_32_to_64: float
    relative_mean_excess_difference_32_to_64: float
    physical_admission: str = PHYSICAL_ADMISSION


@dataclass(frozen=True)
class PureAOracle:
    log_rate_cm3_s: float
    mean_incident_energy_eV: float
    mean_excess_energy_eV: float
    method: str
    scaled_E1_relative_remainder_bound: float | None


def _thermal_variables(parameters: BellParameters, temperature_K: float) -> tuple[float, float, float]:
    if not isinstance(parameters, BellParameters):
        raise TypeError("parameters must be BellParameters")
    temperature = _finite_real(temperature_K, "temperature_K")
    if temperature <= 0.0:
        raise ValueError("temperature_K must be positive")
    theta = KB_EV_K * temperature
    if theta == 0.0 or not math.isfinite(theta):
        raise ValueError("k_B T is outside finite float representation")
    u = parameters.threshold_eV / theta
    if u <= 0.0 or not math.isfinite(u):
        raise ValueError("I/(k_B T) is outside finite float representation")
    return temperature, theta, u


def _scaled_numerator(parameters: BellParameters, log_ratio: float, y: float) -> float:
    scale = parameters.coefficient_scale
    terms = [parameters.A_eV2_cm2 / scale * log_ratio]
    terms.extend((coefficient / scale) * y ** i
                 for i, coefficient in enumerate(parameters.B_eV2_cm2, start=1))
    value = math.fsum(terms)
    if not math.isfinite(value):
        raise ValueError("non-finite cross-section numerator")
    if value < 0.0:
        raise CrossSectionPositivityError("supplied cross section is negative; no clipping is applied")
    return value


def cross_section_cm2(parameters: BellParameters, incident_energy_eV: float) -> float:
    """Evaluate the supplied Bell model; zero below its specified threshold."""
    if not isinstance(parameters, BellParameters):
        raise TypeError("parameters must be BellParameters")
    energy = _finite_real(incident_energy_eV, "incident_energy_eV")
    if energy < 0.0:
        raise ValueError("incident_energy_eV must be nonnegative")
    if energy <= parameters.threshold_eV:
        return 0.0
    delta = energy - parameters.threshold_eV
    ratio_minus_one = delta / parameters.threshold_eV
    log_ratio = (math.log1p(ratio_minus_one) if math.isfinite(ratio_minus_one)
                 else math.log(energy) - math.log(parameters.threshold_eV))
    y = delta / energy
    f = _scaled_numerator(parameters, log_ratio, y)
    if f == 0.0:
        return 0.0
    log_sigma = (math.log(parameters.coefficient_scale) + math.log(f)
                 - math.log(parameters.threshold_eV) - math.log(energy))
    return _represent_positive_log(log_sigma)[0]


@lru_cache(maxsize=2)
def _nodes_and_weights(order: int) -> tuple[tuple[float, ...], tuple[float, ...]]:
    nodes, weights = roots_laguerre(order)
    # Cache immutable values; no callers can mutate shared quadrature nodes.
    return tuple(float(x) for x in nodes), tuple(float(w) for w in weights)


def _represent_positive_log(log_value: float) -> tuple[float, bool, bool]:
    if not math.isfinite(log_value):
        raise ValueError("logarithmic result must remain finite")
    if log_value > math.log(sys.float_info.max):
        raise OverflowError("positive result exceeds float range; retain the logarithmic calculation")
    value = math.exp(log_value)
    return value, value == 0.0, 0.0 < value < sys.float_info.min


def maxwellian_at_order(parameters: BellParameters, temperature_K: float,
                       order: Literal[32, 64]) -> RateEstimate:
    """Two positive-weight scalar quadratures: rate and incoming-energy moment.

    Positivity at the nodes is checked. This finite check is not a proof of
    nonnegativity between nodes, a quadrature error bound, or source validation.
    """
    if isinstance(order, bool) or not isinstance(order, (int, np.integer)) or order not in (32, 64):
        raise ValueError("order must be 32 or 64")
    temperature, theta, u = _thermal_variables(parameters, temperature_K)
    nodes, weights = _nodes_and_weights(order)
    f = tuple(_scaled_numerator(parameters, math.log1p(x / u), x / (u + x))
              for x in nodes)
    j0 = math.fsum(w * value for w, value in zip(weights, f))
    j1 = math.fsum(w * x * value for w, x, value in zip(weights, nodes, f))
    if j0 <= 0.0 or j1 <= 0.0 or not math.isfinite(j0 + j1):
        raise ValueError("quadrature must yield finite positive scaled rate and moment")
    log_rate = (math.log(VELOCITY_FACTOR) + math.log(parameters.coefficient_scale)
                - math.log(parameters.threshold_eV) - 0.5 * math.log(theta)
                - u + math.log(j0))
    rate, underflow, subnormal = _represent_positive_log(log_rate)
    mean_excess = theta * j1 / j0
    mean_incident = parameters.threshold_eV + mean_excess
    if not math.isfinite(mean_incident):
        raise OverflowError("incoming-energy mean exceeds float range")
    log_energy_moment = log_rate + math.log(mean_incident)
    energy_moment, energy_underflow, _ = _represent_positive_log(log_energy_moment)
    return RateEstimate(
        order, temperature, u, log_rate, rate, underflow, subnormal,
        mean_incident, mean_excess, log_energy_moment, energy_moment,
        energy_underflow, min(f), sum(value > 0.0 for value in f),
    )


def evaluate_maxwellian(parameters: BellParameters, temperature_K: float) -> QuadratureAssessment:
    """Return 32/64-order model calculations without physical admission."""
    low = maxwellian_at_order(parameters, temperature_K, 32)
    high = maxwellian_at_order(parameters, temperature_K, 64)
    relative_rate = abs(math.expm1(low.log_rate_cm3_s - high.log_rate_cm3_s))
    relative_excess = abs(low.mean_excess_energy_eV / high.mean_excess_energy_eV - 1.0)
    return QuadratureAssessment(low, high, relative_rate, relative_excess)


def pure_a_oracle(parameters: BellParameters, temperature_K: float) -> PureAOracle:
    """Independent E1 identity for B_i=0; large-U alternating expansion is bounded.

    K = C A / (I sqrt(theta)) E1(U). The large-U expansion is used only
    for U>600, with a first-omitted-term bound for scaled E1.
    """
    _, theta, u = _thermal_variables(parameters, temperature_K)
    if any(b != 0.0 for b in parameters.B_eV2_cm2):
        raise ValueError("pure-A oracle requires every B coefficient to be zero")
    if u <= 600.0:
        e1 = float(exp1(u))
        if e1 <= 0.0 or not math.isfinite(e1):
            raise ValueError("E1 special-function evaluation failed")
        scaled_e1 = math.exp(u) * e1
        log_e1 = math.log(e1)
        mean_x = 1.0 + (1.0 / scaled_e1 - u)
        bound = None  # No mathematical error claim for the library evaluation.
        method = "scipy.special.exp1; library error not certified"
    else:
        terms: list[float] = []
        term = 1.0
        for n in range(1, 257):
            term *= -n / u
            terms.append(term)
            series = 1.0 + math.fsum(terms)
            next_term = term * (-(n + 1) / u)
            if abs(next_term) < 0.25 * sys.float_info.epsilon * abs(series):
                break
            if abs(next_term) >= abs(term):
                raise ArithmeticError("asymptotic E1 expansion stopped decreasing")
        else:
            raise ArithmeticError("asymptotic E1 expansion did not converge to target")
        delta = math.fsum(terms)
        log_e1 = -u - math.log(u) + math.log1p(delta)
        # This avoids subtracting U from the nearly equal reciprocal of scaled E1.
        mean_x = 1.0 - u * delta / (1.0 + delta)
        bound = abs(next_term) / (abs(series) - abs(next_term))
        method = "scaled-E1 alternating asymptotic series with omitted-term bound"
    log_rate = (math.log(VELOCITY_FACTOR) + math.log(parameters.A_eV2_cm2)
                - math.log(parameters.threshold_eV) - 0.5 * math.log(theta) + log_e1)
    mean_excess = theta * mean_x
    return PureAOracle(log_rate, parameters.threshold_eV + mean_excess,
                       mean_excess, method, bound)
