"""Source-derived, first-Sonine neutral H/He shear viscosity in SI units.

Wargnier et al. (2020), Appendix C.29, C.30, C.35--C.38, supplies the
two-species matrix. Bruno et al. (2010), Eq. 11 and Table I, supplies the
collision-integral fits pinned in data/NEUTRAL_H_HE_TRANSPORT_SUBSET.json.
The positive rational expression is an exact algebraic reduction of that
matrix, including its pure-species limits. It adds no composition floor.

Masses are explicit caller inputs. The physical assumptions are a dilute,
common-temperature neutral gas near a Maxwellian hydrodynamic state. This
module supplies neither an all-species gas closure nor a transient collision
operator. The optional diagnostic nu_match=p_neutral/eta is a viscosity
matching convention, not an identity for the Boltzmann relaxation spectrum.
The scalar path needs only the standard library; NumPy is imported lazily.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from numbers import Real
from pathlib import Path


KB_J_K = 1.380649e-23
TEMPERATURE_DOMAIN_K = (50.0, 50000.0)
DATA_PATH = Path(__file__).resolve().parents[1] / "data/NEUTRAL_H_HE_TRANSPORT_SUBSET.json"
DATA_SHA256 = "699114aa23d13d38bd1d67fd74358fb52d06c25e8d3c87aa8d282de82dc26542"
_data_bytes = DATA_PATH.read_bytes()
if hashlib.sha256(_data_bytes).hexdigest() != DATA_SHA256:
    raise ValueError("Neutral transport data differ from the source-audited subset")
_data = json.loads(_data_bytes)
_coefficients = {(tuple(row["pair"]), row["kind"]): tuple(row["coefficients"])
                 for row in _data["fits"]}


def _finite_real(value, name):
    if not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite real scalar")
    return float(value)


def _positive(value, name):
    value = _finite_real(value, name)
    if value <= 0.0:
        raise ValueError(f"{name} must be positive")
    return value


def _expit(value):
    if value >= 0.0:
        return 1.0 / (1.0 + math.exp(-value))
    exponential = math.exp(value)
    return exponential / (1.0 + exponential)


def collision_integral(T_K, pair, kind):
    """Return Qbar [m^2]; reject extrapolation outside 50--50000 K.

    The Bruno fit gives sigma^2 Omega* in angstrom^2. The area-form
    normalization used by the viscosity equations is pi * 1e-20 * fit.
    """
    temperature = _positive(T_K, "T_K")
    if not TEMPERATURE_DOMAIN_K[0] <= temperature <= TEMPERATURE_DOMAIN_K[1]:
        raise ValueError("Bruno2010 fit requires 50 <= T_K <= 50000 K")
    try:
        a = _coefficients[(tuple(pair), kind)]
    except (KeyError, TypeError) as error:
        raise ValueError("Unsupported neutral collision-integral pair/kind") from error
    logarithm = math.log(temperature)
    fit_A2 = ((a[0] + a[1] * logarithm) * _expit(2.0 * (logarithm - a[2]) / a[3])
              + a[4] * _expit(2.0 * (logarithm - a[5]) / a[6]))
    return _positive(math.pi * 1e-20 * fit_A2, "Qbar_m2")


def _scaled_array_weights(n_H_weight, n_He_weight):
    """Validate and broadcast finite real weights, then scale homogeneously."""
    import numpy as np

    arrays = []
    for value in (n_H_weight, n_He_weight):
        raw = np.asarray(value)
        if raw.dtype.kind not in "biuf":
            raise ValueError("Number weights must contain real numeric values")
        array = np.asarray(raw, dtype=np.float64)
        if not np.all(np.isfinite(array)) or np.any(array < 0.0):
            raise ValueError("Number weights must be finite and nonnegative")
        arrays.append(array)
    try:
        hydrogen, helium = np.broadcast_arrays(*arrays)
    except ValueError as error:
        raise ValueError("Number weights must have broadcast-compatible shapes") from error
    scale = np.maximum(hydrogen, helium)
    if np.any(scale == 0.0):
        raise ValueError("A zero-density pair has no defined mixture composition")
    # This is exact homogeneity of the formula, not a species floor or clipping.
    return hydrogen / scale, helium / scale


@dataclass(frozen=True)
class NeutralTransport:
    """Coefficients prepared once for fixed temperature and explicit masses."""

    T_K: float
    mass_H_kg: float
    mass_He_kg: float
    QHH22_m2: float
    QHHe11_m2: float
    QHHe22_m2: float
    QHeHe22_m2: float
    eta_H_Pa_s: float
    eta_He_Pa_s: float
    nD_HHe_per_m_s: float
    r: float
    Astar: float
    u: float
    _a: float
    _b: float
    _c_H: float
    _c_He: float
    _cross_D: float
    _sqrt_r: float

    def viscosity(self, n_H_weight, n_He_weight):
        """Scalar eta [Pa s] for nonnegative weights proportional to number."""
        hydrogen = _finite_real(n_H_weight, "n_H_weight")
        helium = _finite_real(n_He_weight, "n_He_weight")
        if hydrogen < 0.0 or helium < 0.0:
            raise ValueError("Number weights must be nonnegative")
        scale = max(hydrogen, helium)
        if scale == 0.0:
            raise ValueError("A zero-density pair has no defined mixture composition")
        # Preserve the pure-species values bit for bit, including signed zero.
        if helium == 0.0:
            return self.eta_H_Pa_s
        if hydrogen == 0.0:
            return self.eta_He_Pa_s
        x, y = hydrogen / scale, helium / scale
        numerator = (self.u * (1.2 * self.Astar * (x / self._sqrt_r - y * self._sqrt_r) ** 2
                              + 2.0 * (x + y) ** 2) + x * y * (self._a + self._b))
        denominator = (x * x * self._c_He * self._a + y * y * self._c_H * self._b
                       + x * y * self._cross_D)
        return _positive(numerator / denominator, "eta_mix_Pa_s")

    def viscosity_vectorized(self, n_H_weight, n_He_weight):
        """NumPy binary64 eta with broadcasting and the scalar input contract."""
        import numpy as np

        x, y = _scaled_array_weights(n_H_weight, n_He_weight)
        numerator = (self.u * (1.2 * self.Astar * (x / self._sqrt_r - y * self._sqrt_r) ** 2
                              + 2.0 * (x + y) ** 2) + x * y * (self._a + self._b))
        denominator = (x * x * self._c_He * self._a + y * y * self._c_H * self._b
                       + x * y * self._cross_D)
        result = numerator / denominator
        result = np.where(y == 0.0, self.eta_H_Pa_s, result)
        result = np.where(x == 0.0, self.eta_He_Pa_s, result)
        if not np.all(np.isfinite(result)) or np.any(result <= 0.0):
            raise ValueError("eta_mix_Pa_s is not finite and positive")
        return result


def prepare_neutral_transport(T_K, mass_H_kg, mass_He_kg):
    """Prepare temperature/mass coefficients without prescribing their values."""
    hydrogen_mass = _positive(mass_H_kg, "mass_H_kg")
    helium_mass = _positive(mass_He_kg, "mass_He_kg")
    temperature = _positive(T_K, "T_K")
    q_hh = collision_integral(temperature, ("H", "H"), "Q22")
    q_hhe_11 = collision_integral(temperature, ("H", "He"), "Q11")
    q_hhe_22 = collision_integral(temperature, ("H", "He"), "Q22")
    q_hehe = collision_integral(temperature, ("He", "He"), "Q22")
    try:
        eta_h = _positive(5.0 / 16.0 * math.sqrt(math.pi * KB_J_K * temperature * hydrogen_mass)
                          / q_hh, "eta_H_Pa_s")
        eta_he = _positive(5.0 / 16.0 * math.sqrt(math.pi * KB_J_K * temperature * helium_mass)
                           / q_hehe, "eta_He_Pa_s")
        n_diffusion = _positive(3.0 / 16.0 * math.sqrt(2.0 * math.pi * KB_J_K * temperature
                                    * (1.0 / hydrogen_mass + 1.0 / helium_mass)) / q_hhe_11,
                               "nD_HHe_per_m_s")
        ratio = _positive(helium_mass / hydrogen_mass, "mass_ratio")
        astar = _positive(q_hhe_22 / q_hhe_11, "Astar")
        u = _positive(1.0 / (n_diffusion * (hydrogen_mass + helium_mass)), "u")
        a, b = 1.0 / eta_h, 1.0 / eta_he
        c_h = _positive(u * (1.2 * astar * ratio + 2.0), "c_H")
        c_he = _positive(u * (1.2 * astar / ratio + 2.0), "c_He")
        cross_d = _positive(a * b + 2.4 * astar * u * u * (ratio + 1.0 / ratio + 2.0),
                            "cross_D")
    except (OverflowError, ZeroDivisionError) as error:
        raise ValueError("Mass/temperature coefficients exceed binary64 representability") from error
    return NeutralTransport(temperature, hydrogen_mass, helium_mass, q_hh, q_hhe_11,
                            q_hhe_22, q_hehe, eta_h, eta_he, n_diffusion, ratio, astar, u,
                            a, b, c_h, c_he, cross_d, math.sqrt(ratio))
