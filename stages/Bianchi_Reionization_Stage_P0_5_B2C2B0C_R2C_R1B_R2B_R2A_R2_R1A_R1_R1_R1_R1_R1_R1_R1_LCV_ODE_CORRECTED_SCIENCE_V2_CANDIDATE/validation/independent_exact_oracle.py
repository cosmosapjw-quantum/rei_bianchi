"""Independent integer-ratio replay of exact point-system certificates.

This module intentionally imports no candidate analysis helper.  Arithmetic is
performed on normalized integer pairs and binary64 endpoints are decoded with
``as_integer_ratio``.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import itertools
import json
import math
from math import gcd


@dataclass(frozen=True)
class IndependentVerdict:
    passed: bool
    failures: tuple[str, ...]


def _normal(numerator: int, denominator: int):
    if denominator == 0:
        raise ZeroDivisionError
    if denominator < 0:
        numerator, denominator = -numerator, -denominator
    divisor = gcd(abs(numerator), denominator)
    return numerator // divisor, denominator // divisor


def _add(a, b):
    return _normal(a[0] * b[1] + b[0] * a[1], a[1] * b[1])


def _sub(a, b):
    return _normal(a[0] * b[1] - b[0] * a[1], a[1] * b[1])


def _mul(a, b):
    return _normal(a[0] * b[0], a[1] * b[1])


def _pair(value):
    if isinstance(value, bool):
        raise TypeError
    if isinstance(value, int):
        return value, 1
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ArithmeticError
        return _normal(*value.as_integer_ratio())
    exact = getattr(value, "value", None)
    if exact is not None and hasattr(exact, "numerator") and hasattr(exact, "denominator"):
        return _normal(int(exact.numerator), int(exact.denominator))
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        return _normal(int(value.numerator), int(value.denominator))
    raise TypeError


def _matrix(values):
    return [[_pair(item) for item in row] for row in values]


def _vector(values):
    return [_pair(item) for item in values]


def _digest(matrix, rhs):
    payload = {
        "A": [[list(item) for item in row] for row in matrix],
        "b": [list(item) for item in rhs],
        "dimension": len(matrix),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _permutation_sign(permutation):
    inversions = sum(
        permutation[left] > permutation[right]
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
    )
    return -1 if inversions % 2 else 1


def _determinant(matrix):
    size = len(matrix)
    total = (0, 1)
    for permutation in itertools.permutations(range(size)):
        term = (1, 1)
        for row, column in enumerate(permutation):
            term = _mul(term, matrix[row][column])
        if _permutation_sign(permutation) < 0:
            term = (-term[0], term[1])
        total = _add(total, term)
    return total


def _status_value(status):
    return str(getattr(status, "value", status))


def verify_point_certificate(A_lower, A_upper, b_lower, b_upper, certificate) -> IndependentVerdict:
    failures = []
    try:
        lower = _matrix(A_lower)
        upper = _matrix(A_upper)
        rhs_lower = _vector(b_lower)
        rhs_upper = _vector(b_upper)
    except (TypeError, ArithmeticError, ZeroDivisionError):
        return IndependentVerdict(False, ("oracle input is malformed",))
    if lower != upper or rhs_lower != rhs_upper:
        failures.append("oracle input is not a point system")
    if _status_value(certificate.status) != "CERTIFIED_UNIQUE_POINT":
        failures.append("certificate status is not exact unique-point success")
    size = len(lower)
    if size not in (1, 2, 3) or any(len(row) != size for row in lower) or len(rhs_lower) != size:
        failures.append("oracle dimension is unsupported")
        return IndependentVerdict(False, tuple(failures))
    expected_digest = _digest(lower, rhs_lower)
    if certificate.canonical_input_digest != expected_digest:
        failures.append("canonical input digest mismatch")
    determinant = _determinant(lower)
    if determinant == (0, 1):
        failures.append("exact determinant is zero")
    try:
        reported_det = _normal(*certificate.determinant)
    except (TypeError, ZeroDivisionError):
        reported_det = None
    if reported_det != determinant:
        failures.append("determinant witness mismatch")
    try:
        solution = tuple(_normal(*item) for item in certificate.solution_exact)
    except (TypeError, ZeroDivisionError):
        solution = ()
        failures.append("exact solution witness is malformed")
    if len(solution) == size:
        residual_nonzero = False
        for row in range(size):
            total = (0, 1)
            for column in range(size):
                total = _add(total, _mul(lower[row][column], solution[column]))
            residual_nonzero |= _sub(total, rhs_lower[row]) != (0, 1)
        if residual_nonzero:
            failures.append("exact residual is nonzero")
        bounds = certificate.solution_binary64
        if bounds is None or len(bounds) != size:
            failures.append("binary64 enclosure witness is malformed")
        else:
            for exact, interval in zip(solution, bounds):
                if not (math.isfinite(interval.lo) and math.isfinite(interval.hi)):
                    failures.append("binary64 enclosure is nonfinite")
                    continue
                lo = _normal(*interval.lo.as_integer_ratio())
                hi = _normal(*interval.hi.as_integer_ratio())
                if _sub(exact, lo)[0] < 0 or _sub(hi, exact)[0] < 0:
                    failures.append("binary64 enclosure excludes exact solution")
    return IndependentVerdict(not failures, tuple(failures))


__all__ = ["IndependentVerdict", "verify_point_certificate"]
