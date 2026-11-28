#!/usr/bin/env python3
"""Independent numerical reference for the bounded WU088_HH R6 obligation.

PREPARED, NOT EXECUTED by its author. Importing this module runs no science.
No production module is imported. This program is a numerical crosscheck,
not a floating-point replacement for the rational proof certificate.

Run only after the root's S01 contract and explicit execution instruction:
  python reference_r6.py --input INPUT.json --output RESULT.json

Input schema: WU_R6_REFERENCE_INPUT_V1
{
  "schema": "WU_R6_REFERENCE_INPUT_V1",
  "contract_id": "...", "primary_run_id": "...",
  "source": {"path": "...", "sha256": "...", "temperature_K": "100",
             "collider_id": 2, "rate_unit_cm3_s": "1e-11"},
  "primary_result_path": "...",  // or embedded "primary_result"
  "forced_controls": [...],      // may also live in primary_result
  "switched_graphs": [...]       // optional piecewise-constant controls
}

Primary export, independently consumable without importing its producer:
{
 "thermal": {
   "level_ids": [1,...,9],
   "exp_neg_z": [{"lo": rational, "hi": rational}, ...],
   "pi": [{"lo": rational, "hi": rational}, ...],
   "pair_ratios": [{"upper_id": 2,"lower_id": 1,"lo":...,"hi":...}, ...]
 },
 "graph": {
   "lambda": rational, "K_lo": matrix, "K_hi": matrix,
   "P_lower": matrix,
   "blocks": [{"id": "...", "H": rational, "N": int,
               "precision_bits": int, "exp_neg_mu": {"lo":...,"hi":...},
               "R_lower": matrix, "beta_lower": rational,
               "rho_upper": rational}, ...]
 }
}

Rationals are integer/decimal/fraction strings, integers, objects
{"num": integer_string, "den": integer_string}, or dyadics
{"num": integer_string, "den_exp": nonnegative_integer}.
Binary JSON floats are rejected for certified quantities.

Each optional forced control provides id, K (matrix or "source"), pi
(vector or "source"), v=hd, f, x0, Xbar0, kappa, H, steps, coefficients
{k_lower,b_lower,q_upper,g_upper,s_upper,F_upper}, endpoints
[{M,U,E}, ...] including t=0, and whole_blocks [{M,U,E}, ...].
Its optional certificate is a block object above plus lambda/P_lower.
All such controls are mathematical fixtures, not recovered physical inputs.
The constant-coefficient exact solution is independently evaluated through
an augmented matrix exponential; within-block samples are numerical checks,
not an exhaustive proof over continuous time.

Optional switched graph: {id, segments:[{duration:rational,A:rational_matrix},...],
certificate:{id,H,lambda,P_lower,N,precision_bits,exp_neg_mu,R_lower,
beta_lower,rho_upper}}. Durations sum exactly to H. The reference propagator
is the chronologically ordered product of separate matrix exponentials;
each supplied rational generator must dominate the common P_lower exactly.

Limits: n<=9; N<=512; precision_bits<=768; lambda*H<=256; <=8 supplied
source-graph blocks; <=3 forced fixtures; <=16 blocks per fixture.
Python decimal.Decimal uses 250 decimal digits. No mpmath installation is
required. SciPy double-precision errors are reported
with explicit tolerances. Narrower-than-working-precision enclosures are
labelled numerically compatible, not independently proved by this run.
CPU has a 58 s internal interrupt, reserving time to write a <=60 s receipt.
"""

from __future__ import annotations

import argparse
import datetime as dt
import decimal
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time
import traceback


REFERENCE_DIGITS = 250
REFERENCE_GUARD_DIGITS = 15
SCIPY_ATOL = 2e-12
SCIPY_RTOL = 2e-11
CPU_INTERRUPT_SECONDS = 58.0
SOURCE_MAX_N = 9
MAX_GRAPH_BLOCKS = 8
MAX_FORCED_FIXTURES = 3
MAX_FORCED_STEPS = 16


class BudgetExceeded(RuntimeError):
    pass


