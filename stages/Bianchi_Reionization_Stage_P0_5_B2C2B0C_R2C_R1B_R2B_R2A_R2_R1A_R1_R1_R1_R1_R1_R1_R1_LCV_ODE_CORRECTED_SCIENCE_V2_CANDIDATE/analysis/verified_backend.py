"""Exact algebraic shadow backend for the LCV-ODE successor stage.

Only finite rational algebra is implemented.  Transcendental functions are
deliberately unavailable until a separately qualified outward-rounded backend
is bound to the numerical ABI.  This module is reference/shadow machinery, not
a production ODE arithmetic backend.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
import math
import sys
from typing import Generic, Iterable, TypeVar


MAX_EXACT_BITS = 16_384
MAX_SUM_TERMS = 4_096


class ExactProvenance(StrEnum):
    BINARY64 = "BINARY64"
    DECIMAL_TEXT = "DECIMAL_TEXT"
    INTEGER_RATIO = "INTEGER_RATIO"


class NumericStatus(StrEnum):
    OK = "OK"
    NONFINITE_INPUT = "NONFINITE_INPUT"
    INVALID_DECIMAL = "INVALID_DECIMAL"
    INVALID_RATIO = "INVALID_RATIO"
    INVALID_INTERVAL = "INVALID_INTERVAL"
    DIVISOR_CONTAINS_ZERO = "DIVISOR_CONTAINS_ZERO"
    BINARY64_OVERFLOW = "BINARY64_OVERFLOW"
    EXACT_RESOURCE_LIMIT = "EXACT_RESOURCE_LIMIT"
    UNSUPPORTED_TRANSCENDENTAL = "UNSUPPORTED_TRANSCENDENTAL"
    UNSUPPORTED_OPERATION = "UNSUPPORTED_OPERATION"


T = TypeVar("T")


@dataclass(frozen=True)
class NumericOutcome(Generic[T]):
    status: NumericStatus
    value: T | None
    operation: str
    detail: str = ""


@dataclass(frozen=True)
class ExactScalar:
    value: Fraction
    provenance: ExactProvenance


@dataclass(frozen=True)
class ExactInterval:
    lo: Fraction
    hi: Fraction

    def __post_init__(self) -> None:
        if self.lo > self.hi:
            raise ValueError("exact interval lower endpoint exceeds upper endpoint")


@dataclass(frozen=True)
class Binary64Interval:
    lo: float
    hi: float

    def __post_init__(self) -> None:
        if not (math.isfinite(self.lo) and math.isfinite(self.hi)):
            raise ValueError("binary64 enclosure endpoints must be finite")
        if self.lo > self.hi:
            raise ValueError("binary64 lower endpoint exceeds upper endpoint")


@dataclass(frozen=True)
class ExactBinary64Value:
    exact: Fraction
    binary64: Binary64Interval


_MAX_BINARY64 = Fraction.from_float(sys.float_info.max)


def fraction_within_resource(value: Fraction) -> bool:
    """Return whether an exact scalar stays inside the fixed limb ceiling."""

    return (
        abs(value.numerator).bit_length() <= MAX_EXACT_BITS
        and value.denominator.bit_length() <= MAX_EXACT_BITS
    )


def _resource_outcome(operation: str) -> NumericOutcome:
    return NumericOutcome(
        NumericStatus.EXACT_RESOURCE_LIMIT,
        None,
        operation,
        f"exact numerator/denominator exceeds {MAX_EXACT_BITS} bits",
    )


def exact_scalar_from_binary64(value: float) -> NumericOutcome[ExactScalar]:
    operation = "from_binary64"
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return NumericOutcome(NumericStatus.NONFINITE_INPUT, None, operation, "not a binary64 scalar")
    if not math.isfinite(number):
        return NumericOutcome(NumericStatus.NONFINITE_INPUT, None, operation, "binary64 input is not finite")
    exact = Fraction.from_float(number)
    if not fraction_within_resource(exact):
        return _resource_outcome(operation)
    return NumericOutcome(
        NumericStatus.OK,
        ExactScalar(exact, ExactProvenance.BINARY64),
        operation,
    )


def exact_scalar_from_decimal_text(text: str) -> NumericOutcome[ExactScalar]:
    operation = "from_decimal_text"
    if not isinstance(text, str):
        return NumericOutcome(NumericStatus.INVALID_DECIMAL, None, operation, "decimal input must be text")
    try:
        exact = Fraction(text)
    except (ValueError, ZeroDivisionError):
        return NumericOutcome(NumericStatus.INVALID_DECIMAL, None, operation, "invalid finite decimal text")
    if not fraction_within_resource(exact):
        return _resource_outcome(operation)
    return NumericOutcome(
        NumericStatus.OK,
        ExactScalar(exact, ExactProvenance.DECIMAL_TEXT),
        operation,
    )


def exact_scalar_from_ratio(numerator: int, denominator: int = 1) -> NumericOutcome[ExactScalar]:
    operation = "from_integer_ratio"
    if isinstance(numerator, bool) or isinstance(denominator, bool):
        return NumericOutcome(NumericStatus.INVALID_RATIO, None, operation, "boolean is not an integer-ratio scalar")
    if not isinstance(numerator, int) or not isinstance(denominator, int) or denominator == 0:
        return NumericOutcome(NumericStatus.INVALID_RATIO, None, operation, "ratio requires integers and nonzero denominator")
    exact = Fraction(numerator, denominator)
    if not fraction_within_resource(exact):
        return _resource_outcome(operation)
    return NumericOutcome(
        NumericStatus.OK,
        ExactScalar(exact, ExactProvenance.INTEGER_RATIO),
        operation,
    )


def outward_binary64(value: Fraction) -> NumericOutcome[Binary64Interval]:
    operation = "outward_binary64"
    if not isinstance(value, Fraction):
        return NumericOutcome(NumericStatus.INVALID_RATIO, None, operation, "value must be Fraction")
    if not fraction_within_resource(value):
        return _resource_outcome(operation)
    if value < -_MAX_BINARY64 or value > _MAX_BINARY64:
        return NumericOutcome(
            NumericStatus.BINARY64_OVERFLOW,
            None,
            operation,
            "exact finite value is outside finite binary64 range",
        )
    nearest = float(value)
    represented = Fraction.from_float(nearest)
    if represented < value:
        lower = nearest
        upper = math.nextafter(nearest, math.inf)
    elif represented > value:
        lower = math.nextafter(nearest, -math.inf)
        upper = nearest
    else:
        lower = upper = nearest
    if not (math.isfinite(lower) and math.isfinite(upper)):
        return NumericOutcome(
            NumericStatus.BINARY64_OVERFLOW,
            None,
            operation,
            "outward endpoint is not finite",
        )
    return NumericOutcome(NumericStatus.OK, Binary64Interval(lower, upper), operation)


def outward_binary64_interval(value: ExactInterval) -> NumericOutcome[Binary64Interval]:
    operation = "outward_binary64_interval"
    lower = outward_binary64(value.lo)
    if lower.status is not NumericStatus.OK:
        return NumericOutcome(lower.status, None, operation, lower.detail)
    upper = outward_binary64(value.hi)
    if upper.status is not NumericStatus.OK:
        return NumericOutcome(upper.status, None, operation, upper.detail)
    return NumericOutcome(
        NumericStatus.OK,
        Binary64Interval(lower.value.lo, upper.value.hi),
        operation,
    )


def _interval_result(operation: str, lo: Fraction, hi: Fraction) -> NumericOutcome[ExactInterval]:
    if not (fraction_within_resource(lo) and fraction_within_resource(hi)):
        return _resource_outcome(operation)
    return NumericOutcome(NumericStatus.OK, ExactInterval(lo, hi), operation)


def exact_add(a: ExactInterval, b: ExactInterval) -> NumericOutcome[ExactInterval]:
    return _interval_result("add", a.lo + b.lo, a.hi + b.hi)


def exact_sub(a: ExactInterval, b: ExactInterval) -> NumericOutcome[ExactInterval]:
    return _interval_result("sub", a.lo - b.hi, a.hi - b.lo)


def exact_mul(a: ExactInterval, b: ExactInterval) -> NumericOutcome[ExactInterval]:
    products = (a.lo * b.lo, a.lo * b.hi, a.hi * b.lo, a.hi * b.hi)
    return _interval_result("mul", min(products), max(products))


def exact_div(a: ExactInterval, b: ExactInterval) -> NumericOutcome[ExactInterval]:
    operation = "div"
    if b.lo <= 0 <= b.hi:
        return NumericOutcome(
            NumericStatus.DIVISOR_CONTAINS_ZERO,
            None,
            operation,
            "exact divisor interval contains zero",
        )
    reciprocal = ExactInterval(min(Fraction(1, 1) / b.lo, Fraction(1, 1) / b.hi), max(Fraction(1, 1) / b.lo, Fraction(1, 1) / b.hi))
    result = exact_mul(a, reciprocal)
    return NumericOutcome(result.status, result.value, operation, result.detail)


def exact_integer_power(a: ExactInterval, exponent: int) -> NumericOutcome[ExactInterval]:
    operation = "integer_power"
    if isinstance(exponent, bool) or not isinstance(exponent, int):
        return NumericOutcome(NumericStatus.UNSUPPORTED_OPERATION, None, operation, "exponent must be integer")
    if exponent == 0:
        return _interval_result(operation, Fraction(1), Fraction(1))
    if exponent < 0:
        reciprocal = exact_div(ExactInterval(Fraction(1), Fraction(1)), a)
        if reciprocal.status is not NumericStatus.OK:
            return NumericOutcome(reciprocal.status, None, operation, reciprocal.detail)
        return exact_integer_power(reciprocal.value, -exponent)
    endpoints = (a.lo**exponent, a.hi**exponent)
    if exponent % 2 == 0 and a.lo <= 0 <= a.hi:
        lo, hi = Fraction(0), max(endpoints)
    else:
        lo, hi = min(endpoints), max(endpoints)
    return _interval_result(operation, lo, hi)


def exact_sum_binary64(values: Iterable[float]) -> NumericOutcome[ExactBinary64Value]:
    operation = "sum_binary64"
    try:
        iterator = iter(values)
    except TypeError:
        return NumericOutcome(NumericStatus.NONFINITE_INPUT, None, operation, "values must be iterable")
    exact = Fraction(0)
    for index, value in enumerate(iterator):
        if index >= MAX_SUM_TERMS:
            return NumericOutcome(
                NumericStatus.EXACT_RESOURCE_LIMIT,
                None,
                operation,
                f"term count exceeds {MAX_SUM_TERMS}",
            )
        converted = exact_scalar_from_binary64(value)
        if converted.status is not NumericStatus.OK:
            return NumericOutcome(converted.status, None, operation, converted.detail)
        exact += converted.value.value
        if not fraction_within_resource(exact):
            return _resource_outcome(operation)
    enclosure = outward_binary64(exact)
    if enclosure.status is not NumericStatus.OK:
        return NumericOutcome(enclosure.status, None, operation, enclosure.detail)
    return NumericOutcome(
        NumericStatus.OK,
        ExactBinary64Value(exact, enclosure.value),
        operation,
    )


def outward_elementary(name: str, value: ExactInterval) -> NumericOutcome[ExactInterval]:
    operation = f"elementary:{name}"
    normalized = str(name).lower()
    if normalized == "log" and value.lo <= 0:
        return NumericOutcome(NumericStatus.INVALID_INTERVAL, None, operation, "log domain is not strictly positive")
    if normalized == "sqrt" and value.lo < 0:
        return NumericOutcome(NumericStatus.INVALID_INTERVAL, None, operation, "sqrt domain is negative")
    if normalized in {"exp", "log", "sqrt", "pow_noninteger"}:
        return NumericOutcome(
            NumericStatus.UNSUPPORTED_TRANSCENDENTAL,
            None,
            operation,
            "no qualified outward transcendental backend is bound",
        )
    return NumericOutcome(NumericStatus.UNSUPPORTED_OPERATION, None, operation, "unknown elementary operation")


__all__ = [
    "Binary64Interval",
    "ExactBinary64Value",
    "ExactInterval",
    "ExactProvenance",
    "ExactScalar",
    "MAX_EXACT_BITS",
    "MAX_SUM_TERMS",
    "NumericOutcome",
    "NumericStatus",
    "exact_add",
    "exact_div",
    "exact_integer_power",
    "exact_mul",
    "exact_scalar_from_binary64",
    "exact_scalar_from_decimal_text",
    "exact_scalar_from_ratio",
    "exact_sub",
    "exact_sum_binary64",
    "fraction_within_resource",
    "outward_binary64",
    "outward_binary64_interval",
    "outward_elementary",
]
