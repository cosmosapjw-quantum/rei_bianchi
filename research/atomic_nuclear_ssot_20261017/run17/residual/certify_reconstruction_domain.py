#!/usr/bin/env python3
"""Produce exact-rational Bernstein certificates from frozen RUN17 arrays."""
from __future__ import annotations
import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys
import time
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"native"))
from native_context import load_context, file_identity, sha256, save_json
import numpy as np
from bernstein_domain import (rational, bernstein_coefficients, dop853_power,
    shifted_cubic_power, affine_gas_power, minimum_record)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--run16-root", required=True, type=Path)
    parser.add_argument("--control-result", required=True, type=Path)
    parser.add_argument("--residual-result", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(); started = time.perf_counter()
    ctx = load_context(args.source_root, args.run16_root)
    inputs = []
    def arrays(result_path, member):
        result_path = result_path.resolve()
        record = json.loads(result_path.read_text())
        path = result_path.parent/Path(record[member]["path"]).name
        if sha256(path) != record[member]["sha256"]:
            raise ValueError("frozen input array mismatch")
        inputs.extend([file_identity(result_path), file_identity(path)])
        with np.load(path, allow_pickle=False) as data:
            return {key: data[key].copy() for key in data.files}
    native = arrays(args.control_result, "state")
    residual = arrays(args.residual_result, "arrays")
    charge_weight = [int(v) for v in (1+ctx.native.CHARGE)]
    K = 2*rational(ctx.native.EV_J)/(3*rational(ctx.native.KB))
    certificates = []
    def certify(label, left, right, q_power, depth_power=()):
        gas = affine_gas_power(q_power, ctx.gas0, ctx.lift, ctx.q0)
        degree = len(gas[0])-1
        particles = [sum((charge_weight[s]*gas[s][k] for s in range(13)), Fraction(0))
                     for k in range(degree+1)]
        nuclear = []
        for indices in ([1, 2], [3, 4], [10, 11, 12]):
            coefficients = [sum((gas[i][k] for i in indices), Fraction(0)) for k in range(degree+1)]
            total = sum((rational(ctx.gas0[i]) for i in indices), Fraction(0))
            nuclear.append(coefficients[0] == total and all(v == 0 for v in coefficients[1:]))
        margins = {f"gas_{index}": minimum_record(gas[index]) for index in (1,2,3,4,10,11,12,13)}
        margins["particle_count"] = minimum_record(particles)
        margins["T_above_2.7K_times_particle_count"] = minimum_record([
            K*gas[13][k]-rational(2.7)*particles[k] for k in range(degree+1)])
        margins["T_below_200000K_times_particle_count"] = minimum_record([
            rational(200000.)*particles[k]-K*gas[13][k] for k in range(degree+1)])
        depth_bounds = [min(bernstein_coefficients(power)) for power in depth_power]
        item = {"label": label, "interval_z": [left, right], "polynomial_degree": degree,
                "nuclear_totals_exactly_constant": nuclear, "gas_EOS_margins": margins,
                "depth_polynomials_checked": len(depth_bounds),
                "all_depth_Bernstein_bounds_nonnegative": all(v >= 0 for v in depth_bounds)}
        if depth_bounds:
            minimum = min(depth_bounds)
            item["minimum_depth_lower_bound_rational"] = str(minimum)
            item["minimum_depth_lower_bound_float_for_display"] = float(minimum)
        item["certificate_pass"] = (all(nuclear) and all(v["exact_positive"] for v in margins.values())
                                    and item["all_depth_Bernstein_bounds_nonnegative"])
        certificates.append(item)
    # P has a single cubic piece on this panel. Its ideal path-consistent depths
    # are nonnegative from positive opacity/gas; no quadrature polynomial claim.
    knots = residual["pchip_knots"]
    if not (knots[0] <= ctx.left < ctx.right <= knots[1]):
        raise ValueError("one original PCHIP piece expected")
    qpower = [shifted_cubic_power(residual["pchip_q_coefficients"][:, 0, j],
                rational(ctx.left)-rational(knots[0]), rational(ctx.right)-rational(ctx.left))
              for j in range(5)]
    certify("P invariant cubic", ctx.left, ctx.right, qpower)
    for index, (left, right) in enumerate(zip(native["accepted_z"][:-1], native["accepted_z"][1:])):
        if left != native["dense_t_old"][index]:
            raise ValueError("dense predecessor time mismatch")
        x_scale = (rational(right)-rational(left))/rational(native["dense_h"][index])
        polynomial = [dop853_power(native["dense_y_old"][index, j],
                         native["dense_F"][index, :, j], x_scale) for j in range(5+ctx.active)]
        certify(f"R dense piece {index}", float(left), float(right), polynomial[:5], polynomial[5:])
        certificates[-1]["exact_clock_scale"] = str(x_scale)
    result = {"schema": "rei.run17.bernstein-reconstruction-domain.v1",
        "status": "EXACT_RATIONAL_STORED_POLYNOMIAL_CERTIFICATES",
        "all_certificates_pass": all(row["certificate_pass"] for row in certificates),
        "gas_polynomial_pieces": len(certificates),
        "native_depth_polynomials": sum(row["depth_polynomials_checked"] for row in certificates),
        "interpretation": "Binary64 stored coefficients/constants interpreted as exact rational numbers; ideal real reconstructions, not exact IVP, feedback tube, or exhaustive rounded-evaluation enclosure",
        "method": "Exact Fraction power-to-Bernstein conversion; nonnegative Bernstein basis partitions unity on normalized [0,1]",
        "constant_nuclear_reference": "exact rational sum of stored original gas0 species, not a separately rounded normalization scalar",
        "positive_margin_not_certified_would_mean": "insufficient Bernstein certificate, not automatic proof of a negative path",
        "temperature_domain_K": [2.7, 200000.],
        "certificates": certificates, "inputs": inputs,
        "native_rhs_calls": 0, "native_IVP_solves": 0, "historical_m2_reruns": 0,
        "code": [file_identity(__file__), file_identity(Path(__file__).with_name("bernstein_domain.py"))],
        "command_argv": sys.argv, "python": sys.version,
        "wall_seconds": time.perf_counter()-started}
    save_json(args.output, result)
    print(json.dumps({key: result[key] for key in ("status", "all_certificates_pass", "gas_polynomial_pieces", "native_depth_polynomials", "wall_seconds")}))
    if not result["all_certificates_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
