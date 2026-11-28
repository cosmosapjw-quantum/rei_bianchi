"""Partial Maxwellian moments of a positive finite cross-section table.

The table is piecewise linear in energy [eV] and cross section [m^2].
No extrapolation, physical omitted-tail bound, isotope substitution, or
distribution closure is supplied.  The numerical temperature interval is
a computational contract, not a source-error or physical-admission claim.

For a Maxwellian relative-energy kernel K(g)=g sigma(E), E=mu*g^2/2,
M_j=<E^j K>, j=0..3.  M_0=alpha [m^3/s], M_1=beta [J m^3/s],
M_2=gamma [J^2 m^3/s]; M_3 supports the derivative of M_2.  Fixed table
endpoints and temperature-independent sigma imply
d M_j / d ln(T) = M_(j+1)/(k_B T) - 3 M_j/2.

For the actual CCC incident-electron table the admitted mapping is the
heavy fixed-target convention mu=m_e.  Other reduced masses are accepted
only under the explicit manufactured-relative-energy label.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math

import numpy as np
from numpy.polynomial.legendre import leggauss

EV_J = 1.602176634e-19
KB_J_K = 1.380649e-23
KB_EV_K = KB_J_K / EV_J
ME_KG = 9.1093837139e-31
A0_M = 5.29177210544e-11
DEFAULT_T_DOMAIN_K = (2000.0, 200000.0)
MOMENT_UNITS = ("m^3/s", "J m^3/s", "J^2 m^3/s", "J^3 m^3/s")
_LOG_MAX = math.log(np.finfo(np.float64).max)
_LOG_TINY = math.log(np.finfo(np.float64).tiny)


def _real_scalar(value, name, *, positive=False, nonnegative=False):
    if isinstance(value, (bool, np.bool_)) or np.iscomplexobj(value):
        raise ValueError(name + " must be a real scalar, not bool/complex")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(name + " must be a finite real scalar") from exc
    if not math.isfinite(number):
        raise ValueError(name + " must be finite")
    if positive and number <= 0:
        raise ValueError(name + " must be positive")
    if nonnegative and number < 0:
        raise ValueError(name + " must be nonnegative")
    return number


def _array(values, name):
    original = np.asarray(values)
    if original.dtype.kind in "bc" or original.ndim != 1:
        raise ValueError(name + " must be a real one-dimensional array")
    try:
        out = np.asarray(values, dtype=np.float64)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(name + " must contain finite real values") from exc
    if not np.isfinite(out).all():
        raise ValueError(name + " must be finite")
    return out


def _immutable(values):
    array = np.asarray(values)
    return np.frombuffer(array.tobytes(), dtype=array.dtype).reshape(array.shape)


@dataclass(frozen=True)
class MomentEvaluation:
    temperature_K: np.ndarray
    moments_SI: np.ndarray
    log_moments_SI: np.ndarray
    dlogT_moments_SI: np.ndarray
    dlogT_log_abs_SI: np.ndarray
    underflow: np.ndarray
    subnormal: np.ndarray
    derivative_underflow: np.ndarray
    logarithmic_slopes: np.ndarray | None
    conditional_mean_energy_J: np.ndarray | None
    identity: str
    zero_tabulated_integral: bool
    finite_source_partial: bool = True
    physical_tail_bound_established: bool = False

    @property
    def alpha_m3_s(self):
        return self.moments_SI[:, 0]

    @property
    def beta_J_m3_s(self):
        return self.moments_SI[:, 1]

    @property
    def gamma_J2_m3_s(self):
        return self.moments_SI[:, 2]

    @property
    def delta_J3_m3_s(self):
        return self.moments_SI[:, 3]


@dataclass(frozen=True)
class PreparedMaxwellianMoments:
    energy_eV: np.ndarray
    sigma_m2: np.ndarray
    threshold_eV: float
    source_id: str
    reduced_mass_kg: float = ME_KG
    energy_mapping: str = "manufactured_relative_energy"
    temperature_domain_K: tuple[float, float] = DEFAULT_T_DOMAIN_K
    quadrature_order: int = 16
    node_energy_eV: np.ndarray = field(init=False, repr=False)
    node_sigma_m2: np.ndarray = field(init=False, repr=False)
    node_weights_eV: np.ndarray = field(init=False, repr=False)
    weighted_energy_powers: np.ndarray = field(init=False, repr=False)
    anchor_eV: float = field(init=False)
    zero_tabulated_integral: bool = field(init=False)
    identity: str = field(init=False)

    def __post_init__(self):
        energy = _array(self.energy_eV, "energy_eV")
        sigma = _array(self.sigma_m2, "sigma_m2")
        if energy.shape != sigma.shape or energy.size < 2:
            raise ValueError("at least two paired table endpoints are required")
        if np.any(energy < 0) or np.any(np.diff(energy) <= 0):
            raise ValueError("table energies must be nonnegative and strictly increasing")
        if np.any(sigma < 0):
            raise ValueError("cross sections must be nonnegative; clipping is forbidden")
        threshold = _real_scalar(self.threshold_eV, "threshold_eV", nonnegative=True)
        if energy[0] < threshold:
            raise ValueError("table support starts below the declared threshold")
        mass = _real_scalar(self.reduced_mass_kg, "reduced_mass_kg", positive=True)
        if self.energy_mapping not in ("heavy_fixed_target_incident_electron",
                                       "manufactured_relative_energy"):
            raise ValueError("unqualified energy-to-relative-motion mapping")
        if self.energy_mapping == "heavy_fixed_target_incident_electron" and mass != ME_KG:
            raise ValueError("actual incident-electron table requires the declared m_e convention")
        if not isinstance(self.source_id, str) or not self.source_id.strip():
            raise ValueError("a nonempty source_id is required")
        if not isinstance(self.temperature_domain_K, (tuple, list, np.ndarray)) or len(self.temperature_domain_K) != 2:
            raise ValueError("temperature_domain_K must have two endpoints")
        lo, hi = (_real_scalar(v, "temperature domain endpoint", positive=True)
                  for v in self.temperature_domain_K)
        if lo >= hi:
            raise ValueError("temperature domain must be strictly increasing")
        order = self.quadrature_order
        if isinstance(order, (bool, np.bool_)) or not isinstance(order, (int, np.integer)):
            raise ValueError("quadrature_order must be an integer")
        if not 2 <= order <= 64:
            raise ValueError("supported quadrature order is 2..64")

        abscissa, weight = leggauss(int(order))
        t = (abscissa + 1.0) * 0.5
        width = np.diff(energy)
        with np.errstate(over="raise", invalid="raise", under="ignore"):
            nodes = (energy[:-1, None] + width[:, None] * t).ravel()
            weights = (width[:, None] * (weight * 0.5)).ravel()
            # Both coefficients are positive: no slope subtraction or clipping.
            sig_nodes = (sigma[:-1, None] * (1.0 - t)
                         + sigma[1:, None] * t).ravel()
            expected_positive = np.broadcast_to(
                ((sigma[:-1] > 0) | (sigma[1:] > 0))[:, None],
                (len(width), int(order))).ravel()
            if np.any(expected_positive & (sig_nodes == 0)) or np.any(weights <= 0):
                raise FloatingPointError("positive interpolation/weight underflow")
            active = sig_nodes > 0
            zero = not bool(np.any(active))
            if not zero:
                e = nodes[active]
                s = sig_nodes[active]
                w = weights[active]
                basis = w[:, None] * s[:, None] * e[:, None] ** np.arange(1, 5)
                if not np.isfinite(basis).all() or np.any(basis <= 0):
                    raise FloatingPointError("unrepresentable prepared positive moment weights")
                anchor = float(e.min())
            else:
                e = s = w = np.empty(0)
                basis = np.empty((0, 4))
                anchor = float(energy[0])
        for key, value in (("energy_eV", energy), ("sigma_m2", sigma),
                           ("node_energy_eV", e), ("node_sigma_m2", s),
                           ("node_weights_eV", w), ("weighted_energy_powers", basis)):
            object.__setattr__(self, key, _immutable(value))
        object.__setattr__(self, "threshold_eV", threshold)
        object.__setattr__(self, "reduced_mass_kg", mass)
        object.__setattr__(self, "temperature_domain_K", (lo, hi))
        object.__setattr__(self, "quadrature_order", int(order))
        object.__setattr__(self, "anchor_eV", anchor)
        object.__setattr__(self, "zero_tabulated_integral", zero)
        identity_data = dict(source_id=self.source_id, energy_eV=energy.tolist(),
            sigma_m2=sigma.tolist(), threshold_eV=threshold, reduced_mass_kg=mass,
            energy_mapping=self.energy_mapping, temperature_domain_K=(lo, hi),
            quadrature_order=int(order), units=MOMENT_UNITS,
            convention="finite_partial_piecewise_linear_positive_GL_v1",
            EV_J=EV_J, KB_J_K=KB_J_K, ME_KG=ME_KG)
        identity = hashlib.sha256(json.dumps(identity_data, sort_keys=True,
            separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        object.__setattr__(self, "identity", identity)

    def coverage(self):
        return dict(identity=self.identity, source_id=self.source_id,
            table_rows=len(self.energy_eV), interval_count=len(self.energy_eV)-1,
            interval_eV=[float(self.energy_eV[0]), float(self.energy_eV[-1])],
            threshold_eV=self.threshold_eV,
            lower_gap_eV=[self.threshold_eV, float(self.energy_eV[0])],
            lower_gap_is_unmodeled=bool(self.threshold_eV < self.energy_eV[0]),
            interpolation="positive piecewise linear in E and sigma",
            energy_mapping=self.energy_mapping, reduced_mass_kg=self.reduced_mass_kg,
            numerical_temperature_domain_K=list(self.temperature_domain_K),
            quadrature_order=self.quadrature_order, positive_node_count=len(self.node_energy_eV),
            full_physical_rate=False, finite_source_partial=True,
            high_energy_tail="UNMODELED", physical_tail_bound_established=False,
            physical_interpolation_error="UNQUANTIFIED", moment_units=MOMENT_UNITS)

    def evaluate(self, temperature_K, *, batch_size=128, require_full_physical_rate=False):
        if not isinstance(require_full_physical_rate, (bool, np.bool_)):
            raise ValueError("full-physical-rate request must be bool")
        if require_full_physical_rate:
            raise ValueError("a finite table does not supply a full physical rate")
        if isinstance(temperature_K, (bool, np.bool_)) or np.iscomplexobj(temperature_K):
            raise ValueError("temperature must be real, not bool/complex")
        original = np.asarray(temperature_K)
        if original.dtype.kind == "b" or original.ndim > 1:
            raise ValueError("temperature must be scalar or one-dimensional")
        temps = _array(np.atleast_1d(temperature_K), "temperature_K")
        lo, hi = self.temperature_domain_K
        if temps.size == 0 or np.any(temps < lo) or np.any(temps > hi):
            raise ValueError("temperature outside the declared numerical domain")
        if isinstance(batch_size, (bool, np.bool_)) or not isinstance(batch_size, (int, np.integer)) or batch_size <= 0:
            raise ValueError("batch_size must be a positive integer")
        n = len(temps)
        if self.zero_tabulated_integral:
            return MomentEvaluation(_immutable(temps), _immutable(np.zeros((n, 4))),
                _immutable(np.full((n, 4), -np.inf)), _immutable(np.zeros((n, 3))),
                _immutable(np.full((n, 3), -np.inf)), _immutable(np.zeros((n, 4), bool)),
                _immutable(np.zeros((n, 4), bool)), _immutable(np.zeros((n, 3), bool)),
                None, None, self.identity, True)

        values = np.empty((n, 4))
        logs = np.empty((n, 4))
        slopes = np.empty((n, 3))
        deriv = np.empty((n, 3))
        deriv_logs = np.full((n, 3), -np.inf)
        means = np.empty(n)
        log_prefactor_const = 0.5 * (math.log(8.0 * EV_J / math.pi)
                                    - math.log(self.reduced_mass_kg))
        for start in range(0, n, int(batch_size)):
            stop = min(start + int(batch_size), n)
            theta = KB_EV_K * temps[start:stop]
            with np.errstate(over="raise", invalid="raise", divide="raise", under="ignore"):
                shift = (self.node_energy_eV - self.anchor_eV)[None, :] / theta[:, None]
                exponential = np.exp(-shift)
                sums = exponential @ self.weighted_energy_powers
                if not np.isfinite(sums).all() or np.any(sums <= 0):
                    raise FloatingPointError("nonpositive or unrepresentable quadrature sum")
                log_prefactor = log_prefactor_const - 1.5 * np.log(theta)
                chunk_logs = (log_prefactor[:, None] - (self.anchor_eV / theta)[:, None]
                    + np.log(sums) + np.arange(4)[None, :] * math.log(EV_J))
                if not np.isfinite(chunk_logs).all() or np.any(chunk_logs > _LOG_MAX):
                    raise FloatingPointError("unrepresentable moment logarithm/overflow")
                chunk_slopes = sums[:, 1:] / sums[:, :-1] / theta[:, None] - 1.5
                if not np.isfinite(chunk_slopes).all():
                    raise FloatingPointError("unrepresentable logarithmic temperature slope")
                chunk_deriv_logs = np.full(chunk_slopes.shape, -np.inf)
                nonzero = chunk_slopes != 0
                chunk_deriv_logs[nonzero] = (chunk_logs[:, :3][nonzero]
                                             + np.log(np.abs(chunk_slopes[nonzero])))
                if np.any(chunk_deriv_logs > _LOG_MAX):
                    raise FloatingPointError("temperature derivative overflows binary64")
                values[start:stop] = np.exp(chunk_logs)
                logs[start:stop] = chunk_logs
                slopes[start:stop] = chunk_slopes
                deriv_logs[start:stop] = chunk_deriv_logs
                deriv[start:stop] = np.sign(chunk_slopes) * np.exp(chunk_deriv_logs)
                means[start:stop] = EV_J * sums[:, 1] / sums[:, 0]
        underflow = (values == 0) & np.isfinite(logs)
        subnormal = (values != 0) & (logs < _LOG_TINY)
        derivative_underflow = (deriv == 0) & np.isfinite(deriv_logs)
        return MomentEvaluation(*map(_immutable, (temps, values, logs, deriv, deriv_logs,
            underflow, subnormal, derivative_underflow, slopes, means)), self.identity, False)
