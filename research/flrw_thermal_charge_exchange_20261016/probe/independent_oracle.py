"""Independent exact polynomial identities and Decimal manufactured CX oracle.

This file imports no implementation/runtime module and evaluates no Savin rates.
Run once under the frozen R5 fixture contract; retain its emitted result.
"""
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import time


# A polynomial is {powers of (F,b,K,q,p): rational coefficient}.
NVAR = 5
ZERO = (0,) * NVAR


def const(value):
    value = Fraction(value)
    return {ZERO: value} if value else {}


def var(i):
    power = [0] * NVAR
    power[i] = 1
    return {tuple(power): Fraction(1)}


def add(a, b):
    out = dict(a)
    for power, coefficient in b.items():
        out[power] = out.get(power, Fraction(0)) + coefficient
        if out[power] == 0:
            del out[power]
    return out


def neg(a):
    return {power: -coefficient for power, coefficient in a.items()}


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    out = {}
    for pa, ca in a.items():
        for pb, cb in b.items():
            power = tuple(x + y for x, y in zip(pa, pb))
            out[power] = out.get(power, Fraction(0)) + ca * cb
    return {power: coefficient for power, coefficient in out.items() if coefficient}


def diff(a, i):
    out = {}
    for power, coefficient in a.items():
        if power[i]:
            reduced = list(power)
            reduced[i] -= 1
            out[tuple(reduced)] = coefficient * power[i]
    return out


def substitute(a, i, value):
    out = {}
    for power, coefficient in a.items():
        reduced = list(power)
        exponent = reduced[i]
        reduced[i] = 0
        term = {tuple(reduced): coefficient}
        for _ in range(exponent):
            term = mul(term, value)
        out = add(out, term)
    return out


def serialize(a):
    return [{"powers_F_b_K_q_p": list(power), "coefficient": str(value)}
            for power, value in sorted(a.items())]


def exact_checks():
    one = const(1)
    F, b, K, q, p = (var(i) for i in range(NVAR))
    lam = sub(K, mul(b, F))
    checks = []

    def identity(name, lhs, rhs, interpretation):
        residual = sub(lhs, rhs)
        checks.append({"name": name, "PASS": not residual,
                       "residual_coefficients": serialize(residual),
                       "interpretation": interpretation})

    # q form. No rational simplification library or production code is used.
    n = mul(F, sub(one, q))
    d = sub(K, mul(mul(b, F), q))
    qprime = neg(mul(lam, q))
    numerator_derivative = sub(mul(mul(diff(n, 3), qprime), d),
                               mul(n, mul(diff(d, 3), qprime)))
    rhs_numerator = mul(sub(d, mul(b, n)), sub(mul(F, d), mul(K, n)))
    expected = mul(mul(F, mul(lam, lam)), q)
    identity("q_quotient_derivative", numerator_derivative, expected,
             "d[x]/dt numerator equals F*(K-bF)^2*q over D^2")
    identity("q_ODE_residual", numerator_derivative, rhs_numerator,
             "(1-b*x)*(F-K*x) equals d[x]/dt where denominator nonzero")
    identity("q_initial_numerator", substitute(n, 3, one), {},
             "q(0)=1 implies x(0)=0 when K-bF != 0")

    # phi form is regular at lambda=0 and makes the limiting solution explicit.
    n = mul(F, p)
    d = add(one, mul(mul(b, F), p))
    pprime = sub(one, mul(lam, p))
    numerator_derivative = sub(mul(mul(diff(n, 4), pprime), d),
                               mul(n, mul(diff(d, 4), pprime)))
    rhs_numerator = mul(sub(d, mul(b, n)), sub(mul(F, d), mul(K, n)))
    identity("phi_ODE_residual", numerator_derivative, rhs_numerator,
             "phi' = 1-lambda*phi, x=F*phi/(1+bF*phi)")
    identity("phi_initial_numerator", substitute(n, 4, {}), {},
             "phi(0)=0 gives x(0)=0 with denominator=1")
    identity("phi_initial_derivative", substitute(numerator_derivative, 4, {}), F,
             "x'(0)=F")
    identity("beta_zero_denominator", substitute(d, 1, {}), one,
             "b=0 gives x=F*phi with lambda=K")
    identity("F_zero_numerator", substitute(n, 0, {}), {},
             "F=0 gives identically x=0")
    identity("lambda_zero_derivative", substitute(numerator_derivative, 2, mul(b, F)), F,
             "K=bF gives x=F*t/(1+bF*t), derivative numerator F")
    identity("lambda_zero_rhs", substitute(rhs_numerator, 2, mul(b, F)), F,
             "same degenerate solution satisfies the ODE exactly")
    # x''(0) follows from differentiating the scalar field at x=0.
    curvature = neg(mul(F, add(K, mul(b, F))))
    phi_second = neg(lam)
    representation_second = sub(mul(F, phi_second), mul(const(2), mul(b, mul(F, F))))
    identity("small_time_second_derivative", representation_second, curvature,
             "x=F*t-F*(K+bF)*t^2/2+O(t^3)")
    return checks


def dec(value):
    rational = Fraction(str(value))
    return Decimal(rational.numerator) / Decimal(rational.denominator)


def phi(lam, t):
    return t if lam == 0 else (Decimal(1) - (-lam * t).exp()) / lam


