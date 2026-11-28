"""Local source-compatibility guard for a caller-supplied fixed linear lift.

For Y=L z>0, evaluate the two supplied source maps at their proper states and
form d=R_full(L z)-L R_reduced(z). The componentwise gate is explicitly

    |d_i| <= atol_i + rtol * max(|R_full_i|, |(L R_reduced)_i|).

This is a local diagnostic at one positive state, not an inferred reaction
map, a theorem over the whole state domain, a physical source provider, or an
integration/trajectory error bound. It does not make an electronic-only
isotope reduction compatible with arbitrary isotope-resolved source channels.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Callable

import numpy as np

from .reactive_moments import MomentDomainError, _muldiv, _readonly, _scalar, _sum


def _array(value, ndim, name):
    original = np.asarray(value)
    if original.ndim != ndim or original.dtype.kind not in "fiu":
        raise MomentDomainError(name + ": REAL_ARRAY_DIMENSION_REQUIRED")
    array = np.asarray(original, dtype=float)
    if not np.isfinite(array).all():
        raise MomentDomainError(name + ": FINITE_ARRAY_REQUIRED")
    return _readonly(array)


def _matvec(matrix, vector, *, label):
    return _readonly([_sum((_muldiv((float(a), float(b)), label=label)
                            for a, b in zip(row, vector)), label=label)
                      for row in matrix])


@dataclass(frozen=True, slots=True)
class SourceLiftReport:
    full_state: np.ndarray
    reduced_state: np.ndarray
    full_source: np.ndarray
    lifted_reduced_source: np.ndarray
    defect: np.ndarray
    absolute_gate: np.ndarray
    atol: np.ndarray
    rtol: float
    source_unit: str
    passed: bool
    failing_indices: tuple[int, ...]
    full_state_strictly_positive: bool = True
    scope: str = "one_state_source_lift_validation_no_reaction_map_or_global_bound"


class SourceLiftDefect(ValueError):
    """A specified source-lift gate failed; the complete report is retained."""
    def __init__(self, report):
        self.report = report
        super().__init__("SOURCE_LIFT_DEFECT_EXCEEDS_EXPLICIT_GATE:" + str(report.failing_indices))


def validate_source_lift(lift, reduced_state, R_full, R_reduced, *,
                         atol, rtol, source_unit):
    """Evaluate each supplied source once, with explicit absolute/relative gates.

    The lift is fixed and linear. A moving/nonlinear lift requires extra
    derivatives and is outside this function. Negative or zero full states are
    rejected before either source is evaluated; no abundance floors are added.
    Source callbacks receive immutable state arrays. A failed gate raises
    SourceLiftDefect carrying the computed report, rather than returning a
    successful source admission. Exact ``atol=rtol=0`` is permitted explicitly.
    """
    L = _array(lift, 2, "lift")
    z = _array(reduced_state, 1, "reduced_state")
    if L.shape[1] != len(z) or min(L.shape) == 0 or np.any(z < 0):
        raise MomentDomainError("LIFT_SHAPE_OR_REDUCED_NONNEGATIVITY_MISMATCH")
    if not callable(R_full) or not callable(R_reduced):
        raise MomentDomainError("EXPLICIT_FULL_AND_REDUCED_SOURCE_FUNCTIONS_REQUIRED")
    if not isinstance(source_unit, str) or not source_unit.strip():
        raise MomentDomainError("EXPLICIT_SOURCE_UNIT_REQUIRED")
    relative = _scalar(rtol, "rtol", nonnegative=True)
    if np.asarray(atol).ndim == 0:
        absolute = np.full(L.shape[0], _scalar(atol, "atol", nonnegative=True))
    else:
        absolute = _array(atol, 1, "atol")
        if absolute.shape != (L.shape[0],) or np.any(absolute < 0):
            raise MomentDomainError("COMPONENTWISE_ATOL_SHAPE_OR_SIGN_MISMATCH")
    y = _matvec(L, z, label="full_lifted_state")
    if np.any(y <= 0):
        raise MomentDomainError("STRICTLY_POSITIVE_FULL_LIFTED_STATE_REQUIRED")
    full = _array(R_full(y), 1, "full_source")
    reduced = _array(R_reduced(z), 1, "reduced_source")
    if full.shape != y.shape or reduced.shape != z.shape:
        raise MomentDomainError("SOURCE_OUTPUT_SHAPE_MISMATCH")
    lifted = _matvec(L, reduced, label="lifted_reduced_source")
    defect = _readonly([_sum((float(a), -float(b)), label="source_lift_defect")
                        for a, b in zip(full, lifted)])
    gates = _readonly([_sum((float(a), _muldiv((relative, max(abs(float(f)), abs(float(r)))),
                                              label="relative_source_gate")), label="absolute_relative_source_gate")
                       for a, f, r in zip(absolute, full, lifted)])
    bad = tuple(int(i) for i in np.flatnonzero(np.abs(defect) > gates))
    report = SourceLiftReport(y, z, full, lifted, defect, gates,
                              _readonly(absolute), relative, source_unit, not bad, bad)
    if bad:
        raise SourceLiftDefect(report)
    return report
