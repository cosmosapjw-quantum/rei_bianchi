#!/usr/bin/env python3
"""Independent R13 reference: primitive moments and Decimal monomial integrals.

No production or predecessor import. This runner is authored for one externally
metered execution under CONTRACT.json. Writing an existing result is forbidden.
The 160-digit reference and 1e-80 relative guard are numerical corroboration,
not an interval arithmetic proof.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import traceback


PRECISION = 160
RELATIVE_GUARD = Decimal("1e-80")
PHI_SERIES_THRESHOLD = Decimal("1e-12")
PHI_SERIES_STOP = Decimal("1e-150")
PHI_SERIES_MAX_TERMS = 512
ZERO = Fraction(0)
ONE = Fraction(1)


def exact(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, Fraction)):
        raise ValueError("Independent reference requires exact rational input")
    return Fraction(value)


def dec(value):
    if isinstance(value, Decimal):
        return value
    value = exact(value)
    return Decimal(value.numerator) / Decimal(value.denominator)


def safe_json(value):
    if isinstance(value, (Fraction, Decimal)):
        return str(value)
    if isinstance(value, dict):
        return {str(k): safe_json(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [safe_json(v) for v in value]
    return value


def short(value):
    text = json.dumps(safe_json(value), ensure_ascii=False, sort_keys=True)
    return text if len(text) <= 1200 else text[:1200] + "..."


class Checks:
    def __init__(self):
        self.counts = Counter()
        self.failure_counts = Counter()
        self.groups = []
        self.failures = []
        self.active = None

    def group(self, name):
        self.active = {"id": name, "components": 0, "failures": 0}
        self.groups.append(self.active)

    def expect(self, category, name, condition, actual=None, expected=None):
        self.counts[category] += 1
        if self.active is None:
            self.group("ungrouped")
        self.active["components"] += 1
        if not condition:
            self.failure_counts[category] += 1
            self.active["failures"] += 1
            if len(self.failures) < 100:
                self.failures.append({
                    "group": self.active["id"], "id": name,
                    "category": category,
                    "actual": short(actual), "expected": short(expected),
                })

    def equal(self, name, actual, expected, category="metadata"):
        self.expect(category, name, actual == expected, actual, expected)

    def rational(self, name, actual, expected, category="exact"):
        try:
            value = exact(actual)
        except Exception as exc:
            self.expect(category, name, False, repr(exc), str(expected))
            return
        self.expect(category, name, value == expected, value, expected)

    def rationals(self, name, actual, expected, category="exact"):
        if not isinstance(actual, (list, tuple)):
            self.expect("metadata", name + ".sequence", False, actual, "sequence")
            return
        self.equal(name + ".length", len(actual), len(expected))
        for i, (a, b) in enumerate(zip(actual, expected)):
            if isinstance(b, (list, tuple)):
                self.rationals(f"{name}[{i}]", a, b, category)
            else:
                self.rational(f"{name}[{i}]", a, b, category)

    def decimal_between(self, name, value, lower, upper, category="decimal"):
        low, high = dec(lower), dec(upper)
        scale = max(Decimal(1), abs(value), abs(low), abs(high))
        guard = RELATIVE_GUARD * scale
        self.expect(category, name + ".lower", value + guard >= low, value, low)
        self.expect(category, name + ".upper", value - guard <= high, value, high)

    def decimal_le(self, name, value, upper, category="decimal"):
        high = dec(upper)
        guard = RELATIVE_GUARD * max(Decimal(1), abs(value), abs(high))
        self.expect(category, name, value <= high + guard, value, high)

    def decimal_equal(self, name, a, b, category="decimal"):
        a, b = dec(a), dec(b)
        guard = RELATIVE_GUARD * max(Decimal(1), abs(a), abs(b))
        self.expect(category, name, abs(a - b) <= guard, a, b)


def phi_values(z):
    """Independent phi1/2/3: closed exp forms, with a frozen small-z branch."""
    z = dec(z)
    if not z:
        return Decimal(1), Decimal(1) / 2, Decimal(1) / 6
    if abs(z) >= PHI_SERIES_THRESHOLD:
        em1 = z.exp() - Decimal(1)
        return em1 / z, (em1 - z) / (z * z), (
            em1 - z - z * z / 2
        ) / (z * z * z)
    output = []
    for order, factorial in ((1, 1), (2, 2), (3, 6)):
        term = Decimal(1) / factorial
        total = term
        for n in range(1, PHI_SERIES_MAX_TERMS + 1):
            term *= z / Decimal(n + order)
            total += term
            if abs(term) <= PHI_SERIES_STOP * max(Decimal(1), abs(total)):
                output.append(total)
                break
        else:
            raise ArithmeticError("Independent small-z phi series did not terminate")
    return tuple(output)


def polynomial_step(e0, d, duration, coefficients):
    """Integrate Q0+Q1*u+Q2*u^2 using monomial moments, not B2 weights."""
    duration, d = dec(duration), dec(d)
    z = d * duration
    phi1, phi2, phi3 = phi_values(z)
    q0, q1, q2 = map(dec, coefficients)
    return z.exp() * e0 + (
        q0 * duration * phi1
        + q1 * duration * duration * phi2
        + 2 * q2 * duration * duration * duration * phi3
    )


@dataclass
class Model:
    record: dict
    q: Fraction = field(init=False)
    tau: Fraction = field(init=False)
    c: Fraction = field(init=False)
    d: Fraction = field(init=False)
    r0: Fraction = field(init=False)
    e0: Fraction = field(init=False)
    source: tuple = field(init=False)
    observation: tuple = field(init=False)
    gr: tuple = field(init=False)
    ge: tuple = field(init=False)
    f_cache: dict = field(default_factory=dict)
    base: list = field(default_factory=list)
    vertices: list = field(default_factory=list)
    refined: list = field(default_factory=list)
    cells: list = field(default_factory=list)
    e_decimal: list = field(default_factory=list)
    e_fraction: list | None = None

    def __post_init__(self):
        r = self.record
        self.q, self.tau, self.c, self.d = map(exact, (r["q"], r["tau"], r["c"], r["d"]))
        self.r0, self.e0 = map(exact, r["initial"])
        self.source = tuple(map(exact, r["source_knots"]))
        self.observation = tuple(map(exact, r["observation_knots"]))
        self.gr = tuple(tuple(map(exact, pair)) for pair in r["g_r"])
        self.ge = tuple(tuple(map(exact, pair)) for pair in r["g_e"])
        if not 0 <= self.q <= 1 or self.tau <= 0 or self.c < 0:
            raise ValueError("Independent valid-case parameter domain failed")
        if not self.r0 >= 0 or not self.e0 >= 0:
            raise ValueError("Independent initial nonnegativity failed")
        if any(a >= b for a, b in zip(self.source, self.source[1:])):
            raise ValueError("Independent source ordering failed")
        if any(a >= b for a, b in zip(self.observation, self.observation[1:])):
            raise ValueError("Independent observation ordering failed")
        if (self.source[0], self.source[-1]) != (self.observation[0], self.observation[-1]):
            raise ValueError("Independent clock endpoints differ")
        if len(self.gr) != len(self.source) - 1 or len(self.ge) != len(self.gr):
            raise ValueError("Independent source lengths differ")
        if any(len(pair) != 2 or min(pair) < 0 for pair in self.gr + self.ge):
            raise ValueError("Independent endpoint forcing domain failed")

    @property
    def t0(self):
        return self.source[0]

    @property
    def end(self):
        return self.source[-1]

    def power(self, n):
        return ONE if n == 0 else self.q ** n

    def kernel(self, t):
        return self.power(int((t - self.t0) // self.tau))

    def primitives(self, age):
        if age <= 0:
            return ZERO, ZERO
        n = int(age // self.tau)
        j0, j1 = ZERO, ZERO
        for k in range(n):
            weight = self.power(k)
            j0 += self.tau * weight
            j1 += self.tau * self.tau * weight * (Fraction(k) + Fraction(1, 2))
        kn = self.power(n)
        j0 += kn * (age - n * self.tau)
        j1 += kn * (age * age - (n * self.tau) ** 2) / 2
        return j0, j1

    def forcing(self, t):
        if t in self.f_cache:
            return self.f_cache[t]
        total = ZERO
        for j, (left, right) in enumerate(zip(self.source, self.source[1:])):
            alpha = self.gr[j][0]
            beta = (self.gr[j][1] - alpha) / (right - left)
            a0, a1 = self.primitives(t - left)
            b0, b1 = self.primitives(t - right)
            total += (alpha + beta * (t - left)) * (a0 - b0) - beta * (a1 - b1)
        self.f_cache[t] = total
        return total

    def rpoint(self, t):
        return self.kernel(t) * self.r0 + self.forcing(t)

    def source_value(self, family, t, cell_index=None):
        if cell_index is None:
            cell_index = min(bisect_right(self.source, t) - 1, len(self.gr) - 1)
        left, right = self.source[cell_index:cell_index + 2]
        pair = self.gr[cell_index] if family == "r" else self.ge[cell_index]
        return pair[0] + (pair[1] - pair[0]) * (t - left) / (right - left)

    def construct(self):
        count = int((self.end - self.t0) // self.tau)
        events = set(self.source) | set(self.observation)
        for k in range(count + 1):
            shifted_initial = self.t0 + k * self.tau
            if self.t0 <= shifted_initial <= self.end:
                events.add(shifted_initial)
            for knot in self.source:
                shifted = knot + k * self.tau
                if self.t0 <= shifted <= self.end:
                    events.add(shifted)
        self.base = sorted(events)
        self.cells = []
        self.vertices = []
        for left, right in zip(self.base, self.base[1:]):
            duration = right - left
            initial = self.kernel(left) * self.r0
            p0 = initial + self.forcing(left)
            pm = initial + self.forcing((left + right) / 2)
            pe = initial + self.forcing(right)
            p1 = (4 * pm - 3 * p0 - pe) / duration
            p2 = 2 * (p0 + pe - 2 * pm) / (duration * duration)
            breaks = [left, right]
            if p2:
                offset = -p1 / (2 * p2)
                if 0 < offset < duration:
                    self.vertices.append(left + offset)
                    breaks.insert(1, left + offset)
            for a, b in zip(breaks, breaks[1:]):
                shift, span = a - left, b - a
                coeff = (p0 + p1 * shift + p2 * shift * shift, p1 + 2 * p2 * shift, p2)
                bernstein = (
                    coeff[0],
                    coeff[0] + span * coeff[1] / 2,
                    coeff[0] + span * coeff[1] + span * span * coeff[2],
                )
                j = min(bisect_right(self.source, a) - 1, len(self.gr) - 1)
                ge = (self.source_value("e", a, j), self.source_value("e", b, j))
                whole = max(bernstein[0], bernstein[2], self.rpoint(b))
                self.cells.append({
                    "left": a, "right": b, "coefficients_local": coeff,
                    "bernstein": bernstein, "whole_R": whole, "ge_endpoints": ge,
                    "source_index": j,
                })
        self.vertices = sorted(set(self.vertices))
        self.refined = [self.t0] + [cell["right"] for cell in self.cells]
        self.e_decimal = [dec(self.e0)]
        self.e_fraction = [self.e0] if self.d == 0 else None
        for cell in self.cells:
            duration = cell["right"] - cell["left"]
            p0, p1, p2 = cell["coefficients_local"]
            e0, e1 = cell["ge_endpoints"]
            qpoly = (self.c * p0 + e0, self.c * p1 + (e1 - e0) / duration, self.c * p2)
            cell["Q_monomial"] = qpoly
            self.e_decimal.append(polynomial_step(self.e_decimal[-1], self.d, duration, qpoly))
            if self.e_fraction is not None:
                q0, q1, q2 = qpoly
                self.e_fraction.append(self.e_fraction[-1] + q0 * duration + q1 * duration**2 / 2 + q2 * duration**3 / 3)
        return self

    def e_at(self, t):
        if t == self.end:
            return self.e_decimal[-1]
        i = bisect_right(self.refined, t) - 1
        cell = self.cells[i]
        return polynomial_step(self.e_decimal[i], self.d, t - cell["left"], cell["Q_monomial"])


def check_matrix_shape(checks, name, matrix, rows, columns=2):
    checks.equal(name + ".rows", len(matrix), rows)
    for i, row in enumerate(matrix):
        checks.equal(f"{name}[{i}].columns", len(row), columns)


def check_case(checks, case, primary):
    model = Model(case).construct()
    cid = case["id"]
    result = primary["result"]
    checks.group(cid + "/input_and_events")
    checks.equal("input_identity", primary["input"], case)
    checks.rationals("requested_times", result["requested_times"], model.observation)
    checks.rationals("base_times", result["base_times"], model.base)
    checks.rationals("refined_times", result["refined_times"], model.refined)
    checks.rationals("vertex_times", result["vertex_times"], model.vertices)

    checks.group(cid + "/exact_primitives_and_polynomials")
    ex = result["exact"]
    checks.rationals("F_at_refined", ex["F_at_refined"], [model.forcing(t) for t in model.refined])
    checks.rationals("R_at_refined", ex["R_at_refined"], [model.rpoint(t) for t in model.refined])
    checks.rationals("kernel_at_refined", ex["kernel_at_refined"], [model.kernel(t) for t in model.refined])
    reported_cells = ex["R_quadratic_cells"]
    checks.equal("polynomial_cell_count", len(reported_cells), len(model.cells))
    for i, (reported, cell) in enumerate(zip(reported_cells, model.cells)):
        for key in ("left", "right", "whole_R"):
            checks.rational(f"cell{i}/{key}", reported[key], cell[key])
        for key in ("coefficients_local", "bernstein", "ge_endpoints"):
            checks.rationals(f"cell{i}/{key}", reported[key], cell[key])
        for k, value in enumerate(cell["bernstein"]):
            checks.expect("exact", f"cell{i}/B{k}_nonnegative", value >= 0, value, ">=0")
        p0, p1, p2 = cell["coefficients_local"]
        duration = cell["right"] - cell["left"]
        d0, d1 = p1, p1 + 2 * p2 * duration
        checks.expect("exact", f"cell{i}/monotone_after_vertex", d0 * d1 >= 0, [d0, d1], "same sign or zero")
        for theta in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)):
            u = duration * theta
            t = cell["left"] + u
            from_polynomial = p0 + p1 * u + p2 * u * u
            checks.rational(f"cell{i}/interior_R_{theta}", from_polynomial, model.rpoint(t))

    raw = result["raw"]
    lower = raw["refined_endpoints_lower"]
    upper = raw["refined_endpoints_upper"]
    whole = raw["refined_whole_cells_upper"]
    checks.group(cid + "/refined_endpoint_enclosures")
    check_matrix_shape(checks, "refined_lower", lower, len(model.refined))
    check_matrix_shape(checks, "refined_upper", upper, len(model.refined))
    check_matrix_shape(checks, "refined_whole", whole, len(model.cells))
    for i, t in enumerate(model.refined):
        r = model.rpoint(t)
        lo, hi = tuple(map(exact, lower[i])), tuple(map(exact, upper[i]))
        checks.expect("exact", f"point{i}/R_lower", lo[0] <= r, lo[0], r)
        checks.expect("exact", f"point{i}/R_upper", r <= hi[0], r, hi[0])
        checks.expect("exact", f"point{i}/E_order", lo[1] <= hi[1], lo[1], hi[1])
        checks.decimal_between(f"point{i}/E", model.e_decimal[i], lo[1], hi[1])
        if model.e_fraction is not None:
            true_e = model.e_fraction[i]
            checks.expect("exact", f"point{i}/E_exact_lower", lo[1] <= true_e, lo[1], true_e)
            checks.expect("exact", f"point{i}/E_exact_upper", true_e <= hi[1], true_e, hi[1])

    checks.group(cid + "/closed_cell_certificates")
    required_e_whole = []
    for i, cell in enumerate(model.cells):
        a, b = cell["left"], cell["right"]
        rmax = cell["whole_R"]
        reported_r, reported_e = map(exact, whole[i])
        checks.expect("coverage", f"cell{i}/whole_R", rmax <= reported_r, rmax, reported_r)
        eleft_upper = dec(upper[i][1])
        qmax = model.c * rmax + max(cell["ge_endpoints"])
        yend = polynomial_step(eleft_upper, model.d, b - a, (qmax, ZERO, ZERO))
        requirement = max(eleft_upper, yend)
        required_e_whole.append(requirement)
        checks.decimal_le(f"cell{i}/constant_majorant", requirement, reported_e, "coverage")
        for e in (0, 1):
            for component in (0, 1):
                endpoint_upper = exact(upper[i + e][component])
                checks.expect("coverage", f"cell{i}/point{e}_upper{component}",
                              endpoint_upper <= exact(whole[i][component]), endpoint_upper, whole[i][component])
        for theta in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)):
            t = a + (b - a) * theta
            checks.expect("coverage", f"cell{i}/sample_R_{theta}", model.rpoint(t) <= reported_r,
                          model.rpoint(t), reported_r)
            e_value = polynomial_step(model.e_decimal[i], model.d, t - a, cell["Q_monomial"])
            checks.decimal_le(f"cell{i}/sample_E_{theta}", e_value, reported_e, "coverage")

    checks.group(cid + "/observation_aggregation")
    obs_lower, obs_upper = raw["endpoints_lower"], raw["endpoints_upper"]
    obs_whole = raw["whole_cells_upper"]
    check_matrix_shape(checks, "observed_lower", obs_lower, len(model.observation))
    check_matrix_shape(checks, "observed_upper", obs_upper, len(model.observation))
    check_matrix_shape(checks, "observed_whole", obs_whole, len(model.observation) - 1)
    indices = [model.refined.index(t) for t in model.observation]
    for j, k in enumerate(indices):
        checks.rationals(f"obs{j}/lower_select", obs_lower[j], tuple(map(exact, lower[k])))
        checks.rationals(f"obs{j}/upper_select", obs_upper[j], tuple(map(exact, upper[k])))
    for j, (first, last) in enumerate(zip(indices, indices[1:])):
        checks.expect("coverage", f"obs{j}/gap_free_indices", 0 <= first < last <= len(model.cells),
                      [first, last], "ordered nonempty contiguous subcell range")
        for component in (0, 1):
            expected = max(exact(whole[k][component]) for k in range(first, last))
            checks.rational(f"obs{j}/max_component{component}", obs_whole[j][component], expected, "coverage")
        exact_rmax = max(cell["whole_R"] for cell in model.cells[first:last])
        checks.expect("coverage", f"obs{j}/exact_R_sup", exact_rmax <= exact(obs_whole[j][0]), exact_rmax, obs_whole[j][0])
        checks.decimal_le(f"obs{j}/E_majorant_coverage", max(required_e_whole[first:last]), obs_whole[j][1], "coverage")

    return model, {
        "id": cid,
        "base_cells": len(model.base) - 1,
        "vertex_insertions": len(model.vertices),
        "refined_cells": len(model.cells),
        "requested_times": [str(t) for t in model.observation],
        "exact_R_at_requested": [str(model.rpoint(t)) for t in model.observation],
        "Decimal_E_at_requested": [str(model.e_at(t)) for t in model.observation],
        "exact_E_at_refined_if_d_zero": None if model.e_fraction is None else [str(x) for x in model.e_fraction],
        "whole_E_reference": "constant majorant checked at endpoints; interior quarters additionally corroborated",
    }


def shared_parameters(a, b):
    return (a.q, a.tau, a.c, a.d, a.r0, a.e0, a.t0, a.end) == (
        b.q, b.tau, b.c, b.d, b.r0, b.e0, b.t0, b.end
    )


def source_relation(a, b, relation):
    """Return equality or ordering on every affine open source subcell."""
    if not shared_parameters(a, b):
        return False
    knots = sorted(set(a.source) | set(b.source))
    for left, right in zip(knots, knots[1:]):
        midpoint = (left + right) / 2
        ia = bisect_right(a.source, midpoint) - 1
        ib = bisect_right(b.source, midpoint) - 1
        for family in ("r", "e"):
            for t in (left, right):
                va = a.source_value(family, t, ia)
                vb = b.source_value(family, t, ib)
                if relation == "equal" and va != vb:
                    return False
                if relation == "le" and va > vb:
                    return False
    return True


def check_relations(checks, models):
    reports = []
    explicit = []
    for cid, model in models.items():
        relations = model.record.get("relations", [])
        if "relation" in model.record:
            relations = list(relations) + [model.record["relation"]]
        for relation in relations:
            explicit.append((cid, relation))
    for cid, relation in explicit:
        other = relation.get("other")
        kind = relation.get("kind")
        checks.group(cid + "/relation/" + str(other) + "/" + str(kind))
        checks.expect("metadata", "related_case_exists", other in models, other, list(models))
        if other not in models:
            continue
        a, b = models[cid], models[other]
        checks.expect("exact", "common_parameters", shared_parameters(a, b), cid, other)
        if kind == "same_function":
            matched = source_relation(a, b, "equal")
            checks.expect("exact", "same_piecewise_affine_function", matched, cid, other)
            for t in sorted(set(a.observation) | set(b.observation)):
                checks.rational(f"F_at_{t}", a.forcing(t), b.forcing(t))
                checks.rational(f"R_at_{t}", a.rpoint(t), b.rpoint(t))
                checks.decimal_equal(f"E_at_{t}", a.e_at(t), b.e_at(t))
        elif kind == "supremum_constant":
            matched = source_relation(a, b, "le")
            checks.expect("exact", "affine_forcing_le_constant", matched, cid, other)
            for family in (b.gr, b.ge):
                for j, pair in enumerate(family):
                    checks.expect("exact", f"sup_constant_pair{j}", pair[0] == pair[1], pair, "equal endpoints")
            for t in sorted(set(a.observation) | set(b.observation)):
                checks.expect("exact", f"R_order_at_{t}", a.rpoint(t) <= b.rpoint(t), a.rpoint(t), b.rpoint(t))
                checks.decimal_le(f"E_order_at_{t}", a.e_at(t), b.e_at(t))
        else:
            checks.expect("metadata", "supported_relation", False, kind, ["same_function", "supremum_constant"])
        reports.append({"case": cid, "other": other, "kind": kind})
    return reports


def run(root, primary_path, case_path):
    cases_bytes = case_path.read_bytes()
    primary_bytes = primary_path.read_bytes()
    case_data = json.loads(cases_bytes)
    primary_data = json.loads(primary_bytes)
    cases = case_data["cases"]
    records = primary_data["cases"]
    checks = Checks()
    checks.group("frozen_input_collection")
    ids = [case["id"] for case in cases]
    record_ids = [record["id"] for record in records]
    checks.equal("unique_input_case_ids", len(set(ids)), len(ids))
    checks.equal("unique_primary_case_ids", len(set(record_ids)), len(record_ids))
    checks.equal("case_order", record_ids, ids)
    primary_by_id = {record["id"]: record for record in records}
    models, summaries = {}, []
    for case in cases:
        model, summary = check_case(checks, case, primary_by_id[case["id"]])
        models[case["id"]] = model
        summaries.append(summary)
    relations = check_relations(checks, models)
    failures = sum(checks.failure_counts.values())
    for group in checks.groups:
        group["status"] = "PASS" if group["failures"] == 0 else "FAIL"
    return {
        "schema": "WU_R13_INDEPENDENT_REFERENCE_V1",
        "unit": "WU_AFFINE_FORCING_R13",
        "status": "PASS" if failures == 0 else "FAIL",
        "checks_total": len(checks.groups),
        "checks_passed": sum(group["failures"] == 0 for group in checks.groups),
        "checks_failed": sum(group["failures"] != 0 for group in checks.groups),
        "component_comparisons": sum(checks.counts.values()),
        "component_counts": dict(checks.counts),
        "component_failures": failures,
        "component_failure_counts": dict(checks.failure_counts),
        "checks": checks.groups,
        "failures": checks.failures,
        "failure_log_truncated": failures > len(checks.failures),
        "cases": summaries,
        "relations": relations,
        "input_identities": {
            "cases_sha256": hashlib.sha256(cases_bytes).hexdigest(),
            "primary_sha256": hashlib.sha256(primary_bytes).hexdigest(),
            "reference_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "numeric_reference": {
            "Decimal_precision": PRECISION,
            "relative_guard": str(RELATIVE_GUARD),
            "guard_fixed_before_execution": True,
            "phi_series_threshold": str(PHI_SERIES_THRESHOLD),
            "phi_series_stop": str(PHI_SERIES_STOP),
            "phi_series_max_terms": PHI_SERIES_MAX_TERMS,
            "meaning": "Numerical corroboration, not interval reference",
        },
        "independence": {
            "production_or_predecessor_imports": False,
            "F": "Exact primitive J0/J1 first age moment, no positive-overlap implementation",
            "grid": "Independent source translation, quadratic reconstruction, rational vertex generation",
            "E": "Decimal160 monomial phi1/phi2/phi3 integrals, no production Bernstein moment routine",
            "coverage": "Independent exact R supremum, constant E majorant, observation aggregation and interior quarters",
        },
        "physical_status": {
            "actual_HD_reactive_array": "INPUT_PENDING",
            "named_consumer_density_clock": "INPUT_PENDING",
            "HH_R10": "OFF", "production": "NOT_ISSUED", "L4_ready": False,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--cases", type=Path)
    parser.add_argument("--primary", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "raw" / "REFERENCE_RESULTS.json"
    if output.exists():
        raise SystemExit("Refusing to overwrite an existing reference result")
    case_path = args.cases or root / "verification" / "CASES.json"
    primary_path = args.primary or root / "raw" / "PRIMARY_RESULTS.json"
    try:
        with localcontext() as context:
            context.prec = PRECISION
            result = run(root, primary_path, case_path)
    except Exception as exc:
        result = {
            "schema": "WU_R13_INDEPENDENT_REFERENCE_V1",
            "unit": "WU_AFFINE_FORCING_R13", "status": "EXECUTION_FAILED",
            "error_class": type(exc).__name__, "error": str(exc),
            "traceback": traceback.format_exc(),
            "meaning": "Observed runner/input failure; no scientific success inferred",
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(safe_json(result), handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({
        "status": result["status"], "output": str(output),
        "checks_passed": result.get("checks_passed"),
        "checks_total": result.get("checks_total"),
        "component_comparisons": result.get("component_comparisons"),
        "component_failures": result.get("component_failures"),
    }))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
