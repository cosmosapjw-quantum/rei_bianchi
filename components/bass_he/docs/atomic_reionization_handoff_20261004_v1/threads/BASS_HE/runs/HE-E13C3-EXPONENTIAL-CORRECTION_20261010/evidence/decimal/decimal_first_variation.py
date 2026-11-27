#!/usr/bin/env python3
"""New 70-digit E13C3 first variation; never rerun the E13C2 oracle.

This contributor shares E13C2's unchanged Coefficients definitions and Decimal
Gauss roots/weights. Frozen fields, damped correction kernels, Fubini moments,
heat, ledgers and comparison metrics are implemented here independently.
Only the six local rows in the saved ORACLE_RESULTS.json are admissible.
"""

import argparse
import csv
from datetime import datetime, UTC
import decimal
from decimal import Decimal as D, getcontext
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import shlex
import sys
import time

ZERO, ONE = D(0), D(1)
SPECIES = ("HI", "HeI", "HeII")
OBSERVABLES = ("P1", "A", "B_eV", "Z_eV", "QN", "QE_eV", "H_eV", "H_total_eV")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n")


def lift(value):
    return D.from_float(float(value))


def keyed(row):
    return (row["mode"], int(row["step"]), int(row["node"]), int(row["segment"]))


def j_response(rate, duration):
    """Independent closed Decimal exponential; explicit removable singularity."""
    if duration == ZERO:
        return ZERO
    if rate == ZERO:
        return duration
    return (ONE - (-rate * duration).exp()) / rate


class FrozenField:
    def __init__(self, coeffs, row):
        self.coeffs = coeffs
        self.q = lift(row["q"])
        self.lam = [lift(row["lambda_" + species]) for species in SPECIES]
        self.total = sum(self.lam, ZERO)
        if self.total < ZERO or coeffs.h <= ZERO:
            raise ArithmeticError("invalid local frozen rate or duration")

    def __call__(self, elapsed):
        return (self.coeffs.f0 * (-self.total * elapsed).exp()
                + self.q * j_response(self.total, elapsed))

    def residual_sample(self, elapsed):
        energy, q, lam = self.coeffs(elapsed / self.coeffs.h)
        pf = self(elapsed)
        dq = q - self.q
        dl = [value - frozen for value, frozen in zip(lam, self.lam)]
        r = dq - sum(dl, ZERO) * pf
        return energy, pf, dq, dl, r


def add_heat(result, chi):
    result["H_eV"] = [b - ion * a for a, b, ion in zip(result["A"], result["B_eV"], chi)]
    result["H_total_eV"] = sum(result["H_eV"], ZERO)
    return result


def first_variation(field, nodes, weights, chi):
    """One-dimensional quadrature of the new response and direct moments."""
    h, lf = field.coeffs.h, field.total
    p1 = i0 = ie = qn = qe = ZERO
    direct_a = [ZERO] * 3
    direct_b = [ZERO] * 3
    for node, weight in zip(nodes, weights):
        elapsed = h * node
        remaining = h - elapsed
        energy, pf, dq, dl, r = field.residual_sample(elapsed)
        dv = h * weight
        p1 += dv * (-lf * remaining).exp() * r
        i0 += dv * j_response(lf, remaining) * r
        ie += dv * energy * j_response(lf + ONE, remaining) * r
        qn += dv * dq
        qe += dv * energy * dq
        for species in range(3):
            direct_a[species] += dv * dl[species] * pf
            direct_b[species] += dv * energy * dl[species] * pf
    response_a = [lam * i0 for lam in field.lam]
    response_b = [lam * ie for lam in field.lam]
    da = [direct + response for direct, response in zip(direct_a, response_a)]
    db = [direct + response for direct, response in zip(direct_b, response_b)]
    energy1 = field.coeffs.e0 * (-h).exp()
    result = {
        "P1": p1, "A": da, "B_eV": db, "Z_eV": ie,
        "QN": qn, "QE_eV": qe,
        "direct_A": direct_a, "direct_B_eV": direct_b,
        "response_A": response_a, "response_B_eV": response_b,
        "I0": i0, "IE_eV": ie,
        "number_ledger": p1 + sum(da, ZERO) - qn,
        "energy_ledger_eV": energy1 * p1 + sum(db, ZERO) + ie - qe,
        "initial_correction": ZERO,
        "captured_initial_P0": field.coeffs.f0,
        "frozen_endpoint_P1": field(h),
        "corrected_endpoint_P1": field(h) + p1,
        "endpoint_E1_eV": energy1,
    }
    return add_heat(result, chi)


