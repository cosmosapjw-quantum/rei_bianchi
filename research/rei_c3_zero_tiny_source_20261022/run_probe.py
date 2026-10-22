"""One prescribed manufactured-fixture verification pass, Decimal precision 100."""
import hashlib
import json
import math
from pathlib import Path
import resource
import sys
import time
import traceback
from decimal import Decimal as D, getcontext
from local_source import Event, UnresolvedInput, evaluate

ROOT = Path(__file__).resolve().parent
getcontext().prec = 100
START_WALL, START_CPU = time.perf_counter(), time.process_time()
resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
resource.setrlimit(resource.RLIMIT_AS, (256 * 1024**2, 256 * 1024**2))
BINDINGS = json.loads((ROOT / "input/BINDINGS.json").read_text())
SLOTS = BINDINGS["slots"]
assert [s["index"] for s in SLOTS] == list(range(21))
INDEX = {s["name"]: s["index"] for s in SLOTS}
TOL = D("2e-12")
RESULT = {"schema": "rei-c3-manufactured-probe-v1", "status": "RUNNING",
          "fixture_label": "MANUFACTURED", "decimal_precision": 100,
          "relative_tolerance": str(TOL), "fixtures": [], "controls": [],
          "scope": "local representation only; no physical coefficient/branch admission"}


def vector(values, default="0"):
    out = [default] * 21
    for name, value in values.items():
        out[INDEX[name]] = value
    return out


def event(name, reactants, products, k):
    return {"name": name, "reactants": {INDEX[j]: m for j, m in reactants.items()},
            "products": {INDEX[j]: m for j, m in products.items()},
            "k_decimal": k, "label": "MANUFACTURED"}


def instantiate(declaration, applicability="ACTIVE"):
    return Event(declaration["name"], declaration["reactants"], declaration["products"],
                 math.log(float(declaration["k_decimal"])), applicability)


def oracle(declarations, y, scales, n_b):
    """Direct Decimal coefficient/products, independent of logarithmic path."""
    yd, sd, nb = list(map(D, y)), list(map(D, scales)), D(n_b)
    source = [D(0)] * 21
    magnitude = [D(0)] * 21
    jac = [[D(0)] * 21 for _ in range(21)]
    rates, balances = [], []
    for e in declarations:
        m = e["reactants"]
        nu = {j: e["products"].get(j, 0) - m.get(j, 0)
              for j in e["products"].keys() | m.keys()}
        prefactor = D(e["k_decimal"]) * nb ** (sum(m.values()) - 1)
        for multiplicity in m.values():
            prefactor /= D(math.factorial(multiplicity))
        rate = prefactor
        for j, exponent in m.items():
            rate *= yd[j] ** exponent
        rates.append(rate)
        # Reconstruct physical conservation without binary64 underflow.
        baryon = sum((D(SLOTS[i]["A"] * v) * rate for i, v in nu.items()), D(0))
        charge_identity = sum((D(SLOTS[i]["q"] + SLOTS[i]["Z"] - SLOTS[i]["q"]
                                 - SLOTS[i]["Z"]) * v * rate for i, v in nu.items()), D(0))
        assert baryon == 0 and charge_identity == 0
        balances.append({"baryon_residual": str(baryon), "electron_bound_Z_residual": str(charge_identity),
                         "positive_event_decimal": rate > 0})
        for i, v in nu.items():
            term = D(v) * rate / sd[i]
            source[i] += term
            magnitude[i] += abs(term)
        for j, multiplicity in m.items():
            derivative = prefactor * D(multiplicity)
            for l, exponent in m.items():
                reduced = exponent - (l == j)
                if reduced:
                    derivative *= yd[l] ** reduced
            for i, v in nu.items():
                jac[i][j] += D(v) * derivative * sd[j] / sd[i]
    return rates, source, jac, magnitude, balances


def comparison(actual, reference, tolerance=TOL, denominator=None):
    error = abs(D.from_float(actual) - reference)
    denom = abs(reference) if denominator is None else denominator
    passed = error == 0 if denom == 0 else error <= tolerance * denom
    return {"actual": actual, "decimal_reference": str(reference),
            "absolute_error": str(error), "denominator": str(denom),
            "relative_error": None if denom == 0 else str(error / denom),
            "tolerance": str(tolerance), "pass": passed}


