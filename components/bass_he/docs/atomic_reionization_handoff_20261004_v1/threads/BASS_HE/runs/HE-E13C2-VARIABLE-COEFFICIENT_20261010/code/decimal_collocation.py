#!/usr/bin/env python3
"""Independent Decimal Gauss collocation for six E13C2 local photon segments.

Only Python standard library is imported. No original numerical routine is used.
CSV numbers and source float constants are lifted exactly from binary64. The
result is a finite high precision numerical reference, not an interval proof.
"""
import argparse
import csv
from decimal import Decimal, localcontext, getcontext
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

D = Decimal
ZERO, ONE, TWO = D(0), D(1), D(2)
SPECIES = ("HI", "HeI", "HeII")
PARAMS_FLOAT = (
    (.4298, 5.475e4, 32.88, 2.963, 0., 0., 0.),
    (13.61, 949.2, 1.469, 3.188, 2.039, .4434, 2.136),
    (1.720, 1.369e4, 32.88, 2.963, 0., 0., 0.),
)
THRESHOLD_FLOAT = (13.6, 24.59, 54.42)
EXPECTED_KEYS = (
    ("OFF", 1, 0, 0), ("OFF", 1, 1162, 0), ("OFF", 1, 1976, 0),
    ("GM", 2, 1727, 0), ("GM", 2, 2333, 0), ("OFF", 2, 700, 1),
)


def lift(value):
    """Exact binary64 value, including for original decimal CSV strings."""
    return D.from_float(float(value))


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, default=str) + "\n")


def key(row):
    return (row["mode"], int(row["step"]), int(row["node"]), int(row["segment"]))


def read_and_select(source):
    captures, stages, identities = {}, {}, []
    for mode in ("OFF", "GM"):
        p = source / "evidence" / "capture" / mode / "SEGMENTS.csv"
        with p.open(newline="") as f:
            captures[mode] = list(csv.DictReader(f))
        identities.append({"path": str(p), "bytes": p.stat().st_size, "sha256": hash_file(p)})
        p = source / "inputs" / (mode + "_STAGES.csv")
        with p.open(newline="") as f:
            stages[mode] = {int(r["step"]): r for r in csv.DictReader(f)}
        identities.append({"path": str(p), "bytes": p.stat().st_size, "sha256": hash_file(p)})
    p = source / "code" / "photon_green.py"
    identities.append({"path": str(p), "bytes": p.stat().st_size, "sha256": hash_file(p)})
    chosen = []
    for mode, step, target in (("OFF", 1, 13.7), ("OFF", 1, 35.), ("OFF", 1, 70.),
                               ("GM", 2, 55.), ("GM", 2, 99.)):
        pool = [r for r in captures[mode] if int(r["step"]) == step and float(r["source_on"]) == 1.]
        row = min(pool, key=lambda r: abs(float(r["e_mid"]) - target))
        chosen.append((row, stages[mode][step]))
    pool = [r for r in captures["OFF"] if int(r["step"]) == 1 and int(r["segment"]) == 1
            and float(r["source_on"]) == 1.]
    if not pool:
        pool = [r for r in captures["OFF"] if int(r["step"]) == 2 and int(r["segment"]) == 1
                and float(r["source_on"]) == 1.]
    row = pool[0]
    chosen.append((row, stages["OFF"][int(row["step"])]))
    assert tuple(key(r) for r, _ in chosen) == EXPECTED_KEYS, "fixed input selection changed"
    return chosen, identities


def legendre_value_and_derivative(n, x):
    p0, p1 = ONE, x
    for j in range(2, n + 1):
        p0, p1 = p1, (D(2 * j - 1) * x * p1 - D(j - 1) * p0) / D(j)
    return p1, D(n) * (x * p1 - p0) / (x * x - ONE)


