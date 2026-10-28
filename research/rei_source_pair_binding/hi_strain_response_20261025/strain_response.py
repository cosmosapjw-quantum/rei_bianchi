"""Instantaneous initially-isotropic collisionless strain response.

Fixed represented (k,w), exact nominal M=mc^2 in eV. Only R/R_M are new
radial integrals; W/S are supplied saved enclosures. This module adds no
cohort history, geometry clock, density, rest energy, or viscosity law.
"""
from fractions import Fraction

from reuse.stress_source import Interval, enclose, rational


def scalar(value):
    if isinstance(value, bool):
        raise ValueError("bool is not a physical scalar")
    return rational(value)


def matrix(value):
    try:
        if len(value) != 3 or any(len(row) != 3 for row in value):
            raise ValueError("exactly 3x3 matrix required")
        result = tuple(tuple(scalar(v) for v in row) for row in value)
    except TypeError as exc:
        raise ValueError("exactly 3x3 matrix required") from exc
    if any(result[i][j] != result[j][i] for i in range(3) for j in range(3)):
        raise ValueError("exact symmetry required; no auto-symmetrization")
    return result


def trace(B):
    return sum((B[i][i] for i in range(3)), Fraction(0))


def T(B):
    B = matrix(B)
    theta = trace(B)
    return tuple(tuple(2 * B[i][j] + (theta if i == j else 0)
                       for j in range(3)) for i in range(3))


def radial_terms(atoms, mass):
    """Exact individual new kernels; no general-rational native total sum."""
    M = scalar(mass)
    if M <= 0:
        raise ValueError("M must be positive")
    R, RM = [], []
    for kinetic, weight in atoms:
        k, w = scalar(kinetic), scalar(weight)
        if k < 0 or w < 0:
            raise ValueError("nonnegative finite k,w required")
        E = k + M
        R.append(w * k * k * (k + 2 * M) ** 2 / E ** 3)
        RM.append(w * k * k * (k + 2 * M) * (k - 2 * M) / E ** 4)
    return R, RM


def coefficients(W, S, R, RM):
    C = W.scale(5) - R
    CM = S.scale(5) - RM
    return {"C": C, "CM": CM, "kappa": C.scale(Fraction(2, 15)),
            "Gamma": C.divide_positive(W.scale(3)) if W.lo > 0 else None,
            "RoverW": R.divide_positive(W) if W.lo > 0 else None,
            "RoverC": R.divide_positive(C) if C.lo > 0 else None}


def strain_tensor(C, B):
    transform = T(B)
    return [[C.scale(-transform[i][j] / 15) for j in range(3)] for i in range(3)]


def source_jvp(C, CM, B, dB, a, X, da, dX, dM):
    a, X, da, dX, dM = map(scalar, (a, X, da, dX, dM))
    if a < 0 or X < 0:
        raise ValueError("nonnegative amplitudes a,X required")
    TB, TdB = T(B), T(dB)
    amplitude = a * X
    coefficient_direction = C.scale(a * dX + X * da) + CM.scale(amplitude * dM)
    Q = [[C.scale(-amplitude * TB[i][j] / 15) for j in range(3)] for i in range(3)]
    Jv = [[(coefficient_direction.scale(TB[i][j]) + C.scale(amplitude * TdB[i][j])).scale(Fraction(-1, 15))
           for j in range(3)] for i in range(3)]
    return {"Q": Q, "JVP": Jv}


def number_energy_derivatives(A, K, W, B):
    A, K = scalar(A), scalar(K)
    if A < 0 or K < 0:
        raise ValueError("nonnegative saved A,K required")
    theta = trace(matrix(B))
    return {"delta_N": Interval.point(A).scale(-theta),
            "delta_K": (Interval.point(K) + W.scale(Fraction(1, 3))).scale(-theta)}


def tensor_payload(value):
    return [[entry.payload() for entry in row] for row in value]


def directions14():
    """Exact weights and dyads n_i*n_j; no irrational n_i is rounded."""
    rays = []
    for axis in range(3):
        dyad = tuple(tuple(Fraction(int(i == axis and j == axis)) for j in range(3)) for i in range(3))
        rays.extend([(Fraction(1, 15), dyad), (Fraction(1, 15), dyad)])
    for x in (-1, 1):
        for y in (-1, 1):
            for z in (-1, 1):
                signs = (x, y, z)
                rays.append((Fraction(3, 40), tuple(tuple(Fraction(signs[i] * signs[j], 3)
                                                        for j in range(3)) for i in range(3))))
    return rays