def run_fixture(name, declarations, values, scale_values, n_b, statuses):
    y, scales = vector(values), vector(scale_values, "1")
    record = {"name": name, "label": "MANUFACTURED", "declarations": declarations,
              "Y_decimal": y, "scales_decimal": scales, "n_B_decimal": n_b,
              "expected_statuses": statuses}
    RESULT["fixtures"].append(record)
    output = evaluate([instantiate(e) for e in declarations], SLOTS,
                      list(map(float, y)), list(map(float, scales)), float(n_b))
    rates, source, jac, magnitude, balances = oracle(declarations, y, scales, n_b)
    record["output"] = output
    expected_bookkeeping = {
        "DD": {"A_dot_nu": 0, "delta_e": 0, "delta_bound": 0, "Z_dot_nu": 0, "delta_N": 0, "delta_C": 0},
        "supplied_beta_endpoint": {"A_dot_nu": 0, "delta_e": 1, "delta_bound": 0, "Z_dot_nu": 1, "delta_N": 0, "delta_C": 1},
        "supplied_binary_endpoint": {"A_dot_nu": 0, "delta_e": 0, "delta_bound": 0, "Z_dot_nu": 0, "delta_N": -1, "delta_C": -1}}
    record["integer_bookkeeping_references"] = [expected_bookkeeping[e["name"]] for e in declarations]
    assert [e["bookkeeping"] for e in output["events"]] == record["integer_bookkeeping_references"]
    record["decimal_conservation"] = balances
    record["rate_checks"] = [comparison(e["raw_rate"], r) if float(r) != 0 or r == 0
                             else {"actual": e["raw_rate"], "decimal_reference": str(r),
                                   "expected_projection": 0.0, "pass": e["raw_rate"] == 0.0,
                                   "retained_log_rate": e["log_rate"]}
                             for e, r in zip(output["events"], rates)]
    record["source_checks"] = [comparison(a, r, denominator=d)
                               for a, r, d in zip(output["scaled_source"], source, magnitude)]
    record["jacobian_checks"] = [[comparison(a, r) for a, r in zip(arow, rrow)]
                                  for arow, rrow in zip(output["scaled_jacobian"], jac)]
    record["pass"] = ([e["status"] for e in output["events"]] == statuses
                       and all(c["pass"] for c in record["rate_checks"] + record["source_checks"])
                       and all(c["pass"] for row in record["jacobian_checks"] for c in row))
    assert record["pass"], name
    return record


