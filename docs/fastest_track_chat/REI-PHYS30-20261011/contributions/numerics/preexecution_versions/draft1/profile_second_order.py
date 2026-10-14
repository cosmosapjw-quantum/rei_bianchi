#!/usr/bin/env python3
"""PHYS30: one preregistered cached-coefficient calculation, no physical calls.

The two paths are (A) an affine update of retained PHYS29 coefficients and
(B) a separately implemented bivariate quotient series of the profile law.
The only physical k, k', k'' values are read from four retained PHYS29 nodes.
This module is prepared without import/main execution. The owner freezes it
and authorizes the one first main; a different operator owns the one replay.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from fractions import Fraction
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import traceback


TASK = "REI-PHYS30-20261011"
ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = "contributions/numerics/PROTOCOL.json"
FREEZE_PATH = "contributions/numerics/PREEXECUTION_FROZEN.json"
EXPECTED_PROTOCOL_SHA256 = "PROTOCOL_SHA256_TO_BE_SET_BEFORE_OWNER_FREEZE"
EXPECTED_INPUTS = (
    ("inputs/PHYS29/contributions/numerics/SECOND_ORDER_FIRST.json", 137037,
     "40d686d2646ac7dbaff1bd768a789fcfdbaf5043a16b26512c42ffbedbdd8d6f"),
    ("inputs/PHYS29/contributions/numerics/PROTOCOL.json", 16527,
     "6ab5d3c488a00ebfb868e4d4e83d98a2fe1db9479956b587f673d9d9b86e7573"),
)
POWERS = ((0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2))
COEFFICIENT_FIELDS = (
    "response_s-4", "B_s-4_eV-1", "C_s-4_eV-2",
    "Fdd_s-4_eV-2", "FdW_s-4_eV-3", "FWW_s-4_eV-4",
    "c_eV", "d_dimensionless",
)
KERNEL_FIELDS = ("k_s-4", "k_prime_s-4_eV-1", "k_second_s-4_eV-2")
BRANCHES = ("upper_root", "lower_root")
PROFILE_SPECS = {
    "uniform": {
        "density": "1/2 on [-1,1], zero elsewhere",
        "segments": [{"lo": "-1", "hi": "1", "coefficients": ["1/2"]}],
        "mu2": "1/3",
    },
    "triangular": {
        "density": "1-|z| on [-1,1], zero elsewhere",
        "segments": [
            {"lo": "-1", "hi": "0", "coefficients": ["1", "1"]},
            {"lo": "0", "hi": "1", "coefficients": ["1", "-1"]},
        ],
        "mu2": "1/6",
    },
}
ZERO_DEBITS = (
    "new_physical_kernel_evaluations", "new_physical_kernel_derivative_evaluations",
    "new_physical_energy_nodes", "new_physical_root_searches",
    "new_physical_root_iterations_or_corrections", "old_PHYS19_through_PHYS29_imports",
    "old_PHYS19_through_PHYS29_main_invocations", "old_suite_replays",
    "quadrature_evaluations", "finite_difference_evaluations", "width_sweeps",
    "derivative_sign_campaigns", "native_runs", "gas_IVP_runs", "dense_LP_runs",
    "new_physical_data_or_independent_physics_credit",
)


def encode(value):
    """JSON representation with all Decimal/Fraction values retained as strings."""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Fraction):
        return str(value.numerator) + "/" + str(value.denominator)
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(relative):
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or str(path) != relative:
        raise ValueError("Non-canonical or escaping frozen path: " + relative)
    candidate = ROOT / relative
    if candidate.is_symlink() or not candidate.is_file():
        raise ValueError("Frozen member is not a regular file: " + relative)
    if not candidate.resolve().is_relative_to(ROOT):
        raise ValueError("Frozen member escapes project root: " + relative)
    return candidate


class Checks:
    """A check is a preregistered semantic group; all component rows are retained."""

    def __init__(self, tolerance):
        self.tolerance = tolerance
        self.rows = []

    def record(self, name, passed, **evidence):
        if any(row["name"] == name for row in self.rows):
            raise ValueError("Duplicate check identifier: " + name)
        self.rows.append({"name": name, "passed": bool(passed), **evidence})

    def numeric(self, name, comparisons):
        details = []
        for component, actual, expected, fixed_scale in comparisons:
            actual, expected = Decimal(actual), Decimal(expected)
            scale = (max(Decimal(1), abs(actual), abs(expected))
                     if fixed_scale is None else Decimal(fixed_scale))
            if not all(item.is_finite() for item in (actual, expected, scale)) or scale <= 0:
                raise ValueError("Non-finite comparison or invalid scale: " + component)
            error = abs(actual - expected) / scale
            details.append({
                "component": component, "actual": actual, "expected": expected,
                "scale": scale, "scale_rule": "supplied_fixed" if fixed_scale is not None
                else "max(1,abs(actual),abs(expected))",
                "absolute_scaled_error": error, "tolerance": self.tolerance,
                "passed": error <= self.tolerance,
            })
        if not details:
            raise ValueError("Empty numeric check group: " + name)
        self.record(name, all(item["passed"] for item in details),
                    arithmetic="Decimal80", components=details,
                    maximum_scaled_error=max(item["absolute_scaled_error"] for item in details))

    def exact(self, name, comparisons):
        details = [{"component": key, "actual": actual, "expected": expected,
                    "passed": actual == expected}
                   for key, actual, expected in comparisons]
        if not details:
            raise ValueError("Empty exact check group: " + name)
        self.record(name, all(item["passed"] for item in details),
                    arithmetic="Exact Fraction or exact discrete identity", components=details)


class Poly2:
    """Six ordinary coefficients; division uses a triangular recurrence.

    This implementation is new. It does not import the PHYS29 BiSeries2 class
    or use its geometric inverse-series algorithm, nor call the affine path.
    Coefficients are entirely Decimal or entirely Fraction, never binary float.
    """

    def __init__(self, coefficients):
        if len(coefficients) != 6:
            raise ValueError("Poly2 needs six ordinary coefficients")
        kind = type(coefficients[0])
        if kind not in (Decimal, Fraction) or not all(type(x) is kind for x in coefficients):
            raise TypeError("Poly2 must use homogeneous Decimal or Fraction coefficients")
        self.v = tuple(coefficients)
        self.zero = self.v[0] * 0

    def lift(self, other):
        if isinstance(other, Poly2):
            if type(other.zero) is not type(self.zero):
                raise TypeError("Mixed coefficient fields")
            return other
        base = self.zero + other
        return Poly2((base, self.zero, self.zero, self.zero, self.zero, self.zero))

    def __add__(self, other):
        other = self.lift(other)
        return Poly2(tuple(a + b for a, b in zip(self.v, other.v)))

    __radd__ = __add__

    def __neg__(self):
        return Poly2(tuple(-x for x in self.v))

    def __sub__(self, other):
        return self + (-self.lift(other))

    def __rsub__(self, other):
        return self.lift(other) + (-self)

    def __mul__(self, other):
        b = self.lift(other).v
        a = self.v
        return Poly2((
            a[0]*b[0],
            a[1]*b[0] + a[0]*b[1],
            a[2]*b[0] + a[0]*b[2],
            a[3]*b[0] + a[1]*b[1] + a[0]*b[3],
            a[4]*b[0] + a[1]*b[2] + a[2]*b[1] + a[0]*b[4],
            a[5]*b[0] + a[2]*b[2] + a[0]*b[5],
        ))

    __rmul__ = __mul__

    def __truediv__(self, other):
        b = self.lift(other).v
        a = self.v
        if b[0] == 0:
            raise ZeroDivisionError("Poly2 denominator has zero constant coefficient")
        q0 = a[0]/b[0]
        q1 = (a[1] - b[1]*q0)/b[0]
        q2 = (a[2] - b[2]*q0)/b[0]
        q3 = (a[3] - b[1]*q1 - b[3]*q0)/b[0]
        q4 = (a[4] - b[1]*q2 - b[2]*q1 - b[4]*q0)/b[0]
        q5 = (a[5] - b[2]*q2 - b[5]*q0)/b[0]
        return Poly2((q0, q1, q2, q3, q4, q5))

    def __rtruediv__(self, other):
        return self.lift(other)/self

    def as_mapping(self):
        return {str(power): value for power, value in zip(POWERS, self.v)}


def density_moments(profile_name, checks, counts):
    """Integrate specified linear polynomials by exact rational antiderivatives."""
    spec = PROFILE_SPECS[profile_name]
    segments = [(Fraction(item["lo"]), Fraction(item["hi"]),
                 tuple(Fraction(x) for x in item["coefficients"]))
                for item in spec["segments"]]
    partition = (segments[0][0] == -1 and segments[-1][1] == 1
                 and all(lo < hi for lo, hi, _ in segments)
                 and all(left[1] == right[0] for left, right in zip(segments, segments[1:])))
    nonnegative = all(len(c) <= 2 and all(sum((x*z**i for i, x in enumerate(c)), Fraction(0)) >= 0
                                        for z in (lo, hi)) for lo, hi, c in segments)
    symmetric = all(any(other_lo == -hi and other_hi == -lo
                        and other_c == tuple(x*(-1)**i for i, x in enumerate(c))
                        for other_lo, other_hi, other_c in segments)
                    for lo, hi, c in segments)
    checks.record("profile__"+profile_name+"__density_definition_exact",
                  partition and nonnegative and symmetric,
                  exact_partition_minus1_to1=partition, nonnegative_linear_segments=nonnegative,
                  reflection_symmetry=symmetric, density=spec["density"])
    moments = []
    for n in (0, 1, 2):
        value = sum((coefficient*(hi**(i+n+1)-lo**(i+n+1))/Fraction(i+n+1)
                     for lo, hi, coefficients in segments
                     for i, coefficient in enumerate(coefficients)), Fraction(0))
        moments.append(value)
        counts["exact_profile_polynomial_moment_integrals"] += 1
    checks.exact("profile__"+profile_name+"__moments_exact", (
        ("mass", moments[0], Fraction(1)), ("mean_z", moments[1], Fraction(0)),
        ("mu2", moments[2], Fraction(spec["mu2"])),
    ))
    return {"definition": spec, "mass": moments[0], "mean_z": moments[1],
            "mu2": moments[2], "integration": "Exact polynomial antiderivative, not quadrature"}


def retained_branch(branch, source):
    old = source["second_order"]["jet_chain"][branch]
    law = old["law"]
    endpoint_label, center_label = (("a", "v_star") if branch == "upper_root"
                                    else ("b", "u_zero"))
    kernel = source["joint_kernel_outputs"]["jet"]
    pair = {"endpoint": tuple(Decimal(kernel[endpoint_label][field]) for field in KERNEL_FIELDS),
            "center": tuple(Decimal(kernel[center_label][field]) for field in KERNEL_FIELDS)}
    return {"s": law["s"], "R": Decimal(law["R_eV"]),
            "w": Decimal(law["stored_W_eV2"]), "endpoint": Decimal(law["anchor_eV"]),
            "center": Decimal(law["center_eV"]), "mean": Decimal(source["constants"]["mean_eV"]),
            "p": Decimal(law["p_endpoint"]), "q": Decimal(law["p_center"]),
            "D": Decimal(law["denominator_eV2"]), "pair": pair, "old": old,
            "endpoint_label": endpoint_label, "center_label": center_label}


def affine_update(data, mu2, curvature, slope):
    """Path A: retained uniform coefficients plus the analytic affine update."""
    old = data["old"]
    one_third = Decimal(1)/Decimal(3)
    C = Decimal(old["C_s-4_eV-2"])
    fields = {key: Decimal(old[key]) for key in COEFFICIENT_FIELDS}
    fields["Fdd_s-4_eV-2"] = Decimal(old["Fdd_s-4_eV-2"]) + (mu2-one_third)*(curvature-2*C)
    fields["d_dimensionless"] = Decimal(old["d_dimensionless"]) + (mu2-one_third)*slope
    fixed_terms = {key: Decimal(value) for key, value in old["Fdd_decomposition_s-4_eV-2"].items()
                   if key not in ("uniform_band_averaging", "center_variance_V_second")}
    terms = {"profile_band_averaging": mu2*curvature,
             "center_variance_V_second": -2*mu2*C, **fixed_terms}
    d_terms = {key: -value/(2*C) for key, value in terms.items()}
    for key in ("implicit_root_delta_W_cross", "implicit_root_W_curvature"):
        d_terms[key] = Decimal(old["d_decomposition_dimensionless"][key])
    return {**fields, "calH_curvature_s-4_eV-2": curvature,
            "S_profile_slope_dimensionless": slope, "mu2": mu2,
            "Fdd_decomposition_s-4_eV-2": terms,
            "d_decomposition_dimensionless": d_terms,
            "d_profile_independent_geometry_sum": sum((-value/(2*C) for value in fixed_terms.values()), Decimal(0)),
            "d_profile_increment_from_uniform": (mu2-one_third)*slope,
            "interpretation": "Retained finite point and retained nonzero A-level; no root correction"}


def response_series(s, r, w, endpoint, center_base, mean, pair, mu2):
    """Path B: direct ordinary-coefficient law; no cached root/partial helper.

    All dependence is constructed from radius R-delta and V=w+eta-mu2*delta^2.
    k/k'/k'' tuples are already cached; forming their local polynomial is not a
    call to the physical kernel or any derivative evaluator.
    """
    zero, one = r*0, r/r
    delta = Poly2((zero, one, zero, zero, zero, zero))
    physical_W = Poly2((w, zero, one, zero, zero, zero))
    radius = r-delta
    delta_squared = delta*delta
    variance = physical_W-mu2*delta_squared
    e = endpoint+s*delta
    x = mean+s*variance/radius
    denominator = radius*radius+variance
    p = variance/denominator
    q = radius*radius/denominator
    u_e, u_x = e-endpoint, x-center_base
    ke, kep, kepp = pair["endpoint"]
    kx, kxp, kxpp = pair["center"]
    averaged_e = ke+kep*u_e+(kepp/2)*(u_e*u_e+mu2*delta_squared)
    averaged_x = kx+kxp*u_x+(kxpp/2)*(u_x*u_x+mu2*delta_squared)
    response = p*averaged_e+q*averaged_x
    numerator = variance*averaged_e+radius*radius*averaged_x
    f = response.v
    if f[2] == 0:
        raise ZeroDivisionError("Independent series has zero W coefficient")
    c = -f[1]/f[2]
    d = -(f[3]+f[4]*c+f[5]*c*c)/f[2]
    mass = p+q
    first_moment = p*e+q*x
    physical_variance = p*(e-mean)*(e-mean)+q*(x-mean)*(x-mean)+mu2*delta_squared
    return {
        "response_s-4": f[0], "B_s-4_eV-1": f[1], "C_s-4_eV-2": f[2],
        "Fdd_s-4_eV-2": 2*f[3], "FdW_s-4_eV-3": f[4], "FWW_s-4_eV-4": 2*f[5],
        "c_eV": c, "d_dimensionless": d,
        "response_ordinary_series": response.as_mapping(),
        "numerator_ordinary_series": numerator.as_mapping(),
        "denominator_ordinary_series": denominator.as_mapping(),
        "moment_series": {"mass": mass.as_mapping(), "mean_eV": first_moment.as_mapping(),
                          "physical_variance_eV2": physical_variance.as_mapping()},
        "zero_width_endpoint_displacement_eV": u_e.v[0],
        "zero_width_center_displacement_eV": u_x.v[0],
    }


def moment_comparisons(series, mean, w):
    zero, one = w*0, mean/mean
    expected = {
        "mass": (one, zero, zero, zero, zero, zero),
        "mean_eV": (mean, zero, zero, zero, zero, zero),
        "physical_variance_eV2": (w, zero, one, zero, zero, zero),
    }
    return [(name+"__"+str(power), series["moment_series"][name][str(power)], target)
            for name, values in expected.items() for power, target in zip(POWERS, values)]


def numerator_comparisons(series, fields, r, den, mu2, scales):
    """QF identities with the retained A. Scales follow physical dimensions."""
    A, B, C, K, M, N = (fields[key] for key in COEFFICIENT_FIELDS[:6])
    n = series["numerator_ordinary_series"]
    S0, S1, S2 = scales[:3]
    return [
        ("N00=QA", n[str((0, 0))], den*A, S0*18*18),
        ("N10=QB-2RA", n[str((1, 0))], den*B-2*r*A, S0*18),
        ("N01=QC+A", n[str((0, 1))], den*C+A, S0),
        ("Ndd=QK-4RB+2(1-mu2)A", 2*n[str((2, 0))], den*K-4*r*B+2*(1-mu2)*A, S0),
        ("NdW=QM-2RC+B", n[str((1, 1))], den*M-2*r*C+B, S1),
        ("NWW=QN+2C", 2*n[str((0, 2))], den*N+2*C, S2),
    ]


def validate_physical(profile, branch, data, affine, series, mu2, checks, scales):
    prefix = "physical__"+profile+"__"+branch+"__"
    field_scales = (scales[0], scales[1], scales[2], scales[2], scales[3], scales[4], None, None)
    checks.numeric(prefix+"affine_vs_bivariate", [
        (key, affine[key], series[key], scale) for key, scale in zip(COEFFICIENT_FIELDS, field_scales)])
    checks.numeric(prefix+"moment_series", [(key, actual, expected, None)
                                           for key, actual, expected in moment_comparisons(series, data["mean"], data["w"])])
    checks.numeric(prefix+"nonzero_A_numerator_identities",
                   numerator_comparisons(series, affine, data["R"], data["D"], mu2, scales))
    n = series["numerator_ordinary_series"]
    A = affine["response_s-4"]
    c = affine["c_eV"]
    denominator = n[str((0, 1))]-A
    c_numerator = -(n[str((1, 0))]+2*data["R"]*A)/denominator
    d_numerator = -(2*n[str((2, 0))]+2*n[str((1, 1))]*c
                    +2*n[str((0, 2))]*c*c-2*(1-mu2)*A)/(2*denominator)
    checks.numeric(prefix+"residual_preserving_root_coefficients", (
        ("c", c_numerator, c, None), ("d", d_numerator, affine["d_dimensionless"], None)))
    C, calH = affine["C_s-4_eV-2"], affine["calH_curvature_s-4_eV-2"]
    Kterms, dterms = affine["Fdd_decomposition_s-4_eV-2"], affine["d_decomposition_dimensionless"]
    checks.numeric(prefix+"complete_decomposition", (
        ("sum_K", sum(Kterms.values(), Decimal(0)), affine["Fdd_s-4_eV-2"], scales[2]),
        ("sum_d", sum(dterms.values(), Decimal(0)), affine["d_dimensionless"], None),
        ("d_variance=mu2", dterms["center_variance_V_second"], mu2, None),
        ("d_average=-mu2H/(2C)", dterms["profile_band_averaging"], -mu2*calH/(2*C), None)))
    checks.numeric(prefix+"root_coefficient_cancellation", (
        ("delta", affine["B_s-4_eV-1"]+C*c, Decimal(0), scales[1]),
        ("delta_squared_twice", affine["Fdd_s-4_eV-2"]+2*affine["FdW_s-4_eV-3"]*c
         +affine["FWW_s-4_eV-4"]*c*c+2*C*affine["d_dimensionless"], Decimal(0), scales[2])))
    return {"A_level_retained_s-4": A, "series_constant_minus_retained_A_s-4": series["response_s-4"]-A,
            "c_from_residual_preserving_numerator_eV": c_numerator,
            "d_from_residual_preserving_numerator": d_numerator,
            "Qdd_dimensionless": 2*(1-mu2),
            "physical_residual_too_small_to_test_A_term_omission_at_current_tolerance": True,
            "nonzero_A_term_is_instead_falsifiably_tested_by_exact_A1_quadratic_toy": True}


def exact_toy_pair(data):
    """Generic exact quadratic coefficient tuple; never calls a physical kernel."""
    r, w, endpoint, mean = (Fraction(data[key]) for key in ("R", "w", "endpoint", "mean"))
    s = data["s"]
    center = mean+s*w/r
    pair = {"endpoint": ((endpoint-mean)**2-w+1, 2*(endpoint-mean), Fraction(2)),
            "center": ((center-mean)**2-w+1, 2*(center-mean), Fraction(2))}
    return {"s": s, "r": r, "w": w, "endpoint": endpoint, "center": center,
            "mean": mean, "pair": pair, "den": r*r+w}


def quadratic_toy(profile, branch, data, mu2, checks, counts):
    """A=1 makes omission of the residual term detectable by exact equality."""
    prefix = "toy__"+profile+"__"+branch+"__"
    counts["exact_nonzero_A_quadratic_profile_branches"] += 1
    series = response_series(data["s"], data["r"], data["w"], data["endpoint"], data["center"],
                             data["mean"], data["pair"], mu2)
    counts["exact_toy_bivariate_response_series"] += 1
    counts["exact_toy_moment_series"] += 1
    expected = dict(zip(COEFFICIENT_FIELDS, map(Fraction, (1, 0, 1, 0, 0, 0, 0, 0))))
    p, q = data["w"]/data["den"], data["r"]**2/data["den"]
    calH = p*data["pair"]["endpoint"][2]+q*data["pair"]["center"][2]
    S = 1-calH/(2*expected["C_s-4_eV-2"])
    d_avg, d_V = -mu2*calH/(2*expected["C_s-4_eV-2"]), mu2
    checks.exact(prefix+"coefficients_and_profile_split_exact", [
        (key, series[key], value) for key, value in expected.items()] + [
        ("curvature_H", calH, Fraction(2)), ("profile_slope_S", S, Fraction(0)),
        ("d_average", d_avg, -mu2), ("d_V", d_V, mu2),
        ("d_average_plus_d_V", d_avg+d_V, Fraction(0))])
    checks.exact(prefix+"moment_series_exact", moment_comparisons(series, data["mean"], data["w"]))
    n = series["numerator_ordinary_series"]
    A = Fraction(1)
    nw_minus_A = n[str((0, 1))]-A
    c_numerator = -(n[str((1, 0))]+2*data["r"]*A)/nw_minus_A
    d_numerator = -(2*n[str((2, 0))]+2*n[str((1, 1))]*c_numerator
                    +2*n[str((0, 2))]*c_numerator*c_numerator-2*(1-mu2)*A)/(2*nw_minus_A)
    d_omit_A_term = -(2*n[str((2, 0))])/(2*nw_minus_A)
    numerator_rows = numerator_comparisons(series, expected, data["r"], data["den"], mu2,
                                           (Fraction(1),)*5)
    checks.exact(prefix+"nonzero_level_numerator_exact", [
        (key, actual, target) for key, actual, target, _ in numerator_rows] + [
        ("c_with_A1", c_numerator, Fraction(0)), ("d_with_A1", d_numerator, Fraction(0)),
        ("d_when_AQdd_omitted", d_omit_A_term, -(1-mu2)/data["den"]),
        ("omitting_AQdd_changes_d", d_omit_A_term != 0, True)])
    return {"definition": "ktoy(E)=(E-m)^2-w+1, Ftoy(delta,w+eta)=1+eta exactly",
            "arithmetic": "Exact Fraction; dimensionless analytic toy, no physical units or kernel calls",
            "A_level": A, "mu2": mu2, "series": series,
            "calH": calH, "S": S, "d_average": d_avg, "d_V": d_V,
            "c_residual_preserving": c_numerator, "d_residual_preserving": d_numerator,
            "d_with_AQdd_term_omitted": d_omit_A_term,
            "negative_control": "Wrong omission is nonzero and fails the exact known d=0 limit"}


def preflight(result, checks, counts, context):
    protocol_bytes = safe_path(PROTOCOL_PATH).read_bytes()
    protocol = json.loads(protocol_bytes)
    checks.record("protocol_identity", sha256(protocol_bytes) == EXPECTED_PROTOCOL_SHA256,
                  actual_sha256=sha256(protocol_bytes), expected_sha256=EXPECTED_PROTOCOL_SHA256)
    input_records = []
    payloads = {}
    for relative, expected_size, expected_sha in EXPECTED_INPUTS:
        content = safe_path(relative).read_bytes()
        actual = {"path": relative, "bytes": len(content), "sha256": sha256(content)}
        actual["passed"] = len(content) == expected_size and actual["sha256"] == expected_sha
        input_records.append(actual)
        payloads[relative] = content
    checks.record("retained_input_identities", all(item["passed"] for item in input_records), members=input_records)
    freeze_bytes = safe_path(FREEZE_PATH).read_bytes()
    freeze = json.loads(freeze_bytes)
    freeze_members = []
    paths = set()
    for member in freeze["files"]:
        path = member["path"]
        if path == FREEZE_PATH or path in paths:
            raise ValueError("Freeze repeats or binds itself")
        paths.add(path)
        content = safe_path(path).read_bytes()
        good = len(content) == member["bytes"] and sha256(content) == member["sha256"]
        freeze_members.append({"path": path, "bytes": len(content), "sha256": sha256(content), "passed": good})
    required = set(protocol["required_frozen_paths"])
    checks.record("frozen_candidate_identities", required.issubset(paths)
                  and all(item["passed"] for item in freeze_members),
                  required_paths=sorted(required), missing_paths=sorted(required-paths),
                  freeze_sha256=sha256(freeze_bytes), members=freeze_members)
    source = json.loads(payloads[EXPECTED_INPUTS[0][0]])
    old_protocol = json.loads(payloads[EXPECTED_INPUTS[1][0]])
    state_ok = (source["task"] == "REI-PHYS29-20261011" and source["decimal_precision"] == 80
                and source["summary"]["all_pass"] is True and source["summary"]["total_checks"] == 238
                and source["summary"]["passed"] == 238 and source["summary"]["failed"] == 0
                and source["physical_admission"] == "HOLD"
                and source["identity_sha256"]["contributions/numerics/PROTOCOL.json"] == EXPECTED_INPUTS[1][2]
                and old_protocol["tolerances"]["algebra_and_two_expression_scaled"] == "1e-60"
                and old_protocol["arithmetic"]["precision_decimal_digits"] == 80)
    checks.record("PHYS29_authoritative_cached_state", state_ok,
                  source_task=source["task"], stored_summary=source["summary"],
                  note="Stored prior outcome read only; no old predicate reevaluation or old main/import")
    constants = source["constants"]
    nodes = source["energy_nodes_eV"]
    geometry_ok = (constants["support_eV"] == ["13.61", "24.58"] and constants["mean_eV"] == "18"
                   and constants["L_eV"] == "4.39" and constants["H_eV"] == "6.58"
                   and tuple(nodes) == ("a", "v_star", "u_zero", "b")
                   and nodes["a"] == "13.61" and nodes["b"] == "24.58")
    for branch, endpoint_label, center_label in (("upper_root", "a", "v_star"), ("lower_root", "b", "u_zero")):
        law = source["second_order"]["jet_chain"][branch]["law"]
        geometry_ok = (geometry_ok and law["stored_W_eV2"] == constants["stored_PHYS26_root_strings"][branch]
                       and law["anchor_eV"] == nodes[endpoint_label] and law["center_eV"] == nodes[center_label])
    checks.record("retained_geometry_and_node_contract", geometry_ok,
                  support_eV=constants["support_eV"], mean_eV=constants["mean_eV"], nodes_eV=nodes,
                  stored_root_strings=constants["stored_PHYS26_root_strings"])
    numbers = [Decimal(source["joint_kernel_outputs"]["jet"][label][key])
               for label in nodes for key in KERNEL_FIELDS]
    numbers.extend(Decimal(source["second_order"]["jet_chain"][branch][key])
                   for branch in BRANCHES for key in COEFFICIENT_FIELDS)
    finite_and_simple = (all(value.is_finite() for value in numbers)
                         and all(Decimal(source["second_order"]["jet_chain"][b]["C_s-4_eV-2"]) > 0 for b in BRANCHES))
    checks.record("retained_values_finite_and_simple", finite_and_simple,
                  finite_stored_scalar_count=len(numbers), positive_retained_C=True if finite_and_simple else False,
                  meaning="Required finite positive variance slope; no d sign/profile-order criterion")
    checks.record("Decimal_context", context.prec == 80 and context.rounding == ROUND_HALF_EVEN,
                  precision=context.prec, rounding=context.rounding)
    result["input_identities"] = input_records
    result["preexecution_freeze_identity"] = {"path": FREEZE_PATH, "bytes": len(freeze_bytes),
                                              "sha256": sha256(freeze_bytes)}
    result["protocol_identity"] = {"path": PROTOCOL_PATH, "bytes": len(protocol_bytes),
                                    "sha256": sha256(protocol_bytes)}
    if not all(row["passed"] for row in checks.rows):
        raise RuntimeError("Preflight failure; no profile or cached-coefficient algebra executed")
    counts["retained_physical_node_records_loaded"] = 4
    counts["retained_physical_k_kprime_ksecond_values_loaded"] = 12
    return source, protocol


def science(result, checks, counts, context):
    source, protocol = preflight(result, checks, counts, context)
    S0 = Decimal("1e-64")
    scales = tuple(S0/(Decimal(18)**j) for j in range(5))
    result["arithmetic"] = {"precision": context.prec, "rounding": context.rounding,
                            "tolerance": checks.tolerance, "fixed_scales_Sj": scales,
                            "no_transcendental_or_new_physical_evaluations": True}
    result["retained_physical_data"] = {
        "source_cache": "PHYS29 / joint_kernel_outputs.jet (only this cached path is used)",
        "energy_nodes_eV": source["energy_nodes_eV"],
        "components": {label: {key: source["joint_kernel_outputs"]["jet"][label][key] for key in KERNEL_FIELDS}
                       for label in source["energy_nodes_eV"]},
        "PHYS29_uniform_partials_weights_and_coefficients": source["second_order"]["jet_chain"],
        "stored_W_strings": source["constants"]["stored_PHYS26_root_strings"],
        "input_interpretation": "Retained finite Decimal approximations from source-real PHYS29 model; uncertainty unchanged",
    }
    definitions = {name: density_moments(name, checks, counts) for name in PROFILE_SPECS}
    result["exact_profile_moments"] = definitions
    data_by_branch = {branch: retained_branch(branch, source) for branch in BRANCHES}
    slopes = {}
    for branch, data in data_by_branch.items():
        curvature = data["p"]*data["pair"]["endpoint"][2]+data["q"]*data["pair"]["center"][2]
        C = Decimal(data["old"]["C_s-4_eV-2"])
        slope = Decimal(1)-curvature/(2*C)
        slopes[branch] = {"calH_curvature_s-4_eV-2": curvature, "C_s-4_eV-2": C,
                          "S_profile_slope_dimensionless": slope,
                          "formula": "S=1-calH/(2C); H_distance=b-m remains a different symbol"}
        counts["cached_branch_profile_slopes"] += 1
    result["branch_profile_slopes"] = slopes
    toy_pairs = {}
    for branch, data in data_by_branch.items():
        toy_pairs[branch] = exact_toy_pair(data)
        counts["exact_quadratic_coefficient_pairs_constructed"] += 1
    results = {}
    toys = {}
    result["profile_results"], result["exact_quadratic_toys"] = results, toys
    for profile, definition in definitions.items():
        mu2_exact = definition["mu2"]
        mu2 = Decimal(mu2_exact.numerator)/Decimal(mu2_exact.denominator)
        results[profile] = {"mu2_exact": mu2_exact, "mu2_decimal": mu2, "branches": {}}
        toys[profile] = {}
        for branch, data in data_by_branch.items():
            slope = slopes[branch]
            affine = affine_update(data, mu2, slope["calH_curvature_s-4_eV-2"], slope["S_profile_slope_dimensionless"])
            counts["cached_affine_profile_branch_updates"] += 1
            series = response_series(data["s"], data["R"], data["w"], data["endpoint"], data["center"],
                                     data["mean"], data["pair"], mu2)
            counts["cached_bivariate_physical_response_series"] += 1
            counts["cached_bivariate_physical_moment_series"] += 1
            results[profile]["branches"][branch] = {"affine": affine, "bivariate": series}
            residual = validate_physical(profile, branch, data, affine, series, mu2, checks, scales)
            results[profile]["branches"][branch]["retained_nonzero_A_diagnostics"] = residual
            toys[profile][branch] = quadratic_toy(profile, branch, toy_pairs[branch], mu2_exact, checks, counts)
    mu_difference = results["triangular"]["mu2_decimal"]-results["uniform"]["mu2_decimal"]
    for branch in BRANCHES:
        uniform = results["uniform"]["branches"][branch]["bivariate"]
        triangular = results["triangular"]["branches"][branch]["bivariate"]
        prefix = "profile_change__"+branch+"__"
        invariant_fields = (("response_s-4", scales[0]), ("B_s-4_eV-1", scales[1]),
                            ("C_s-4_eV-2", scales[2]), ("FdW_s-4_eV-3", scales[3]),
                            ("FWW_s-4_eV-4", scales[4]), ("c_eV", None))
        checks.numeric(prefix+"zero_and_first_mixed_invariance", [
            (key, triangular[key], uniform[key], scale) for key, scale in invariant_fields])
        slope = slopes[branch]
        checks.numeric(prefix+"K_and_d_affine_law", (
            ("K_difference", triangular["Fdd_s-4_eV-2"]-uniform["Fdd_s-4_eV-2"],
             mu_difference*(slope["calH_curvature_s-4_eV-2"]-2*slope["C_s-4_eV-2"]), scales[2]),
            ("d_difference", triangular["d_dimensionless"]-uniform["d_dimensionless"],
             mu_difference*slope["S_profile_slope_dimensionless"], None)))
    gap_results = {}
    for profile in PROFILE_SPECS:
        branch = results[profile]["branches"]
        up, lo = branch["upper_root"]["affine"], branch["lower_root"]["affine"]
        up_b, lo_b = branch["upper_root"]["bivariate"], branch["lower_root"]["bivariate"]
        d_gap = lo["d_dimensionless"]-up["d_dimensionless"]
        c_gap = lo["c_eV"]-up["c_eV"]
        terms = {key: lo["d_decomposition_dimensionless"][key]-up["d_decomposition_dimensionless"][key]
                 for key in up["d_decomposition_dimensionless"]}
        checks.numeric("gap__"+profile+"__decomposition_and_common_mu2_cancellation", (
            ("c_gap_cross_path", c_gap, lo_b["c_eV"]-up_b["c_eV"], None),
            ("d_gap_cross_path", d_gap, lo_b["d_dimensionless"]-up_b["d_dimensionless"], None),
            ("gap_decomposition", sum(terms.values(), Decimal(0)), d_gap, None),
            ("common_dV_cancels", terms["center_variance_V_second"], Decimal(0), None)))
        gap_results[profile] = {"definition": "Gamma=W_0-W_star", "c_gap_eV": c_gap,
                                "d_gap_dimensionless": d_gap, "d_gap_decomposition": terms,
                                "common_d_variance_contribution": terms["center_variance_V_second"]}
    gap_slope = slopes["lower_root"]["S_profile_slope_dimensionless"]-slopes["upper_root"]["S_profile_slope_dimensionless"]
    alternate_gap_slope = (slopes["upper_root"]["calH_curvature_s-4_eV-2"]/(2*slopes["upper_root"]["C_s-4_eV-2"])
                           -slopes["lower_root"]["calH_curvature_s-4_eV-2"]/(2*slopes["lower_root"]["C_s-4_eV-2"]))
    gap_change = gap_results["triangular"]["d_gap_dimensionless"]-gap_results["uniform"]["d_gap_dimensionless"]
    checks.numeric("gap__profile_change_affine_law", (
        ("S_gap_common_one_cancels", gap_slope, alternate_gap_slope, None),
        ("delta_d_gap", gap_change, mu_difference*gap_slope, None)))
    result["gap_results"] = {"profiles": gap_results, "S_gap_dimensionless": gap_slope,
                              "triangular_minus_uniform_d_gap": gap_change}
    result["descriptive_only"] = {
        "criterion": "Neither coefficient signs nor profile ordering contribute to PASS",
        "triangular_d_exceeds_uniform": {
            branch: results["triangular"]["branches"][branch]["affine"]["d_dimensionless"]
            > results["uniform"]["branches"][branch]["affine"]["d_dimensionless"] for branch in BRANCHES},
        "no_finite_width_triangular_root_or_error_data": True,
        "no_delta_005_profile_accuracy_claim": True,
    }
    expected_counts = protocol["expected_counts_one_successful_main"]
    checks.exact("execution_counts_and_zero_debits", [
        (key, counts[key], expected) for key, expected in expected_counts.items()])
    expected_names = protocol["acceptance_check_names"]
    existing_names = [item["name"] for item in checks.rows]
    checks.record("acceptance_catalogue_exact", existing_names == expected_names[:-1]
                  and expected_names[-1] == "acceptance_catalogue_exact",
                  actual_prior_check_names=existing_names, expected_all_check_names=expected_names,
                  expected_total_grouped_checks=len(expected_names))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="New raw JSON path within project; existing files are refused")
    args = parser.parse_args()
    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT/output
    if not output.resolve().is_relative_to(ROOT) or output.exists():
        raise ValueError("Output must be a new file within this portable project root")
    if not output.parent.is_dir():
        raise ValueError("Output parent must already exist")
    counts = {key: 0 for key in (
        "program_main_invocations_this_process", "retained_physical_node_records_loaded",
        "retained_physical_k_kprime_ksecond_values_loaded", "exact_profile_polynomial_moment_integrals",
        "cached_branch_profile_slopes", "cached_affine_profile_branch_updates",
        "cached_bivariate_physical_response_series", "cached_bivariate_physical_moment_series",
        "exact_quadratic_coefficient_pairs_constructed", "exact_nonzero_A_quadratic_profile_branches",
        "exact_toy_bivariate_response_series", "exact_toy_moment_series", *ZERO_DEBITS)}
    counts["program_main_invocations_this_process"] = 1
    result = {
        "task": TASK, "status": "RUNNING", "role": "NONBLIND numerical designer/generator implementation",
        "python_version": sys.version.split()[0], "evidence_class": ["numerically checked", "implementation-verified within cached coefficient algebra"],
        "coefficient_definition": "W=w+c*delta+d*delta^2+o(delta^2); d=Wsecond(0+)/2, fixed actual W",
        "physical_admission": "HOLD",
        "claim_ceiling": [
            "Conditional exact-root theorem is separate from these retained finite-point same-A-level coefficients.",
            "No new physical kernel, derivative, energy node, root, source/J value, interval enclosure, or physical data.",
            "Affine and bivariate paths share cached kernel data, moments, family, and finite Decimal arithmetic.",
            "Two prescribed profiles at zero width do not establish finite-width equivalence, monotonicity, or ordering.",
            "No triangular finite-width root or numerical root-error data are generated.",
            "No quantitative Taylor remainder, certified validity width, native equivalence, or physical uncertainty enclosure.",
            "Exact A=1 quadratic toy checks the residual term algebra; it is not the physical kernel.",
            "No emitter/history admission, protected runtime/default/source change, or independent physical replay credit.",
        ],
        "protected": {"physical": "HOLD", "interval_160_161": "FAIL", "tick": 160,
                      "auxiliary_escape": "FAIL", "HH": "OFF", "RCT": "OFF", "CR": "OFF",
                      "precision_atomic": "PARKED", "production_source_default_runtime_changes": 0},
    }
    error = None
    with localcontext() as context:
        context.prec = 80
        context.rounding = ROUND_HALF_EVEN
        checks = Checks(Decimal("1e-60"))
        try:
            science(result, checks, counts, context)
        except Exception as exc:
            error = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc(),
                     "classification": "Observed first execution failure; root cause requires review; no automatic retry"}
        result["checks"] = checks.rows
        result["actual_counts"] = counts
        passed = sum(row["passed"] for row in checks.rows)
        result["summary"] = {"total_grouped_checks": len(checks.rows), "passed": passed,
                             "failed": len(checks.rows)-passed,
                             "failed_names": [row["name"] for row in checks.rows if not row["passed"]],
                             "execution_exception": error, "all_pass": error is None and passed == len(checks.rows)}
        result["status"] = "SCOPED_CACHED_ALGEBRA_PASS" if result["summary"]["all_pass"] else "FIRST_EXECUTION_FAILED"
    text = json.dumps(encode(result), ensure_ascii=False, indent=2, allow_nan=False)+"\n"
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    print(json.dumps(encode({"task": TASK, "status": result["status"], "summary": result["summary"],
                             "actual_counts": counts}), ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result["summary"]["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
