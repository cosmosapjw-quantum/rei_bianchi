"""Exact affine postprocessing of finite stored reference candidates.

This is range analysis of supplied numbers, not a validated ODE integrator.
References with the same key are one variable. Merge their coefficients before
projection. Every binary64 input is converted individually, before subtraction.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from collections.abc import Mapping


def exact(value):
    """Interpret an int/Fraction exactly and a finite float as its stored value."""
    if type(value) is bool:
        raise TypeError("Boolean is not a numerical budget input")
    if isinstance(value, Fraction):
        return value
    if type(value) is int:
        return Fraction(value)
    if type(value) is float and math.isfinite(value):
        return Fraction.from_float(value)
    raise ValueError("Budget input must be a finite int, float or Fraction")


def rational_record(value):
    q = exact(value)
    try:
        nearest = float(q)
    except OverflowError:
        nearest = None
    if nearest is not None and not math.isfinite(nearest):
        nearest = None
    return {"exact": str(q), "nearest_float": nearest}


def outward(value, direction):
    """Smallest directed binary64 rounding; no padding of exact endpoints."""
    q = exact(value)
    if direction not in (-1, 1):
        raise ValueError("direction must be -1 or 1")
    try:
        rounded = float(q)
    except OverflowError as exc:
        raise ValueError("Exact bound is outside finite binary64 display") from exc
    if not math.isfinite(rounded):
        raise ValueError("Exact bound is outside finite binary64 display")
    back = Fraction.from_float(rounded)
    if (direction < 0 and back > q) or (direction > 0 and back < q):
        rounded = math.nextafter(rounded, -math.inf if direction < 0 else math.inf)
    if not math.isfinite(rounded):
        raise ValueError("Directed bound is outside finite binary64 display")
    return rounded


@dataclass(frozen=True)
class Hull:
    lower: Fraction
    upper: Fraction
    choices: int
    kind: str

    def as_dict(self):
        if self.lower > self.upper:
            raise ValueError("Inverted hull")
        result = {"kind": self.kind, "candidate_assignments": self.choices,
                  "exact_lower": str(self.lower), "exact_upper": str(self.upper),
                  "exact_width": str(self.upper - self.lower),
                  "true_solution_error_bound": False}
        try:
            lo, hi = outward(self.lower, -1), outward(self.upper, 1)
        except ValueError:
            result.update(lower_float=None, upper_float=None,
                          display_width=None, display_status="OUTSIDE_FINITE_BINARY64")
        else:
            width = hi - lo
            result.update(lower_float=lo, upper_float=hi,
                          display_width=width if math.isfinite(width) else None,
                          display_status="OUTWARD_ENCLOSURE_OF_EXACT_STORED_CANDIDATE_RANGE")
        return result


@dataclass(frozen=True, init=False)
class LinearForm:
    constant: Fraction
    terms: tuple

    def __init__(self, constant=0, terms=()):
        merged = {}
        items = terms.items() if isinstance(terms, Mapping) else terms
        for key, coefficient in items:
            if not isinstance(key, str) or not key:
                raise ValueError("A reference key must be a nonempty string")
            merged[key] = merged.get(key, Fraction(0)) + exact(coefficient)
        object.__setattr__(self, "constant", exact(constant))
        object.__setattr__(self, "terms", tuple(sorted((k, v) for k, v in merged.items() if v)))

    @classmethod
    def reference(cls, key):
        return cls(0, ((key, 1),))

    def __add__(self, other):
        if not isinstance(other, LinearForm):
            other = LinearForm(other)
        return LinearForm(self.constant + other.constant, self.terms + other.terms)

    __radd__ = __add__

    def __neg__(self):
        return LinearForm(-self.constant, ((k, -v) for k, v in self.terms))

    def __sub__(self, other):
        return self + (-other if isinstance(other, LinearForm) else -exact(other))

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, scalar):
        q = exact(scalar)
        return LinearForm(self.constant * q, ((k, v * q) for k, v in self.terms))

    __rmul__ = __mul__

    def evaluate(self, values):
        return self.constant + sum((coef * exact(values[key]) for key, coef in self.terms), Fraction(0))

    def as_dict(self):
        return {"constant": str(self.constant),
                "coefficients": {key: str(coef) for key, coef in self.terms},
                "arithmetic": "exact_rational_of_individually_stored_binary64_inputs"}

    def _candidates(self, candidates):
        selected = {}
        for key, _ in self.terms:
            if key not in candidates or not isinstance(candidates[key], Mapping) or not candidates[key]:
                raise ValueError("Missing finite candidates for reference " + key)
            selected[key] = {}
            for method, value in candidates[key].items():
                if not isinstance(method, str) or not method:
                    raise ValueError("Candidate method label must be a nonempty string")
                selected[key][method] = exact(value)
        return selected

    def product_hull(self, candidates):
        """Tight extrema over independently labelled finite choices at each key."""
        selected = self._candidates(candidates)
        lo = hi = self.constant
        count = 1
        for key, coefficient in self.terms:
            values = selected[key].values()
            left, right = min(values), max(values)
            a, b = coefficient * left, coefficient * right
            lo += min(a, b)
            hi += max(a, b)
            count *= len(selected[key])
        return Hull(lo, hi, count, "independent_finite_candidate_product")

    def coherent_values(self, candidates):
        """One common method label across every surviving reference key."""
        selected = self._candidates(candidates)
        if not selected:
            return {"constant": self.constant}
        common = set.intersection(*(set(row) for row in selected.values()))
        if not common:
            raise ValueError("No common method label for coherent projection")
        return {method: self.evaluate({key: row[method] for key, row in selected.items()})
                for method in sorted(common)}

    def coherent_hull(self, candidates):
        values = self.coherent_values(candidates)
        return Hull(min(values.values()), max(values.values()), len(values),
                    "same_method_label_across_reference_keys")


def project(form, candidates):
    return {"linear_form": form.as_dict(),
            "coherent_method_values": {key: rational_record(value)
                                       for key, value in form.coherent_values(candidates).items()},
            "product_hull": form.product_hull(candidates).as_dict(),
            "coherent_hull": form.coherent_hull(candidates).as_dict()}
