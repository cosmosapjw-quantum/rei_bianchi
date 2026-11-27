"""Certify affine-predictor defect tubes, carrying endpoint error forward.

No solve_ivp, numerical ODE integration, quadrature of sampled residuals or
benchmarks. Saved nodes only choose the predictor. Whole-cell interval RHS
inclusion is the acceptance criterion. Failed inclusions are preserved.
"""
from __future__ import annotations

import argparse
from decimal import Context, Decimal, Inexact, ROUND_HALF_EVEN
import hashlib
import json
from pathlib import Path

from export_owner import canonical
from owner_interval import Arithmetic, FiniteOwner, Interval, decimal, serialize_evaluation, transport


def exact_difference(right, left):
    """Subtract finite decimal coordinates without ambient-context rounding."""
    exponent = min(right.as_tuple().exponent, left.as_tuple().exponent)
    digits = max(right.adjusted(), left.adjusted()) - exponent + 3
    if not 1 <= digits <= 10000:
        raise ValueError("EXACT_COORDINATE_DIFFERENCE_RANGE")
    context = Context(prec=digits, rounding=ROUND_HALF_EVEN)
    context.traps[Inexact] = True
    return context.subtract(right, left)


def _integer(value, lower, upper, label):
    if isinstance(value, bool) or not isinstance(value, int) or not lower <= value <= upper:
        raise ValueError(label)
    return value


def _points(values, length=8):
    if not isinstance(values, list) or len(values) != length:
        raise ValueError("STATE_VECTOR_SHAPE")
    return [decimal(value) for value in values]


def certify_cell(owner, x0, x1, p0, target, initial_box, *, max_inflations=8,
                 radius_floor=Decimal("1e-20"), inflation_factor=Decimal(2)):
    """Prove one local real IVP box or return an explicit noncertificate.

    Slope is a captured rounded Decimal point, part of the predictor's
    definition. Its actual endpoint is enclosed; it is not silently replaced
    by target. Initial_box is the carried enclosure, never a sampled reset.
    """
    a = owner.a
    if not all(isinstance(v, Decimal) and v.is_finite() for v in [x0, x1, *p0, *target]):
        raise ValueError("FINITE_DECIMAL_CELL_DATA")
    if len(p0) != len(target) or len(p0) != len(initial_box) or not p0:
        raise ValueError("CONSISTENT_CELL_DIMENSION")
    if x0 < 0 or x1 <= x0:
        raise ValueError("FORWARD_NONNEGATIVE_CELL")
    _integer(max_inflations, 1, 64, "INFLATION_COUNT_1_TO_64")
    if not radius_floor.is_finite() or radius_floor <= 0 or not inflation_factor.is_finite() or inflation_factor <= 1:
        raise ValueError("POSITIVE_RADIUS_AND_INFLATION_GREATER_THAN_ONE")
    h = exact_difference(x1, x0)
    point_h, time_box = a.point(h), Interval(Decimal(0), h)
    # The two roundings below define a legitimate affine predictor; they do
    # not claim exact interpolation. All subsequent uses are outward.
    slopes = [a.near.divide(a.near.subtract(right, left), h) for left, right in zip(p0, target)]
    slope_boxes = [a.point(v) for v in slopes]
    centers = [a.point(v) for v in p0]
    predictor_box = [a.add(center, a.multiply(time_box, slope)) for center, slope in zip(centers, slope_boxes)]
    predictor_end = [a.add(center, a.multiply(point_h, slope)) for center, slope in zip(centers, slope_boxes)]
    initial_error = [a.subtract(value, center) for value, center in zip(initial_box, centers)]
    radii = [a.up.add(a.up.multiply(inflation_factor, max(v.lo.copy_abs(), v.hi.copy_abs())), radius_floor)
             for v in initial_error]
    attempts = []
    common = {"x": [str(x0), str(x1)], "h": str(h), "predictor_origin": [str(v) for v in p0],
              "predictor_slope": [str(v) for v in slopes],
              "predictor_actual_endpoint": [v.strings() for v in predictor_end],
              "initial_state_box": [v.strings() for v in initial_box],
              "initial_error_box": [v.strings() for v in initial_error]}
    for attempt in range(max_inflations):
        radius_box = [Interval(r.copy_negate(), r) for r in radii]
        state_box = [a.add(p, r) for p, r in zip(predictor_box, radius_box)]
        try:
            evaluation = owner.evaluate(Interval(x0, x1), state_box)
        except (ValueError, ArithmeticError) as exc:
            attempts.append({"attempt": attempt, "radii": [str(v) for v in radii],
                             "status": "DOMAIN_OR_ARITHMETIC_REJECTED", "reason": str(exc)})
            return {**common, "status": "NOT_CERTIFIED", "attempts": attempts,
                    "reason": "candidate tube lacks regular outward domain"}
        rhs = evaluation["rhs"]
        if len(rhs) != len(p0):
            raise ValueError("RHS_DIMENSION_MISMATCH")
        defect = [a.subtract(value, slope) for value, slope in zip(rhs, slope_boxes)]
        image = [a.add(start, a.multiply(time_box, value)) for start, value in zip(initial_error, defect)]
        strict = [r.lo < value.lo and value.hi < r.hi for r, value in zip(radius_box, image)]
        attempts.append({"attempt": attempt, "radii": [str(v) for v in radii],
                         "image": [v.strings() for v in image], "strict_inclusion": strict})
        if all(strict):
            endpoint_error = [a.add(start, a.multiply(point_h, value)) for start, value in zip(initial_error, defect)]
            endpoint = [a.add(p, e) for p, e in zip(predictor_end, endpoint_error)]
            return {**common, "status": "FINITE_OWNER_CELL_ENCLOSED", "attempts": attempts,
                    "whole_cell_state_box": [v.strings() for v in state_box],
                    "defect_box": [v.strings() for v in defect],
                    "endpoint_state_box": [v.strings() for v in endpoint],
                    "endpoint_error_box": [v.strings() for v in endpoint_error],
                    "observables": serialize_evaluation(evaluation),
                    "method": "strict first-exit defect inclusion; locally Lipschitz finite owner"}
        # Preserve already enclosed components. Doubling all old radii on
        # every pass drives harmless passive-clock bounds outward and can
        # continually enlarge coupled sources faster than a neighbor catches
        # up. Every pass still recomputes and checks the complete box image.
        radii = [old if inside else max(old, a.up.add(a.up.multiply(inflation_factor,
                  max(value.lo.copy_abs(), value.hi.copy_abs())), radius_floor))
                 for old, value, inside in zip(radii, image, strict)]
    return {**common, "status": "NOT_CERTIFIED", "attempts": attempts,
            "reason": "strict inclusion not obtained within declared candidate iterations"}