def gauss_rule(n):
    """Newton roots from binary64 seeds, then fully Decimal refinement."""
    pairs = []
    for k in range(1, n + 1):
        x = lift(math.cos(math.pi * (k - .25) / (n + .5)))
        for iteration in range(100):
            p, dp = legendre_value_and_derivative(n, x)
            x1 = x - p / dp
            if abs(x1 - x) < D("1e-67"):
                x = x1
                break
            x = x1
        else:
            raise ArithmeticError("Gauss root Newton failed")
        p, dp = legendre_value_and_derivative(n, x)
        # Map [-1,1] to [0,1], including the Jacobian in the weight.
        pairs.append(((x + ONE) / TWO, ONE / ((ONE - x * x) * dp * dp)))
    pairs.sort()
    nodes, weights = [p[0] for p in pairs], [p[1] for p in pairs]
    moment_errors = [abs(sum((w * x ** power for x, w in pairs), ZERO) - ONE / D(power + 1))
                     for power in range(2 * n)]
    assert max(moment_errors) <= D("1e-50"), "Gauss polynomial moment acceptance failed"
    return nodes, weights, max(moment_errors)


def integrated_lagrange(nodes):
    """I_ij = integral_0^node_i L_j(t) dt, independent monomial construction."""
    n = len(nodes)
    columns = []
    for j, xj in enumerate(nodes):
        poly, den = [ONE], ONE
        for k, xk in enumerate(nodes):
            if j == k:
                continue
            following = [ZERO] * (len(poly) + 1)
            for power, c in enumerate(poly):
                following[power] -= xk * c
                following[power + 1] += c
            poly = following
            den *= xj - xk
        antiderivative = [ZERO] + [c / (den * D(power + 1)) for power, c in enumerate(poly)]
        col = []
        for xi in nodes:
            total = ZERO
            for c in reversed(antiderivative):
                total = total * xi + c
            col.append(total)
        columns.append(col)
    return [[columns[j][i] for j in range(n)] for i in range(n)]


def solve_decimal(matrix, rhs):
    """Dense Gaussian elimination with row partial pivoting."""
    n = len(rhs)
    a = [row[:] + [b] for row, b in zip(matrix, rhs)]
    for k in range(n):
        pivot = max(range(k, n), key=lambda i: abs(a[i][k]))
        a[k], a[pivot] = a[pivot], a[k]
        if a[k][k] == ZERO:
            raise ArithmeticError("singular collocation matrix")
        for i in range(k + 1, n):
            factor = a[i][k] / a[k][k]
            a[i][k] = ZERO
            for j in range(k + 1, n + 1):
                a[i][j] -= factor * a[k][j]
    result = [ZERO] * n
    for i in range(n - 1, -1, -1):
        result[i] = (a[i][n] - sum((a[i][j] * result[j] for j in range(i + 1, n)), ZERO)) / a[i][i]
    return result


