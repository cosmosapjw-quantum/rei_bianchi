"""Source-defined H1 CI reference: Le--Cambier (2016), Eq. 85, isotropic §III.E.

This is a semiclassical heavy stationary-target approximation, NOT a calibrated
H1 angular provider. I=13.6 eV follows the cited source; a0 and SI constants are
the already pinned HE36 values (a deliberate precision update of source a0=.529 A).
No CCC table is combined with this kernel. Number/heat/STF use one event law.

All-energy analytic Maxwellian integration assumes a nonrelativistic, ground-H,
stationary heavy target and a temperature-independent cross section. The
2000--200000 K interval is a numerical contract, not a physical error envelope.
Pressure-moment use is restricted to an infinitesimal incoming Grad perturbation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math

import numpy as np
from scipy.special import expn


# Single constant owner in this component. Values copied unchanged from HE36
# maxwellian_moments.py SHA256 644260261b82d6a528fd049b2bb20702e4c66de087406c7868a395a41ec99c2c.
EV_J = 1.602176634e-19
KB_J_K = 1.380649e-23
ME_KG = 9.1093837139e-31
A0_M = 5.29177210544e-11
I_EV = 13.6
I_J = I_EV * EV_J
TEMPERATURE_DOMAIN_K = (2000.0, 200000.0)
SOURCE_PDF_SHA256 = "5ee591cde0cb90c03b5fc47a8ad439bae93bcc36bd05a4cbb4e1943fec93fc68"
SOURCE_DOI = "10.1063/1.4953050"
MODEL_SCOPE = "source_native_LeCambier_Eq85_isotropic_heavy_target"
ENERGY_MAPPING = "heavy_fixed_target_incident_electron"
MOMENT_UNITS = ("m^3/s", "J m^3/s", "J^2 m^3/s", "J^3 m^3/s")
_IDENTITY_CONTRACT = {
    "algorithm": "lc_h1_ci_expn2_v1", "source_pdf_sha256": SOURCE_PDF_SHA256,
    "source_doi": SOURCE_DOI, "model_scope": MODEL_SCOPE,
    "energy_mapping": ENERGY_MAPPING, "threshold_eV": I_EV,
    "A0_M": A0_M, "ME_KG": ME_KG, "EV_J": EV_J, "KB_J_K": KB_J_K,
    "temperature_domain_K": TEMPERATURE_DOMAIN_K,
    "angular_density_sr_minus2": "1/(16*pi^2)",
    "constant_policy": "HE36_SI_constants_source_13.6eV_threshold",
    "physical_angular_calibration": False,
}
MODEL_IDENTITY = hashlib.sha256(json.dumps(
    _IDENTITY_CONTRACT, sort_keys=True, separators=(",", ":"), allow_nan=False
).encode()).hexdigest()


def _real(values, name):
    """Reject bool, complex, string/object and non-finite inputs before casting."""
    arr = np.asarray(values)
    if arr.dtype.kind not in "iuf" or not np.isfinite(arr).all():
        raise ValueError(name + " must contain finite real numeric values")
    out = np.asarray(arr, dtype=np.float64)
    if not np.isfinite(out).all():
        raise ValueError(name + " cannot be represented as finite binary64")
    return out


def _immutable(values):
    arr = np.asarray(values, dtype=np.float64)
    return np.frombuffer(arr.tobytes(), dtype=np.float64).reshape(arr.shape)


def sigma_m2(energy_eV):
    """Native ground-H integrated cross section; zero for 0<=E<=I.

    Return shape follows the input. No event occurs at threshold. Negative
    kinetic energies and non-real/non-finite inputs are rejected.
    """
    energy = _real(energy_eV, "energy_eV")
    if np.any(energy < 0):
        raise ValueError("kinetic energy cannot be negative")
    active = energy > I_EV
    ratio = np.zeros_like(energy)
    np.divide(I_EV, energy, out=ratio, where=active)
    # This algebra avoids squaring arbitrarily large E.
    excess_fraction = np.zeros_like(energy)
    np.divide(energy - I_EV, energy, out=excess_fraction, where=active)
    out = 4.0 * math.pi * A0_M**2 * ratio * excess_fraction
    return _immutable(out)


def transfer_u(energy_eV, u):
    """Quantile Upsilon(E,u) in eV; 0<=u<=1 and E>=I.

    The positive distribution at E>I integrates to one event. At E=I this
    function returns the continuous degenerate limit I, while sigma=0; it
    does not assert a nonzero event or a regular density there.
    """
    energy, q = np.broadcast_arrays(_real(energy_eV, "energy_eV"), _real(u, "u"))
    if np.any(energy < I_EV) or np.any(q < 0) or np.any(q > 1):
        raise ValueError("quantile requires E>=I and 0<=u<=1")
    # Equivalent to IE/[E-u(E-I)] but accurate at u=1, E>>I.
    denominator = (1.0 - q) + q * (I_EV / energy)
    out = I_EV / denominator
    return _immutable(out)


def transfer_pdf_per_eV(energy_eV, upsilon_eV):
    """Conditional labelled energy-transfer density p(Upsilon|E) [1/eV].

    p=IE/[(E-I)Upsilon²] on I<=Upsilon<=E. E>I is mandatory;
    zero-event threshold and below-threshold conditions have no such density.
    """
    energy, transfer = np.broadcast_arrays(
        _real(energy_eV, "energy_eV"), _real(upsilon_eV, "upsilon_eV"))
    if np.any(energy <= I_EV):
        raise ValueError("conditional density requires positive-event E>I")
    support = (transfer >= I_EV) & (transfer <= energy)
    safe = np.where(support, transfer, I_EV)
    out = (I_EV / safe) * (energy / (energy - I_EV)) / safe
    return _immutable(np.where(support, out, 0.0))


def sdcs_m2_per_eV(energy_eV, upsilon_eV):
    """Eq.85 d sigma/d Upsilon [m²/eV], full event-law support.

    Outside I<=Upsilon<=E or at/below zero-event threshold return zero.
    The integration measure is dUpsilon (not d log Upsilon).
    """
    energy, transfer = np.broadcast_arrays(
        _real(energy_eV, "energy_eV"), _real(upsilon_eV, "upsilon_eV"))
    if np.any(energy < 0):
        raise ValueError("kinetic energy cannot be negative")
    support = (energy > I_EV) & (transfer >= I_EV) & (transfer <= energy)
    safe_e = np.where(support, energy, I_EV)
    safe_u = np.where(support, transfer, I_EV)
    out = 4.0 * math.pi * A0_M**2 * (I_EV / safe_u)**2 / safe_e
    return _immutable(np.where(support, out, 0.0))


def tdcs_m2_per_eV_sr2(energy_eV, upsilon_eV):
    """Eq85 times the §III.E constant angular density 1/(16pi²)."""
    return _immutable(sdcs_m2_per_eV(energy_eV, upsilon_eV) / (16.0 * math.pi**2))


@dataclass(frozen=True)
class LCEvaluation:
    temperature_K: np.ndarray
    moments_SI: np.ndarray
    log_moments_SI: np.ndarray
    kappa2_m3_s: np.ndarray
    conditional_mean_energy_J: np.ndarray
    identity: str = MODEL_IDENTITY
    model_scope: str = MODEL_SCOPE
    energy_mapping: str = ENERGY_MAPPING
    reduced_mass_kg: float = ME_KG
    threshold_eV: float = I_EV
    source_pdf_sha256: str = SOURCE_PDF_SHA256
    finite_source_partial: bool = False
    physical_angular_calibration: bool = False

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

    @property
    def kappa2(self):
        return self.kappa2_m3_s

    @property
    def mean_energy_J(self):
        return self.conditional_mean_energy_J


@dataclass(frozen=True)
class LCModel:
    """Immutable model with no adjustable hidden physical parameters.

    evaluate accepts a scalar or nonempty real 1-D T array and always returns
    N temperatures and an (N,4) moment array. Arrays have immutable byte-backed
    storage. No computations run on import.
    """
    identity: str = field(default=MODEL_IDENTITY, init=False)
    temperature_domain_K: tuple = field(default=TEMPERATURE_DOMAIN_K, init=False)
    model_scope: str = field(default=MODEL_SCOPE, init=False)

    def evaluate(self, temperature_K):
        temperature = _real(temperature_K, "temperature_K")
        if temperature.ndim > 1 or temperature.size == 0:
            raise ValueError("temperature_K must be a scalar or nonempty 1-D array")
        temperature = np.atleast_1d(temperature)
        low, high = self.temperature_domain_K
        if np.any(temperature < low) or np.any(temperature > high):
            raise ValueError("temperature lies outside the numerical [2000,200000] K contract")
        theta = KB_J_K * temperature
        x = I_J / theta
        # S=4pi a0² I is the cross-section numerator's energy constant.
        prefactor = math.sqrt(8.0 / (math.pi * ME_KG)) * (4.0 * math.pi * A0_M**2 * I_J)
        common = prefactor * theta**(-1.5)
        decay = np.exp(-x)
        alpha = common * theta * expn(2, x)
        beta = common * theta**2 * decay
        gamma = beta * (I_J + 2.0 * theta)
        delta = beta * (I_J**2 + 4.0 * I_J * theta + 6.0 * theta**2)
        moments = np.column_stack((alpha, beta, gamma, delta))
        if not np.isfinite(moments).all() or np.any(moments <= 0):
            raise FloatingPointError("positive native model moments were not representable")
        if np.any(moments < np.finfo(np.float64).tiny):
            raise FloatingPointError("subnormal model moments are outside this numerical contract")
        return LCEvaluation(
            temperature_K=_immutable(temperature),
            moments_SI=_immutable(moments),
            log_moments_SI=_immutable(np.log(moments)),
            kappa2_m3_s=_immutable(4.0 * gamma / (15.0 * theta**2)),
            conditional_mean_energy_J=_immutable(beta / alpha),
        )