def certify_request(request):
    if not isinstance(request, dict) or request.get("schema") != "PHYS77_ENCLOSURE_REQUEST_V1":
        raise ValueError("ENCLOSURE_REQUEST_SCHEMA")
    cfg = request["config"]
    precision = _integer(cfg["precision"], 16, 10000, "PRECISION_16_TO_10000")
    count = _integer(cfg["max_cells"], 1, 4096, "CELL_COUNT_1_TO_4096")
    attempts = _integer(cfg["max_inflations"], 1, 64, "INFLATION_COUNT_1_TO_64")
    floor, factor = decimal(cfg["radius_floor"]), decimal(cfg["inflation_factor"])
    owner = FiniteOwner(request["table"], precision)
    a = owner.a
    predictor = request["predictor"]
    if not isinstance(predictor["x"], list) or not 2 <= len(predictor["x"]) <= 4097:
        raise ValueError("PREDICTOR_NODE_COUNT")
    xs = [decimal(v) for v in predictor["x"]]
    states = [_points(v) for v in predictor["state"]]
    if len(xs) != len(states) or count >= len(xs) or any(r <= l for l, r in zip(xs, xs[1:])):
        raise ValueError("FORWARD_MATCHING_PREDICTOR_GRID")
    initial = request["initial"]
    initial_point = _points(initial["state"])
    if (initial.get("kind") != "exact_stored_initial_state" or decimal(initial["x"]) != 0
            or xs[0] != 0 or initial_point != states[0]):
        raise ValueError("EXACT_ORIGINAL_INITIAL_POINT_REQUIRED_NO_SAVED_ENDPOINT_RESET")
    digest = hashlib.sha256(canonical(request)).hexdigest()
    state_box = [a.point(v) for v in initial_point]
    initial_observables = owner.evaluate(a.zero, state_box)
    records, transport_cells = [], []
    for index in range(count):
        result = certify_cell(owner, xs[index], xs[index+1], states[index], states[index+1], state_box,
                              max_inflations=attempts, radius_floor=floor, inflation_factor=factor)
        result["index"] = index
        records.append(result)
        if result["status"] != "FINITE_OWNER_CELL_ENCLOSED":
            break
        state_box = [transport._interval(v) for v in result["endpoint_state_box"]]
        observables = result["observables"]
        transport_cells.append({"h": result["h"], "A": observables["A"], "P_m": observables["P_m"], "P_r": observables["P_r"],
                                "witness": {"scope": "entire_cell", "source_identity": owner.identity + ":" + digest,
                                            "method": result["method"], "locator": "cells/" + str(index)}})
    passed = len(transport_cells) == count
    response = None
    if transport_cells:
        response = transport.propagate(transport_cells, initial_observables["S"].strings(),
                    {"scope": "initial_value", "source_identity": owner.identity + ":" + digest,
                     "method": "outward source evaluation at the declared exact stored initial point",
                     "locator": "initial_observables/S"}, precision)
    return {"schema": "PHYS77_FINITE_OWNER_ENCLOSURE_RESULT_V1",
            "status": "PASS_REQUESTED_PREFIX" if passed else "NOT_CERTIFIED_REQUESTED_PREFIX",
            "request_sha256": digest, "table_sha256": owner.identity,
            "case_id": request["table"]["provenance"]["case_identity"]["case_id"],
            "scope": "declared captured-coefficient exact-real IVP at the exact initial point in this request",
            "provenance": "source mapping is supplied by the hash-bound exporter preparation receipt; hashes alone do not prove historical equality",
            "requested_cells": count, "enclosed_cells": len(transport_cells),
            "covered_x": [str(xs[0]), str(xs[len(transport_cells)])],
            "initial_observables": serialize_evaluation(initial_observables), "cells": records,
            "transport_connection": {"whole_cell_inputs_computed_by_this_producer": bool(transport_cells),
                                     "consumer": response},
            "full_history_certificate": False, "angular_continuum_certificate": False,
            "momentum_continuum_certificate": False, "past_machine_trajectory_certificate": False,
            "new_ODE_solves": 0, "old_ODE_replays": 0, "NCP_jobs": 0, "benchmark_runs": 0,
            "HH_R10": "OFF", "production_admission": "NOT_ISSUED"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = certify_request(json.loads(args.request.read_text()))
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps({key: result[key] for key in ("status", "case_id", "enclosed_cells", "covered_x")}))
    raise SystemExit(0 if result["status"] == "PASS_REQUESTED_PREFIX" else 2)