class Coefficients:
    def __init__(self, row, stage):
        self.row, self.stage = row, stage
        self.a, self.h, self.e0, self.f0 = [lift(row[k]) for k in ("a", "h", "e0", "f0")]
        self.s0, self.s1 = [lift(stage[k]) for k in ("s0", "s1")]
        self.old = [lift(stage["old_" + k]) for k in ("x", "y", "z")]
        self.new = [lift(stage["new_" + k]) for k in ("x", "y", "z")]
        self.mask = [float(row["e_mid"]) >= t for t in THRESHOLD_FLOAT]
        self.source_on = float(row["source_on"]) == 1.
        self.hubble0, self.omega_r, self.omega_m, self.omega_l = map(lift, (2.2e-18, 9e-5, .3, .69991))
        ob, he, gravitational, proton = map(lift, (.048, .24, 6.67430e-8, 1.67262192595e-24))
        rho = D(3) * self.hubble0 * self.hubble0 / (D(8) * lift(math.pi) * gravitational)
        self.nh0 = (ONE - he) * ob * rho / proton
        self.nhe0 = he * ob * rho / (D(4) * proton)
        self.c, self.rate, self.emin, self.emax = map(lift, (2.99792458e10, 1e-15, 13.7, 100.))
        self.params = [list(map(lift, p)) for p in PARAMS_FLOAT]
        self.sigma_mb_log = lift(1e-18).ln()

    def sigma_open_segment(self, i, energy):
        if not self.mask[i]:
            return ZERO
        e0, sigma0, ya, p, yw, y0, y1 = self.params[i]
        x = energy / e0 - y0
        y = (x * x + y1 * y1).sqrt()
        log_sigma = (sigma0.ln() + ((x - ONE) ** 2 + yw * yw).ln()
                     + (p / TWO - D("5.5")) * y.ln()
                     - p * (ONE + (y / ya).sqrt()).ln() + self.sigma_mb_log)
        return log_sigma.exp()

    def __call__(self, t):
        delta_s = self.h * t
        s = self.a + delta_s
        e = self.e0 * (-delta_s).exp()
        theta = (self.a - self.s0 + delta_s) / (self.s1 - self.s0)
        x, y, z = [u + (v - u) * theta for u, v in zip(self.old, self.new)]
        if not (ZERO <= x <= ONE and y >= ZERO and z >= ZERO and y + z <= ONE):
            raise ArithmeticError("invalid interpolated gas")
        nh, nhe = self.nh0 * (-D(3) * s).exp(), self.nhe0 * (-D(3) * s).exp()
        hubble = self.hubble0 * (self.omega_r * (-D(4) * s).exp()
                                + self.omega_m * (-D(3) * s).exp() + self.omega_l).sqrt()
        targets = (nh * (ONE - x), nhe * (ONE - y - z), nhe * y)
        rates = [self.c * target * self.sigma_open_segment(i, e) / hubble
                 for i, target in enumerate(targets)]
        q = (self.rate / ((ONE / self.emin - ONE / self.emax) * e * hubble)
             if self.source_on else ZERO)
        return e, q, rates


def collocate(coeffs, nodes, weights, integrals):
    n, h, p0 = len(nodes), coeffs.h, coeffs.f0
    values = [coeffs(t) for t in nodes]
    energy = [v[0] for v in values]
    source = [v[1] for v in values]
    rates = [v[2] for v in values]
    total = [sum(v, ZERO) for v in rates]
    matrix = [[(ONE if i == j else ZERO) + h * integrals[i][j] * total[j]
               for j in range(n)] for i in range(n)]
    rhs = [p0 + h * sum((integrals[i][j] * source[j] for j in range(n)), ZERO) for i in range(n)]
    p = solve_decimal(matrix, rhs)
    derivative = [source[j] - total[j] * p[j] for j in range(n)]
    p1 = p0 + h * sum((w * d for w, d in zip(weights, derivative)), ZERO)
    a = [h * sum((weights[j] * rates[j][i] * p[j] for j in range(n)), ZERO) for i in range(3)]
    b = [h * sum((weights[j] * energy[j] * rates[j][i] * p[j] for j in range(n)), ZERO) for i in range(3)]
    red = h * sum((weights[j] * energy[j] * p[j] for j in range(n)), ZERO)
    qn = h * sum((w * q for w, q in zip(weights, source)), ZERO)
    qe = h * sum((w * e * q for w, e, q in zip(weights, energy, source)), ZERO)
    endpoint_energy = coeffs.e0 * (-h).exp()
    number_ledger = p1 - p0 + sum(a, ZERO) - qn
    energy_ledger = endpoint_energy * p1 - coeffs.e0 * p0 + sum(b, ZERO) + red - qe
    collocation_residual = max(abs(p[i] - p0 - h * sum((integrals[i][j] * derivative[j] for j in range(n)), ZERO))
                               for i in range(n))
    return {"P1": p1, "A": a, "B_eV": b, "Z_eV": red, "QN": qn, "QE_eV": qe,
            "number_ledger": number_ledger, "energy_ledger_eV": energy_ledger,
            "collocation_equation_max_residual": collocation_residual,
            "min_stage_P": min(p), "max_stage_P": max(p),
            "captured_initial_P0": p0, "endpoint_E1_eV": endpoint_energy}


