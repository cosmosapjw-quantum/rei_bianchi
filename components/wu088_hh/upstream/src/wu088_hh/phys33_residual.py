"""Exact-dyadic whole-cell radial envelope for the frozen PHYS33 cusp-transformed trial.

Scientific scope: a rigorous but potentially loose L2 upper bound on the *broken*
bulk transformed PDE residual over r0<r<rmax, integrated over all angles.
It is NOT an inverse, interface-distribution, origin, or outgoing-boundary
certificate. Interpolation is exact at the archived IEEE-binary64 radial nodes.
"""
from __future__ import annotations

import hashlib
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Sequence

import numpy as np

Q = Fraction
FROZEN_SUBSET_SHA256 = "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
L_MAX, PANEL_COUNT, DEGREE = 20, 6, 10
KAPPA_SQUARED = Q(49, 100)
LAMBDA = Q(1)
# All below are in a0 lengths and Ea=2I0 energy units, not in SI.
I0_EV = "13.605693122990"
CHI_RECEIVER_EV = "13.598434599702"


def dyadic(value: float) -> Q:
    """Exactly represent a stored finite binary64 value as a rational."""
    x = float(value)
    if not np.isfinite(x):
        raise ValueError("nonfinite archived binary64 coefficient")
    a, b = x.as_integer_ratio()
    return Q(a, b)


def mul(a: Sequence[Q], b: Sequence[Q]) -> list[Q]:
    out = [Q(0)] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] += ai * bj
    return out


def add(a: Sequence[Q], b: Sequence[Q]) -> list[Q]:
    out = [Q(0)] * max(len(a), len(b))
    for i, ai in enumerate(a):
        out[i] += ai
    for i, bi in enumerate(b):
        out[i] += bi
    return out


def scale(a: Sequence[Q], value: Q) -> list[Q]:
    return [v * value for v in a]


def derivative(a: Sequence[Q]) -> list[Q]:
    return [i * a[i] for i in range(1, len(a))] or [Q(0)]


def value(a: Sequence[Q], x: Q) -> Q:
    out = Q(0)
    for c in a[::-1]:
        out = out * x + c
    return out


def interpolants(nodes: Sequence[Q]) -> list[list[Q]]:
    """Lagrange basis at *actual stored dyadic* abscissae, not ideal cos nodes."""
    if len(set(nodes)) != len(nodes):
        raise ValueError("duplicate radial collocation nodes")
    out = []
    for i, xi in enumerate(nodes):
        poly, den = [Q(1)], Q(1)
        for j, xj in enumerate(nodes):
            if j == i:
                continue
            poly = mul(poly, [-xj, Q(1)])
            den *= xi - xj
        out.append(scale(poly, Q(1) / den))
    return out


def reconstruct(samples: Sequence[complex], basis: Sequence[Sequence[Q]]) -> tuple[list[Q], list[Q]]:
    n = len(basis)
    if len(samples) != n:
        raise ValueError("sample count and interpolation basis disagree")
    re, im = [Q(0)] * n, [Q(0)] * n
    for i, z in enumerate(samples):
        zr, zi = dyadic(z.real), dyadic(z.imag)
        for j, c in enumerate(basis[i]):
            re[j] += zr * c
            im[j] += zi * c
    return re, im


def squared(re: Sequence[Q], im: Sequence[Q]) -> list[Q]:
    return add(mul(re, re), mul(im, im))


def integrate(poly: Sequence[Q], left: Q, right: Q) -> Q:
    if left >= right:
        raise ValueError("invalid integration interval")
    return sum((c * (right ** (i + 1) - left ** (i + 1)) / (i + 1)
                for i, c in enumerate(poly)), Q(0))


