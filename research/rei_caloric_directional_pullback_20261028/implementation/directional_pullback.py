"""Exact right directional map for a supplied affine moving-knot family.

No physical EOS or callback temperature derivative is supplied by this module.
"""
from bisect import bisect_left
from dataclasses import dataclass
from fractions import Fraction
from deps.caloric_branch import CaloricBranch, exact


class DomainBoundary(ValueError):
    """Requested direction or unrestricted derivative leaves the bracket domain."""


class NonDifferentiableKnot(ValueError):
    """Unequal adjacent slopes do not define one common linearization."""


class MissingDerivativeInput(ValueError):
    """The supplied callback lacks its required temperature column."""


def _vector(values, length, label):
    if type(values) not in (tuple, list) or len(values) != length:
        raise ValueError(label + " must have length " + str(length))
    return tuple(exact(v) for v in values)


def _point(branch, energy):
    if not isinstance(branch, CaloricBranch):
        raise TypeError("the pinned CaloricBranch is required")
    e = exact(energy)
    if not branch.energies[0] <= e <= branch.energies[-1]:
        raise DomainBoundary("energy outside supplied branch image")
    j = bisect_left(branch.energies, e)
    return e, j, branch.energies[j] == e


@dataclass(frozen=True)
class DirectionalResult:
    temperature: Fraction
    temperature_direction: Fraction
    status: str
    segment: int | None
    unrestricted_linearization: bool


@dataclass(frozen=True)
class Linearization:
    energy_coefficient: Fraction
    temperature_knot_coefficients: tuple[Fraction, ...]
    energy_knot_coefficients: tuple[Fraction, ...]


def inverse_directional(branch, energy, energy_direction,
                        temperature_knot_directions, energy_knot_directions):
    """Right derivative through the explicitly affine parameter family."""
    e, j, knot = _point(branch, energy)
    n = len(branch.knots)
    v = exact(energy_direction)
    a = _vector(temperature_knot_directions, n, "temperature knot directions")
    b = _vector(energy_knot_directions, n, "energy knot directions")
    if knot:
        q = v - b[j]
        if (j == 0 and q < 0) or (j == n-1 and q > 0):
            raise DomainBoundary("outward endpoint direction is infeasible")
        smooth = 0 < j < n-1 and branch.slopes[j-1] == branch.slopes[j]
        if q == 0:
            return DirectionalResult(branch.temperatures[j], a[j], "moving_knot", None, smooth)
        segment = j if q > 0 else j-1
        return DirectionalResult(branch.temperatures[j], a[j]+q/branch.slopes[segment],
                                 "right" if q > 0 else "left", segment, smooth)
    i = j-1
    w = (e-branch.energies[i])/(branch.energies[i+1]-branch.energies[i])
    dt = (1-w)*a[i]+w*a[i+1]+(v-(1-w)*b[i]-w*b[i+1])/branch.slopes[i]
    return DirectionalResult(branch.inverse(e), dt, "open_segment", i, True)


def inverse_linearization(branch, energy):
    """Common first differential; refuses unequal-slope knots and endpoints."""
    e, j, knot = _point(branch, energy)
    n = len(branch.knots)
    a = [Fraction(0)]*n
    b = [Fraction(0)]*n
    if knot:
        if j in (0, n-1):
            raise DomainBoundary("endpoint has no unrestricted two-sided derivative")
        if branch.slopes[j-1] != branch.slopes[j]:
            raise NonDifferentiableKnot("unequal adjacent slopes")
        inverse_slope = 1/branch.slopes[j]
        a[j], b[j] = Fraction(1), -inverse_slope
    else:
        i = j-1
        w = (e-branch.energies[i])/(branch.energies[i+1]-branch.energies[i])
        inverse_slope = 1/branch.slopes[i]
        a[i], a[i+1] = 1-w, w
        b[i], b[i+1] = -(1-w)*inverse_slope, -w*inverse_slope
    return Linearization(inverse_slope, tuple(a), tuple(b))


def callback_direction(fixed_temperature_jacobian, state_direction,
                       temperature_column, temperature_direction):
    """Compose supplied derivative data; None never means a zero column."""
    if temperature_column is None:
        raise MissingDerivativeInput("callback temperature_column is required")
    if type(state_direction) not in (tuple, list) or not state_direction:
        raise ValueError("nonempty state direction required")
    z = _vector(state_direction, len(state_direction), "state direction")
    matrix = fixed_temperature_jacobian
    if type(matrix) not in (tuple, list) or not matrix:
        raise ValueError("nonempty rectangular callback Jacobian required")
    rows = tuple(_vector(row, len(z), "Jacobian row") for row in matrix)
    ft = _vector(temperature_column, len(rows), "temperature column")
    dt = exact(temperature_direction)
    return tuple(sum((x*y for x, y in zip(row, z)), Fraction(0))+column*dt
                 for row, column in zip(rows, ft))
