#!/usr/bin/env python3
"""Nominal compact Thomson pair envelope under the frozen local contract.

Only compact JSON inputs are read. No saved-history reconstruction is attempted.
Mathematical upper-sum statements do not make these binary64 values intervals.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRIC_SHA256 = "cf40a696ade5311a59010e450bd3518259a9a76207bd42ae675347f952d54129"


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def background_tuple():
    return (67.4 * 1e5 / 3.0856775814913673e24,
            0.315, 9.2e-5, 1.0 - 0.315 - 9.2e-5)


def require_shared_background(reference, candidate):
    if tuple(reference) != tuple(candidate):
        raise ValueError("shared-H hypothesis fails: background tuples differ")


def hubble(x, background):
    h0, om, radiation, lam = background
    if h0 <= 0 or min(om, radiation, lam) < 0:
        raise ValueError("positive H0 and nonnegative density parameters required")
    value = h0 * math.sqrt(radiation * math.exp(-4*x)
                           + om * math.exp(-3*x) + lam)
    if not math.isfinite(value) or value <= 0:
        raise ValueError("H must be finite and positive")
    return value


def kernel_moments(a, b, panels, background):
    if not b > a or panels <= 0:
        raise ValueError("positive interval width and panel count required")
    h = (b-a) / panels
    nodes = [a + j*h for j in range(panels+1)]
    nodes[0], nodes[-1] = a, b
    w = [1.0/hubble(x, background) for x in nodes]
    moments = {}
    for power in (1, 2):
        values = [v**power for v in w]
        left = h * math.fsum(values[:-1])
        right = h * math.fsum(values[1:])
        moments[str(power)] = {
            "left": left, "right": right,
            "upper_minus_lower": right-left,
            "endpoint_width_formula": h*(values[-1]-values[0]),
            "relative_bracket_width": (right-left)/right,
        }
    return {"panels": panels, "h": h, "H_a": 1/w[0], "H_b": 1/w[-1],
            "w_inf": w[-1], "raw_moments": moments,
            "W2_bracket": [math.sqrt(moments["2"]["left"]),
                           math.sqrt(moments["2"]["right"])],
            "quadrature_claim": "Exact-arithmetic monotone left/right enclosure; evaluated float values are not outward-rounded intervals"}


def envelope(norms, moments, c, sigma, units="cgs"):
    """Inputs must share a complete cgs or SI tuple; no mixed unit tuple accepted."""
    expected = {"cgs": ("cm/s", "cm^2", "cm^-3"),
                "SI": ("m/s", "m^2", "m^-3")}
    if isinstance(units, str):
        unit_tuple = expected.get(units)
    else:
        unit_tuple = tuple(units)
    if unit_tuple not in expected.values():
        raise ValueError("c, sigma and density must use one consistent unit tuple")
    if any(not math.isfinite(v) or v < 0 for v in norms.values()):
        raise ValueError("norms must be finite and nonnegative")
    k = c*sigma
    components = {
        "B_L1": k*norms["N1"]*moments["w_inf"],
        "B_L2": k*norms["N2"]*math.sqrt(moments["raw_moments"]["2"]["right"]),
        "B_Linf": k*norms["Ninf"]*moments["raw_moments"]["1"]["right"],
    }
    selected = min(components, key=components.get)
    bound = components[selected]
    return {"K": k, "components": components, "selected": selected, "B": bound,
            "q": -math.expm1(-bound), "units": list(unit_tuple)}


def decimal_reference(a, b, panels, norms, constants):
    """Independent 50-digit exp/sqrt, sums and scalar evaluation, no float kernel."""
    with localcontext() as ctx:
        ctx.prec = 50
        d = Decimal
        # Stored coordinates/norms are the exact parsed binary64 inputs.
        da, db = d.from_float(a), d.from_float(b)
        h = (db-da)/d(panels)
        h0 = d("67.4")*d("1e5")/d("3.0856775814913673e24")
        om, rad = d("0.315"), d("9.2e-5")
        lam = d(1)-om-rad
        kernels = []
        for j in range(panels+1):
            x = db if j == panels else da+d(j)*h
            hub = h0*(rad*(-4*x).exp()+om*(-3*x).exp()+lam).sqrt()
            kernels.append(1/hub)
        u1 = h*sum(kernels[1:], d(0))
        u2 = h*sum((v*v for v in kernels[1:]), d(0))
        k = d(str(constants["c_cm_per_s"]))*d(str(constants["sigma_T_cm2"]))
        comp = {"B_L1": k*d.from_float(norms["N1"])*kernels[-1],
                "B_L2": k*d.from_float(norms["N2"])*u2.sqrt(),
                "B_Linf": k*d.from_float(norms["Ninf"])*u1}
        bound = min(comp.values())
        values = {"H_a": 1/kernels[0], "H_b": 1/kernels[-1],
                  "w_inf": kernels[-1], "U1": u1, "U2": u2,
                  "K": k, **comp, "B": bound, "q": 1-(-bound).exp()}
        return {"precision_digits": 50,
                "input_convention": "Exact parsed binary64 coordinates/norms; nominal decimal constants/background expressions",
                "values": {key: str(value) for key, value in values.items()}}


def select_metrics(raw, contract):
    expected = contract["immutable_metric_selection"]
    data = json.loads(raw)
    for key in ("coordinate", "arithmetic", "reference", "candidate", "overlap",
                "overlap_width", "union_knots"):
        if data[key] != expected[key]:
            raise ValueError(f"frozen metric mismatch: {key}")
    rows = [row for row in data["summary"] if row["observable"] == expected["observable"]]
    if len(rows) != 1 or rows[0]["units"] != expected["units"]:
        raise ValueError("exactly one ne_cm3 row with frozen cm^-3 units required")
    row = rows[0]
    mapping = {"Ninf": "sup_absolute_difference", "N1": "l1_integral", "N2": "l2_norm"}
    norms = {key: row[source] for key, source in mapping.items()}
    for key, value in norms.items():
        if value != expected[key]:
            raise ValueError(f"frozen metric mismatch: {key}")
    return data, norms, mapping


def evaluate(metrics_path, contract_path=None, binding_path=None):
    contract_path = contract_path or ROOT / "spec/THOMSON_PAIR_CONTRACT.json"
    binding_path = binding_path or ROOT / "intake/BACKGROUND_BINDING.json"
    contract = json.loads(Path(contract_path).read_text())
    raw = Path(metrics_path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != METRIC_SHA256:
        raise ValueError("BYTE_IDENTITY_MISMATCH: immutable compact metric input")
    data, norms, mapping = select_metrics(raw, contract)
    binding = json.loads(Path(binding_path).read_text())
    expected_bg = contract["background"]
    if (binding["metric_sha256"] != digest
            or binding["driver_source_commit"] != expected_bg["parameter_source_commit"]
            or not binding["shared_background_supported"]
            or binding["q_ref"] != 0
            or binding["Omega_m"] != expected_bg["Omega_m"]
            or binding["Omega_r"] != expected_bg["Omega_r"]
            or binding["H0_expression_per_s"] != expected_bg["H0_expression_per_s"]):
        raise ValueError("frozen background dependency mismatch")
    bg = background_tuple()
    require_shared_background(bg, bg)
    a, b = data["overlap"]
    moments = kernel_moments(a, b, contract["algorithm"]["panels"], bg)
    constants = contract["constants"]
    bound = envelope(norms, moments, constants["c_cm_per_s"], constants["sigma_T_cm2"])
    decimal = decimal_reference(a, b, moments["panels"], norms, constants)
    acceptance = contract["acceptance"]
    rtol, atol = acceptance["actual_scalar_reference_rtol"], acceptance["actual_scalar_reference_atol"]
    floats = {"H_a": moments["H_a"], "H_b": moments["H_b"], "w_inf": moments["w_inf"],
              "U1": moments["raw_moments"]["1"]["right"],
              "U2": moments["raw_moments"]["2"]["right"],
              "K": bound["K"], **bound["components"], "B": bound["B"], "q": bound["q"]}
    scalar_checks = {key: {"float": value, "decimal": decimal["values"][key],
                          "pass": math.isclose(value, float(decimal["values"][key]), rel_tol=rtol, abs_tol=atol)}
                     for key, value in floats.items()}
    nr = acceptance["norm_consistency_rtol"]
    checks = {"norm_N1_le_sqrt_width_N2": norms["N1"] <= math.sqrt(b-a)*norms["N2"]*(1+nr),
              "norm_N2_le_sqrt_width_Ninf": norms["N2"] <= math.sqrt(b-a)*norms["Ninf"]*(1+nr),
              "q_probability_range": 0 <= bound["q"] <= 1,
              "q_le_B": bound["q"] <= bound["B"],
              "decimal_scalar_reference": all(v["pass"] for v in scalar_checks.values())}
    matter = {"1": 2*(math.exp(1.5*b)-math.exp(1.5*a))/(3*bg[0]*math.sqrt(bg[1])),
              "2": (math.exp(3*b)-math.exp(3*a))/(3*bg[0]**2*bg[1])}
    for p, row in moments["raw_moments"].items():
        checks[f"moment_{p}_relative_width"] = row["relative_bracket_width"] <= acceptance["riemann_moment_relative_bracket_width_max"]
        checks[f"moment_{p}_endpoint_identity"] = math.isclose(row["upper_minus_lower"], row["endpoint_width_formula"], rel_tol=acceptance["numeric_fixture_rtol"], abs_tol=acceptance["numeric_fixture_atol"])
        checks[f"moment_{p}_matter_bound_with_slack"] = row["right"] <= matter[p]+row["upper_minus_lower"]
    passed = all(checks.values())
    return {
        "schema_version": 1, "unit_id": contract["unit_id"],
        "implementation_checks_status": "PASS" if passed else "FAIL",
        "theorem_status": "DERIVED_UNDER_STATED_ASSUMPTIONS",
        "evaluation_status": "NOMINAL_BINARY64_SUMMARY_CONDITIONAL",
        "numerical_claim": "Floating formula evaluation; published norms and computed moments have no outward rounding enclosure",
        "solver_convergence": "HOLD", "continuum_accuracy": "HOLD",
        "input": {"path": str(metrics_path), "sha256": digest,
                  "source_result_commit": contract["source_result_commit"],
                  "repository_anchor": contract["current_repository_anchor"],
                  "selection": contract["immutable_metric_selection"], "norm_field_mapping": mapping,
                  "norm_units": "cm^-3", "coordinate_measure": "dx=d ln(a), dimensionless"},
        "background": {"tuple_order": ["H0_per_s", "Omega_m", "Omega_r", "Omega_Lambda"],
                       "tuple": list(bg), "binding_state": binding["status"],
                       "shared_between_pairs": True, "q_ref": binding["q_ref"],
                       "evidence_scope": binding["scope"], "compiled_aggregate_reassembled": False,
                       "receipt": str(binding_path.relative_to(ROOT)) if binding_path.is_relative_to(ROOT) else str(binding_path)},
        "constants": constants, "assumptions": contract["assumptions"],
        "kernel_moments": moments, "matter_only_exact_upper_moments": matter,
        "optical_depth_envelope": bound,
        "probability_envelope": {"absolute_transmission_difference_max": bound["q"],
                                 "last_scattering_total_variation_max": bound["q"],
                                 "each_bin_CDF_no_scatter_difference_max": bound["q"],
                                 "includes_distinct_no_scatter_state": True,
                                 "visibility_density_pointwise_bound_claimed": False,
                                 "interval": [a, b], "outside_overlap_claimed": False},
        "decimal_reference": decimal, "scalar_reference_checks": scalar_checks,
        "checks": checks, "acceptance_tolerances": acceptance,
        "scientific_admission": "PENDING_FRESH_ASTRA_REVIEW",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = evaluate(args.metrics)
    write_json(args.output, result)
    print(json.dumps({"status": result["implementation_checks_status"],
                      "B": result["optical_depth_envelope"]["B"],
                      "q": result["optical_depth_envelope"]["q"],
                      "selected": result["optical_depth_envelope"]["selected"],
                      "panels": result["kernel_moments"]["panels"],
                      "solver_convergence": "HOLD"}))
    return 0 if result["implementation_checks_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
