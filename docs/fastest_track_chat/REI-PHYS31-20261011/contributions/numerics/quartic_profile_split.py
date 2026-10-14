#!/usr/bin/env python3
"""PHYS31: four retained nodes, two new k'''' expressions, exact quartic toys.

No historical scientific module is imported or executed. The owner must inspect
the frozen code/protocol and give GO before invoking this main. Importing this
module does not evaluate constants, kernels, moments, or toys. Decimal outputs
are finite arithmetic diagnostics, not interval certificates.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, getcontext, localcontext, ROUND_HALF_EVEN
from fractions import Fraction
from hashlib import sha256
import json
from math import comb, factorial
from pathlib import Path
import platform
import sys
import traceback


CONTRACT_SHA256 = "f0bc083e4ecc0c0899b68a7595e5fddac778cccb9eababa191a8fdc0504be8d4"
NODE_ORDER = ("a", "v_star", "u_zero", "b")
BRANCH_ORDER = ("upper_root", "lower_root")
PROFILE_ORDER = ("uniform", "p4")
KERNEL_ORDER = ("cubic", "quartic")
IDENTITY_PATHS = (
    ("contract", "PHYSICS_CONTRACT.json"),
    ("cache30", "inputs/PHYS30/contributions/numerics/PROFILE_SECOND_ORDER_FIRST.json"),
    ("cache29", "inputs/PHYS29/contributions/numerics/SECOND_ORDER_FIRST.json"),
    ("J", "inputs/PHYS29/inputs/PHYS22_INITIAL_COEFFICIENTS.json"),
    ("atomic", "inputs/pinned_source/rust/rei_microphysics/src/atomic_provider.rs"),
    ("coupled", "inputs/pinned_source/rust/rei_microphysics/src/coupled_primary.rs"),
    ("source_manifest", "SOURCE_MANIFEST.json"),
    ("code", "contributions/numerics/quartic_profile_split.py"),
    ("protocol", "contributions/numerics/PROTOCOL.json"),
)


def json_value(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Fraction):
        return str(value.numerator) if value.denominator == 1 else str(value)
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_value(item) for item in value]
    return value


def file_identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": sha256(data).hexdigest()}


def source_f64(text):
    """Interpret the source's binary64 literal as an exact real constant."""
    return Decimal.from_float(float(text))


def source_constants():
    n0 = source_f64("0.05")
    shear = (source_f64("1.01e-14") - source_f64("0.99e-14")) / 2
    q = 2 * shear**2
    kappa = source_f64("29979245800") * source_f64("1e-4") * (1 - source_f64("0.9"))
    return {
        "N0_per_H": n0,
        "q_s-2": q,
        "kappa_s-1_cm-2": kappa,
        "factor_q_N0_kappa_over_180": q * n0 * kappa / 180,
        "chi_eV": source_f64("13.598434599702"),
        "E0_eV": source_f64("0.4298"),
        "ya": source_f64("32.88"),
        "P": source_f64("2.963"),
        "sigma0": source_f64("5.475e4"),
        "area_cm2": source_f64("1e-18"),
    }


class LogTaylor6:
    """Coefficients [t^n] f(E exp(t)); log/exp differential recurrences.

    This implementation does not call ordinary_energy_power or its convolution.
    Only Decimal's scalar ln/exp primitives are shared by the two paths.
    """
    order = 6

    def __init__(self, value):
        if isinstance(value, (list, tuple)):
            if len(value) > 7:
                raise ValueError("LogTaylor6 coefficient overflow")
            self.c = list(value) + [Decimal(0)] * (7 - len(value))
        else:
            self.c = [Decimal(value)] + [Decimal(0)] * 6

    @staticmethod
    def lift(value):
        return value if isinstance(value, LogTaylor6) else LogTaylor6(value)

    def __add__(self, other):
        other = self.lift(other)
        return LogTaylor6([self.c[n] + other.c[n] for n in range(7)])

    __radd__ = __add__

    def __neg__(self):
        return LogTaylor6([-value for value in self.c])

    def __sub__(self, other):
        return self + -self.lift(other)

    def __rsub__(self, other):
        return self.lift(other) + -self

    def __mul__(self, other):
        other = self.lift(other)
        return LogTaylor6([
            sum((self.c[j] * other.c[n-j] for j in range(n+1)), Decimal(0))
            for n in range(7)
        ])

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        if isinstance(scalar, LogTaylor6):
            raise TypeError("LogTaylor6 division is scalar only")
        return LogTaylor6([value / scalar for value in self.c])

    def __pow__(self, exponent):
        exponent = Decimal(exponent)
        if self.c[0] <= 0:
            raise ValueError("Nonpositive logarithmic Taylor base")
        logarithm = [self.c[0].ln()] + [Decimal(0)] * 6
        for n in range(1, 7):
            lower = sum((j * logarithm[j] * self.c[n-j] for j in range(1, n)), Decimal(0))
            logarithm[n] = (n * self.c[n] - lower) / (n * self.c[0])
        scaled_log = [exponent * value for value in logarithm]
        result = [scaled_log[0].exp()] + [Decimal(0)] * 6
        for n in range(1, 7):
            result[n] = sum((j * scaled_log[j] * result[n-j] for j in range(1, n+1)), Decimal(0)) / n
        return LogTaylor6(result)