def correction_endpoint(field, duration, nodes, weights):
    if duration == ZERO:
        return ZERO
    result = ZERO
    for node, weight in zip(nodes, weights):
        elapsed = duration * node
        r = field.residual_sample(elapsed)[4]
        result += duration * weight * (-field.total * (duration - elapsed)).exp() * r
    return result


def observable_values(value):
    if isinstance(value, list):
        return [D(v) for v in value]
    return D(value)


def differences(first, second):
    result = {}
    for name in OBSERVABLES:
        left, right = first[name], second[name]
        result[name] = [a - b for a, b in zip(left, right)] if isinstance(left, list) else left - right
    return result


def maximum_abs(values):
    flat = []
    for value in values:
        flat.extend(value if isinstance(value, list) else [value])
    return max(abs(v) for v in flat)


def comparison_scalar(candidate, reference, floor):
    error = candidate - reference
    above_floor = abs(reference) >= floor
    return {
        "candidate": candidate,
        "reference": reference,
        "signed_error": error,
        "absolute_error": abs(error),
        "absolute_floor": floor,
        "reference_above_or_equal_floor": above_floor,
        "relative_absolute_error": abs(error) / abs(reference) if above_floor else None,
        "relative_status": "EVALUATED" if above_floor else "UNRESOLVED_BELOW_ABSOLUTE_FLOOR",
        "absolute_error_within_floor": abs(error) <= floor,
        "normalized_error_with_absolute_floor": abs(error) / max(abs(reference), floor),
    }


def compare_observables(candidate, reference, number_floor, energy_floor):
    result = {}
    for name in OBSERVABLES:
        floor = number_floor if name in ("P1", "A", "QN") else energy_floor
        if isinstance(candidate[name], list):
            result[name] = [comparison_scalar(a, b, floor) for a, b in zip(candidate[name], reference[name])]
        else:
            result[name] = comparison_scalar(candidate[name], reference[name], floor)
    return result


