"""Exact supplied caloric slice, conditional uncertainty transport only.

Energy ordinates and targets are in J per the same declared reference volume;
temperatures are K. This module neither supplies a physical EOS nor activates
the actual REI recipient.
"""
from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any


def exact(value: Any) -> Fraction:
    """Decode only exact representations; binary floats are never accepted."""
    if type(value) is Fraction:
        return value
    if type(value) is int:
        return Fraction(value)
    if type(value) is dict and set(value) == {"num", "den"}:
        a, b = value["num"], value["den"]
        if type(a) is str and a.lstrip("-").isdigit() and a not in ("", "-"):
            a = int(a)
        if type(b) is str and b.isdigit() and b:
            b = int(b)
        if type(a) is not int or type(b) is not int or b <= 0:
            raise ValueError("invalid numerator/positive denominator record")
        return Fraction(a, b)
    raise TypeError("Fraction, integer, or explicit num/den record required")


def wire(value: Fraction) -> dict[str, str]:
    return {"num": str(value.numerator), "den": str(value.denominator)}


def _required_label(value: Any, name: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(name + " must identify supplied provenance/convention")
    return value


@dataclass(frozen=True)
class CaloricBranch:
    knots: tuple[tuple[Fraction, Fraction], ...]
    reference_volume_id: str
    energy_store_id: str
    provenance: str
    slopes: tuple[Fraction, ...] = field(init=False)
    m0: Fraction = field(init=False)
    temperatures: tuple[Fraction, ...] = field(init=False)
    energies: tuple[Fraction, ...] = field(init=False)

    def __post_init__(self) -> None:
        _required_label(self.reference_volume_id, "reference_volume_id")
        _required_label(self.energy_store_id, "energy_store_id")
        _required_label(self.provenance, "provenance")
        if type(self.knots) not in (tuple, list) or len(self.knots) < 2:
            raise ValueError("at least two supplied knots required")
        rows = []
        for pair in self.knots:
            if type(pair) not in (tuple, list) or len(pair) != 2:
                raise ValueError("each knot must be a temperature/energy pair")
            rows.append((exact(pair[0]), exact(pair[1])))
        ts, es = tuple(x[0] for x in rows), tuple(x[1] for x in rows)
        if ts[0] <= 0 or any(y <= x for x, y in zip(ts, ts[1:])):
            raise ValueError("positive strictly increasing temperatures required")
        if any(y <= x for x, y in zip(es, es[1:])):
            raise ValueError("strictly increasing energy ordinates required")
        slopes = tuple((b-a)/(tb-ta) for (ta, a), (tb, b) in zip(rows, rows[1:]))
        object.__setattr__(self, "knots", tuple(rows))
        object.__setattr__(self, "temperatures", ts)
        object.__setattr__(self, "energies", es)
        object.__setattr__(self, "slopes", slopes)
        object.__setattr__(self, "m0", min(slopes))

    def evaluate(self, temperature: Any) -> Fraction:
        t = exact(temperature)
        if t < self.temperatures[0] or t > self.temperatures[-1]:
            raise ValueError("temperature outside supplied branch")
        i = min(bisect_left(self.temperatures, t), len(self.slopes)-1)
        if i and self.temperatures[i] > t:
            i -= 1
        return self.energies[i] + self.slopes[i]*(t-self.temperatures[i])

    def inverse(self, energy: Any) -> Fraction:
        u = exact(energy)
        if u < self.energies[0] or u > self.energies[-1]:
            raise ValueError("energy outside supplied branch image")
        i = min(bisect_left(self.energies, u), len(self.slopes)-1)
        if i and self.energies[i] > u:
            i -= 1
        return self.temperatures[i] + (u-self.energies[i])/self.slopes[i]

    def enclose_energy(self, Elo: Any, Ehi: Any, eta: Any | None) -> tuple[Fraction, Fraction] | None:
        lo, hi = exact(Elo), exact(Ehi)
        if lo > hi:
            raise ValueError("reversed energy interval")
        if eta is None:
            return None
        radius = exact(eta)
        if radius < 0:
            raise ValueError("eta must be nonnegative")
        return self.inverse(lo-radius), self.inverse(hi+radius)

    def residual_radius(self, Tbar: Any, Ebar: Any, eE: Any | None, eta: Any | None) -> Fraction | None:
        t, center = exact(Tbar), exact(Ebar)
        model_at_t = self.evaluate(t)
        energy_radius = None if eE is None else exact(eE)
        eos_radius = None if eta is None else exact(eta)
        if (energy_radius is not None and energy_radius < 0) or (eos_radius is not None and eos_radius < 0):
            raise ValueError("eE and eta must be nonnegative")
        if eE is None or eta is None:
            return None
        return (abs(model_at_t-center)+energy_radius+eos_radius)/self.m0