def log_fourth_from_phi(coefficients, energy, prefactor):
    """Apply E^-4 (D6-3D5-7D4+27D3-18D2), no lower k outputs."""
    numerator = (
        factorial(6) * coefficients[6]
        - 3 * factorial(5) * coefficients[5]
        - 7 * factorial(4) * coefficients[4]
        + 27 * factorial(3) * coefficients[3]
        - 18 * factorial(2) * coefficients[2]
    )
    return prefactor * numerator / energy**4


def ordinary_energy_multiply(left, right):
    """Independent ordinary additive-energy polynomial multiplication."""
    result = [Decimal(0) for _ in range(7)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            if i + j <= 6:
                result[i+j] += a * b
    return result


def ordinary_energy_power(coefficients, exponent):
    """Generalized binomial finite sum at positive base, additive energy u."""
    base = coefficients[0]
    if base <= 0:
        raise ValueError("Nonpositive ordinary Taylor base")
    remainder = [Decimal(0)] + [value / base for value in coefficients[1:]]
    term = [Decimal(1)] + [Decimal(0)] * 6
    result = list(term)
    binomial = Decimal(1)
    for degree in range(1, 7):
        binomial = binomial * (exponent - degree + 1) / degree
        term = ordinary_energy_multiply(term, remainder)
        for n in range(7):
            result[n] += binomial * term[n]
    scale = (exponent * base.ln()).exp()
    return [scale * value for value in result]


def energy_fourth_from_phi(coefficients, energy, prefactor):
    """K[720 E^2 a6+1440 E a5+672 a4], a_n=[u^n] phi(E+u)."""
    return prefactor * (720 * energy**2 * coefficients[6] + 1440 * energy * coefficients[5] + 672 * coefficients[4])


class ExactSeries4:
    """Ordinary delta series with exact Fraction coefficients through degree 4."""
    def __init__(self, value):
        if isinstance(value, (list, tuple)):
            if len(value) > 5:
                raise ValueError("ExactSeries4 coefficient overflow")
            self.c = [Fraction(item) for item in value] + [Fraction(0)] * (5 - len(value))
        else:
            self.c = [Fraction(value)] + [Fraction(0)] * 4

    @staticmethod
    def lift(value):
        return value if isinstance(value, ExactSeries4) else ExactSeries4(value)

    def __add__(self, other):
        other = self.lift(other)
        return ExactSeries4([a + b for a, b in zip(self.c, other.c)])

    __radd__ = __add__

    def __neg__(self):
        return ExactSeries4([-item for item in self.c])

    def __sub__(self, other):
        return self + -self.lift(other)

    def __rsub__(self, other):
        return self.lift(other) + -self

    def __mul__(self, other):
        other = self.lift(other)
        return ExactSeries4([
            sum((self.c[j] * other.c[n-j] for j in range(n+1)), Fraction(0))
            for n in range(5)
        ])

    __rmul__ = __mul__

    def reciprocal(self):
        if self.c[0] == 0:
            raise ZeroDivisionError("Zero exact series base")
        result = [1 / self.c[0]] + [Fraction(0)] * 4
        for n in range(1, 5):
            result[n] = -sum((self.c[j] * result[n-j] for j in range(1, n+1)), Fraction(0)) / self.c[0]
        return ExactSeries4(result)

    def __truediv__(self, other):
        return self * self.lift(other).reciprocal()

    def __rtruediv__(self, other):
        return self.lift(other) * self.reciprocal()

    def __pow__(self, exponent):
        if not isinstance(exponent, int) or exponent < 0:
            raise ValueError("ExactSeries4 power must be nonnegative integer")
        result = ExactSeries4(1)
        for _ in range(exponent):
            result = result * self
        return result


def rational_polynomial(coefficients, x):
    return sum((coefficient * x**n for n, coefficient in enumerate(coefficients)), Fraction(0))


def rational_polynomial_derivative(coefficients, x):
    return sum((n * coefficients[n] * x**(n-1) for n in range(1, len(coefficients))), Fraction(0))


class Experiment:
    def __init__(self, root):
        self.root = root
        self.here = root / "contributions/numerics"
        self.checks = []
        self.scaled_errors = []
        self.counts = {
            "program_main_invocations_this_process": 1,
            "unique_retained_physical_nodes": 0,
            "log_energy_k4_calls": 0,
            "ordinary_energy_k4_calls": 0,
            "new_physical_k4_component_outputs": 0,
            "new_physical_lower_order_k_component_outputs": 0,
            "log_phi_degree6_builds": 0,
            "ordinary_phi_degree6_builds": 0,
            "physical_branch_coefficient_updates": 0,
            "physical_unnormalized_quotients_from_cached_lower_values": 0,
            "exact_profile_moment_integrals": 0,
            "exact_profile_positivity_polynomial_checks": 0,
            "exact_polynomial_operator_cases": 0,
            "exact_polynomial_operator_expressions": 0,
            "exact_toy_kernel_sign_bound_cases": 0,
            "exact_toy_branches": 0,
            "exact_toy_profile_root_series": 0,
            "exact_toy_formal_root_steps": 0,
            "exact_toy_response_series_builds": 0,
            "new_physical_energy_nodes": 0,
            "new_physical_root_searches_or_corrections": 0,
            "old_scientific_module_imports": 0,
            "old_scientific_main_or_suite_runs": 0,
            "quadrature": 0,
            "finite_differences": 0,
            "physical_width_or_root_sweeps": 0,
            "whole_interval_derivative_sign_campaigns": 0,
            "native_gas_IVP_dense_LP_runs": 0,
            "independent_physical_data_credit": 0,
        }
        self.called_nodes = {"log": set(), "energy": set()}
        self.result = {
            "task": "REI-PHYS31-20261011",
            "status": "STARTED",
            "role": "NONBLIND numerical candidate generation; not final independent review",
            "python_version": platform.python_version(),
            "evidence_class": ["numerically checked", "implementation-verified at fixed inputs"],
            "coefficient_definition": "W_p4-W_uniform=D4*delta^4+o(delta^4), D4 in eV^-2, no factorial in D4",
            "physical_admission": "HOLD",
            "claim_ceiling": [
                "Four retained node strings and original fixed J only; no root or J uncertainty enclosure",
                "Two representations share physical inputs and Decimal transcendental primitives",
                "Same-host separate-path replay carries no independent physical-data credit",
                "No finite-width physical response, root ordering certificate, or valid-width estimate",
                "Physical k4 values and resulting D4 describe retained points and same nonzero A levels",
            ],
            "protected": {"physical": "HOLD", "original_interval": "[160,161] FAIL", "tick": 160, "auxiliary_escape": "FAIL", "HH": "OFF", "RCT": "OFF", "CR": "OFF", "precision_atomic": "PARKED", "production_source_default_runtime_changes": 0},
        }

    def check(self, check_id, passed, **evidence):
        self.checks.append({"id": check_id, "pass": bool(passed), **evidence})

    def close(self, check_id, actual, expected, scale, **evidence):
        if not actual.is_finite() or not expected.is_finite() or scale <= 0:
            raise ArithmeticError("Invalid finite scaled comparison")
        residual = actual - expected
        error = abs(residual) / scale
        self.scaled_errors.append(error)
        self.check(check_id, error <= Decimal("1e-60"), actual=actual, expected=expected, residual=residual, scale=scale, scaled_error=error, tolerance="1e-60", **evidence)

    def verify_inputs(self):
        self.protocol = json.loads((self.here / "PROTOCOL.json").read_text())
        freeze = json.loads((self.here / "PREEXECUTION_FREEZE.json").read_text())
        actual = {}
        for label, relative in IDENTITY_PATHS:
            observed = file_identity(self.root / relative)
            expected = freeze["files"][relative]
            passed = observed == expected
            if label == "contract":
                passed = passed and observed["sha256"] == CONTRACT_SHA256
            self.check("IDENTITY." + label, passed, path=relative, actual=observed, expected=expected, interpretation="Byte identity only")
            actual[relative] = observed
        prescribed = dict(self.protocol["input_identities"])
        self.check("IDENTITY.freeze_mapping", set(freeze["files"]) == {path for _, path in IDENTITY_PATHS} and all(freeze["files"][path] == identity for path, identity in prescribed.items()), interpretation="Externally frozen input/code/protocol linkage; no scientific correctness inference")
        if not all(row["pass"] for row in self.checks):
            raise RuntimeError("Frozen input identity failure before scientific evaluation")
        self.result["input_identities"] = actual
        self.result["preexecution_freeze_identity"] = file_identity(self.here / "PREEXECUTION_FREEZE.json")
        self.cache30 = json.loads((self.root / IDENTITY_PATHS[1][1]).read_text())
        self.cache29 = json.loads((self.root / IDENTITY_PATHS[2][1]).read_text())
        j_source = json.loads((self.root / IDENTITY_PATHS[3][1]).read_text())
        self.data = self.cache30["retained_physical_data"]
        self.node_strings = self.data["energy_nodes_eV"]
        self.nodes = {name: Decimal(self.node_strings[name]) for name in NODE_ORDER}
        self.geometry = self.data["PHYS29_uniform_partials_weights_and_coefficients"]
        self.constants = source_constants()
        self.jx = Decimal(j_source["results"]["baseline_local"]["J_nonphoto"][2][0])
        self.jw = Decimal(j_source["results"]["baseline_local"]["J_nonphoto"][2][3])
        self.check("CACHE.nodes", tuple(self.node_strings) == NODE_ORDER and self.node_strings == self.cache29["energy_nodes_eV"], retained_energy_strings=self.node_strings)
        geometry_flags = {}
        for branch in BRANCH_ORDER:
            current = self.geometry[branch]
            old = self.cache29["second_order"]["jet_chain"][branch]
            geometry_flags[branch] = all(current[key] == old[key] for key in ("response_s-4", "C_s-4_eV-2", "law"))
        geometry_flags["cached_lower_components"] = all(self.data["components"][name][key] == self.cache29["joint_kernel_outputs"]["jet"][name][key] for name in NODE_ORDER for key in ("k_s-4", "k_prime_s-4_eV-1", "k_second_s-4_eV-2"))
        self.check("CACHE.geometry_and_components", all(geometry_flags.values()), flags=geometry_flags)
        constants_flags = {key: value == Decimal(self.cache29["constants"][key]) for key, value in self.constants.items()}
        self.check("CACHE.source_real_constants", all(constants_flags.values()), flags=constants_flags, computed_constants=self.constants, meaning="Exact-real source binary64 literals followed by Decimal80; not native f64 emulation")
        self.check("CACHE.original_J", self.jx == Decimal(self.cache29["constants"]["J_h2_x"]) and self.jw == Decimal(self.cache29["constants"]["J_h2_w"]), J_x=self.jx, J_w=self.jw, uncertainty="Inherited; no new J calculation or enclosure")
        self.check("ARITHMETIC.context", getcontext().prec == 80 and getcontext().rounding == ROUND_HALF_EVEN, observed_precision=getcontext().prec, observed_rounding=getcontext().rounding)
        if not all(row["pass"] for row in self.checks):
            raise RuntimeError("Cached input semantics failed before physical calls")

    def exact_profiles(self):
        densities = {"uniform": [Fraction(1, 2)], "p4": [Fraction(11, 16), Fraction(0), Fraction(-30, 16), Fraction(0), Fraction(35, 16)]}
        square = [Fraction(35, 16) * Fraction(9, 49) + Fraction(2, 7), Fraction(0), -Fraction(35, 16) * Fraction(6, 7), Fraction(0), Fraction(35, 16)]
        self.counts["exact_profile_positivity_polynomial_checks"] += 1
        self.check("PROFILE.positivity_square", square == densities["p4"] and Fraction(35, 16) > 0 and Fraction(2, 7) > 0, polynomial_coefficients=densities["p4"], square_coefficients=square, lower_bound=Fraction(2, 7), support="[-1,1]; positive on the entire interval; zero extension has endpoint jumps")
        expected = {"uniform": [Fraction(1), Fraction(0), Fraction(1, 3), Fraction(0), Fraction(1, 5)], "p4": [Fraction(1), Fraction(0), Fraction(1, 3), Fraction(0), Fraction(71, 315)]}
        self.moments = {}
        for profile in PROFILE_ORDER:
            values = []
            for n in range(5):
                self.counts["exact_profile_moment_integrals"] += 1
                value = sum((coefficient * (Fraction(2, n+j+1) if (n+j) % 2 == 0 else Fraction(0)) for j, coefficient in enumerate(densities[profile])), Fraction(0))
                values.append(value)
                self.check(f"PROFILE.{profile}.moment{n}", value == expected[profile][n], actual=value, expected=expected[profile][n], arithmetic="Exact rational antiderivative, not quadrature")
            self.moments[profile] = values
        self.delta_mu4 = self.moments["p4"][4] - self.moments["uniform"][4]
        self.check("PROFILE.equal_mu2", self.moments["p4"][2] == self.moments["uniform"][2], actual=self.moments["p4"][2])
        self.check("PROFILE.delta_mu4", self.delta_mu4 == Fraction(8, 315), actual=self.delta_mu4, expected=Fraction(8, 315))
        self.result["exact_profile_moments"] = self.moments

    def exact_operator_checks(self):
        rows = []
        energy = Fraction(3)
        for degree in range(7):
            self.counts["exact_polynomial_operator_cases"] += 1
            self.counts["exact_polynomial_operator_expressions"] += 2
            log_coeff = [energy**degree * Fraction(degree**n, factorial(n)) for n in range(7)]
            additive_coeff = [Fraction(comb(degree, n)) * energy**(degree-n) if n <= degree else Fraction(0) for n in range(7)]
            log_value = log_fourth_from_phi(log_coeff, energy, Fraction(1))
            energy_value = energy_fourth_from_phi(additive_coeff, energy, Fraction(1))
            falling = Fraction(1)
            for j in range(4):
                falling *= degree - j
            expected = degree * (degree + 3) * falling * energy**(degree-4)
            row = {"phi_degree": degree, "energy": energy, "log_expression": log_value, "ordinary_expression": energy_value, "direct_d4_of_n_nplus3_En": expected}
            self.check(f"OPERATOR.phi_degree{degree}", log_value == expected and energy_value == expected, **row)
            rows.append(row)
        self.result["exact_operator_checks"] = rows

    def count_physical(self, path, name):
        if name not in NODE_ORDER or name in self.called_nodes[path]:
            raise RuntimeError("Repeated or unregistered physical node")
        energy = self.nodes[name]
        if not Decimal("13.61") <= energy <= Decimal("24.58") or not source_f64("13.60") < energy < source_f64("24.59"):
            raise ValueError("Retained energy left analytic HI support")
        counter = "log_energy_k4_calls" if path == "log" else "ordinary_energy_k4_calls"
        if self.counts[counter] >= 4 or self.counts["log_energy_k4_calls"] + self.counts["ordinary_energy_k4_calls"] >= 8:
            raise RuntimeError("Frozen four calls per path / eight calls per main exceeded")
        self.counts[counter] += 1
        self.called_nodes[path].add(name)
        self.counts["unique_retained_physical_nodes"] = len(self.called_nodes["log"] | self.called_nodes["energy"])

    def k4_log(self, name):
        self.count_physical("log", name)
        self.counts["log_phi_degree6_builds"] += 1
        e = self.nodes[name]
        c = self.constants
        ej = LogTaylor6([e / factorial(n) for n in range(7)])
        x = ej / c["E0_eV"]
        xm = x - 1
        sigma = c["sigma0"] * c["area_cm2"] * (xm * xm) * x**(c["P"] / 2 - source_f64("5.5")) * (1 + (x / c["ya"])**Decimal("0.5"))**(-c["P"])
        phi = sigma * (self.jx + self.jw * (ej - c["chi_eV"]))
        value = log_fourth_from_phi(phi.c, e, c["factor_q_N0_kappa_over_180"])
        if not value.is_finite():
            raise ArithmeticError("Nonfinite log-energy k4")
        self.counts["new_physical_k4_component_outputs"] += 1
        return value

    def k4_energy(self, name):
        self.count_physical("energy", name)
        self.counts["ordinary_phi_degree6_builds"] += 1
        e = self.nodes[name]
        c = self.constants
        x = [e / c["E0_eV"], 1 / c["E0_eV"]] + [Decimal(0)] * 5
        xm = list(x)
        xm[0] -= 1
        squared = ordinary_energy_multiply(xm, xm)
        xp = ordinary_energy_power(x, c["P"] / 2 - source_f64("5.5"))
        sqrt_series = ordinary_energy_power([value / c["ya"] for value in x], Decimal("0.5"))
        sqrt_series[0] += 1
        last = ordinary_energy_power(sqrt_series, -c["P"])
        sigma = ordinary_energy_multiply(ordinary_energy_multiply(squared, xp), last)
        sigma = [c["sigma0"] * c["area_cm2"] * value for value in sigma]
        affine = [self.jx + self.jw * (e - c["chi_eV"]), self.jw] + [Decimal(0)] * 5
        phi = ordinary_energy_multiply(sigma, affine)
        value = energy_fourth_from_phi(phi, e, c["factor_q_N0_kappa_over_180"])
        if not value.is_finite():
            raise ArithmeticError("Nonfinite ordinary-energy k4")
        self.counts["new_physical_k4_component_outputs"] += 1
        return value

    def physical_outputs(self):
        paths = {"log": {}, "energy": {}}
        for name in NODE_ORDER:
            paths["log"][name] = self.k4_log(name)
        for name in NODE_ORDER:
            paths["energy"][name] = self.k4_energy(name)
        s0 = Decimal("1e-64")
        s4 = s0 / Decimal(18)**4
        d4_scale = Decimal(1) / Decimal(18)**2
        for name in NODE_ORDER:
            self.close("PHYSICAL.k4." + name, paths["log"][name], paths["energy"][name], s4, units="s^-4 eV^-4")
        delta_mu4 = Decimal(self.delta_mu4.numerator) / Decimal(self.delta_mu4.denominator)
        branches = {}
        for branch in BRANCH_ORDER:
            self.counts["physical_branch_coefficient_updates"] += 1
            self.counts["physical_unnormalized_quotients_from_cached_lower_values"] += 2
            old = self.geometry[branch]
            law = old["law"]
            sign = law["s"]
            endpoint, interior = ("a", "v_star") if branch == "upper_root" else ("b", "u_zero")
            r = Decimal(law["R_eV"])
            w = Decimal(law["stored_W_eV2"])
            q = r*r + w
            p, pc = Decimal(law["p_endpoint"]), Decimal(law["p_center"])
            level, slope = Decimal(old["response_s-4"]), Decimal(old["C_s-4_eV-2"])
            k_endpoint = Decimal(self.data["components"][endpoint]["k_s-4"])
            kp_interior = Decimal(self.data["components"][interior]["k_prime_s-4_eV-1"])
            nw = k_endpoint + sign*r*kp_interior
            gw = nw - level
            self.close("PHYSICAL." + branch + ".G_W", gw, q*slope, s0, units="s^-4", N_W_from_cached_k_and_kprime=nw, retained_A=level, denominator="N_W-A, constructed without using C")
            row = {"endpoint": endpoint, "interior": interior, "retained_W_eV2": law["stored_W_eV2"], "retained_A_s-4": old["response_s-4"], "retained_C_s-4_eV-2": old["C_s-4_eV-2"], "Q_eV2": q, "N_W_from_cached_values_s-4": nw, "G_W_s-4": gw, "Delta_mu4": delta_mu4, "paths": {}}
            for path in ("log", "energy"):
                h4 = p*paths[path][endpoint] + pc*paths[path][interior]
                response_coefficient = delta_mu4*h4/24
                d4 = -response_coefficient/slope
                unnormalized_numerator = w*paths[path][endpoint] + r*r*paths[path][interior]
                d4_numerator = -delta_mu4*unnormalized_numerator/(24*gw)
                self.close("PHYSICAL." + branch + "." + path + ".root_quotient", d4, d4_numerator, d4_scale, units="eV^-2", numerator_wk4_plus_R2k4=unnormalized_numerator, retained_A=level)
                row["paths"][path] = {"H4_s-4_eV-4": h4, "response_delta4_s-4_eV-4": response_coefficient, "D4_eV-2": d4, "unnormalized_D4_eV-2": d4_numerator, "H4_nonzero_finite_arithmetic": h4 != 0, "H4_sign_finite_arithmetic": "+" if h4 > 0 else ("-" if h4 < 0 else "0"), "D4_sign_finite_arithmetic": "+" if d4 > 0 else ("-" if d4 < 0 else "0")}
            self.close("PHYSICAL." + branch + ".D4_paths", row["paths"]["log"]["D4_eV-2"], row["paths"]["energy"]["D4_eV-2"], d4_scale, units="eV^-2")
            branches[branch] = row
        self.result["new_fourth_derivative_outputs"] = {path: {name: {"retained_energy_eV": self.node_strings[name], "k4_s-4_eV-4": value} for name, value in values.items()} for path, values in paths.items()}
        self.result["physical_quartic_profile_difference"] = branches
        self.result["descriptive_gap_quartic_difference"] = {
            "definition": "Coefficient of delta^4 in (W_lower,p4-W_upper,p4)-(W_lower,uniform-W_upper,uniform)",
            "units": "eV^-2",
            "new_physical_evaluations": 0,
            "paths": {path: branches["lower_root"]["paths"][path]["D4_eV-2"] - branches["upper_root"]["paths"][path]["D4_eV-2"] for path in ("log", "energy")},
            "interpretation": "Algebra from the two existing branch coefficients only; no additional sign or finite-width acceptance claim",
        }
        self.result["arithmetic"] = {"precision_decimal_digits": getcontext().prec, "rounding": getcontext().rounding, "fixed_tolerance": "1e-60", "S0_s-4": s0, "S4_s-4_eV-4": s4, "D4_scale_eV-2": d4_scale, "no_tolerance_or_precision_sweep": True, "shared_primitives": "Decimal scalar ln and exp; same fixed fit and J; independent series recurrences"}

    def toy_response(self, kernel, sign, root_coefficients, moments):
        self.counts["exact_toy_response_series_builds"] += 1
        delta = ExactSeries4([0, 1])
        r = 2 - delta
        actual_w = ExactSeries4(root_coefficients)
        v = actual_w - moments[2] * delta**2
        endpoint = -sign*r
        interior = sign*v/r

        def average(center):
            result = ExactSeries4(0)
            for degree, coefficient in enumerate(kernel):
                for n in range(degree+1):
                    result += coefficient * comb(degree, n) * center**(degree-n) * delta**n * moments[n]
            return result

        numerator = v*average(endpoint) + r**2*average(interior)
        denominator = r**2 + v
        return numerator/denominator, numerator, denominator

    def exact_toys(self):
        all_results = {}
        for kernel_name in KERNEL_ORDER:
            beta = Fraction(0) if kernel_name == "cubic" else Fraction(1, 100)
            kernel = [Fraction(1), Fraction(0), Fraction(1), Fraction(-1, 10), beta]
            self.counts["exact_toy_kernel_sign_bound_cases"] += 1
            min_k2 = Fraction(4, 5) if kernel_name == "cubic" else Fraction(32, 25)
            max_k3 = Fraction(-3, 5) if kernel_name == "cubic" else Fraction(-3, 25)
            self.check("TOY." + kernel_name + ".derivative_bounds", min_k2 > 0 and max_k3 < 0 and min_k2 == 2 - Fraction(3, 5)*2 + 12*beta*4 and max_k3 == -Fraction(3, 5) + 24*beta*2, min_ksecond=min_k2, max_kthird=max_k3, interval="[-2,2]", basis="k''' affine and negative implies k'' decreasing; endpoint rational bounds")
            kernel_results = {}
            for branch, sign in (("upper", 1), ("lower", -1)):
                self.counts["exact_toy_branches"] += 1
                prefix = "TOY." + kernel_name + "." + branch
                r, w = Fraction(2), Fraction(1)
                endpoint, interior = -sign*r, sign*w/r
                q = r*r + w
                numerator = w*rational_polynomial(kernel, endpoint) + r*r*rational_polynomial(kernel, interior)
                level = numerator/q
                nw = rational_polynomial(kernel, endpoint) + sign*r*rational_polynomial_derivative(kernel, interior)
                gw = nw - level
                slope = gw/q
                direct_a = Fraction(40+3*sign, 20) if kernel_name == "cubic" else Fraction(813+60*sign, 400)
                direct_c = Fraction(10+sign, 10) if kernel_name == "cubic" else Fraction(411+40*sign, 400)
                self.check(prefix + ".base_level", level == direct_a and slope == direct_c and level != 0 and slope > 0 and q*slope == nw-level, A=level, C=slope, hand_derived_A=direct_a, hand_derived_C=direct_c, Q=q, N_W=nw, G_W=gw, exact=True)
                fixed = {}
                for profile in PROFILE_ORDER:
                    fixed[profile] = self.toy_response(kernel, sign, [w], self.moments[profile])[0].c
                fixed_difference = [a-b for a, b in zip(fixed["p4"], fixed["uniform"])]
                expected_response = [Fraction(0)]*4 + [beta*self.delta_mu4]
                self.check(prefix + ".response_difference", fixed_difference == expected_response, actual=fixed_difference, expected=expected_response)
                roots, steps, final_residuals = {}, {}, {}
                for profile in PROFILE_ORDER:
                    self.counts["exact_toy_profile_root_series"] += 1
                    coeff = [w] + [Fraction(0)]*4
                    profile_steps = []
                    for order in range(1, 5):
                        self.counts["exact_toy_formal_root_steps"] += 1
                        normalized, nseries, qseries = self.toy_response(kernel, sign, coeff, self.moments[profile])
                        gseries = nseries - level*qseries
                        from_numerator = -gseries.c[order]/gw
                        from_normalized = -normalized.c[order]/slope
                        profile_steps.append({"order": order, "N_minus_AQ_coefficient": gseries.c[order], "F_minus_A_coefficient": normalized.c[order], "root_coefficient_from_numerator": from_numerator, "root_coefficient_from_normalized": from_normalized, "equal": from_numerator == from_normalized})
                        coeff[order] = from_numerator
                    ffinal, nfinal, qfinal = self.toy_response(kernel, sign, coeff, self.moments[profile])
                    norm_residual = (ffinal-level).c
                    num_residual = (nfinal-level*qfinal).c
                    self.check(prefix + "." + profile + ".root_series", norm_residual == [Fraction(0)]*5 and num_residual == [Fraction(0)]*5, coefficients=coeff, normalized_residual=norm_residual, numerator_residual=num_residual, same_A=level)
                    roots[profile], steps[profile] = coeff, profile_steps
                    final_residuals[profile] = {"normalized": norm_residual, "unnormalized": num_residual}
                difference = [a-b for a, b in zip(roots["p4"], roots["uniform"])]
                expected_d4 = -beta*self.delta_mu4/slope
                direct_d4 = Fraction(0) if kernel_name == "cubic" else -Fraction(32, 315*(411+40*sign))
                expected_root = [Fraction(0)]*4 + [expected_d4]
                self.check(prefix + ".root_difference", difference == expected_root and expected_d4 == direct_d4, actual=difference, expected=expected_root, hand_derived_D4=direct_d4, first_three_common=True if difference[1:4] == [Fraction(0)]*3 else False)
                self.check(prefix + ".normalized_unnormalized_steps", all(step["equal"] for profile_steps in steps.values() for step in profile_steps), comparisons=8, residual_preserving=True)
                negatives = {}
                if kernel_name == "quartic":
                    k4 = 24*beta
                    missing_24 = -self.delta_mu4*k4/slope
                    self.check(prefix + ".negative_control_missing24", missing_24 != expected_d4 and missing_24 == 24*expected_d4 and difference[4] == expected_d4, correct=expected_d4, incorrect=missing_24, wrong_minus_correct=missing_24-expected_d4, expected="Incorrect no-factorial formula is rejected")
                    dropped_a = -beta*self.delta_mu4*q/nw
                    self.check(prefix + ".negative_control_dropped_A", dropped_a != expected_d4 and difference[4] == expected_d4, correct=expected_d4, incorrect=dropped_a, retained_A=level, wrong_minus_correct=dropped_a-expected_d4, expected="Incorrect denominator N_W instead of N_W-A is rejected")
                    negatives = {"missing24": missing_24, "dropped_A": dropped_a}
                kernel_results[branch] = {"kernel_coefficients": kernel, "A": level, "C": slope, "Q": q, "N_W": nw, "G_W": gw, "fixed_W_response_coefficients": fixed, "fixed_W_response_difference": fixed_difference, "formal_root_coefficients": roots, "root_difference": difference, "formal_steps": steps, "final_residuals": final_residuals, "negative_controls": negatives}
            all_results[kernel_name] = kernel_results
        self.result["exact_polynomial_toys"] = all_results

    def run(self):
        self.verify_inputs()
        self.exact_profiles()
        self.exact_operator_checks()
        self.physical_outputs()
        self.exact_toys()
        expected_counts = self.protocol["expected_counts_per_main"]
        self.check("LEDGER.exact_counts", self.counts == expected_counts, actual=self.counts, expected=expected_counts)
        expected_ids = self.protocol["expected_check_ids"]
        self.check("LEDGER.check_id_order", [row["id"] for row in self.checks] == expected_ids[:-1], actual_before_this_row=[row["id"] for row in self.checks], expected_before_this_row=expected_ids[:-1])
        passed = all(row["pass"] for row in self.checks)
        self.result["status"] = "PASS_SCOPED" if passed else "FAIL"
        return 0 if passed else 1

    def finish(self):
        self.result["checks"] = self.checks
        self.result["actual_counts"] = self.counts
        expected_ids = getattr(self, "protocol", {}).get("expected_check_ids", [])
        executed = [row["id"] for row in self.checks]
        self.result["summary"] = {"evaluated_checks": len(self.checks), "passing_checks": sum(row["pass"] for row in self.checks), "failing_check_ids": [row["id"] for row in self.checks if not row["pass"]], "not_evaluated_check_ids": [check_id for check_id in expected_ids if check_id not in executed], "maximum_scaled_error": max(self.scaled_errors, default=Decimal(0)), "fixed_tolerance": "1e-60", "no_post_result_tolerance_change": True}
        return self.result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise FileExistsError("Refuse duplicate output before scientific execution: " + str(output))
    output.parent.mkdir(parents=True, exist_ok=True)
    experiment = Experiment(Path(__file__).resolve().parents[2])
    exit_code = 2
    with localcontext() as context:
        context.prec = 80
        context.rounding = ROUND_HALF_EVEN
        try:
            exit_code = experiment.run()
        except Exception as error:
            experiment.result["status"] = "FAIL_EXCEPTION"
            experiment.result["observed_exception"] = {"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc(), "failure_layer": "UNCLASSIFIED_OBSERVED_EXCEPTION_NO_FALLBACK"}
            traceback.print_exc(file=sys.stderr)
        result = experiment.finish()
        with output.open("x", encoding="utf-8") as stream:
            json.dump(json_value(result), stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    print(json.dumps({"task": "REI-PHYS31-20261011", "status": result["status"], "summary": json_value(result["summary"]), "actual_counts": experiment.counts}, ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