def all_finite(value):
    if isinstance(value, D):
        return value.is_finite()
    if isinstance(value, dict):
        return all(all_finite(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return all(all_finite(v) for v in value)
    return True


def load_inputs(root, contract):
    identities, checks = [], {}
    for rel, expected in contract["source_pins"].items():
        path = root / rel
        observed = sha256(path)
        identities.append({"path": str(path), "sha256": observed, "bytes": path.stat().st_size})
        checks["pin:" + rel] = observed == expected
    if not all(checks.values()):
        raise ValueError("predeclared input pin mismatch: " + repr(checks))
    saved = json.loads((root / "evidence/ORACLE_RESULTS.json").read_text())
    expected_keys = contract["selection_fixed_before_execution"]
    checks["saved_six_keys_exact"] = [record["key"] for record in saved["results"]] == expected_keys
    checks["saved_reference_pass_scoped"] = saved["verdict"] == "PASS_SCOPED"
    checks["helper_matches_saved_as_run_identity"] = (saved["oracle_code_sha256"]
                                                     == contract["source_pins"]["code/decimal_collocation.py"])
    upstream = root / "inputs/upstream_e13c1"
    capture_rows, stage_rows = {}, {}
    for rel in ("evidence/capture/OFF/SEGMENTS.csv", "inputs/OFF_STAGES.csv",
                "evidence/capture/GM/SEGMENTS.csv", "inputs/GM_STAGES.csv", "code/photon_green.py"):
        path = upstream / rel
        matched = [r for r in saved["source_identity"] if r["path"].endswith("/" + rel)]
        if len(matched) != 1:
            raise ValueError("ambiguous/missing saved source identity for " + rel)
        identity = {"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size,
                    "saved_path": matched[0]["path"]}
        identities.append(identity)
        checks["saved_source_hash:" + rel] = identity["sha256"] == matched[0]["sha256"]
        checks["saved_source_bytes:" + rel] = identity["bytes"] == matched[0]["bytes"]
        if rel.endswith("SEGMENTS.csv"):
            with path.open(newline="") as source:
                for row in csv.DictReader(source):
                    rowkey = keyed(row)
                    if list(rowkey) in expected_keys:
                        if rowkey in capture_rows:
                            raise ValueError("duplicate selected segment row")
                        capture_rows[rowkey] = row
        elif rel.endswith("STAGES.csv"):
            mode = path.name.split("_")[0]
            with path.open(newline="") as source:
                for row in csv.DictReader(source):
                    stage_rows[(mode, int(row["step"]))] = row
    for record in saved["results"]:
        rowkey = tuple(record["key"])
        checks["captured_row:" + repr(rowkey)] = capture_rows.get(rowkey) == record["input_row_exact_csv_strings"]
        checks["stage_row:" + repr(rowkey)] = stage_rows.get(rowkey[:2]) == record["stage_input_exact_csv_strings"]
    if not all(checks.values()):
        raise ValueError("saved input identity/equality failed: " + repr(checks))
    return saved, identities, checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior-root", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    started = time.perf_counter()
    started_utc = datetime.now(UTC).isoformat()
    contract = json.loads(args.contract.read_text())
    getcontext().prec = contract["numerics"]["decimal_digits"]
    source_sha_as_run = sha256(Path(__file__).resolve())
    saved, input_identity, input_checks = load_inputs(args.prior_root, contract)
    # Import defines the old routines, but the only helpers called are the two
    # named below. Disable bytecode writes so the original tree stays unchanged.
    sys.dont_write_bytecode = True
    helper_path = args.prior_root / "code/decimal_collocation.py"
    spec = importlib.util.spec_from_file_location("e13c2_shared_coefficient_definitions", helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    chi = [lift(value) for value in contract["mathematical_contract"]["chi_eV_binary64_exact_lift"]]
    numerical = contract["predeclared_gates"]
    diagnostics = numerical["heat_defect_accuracy_research_diagnostic"]
    number_floor, energy_floor = D(diagnostics["number_floor"]), D(diagnostics["energy_floor_eV"])
    degree_low, degree_high = contract["numerics"]["degrees"]
    rules, quadrature_checks = {}, {}
    for degree in (degree_low, degree_high):
        nodes, weights, error = helper.gauss_rule(degree)
        rules[degree] = (nodes, weights)
        quadrature_checks[str(degree)] = {
            "maximum_polynomial_moment_error": error,
            "tolerance": D(numerical["quadrature_polynomial_moment_abs"]),
            "pass": error <= D(numerical["quadrature_polynomial_moment_abs"]),
        }
    limit_checks = {
        "J_zero_rate_exact": all(j_response(ZERO, t) == t for t in (ZERO, D("1e-7"), ONE)),
        "J_zero_duration_exact": all(j_response(rate, ZERO) == ZERO for rate in (ZERO, ONE, D("1e6"))),
    }
    results, numerical_failures, research_failures = [], [], []
    for record in saved["results"]:
        row, stage = record["input_row_exact_csv_strings"], record["stage_input_exact_csv_strings"]
        coeffs = helper.Coefficients(row, stage)
        field = FrozenField(coeffs, row)
        calculations = {str(degree): first_variation(field, *rules[degree], chi)
                        for degree in (degree_low, degree_high)}
        low, high = calculations[str(degree_low)], calculations[str(degree_high)]
        reference = {name: observable_values(record["signed_continuous_minus_frozen"][name])
                     for name in ("P1", "A", "B_eV", "Z_eV", "QN", "QE_eV")}
        add_heat(reference, chi)
        difference = differences(high, low)
        max_number = maximum_abs(difference[name] for name in ("P1", "A", "QN"))
        max_energy = maximum_abs(difference[name] for name in ("B_eV", "Z_eV", "QE_eV", "H_eV", "H_total_eV"))
        errors = compare_observables(high, reference, number_floor, energy_floor)
        heat_error = errors["H_total_eV"]
        heat_comparable = heat_error["reference_above_or_equal_floor"]
        heat_pass = (heat_error["relative_absolute_error"] <= D("0.01")) if heat_comparable else None
        heat_status = ("PASS_RESEARCH_DIAGNOSTIC" if heat_pass else "FAIL_RESEARCH_DIAGNOSTIC") if heat_comparable else "UNRESOLVED_BELOW_ABSOLUTE_FLOOR"
        samples = []
        for fraction_text in contract["numerics"]["optional_positivity_sample_fractions"]:
            fraction = D(fraction_text)
            elapsed = fraction * coeffs.h
            correction = (high["P1"] if fraction == ONE else correction_endpoint(field, elapsed, *rules[degree_high]))
            pf = field(elapsed)
            samples.append({"fraction": fraction, "frozen_P": pf, "e1": correction, "corrected_P": pf + correction})
        checks = {
            "finite": all_finite(calculations) and all_finite(samples) and all_finite(reference),
            "fixed_absorber_support_matches_saved": dict(zip(SPECIES, coeffs.mask)) == record["fixed_absorber_support"],
            "degree12_20_number_abs": max_number <= D(numerical["degree12_20_number_abs"]),
            "degree12_20_energy_eV_abs": max_energy <= D(numerical["degree12_20_energy_eV_abs"]),
            "number_first_variation_ledgers": max(abs(v["number_ledger"]) for v in calculations.values()) <= D(numerical["number_first_variation_ledger_abs"]),
            "energy_first_variation_ledgers": max(abs(v["energy_ledger_eV"]) for v in calculations.values()) <= D(numerical["energy_first_variation_ledger_eV_abs"]),
            "initial_correction_exact_zero": samples[0]["e1"] == ZERO and all(v["initial_correction"] == ZERO for v in calculations.values()),
        }
        result = {
            "key": record["key"],
            "input_row_exact_csv_strings": row,
            "stage_input_exact_csv_strings": stage,
            "fixed_absorber_support": dict(zip(SPECIES, coeffs.mask)),
            "source_on": coeffs.source_on,
            "local_initial_correction": ZERO,
            "lambda_f": field.lam, "Lambda_f": field.total, "q_f": field.q,
            "lambda_h": field.total * coeffs.h,
            "calculated_by_degree": calculations,
            "saved_signed_reference": reference,
            "degree20_minus_degree12": difference,
            "max_abs_degree_difference_number": max_number,
            "max_abs_degree_difference_energy_eV": max_energy,
            "first_variation_minus_saved_signed_reference": differences(high, reference),
            "approximation_errors": errors,
            "heat_defect_research_diagnostic": {"status": heat_status, "pass": heat_pass, "threshold": D("0.01"), **heat_error},
            "sampled_positivity": {"samples": samples, "all_nonnegative": all(v["corrected_P"] >= ZERO for v in samples),
                                   "minimum_sampled_corrected_P": min(v["corrected_P"] for v in samples),
                                   "scope": "Five point samples per segment, not a positivity enclosure."},
            "new_frozen_endpoint_minus_saved": high["frozen_endpoint_P1"] - D(record["frozen_exact_captured_coefficients"]["P1"]),
            "checks": checks,
            "numerical_status": "PASS_SCOPED" if all(checks.values()) else "FAIL",
        }
        results.append(result)
        numerical_failures.extend({"key": record["key"], "check": name, "failure_class": "NUMERICAL_OR_IMPLEMENTATION_UNRESOLVED"}
                                  for name, passed in checks.items() if not passed)
        if heat_pass is False:
            research_failures.append({"key": record["key"], "status": heat_status, "relative_heat_defect_error": heat_error["relative_absolute_error"]})
        print(json.dumps({"key": record["key"], "numerical_status": result["numerical_status"],
                          "heat_defect_diagnostic": heat_status, "relative_heat_defect_error": str(heat_error["relative_absolute_error"]),
                          "signed_heat_first_eV": str(high["H_total_eV"]), "signed_heat_saved_eV": str(reference["H_total_eV"])}), flush=True)
    for name, passed in limit_checks.items():
        if not passed:
            numerical_failures.append({"check": name, "failure_class": "THEORY_OR_IMPLEMENTATION"})
    for degree, checks in quadrature_checks.items():
        if not checks["pass"]:
            numerical_failures.append({"check": "Gauss polynomial moment", "degree": degree, "failure_class": "NUMERICAL"})
    summary = {
        "segments": len(results),
        "numerical_pass_count": sum(r["numerical_status"] == "PASS_SCOPED" for r in results),
        "research_heat_diagnostic_pass_count": sum(r["heat_defect_research_diagnostic"]["pass"] is True for r in results),
        "research_heat_diagnostic_below_floor_count": sum(r["heat_defect_research_diagnostic"]["pass"] is None for r in results),
        "max_relative_total_heat_defect_error": max((r["heat_defect_research_diagnostic"]["relative_absolute_error"] for r in results
                                                     if r["heat_defect_research_diagnostic"]["pass"] is not None), default=None),
        "max_abs_degree_difference_number": max(r["max_abs_degree_difference_number"] for r in results),
        "max_abs_degree_difference_energy_eV": max(r["max_abs_degree_difference_energy_eV"] for r in results),
        "max_abs_number_ledger": max(abs(v["number_ledger"]) for r in results for v in r["calculated_by_degree"].values()),
        "max_abs_energy_ledger_eV": max(abs(v["energy_ledger_eV"]) for r in results for v in r["calculated_by_degree"].values()),
        "sampled_positivity_all_nonnegative": all(r["sampled_positivity"]["all_nonnegative"] for r in results),
    }
    packet = {
        "schema_version": "1.0", "task": contract["task"], "role": contract["role"],
        "evidence_status": ["derived", "numerically checked", "implementation-verified"],
        "claim_ceiling": "Six local first coefficient-variation controls; numerical contributor only. No production admission, no old continuous-oracle rerun, no interval or global error certificate.",
        "equation_sign": "Signed continuous-minus-exact-captured-frozen first variation, each e_a=0.",
        "units": "P,A,QN in photon number per H nucleus per d eta; B,Z,QE,H in eV times that photon normalization.",
        "precision_decimal_digits": getcontext().prec, "degrees": [degree_low, degree_high],
        "chi_eV_exact_binary64_lift": chi,
        "started_utc": started_utc, "finished_utc": datetime.now(UTC).isoformat(),
        "elapsed_seconds": time.perf_counter() - started,
        "actual_command_argv": [sys.executable, *sys.argv],
        "actual_command_shell_display": shlex.join([sys.executable, *sys.argv]),
        "environment": {"python": sys.version, "python_implementation": platform.python_implementation(),
                        "platform": platform.platform(), "decimal_libmpdec_version": decimal.__libmpdec_version__, "modules": "stdlib only"},
        "new_code_sha256_as_run": source_sha_as_run,
        "new_code_path_as_run": str(Path(__file__).resolve()),
        "contract_sha256_as_run": sha256(args.contract),
        "input_identity": input_identity, "input_checks": input_checks,
        "shared_implementation": contract["independence"],
        "quadrature_rule_checks": quadrature_checks, "analytic_limit_checks": limit_checks,
        "results": results, "summary": summary,
        "numerical_failures": numerical_failures, "research_diagnostic_failures": research_failures,
        "numerical_verdict": "PASS_SCOPED" if not numerical_failures else "FAIL",
        "research_diagnostic_verdict": "PASS_SCOPED_RESEARCH_ONLY" if not research_failures and all(r["heat_defect_research_diagnostic"]["pass"] is True for r in results) else "FAIL_OR_UNRESOLVED",
        "protected_state": contract["protected_state"], "decision_reviewer_status": "NOT_THIS_CONTRIBUTOR",
    }
    write_json(args.output, packet)
    if numerical_failures or research_failures:
        first_failure = args.output.parent / "FIRST_FAILURE.json"
        if not first_failure.exists():
            write_json(first_failure, packet)
    print(json.dumps({"numerical_verdict": packet["numerical_verdict"], "research_diagnostic_verdict": packet["research_diagnostic_verdict"],
                      "summary": summary, "elapsed_seconds": packet["elapsed_seconds"], "output": str(args.output)}, default=str), flush=True)
    return 0 if not numerical_failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
