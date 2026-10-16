#!/usr/bin/env python3
"""Independent R7 exact-rational synthetic oracle, with no production import.

Fraction Gauss-Jordan elimination computes both correction and exact inverse.
The eight cases are frozen by ../FIXTURE_SPEC.json; synthetic inequality passes
do not identify an accepted production stage or certify a nonlinear error.
"""
from __future__ import annotations

from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import json
import platform
from pathlib import Path
import resource
import time


HERE = Path(__file__).resolve().parent
SPEC_PATH = HERE.parent / "FIXTURE_SPEC.json"


def vector_inf(v):
    return max(map(abs, v), default=Q(0))


def matrix_inf(a):
    return max(sum(map(abs, row), Q(0)) for row in a)


def matvec(a, v):
    return [sum((x*y for x, y in zip(row, v)), Q(0)) for row in a]


def identity(n=4):
    return [[Q(int(i == j)) for j in range(n)] for i in range(n)]


def diagonal(v):
    return [[x if i == j else Q(0) for j in range(len(v))] for i, x in enumerate(v)]


def inverse_exact(a):
    """Exact Gauss-Jordan inverse, using rational pivots, no tolerance."""
    n = len(a)
    augmented = [list(row) + tail for row, tail in zip(a, identity(n))]
    for col in range(n):
        pivot = next((i for i in range(col, n) if augmented[i][col]), None)
        if pivot is None:
            raise ArithmeticError("HOLD_SINGULAR_JACOBIAN")
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        scale = augmented[col][col]
        augmented[col] = [x/scale for x in augmented[col]]
        for row in range(n):
            if row != col:
                scale = augmented[row][col]
                augmented[row] = [x-scale*y for x, y in zip(augmented[row], augmented[col])]
    return [row[n:] for row in augmented]


def temperature(y, f_he, k_b):
    x, he2, he3, w = y
    if not (0 <= x <= 1 and he2 >= 0 and he3 >= 0 and he2+he3 <= 1 and w > 0):
        return None
    denom = 1 + f_he + x + f_he*(he2+2*he3)
    return 2*w/(3*k_b*denom)


def thermal_projection(y, delta, f_he, k_b):
    x, he2, he3, w = y
    denom = 1 + f_he + x + f_he*(he2+2*he3)
    d_denom = delta[0] + f_he*(delta[1]+2*delta[2])
    linear = 2/(3*k_b*denom)*(delta[3]-w*d_denom/denom)
    corrected = [a+b for a, b in zip(y, delta)]
    before, after = temperature(y, f_he, k_b), temperature(corrected, f_he, k_b)
    return {"temperature_before": before, "temperature_corrected": after,
            "delta_temperature_linear": linear,
            "delta_temperature_exact_map": None if after is None else after-before,
            "corrected_state": corrected,
            "corrected_domain": "VALID" if after is not None else "INVALID_FRACTION_OR_ENERGY"}


def packet(y, residual, jacobian, fraction_floor, energy_floor, f_he, k_b):
    """Exact oracle for a synthetic same-state R/J packet; SR is frozen."""
    residual_scale = [Q(1), Q(1), Q(1), max(abs(y[3]), energy_floor)]
    state_scale = [max(abs(v), fraction_floor) for v in y[:3]] + [max(abs(y[3]), energy_floor)]
    a = [[jacobian[i][j]*state_scale[j]/residual_scale[i] for j in range(4)] for i in range(4)]
    b = [r/s for r, s in zip(residual, residual_scale)]
    out = {"scope": "SYNTHETIC_SAME_STATE_CHEMICAL_PACKET_ONLY",
           "state": y, "old_state": y, "residual": residual, "jacobian": jacobian,
           "residual_scale": residual_scale, "state_scale": state_scale, "A": a, "b": b,
           "native_scaled_residual_inf": vector_inf(b),
           "passes_production_residual_inequality_synthetic_only": vector_inf(b) <= Q("1e-11")}
    try:
        inv_a = inverse_exact(a)
        inv_j = inverse_exact(jacobian)
    except ArithmeticError:
        out.update(status="HOLD_SINGULAR_JACOBIAN", scaled_correction=None,
                   delta=None, kappa_inf=None, linear_backward_error=None, thermal=None)
        return out
    z = [-v for v in matvec(inv_a, b)]
    delta = [s*v for s, v in zip(state_scale, z)]
    direct_delta = [-v for v in matvec(inv_j, residual)]
    assert delta == direct_delta
    equation_residual = [u+v for u, v in zip(matvec(a, z), b)]
    denominator = matrix_inf(a)*vector_inf(z) + vector_inf(b)
    backward_error = vector_inf(equation_residual)/denominator if denominator else Q(0)
    assert vector_inf(equation_residual) == 0
    out.update(status="EXACT_LINEAR_CORRECTION_ONLY", inverse_A=inv_a,
               scaled_correction=z, scaled_correction_inf=vector_inf(z), delta=delta,
               direct_and_scaled_solve_equal=True,
               kappa_inf=matrix_inf(a)*matrix_inf(inv_a),
               linear_equation_residual=equation_residual, linear_backward_error=backward_error,
               thermal=thermal_projection(y, delta, f_he, k_b))
    return out


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, list):
        return [encode(x) for x in value]
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    return value


