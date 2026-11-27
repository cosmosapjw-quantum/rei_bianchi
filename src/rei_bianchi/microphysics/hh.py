"""Ground-state D/H charge exchange in proper cgs units.

Savin (2002), ApJ 566, 599, Table 1, DOI 10.1086/324218.
Use WU R51's log(T)–log(rate) interpolation and qualified 2.7–200,000 K
domain. The forward reaction D I + H II -> D II + H I is endothermic.
"""

from __future__ import annotations

from bisect import bisect_left
import csv
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
import math


EV_TO_ERG = 1.602176634e-12
CX_THRESHOLD_EV = 0.0037
VALID_T_K = (2.7, 200_000.0)


@lru_cache(maxsize=1)
def _table() -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
    resource = files(__package__).joinpath("data", "savin2002_charge_exchange.csv")
    with resource.open(encoding="ascii", newline="") as stream:
        rows = [
            (float(r["T_K"]), float(r["k_forward_cm3_s"]), float(r["k_reverse_cm3_s"]))
            for r in csv.DictReader(stream)
        ]
    if len(rows) != 47 or rows[0][0] != 1 or rows[-1][0] != VALID_T_K[1]:
        raise ValueError("Savin Table 1 is incomplete")
    if any(b[0] <= a[0] for a, b in zip(rows, rows[1:])) or any(
        not math.isfinite(v) or v <= 0 for row in rows for v in row
    ):
        raise ValueError("Invalid Savin Table 1 values")
    t, kf, kr = zip(*rows)
    return t, kf, kr


def savin_rates(T_K: float) -> tuple[float, float]:
    """Return forward and reverse thermal rates in cm³/s at gas temperature T_K."""
    if not math.isfinite(T_K) or not VALID_T_K[0] <= T_K <= VALID_T_K[1]:
        raise ValueError("Savin rates require 2.7 <= T_K <= 200000 K")
    ts, forward, reverse = _table()
    j = bisect_left(ts, T_K)
    if ts[j] == T_K:
        return forward[j], reverse[j]
    i = j - 1
    fraction = math.log(T_K / ts[i]) / math.log(ts[j] / ts[i])
    return tuple(
        math.exp((1.0 - fraction) * math.log(k[i]) + fraction * math.log(k[j]))
        for k in (forward, reverse)
    )


@dataclass(frozen=True)
class ChargeExchangeSource:
    """A single net reaction extent per proper volume and proper second."""

    net_events_cm3_s: float

    @property
    def hi_rate_cm3_s(self) -> float:
        return self.net_events_cm3_s

    @property
    def di_rate_cm3_s(self) -> float:
        return -self.net_events_cm3_s

    @property
    def photon_rate_cm3_s(self) -> float:
        return 0.0

    @property
    def hii_rate_cm3_s(self) -> float:
        return -self.net_events_cm3_s

    @property
    def dii_rate_cm3_s(self) -> float:
        return self.net_events_cm3_s

    @property
    def electron_rate_cm3_s(self) -> float:
        return 0.0

    @property
    def gas_power_erg_cm3_s(self) -> float:
        return -(CX_THRESHOLD_EV * EV_TO_ERG) * self.net_events_cm3_s

    @property
    def binding_power_erg_cm3_s(self) -> float:
        return -self.gas_power_erg_cm3_s


def charge_exchange_source(
    T_K: float, n_HI_cm3: float, n_HII_cm3: float, n_DI_cm3: float, n_DII_cm3: float
) -> ChargeExchangeSource:
    """Evaluate ground-state forward minus reverse extent and energy transfer."""
    densities = (n_HI_cm3, n_HII_cm3, n_DI_cm3, n_DII_cm3)
    if any(not math.isfinite(v) or v < 0 for v in densities):
        raise ValueError("Charge exchange requires finite nonnegative proper densities")
    kf, kr = savin_rates(T_K)
    extent = (kf * n_HII_cm3) * n_DI_cm3 - (kr * n_HI_cm3) * n_DII_cm3
    if not math.isfinite(extent) or not math.isfinite(
        extent * (CX_THRESHOLD_EV * EV_TO_ERG)
    ):
        raise ValueError("Nonfinite charge-exchange source")
    return ChargeExchangeSource(extent)


def trace_step(
    y: float, dt_s: float, T_K: float, n_H_cm3: float, x_HII: float
) -> float:
    """Propagate a trace D II fraction for constant H density, ion fraction and T."""
    if not (0 <= y <= 1 and 0 <= x_HII <= 1):
        raise ValueError("Element fractions must lie in [0,1]")
    if any(not math.isfinite(v) or v < 0 for v in (dt_s, n_H_cm3)):
        raise ValueError("Duration and density must be finite and nonnegative")
    kf, kr = savin_rates(T_K)
    a = kf * x_HII
    b = kr * (1.0 - x_HII)
    equilibrium = a / (a + b)
    relaxation = (n_H_cm3 * (a + b)) * dt_s
    return math.fsum(
        (y * math.exp(-relaxation), equilibrium * (-math.expm1(-relaxation)))
    )