def extent(F, beta, K, t):
    ph = phi(K - beta * F, t)
    return F * ph / (Decimal(1) + beta * F * ph)


def crossing_time(F, beta, K, target):
    # Invert x=F*phi/(1+beta*F*phi) and phi=(1-exp(-lambda*t))/lambda.
    ph = target / (F * (Decimal(1) - beta * target))
    lam = K - beta * F
    return ph if lam == 0 else -(Decimal(1) - lam * ph).ln() / lam


def fixture_oracles(frozen):
    raw = json.loads((frozen / "FIXTURES.json").read_text())
    records = []
    with localcontext() as context:
        context.prec = 80
        for case in raw["manufactured_cases"]:
            inputs = dict(raw["manufactured_common"])
            inputs.update(case)
            h0, hp, d0, dp = (dec(inputs[x]) for x in ("h0", "hp", "d0", "dp"))
            beta, k0, T0, requested, Tmin, Tmax = (
                dec(inputs[x]) for x in ("beta", "k0_cm3_s", "T0_K", "t_requested_s", "Tmin_K", "Tmax_K"))
            F = k0 * (d0 * hp - dp * h0)
            K = k0 * (h0 + hp + d0 + dp)
            equilibrium = F / K if K else None
            exact_requested = extent(F, beta, K, requested)
            crossings = []
            if beta and F:
                for kind, bound in (("lower", Tmin), ("upper", Tmax)):
                    target = (Decimal(1) - bound / T0) / beta
                    on_branch = ((F > 0 and 0 < target < equilibrium) or
                                 (F < 0 and equilibrium < target < 0))
                    if on_branch:
                        crossing = crossing_time(F, beta, K, target)
                        crossings.append({"kind": kind, "extent_cm3": str(target),
                                          "temperature_K": str(bound), "time_s": str(crossing)})
            relevant = [x for x in crossings if dec(x["time_s"]) < requested]
            event = min(relevant, key=lambda x: dec(x["time_s"])) if relevant else None
            reached = dec(event["time_s"]) if event else requested
            x = dec(event["extent_cm3"]) if event else exact_requested
            T = T0 * (1 - beta * x)
            records.append({
                "id": inputs["id"], "decimal_precision": 80,
                "F_cm3_s": str(F), "K_s-1": str(K), "beta_cm3": str(beta),
                "lambda_s-1": str(K - beta * F),
                "xi_equilibrium_cm3": str(equilibrium),
                "requested_time_s": str(requested),
                "xi_at_requested_time_unrestricted_cm3": str(exact_requested),
                "oracle_status": "EXACT_DOMAIN_CROSSING" if event else "COMPLETE",
                "analytic_crossings_on_monotone_branch": crossings,
                "first_event": event, "oracle_time_s": str(reached), "xi_cm3": str(x),
                "temperature_K": str(T), "temperature_ratio": str(1 - beta * x),
                "densities_cm3": dict(zip(("h0", "hp", "d0", "dp"),
                                         map(str, (h0 + x, hp - x, d0 - x, dp + x)))),
                "physical_interval_cm3": [str(-min(dp, h0)), str(min(d0, hp))],
                "domain_checks": {"density_nonnegative": all(v >= 0 for v in (h0+x, hp-x, d0-x, dp+x)),
                                  "temperature_inclusive": Tmin <= T <= Tmax},
                "precision_claim": "80-significant-digit Decimal evaluation of the exact analytic expression; no numerical integration and no certified rounding interval",
            })
    return records


def main():
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    frozen, output = map(Path, sys.argv[1:3])
    checks = exact_checks()
    records = fixture_oracles(frozen)
    result = {
        "schema": "rei.thermal-cx-independent-probe/1",
        "role": "Independent algebra and manufactured analytic-reference probe; no production/runtime imports",
        "command_argv": sys.argv,
        "runtime": {"python": sys.version, "executable": sys.executable,
                    "platform": platform.platform(),
                    "sympy_available": importlib.util.find_spec("sympy") is not None,
                    "mpmath_available": importlib.util.find_spec("mpmath") is not None},
        "input_sha256": {name: hashlib.sha256((frozen / name).read_bytes()).hexdigest()
                         for name in ("FIXTURES.json", "CONTRACT.json")},
        "exact_polynomial_coefficient_checks": checks,
        "manufactured_oracles": records,
        "wolfram": {"verified": False, "status": "ENVIRONMENTAL_FAILURE",
                    "actual_observation_owner": "root",
                    "context_calls_failed": 2, "evaluator_calls_failed": 1,
                    "error": "-32603 Internal error", "new_calls_this_probe": 0},
        "execution_scope": {"scientific_invocations": 1, "native_runs": 0,
                            "Savin_trajectories": 0, "old_suite_replays": 0,
                            "numeric_integration_runs": 0, "external_reference_runs": 0},
        "all_exact_checks_PASS": all(x["PASS"] for x in checks),
        "all_fixture_domain_checks_PASS": all(all(x["domain_checks"].values()) for x in records),
        "wall_seconds": time.perf_counter() - start_wall,
        "cpu_seconds": time.process_time() - start_cpu,
    }
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not result["all_exact_checks_PASS"] or not result["all_fixture_domain_checks_PASS"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