def decimal_string(q):
    return str(Decimal(q.numerator)/Decimal(q.denominator))


def main():
    wall_start, cpu_start = time.perf_counter(), time.process_time()
    spec = json.loads(SPEC_PATH.read_text())
    assert len(spec["fixtures"]) == 8
    y = list(map(Q, spec["base_state"]))
    r = list(map(Q, spec["base_residual"]))
    ff, ef, f_he, k_b = map(Q, (spec["fraction_floor"], spec["energy_floor"],
                                spec["f_He"], spec["k_B_eV_per_K"]))
    common = (ff, ef, f_he, k_b)
    cases = {}
    cases["identity"] = packet(y, r, identity(), *common)
    assert cases["identity"]["delta"] == [-v for v in r]
    assert cases["identity"]["thermal"]["corrected_domain"] == "VALID"
    coupled_spec = next(x for x in spec["fixtures"] if x["id"] == "coupled")
    coupled_j = [[Q(x) for x in row] for row in coupled_spec["J"]]
    cases["coupled"] = packet(y, r, coupled_j, *common)
    assert cases["coupled"]["thermal"]["corrected_domain"] == "VALID"
    for key in ("floor_bridge", "large_inverse", "singular"):
        fixture = next(x for x in spec["fixtures"] if x["id"] == key)
        jac = identity() if fixture.get("J") == "I4" else diagonal(list(map(Q, fixture["J_diagonal"])))
        fixture_residual = r if fixture["R"] == "base_residual" else list(map(Q, fixture["R"]))
        cases[key] = packet(y, fixture_residual, jac, *common)
    bridge = cases["floor_bridge"]
    assert bridge["native_scaled_residual_inf"] == Q("1e-11")
    assert bridge["scaled_correction_inf"] == Q("1e-6")
    bridge["correction_ratio_to_local_target"] = bridge["scaled_correction_inf"]/Q(spec["target"])
    assert bridge["correction_ratio_to_local_target"] == Q("1/10")
    large = cases["large_inverse"]
    assert large["delta"][0] == -Q("1/1000") and large["scaled_correction_inf"] == 5
    assert large["thermal"]["temperature_corrected"] is None
    assert cases["singular"]["status"] == "HOLD_SINGULAR_JACOBIAN"

    unit_spec = next(x for x in spec["fixtures"] if x["id"] == "energy_unit_change")
    u = Q(unit_spec["u"])
    transform = [Q(1), Q(1), Q(1), u]
    transformed_j = [[transform[i]*coupled_j[i][j]/transform[j] for j in range(4)] for i in range(4)]
    transformed = packet([p*v for p, v in zip(transform, y)],
                         [p*v for p, v in zip(transform, r)], transformed_j,
                         ff, u*ef, f_he, u*k_b)
    original = cases["coupled"]
    for field in ("A", "b", "scaled_correction", "scaled_correction_inf", "kappa_inf", "linear_backward_error"):
        assert transformed[field] == original[field], field
    for field in ("temperature_before", "temperature_corrected", "delta_temperature_linear", "delta_temperature_exact_map"):
        assert transformed["thermal"][field] == original["thermal"][field], field
    assert transformed["delta"] == [p*v for p, v in zip(transform, original["delta"])]
    transformed["unit_transform_exact_invariance"] = True
    cases["energy_unit_change"] = transformed

    eos_spec = next(x for x in spec["fixtures"] if x["id"] == "EOS_composition_cancellation")
    eos_y = list(map(Q, eos_spec["y"]))
    delta_species = list(map(Q, eos_spec["delta_species"]))
    denom = 1 + f_he + eos_y[0] + f_he*(eos_y[1]+2*eos_y[2])
    d_denom = delta_species[0]+f_he*(delta_species[1]+2*delta_species[2])
    eos_delta = delta_species+[eos_y[3]*d_denom/denom]
    eos = packet(eos_y, [-v for v in eos_delta], identity(), *common)
    assert eos["thermal"]["corrected_domain"] == "VALID"
    assert eos["scaled_correction_inf"] > 0
    assert eos["thermal"]["delta_temperature_linear"] == 0
    assert eos["thermal"]["delta_temperature_exact_map"] == 0
    cases["EOS_composition_cancellation"] = eos

    be_spec = next(x for x in spec["fixtures"] if x["id"] == "BE_pair_cancellation")
    be_z, y0, ra, rb, rf = map(Q, (be_spec["z"], be_spec["y0"], be_spec["rA"], be_spec["rB"], be_spec["rF"]))
    q, qh = 1/(1+be_z), 1/(1+be_z/2)
    exact_full, exact_fine = q*y0, qh*qh*y0
    observed_full = q*(y0+rf)
    half_a = qh*(y0+ra)
    observed_fine = qh*(half_a+rb)
    assert observed_full == observed_fine
    assert exact_fine != exact_full and abs(rf) < Q("1e-11")
    assert rf == (1+be_z)*(qh*qh-q)*y0
    with localcontext() as ctx:
        ctx.prec = 80
        decay_exact_decimal = (-Decimal(be_z.numerator)/Decimal(be_z.denominator)).exp()*Decimal(y0.numerator)/Decimal(y0.denominator)
        fine_decimal = Decimal(exact_fine.numerator)/Decimal(exact_fine.denominator)
        fine_error = fine_decimal-decay_exact_decimal
        assert fine_error != 0
        be = {"scope": "SYNTHETIC_SCALAR_BACKWARD_EULER_ONLY", "z": be_z, "y0": y0,
              "q": q, "qh": qh, "rA": ra, "rB": rb, "rF": rf,
              "exact_BE_full": exact_full, "exact_BE_fine": exact_fine,
              "exact_BE_pair_difference": exact_fine-exact_full,
              "observed_full": observed_full, "observed_fine": observed_fine,
              "observed_pair_difference": observed_fine-observed_full,
              "passes_residual_inequality_synthetic_only": abs(rf) <= Q("1e-11"),
              "fine_minus_exp_minus_z_decimal80": str(fine_error),
              "exp_minus_z_decimal80": str(decay_exact_decimal),
              "decimal_precision": 80, "actual_production_stage": False}
    cases["BE_pair_cancellation"] = be

    for key, result in cases.items():
        status = result.get("status", "EXACT_PAIR_CANCELLATION")
        print(key + ": " + status)
        for field in ("native_scaled_residual_inf", "scaled_correction_inf", "kappa_inf", "linear_backward_error",
                      "exact_BE_pair_difference", "observed_pair_difference", "fine_minus_exp_minus_z_decimal80"):
            if field in result:
                print("  " + field + "=" + str(result[field]))
    result = {"schema_version": 1, "workflow_version": "1.0.0",
              "unit_id": "flrw_nonlinear_error_budget_20261016", "stage": "R7",
              "scope": "Independent exact-rational synthetic fixture oracle; not actual stage attribution",
              "execution_status": "completed", "checks": "PASS_SCOPED_EIGHT_SYNTHETIC_CASES",
              "source": {"spec_sha256": hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest(),
                         "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
              "method": "Fraction Gauss-Jordan inversion and direct/scaled solve equality; exact EOS map; Decimal80 scalar exponential comparison",
              "production_module_imports": 0, "actual_stage_attribution": "NOT_RUN_MISSING_RESIDUAL_AND_JACOBIAN_PACKET",
              "nonlinear_error_certificate": None, "python": platform.python_version(),
              "command": "python3 research/flrw_nonlinear_error_budget_20261016/probe/probe_nonlinear.py",
              "fixtures": cases,
              "resources": {"native_builds": 0, "native_solver_runs": 0, "physical_history_reads": 0,
                            "wall_seconds": time.perf_counter()-wall_start,
                            "cpu_seconds": time.process_time()-cpu_start,
                            "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    (HERE / "RESULT.json").write_text(json.dumps(encode(result), indent=2, sort_keys=True)+"\n")
    print("ALL EIGHT SYNTHETIC CHECKS COMPLETE; no actual production stage or nonlinear error certificate")
    print("RESOURCES " + json.dumps(result["resources"], sort_keys=True))


if __name__ == "__main__":
    main()
