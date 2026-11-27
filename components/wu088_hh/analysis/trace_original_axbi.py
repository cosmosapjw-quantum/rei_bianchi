"""Drive trace isotope exchange on the original five saved AXBI H/He samples.

Coefficient interpolation is piecewise linear in proper time. Ionic fractions
are per element. A second implementation uses the optical-depth coordinate.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss

from rei_bianchi.microphysics.hh import savin_rates


SOURCE = "research/rei_igm_sync_20261116/approximation_validity/incremental_fifth/results_five/five_case_abundances.csv.gz"
SOURCE_BLOB = "ce22a6b6d94aabf1bffcc3b5c472316cac1983d4"
CASES = ("ZERO", "SHEAR_HALF_PLUS", "SHEAR_HALF_MINUS", "SHEAR_PLUS", "SHEAR_MINUS")
INPUT_COLUMNS = ("a", "time_s", "temperature_K", "nH_proper_cm3", "x_HII")


def parse_histories(file):
    data = file.read_bytes()
    if (
        hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        != SOURCE_BLOB
    ):
        raise ValueError("The five-case source differs from the AX08 input")
    rows = list(csv.DictReader(io.StringIO(gzip.decompress(data).decode())))
    histories = {}
    for case in CASES:
        x = np.array(
            [[float(r[c]) for c in INPUT_COLUMNS] for r in rows if r["case"] == case]
        )
        if len(x) != 1001 or not np.isfinite(x).all():
            raise ValueError("Incomplete original trajectory " + case)
        if not (np.diff(x[:, 0]) > 0).all() or not (np.diff(x[:, 1]) > 0).all():
            raise ValueError("Nonmonotone scale or clock")
        if np.any(x[:, 3] <= 0) or np.any((x[:, 4] < 0) | (x[:, 4] > 1)):
            raise ValueError("Unphysical source H density or fraction")
        histories[case] = x
    return histories


def coefficients(x):
    rates = np.array([savin_rates(float(t)) for t in x[:, 2]])
    return rates[:, 0] * x[:, 3] * x[:, 4], rates[:, 1] * x[:, 3] * (1.0 - x[:, 4])


def propagate_midpoints(t, forward, back, y0, subdivisions):
    y = float(y0)
    curve = [y]
    fractions = (np.arange(subdivisions, dtype=float) + 0.5) / subdivisions
    for j, dt in enumerate(np.diff(t)):
        a = forward[j] + (forward[j + 1] - forward[j]) * fractions
        b = back[j] + (back[j + 1] - back[j]) * fractions
        optical = (a + b) * (dt / subdivisions)
        decay = np.exp(-optical)
        source = -np.expm1(-optical) * a / (a + b)
        for factor, injection in zip(decay, source):
            y = factor * y + injection
        curve.append(y)
    return np.asarray(curve)


def optical_interval(y0, dt, a0, a1, b0, b1, rule):
    """Endpoint of the affine-rate equation, with quadrature in optical depth."""
    if dt == 0:
        return float(y0), 0.0
    l0, l1 = a0 + b0, a1 + b1
    total = 0.5 * dt * (l0 + l1)
    # Equilibrium lies in [0,1], so truncating here costs at most exp(-50) per cell.
    extent = min(total, 50.0)
    pieces = max(1, math.ceil(extent))
    nodes, weights = rule
    s = ((np.arange(pieces)[:, None] + 0.5) + 0.5 * nodes) * (extent / pieces)
    # s=dt*w*(lambda_right-delta_lambda*w/2), w=(t_right-t)/dt.
    discriminant = l1 * l1 - 2.0 * (l1 - l0) * s / dt
    if np.any(discriminant <= 0):
        raise ArithmeticError("Invalid optical coordinate on open cell")
    w = 2.0 * s / (dt * (l1 + np.sqrt(discriminant)))
    a = a1 - w * (a1 - a0)
    local_lam = l1 - (l1 - l0) * w
    integral = extent / (2 * pieces) * np.sum(weights * (a / local_lam) * np.exp(-s))
    return y0 * math.exp(-total) + integral, total


def propagate_optical(t, forward, back, y0, order):
    rule = leggauss(order)
    curve = [float(y0)]
    cumulative = [0.0]
    for j, dt in enumerate(np.diff(t)):
        y, total = optical_interval(
            curve[-1], dt, forward[j], forward[j + 1], back[j], back[j + 1], rule
        )
        curve.append(y)
        cumulative.append(cumulative[-1] + total)
    return np.asarray(curve), np.asarray(cumulative)


def evaluate_at(curve, grid, axis):
    """Dense D solution. Scale-factor matching uses piecewise affine a(t)."""
    x, y = curve
    coord = x[:, axis]
    a, b = coefficients(x)
    if np.any(grid < coord[0]) or np.any(grid > coord[-1]):
        raise ValueError("Coordinate extrapolation")
    rule = leggauss(16)
    out = []
    for q in grid:
        j = int(np.searchsorted(coord, q))
        if q == coord[j]:
            out.append(y[j])
            continue
        u = (q - coord[j - 1]) / (coord[j] - coord[j - 1])
        dt = u * (x[j, 1] - x[j - 1, 1])
        aq = a[j - 1] + u * (a[j] - a[j - 1])
        bq = b[j - 1] + u * (b[j] - b[j - 1])
        dense, _ = optical_interval(y[j - 1], dt, a[j - 1], aq, b[j - 1], bq, rule)
        out.append(dense)
    return np.array(out)


def comparison(candidate, reference, axis, index):
    grid = candidate[0][:, axis]
    bg = reference[0][:, axis]
    shared = (grid >= bg[0]) & (grid <= bg[-1])
    grid = grid[shared]
    reference_at = evaluate_at(reference, grid, axis)
    delta = candidate[1][shared] - reference_at
    imax = int(np.argmax(abs(delta)))
    return dict(
        axis=index,
        compared=int(shared.sum()),
        max_abs=float(abs(delta[imax])),
        signed_at_max=float(delta[imax]),
        at_axis=float(grid[imax]),
        linear_abundance_interpolation_max_difference=float(
            max(abs(np.interp(grid, bg, reference[1]) - reference_at))
        ),
        at_candidate_zbar=float(1 / candidate[0][shared, 0][imax] - 1),
    )


def run(source, target):
    histories = parse_histories(source)
    target.mkdir(parents=True, exist_ok=True)
    curves = {}
    coarse_curves = {}
    report = dict(
        source=SOURCE,
        source_git_blob=SOURCE_BLOB,
        original_case_count=len(histories),
        reconstruction="Forward/back rates at each source knot are linearly interpolated in elapsed proper time",
        model="Ground-state atomic deuterium with charge exchange alone in prescribed AXBI H/T/density histories. Trace limit, no feedback to H, thermal, electron or photon evolution.",
        initial_conditions="H-matched y0=x_HII(t0); neutral y0=0 differs by y0*exp(-integrated_relaxation)",
        scope="Conditional science on 1001 saved knots/case. Interpolation uncertainty inside a saved history interval and omitted D photoionization remain outside this reconstruction.",
        inputs=dict(
            table_DOI="10.1086/324218",
            rates_unit="cm3 s-1",
            density_unit="proper cm-3",
            time_unit="proper s",
        ),
        cases={},
        signed_responses={},
    )
    trace_rows = []
    for name, x in histories.items():
        t = x[:, 1]
        y0 = x[0, 4]
        f, b = coefficients(x)
        y, optical = propagate_optical(t, f, b, y0, 16)
        ref, _ = propagate_optical(t, f, b, y0, 8)
        if np.max(abs(y - ref)) > 2e-13 or np.any(y < 0) or np.any(y > 1):
            raise ArithmeticError("Positive-domain or independent quadrature failure")
        # Coarsening changes the reconstructed rates, serving as a sampling sensitivity.
        coarse, _ = propagate_optical(t[::2], f[::2], b[::2], y0, 16)
        midpoints = {n: propagate_midpoints(t, f, b, y0, n) for n in (1, 2, 4, 16, 64)}
        delta_eq = y - f / (f + b)
        ipeak = int(np.argmax(abs(delta_eq)))
        report["cases"][name] = dict(
            source_knots=len(t),
            temperature_range_K=[float(x[:, 2].min()), float(x[:, 2].max())],
            y_DII_endpoint=float(y[-1]),
            x_HII_endpoint=float(x[-1, 4]),
            endpoint_delta_DII_minus_HII=float(y[-1] - x[-1, 4]),
            total_relaxation_depth=float(optical[-1]),
            log10_final_initial_memory=float(-optical[-1] / math.log(10)),
            max_transient_minus_CX_equilibrium=float(delta_eq[ipeak]),
            zbar_at_max_departure=float(1 / x[ipeak, 0] - 1),
            optical_GL8_GL16_max_abs=float(max(abs(y - ref))),
            midpoint_max_abs_error_vs_GL16={
                str(n): float(max(abs(a - y))) for n, a in midpoints.items()
            },
            every_second_knot_vs_all_knots_at_shared_points=float(
                max(abs(coarse - y[::2]))
            ),
            opt_tail_abs_source_bound_per_step=math.exp(-50),
        )
        curves[name] = x, y
        coarse_curves[name] = x[::2], coarse
        for cell, value, tau, eq in zip(x, y, optical, f / (f + b)):
            trace_rows.append(
                [name, *cell, value, value - y0 * math.exp(-tau), eq, tau]
            )
    for name in CASES[1:]:
        pair = []
        for axis, label in enumerate(("scale_factor", "elapsed_proper_seconds")):
            full = comparison(curves[name], curves["ZERO"], axis, label)
            coarse = comparison(coarse_curves[name], coarse_curves["ZERO"], axis, label)
            cx, cy = coarse_curves[name]
            rx, ry = coarse_curves["ZERO"]
            grid = cx[:, axis]
            shared = (grid >= rx[0, axis]) & (grid <= rx[-1, axis])
            grid = grid[shared]
            d_coarse = cy[shared] - evaluate_at(coarse_curves["ZERO"], grid, axis)
            d_fine = curves[name][1][::2][shared] - evaluate_at(
                curves["ZERO"], grid, axis
            )
            full["every_second_knot_pair_signed_max"] = coarse["signed_at_max"]
            full["paired_coarsening_max_abs_at_common_coordinates"] = float(
                np.max(abs(d_fine - d_coarse))
            )
            pair.append(full)
        report["signed_responses"][name] = pair
    with (
        (target / "FIVE_CASE_TRACE.csv.gz").open("wb") as fp,
        gzip.GzipFile(filename="", fileobj=fp, mode="wb", mtime=0) as gz,
        io.TextIOWrapper(gz, encoding="ascii", newline="") as out,
    ):
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow(
            (
                "case",
                *INPUT_COLUMNS,
                "x_DII_Hmatched",
                "x_DII_neutralIC",
                "x_DII_CXequilibrium",
                "cumulative_relaxation_depth",
            )
        )
        writer.writerows(trace_rows)
    (target / "FIVE_CASE_TRACE.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n"
    )
    print(
        json.dumps(
            dict(
                rows=len(trace_rows),
                plus=report["cases"]["SHEAR_PLUS"],
                response=report["signed_responses"]["SHEAR_PLUS"],
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("output", type=Path)
    opts = p.parse_args()
    run(opts.source, opts.output)