def main():
    dd = event("DD", {"DII": 2}, {"TII": 1, "H1II": 1}, "2e-20")
    tiny_dd = dict(dd, k_decimal="1")
    beta = event("supplied_beta_endpoint", {"TI": 1}, {"He3II": 1}, "1e-230")
    fusion = event("supplied_binary_endpoint", {"DII": 1, "H1II": 1}, {"He3III": 1}, "1e-100")
    ordinary = run_fixture("ordinary_DD", [dd], {"DII": "0.02", "H1I": "0.96"}, {}, "3", ["ACTIVE"])
    assert D(ordinary["rate_checks"][0]["decimal_reference"]) == D("1.2e-23")
    assert ordinary["output"]["scaled_source"][INDEX["TII"]] > 0
    assert sum((D(s["A"]) * D(v) for s, v in zip(SLOTS, ordinary["Y_decimal"])), D(0)) == 1
    tiny = run_fixture("tiny_DD", [tiny_dd], {"DII": "1e-104"},
                       {"DII": "1e-104", "TII": "1e-104", "H1II": "1e-104"}, "1", ["ACTIVE"])
    under = run_fixture("underflow_unary", [beta], {"TI": "1e-104"},
                        {"TI": "1e-104", "He3II": "1e-104"}, "1", ["UNDERFLOW"])
    zero_beta = run_fixture("zero_stock_unary", [beta], {},
                            {"TI": "1e-104", "He3II": "1e-104"}, "1", ["ZERO_REACTANT"])
    onset = run_fixture("one_zero_binary", [fusion], {"H1II": "0.5"},
                        {"DII": "1e-104", "He3III": "1e-104"}, "1", ["ZERO_REACTANT"])
    assert onset["output"]["events"][0]["bookkeeping"] == {
        "A_dot_nu": 0, "delta_e": 0, "delta_bound": 0, "Z_dot_nu": 0, "delta_N": -1, "delta_C": -1}
    run_fixture("DD_zero_boundary", [tiny_dd], {}, {"DII": "1e-104", "TII": "1e-104", "H1II": "1e-104"},
                "1", ["ZERO_REACTANT"])
    status_records = []
    for declaration in (dd, beta, fusion):
        for status in ("SUPPORT_ZERO", "ABSENT", "UNRESOLVED"):
            entry = {"label": "MANUFACTURED", "event": declaration, "applicability": status}
            status_records.append(entry)
            try:
                out = evaluate([instantiate(declaration, status)], SLOTS, [0.] * 21, [1.] * 21, 1.)
                entry["output"] = out
                entry["pass"] = (status != "UNRESOLVED" and out["events"][0]["status"] == status
                                 and all(v == 0 for v in out["scaled_source"])
                                 and all(v == 0 for row in out["scaled_jacobian"] for v in row))
            except UnresolvedInput as exc:
                entry["observed_exception"] = str(exc)
                entry["pass"] = status == "UNRESOLVED"
            assert entry["pass"]
    RESULT["status_controls"] = status_records
    invalid = event("nonconserving", {"DII": 1}, {"H1II": 1}, "1")
    rejection = {"name": "nonconserving_rejection", "label": "MANUFACTURED", "declaration": invalid}
    RESULT["controls"].append(rejection)
    try:
        evaluate([instantiate(invalid)], SLOTS, [1.] * 21, [1.] * 21, 1.)
    except ValueError as exc:
        rejection.update(observed_exception=str(exc), **{"pass": "nonconserving" in str(exc)})
    assert rejection.get("pass", False)

    moderate_declarations = [dict(dd, k_decimal="0.7"), dict(fusion, k_decimal="0.3")]
    moderate = run_fixture("moderate_two_event_sum", moderate_declarations,
                           {"DII": "0.1", "H1II": "0.2", "TII": "0.01", "He3III": "0.03"},
                           {"DII": "0.05", "H1II": "0.08", "TII": "0.03", "He3III": "0.02"},
                           "2", ["ACTIVE", "ACTIVE"])
    ys = list(map(float, moderate["Y_decimal"]))
    scales = list(map(float, moderate["scales_decimal"]))
    fd = {"name": "moderate_central_differences", "label": "MANUFACTURED", "checks": [],
          "step_rule": "h=1e-5*abs(u_j); only positive moderate reactant coordinates",
          "scope": "central polynomial truncation and binary64 subtraction roundoff only; no boundary/underflow certification"}
    RESULT["controls"].append(fd)
    for j in (INDEX["DII"], INDEX["H1II"]):
        u = ys[j] / scales[j]
        h = 1e-5 * abs(u)
        yp, ym = list(ys), list(ys)
        yp[j], ym[j] = (u + h) * scales[j], (u - h) * scales[j]
        assert ym[j] > 0
        fp = evaluate([instantiate(e) for e in moderate_declarations], SLOTS, yp, scales, 2.)["scaled_source"]
        fm = evaluate([instantiate(e) for e in moderate_declarations], SLOTS, ym, scales, 2.)["scaled_source"]
        for i in range(21):
            check = comparison((fp[i] - fm[i]) / (2 * h),
                               D.from_float(moderate["output"]["scaled_jacobian"][i][j]), D("2e-7"))
            check.update(i=i, j=j, h=h, positive_perturbed_Y=[ym[j], yp[j]])
            fd["checks"].append(check)
            assert check["pass"]
    fd["pass"] = True
    naive = float("1e-230") * float("1e-104") / float("1e-104")
    positive_scaled = under["output"]["scaled_source"][INDEX["He3II"]]
    RESULT["controls"].append({"name": "naive_raw_before_scale_negative_control", "label": "MANUFACTURED",
                               "naive": naive, "accepted_scaled": positive_scaled,
                               "pass": naive == 0 and positive_scaled > 0, "rejected_by_positive_oracle": True})
    try:
        quotient = 0.0 / 0.0
    except ZeroDivisionError as exc:
        quotient = type(exc).__name__
    analytic = zero_beta["output"]["scaled_jacobian"][INDEX["He3II"]][INDEX["TI"]]
    RESULT["controls"].append({"name": "quotient_at_zero_negative_control", "label": "MANUFACTURED",
                               "naive_quotient": quotient, "accepted_boundary_jacobian": analytic,
                               "pass": quotient == "ZeroDivisionError" and analytic > 0})
    mapping = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 17, 18, 19, 20]
    projection_y = vector({"DII": "0.02", "H1I": "0.95999994", "Li6I": "1e-8"})
    full_d = sum((D(s["A"]) * D(y) for s, y in zip(SLOTS, projection_y)), D(0))
    projected_d = sum((D(SLOTS[j]["A"]) * D(projection_y[j]) for j in mapping), D(0))
    full_f = math.fsum(s["A"] * float(y) for s, y in zip(SLOTS, projection_y))
    projected_f = math.fsum(SLOTS[j]["A"] * float(projection_y[j]) for j in mapping)
    omitted = D("6e-8")
    error = abs(D.from_float(1.0 - projected_f) - omitted)
    # Subtraction near unity has an absolute binary64 roundoff bound.
    roundoff = D.from_float(4 * math.ulp(1.0))
    projection = {"name": "17_to_21_projection_nonrenormalization", "label": "MANUFACTURED",
                  "map_17_to_21": mapping, "names_17": [SLOTS[j]["name"] for j in mapping],
                  "full_Y_decimal": projection_y, "projected_Y_decimal": [projection_y[j] for j in mapping],
                  "full_A_dot_Y_decimal": str(full_d), "projected_A_dot_Y_decimal": str(projected_d),
                  "full_A_dot_Y_binary64": full_f, "projected_A_dot_Y_binary64": projected_f,
                  "omitted_Li6_baryons_decimal": str(omitted), "deficit_error": str(error),
                  "roundoff_criterion_4_ulp_at_unity": str(roundoff), "renormalized": False,
                  "pass": full_d == 1 and 1 - projected_d == omitted and error <= roundoff
                          and abs(full_f - 1) <= float(roundoff)}
    RESULT["controls"].append(projection)
    assert projection["pass"]
    assert all(c["pass"] for c in RESULT["controls"])
    RESULT["status"] = "PASS"


