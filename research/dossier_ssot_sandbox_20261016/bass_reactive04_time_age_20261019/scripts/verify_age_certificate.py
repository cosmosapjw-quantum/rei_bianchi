#!/usr/bin/env python3
"""Independent Decimal90 audit of Rust certificates using actual input nodes.

The reference integrates the absolute difference of quantiles analytically.
The Rust implementation instead integrates positive CDF plateau areas.
The explicitly selected exported inputs are read-only; all new results go to
the caller-selected output directory.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import sys
import time

PRECISION = 90
D = Decimal
ZERO = D(0)
ONE = D(1)
EXP_CUTOFF = D(1800)


def decimal64(value):
    """The exact real number represented by the round-tripped f64 input."""
    return D.from_float(float(value))


def negexp(z):
    # Main reference domain tau <= 1e12. The omitted normalized exponential
    # tail is bounded by 1e12*exp(-1800) < 2e-770 for these unit-weight rules.
    return ZERO if z > EXP_CUTOFF else (-z).exp()


class Reference:
    def __init__(self, tau):
        self.tau = tau
        self.tail = negexp(tau)
        self.denominator = ONE - self.tail
        self.phi = ONE if tau == 0 else self.denominator / tau

    def cdf(self, x):
        return x if self.tau == 0 else (ONE - negexp(self.tau * x)) / self.denominator

    def quantile_integral(self, p):
        """Integral_0^p Q(q)dq, used only by the independent reference."""
        if self.tau == 0:
            return p * p / 2
        y = ONE - self.denominator * p
        ylogy = ZERO if y == 0 else y * y.ln()
        return (ylogy + self.denominator * p) / (self.tau * self.denominator)

    def exact_moments(self):
        if self.tau == 0:
            return D(1) / 2, D(1) / 3
        t = self.tau
        ratio = self.tail / self.denominator
        return ONE / t - ratio, D(2) / (t * t) - (ONE + D(2) / t) * ratio

    def quantile_area(self, p0, p1, x):
        """Integral_p0^p1 |Q(p)-x|dp, split at exact P(X<=x)."""
        q = self.cdf(x)
        r0, r1 = self.quantile_integral(p0), self.quantile_integral(p1)
        if q <= p0:
            answer = r1 - r0 - x * (p1 - p0)
        elif q >= p1:
            answer = x * (p1 - p0) - r1 + r0
        else:
            rq = self.quantile_integral(q)
            answer = x * (q - p0) - rq + r0 + r1 - rq - x * (p1 - q)
        if answer < 0:
            assert abs(answer) < D("1e-75"), ("negative high-precision area", answer)
            answer = ZERO
        return answer


def certify(tau, nodes):
    reference = Reference(tau)
    ordered = sorted((x, w) for x, w in nodes if w > 0)
    assert ordered and all(0 <= x <= 1 for x, _ in ordered)
    logs = [w.ln() - tau * x for x, w in ordered]
    shift = max(logs)
    shifted = [negexp(shift - value) for value in logs]
    total = sum(shifted, ZERO)
    log_mass = shift + total.ln()
    log_ratio = log_mass - reference.phi.ln()
    discrete_mass = negexp(-log_mass) if log_mass <= 0 else log_mass.exp()
    mass_ratio = negexp(-log_ratio) if log_ratio <= 0 else log_ratio.exp()
    probabilities = [w / total for w in shifted]
    p0, ks, w1 = ZERO, ZERO, ZERO
    moments = [ZERO, ZERO]
    positive = [(node, p) for node, p in zip(ordered, probabilities) if p > 0]
    for index, ((x, _), p) in enumerate(positive):
        p1 = ONE if index + 1 == len(positive) else p0 + p
        # Decimal rounding in the accumulated cdf is much below its audit floor.
        if p1 > ONE:
            assert p1 - ONE < D("1e-75")
            p1 = ONE
        gx = reference.cdf(x)
        ks = max(ks, abs(gx - p0), abs(gx - p1))
        w1 += reference.quantile_area(p0, p1, x)
        moments[0] += p * x
        moments[1] += p * x * x
        p0 = p1
    exact = reference.exact_moments()
    return {
        "exact_mass": reference.phi,
        "discrete_mass": discrete_mass,
        "relative_mass_defect": mass_ratio - ONE,
        "log_mass_ratio": log_ratio,
        "cdf_sup": ks,
        "w1": w1,
        "exact_mean": exact[0],
        "discrete_mean": moments[0],
        "mean_defect": moments[0] - exact[0],
        "exact_second": exact[1],
        "discrete_second": moments[1],
        "second_defect": moments[1] - exact[1],
        "largest_probability": max(probabilities),
        "reference_tail_cut_atoms": len(ordered) - len(positive),
    }


def selftests():
    checks = []
    for x, cost, ks in [(ZERO, D("0.5"), ONE), (D("0.5"), D("0.25"), D("0.5")), (ONE, D("0.5"), ONE)]:
        c = certify(ZERO, [(x, ONE)])
        assert c["w1"] == cost and c["cdf_sup"] == ks
        checks.append("uniform_single_atom_" + str(x))
    a = D("0.5") - ONE / (2 * D(3).sqrt())
    c = certify(ZERO, [(a, D("0.5")), (ONE - a, D("0.5"))])
    exact_cost = D(5) / 12 - ONE / (2 * D(3).sqrt())
    assert abs(c["w1"] - exact_cost) < D("1e-80")
    assert abs(c["cdf_sup"] - ONE / (2 * D(3).sqrt())) < D("1e-80")
    checks.append("uniform_GL2_exact_radical")
    for t in [D("1e-8"), D(1), D(93), D("1e12")]:
        c = certify(t, [(ZERO, ONE)])
        assert abs(c["w1"] - c["exact_mean"]) < D("1e-65")
    checks.append("young_atom_W1_equals_exact_mean_four_optical_depths")
    # Zero-opacity composite equal-weight midpoint rule has exact W1=1/(4N).
    for n in [2, 4, 8]:
        nodes = [((D(i) + D("0.5")) / n, ONE / n) for i in range(n)]
        assert abs(certify(ZERO, nodes)["w1"] - ONE / (4 * n)) < D("1e-80")
    checks.append("composite_midpoint_W1_exact_three_grids")
    return checks


def key(row):
    return row["family"], row["tau"], int(row["nsteps"]), int(row["resolution"])


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close_decimal(actual, expected, relative=D("2e-10"), absolute=D("2e-30")):
    return abs(actual - expected) <= relative * abs(expected) + absolute


def verify(nodes_path, certificates_path, out_dir):
    hashes = {str(p): hash_file(p) for p in [nodes_path, certificates_path]}
    groups = {}
    with nodes_path.open(newline="") as f:
        for row in csv.DictReader(f):
            groups.setdefault(key(row), []).append((decimal64(row["age"]), decimal64(row["emitted_weight"])))
    with certificates_path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    reference_rows, comparisons, problems = [], [], []
    maximum_absolute, maximum_scaled = {}, {}
    with localcontext() as ctx:
        ctx.prec = PRECISION
        checked_tests = selftests()
        for row in rows:
            case = key(row)
            nodes = groups[case]
            assert len(nodes) == int(row["node_count"])
            tau = ZERO if row["measure"] == "emitted" else decimal64(row["tau"])
            assert 0 <= tau <= D("1e12")
            ref = certify(tau, nodes)
            reference_rows.append({**{k: row[k] for k in ["family", "tau", "nsteps", "resolution", "measure"]}, **{k: str(v) for k, v in ref.items()}})
            errors = {}
            for field in [
                "exact_mass", "discrete_mass", "relative_mass_defect", "log_mass_ratio",
                "cdf_sup", "w1", "exact_mean", "discrete_mean", "mean_defect",
                "exact_second", "discrete_second", "second_defect",
            ]:
                actual = decimal64(row[field])
                expected = ref[field]
                assert actual.is_finite()
                error = abs(actual - expected)
                # Declared before reading results. Tight relative checks on W1
                # and positive moments remain meaningful when tau is huge.
                if field in ["w1", "exact_mean", "discrete_mean", "exact_second", "discrete_second", "exact_mass"]:
                    tolerance = D("2e-10") * abs(expected) + D("2e-30")
                elif field == "log_mass_ratio":
                    tolerance = D("3e-14") * max(ONE, abs(expected))
                elif field == "discrete_mass":
                    tolerance = D("2e-10") * abs(expected) + D("1e-320")
                else:
                    tolerance = D("3e-14")
                passed = error <= tolerance
                scaled = error / tolerance if tolerance else ZERO
                errors[field] = {"absolute_error": str(error), "tolerance": str(tolerance), "pass": passed}
                maximum_absolute[field] = max(maximum_absolute.get(field, ZERO), error)
                maximum_scaled[field] = max(maximum_scaled.get(field, ZERO), scaled)
                if not passed:
                    problems.append({"case": [*case, row["measure"]], "field": field, "expected": str(expected), "actual": str(actual), **errors[field]})
            assert ref["cdf_sup"] + D("1e-75") >= ref["largest_probability"] / 2
            assert abs(ref["mean_defect"]) <= ref["w1"] + D("1e-65")
            assert abs(ref["second_defect"]) <= 2 * ref["w1"] + D("1e-65")
            comparisons.append({"case": [*case, row["measure"]], "errors": errors})
    assert all(hash_file(Path(p)) == h for p, h in hashes.items()), "Input changed while auditing"
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "DECIMAL_ACTUAL_NODE_REFERENCE.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(reference_rows[0]))
        writer.writeheader()
        writer.writerows(reference_rows)
    result = {
        "status": "PASS_SCOPED" if not problems else "FAIL",
        "method": "Decimal90 on exact round-tripped f64 nodes; analytic quantile-antiderivative route independent of Rust positive CDF plateau integrals.",
        "precision": PRECISION, "reference_domain_tau_max": "1e12",
        "exponential_tail_policy": "exp(-z) replaced by zero for z>1800; for this unit-weight matrix normalized omitted mass <=1e12*exp(-1800)<2e-770.",
        "certificate_scope": "Floating numerical verification of real-arithmetic identities, not an outward-rounded interval proof or evolving-gas error bound.",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version, "input_hashes": hashes,
        "inputs_unchanged": True, "case_count": len(groups), "measure_rows": len(rows),
        "input_node_rows": sum(len(v) for v in groups.values()),
        "comparison_fields_per_row": 12, "scalar_comparisons": 12 * len(rows),
        "selftests": checked_tests,
        "max_absolute_errors": {k: str(v) for k, v in maximum_absolute.items()},
        "max_fraction_of_allowed_tolerance": {k: str(v) for k, v in maximum_scaled.items()},
        "issues": problems, "comparisons": comparisons,
    }
    (out_dir / "DECIMAL_ACTUAL_NODE_VERIFICATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["status", "case_count", "measure_rows", "input_node_rows", "scalar_comparisons", "max_absolute_errors", "issues"]}, indent=2))
    return not problems


def verify_source(age_study, out_dir, source_path):
    """Full label/composition arithmetic; independent shape at 12 chosen rules."""
    paths = [age_study / name for name in [
        "AGE_SOURCE_CERTIFICATES.csv", "AGE_SOURCE_ACTUAL_NODES.csv",
        "AGE_SOURCE_MIXTURE_BOUNDS.csv",
    ]]
    paths.append(source_path)
    hashes = {str(p): hash_file(p) for p in paths}
    with paths[0].open(newline="") as f:
        labels = list(csv.DictReader(f))
    with paths[2].open(newline="") as f:
        mixtures = list(csv.DictReader(f))
    with source_path.open(newline="") as f:
        sources = list(csv.DictReader(f))
    assert len(sources) == 384 and len(labels) == 4608 and len(mixtures) == 12
    representatives, by_family, grouped_labels = {}, {}, {}
    for row in labels:
        rule_id = int(row["rule_id"])
        representatives.setdefault((rule_id, row["measure"]), row)
        by_family.setdefault((row["family"], int(row["resolution"])), {})[rule_id] = decimal64(row["tau"])
        grouped_labels.setdefault((row["family"], int(row["resolution"]), row["measure"]), []).append(row)
    selected = sorted({
        choice
        for rules in by_family.values()
        for choice in [
            min(rules, key=lambda rule: (rules[rule], rule)),
            max(rules, key=lambda rule: (rules[rule], -rule)),
        ]
    })
    assert len(selected) == 12
    selected_set = set(selected)
    nodes, total_input_nodes = {}, 0
    with paths[1].open(newline="") as f:
        for row in csv.DictReader(f):
            total_input_nodes += 1
            rule_id = int(row["rule_id"])
            if rule_id in selected_set:
                nodes.setdefault(rule_id, []).append((decimal64(row["age"]), decimal64(row["emitted_weight"])))
    failures, sample_rows, max_sample_errors = [], [], {}
    composition_rows, maximum_composition_error = [], {}
    source_identity_checks = 0
    with localcontext() as ctx:
        ctx.prec = PRECISION
        for row in labels:
            src = sources[int(row["source_id"])]
            assert decimal64(row["energy_ev"]) == decimal64(src["energy_ev"])
            assert decimal64(row["born_com3"]) == decimal64(src["total_birth_com3"])
            kappa = sum((decimal64(src[name]) for name in ["k_HI", "k_HeI", "k_HeII", "k_DI"]), ZERO)
            exact_tau = kappa * decimal64(row["duration_s"])
            assert close_decimal(decimal64(row["tau"]), exact_tau, D("8e-16"), D("1e-30"))
            source_identity_checks += 1
        for rule_id in selected:
            for measure in ["emitted", "survivor"]:
                row = representatives[(rule_id, measure)]
                tau = ZERO if measure == "emitted" else decimal64(row["tau"])
                ref = certify(tau, nodes[rule_id])
                born = decimal64(row["born_com3"])
                mapped = {
                    "exact_mass_com3": born * ref["exact_mass"],
                    "discrete_mass_com3": born * ref["discrete_mass"],
                    **{field: ref[field] for field in [
                        "relative_mass_defect", "cdf_sup", "w1", "exact_mean",
                        "discrete_mean", "mean_defect", "exact_second",
                        "discrete_second", "second_defect",
                    ]},
                }
                for field, expected in mapped.items():
                    error = abs(decimal64(row[field]) - expected)
                    if field in ["relative_mass_defect", "cdf_sup", "mean_defect", "second_defect"]:
                        tolerance = D("3e-14")
                    else:
                        tolerance = D("2e-10") * abs(expected) + D("2e-30")
                    max_sample_errors[field] = max(max_sample_errors.get(field, ZERO), error)
                    if error > tolerance:
                        failures.append({"kind": "actual_node", "rule_id": rule_id, "measure": measure,
                                         "field": field, "error": str(error), "tolerance": str(tolerance)})
                sample_rows.append({
                    "rule_id": rule_id, "family": row["family"], "resolution": row["resolution"],
                    "tau": row["tau"], "measure": measure, "node_count": len(nodes[rule_id]),
                    **{field: str(value) for field, value in mapped.items()},
                })
        for mixture in mixtures:
            group_key = mixture["family"], int(mixture["resolution"]), mixture["measure"]
            rows = grouped_labels[group_key]
            assert len(rows) == 384 and {int(row["source_id"]) for row in rows} == set(range(384))
            assert len({int(row["rule_id"]) for row in rows}) == 48
            exact_masses = [decimal64(row["exact_mass_com3"]) for row in rows]
            discrete_masses = [decimal64(row["discrete_mass_com3"]) for row in rows]
            exact_total, discrete_total = sum(exact_masses, ZERO), sum(discrete_masses, ZERO)
            alpha = [mass / exact_total for mass in exact_masses]
            beta = [mass / discrete_total for mass in discrete_masses]
            tv = sum((abs(a - b) for a, b in zip(alpha, beta)), ZERO) / 2
            weighted = lambda field, weights: sum(
                (weight * decimal64(row[field]) for weight, row in zip(weights, rows)), ZERO
            )
            cdf, w1 = weighted("cdf_sup", alpha), weighted("w1", alpha)
            em, dm = weighted("exact_mean", alpha), weighted("discrete_mean", beta)
            es, ds = weighted("exact_second", alpha), weighted("discrete_second", beta)
            expected = {
                "exact_mass_com3": exact_total, "discrete_mass_com3": discrete_total,
                "relative_mass_defect": discrete_total / exact_total - ONE,
                "exact_weighted_cdf_sup": cdf, "exact_weighted_w1": w1, "label_weight_tv": tv,
                "mixture_cdf_upper_bound": cdf + tv, "mixture_w1_upper_bound": w1 + tv,
                "mixture_exact_mean": em, "mixture_discrete_mean": dm,
                "mixture_mean_defect": dm - em, "mixture_exact_second": es,
                "mixture_discrete_second": ds, "mixture_second_defect": ds - es,
            }
            for field, value in expected.items():
                error = abs(decimal64(mixture[field]) - value)
                tolerance = D("3e-14") if "mass_com3" not in field else D("3e-14") * abs(value)
                maximum_composition_error[field] = max(maximum_composition_error.get(field, ZERO), error)
                if error > tolerance:
                    failures.append({"kind": "mixture_arithmetic", "case": list(group_key),
                                     "field": field, "error": str(error), "tolerance": str(tolerance)})
            composition_rows.append({**{k: mixture[k] for k in ["family", "resolution", "measure"]},
                                     **{k: str(v) for k, v in expected.items()}})
    assert all(hash_file(Path(p)) == h for p, h in hashes.items()), "Source input changed"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in [
        ("DECIMAL_SOURCE_SAMPLE_REFERENCE.csv", sample_rows),
        ("DECIMAL_SOURCE_MIXTURE_ARITHMETIC.csv", composition_rows),
    ]:
        with (out_dir / name).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    result = {
        "status": "PASS_SCOPED" if not failures else "FAIL",
        "precision": PRECISION, "input_hashes": hashes, "inputs_unchanged": True,
        "actual_node_sample_selection": "Predeclared smallest and largest total opacity in each of AP r1,r2,r4,r8 and GL2,GL4; ties select smallest rule_id.",
        "selected_rule_ids": selected, "selected_unique_rules": len(selected),
        "available_unique_rules": len(representatives) // 2,
        "selected_actual_node_rows": sum(len(n) for n in nodes.values()),
        "available_actual_node_rows": total_input_nodes, "sample_measure_rows": len(sample_rows),
        "sample_scalar_comparisons": 11 * len(sample_rows),
        "source_rows": len(sources), "label_identity_rows_checked": source_identity_checks,
        "mixture_rows_checked": len(mixtures), "mixture_scalar_comparisons": 14 * len(mixtures),
        "composition_scope": "All 4608 label rows are checked for source identity and independently recombined. Their per-label certificate values are input to this arithmetic check; direct Decimal node integration covers the 12 selected rules only.",
        "mixture_scope": "Weighted component distances plus label-weight TV are upper bounds for scalar mixtures, not exact scalar-mixture distances.",
        "max_sample_absolute_errors": {k: str(v) for k, v in max_sample_errors.items()},
        "max_composition_absolute_errors": {k: str(v) for k, v in maximum_composition_error.items()},
        "issues": failures,
    }
    (out_dir / "DECIMAL_SOURCE_VERIFICATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in [
        "status", "selected_rule_ids", "selected_actual_node_rows", "sample_scalar_comparisons",
        "label_identity_rows_checked", "mixture_scalar_comparisons", "issues",
    ]}, indent=2))
    return not failures


def verify_edges(age_study, out_dir):
    """Independent analytic limits for the explicitly exported edge contracts."""
    path = age_study / "AGE_EDGE_CASES.csv"
    failure_path = age_study / "AGE_RULE_FAILURES.csv"
    hashes = {str(p): hash_file(p) for p in [path, failure_path]}
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    failures, checked = [], []
    invalid = {"negative_population", "negative_source", "invalid_age"}
    empty = {"zero_source", "empty_source", "empty_positive_source"}
    with localcontext() as ctx:
        ctx.prec = PRECISION
        for row in rows:
            name = row["case"]
            if name in invalid:
                assert row["result"] == "InvalidInput"
            else:
                assert row["result"] == "OK"
                if name in empty:
                    assert row["shape_defined"] == "false"
                    assert row["cdf_sup"] == row["w1"] == ""
                    assert float(row["survivor_discrete_mass"]) == 0
                    assert row["absolute_mass_underflow"] == "false"
                    if name != "empty_positive_source":
                        assert float(row["survivor_exact_mass"]) == 0
                else:
                    tau = decimal64(row["tau"])
                    if name == "zero_opacity":
                        expected_ks, expected_w1 = D("0.5"), D("0.25")
                    elif name == "underflowed_absolute_survivors":
                        expected_ks, expected_w1 = ONE, ONE - Reference(tau).exact_moments()[0]
                        assert row["absolute_mass_underflow"] == "true"
                        assert float(row["survivor_discrete_mass"]) == 0
                    elif name == "huge_tau_young_atom":
                        expected_ks, expected_w1 = ONE, ONE / tau
                    elif name == "huge_tau_mean_atom":
                        age = decimal64("1e-300")
                        tail_at_age = negexp(tau * age)
                        expected_ks = max(tail_at_age, ONE - tail_at_age)
                        expected_w1 = age - ONE / tau + 2 * tail_at_age / tau
                    else:
                        raise AssertionError("Unexpected edge contract: " + name)
                    assert row["shape_defined"] == "true"
                    for field, expected in [("cdf_sup", expected_ks), ("w1", expected_w1)]:
                        actual = decimal64(row[field])
                        tolerance = D("3e-14") * abs(expected) + D("1e-320")
                        if abs(actual - expected) > tolerance:
                            failures.append({"case": name, "field": field, "error": str(abs(actual-expected)),
                                             "tolerance": str(tolerance)})
            checked.append(name)
    with failure_path.open(newline="") as f:
        rule_failures = list(csv.DictReader(f))
    assert len(rule_failures) == 5
    assert all(r["error"] == "NoForwardProgress" and r["class"] == "NUMERICAL_REPRESENTATION_LIMIT"
               and float(r["tau"]) == 1e300 for r in rule_failures)
    assert all(hash_file(Path(p)) == h for p, h in hashes.items())
    result = {
        "status": "PASS_SCOPED" if not failures else "FAIL", "edge_cases_checked": checked,
        "edge_input_contract": "One atom at age 1/2 for zero opacity, age 1 for absolute underflow, age 0 and exact f64 1e-300 at tau=exact f64 1e300; empty/invalid inputs as named in the Rust example.",
        "reference": "Closed single-atom CDF/W1 limits and exact normalized exponential moments; finite upper-tail correction at tau=1e300 is negligible beyond Decimal90, not a changed source model.",
        "zero_source": "Physical mass zero; normalized shape undefined.",
        "underflow": "A positive analytic survival mass may be unrepresentable in binary64 while its conditional shape remains defined by log-scaled weights.",
        "fitted_rule_failures_checked": len(rule_failures),
        "failure_class": "Existing AP rule cannot progress at tau=1e300; NUMERICAL_REPRESENTATION_LIMIT, neither Cx(WorkLimit) nor physical no-solution.",
        "input_hashes": hashes, "inputs_unchanged": True, "issues": failures,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "DECIMAL_EDGE_VERIFICATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"edge_status": result["status"], "edge_cases": len(checked),
                      "expected_rule_limits": len(rule_failures), "issues": failures}, indent=2))
    return not failures


def main():
    p = argparse.ArgumentParser()
    p.add_argument("age_study", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--include-source", action="store_true",
                   help="Audit 12 actual source rules and all source-label mixture arithmetic.")
    p.add_argument("--include-edges", action="store_true",
                   help="Audit empty, invalid and extreme-opacity edge contracts.")
    p.add_argument("--source-inputs", type=Path,
                   default=Path(__file__).resolve().parents[1] / "inputs" / "AP_FROZEN_SOURCE_INPUTS.csv",
                   help="Original frozen source CSV; defaults to the verifier's unit inputs directory.")
    args = p.parse_args()
    start = time.monotonic()
    ok = verify(args.age_study / "AGE_ACTUAL_NODES.csv", args.age_study / "AGE_CERTIFICATES.csv", args.output)
    if args.include_source:
        ok = verify_source(args.age_study, args.output, args.source_inputs) and ok
    if args.include_edges:
        ok = verify_edges(args.age_study, args.output) and ok
    elapsed = time.monotonic() - start
    print(json.dumps({"overall_status": "PASS_SCOPED" if ok else "FAIL",
                      "elapsed_seconds": elapsed, "output": str(args.output)}, indent=2))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