class HighPrecisionDecimal:
    """Small independent transcendental reference using Python/libmpdec.

    The reference process owns its decimal context. This numerical path does
    not call the production alternating-series or dyadic arithmetic code.
    Subtraction in expm1 is only used by fixed, non-small analytic controls;
    the zero-rate limit is handled analytically by their caller.
    """

    def __init__(self):
        decimal.getcontext().prec = REFERENCE_DIGITS
        decimal.getcontext().rounding = decimal.ROUND_HALF_EVEN

    @staticmethod
    def number(value):
        if isinstance(value, float):
            raise TypeError("Decimal reference must not ingest a binary float")
        return decimal.Decimal(value)

    @staticmethod
    def exp(value):
        return decimal.Decimal(value).exp()

    @staticmethod
    def expm1(value):
        return decimal.Decimal(value).exp() - decimal.Decimal(1)

    @staticmethod
    def power(base, exponent):
        return decimal.Decimal(base) ** exponent

    @staticmethod
    def fsum(values):
        return sum(values, decimal.Decimal(0))

    @staticmethod
    def nstr(value, digits):
        return format(value, f".{digits}g")


def rational(value):
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("Certified input must not be a JSON bool/float")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, dict):
        num = int(value.get("num", value.get("numerator")))
        if "den_exp" in value:
            p = int(value["den_exp"])
            if not 0 <= p <= 20000:
                raise ValueError("Invalid dyadic exponent")
            return Fraction(num, 1 << p)
        return Fraction(num, int(value.get("den", value.get("denominator"))))
    raise TypeError("Unsupported rational representation")


def matrix_rational(values, n):
    if len(values) != n or any(len(row) != n for row in values):
        raise ValueError("Matrix dimension does not match the independently read source")
    return [[rational(v) for v in row] for row in values]


def rational_text(value):
    value = rational(value) if not isinstance(value, Fraction) else value
    return str(value.numerator) if value.denominator == 1 else str(value)


def resolve_path(value, base):
    p = Path(value)
    return p if p.is_absolute() else base / p


def load_lamda(path, expected_sha):
    """Parse LAMDA structure independently, without any project parser."""
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha:
        raise ValueError("Original LAMDA byte hash mismatch")
    records = [line.strip() for line in raw.decode("utf-8").splitlines()
               if line.strip() and not line.lstrip().startswith("!")]
    cursor = 0

    def take():
        nonlocal cursor
        if cursor >= len(records):
            raise ValueError("Unexpected end of LAMDA source")
        result = records[cursor]
        cursor += 1
        return result

    molecule, weight = take(), take()
    n = int(take())
    if not 1 <= n <= SOURCE_MAX_N:
        raise ValueError("Native state count exceeds the R6 contract")
    levels = []
    for _ in range(n):
        cols = take().split()
        levels.append({"id": int(cols[0]), "energy_cm_inv": cols[1],
                       "weight": cols[2], "quantum_label": " ".join(cols[3:])})
    if [x["id"] for x in levels] != list(range(1, n + 1)):
        raise ValueError("Unsupported nonconsecutive native level identifiers")
    radiative_count = int(take())
    for _ in range(radiative_count):
        take()  # Radiative coefficients are deliberately outside this graph.
    partners = {}
    for _ in range(int(take())):
        label = take()
        partner_id = int(label.split()[0])
        count = int(take())
        nt = int(take())
        temperatures = []
        while len(temperatures) < nt:
            temperatures.extend(take().split())
        if len(temperatures) != nt:
            raise ValueError("Ambiguous LAMDA temperature records")
        transitions = []
        for _ in range(count):
            cols = take().split()
            if len(cols) != nt + 3:
                raise ValueError("Unexpected number of native rate columns")
            transitions.append({"id": int(cols[0]), "upper": int(cols[1]),
                                "lower": int(cols[2]), "rates": cols[3:]})
        if partner_id in partners:
            raise ValueError("Duplicate native collider identifier")
        partners[partner_id] = {"label": label, "temperatures": temperatures,
                                "transitions": transitions}
    if cursor != len(records):
        raise ValueError("Unconsumed native source records")
    return {"sha256": digest, "molecule": molecule, "molecular_weight": weight,
            "levels": levels, "partners": partners, "n": n,
            "radiative_rows_excluded": radiative_count}


