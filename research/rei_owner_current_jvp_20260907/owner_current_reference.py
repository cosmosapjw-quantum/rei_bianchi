"""UNEXECUTED research candidate: exact-real resolved owner current and JVP.

No production imports, atomic rates, interval arithmetic, or runtime authority.
One photon group, fixed structural support, positive opacity and node counts.
The subgrid output is its GROUP TOTAL, not its state-dependent node distribution.
Fractions model exact input numbers, not the binary64 residual-correction path.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from typing import Sequence

Scalar = int | Q
Grid = tuple[tuple[Q, ...], ...]


def rational(value: Scalar) -> Q:
    if isinstance(value, Q):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return Q(value)
    raise TypeError("exact rational input required; floats/bools are not admitted")


def _vector(values: Sequence[Scalar], size: int) -> tuple[Q, ...]:
    result = tuple(rational(x) for x in values)
    if len(result) != size:
        raise ValueError(f"expected {size} entries")
    return result


def _grid(values: Sequence[Sequence[Scalar]]) -> Grid:
    rows = tuple(tuple(rational(x) for x in row) for row in values)
    if len(rows) != 3 or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("expected rectangular [HI,HeI,HeII] x nonempty-node grid")
    return rows


def coefficient_jvp(prefactors, d_prefactors, *, hydrogen_total: Scalar,
                    helium_total: Scalar, d_hydrogen_total: Scalar = 0,
                    d_helium_total: Scalar = 0):
    """prefactors=(a*nH_phys*sigmaHI*Mpc, a*nHe_phys*sigmaHeI*Mpc,
    a*nHe_phys*sigmaHeII*Mpc). Preserve HeII-per-H, NOT HeII-per-He.
    Callers bind the actual constants, redshift/cross sections and directions.
    This function does not infer them from a synthetic fixture.
    """
    p = _vector(prefactors, 3)
    dp = _vector(d_prefactors, 3)
    h, he = rational(hydrogen_total), rational(helium_total)
    dh, dhe = rational(d_hydrogen_total), rational(d_helium_total)
    if h <= 0 or he <= 0 or any(x < 0 for x in p):
        raise ValueError("positive elemental totals and nonnegative prefactors required")
    if any(x == 0 and dx != 0 for x, dx in zip(p, dp)):
        raise ValueError("structurally absent coefficient cannot move")
    den, dden = (h, he, h), (dh, dhe, dh)
    c = tuple(p[s] / den[s] for s in range(3))
    dc = tuple((dp[s] - c[s] * dden[s]) / den[s] for s in range(3))
    return c, dc


@dataclass(frozen=True)
class OwnerCurrentResult:
    resolved: Grid
    d_resolved: Grid
    subgrid_total: Q
    d_subgrid_total: Q
    raw_total: Q
    d_raw_total: Q
    augmented_l1_direction_bound: Q


def resolved_current_jvp(counts, d_counts, strengths, d_strengths, *,
                         current: Scalar, d_current: Scalar = 0,
                         external: Scalar, d_external: Scalar = 0,
                         opacity: Scalar) -> OwnerCurrentResult:
    """Exact-real source reduction j_si=J*c_s*N_si/R and full directional JVP.

    Strengths are raw-opacity/count, external is subgrid raw-opacity, current
    is absorbed photon count/time. Opacity must be positive: its direct effect
    cancels only at fixed current and external response. All their indirect
    forcing dependencies must be supplied through the corresponding tangents.
    Signed tangents are allowed; zero structural strengths/external/current
    are restricted to zero tangents (fixed, two-sided active domain).
    """
    n, dn = _grid(counts), _grid(d_counts)
    if len(n[0]) != len(dn[0]):
        raise ValueError("count and tangent shapes differ")
    c, dc = _vector(strengths, 3), _vector(d_strengths, 3)
    j, dj = rational(current), rational(d_current)
    e, de = rational(external), rational(d_external)
    kappa = rational(opacity)
    if kappa <= 0 or j < 0 or e < 0 or any(x < 0 for x in c):
        raise ValueError("outside fixed positive-opacity/nonnegative-owner domain")
    if any(x <= 0 for row in n for x in row):
        raise ValueError("strictly positive node populations required")
    if any(x == 0 and dx != 0 for x, dx in zip(c + (e, j), dc + (de, dj))):
        raise ValueError("moving zero support/current needs a separate one-sided analysis")
    a = tuple(tuple(c[s] * n[s][i] for i in range(len(n[0]))) for s in range(3))
    da = tuple(tuple(c[s] * dn[s][i] + dc[s] * n[s][i]
                     for i in range(len(n[0]))) for s in range(3))
    r = e + sum(x for row in a for x in row)
    dr = de + sum(x for row in da for x in row)
    if r <= 0:
        raise ValueError("positive total raw owner support required")
    p = tuple(tuple(x / r for x in row) for row in a)
    out = tuple(tuple(j * x for x in row) for row in p)
    dout = tuple(tuple(dj * p[s][i] + j * (da[s][i] - p[s][i] * dr) / r
                       for i in range(len(n[0]))) for s in range(3))
    p0 = e / r
    bound = abs(dj) + 2 * j / r * (abs(de) + sum(abs(x) for row in da for x in row))
    return OwnerCurrentResult(out, dout, j * p0,
                              dj * p0 + j * (de - p0 * dr) / r, r, dr, bound)