def ceil_sqrt_fixed(x: Q, digits: int = 12) -> str:
    """Outward decimal bound, verified in exact integer arithmetic."""
    if x < 0 or not 0 <= digits <= 24:
        raise ValueError("expected positive rational and bounded digits")
    base = 10 ** digits
    n = isqrt(x.numerator * base * base // x.denominator)
    if n * n * x.denominator < x.numerator * base * base:
        n += 1
    whole, frac = divmod(n, base)
    return str(whole) if not digits else f"{whole}.{frac:0{digits}d}"


def load_frozen(filename: str | Path, pinned: bool = True) -> tuple[np.ndarray, np.ndarray, str]:
    path = Path(filename)
    contents = path.read_bytes()
    digest = hashlib.sha256(contents).hexdigest()
    if pinned and digest != FROZEN_SUBSET_SHA256:
        raise ValueError("frozen source byte identity mismatch")
    with np.load(path, allow_pickle=False) as z:
        if set(z.files) != {"r", "u"}:
            raise ValueError("unexpected source NPZ members")
        r = np.array(z["r"], copy=True)
        u = np.array(z["u"], copy=True)
    if r.shape != (PANEL_COUNT * (DEGREE + 1),) or u.shape != ((L_MAX + 1) * r.size,):
        raise ValueError("frozen input must contain r[66] and u[1386]")
    if r.dtype != np.dtype("float64") or u.dtype != np.dtype("complex128"):
        raise ValueError("frozen input dtypes not preserved")
    if not np.isfinite(r).all() or not np.isfinite(u).all():
        raise ValueError("nonfinite frozen input")
    r = r.reshape(PANEL_COUNT, DEGREE + 1)
    if not all(np.all(np.diff(row) > 0) for row in r):
        raise ValueError("nodes not strictly increasing")
    if not all(r[i, -1] == r[i + 1, 0] for i in range(PANEL_COUNT - 1)):
        raise ValueError("panel interfaces are not identical dyadic endpoints")
    if r[0, 0] <= 0:
        raise ValueError("origin singularity must remain excluded")
    return r, u.reshape((L_MAX + 1, PANEL_COUNT, DEGREE + 1)), digest


def bound_broken_bulk(filename: str | Path, subcells: int = 8,
                      output_digits: int = 12, pinned: bool = True,
                      partition: str = "geometric") -> dict:
    """Compute exact dyadic upper bounds; NO floating quadrature enters the bound.

    Bound ||D y||, ||grad(y/r)||, ||y/r|| using exact polynomial integrals and
    each subcell's minimum radius. Then the original transformed PDE satisfies
    ||residual|| <= ||D y|| + 2 lambda ||grad(y/r)|| + 4 ||y/r|| + (1+k^2)
    because |lambda exp(-s)|<=1, |U_lambda|<=2, F^-1<=1 and ||phi||=1.
    """
    if isinstance(subcells, bool) or not isinstance(subcells, int) or not 1 <= subcells <= 256:
        raise ValueError("subcells must be an integer between 1 and 256")
    if partition not in ("uniform", "geometric"):
        raise ValueError("partition must be uniform or geometric")
    rr, uu, digest = load_frozen(filename, pinned)
    diag2, grad2, mass2 = Q(0), Q(0), Q(0)
    panels = []
    partition_points_exact = []
    jumps = []
    previous: list[tuple[Q, Q, Q, Q]] | None = None
    nodal_failures = 0
    for j in range(PANEL_COUNT):
        lo, hi = dyadic(rr[j, 0]), dyadic(rr[j, -1])
        half, mid = (hi - lo) / 2, (hi + lo) / 2
        nodes = [(dyadic(x) - mid) / half for x in rr[j]]
        basis = interpolants(nodes)
        rp = [mid, half]
        r2 = mul(rp, rp)
        if partition == "geometric":
            # Endpoints generated in binary64 are *then treated exactly as dyadics*.
            # Any strictly increasing rational partition yields a sound bound.
            cut_points = [dyadic(x) for x in np.geomspace(float(lo), float(hi), subcells + 1)]
            cut_points[0], cut_points[-1] = lo, hi
        else:
            cut_points = [lo + (hi - lo) * Q(i, subcells) for i in range(subcells + 1)]
        if any(a >= b for a, b in zip(cut_points, cut_points[1:])):
            raise ValueError("subcells not strictly ordered")
        # Freeze the *exact* rational partition. A future NumPy version may
        # select different geometric binary64 breakpoints; the certificate is
        # about these explicit cells, not an unrecorded geomspace convention.
        partition_points_exact.append([str(x) for x in cut_points])
        p_diag2, p_grad2, p_mass2 = Q(0), Q(0), Q(0)
        now: list[tuple[Q, Q, Q, Q]] = []
        for ell in range(L_MAX + 1):
            re, im = reconstruct(uu[ell, j], basis)
            for i, val in enumerate(uu[ell, j]):
                if value(re, nodes[i]) != dyadic(val.real) or value(im, nodes[i]) != dyadic(val.imag):
                    nodal_failures += 1
            re1, im1 = scale(derivative(re), 1 / half), scale(derivative(im), 1 / half)
            re2, im2 = scale(derivative(re1), 1 / half), scale(derivative(im1), 1 / half)
            # Exact numerator for D u = u''+(k^2+2/r-ell(ell+1)/r^2)u.
            potential = add(add(scale(r2, KAPPA_SQUARED), scale(rp, Q(2))),
                            [-Q(ell * (ell + 1))])
            nu_re = add(mul(r2, re2), mul(potential, re))
            nu_im = add(mul(r2, im2), mul(potential, im))
            gr_re = add(mul(rp, re1), scale(re, Q(-1)))
            gr_im = add(mul(rp, im1), scale(im, Q(-1)))
            sr2, sg2, su2 = squared(nu_re, nu_im), squared(gr_re, gr_im), squared(re, im)
            p_mass2 += half * integrate(su2, Q(-1), Q(1))
            for cell in range(subcells):
                minimum, maximum = cut_points[cell], cut_points[cell + 1]
                x0, x1 = (minimum - mid) / half, (maximum - mid) / half
                if minimum <= 0:
                    raise ValueError("subcell intersects excluded singular origin")
                p_diag2 += half * integrate(sr2, x0, x1) / minimum ** 4
                p_grad2 += half * (integrate(sg2, x0, x1) +
                                     ell * (ell + 1) * integrate(su2, x0, x1)) / minimum ** 2
            now.append((value(re, Q(-1)), value(im, Q(-1)),
                        value(re1, Q(-1)), value(im1, Q(-1))))
            if previous is not None:
                old = previous[ell]
                # Cache old *right* endpoint from the previous panel.
                jumps.append((j, ell,
                              (old[0] - now[-1][0]) ** 2 + (old[1] - now[-1][1]) ** 2,
                              (old[2] - now[-1][2]) ** 2 + (old[3] - now[-1][3]) ** 2))
            # Replace left with right endpoint for use in next panel.
            now[-1] = (value(re, Q(1)), value(im, Q(1)),
                       value(re1, Q(1)), value(im1, Q(1)))
        if min(p_diag2, p_grad2, p_mass2) < 0:
            raise ArithmeticError("exact polynomial integral unexpectedly negative")
        diag2 += p_diag2
        grad2 += p_grad2
        mass2 += p_mass2
        previous = now
        panels.append({"panel": j, "r": [str(float(lo)), str(float(hi))],
                       "coulomb_diagonal_l2_upper": ceil_sqrt_fixed(p_diag2, output_digits),
                       "gradient_l2_upper": ceil_sqrt_fixed(p_grad2, output_digits),
                       "reduced_state_l2_upper": ceil_sqrt_fixed(p_mass2, output_digits)})
    if nodal_failures:
        raise ArithmeticError(f"exact nodal reconstruction failed {nodal_failures} times")
    jumps_by_r = []
    for j in range(1, PANEL_COUNT):
        jj = [x for x in jumps if x[0] == j]
        jumps_by_r.append({"interface": j, "r": str(float(dyadic(rr[j, 0]))),
                           "value_l2_upper": ceil_sqrt_fixed(sum(x[2] for x in jj), output_digits),
                           "derivative_l2_upper": ceil_sqrt_fixed(sum(x[3] for x in jj), output_digits)})
    dstr = ceil_sqrt_fixed(diag2, output_digits)
    gstr = ceil_sqrt_fixed(grad2, output_digits)
    mstr = ceil_sqrt_fixed(mass2, output_digits)
    # Decimal representations are exact positive fractions and are already outward.
    upper = Q(dstr) + Q(2) * Q(gstr) + Q(4) * Q(mstr) + Q(149, 100)
    return {
        "schema": "WU088_HH_PHYS34_BROKEN_WHOLE_CELL_V1",
        "source_sha256": digest,
        "node_interpolation": "exact Lagrange polynomial through archived binary64 r and u, all nodes verified",
        "subcells_per_panel": subcells, "partition": partition,
        "partition_exact_rationals": partition_points_exact, "angular_L": L_MAX,
        "domain": [str(float(dyadic(rr[0, 0]))), str(float(dyadic(rr[-1, -1])))],
        "units": {"r": "a0", "h": "2I0", "kappa": "7/10", "lambda": "1",
                  "receiver_chiH_eV": CHI_RECEIVER_EV, "source_I0_eV": I0_EV},
        "norm_upper": {"coulomb_diagonal": dstr, "state_gradient": gstr,
                       "state": mstr,
                       "broken_transformed_bulk_residual": ceil_sqrt_fixed(upper * upper, output_digits)},
        "panels": panels, "interfaces": jumps_by_r,
        "checked_nodal_values": (L_MAX + 1) * PANEL_COUNT * (DEGREE + 1),
        "status": "WHOLE_CELL_BROKEN_BULK_UPPER_COVERAGE_EXPLICIT",
        "claims_excluded": [
            "distributional interface jump in H-1", "r<first radial node",
            "outgoing boundary defect", "continuous low-Schur inverse",
            "global scattering amplitude/thermal rate", "certified special-function or atom-calibration error",
        ],
        "mathematical_contract": (
            "Exact dyadic polynomial integrals + positive radial-minimum bounds; "
            "|U_lambda|<=2, |lambda exp(-s)|<=1, F^-1<=1, ||phi||_L2(R3)=1. "
            "Result is a conservative full-angular bound on the broken transformed PDE "
            "bulk, not an end-to-end continuum certificate."),
    }
