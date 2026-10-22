"""Scalar radiative-recombination fit and conditional kinetic moment.

The source label identifies the recombined product, not the incident ion.
ElementalElectronicEquality reuses each rate for H1/D/T, He3/He4, Li6/Li7;
isotope-specific spectroscopy is unresolved. The moment is a derivative of a
fitted rate, without an empirical moment-accuracy bound.
"""

import json
import math
from pathlib import Path


K_B_J_K = 1.380649e-23  # SI definition
CM3_TO_M3 = 1e-6
STATUS = "CONDITIONAL_DERIVATIVE_OF_FIT"
ELEMENTAL_ELECTRONIC_EQUALITY = {
    "H I": ("H1", "D", "T"),
    "HeI a": ("He3", "He4"),
    "HeII": ("He3", "He4"),
    "LiI": ("Li6", "Li7"),
    "LiII": ("Li6", "Li7"),
    "LiIII": ("Li6", "Li7"),
}

_DATA = json.loads(Path(__file__).with_name("rr_rows.json").read_text())
_ROWS = {row[0]: row for row in _DATA["rows"]}
CHANNELS = tuple(_ROWS)


def _finite(value, name):
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite real number") from exc
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite real number")
    return value


def rr_rate(channel, T_K, chi_J=None):
    """Return alpha, its log-temperature slope, and electron kinetic loss.

    Coefficients multiply ne [m^-3] times ni [m^-3] to obtain J m^-3 s^-1.
    Optional chi_J supplies a separate completed-cascade energy ledger.
    The caller handles the temperature's particle-number term.
    """
    if channel not in _ROWS:
        raise ValueError(f"unknown RR channel: {channel!r}")
    T_K = _finite(T_K, "T_K")
    if not 100.0 <= T_K <= 10000.0:
        raise ValueError("T_K outside inclusive [100, 10000] K")
    if chi_J is not None:
        chi_J = _finite(chi_J, "chi_J")
        if chi_J < 0:
            raise ValueError("chi_J must be nonnegative")

    _, Z, bound_electrons, a, b, T0, T1 = _ROWS[channel]
    x = math.sqrt(T_K / T0)
    y = math.sqrt(T_K / T1)
    alpha_cm3_s = a / (x * (1 + x) ** (1 - b) * (1 + y) ** (1 + b))
    slope = -0.5 - (1 - b) * x / (2 * (1 + x)) - (1 + b) * y / (2 * (1 + y))
    factor = 1.5 + slope
    alpha_m3_s = CM3_TO_M3 * alpha_cm3_s
    lambda_J_m3_s = K_B_J_K * T_K * alpha_m3_s * factor
    if not all(math.isfinite(v) for v in (alpha_m3_s, slope, factor, lambda_J_m3_s)):
        raise ValueError("nonfinite RR fit or moment")
    if lambda_J_m3_s < 0:
        raise ValueError("negative kinetic moment from RR fit")
    result = {
        "channel": channel,
        "input_charge": Z - bound_electrons + 1,
        "output_charge": Z - bound_electrons,
        "alpha_m3_s": alpha_m3_s,
        "d_ln_alpha_d_ln_T": slope,
        "kinetic_factor": factor,
        "lambda_J_m3_s": lambda_J_m3_s,
        "status": STATUS,
    }
    if chi_J is not None:
        binding = chi_J * alpha_m3_s
        cascade = lambda_J_m3_s + binding
        if not math.isfinite(cascade):
            raise ValueError("nonfinite completed-cascade coefficient")
        result["coefficient_ledger_J_m3_s"] = {
            "thermal": -lambda_J_m3_s,
            "binding": -binding,
            "completed_cascade": cascade,
        }
    return result