def j_integral(rate, h):
    """J(rate)=integral_0^h exp(-rate*u) du, via convergent Taylor series."""
    z = -rate * h
    term, total = ONE, ONE
    for k in range(1, 1000):
        term *= z / D(k + 1)
        total += term
        if abs(term) < D("1e-69"):
            return h * total
    raise ArithmeticError("J series did not converge")


def frozen_exact(coeffs):
    row, h, e, p0 = coeffs.row, coeffs.h, coeffs.e0, coeffs.f0
    q = lift(row["q"])
    lam = [lift(row["lambda_" + k]) for k in SPECIES]
    total = sum(lam, ZERO)
    if total <= ZERO:
        raise ValueError("selected captured frozen controls require positive total rate")
    jl, jle, j1 = j_integral(total, h), j_integral(total + ONE, h), j_integral(ONE, h)
    p1 = p0 * (-total * h).exp() + q * jl
    integral_p = p0 * jl + q * (h - jl) / total
    integral_ep = e * (p0 * jle + q * (j1 - jle) / total)
    a = [l * integral_p for l in lam]
    b = [l * integral_ep for l in lam]
    qn, qe = q * h, e * q * j1
    result = {"P1": p1, "A": a, "B_eV": b, "Z_eV": integral_ep, "QN": qn, "QE_eV": qe,
              "number_ledger": p1 - p0 + sum(a, ZERO) - qn,
              "energy_ledger_eV": e * (-h).exp() * p1 - e * p0 + sum(b, ZERO) + integral_ep - qe,
              "lambda_h": total * h}
    return result


def differences(first, second):
    return {"P1": first["P1"] - second["P1"],
            "A": [a - b for a, b in zip(first["A"], second["A"])],
            "B_eV": [a - b for a, b in zip(first["B_eV"], second["B_eV"])],
            "Z_eV": first["Z_eV"] - second["Z_eV"],
            "QN": first["QN"] - second["QN"], "QE_eV": first["QE_eV"] - second["QE_eV"]}


def captured_output(row):
    eps = lift(1.602176634e-12)
    return {"P1": lift(row["n"]), "A": [lift(row["A_" + k]) for k in SPECIES],
            "B_eV": [lift(row["B_" + k]) / eps for k in SPECIES],
            "Z_eV": lift(row["red"]) / eps, "QN": lift(row["qn"]), "QE_eV": lift(row["qe"]) / eps}