class Reference:
    def __init__(self, result):
        # Limit numerical libraries to a single thread inside this process.
        for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
            os.environ[key] = "1"
        import numpy as np
        import scipy
        from scipy.linalg import expm
        from scipy.sparse.linalg import expm_multiply
        self.hp, self.np = HighPrecisionDecimal(), np
        self.expm, self.expm_multiply = expm, expm_multiply
        self.result = result
        self.cases = result["cases"]
        self.result["versions"] = {"python": sys.version.split()[0],
                                   "decimal_module": decimal.__version__,
                                   "libmpdec": decimal.__libmpdec_version__,
                                   "numpy": np.__version__,
                                   "scipy": scipy.__version__}

    def m(self, value):
        value = value if isinstance(value, Fraction) else rational(value)
        return self.hp.number(value.numerator) / value.denominator

    def record(self, name, passed, kind, observations):
        self.cases.append({"case": name, "status": "CONSISTENT" if passed else "MISMATCH",
                           "evidence_level": kind, "observations": observations})

    def exp_interval(self, name, ref, interval):
        lo, hi = rational(interval["lo"]), rational(interval["hi"])
        low, high = self.m(lo), self.m(hi)
        guard = self.hp.power(10, -(REFERENCE_DIGITS - REFERENCE_GUARD_DIGITS)) * max(
            abs(ref), abs(low), abs(high), self.hp.power(10, -REFERENCE_DIGITS))
        compatible = lo <= hi and low - guard <= ref <= high + guard
        strict_margin = min(ref - low, high - ref)
        self.record(name, compatible, f"{REFERENCE_DIGITS}_decimal_digit_numerical_consistency",
                    {"reference": self.hp.nstr(ref, REFERENCE_DIGITS),
                     "lower": rational_text(lo), "upper": rational_text(hi),
                     "guard": self.hp.nstr(guard, 12),
                     "strict_margin": self.hp.nstr(strict_margin, 12),
                     "resolution": ("OUTSIDE_ENCLOSURE_BEYOND_GUARD" if not compatible
                                    else "INTERIOR_RESOLVED" if strict_margin > guard
                                    else f"NUMERICALLY_COMPATIBLE_BUT_NOT_RESOLVED_AT_{REFERENCE_DIGITS}_DPS"),
                     "rigorous_interval_verification": False})

    def float_matrix(self, values):
        return self.np.array([[float(v) for v in row] for row in values], dtype=float)

    def numeric_lower(self, name, lower, actual):
        lower = self.float_matrix(lower)
        slack = actual - lower
        tolerance = SCIPY_ATOL + SCIPY_RTOL * max(1.0, float(self.np.max(self.np.abs(actual))))
        self.record(name, bool(self.np.min(slack) >= -tolerance),
                    "scipy_double_precision_entrywise_reference",
                    {"minimum_entrywise_slack": float(self.np.min(slack)),
                     "tolerance": tolerance, "formal_outward_proof": False})

    def dobrushin(self, matrix):
        n = matrix.shape[0]
        if n == 1:
            return 0.0
        return max(0.5 * float(self.np.sum(self.np.abs(matrix[:, j] - matrix[:, k])))
                   for j in range(n) for k in range(j + 1, n))

    def source_reference(self, contract, base):
        source = contract["source"]
        data = load_lamda(resolve_path(source["path"], base), source["sha256"])
        if rational(source["temperature_K"]) != 100 or int(source["collider_id"]) != 2:
            raise ValueError("Only literal native 100 K para-H2 is admitted")
        rate_scale = rational(source["rate_unit_cm3_s"])
        if rate_scale <= 0:
            raise ValueError("Nonpositive declared dimensionless rate scale")
        partner = data["partners"][2]
        matches = [i for i, t in enumerate(partner["temperatures"]) if rational(t) == 100]
        if len(matches) != 1:
            raise ValueError("Native 100 K column is absent or ambiguous")
        tidx = matches[0]
        levels, n = data["levels"], data["n"]
        factor = self.m("6.62607015e-34") * self.m("299792458") * 100 / (
            self.m("1.380649e-23") * 100)
        energy0 = self.m(levels[0]["energy_cm_inv"])
        z = [factor * (self.m(x["energy_cm_inv"]) - energy0) for x in levels]
        boltzmann = [self.hp.exp(-value) for value in z]
        weights = [self.m(x["weight"]) * b for x, b in zip(levels, boltzmann)]
        total = self.hp.fsum(weights)
        pi = [w / total for w in weights]
        K = [[self.hp.number(0) for _ in range(n)] for _ in range(n)]
        ratios = {}
        for row in partner["transitions"]:
            u, l = row["upper"] - 1, row["lower"] - 1
            if not (0 <= l < u < n):
                raise ValueError("Unexpected native transition orientation")
            down = self.m(row["rates"][tidx]) / self.m(rate_scale)
            ratio = self.m(levels[u]["weight"]) / self.m(levels[l]["weight"]) * self.hp.exp(-(z[u] - z[l]))
            K[l][u] += down
            K[u][l] += down * ratio
            ratios[(u + 1, l + 1)] = ratio
        for j in range(n):
            K[j][j] = -self.hp.fsum(K[i][j] for i in range(n) if i != j)
        equilibrium_error = max(abs(self.hp.fsum(K[i][j] * pi[j] for j in range(n))) for i in range(n))
        self.record("native_source_independent_parse_and_balance",
                    equilibrium_error < self.hp.power(10, -(REFERENCE_DIGITS - 20)),
                    "native_byte_binding_and_high_precision_reconstruction",
                    {"source_sha256": data["sha256"], "n": n,
                     "native_downward_rows": len(partner["transitions"]),
                     "collider_id": 2, "temperature_K": "100",
                     "Kpi_max_abs_high_precision": self.hp.nstr(equilibrium_error, 12),
                     "decimal_digits": REFERENCE_DIGITS,
                     "rate_unit_cm3_s": rational_text(rate_scale),
                     "clock": "tau = collider_density * rate_unit_cm3_s * proper_time; density UNBOUND",
                     "missing_transitions": "MISSING_NOT_ZERO",
                     "vibrational_state": "UNSPECIFIED"})
        self.n, self.K_decimal, self.pi_decimal = n, K, pi
        self.K = self.np.array(K, dtype=float)
        self.pi = self.np.array([float(p) for p in pi])
        return boltzmann, pi, ratios

    def thermal_checks(self, primary, reference):
        thermal = primary["thermal"]
        boltzmann, pi, ratios = reference
        if thermal["level_ids"] != list(range(1, self.n + 1)):
            raise ValueError("Primary level identity mismatch")
        for key in ("exp_neg_z", "pi"):
            if len(thermal[key]) != self.n:
                raise ValueError("Incomplete thermal interval export")
        for i, (b, p) in enumerate(zip(boltzmann, pi)):
            self.exp_interval(f"boltzmann_level_{i + 1}", b, thermal["exp_neg_z"][i])
            self.exp_interval(f"normalized_pi_level_{i + 1}", p, thermal["pi"][i])
        supplied = set()
        for record in thermal["pair_ratios"]:
            pair = (int(record["upper_id"]), int(record["lower_id"]))
            if pair in supplied or pair not in ratios:
                raise ValueError("Duplicate or nonsource pair ratio")
            supplied.add(pair)
            self.exp_interval(f"direct_pair_ratio_{pair[0]}_{pair[1]}", ratios[pair], record)
        if supplied != set(ratios):
            raise ValueError("Not all native pair-ratio intervals were exported")

    def graph_checks(self, primary):
        graph = primary["graph"]
        n = self.n
        Klo = matrix_rational(graph["K_lo"], n)
        Khi = matrix_rational(graph["K_hi"], n)
        self.record("source_generator_interval_order", all(Klo[i][j] <= Khi[i][j]
                    and (i == j or Klo[i][j] >= 0) for i in range(n) for j in range(n)),
                    "exact_rational_input_consistency", {})
        self.numeric_lower("source_generator_lower", Klo, self.K)
        self.numeric_lower("source_generator_upper", [[-v for v in row] for row in Khi], -self.K)
        lam = rational(graph["lambda"])
        exits = [sum(Khi[i][j] for i in range(n) if i != j) for j in range(n)]
        self.record("uniformization_exit_bound", lam > 0 and all(e <= lam for e in exits),
                    "exact_rational_input_consistency",
                    {"lambda": rational_text(lam), "max_exit_upper": rational_text(max(exits))})
        Plo = matrix_rational(graph["P_lower"], n)
        self.record("P_lower_nonnegative_substochastic", all(v >= 0 for row in Plo for v in row)
                    and all(sum(Plo[i][j] for i in range(n)) <= 1 for j in range(n)),
                    "exact_rational_input_consistency", {})
        self.numeric_lower("P_lower_against_actual_source", Plo, self.np.eye(n) + self.K / float(lam))
        blocks = graph["blocks"]
        if not 1 <= len(blocks) <= MAX_GRAPH_BLOCKS:
            raise ValueError("Graph H count exceeds the admitted finite search")
        for block in blocks:
            self.certificate_block(block, self.K, lam, Plo, "source_graph")

    def certificate_block(self, block, A, lam, Plo, prefix, transition_reference=None):
        n = A.shape[0]
        H = rational(block["H"])
        N, p = int(block["N"]), int(block["precision_bits"])
        mu = lam * H
        if not (H > 0 and 0 <= N <= 512 and 1 <= p <= 768 and 0 < mu <= 256):
            raise ValueError("Certificate parameters exceed the R6 contract")
        tag = f"{prefix}:{block['id']}"
        self.exp_interval(tag + ":exp_neg_mu", self.hp.exp(-self.m(mu)), block["exp_neg_mu"])
        R = matrix_rational(block["R_lower"], n)
        dyadic_ok = all(v >= 0 and v.denominator & (v.denominator - 1) == 0
                        and v.denominator.bit_length() - 1 <= p for row in R for v in row)
        beta = min((sum(min(R[i][j], R[i][k]) for i in range(n))
                    for j in range(n) for k in range(j + 1, n)), default=Fraction(1))
        declared_beta, rho = rational(block["beta_lower"]), rational(block["rho_upper"])
        exact_ok = (dyadic_ok and 0 <= declared_beta <= beta <= 1
                    and 1 - declared_beta <= rho <= 1
                    and all(sum(R[i][j] for i in range(n)) <= 1 for j in range(n)))
        self.record(tag + ":dyadic_and_overlap", exact_ok, "exact_rational_input_consistency",
                    {"H": rational_text(H), "mu": rational_text(mu), "N": N,
                     "precision_bits": p, "recomputed_overlap": rational_text(beta),
                     "declared_beta_lower": rational_text(declared_beta), "rho_upper": rational_text(rho)})
        S = self.expm(A * float(H)) if transition_reference is None else transition_reference
        self.numeric_lower(tag + ":R_lower_vs_transition", R, S)
        stoch_error = float(self.np.max(self.np.abs(self.np.sum(S, axis=0) - 1)))
        self.record(tag + ":expm_stochasticity", stoch_error <= SCIPY_ATOL + SCIPY_RTOL
                    and float(self.np.min(S)) >= -SCIPY_ATOL,
                    "scipy_double_precision_reference", {"max_column_sum_error": stoch_error})
        power = self.np.eye(n)
        for exponent in (1, 2, 3):
            power = power @ S
            actual = self.dobrushin(power)
            bound = float(rho ** exponent)
            tolerance = SCIPY_ATOL + SCIPY_RTOL
            self.record(tag + f":semigroup_power_{exponent}", actual <= bound + tolerance,
                        "scipy_double_precision_semigroup_reference",
                        {"block_power": exponent, "dobrushin_reference": actual,
                         "rho_power_bound": bound, "tolerance": tolerance,
                         "new_graph_H_selection": False})
        return S

    def switched_graph(self, fixture):
        segments = fixture["segments"]
        if not 1 <= len(segments) <= MAX_FORCED_STEPS:
            raise ValueError("Switched graph segment count exceeds the bounded control")
        certificate = fixture["certificate"]
        lam = rational(certificate["lambda"])
        if lam <= 0:
            raise ValueError("Nonpositive switched uniformization rate")
        n = len(segments[0]["A"])
        if not 1 <= n <= SOURCE_MAX_N:
            raise ValueError("Switched graph dimension exceeds scope")
        Plo = matrix_rational(certificate["P_lower"], n)
        elapsed, S = Fraction(0), self.np.eye(n)
        bound_ok = True
        generators = []
        for index, segment in enumerate(segments):
            duration = rational(segment["duration"])
            if duration <= 0:
                raise ValueError("Nonpositive switched segment duration")
            elapsed += duration
            A = matrix_rational(segment["A"], n)
            generator_ok = (all(sum(A[i][j] for i in range(n)) == 0 for j in range(n))
                            and all(A[i][j] >= 0 for i in range(n) for j in range(n) if i != j))
            local_bound = all(Plo[i][j] <= (Fraction(i == j) + A[i][j] / lam)
                              for i in range(n) for j in range(n))
            bound_ok = bound_ok and generator_ok and local_bound
            numeric_A = self.float_matrix(A)
            generators.append(numeric_A)
            S = self.expm(numeric_A * float(duration)) @ S
        if elapsed != rational(certificate["H"]):
            raise ValueError("Switched segment durations do not sum to certificate H")
        self.record("switched:" + str(fixture["id"]) + ":common_generator_bound", bound_ok,
                    "exact_rational_piecewise_generator_consistency",
                    {"segment_count": len(segments), "H": rational_text(elapsed),
                     "chronological_order": "exp(A_last*dt_last)...exp(A_first*dt_first)",
                     "scope": "synthetic_piecewise_constant_control"})
        self.certificate_block(certificate, generators[0], lam, Plo,
                               "switched:" + str(fixture["id"]), transition_reference=S)

    def forced_fixture(self, fixture):
        np = self.np
        K = self.K if fixture["K"] == "source" else self.float_matrix(
            matrix_rational(fixture["K"], len(fixture["K"])))
        n = K.shape[0]
        pi = self.pi if fixture["pi"] == "source" else np.array([float(rational(p)) for p in fixture["pi"]])
        vectors = {name: np.array([float(rational(v)) for v in fixture[name]])
                   for name in ("v", "f", "x0")}
        if n > SOURCE_MAX_N or any(len(v) != n for v in vectors.values()) or len(pi) != n:
            raise ValueError("Forced fixture dimension mismatch")
        v, f, x0 = (vectors[k] for k in ("v", "f", "x0"))
        H, kappa = float(rational(fixture["H"])), float(rational(fixture["kappa"]))
        steps = int(fixture["steps"])
        if not (H > 0 and 1 <= steps <= MAX_FORCED_STEPS):
            raise ValueError("Forced clock exceeds finite control scope")
        Xbar0 = float(rational(fixture["Xbar0"]))
        if (min(float(np.min(v)), float(np.min(f)), float(np.min(x0)), float(np.min(pi))) < 0
                or abs(float(np.sum(pi)) - 1) > SCIPY_ATOL
                or kappa < 0 or kappa > float(np.min(v)) + SCIPY_ATOL):
            raise ValueError("Forced fixture positivity/simplex/killing condition fails")
        name = "forced:" + str(fixture["id"])
        vbar, F = float(pi @ v), float(np.sum(f))
        B = np.outer(pi, v) - np.diag(v)
        L = K + B
        A = K + np.outer(pi, v - kappa) - np.diag(v - kappa)
        Z = np.eye(n)[:, :max(n - 1, 0)]
        if n > 1:
            Z[-1, :] = -1
        residual_identity = float(np.max(np.abs((L - A + kappa * np.eye(n)) @ Z))) if n > 1 else 0.0
        SL, SA = self.expm(L * H), self.expm(A * H)
        split_error = float(np.max(np.abs((SL - np.exp(-kappa * H) * SA) @ Z))) if n > 1 else 0.0
        self.record(name + ":common_killing_split", residual_identity <= SCIPY_ATOL
                    and split_error <= SCIPY_ATOL + SCIPY_RTOL,
                    "independent_matrix_exponential_identity",
                    {"algebraic_zero_sum_residual": residual_identity,
                     "propagator_split_error": split_error,
                     "K_reset_commutator_norm": float(np.linalg.norm(K @ B - B @ K, ord=1)),
                     "kappa": kappa, "rho_must_belong_to": "A = L - kappa*(pi*1T-I)"})
        if "certificate" in fixture:
            cert = fixture["certificate"]
            if rational(cert["H"]) != rational(fixture["H"]):
                raise ValueError("Forced block certificate uses a different H")
            lam = rational(cert["lambda"])
            Plo = matrix_rational(cert["P_lower"], n)
            self.numeric_lower(name + ":P_lower_vs_full_A", Plo, np.eye(n) + A / float(lam))
            self.certificate_block(cert, A, lam, Plo, name + ":full_A")
        coeff = {key: float(rational(val)) for key, val in fixture["coefficients"].items()}
        c = K @ pi - (v * pi - pi * vbar)
        g = f - pi * F
        coefficient_ok = (all(value >= 0 for value in coeff.values())
                          and 0 <= coeff["k_lower"] <= float(np.min(v)) + SCIPY_ATOL
                          and 0 <= coeff["b_lower"] <= vbar + SCIPY_ATOL
                          and coeff["q_upper"] + SCIPY_ATOL >= float(np.sum(np.abs(c)))
                          and coeff["g_upper"] + SCIPY_ATOL >= float(np.sum(np.abs(g)))
                          and coeff["F_upper"] + SCIPY_ATOL >= F
                          and coeff["s_upper"] + SCIPY_ATOL >= float(np.ptp(v)) / 2)
        self.record(name + ":coefficient_bounds", coefficient_ok,
                    "constant_fixture_direct_coefficient_reference",
                    {"c_l1": float(np.sum(np.abs(c))), "Qf_l1": float(np.sum(np.abs(g))),
                     "total_formation_F": F, "F_upper": coeff["F_upper"],
                     "min_v": float(np.min(v)), "vbar": vbar, "osc_v_over_2": float(np.ptp(v)) / 2})
        aug = np.zeros((n + 2, n + 2))
        aug[:n, :n] = K - np.diag(v)
        aug[:n, -1] = f
        aug[n, n], aug[n, -1] = -vbar, F
        initial = np.concatenate((x0, [Xbar0, 1.0]))
        samples = self.expm_multiply(aug, initial, start=0.0, stop=steps * H,
                                     num=4 * steps + 1, endpoint=True, traceA=float(np.trace(aug)))
        endpoints = fixture["endpoints"]
        interiors = fixture["whole_blocks"]
        if len(endpoints) != steps + 1 or len(interiors) != steps:
            raise ValueError("Forced primary envelope has wrong clock count")
        worst = {"M": 0.0, "U": 0.0, "E": 0.0}
        failures = []
        for index, state in enumerate(samples):
            x, xbar = state[:n], float(state[n])
            X = float(np.sum(x))
            actual = {"M": X, "U": float(np.sum(np.abs(x - pi * X))), "E": abs(X - xbar)}
            if index % 4 == 0:
                block_index = index // 4
                envelopes = [("endpoint", endpoints[block_index])]
                if block_index > 0:
                    envelopes.append(("previous_whole_block", interiors[block_index - 1]))
                if block_index < steps:
                    envelopes.append(("next_whole_block", interiors[block_index]))
            else:
                envelopes = [("whole_block", interiors[index // 4])]
            for envelope_kind, primary in envelopes:
                for key in actual:
                    bound = float(rational(primary[key]))
                    gap = actual[key] - bound
                    worst[key] = max(worst[key], gap)
                    tol = SCIPY_ATOL + SCIPY_RTOL * max(1.0, abs(actual[key]), abs(bound))
                    if gap > tol:
                        failures.append({"sample": index, "component": key,
                                         "envelope_kind": envelope_kind,
                                         "excess": gap, "tolerance": tol})
        self.record(name + ":M_U_E_clock_envelopes", not failures,
                    "independent_augmented_linear_exponential_reference",
                    {"H": H, "steps": steps, "sample_count": len(samples),
                     "interior_fractions": ["1/4", "1/2", "3/4"],
                     "worst_positive_excess": worst, "failures": failures,
                     "continuous_time_proof": False, "physical_scope": "synthetic_constant_coefficient_control"})

    def analytic_controls(self):
        """Two-state forced exact formula, tested under three clock scalings."""
        hp, np = self.hp, self.np

        def psi(rate, clock):
            return clock if rate == 0 else -hp.expm1(-rate * clock) / rate

        a, b = self.m(2), self.m(3)
        pi = [b / (a + b), a / (a + b)]
        initial = [self.m("2/3"), self.m("1/3")]
        forcing = [self.m("3/7"), self.m("2/7")]
        F, X0 = sum(forcing), sum(initial)
        r0, ur = initial[0] - pi[0] * X0, forcing[0] - pi[0] * F
        tau = self.m("1/4")
        for kappa_text in ("0", "2/5"):
            kappa = self.m(kappa_text)
            exact_X = X0 * hp.exp(-kappa * tau) + F * psi(kappa, tau)
            exact_r = r0 * hp.exp(-(a + b + kappa) * tau) + ur * psi(a + b + kappa, tau)
            expected = np.array([float(pi[0] * exact_X + exact_r), float(pi[1] * exact_X - exact_r)])
            for scale_text in ("1/1000", "1", "1000"):
                scale = float(rational(scale_text))
                T = float(tau) / scale
                matrix = np.array([[-float(a + kappa), float(b), float(forcing[0])],
                                   [float(a), -float(b + kappa), float(forcing[1])],
                                   [0.0, 0.0, 0.0]]) * scale
                observed = (self.expm(matrix * T) @ np.array([float(initial[0]), float(initial[1]), 1.0]))[:2]
                err = float(np.max(np.abs(observed - expected)))
                self.record(f"analytic_two_state:kappa={kappa_text}:clock_scale={scale_text}",
                            err <= SCIPY_ATOL + SCIPY_RTOL, "closed_form_forced_reference_control",
                            {"proper_clock_for_fixture": T, "dimensionless_tau": "1/4",
                             "clock_scale": scale_text, "kappa": kappa_text,
                             "max_abs_error": err, "zero_kappa_branch": kappa == 0,
                             "reference_is_physical_application": False})

    def run(self, contract, base):
        if contract.get("schema") != "WU_R6_REFERENCE_INPUT_V1":
            raise ValueError("Unexpected reference input schema")
        if "primary_result" in contract:
            primary = contract["primary_result"]
        else:
            p = resolve_path(contract["primary_result_path"], base)
            raw = p.read_bytes()
            self.result["primary_result_sha256"] = hashlib.sha256(raw).hexdigest()
            primary = json.loads(raw)
        self.result["contract_id"] = contract["contract_id"]
        self.result["primary_run_id"] = contract["primary_run_id"]
        thermal_reference = self.source_reference(contract, base)
        self.thermal_checks(primary, thermal_reference)
        self.graph_checks(primary)
        self.analytic_controls()
        switched = contract.get("switched_graphs", primary.get("switched_graphs", []))
        if len(switched) > 3:
            raise ValueError("Too many switched graph fixtures for the bounded run")
        for fixture in switched:
            self.switched_graph(fixture)
        self.result["switched_graph_fixture_count"] = len(switched)
        controls = contract.get("forced_controls", primary.get("forced_controls", []))
        if len(controls) > MAX_FORCED_FIXTURES:
            raise ValueError("Too many forced fixtures for this bounded run")
        for fixture in controls:
            self.forced_fixture(fixture)
        self.result["forced_primary_fixture_count"] = len(controls)
        self.result["scope_completeness"] = ("SOURCE_GRAPH_AND_FORCED_PRIMARY_CHECKED"
                                               if controls else "FORCED_PRIMARY_EXPORT_MISSING")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    input_path, output_path = Path(args.input).resolve(), Path(args.output).resolve()
    if output_path.exists():
        raise FileExistsError("Create-only result path already exists; do not silently rerun")
    started_cpu, started_wall = time.process_time(), time.monotonic()
    result = {
        "schema": "WU_R6_INDEPENDENT_REFERENCE_RESULT_V1",
        "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "STARTED", "cases": [],
        "precision": {"backend": "decimal.Decimal", "decimal_digits": REFERENCE_DIGITS,
                      "rounding": "ROUND_HALF_EVEN", "guard_digits": REFERENCE_GUARD_DIGITS,
                      "scipy_atol": SCIPY_ATOL, "scipy_rtol": SCIPY_RTOL},
        "scope": {"name": "literal_native_100K_Gibbs_and_forced_finite_block_reference",
                  "production_core_imports": False, "independent_final_C9_review": False,
                  "PHYS91_new_runs": 0, "old_scope_replays": 0,
                  "new_R6_reference_runs_consumed": 1, "maximum_n": 9,
                  "maximum_N": 512, "maximum_precision_bits": 768,
                  "maximum_mu": 256, "maximum_source_graph_H": 8,
                  "physical_destruction_arrays": "UNBOUND", "physical_production": "NOT_RUN"},
        "budget": {"cpu_allowance_seconds": 60, "internal_interrupt_seconds": CPU_INTERRUPT_SECONDS},
    }

    def on_cpu_interrupt(signum, frame):
        raise BudgetExceeded("58 CPU second internal interrupt; no retry authorized")

    old_handler = signal.signal(signal.SIGPROF, on_cpu_interrupt)
    signal.setitimer(signal.ITIMER_PROF, CPU_INTERRUPT_SECONDS)
    exit_code = 0
    try:
        raw = input_path.read_bytes()
        result["input_sha256"] = hashlib.sha256(raw).hexdigest()
        result["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        contract = json.loads(raw)
        Reference(result).run(contract, input_path.parent)
        failures = sum(case["status"] == "MISMATCH" for case in result["cases"])
        result["case_count"], result["mismatch_count"] = len(result["cases"]), failures
        complete = result["scope_completeness"] == "SOURCE_GRAPH_AND_FORCED_PRIMARY_CHECKED"
        result["status"] = ("NUMERICAL_CROSSCHECKS_COMPLETED" if not failures and complete
                            else "NUMERICAL_MISMATCH" if failures else "PARTIAL_SCOPE")
        exit_code = 0 if not failures and complete else 1
    except BudgetExceeded as exc:
        result["status"], result["error"] = "CPU_BUDGET_INTERRUPTED", str(exc)
        exit_code = 3
    except Exception as exc:
        result["status"], result["error"] = "EXECUTION_ERROR", str(exc)
        result["traceback"] = traceback.format_exc(limit=10)
        exit_code = 2
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0)
        signal.signal(signal.SIGPROF, old_handler)
        result["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        result["actual_cpu_seconds_at_finalize"] = time.process_time() - started_cpu
        result["actual_process_cpu_seconds_at_finalize"] = time.process_time()
        result["actual_wall_seconds_at_finalize"] = time.monotonic() - started_wall
        result["cpu_allowance_satisfied_at_finalize"] = result["actual_process_cpu_seconds_at_finalize"] <= 60
        result["case_count"] = len(result["cases"])
        result["mismatch_count"] = sum(case["status"] == "MISMATCH" for case in result["cases"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, ensure_ascii=False, allow_nan=False)
            handle.write("\n")
        print(json.dumps({"status": result["status"], "case_count": result["case_count"],
                          "mismatch_count": result["mismatch_count"],
                          "actual_cpu_seconds_at_finalize": result["actual_cpu_seconds_at_finalize"],
                          "output": str(output_path)}, ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