if __name__ == "__main__":
    exit_code = 0
    try:
        main()
    except Exception:
        exit_code = 1
        RESULT["status"] = "FAIL"
        RESULT["failure_traceback"] = traceback.format_exc()
        traceback.print_exc()
    finally:
        (ROOT / "RESULT.json").write_text(json.dumps(RESULT, indent=2, allow_nan=False) + "\n")
        paths = [ROOT / "local_source.py", ROOT / "run_probe.py", ROOT / "input/BINDINGS.json", ROOT.parent / "C3_FROZEN_CONTRACT.md"]
        execution = {"command": "timeout 30s python3 -B run_probe.py > stdout.txt 2> stderr.txt",
                     "cwd": str(ROOT), "python_version": sys.version, "platform": sys.platform,
                     "invocations": 1, "exit_code": exit_code,
                     "wall_seconds": time.perf_counter() - START_WALL,
                     "cpu_seconds": time.process_time() - START_CPU,
                     "max_rss_KiB_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                     "limits": {"wall_seconds": 30, "cpu_seconds": 30, "address_space_bytes": 256 * 1024**2,
                                "scientific_processes": 1, "thread_pool": False},
                     "sha256": {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else "../" + p.name:
                                hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                     "requested_model": "gpt-6.1-sol", "observed_model": "NOT_EXPOSED",
                     "result_status": RESULT["status"]}
        (ROOT / "EXECUTION.json").write_text(json.dumps(execution, indent=2) + "\n")
        print(json.dumps({"status": RESULT["status"], "fixtures": len(RESULT["fixtures"]),
                          "status_controls": len(RESULT.get("status_controls", [])),
                          "controls": len(RESULT["controls"]), "exit_code": exit_code}))
    sys.exit(exit_code)