def finite_recursive(obj):
    if isinstance(obj, D):
        return obj.is_finite()
    if isinstance(obj, dict):
        return all(finite_recursive(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return all(finite_recursive(v) for v in obj)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("/workspace/scratch/7fd51143e473/intake_drive/physics/BASS_HE_E13C_PHOTON_PHYSICS_20261010_v1"))
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "ORACLE_RESULTS.json")
    args = parser.parse_args()
    started = time.perf_counter()
    getcontext().prec = 70
    selected, source_identity = read_and_select(args.source)
    degrees = (12, 20)
    rules, rule_checks = {}, {}
    for degree in degrees:
        nodes, weights, moment_error = gauss_rule(degree)
        integrals = integrated_lagrange(nodes)
        rowsum = max(abs(sum(row, ZERO) - x) for row, x in zip(integrals, nodes))
        assert rowsum < D("1e-50"), "integrated Lagrange row-sum acceptance failed"
        rules[degree] = (nodes, weights, integrals)
        rule_checks[degree] = {"max_polynomial_moment_error": moment_error,
                               "max_integrated_Lagrange_rowsum_error": rowsum}
    results, failures = [], []
    for row, stage in selected:
        coeffs = Coefficients(row, stage)
        calculated = {degree: collocate(coeffs, *rules[degree]) for degree in degrees}
        low, high = calculated[degrees[0]], calculated[degrees[1]]
        frozen = frozen_exact(coeffs)
        degree_diff = differences(high, low)
        max_number = max(abs(degree_diff["P1"]), abs(degree_diff["QN"]), *(abs(v) for v in degree_diff["A"]))
        max_energy = max(abs(degree_diff["Z_eV"]), abs(degree_diff["QE_eV"]), *(abs(v) for v in degree_diff["B_eV"]))
        checks = {"finite": finite_recursive(calculated) and finite_recursive(frozen),
                  "degree_convergence_P1_A_QN": max_number <= D("1e-25"),
                  "degree_convergence_energy_eV": max_energy <= D("1e-23"),
                  "number_ledgers": max(abs(v["number_ledger"]) for v in [low, high, frozen]) <= D("1e-45"),
                  "continuous_energy_ledgers": max(abs(v["energy_ledger_eV"]) for v in [low, high]) <= D("1e-25"),
                  "frozen_energy_ledger": abs(frozen["energy_ledger_eV"]) <= D("1e-45"),
                  "collocation_equation_residual": max(v["collocation_equation_max_residual"] for v in [low, high]) <= D("1e-45"),
                  "photon_positivity": all(v["P1"] >= ZERO and v["min_stage_P"] >= ZERO for v in [low, high])}
        mid_e, mid_q, mid_lam = coeffs(ONE / TWO)
        result = {"key": key(row), "input_row_exact_csv_strings": row,
                  "stage_input_exact_csv_strings": stage, "fixed_absorber_support": dict(zip(SPECIES, coeffs.mask)),
                  "continuum_at_mathematical_midpoint": {"E_eV": mid_e, "q": mid_q, "lambda": mid_lam},
                  "calculated_by_degree": calculated, "frozen_exact_captured_coefficients": frozen,
                  "signed_continuous_minus_frozen": differences(high, frozen),
                  "captured_ieee_minus_exact_frozen": differences(captured_output(row), frozen),
                  "degree20_minus_degree12": degree_diff,
                  "max_abs_degree_difference_number": max_number,
                  "max_abs_degree_difference_energy_eV": max_energy,
                  "checks": checks, "status": "PASS_SCOPED" if all(checks.values()) else "FAIL"}
        results.append(result)
        for check, passed in checks.items():
            if not passed:
                failures.append({"key": key(row), "check": check, "failure_class": "NUMERICAL_OR_IMPLEMENTATION_UNRESOLVED"})
        print(json.dumps({"key": key(row), "status": result["status"],
                          "max_abs_degree_difference_number": str(max_number),
                          "max_abs_degree_difference_energy_eV": str(max_energy),
                          "signed_delta_P1": str(result["signed_continuous_minus_frozen"]["P1"])}), flush=True)
    packet = {"schema_version": "1.0", "scope": "six actual local captured E13C segments; fixed physical gas path",
              "evidence_status": ["numerically checked", "implementation-verified"],
              "claim_ceiling": "Finite high-precision numerical oracle; no outward interval certificate, atomic-fit uncertainty, globally carried photon history, or gas/coupled advancement.",
              "precision_decimal_digits": 70, "degrees": degrees, "source_lift": "CSV string -> Python binary64 -> Decimal.from_float exactly",
              "energy_unit": "eV (B and Z carry photon-number times eV); captured erg outputs divided by exactly lifted eps_eV",
              "environment": {"python": sys.version, "platform": platform.platform(), "modules": "stdlib only"},
              "source_identity": source_identity, "oracle_code_sha256": hash_file(Path(__file__)),
              "quadrature_rule_checks": rule_checks, "results": results, "failures": failures,
              "elapsed_seconds": time.perf_counter() - started,
              "verdict": "PASS_SCOPED" if not failures else "FAIL"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    dump(args.output, packet)
    if failures:
        first_failure_path = args.output.parent / "FIRST_FAILURE.json"
        if not first_failure_path.exists():
            dump(first_failure_path, packet)
    print(json.dumps({"verdict": packet["verdict"], "output": str(args.output),
                      "elapsed_seconds": packet["elapsed_seconds"]}), flush=True)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
