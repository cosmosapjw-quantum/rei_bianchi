"""PHYS82 conditional Li7 threshold-gap operators.

The four CCC-matched models and the independent recentered ZA1969 slope
comparator are finite-support hypotheses.  No outside-window physical
cross section, physical confidence interval, or coupled evolution bound is
provided.  The stationary-target Maxwell convention is inherited unchanged.
All logarithms refer to numerical values in the stated units.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Real
from types import MappingProxyType

import numpy as np
from scipy.special import gammainc, gammaln

if __package__:
    from .vendor.phys81.finite_ci import (
        FiniteCIRate, KB_EV_K, MAXWELL_CM3_S_PER_CM2,
    )
else:
    from vendor.phys81.finite_ci import (
        FiniteCIRate, KB_EV_K, MAXWELL_CM3_S_PER_CM2,
    )


ICHEMICAL_EV = 5.39172060034581
E0_EV = 6.0
SIGMA0_CM2 = 5.18148e-17
ZA_SLOPE_CM2_PER_EV = 9.0e-17
P_W = (math.sqrt(91.0 / 3.0) - 1.0) / 4.0
NUMERICAL_T_DOMAIN_K = (255.0, 50000.0)
MODEL_NAMES = ("L0", "L1", "W0", "W1", "ZA1969")
MATCHED_MODEL_NAMES = MODEL_NAMES[:4]


def _real(value, name: str) -> float:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ValueError(f"{name}_MUST_BE_REAL_NOT_BOOL")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name}_MUST_BE_FINITE")
    return result


def _label(value, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{name}_NONEMPTY_STRIPPED_STRING_REQUIRED")
    return value


def _finite_only(full_physical_rate) -> None:
    if not isinstance(full_physical_rate, (bool, np.bool_)):
        raise ValueError("FULL_PHYSICAL_RATE_FLAG_MUST_BE_BOOL")
    if full_physical_rate:
        raise ValueError("FULL_PHYSICAL_CI_RATE_UNAVAILABLE")


def _temperature(value) -> float:
    temperature = _real(value, "TEMPERATURE_K")
    if not NUMERICAL_T_DOMAIN_K[0] <= temperature <= NUMERICAL_T_DOMAIN_K[1]:
        raise ValueError("PHYS82_TEMPERATURE_OUTSIDE_255_TO_50000_K")
    return temperature


def _rate_and_derivative(log_rate: float, dlog: float) -> tuple[float, float]:
    """Preserve a representable derivative even when K itself underflows."""
    try:
        rate = math.exp(log_rate)
        derivative = (0.0 if dlog == 0.0 else
                      math.copysign(math.exp(log_rate + math.log(abs(dlog))), dlog))
    except OverflowError as exc:
        raise ArithmeticError("PHYS82_RATE_OR_DERIVATIVE_OVERFLOW") from exc
    if not math.isfinite(rate) or not math.isfinite(derivative):
        raise ArithmeticError("PHYS82_NONFINITE_RATE_OR_DERIVATIVE")
    return rate, derivative


def _log_scaled_moment(a: float, z: float) -> float:
    # F = exp(-z) sum_k z^k Gamma(a)/Gamma(a+k+1).
    # This positive small-z expansion avoids subtractive gamma recurrence.
    if z < 0.5:
        term = 1.0 / a
        terms = [term]
        for k in range(1, 256):
            term *= z / (a + k)
            terms.append(term)
            total = math.fsum(terms)
            ratio = z / (a + k + 1.0)
            remainder_bound = term * ratio / (1.0 - ratio)
            if remainder_bound <= np.finfo(float).eps * total / 4.0:
                return -z + math.log(total)
        raise ArithmeticError("PHYS82_POSITIVE_SERIES_DID_NOT_CONVERGE")
    regularized = float(gammainc(a, z))
    if not math.isfinite(regularized) or regularized <= 0.0:
        raise ArithmeticError("PHYS82_REGULARIZED_GAMMA_UNREPRESENTABLE")
    result = float(gammaln(a)) + math.log(regularized) - a * math.log(z)
    if not math.isfinite(result):
        raise ArithmeticError("PHYS82_NONFINITE_LOG_SCALED_MOMENT")
    return result


def scaled_log_moments(p, z) -> tuple[float, float, float]:
    """Return log F_0, log F_1, log F_2 for F_j=int_0^1 t^(p+j)e^-zt dt.

    The supported exponent interval is the frozen sensitivity rectangle;
    arbitrary large-p numerical reliability is not inferred from this work.
    z=0 is the analytic removable limit, useful independently of temperature.
    """
    exponent = _real(p, "EXPONENT_P")
    scale = _real(z, "GAP_OVER_THETA")
    if not 1.0 <= exponent <= P_W:
        raise ValueError("PHYS82_P_OUTSIDE_FROZEN_1_TO_WANNIER_INTERVAL")
    if scale < 0.0:
        raise ValueError("GAP_OVER_THETA_MUST_BE_NONNEGATIVE")
    return tuple(_log_scaled_moment(exponent + j + 1.0, scale)
                 for j in range(3))


@dataclass(frozen=True, slots=True)
class ThresholdRate:
    """Immutable rate summary; a finite operator is never a full rate."""

    temperature_K: float
    K_cm3_s: float
    logK_cm3_s: float
    mean_incoming_eV: float
    mean_excess_over_chemical_eV: float
    dK_dT_cm3_s_K: float
    dlogK_dT_per_K: float
    float64_underflow: bool
    derivative_float64_underflow: bool
    model: str
    component: str
    source_identity: str
    Ichemical_eV: float
    lower_eV: float
    upper_eV: float
    gap_fraction: float
    species: str = "Li7"
    finite_window_only: bool = True
    full_physical_rate_available: bool = False

    def __post_init__(self) -> None:
        _temperature(self.temperature_K)
        for name in (
            "K_cm3_s", "logK_cm3_s", "mean_incoming_eV",
            "mean_excess_over_chemical_eV", "dK_dT_cm3_s_K",
            "dlogK_dT_per_K", "Ichemical_eV", "lower_eV",
            "upper_eV", "gap_fraction",
        ):
            _real(getattr(self, name), name.upper())
        for name in ("model", "source_identity", "species"):
            _label(getattr(self, name), name.upper())
        for name in ("float64_underflow", "derivative_float64_underflow",
                     "finite_window_only", "full_physical_rate_available"):
            if not isinstance(getattr(self, name), (bool, np.bool_)):
                raise ValueError(f"{name.upper()}_MUST_BE_BOOL")
        if self.species != "Li7" or self.component not in ("baseline", "gap", "total"):
            raise ValueError("PHYS82_RATE_SPECIES_OR_COMPONENT_INVALID")
        if self.Ichemical_eV <= 0.0 or not (
            self.Ichemical_eV <= self.lower_eV < self.upper_eV
        ):
            raise ValueError("PHYS82_RATE_SUPPORT_INVALID")
        if not self.lower_eV <= self.mean_incoming_eV <= self.upper_eV:
            raise ValueError("PHYS82_MEAN_OUTSIDE_SUPPORT")
        if self.mean_excess_over_chemical_eV < 0.0 or not math.isclose(
            self.mean_excess_over_chemical_eV,
            self.mean_incoming_eV - self.Ichemical_eV,
            rel_tol=2e-13, abs_tol=2e-14,
        ):
            raise ValueError("PHYS82_MEAN_EXCESS_INCONSISTENT")
        if self.K_cm3_s < 0.0 or not 0.0 <= self.gap_fraction <= 1.0:
            raise ValueError("PHYS82_RATE_OR_GAP_FRACTION_INVALID")
        if bool(self.float64_underflow) != (self.K_cm3_s == 0.0):
            raise ValueError("PHYS82_RATE_UNDERFLOW_FLAG_INCONSISTENT")
        expected_derivative_underflow = (
            self.dlogK_dT_per_K != 0.0 and self.dK_dT_cm3_s_K == 0.0
        )
        if bool(self.derivative_float64_underflow) != expected_derivative_underflow:
            raise ValueError("PHYS82_DERIVATIVE_UNDERFLOW_FLAG_INCONSISTENT")
        if not self.finite_window_only or self.full_physical_rate_available:
            raise ValueError("FULL_PHYSICAL_CI_RATE_UNAVAILABLE")
        if self.component == "baseline" and self.gap_fraction != 0.0:
            raise ValueError("PHYS82_BASELINE_GAP_FRACTION_MUST_BE_ZERO")
        if self.component == "gap" and self.gap_fraction != 1.0:
            raise ValueError("PHYS82_GAP_COMPONENT_FRACTION_MUST_BE_ONE")

    @property
    def log10K_cm3_s(self) -> float:
        return self.logK_cm3_s / math.log(10.0)

    @property
    def thermal_loss_per_event_eV(self) -> float:
        return self.Ichemical_eV


@dataclass(frozen=True, slots=True)
class ThresholdGap:
    """Positive immutable threshold model on [Ichemical, E0].

    amplitude_cm2 is the left-hand endpoint amplitude at E0.  In ZA1969
    it equals the independent historical slope times gap width, and is
    deliberately not forced to the CCC endpoint.
    """

    name: str
    p: float
    q: int
    amplitude_cm2: float
    source_identity: str
    matched_CCC_endpoint: bool
    Ichemical_eV: float = ICHEMICAL_EV
    E0_eV: float = E0_EV

    def __post_init__(self) -> None:
        _label(self.name, "MODEL_NAME")
        _label(self.source_identity, "SOURCE_IDENTITY")
        exponent = _real(self.p, "EXPONENT_P")
        power = _real(self.q, "POWER_Q")
        amplitude = _real(self.amplitude_cm2, "AMPLITUDE_CM2")
        chemical = _real(self.Ichemical_eV, "ICHEMICAL_EV")
        endpoint = _real(self.E0_eV, "E0_EV")
        if not 1.0 <= exponent <= P_W or power not in (0.0, 1.0):
            raise ValueError("PHYS82_P_Q_OUTSIDE_SUPPORTED_RECTANGLE")
        if amplitude <= 0.0 or not 0.0 < chemical < endpoint:
            raise ValueError("PHYS82_POSITIVE_AMPLITUDE_AND_GAP_REQUIRED")
        if not isinstance(self.matched_CCC_endpoint, (bool, np.bool_)):
            raise ValueError("MATCHED_CCC_ENDPOINT_FLAG_MUST_BE_BOOL")
        # The named public models are frozen, including their source amplitude.
        if self.name not in MODEL_NAMES:
            raise ValueError("PHYS82_UNKNOWN_FROZEN_MODEL")
        expected_p = P_W if self.name.startswith("W") else 1.0
        expected_q = 1 if self.name in ("L1", "W1") else 0
        matched = self.name in MATCHED_MODEL_NAMES
        expected_amplitude = (SIGMA0_CM2 if matched else
                              ZA_SLOPE_CM2_PER_EV * (E0_EV - ICHEMICAL_EV))
        if (exponent != expected_p or power != expected_q
                or chemical != ICHEMICAL_EV or endpoint != E0_EV
                or amplitude != expected_amplitude
                or bool(self.matched_CCC_endpoint) != matched):
            raise ValueError("PHYS82_NAMED_MODEL_CONTRACT_MISMATCH")
        for name, value in (("p", exponent), ("q", int(power)),
                            ("amplitude_cm2", amplitude),
                            ("Ichemical_eV", chemical), ("E0_eV", endpoint),
                            ("matched_CCC_endpoint", matched)):
            object.__setattr__(self, name, value)

    @property
    def width_eV(self) -> float:
        return self.E0_eV - self.Ichemical_eV

    def cross_section(self, energy_eV, *, full_physical_rate=False):
        """Evaluate selected gap support; vector outputs have immutable bytes."""
        _finite_only(full_physical_rate)
        if isinstance(energy_eV, Real) and not isinstance(energy_eV, (bool, np.bool_)):
            energy = _real(energy_eV, "INCIDENT_ENERGY_EV")
            if energy < 0.0:
                raise ValueError("INCIDENT_ENERGY_EV_MUST_BE_NONNEGATIVE")
            if not self.Ichemical_eV < energy <= self.E0_eV:
                return 0.0
            t = (energy - self.Ichemical_eV) / self.width_eV
            return self.amplitude_cm2 * t**self.p * (self.E0_eV / energy)**self.q
        raw = np.asarray(energy_eV, dtype=object)
        if raw.ndim != 1 or raw.size == 0:
            raise ValueError("INCIDENT_ENERGY_REQUIRES_REAL_SCALAR_OR_NONEMPTY_VECTOR")
        values = np.asarray([_real(v, "INCIDENT_ENERGY_EV") for v in raw], dtype=float)
        if np.any(values < 0.0):
            raise ValueError("INCIDENT_ENERGY_EV_MUST_BE_NONNEGATIVE")
        result = np.zeros_like(values)
        use = (values > self.Ichemical_eV) & (values <= self.E0_eV)
        result[use] = (
            self.amplitude_cm2
            * ((values[use] - self.Ichemical_eV) / self.width_eV)**self.p
            * (self.E0_eV / values[use])**self.q
        )
        return np.frombuffer(result.tobytes(), dtype=np.float64)

    def evaluate(self, temperature_K, *, full_physical_rate=False) -> ThresholdRate:
        _finite_only(full_physical_rate)
        temperature = _temperature(temperature_K)
        theta = KB_EV_K * temperature
        delta = self.width_eV
        log_f0, log_f1, log_f2 = scaled_log_moments(self.p, delta / theta)
        r1, r2 = math.exp(log_f1 - log_f0), math.exp(log_f2 - log_f0)
        if not 0.0 < r2 < r1 < 1.0:
            raise ArithmeticError("PHYS82_POSITIVE_MOMENT_ORDER_FAILED")
        if self.q == 0:
            flux = self.Ichemical_eV + delta * r1
            excess = delta * (self.Ichemical_eV * r1 + delta * r2) / flux
        else:
            flux = self.E0_eV
            excess = delta * r1
        mean = self.Ichemical_eV + excess
        log_rate = math.fsum((
            math.log(MAXWELL_CM3_S_PER_CM2), math.log(self.amplitude_cm2),
            math.log(delta), -1.5 * math.log(theta), -self.Ichemical_eV / theta,
            log_f0, math.log(flux),
        ))
        dlog = (mean / theta - 1.5) / temperature
        rate, derivative = _rate_and_derivative(log_rate, dlog)
        return ThresholdRate(
            temperature, rate, log_rate, mean, excess, derivative, dlog,
            rate == 0.0, dlog != 0.0 and derivative == 0.0,
            self.name, "gap", self.source_identity, self.Ichemical_eV,
            self.Ichemical_eV, self.E0_eV, 1.0,
        )

    def coverage(self) -> dict:
        return {
            "model": self.name,
            "support_eV": [self.Ichemical_eV, self.E0_eV],
            "temperature_domain_K": list(NUMERICAL_T_DOMAIN_K),
            "matched_CCC_endpoint": self.matched_CCC_endpoint,
            "source_class": ("CONDITIONAL_CCC_MATCHED_FAMILY" if
                             self.matched_CCC_endpoint else
                             "RECENTERED_HISTORICAL_SLOPE_COMPARATOR"),
            "source_identity": self.source_identity,
            "outside_window": "zero by selected finite-operator definition only",
            "physical_gap_coverage": "OPEN",
            "physical_tail_above_15_eV": "OPEN",
            "full_physical_rate_available": False,
            "model_envelope_is_physical_confidence_interval": False,
            "coupled_feedback_error_bound": False,
            "thermal_loss_per_event_eV": self.Ichemical_eV,
            "mean_incoming_energy_is_additional_heat_loss": False,
        }


def named_models(*, source_identity="PHYS82:FROZEN_PRIMARY_SOURCE_CONTRACT"):
    """Return all five immutable models in frozen order in a read-only mapping."""
    source = _label(source_identity, "SOURCE_IDENTITY")
    return MappingProxyType({
        name: ThresholdGap(
            name=name,
            p=P_W if name.startswith("W") else 1.0,
            q=1 if name in ("L1", "W1") else 0,
            amplitude_cm2=(SIGMA0_CM2 if name in MATCHED_MODEL_NAMES else
                           ZA_SLOPE_CM2_PER_EV * (E0_EV - ICHEMICAL_EV)),
            source_identity=source + ":" + name,
            matched_CCC_endpoint=name in MATCHED_MODEL_NAMES,
        )
        for name in MODEL_NAMES
    })


def from_finite_rate(rate: FiniteCIRate) -> ThresholdRate:
    """Copy an already evaluated immutable PHYS81 rate, without evaluating it."""
    if not isinstance(rate, FiniteCIRate) or rate.finite_window_only is not True:
        raise ValueError("PHYS82_IMMUTABLE_FINITE_BASELINE_RATE_REQUIRED")
    return ThresholdRate(
        rate.temperature_K, rate.K_cm3_s, rate.logK_cm3_s,
        rate.mean_incoming_eV, rate.mean_incoming_eV - rate.Ichemical_eV,
        rate.dK_dT_cm3_s_K, rate.dlogK_dT_per_K, rate.float64_underflow,
        rate.dlogK_dT_per_K != 0.0 and rate.dK_dT_cm3_s_K == 0.0,
        "CCC_6_15", "baseline", rate.source_identity, rate.Ichemical_eV,
        rate.lower_eV, rate.upper_eV, 0.0, species=rate.species,
    )


def _compatible_pair(baseline, gap) -> tuple[ThresholdRate, ThresholdRate]:
    if isinstance(baseline, FiniteCIRate):
        baseline = from_finite_rate(baseline)
    if not isinstance(baseline, ThresholdRate) or not isinstance(gap, ThresholdRate):
        raise ValueError("PHYS82_IMMUTABLE_RATE_PAIR_REQUIRED")
    if baseline.component != "baseline" or gap.component != "gap":
        raise ValueError("PHYS82_BASELINE_AND_GAP_COMPONENTS_REQUIRED")
    if (baseline.temperature_K != gap.temperature_K
            or baseline.Ichemical_eV != gap.Ichemical_eV
            or baseline.species != gap.species
            or gap.upper_eV != baseline.lower_eV
            or gap.lower_eV != gap.Ichemical_eV):
        raise ValueError("PHYS82_RATE_PAIR_CONTRACT_MISMATCH")
    return baseline, gap


def combine_rates(baseline, gap, *, full_physical_rate=False) -> ThresholdRate:
    """Add contiguous positive finite components using logaddexp."""
    _finite_only(full_physical_rate)
    baseline, gap = _compatible_pair(baseline, gap)
    log_rate = float(np.logaddexp(baseline.logK_cm3_s, gap.logK_cm3_s))
    wb = math.exp(baseline.logK_cm3_s - log_rate)
    wg = math.exp(gap.logK_cm3_s - log_rate)
    norm = wb + wg
    wb, wg = wb / norm, wg / norm
    mean = math.fsum((wb * baseline.mean_incoming_eV, wg * gap.mean_incoming_eV))
    excess = math.fsum((wb * baseline.mean_excess_over_chemical_eV,
                        wg * gap.mean_excess_over_chemical_eV))
    dlog = (mean / (KB_EV_K * gap.temperature_K) - 1.5) / gap.temperature_K
    rate, derivative = _rate_and_derivative(log_rate, dlog)
    return ThresholdRate(
        gap.temperature_K, rate, log_rate, mean, excess, derivative, dlog,
        rate == 0.0, dlog != 0.0 and derivative == 0.0, gap.model,
        "total", baseline.source_identity + "+" + gap.source_identity,
        gap.Ichemical_eV, gap.lower_eV, baseline.upper_eV, wg,
    )


@dataclass(frozen=True, slots=True)
class ExposureResult:
    exposure_cm3_inverse_s: float
    baseline_hazard: float | None
    gap_hazard: float | None
    total_hazard: float | None
    baseline_hazard_overflow: bool
    gap_hazard_overflow: bool
    total_hazard_overflow: bool
    baseline_probability: float
    gap_alone_probability: float
    total_probability: float
    delta_probability: float
    delta_probability_upper_bound: float
    delta_probability_unattenuated_upper_bound: float
    delta_probability_float64_underflow: bool
    prescribed_T_ne_only: bool = True
    coupled_feedback_error_bound: bool = False


def fixed_exposure(baseline, gap, exposure_cm3_inverse_s, *,
                   full_physical_rate=False) -> ExposureResult:
    """Exact fixed-history hazard difference using -expm1, never Ptot-Pbase.

    Lambda is n_e*tau in cm^-3 s.  A null hazard records binary64 overflow;
    the corresponding probability still has its well-defined saturation.
    """
    _finite_only(full_physical_rate)
    baseline, gap = _compatible_pair(baseline, gap)
    exposure = _real(exposure_cm3_inverse_s, "EXPOSURE_CM3_INVERSE_S")
    if exposure < 0.0:
        raise ValueError("EXPOSURE_MUST_BE_NONNEGATIVE")

    def hazard(log_rate):
        if exposure == 0.0:
            return 0.0
        try:
            return math.exp(math.log(exposure) + log_rate)
        except OverflowError:
            return math.inf

    hb, hg = hazard(baseline.logK_cm3_s), hazard(gap.logK_cm3_s)
    ht = hb + hg
    survival = math.exp(-hb)
    pb, pg, pt = -math.expm1(-hb), -math.expm1(-hg), -math.expm1(-ht)
    delta = survival * pg
    bound = survival * min(1.0, hg)
    return ExposureResult(
        exposure, hb if math.isfinite(hb) else None,
        hg if math.isfinite(hg) else None, ht if math.isfinite(ht) else None,
        not math.isfinite(hb), not math.isfinite(hg), not math.isfinite(ht),
        pb, pg, pt, delta, bound, min(1.0, hg),
        exposure > 0.0 and delta == 0.0,
    )


# A short descriptive alias for callers constructing the frozen model objects.
GapModel = ThresholdGap
