"""Exact, independently replayable certificates for small point systems.

Non-degenerate interval systems are intentionally unsupported.  This prevents
the exact point solver from being mistaken for a verified interval Krawczyk
implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
import hashlib
import json
import math
from typing import Any

import verified_backend as vb


MAX_POINT_DIMENSION = 3


class LinearCertificateStatus(StrEnum):
    CERTIFIED_UNIQUE_POINT = "CERTIFIED_UNIQUE_POINT"
    NONFINITE_INPUT = "NONFINITE_INPUT"
    INVALID_SHAPE = "INVALID_SHAPE"
    NONPOINT_INTERVAL_UNSUPPORTED = "NONPOINT_INTERVAL_UNSUPPORTED"
    DIMENSION_UNSUPPORTED = "DIMENSION_UNSUPPORTED"
    SINGULAR = "SINGULAR"
    EXACT_RESOURCE_LIMIT = "EXACT_RESOURCE_LIMIT"
    ENCLOSURE_OVERFLOW = "ENCLOSURE_OVERFLOW"
    INTERNAL_EXACT_RESIDUAL_FAILURE = "INTERNAL_EXACT_RESIDUAL_FAILURE"


@dataclass(frozen=True)
class PointLinearCertificate:
    status: LinearCertificateStatus
    dimension: int
    determinant: tuple[int, int] | None
    solution_exact: tuple[tuple[int, int], ...] | None
    solution_binary64: tuple[vb.Binary64Interval, ...] | None
    residual_exact_zero: bool
    canonical_input_digest: str | None
    detail: str = ""


def _empty(status: LinearCertificateStatus, detail: str, dimension: int = 0, digest: str | None = None) -> PointLinearCertificate:
    return PointLinearCertificate(status, dimension, None, None, None, False, digest, detail)


def _exact(value: Any) -> Fraction:
    if isinstance(value, vb.ExactScalar):
        return value.value
    if isinstance(value, bool):
        raise TypeError("boolean is not a point-system scalar")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ArithmeticError("nonfinite binary64 point-system input")
        return Fraction.from_float(value)
    if isinstance(value, Fraction):
        return value
    raise TypeError("unsupported point-system scalar")


def _decode_matrix(value: Any) -> list[list[Fraction]]:
    if not isinstance(value, (list, tuple)):
        raise TypeError("matrix must be a sequence of rows")
    rows = []
    for row in value:
        if not isinstance(row, (list, tuple)):
            raise TypeError("matrix row must be a sequence")
        rows.append([_exact(item) for item in row])
    return rows


def _decode_vector(value: Any) -> list[Fraction]:
    if not isinstance(value, (list, tuple)):
        raise TypeError("rhs must be a sequence")
    return [_exact(item) for item in value]


def _pair(value: Fraction) -> tuple[int, int]:
    return value.numerator, value.denominator


def _canonical_digest(matrix: list[list[Fraction]], rhs: list[Fraction]) -> str:
    payload = {
        "A": [[list(_pair(item)) for item in row] for row in matrix],
        "b": [list(_pair(item)) for item in rhs],
        "dimension": len(matrix),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _solve_exact(matrix: list[list[Fraction]], rhs: list[Fraction]) -> tuple[Fraction, list[Fraction]] | None:
    size = len(matrix)
    work = [row.copy() + [rhs[index]] for index, row in enumerate(matrix)]
    determinant = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column] != 0), None)
        if pivot is None:
            return None
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = -determinant
        pivot_value = work[column][column]
        determinant *= pivot_value
        work[column] = [item / pivot_value for item in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    work[row][entry] - factor * work[column][entry]
                    for entry in range(size + 1)
                ]
        for row in work:
            if any(not vb.fraction_within_resource(item) for item in row):
                raise OverflowError("exact elimination exceeded fixed resource ceiling")
    return determinant, [work[row][-1] for row in range(size)]


def certify_point_interval_system(A_lower, A_upper, b_lower, b_upper) -> PointLinearCertificate:
    try:
        lower = _decode_matrix(A_lower)
        upper = _decode_matrix(A_upper)
        rhs_lower = _decode_vector(b_lower)
        rhs_upper = _decode_vector(b_upper)
    except ArithmeticError as exc:
        return _empty(LinearCertificateStatus.NONFINITE_INPUT, str(exc))
    except (TypeError, ValueError) as exc:
        return _empty(LinearCertificateStatus.INVALID_SHAPE, str(exc))

    size = len(lower)
    if size < 1 or size > MAX_POINT_DIMENSION:
        return _empty(
            LinearCertificateStatus.DIMENSION_UNSUPPORTED,
            f"dimension must be in [1,{MAX_POINT_DIMENSION}]",
            size,
        )
    if any(len(row) != size for row in lower) or len(upper) != size or any(len(row) != size for row in upper):
        return _empty(LinearCertificateStatus.INVALID_SHAPE, "matrix must be square", size)
    if len(rhs_lower) != size or len(rhs_upper) != size:
        return _empty(LinearCertificateStatus.INVALID_SHAPE, "rhs dimension mismatch", size)
    if lower != upper or rhs_lower != rhs_upper:
        return _empty(
            LinearCertificateStatus.NONPOINT_INTERVAL_UNSUPPORTED,
            "exact point certificate refuses non-degenerate intervals",
            size,
        )
    if any(not vb.fraction_within_resource(item) for row in lower for item in row) or any(
        not vb.fraction_within_resource(item) for item in rhs_lower
    ):
        return _empty(LinearCertificateStatus.EXACT_RESOURCE_LIMIT, "input exceeds exact resource ceiling", size)

    digest = _canonical_digest(lower, rhs_lower)
    try:
        solved = _solve_exact(lower, rhs_lower)
    except OverflowError as exc:
        return _empty(LinearCertificateStatus.EXACT_RESOURCE_LIMIT, str(exc), size, digest)
    if solved is None:
        return _empty(LinearCertificateStatus.SINGULAR, "exact determinant is zero", size, digest)
    determinant, solution = solved
    residual = [
        sum((lower[row][column] * solution[column] for column in range(size)), Fraction(0))
        - rhs_lower[row]
        for row in range(size)
    ]
    if determinant == 0 or any(item != 0 for item in residual):
        return _empty(
            LinearCertificateStatus.INTERNAL_EXACT_RESIDUAL_FAILURE,
            "exact determinant/residual success predicate failed",
            size,
            digest,
        )

    enclosures = []
    for item in solution:
        converted = vb.outward_binary64(item)
        if converted.status is vb.NumericStatus.BINARY64_OVERFLOW:
            return _empty(LinearCertificateStatus.ENCLOSURE_OVERFLOW, converted.detail, size, digest)
        if converted.status is not vb.NumericStatus.OK:
            return _empty(LinearCertificateStatus.EXACT_RESOURCE_LIMIT, converted.detail, size, digest)
        enclosures.append(converted.value)
    return PointLinearCertificate(
        LinearCertificateStatus.CERTIFIED_UNIQUE_POINT,
        size,
        _pair(determinant),
        tuple(_pair(item) for item in solution),
        tuple(enclosures),
        True,
        digest,
        "exact point solve; not an interval-system certificate",
    )


__all__ = [
    "LinearCertificateStatus",
    "MAX_POINT_DIMENSION",
    "PointLinearCertificate",
    "certify_point_interval_system",
]
