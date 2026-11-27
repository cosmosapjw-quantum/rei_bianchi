#!/usr/bin/env python3
"""One create-only, bounded changed-obligation primary run for WU R6.

Prepared without executing scientific checks. Invoke only under CONTRACT.json.
The output contains exact certificates and actual test observations, never
prepopulated acceptance. The old R5/REC/PHYS91 suites are not invoked.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import signal
import sys
import time
import traceback

LEAF = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LEAF / "src"))
import interval_block as ib


class BudgetExceeded(RuntimeError):
    pass


def export_tree(value):
    if isinstance(value, Fraction):
        return ib.rational_text(value)
    if isinstance(value, dict):
        return {k: export_tree(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [export_tree(v) for v in value]
    return value


class Primary:
    def __init__(self, output):
        self.result = output
        self.cases = output["cases"]

    def check(self, group, name, condition, evidence=None):
        self.cases.append({"group": group, "case": name,
                           "status": "PASS" if bool(condition) else "FAIL",
                           "evidence": export_tree(evidence or {})})

    def rejects(self, name, operation):
        try:
            operation()
        except ib.DomainError as error:
            self.check("guards", name, True, {"observed_exception": type(error).__name__, "message": str(error)})
        else:
            self.check("guards", name, False, {"observed_exception": None})

    def primitives(self):
        self.check("exact_primitives", "zero_exponential_is_exact_one", ib.exp_neg(0).export() == {"lo": "1", "hi": "1"})
        for z in ("1/4", "1/2", "1", "8", "32", "128", "256"):
            q = ib.Q(z)
            e = ib.exp_neg(q, 512)
            self.check("exact_primitives", "positive_exp_global_bound_" + z,
                       0 < e.lo <= e.hi <= 1 / (1 + q), {"width": e.width})
        for z in ("1/4", "1", "8", "32"):
            coarse, fine = ib.exp_neg(z, 192), ib.exp_neg(z, 256)
            self.check("exact_primitives", "precision_enclosure_nesting_" + z,
                       coarse.lo <= fine.lo <= fine.hi <= coarse.hi,
                       {"coarse_width": coarse.width, "fine_width": fine.width})
        a, b, total = ib.exp_neg("1/4"), ib.exp_neg("1/2"), ib.exp_neg("3/4")
        self.check("exact_primitives", "exp_addition_interval_intersection",
                   max(a.lo * b.lo, total.lo) <= min(a.hi * b.hi, total.hi))
        weights = [ib.Interval(1, 2), ib.Interval(3, 4), ib.Interval(2, 3)]
        pi = ib.normalize_weights(weights)
        self.check("exact_primitives", "normalized_weight_corner_values",
                   pi[0].lo == Fraction(1, 8) and pi[0].hi == Fraction(2, 7))
        self.check("exact_primitives", "simplex_box_mass",
                   sum(p.lo for p in pi) <= 1 <= sum(p.hi for p in pi))
        flat = ib.thermal_from_levels([0, 0, 0], [1, 1, 1])
        self.check("exact_primitives", "degenerate_equal_energy_equal_probability",
                   all(p.lo == p.hi == Fraction(1, 3) for p in flat["pi"]))
        long_text = "7" * 5001 + "/" + "8" * 5000
        long_q = ib.Q(long_text)
        encoded = ib.rational_text(long_q)
        self.check("serialization", "long_rational_roundtrip_beyond_4300_digit_default",
                   ib.Q(encoded) == long_q,
                   {"input_characters": len(long_text), "canonical_characters": len(encoded),
                    "canonical_sha256": hashlib.sha256(encoded.encode()).hexdigest(),
                    "global_integer_digit_limit_modified": False})
        self.check("serialization", "canonical_sign_reduction", ib.rational_text(ib.Q("-00012/-00018")) == "2/3")
        two = ib.exact_generator([[-1, 1], [1, -1]])
        single = ib.exact_generator([[0]])
        one = ib.finite_block(single, 1, 8, 128, identifier="n1_zero_sum")
        self.check("matrix_controls", "singleton_zero_sum_subspace", one["beta_lower"] == "1" and one["rho_upper"] == "0")
        zero = ib.exact_generator([[0, 0], [0, 0]])
        no_mix = ib.finite_block(zero, 1, 8, 128, identifier="disconnected_control")
        self.check("matrix_controls", "disconnected_graph_does_not_claim_contraction", no_mix["beta_lower"] == "0" and no_mix["rho_upper"] == "1")
        first = ib.finite_block(two, "1/2", 1, 256, rate=2, identifier="analytic_rank_one_P")
        beta, e = ib.Q(first["beta_lower"]), ib.exp_neg(1, 256)
        self.check("matrix_controls", "rank_one_transition_N1_overlap", 0 <= e.lo - beta <= Fraction(2, 1 << 256),
                   {"analytic_overlap_for_exact_weight": e.lo, "computed_overlap": beta})
        bad_operations = [
            ("reject_boolean", lambda: ib.Q(True)),
            ("reject_binary64", lambda: ib.Q(0.1)),
            ("reject_zero_denominator", lambda: ib.Q("1/0")),
            ("reject_nonfinite", lambda: ib.Q("NaN")),
            ("reject_expression", lambda: ib.Q("1/2/3")),
            ("reject_unbounded_decimal_exponent", lambda: ib.Q("1e10001")),
            ("reject_negative_exp_argument", lambda: ib.exp_neg(-1)),
            ("reject_exp_outside_domain", lambda: ib.exp_neg(257)),
            ("reject_low_precision", lambda: ib.exp_neg(1, 127)),
            ("reject_nonpositive_weight", lambda: ib.normalize_weights([ib.Interval(0, 1)])),
            ("reject_nonsimplex_reset", lambda: ib.reset_generator_bounds(two, [ib.Interval(1, 1)] * 2, [ib.Interval(1, 1)] * 2)),
            ("reject_excess_killing", lambda: ib.reset_generator_bounds(two, [ib.Interval("1/2", "1/2")] * 2, [ib.Interval(0, 0)] * 2, 1)),
            ("reject_nonconservative_K", lambda: ib.exact_generator([[-1, 1], [2, -1]])),
            ("reject_negative_edge", lambda: ib.exact_generator([[1, 0], [-1, 0]])),
            ("reject_H_zero", lambda: ib.finite_block(two, 0, 8)),
            ("reject_degree_limit", lambda: ib.finite_block(two, 1, 513)),
            ("reject_precision_limit", lambda: ib.finite_block(two, 1, 8, 769)),
            ("reject_lambda_below_exit", lambda: ib.finite_block(two, 1, 8, rate="1/2")),
            ("reject_mu_limit", lambda: ib.finite_block(two, 129, 8)),
        ]
        for name, operation in bad_operations:
            self.rejects(name, operation)

    def source(self, configuration, base):
        settings = configuration["source"]
        source = (base / settings["path"]).resolve()
        parser = (base / settings["parser_path"]).resolve()
        if (settings["sha256"] != ib.SOURCE_SHA256 or settings["temperature_K"] != "100"
                or settings["collider_id"] != 2
                or ib.Q(settings["rate_unit_cm3_s"]) != ib.RATE_SCALE_CM3_S):
            raise ib.DomainError("Primary source identity/native-domain contract mismatch")
        K, thermal, exported = ib.native_hd_source(source, parser, configuration["thermal_bits"])
        self.result["thermal"] = exported
        rate, P = ib.uniformization_lower(K)
        self.result["graph"] = {"lambda": ib.rational_text(rate), "K_lo": ib.export_matrix(K.lower),
                                "K_hi": ib.export_matrix(K.upper), "P_lower": ib.export_matrix(P), "blocks": [],
                                "instantaneous_coefficient_lower": ib.rational_text(ib.instantaneous_coefficient(K)),
                                "clock": "tau = n_coll * (1e-11 cm^3/s) * t; density unbound"}
        self.check("source", "pinned_native_source_shape", K.n == 9 and len(exported["pair_ratios"]) == 9)
        self.check("source", "positive_literal_thermal_intervals", all(0 < p.lo <= p.hi < 1 for p in thermal["pi"]))
        self.check("source", "normalized_literal_box_contains_unit_mass", sum(p.lo for p in thermal["pi"]) <= 1 <= sum(p.hi for p in thermal["pi"]))
        self.check("source", "strict_thermal_precision_width", max(p.width for p in thermal["pi"]) < Fraction(1, 10**60),
                   {"max_pi_width": max(p.width for p in thermal["pi"])})
        self.check("source", "instantaneous_lower_gap_is_zero", ib.instantaneous_coefficient(K) == 0)
        self.check("source", "P_lower_nonnegative_substochastic", all(x >= 0 for row in P for x in row)
                   and all(sum(P[i][j] for i in range(K.n)) <= 1 for j in range(K.n)))
        block_specs = configuration["source_blocks"]
        if not 1 <= len(block_specs) <= 8:
            raise ib.DomainError("Source block case limit exceeded")
        for spec in block_specs:
            mu, degree = ib.Q(spec["mu"]), spec["N"]
            cert = ib.finite_block(K, mu / rate, degree, configuration["polynomial_bits"], rate,
                                   identifier="native_mu_" + ib.rational_text(mu))
            self.result["graph"]["blocks"].append(cert)
            betas = [ib.Q(x["beta_lower"]) for x in cert["partial_overlap_trace"]]
            self.check("source_blocks", cert["id"] + "_overlap_monotonicity", all(a <= b for a, b in zip(betas, betas[1:])))
            self.check("source_blocks", cert["id"] + "_finite_block_contraction", 0 < ib.Q(cert["beta_lower"]) <= 1,
                       {"H": cert["H"], "beta_lower": cert["beta_lower"], "rho_upper": cert["rho_upper"],
                        "instantaneous_gap_inference": False})
        self.result["source_case_count"] = len(block_specs)

    def forced(self, specification):
        K = ib.exact_generator(specification["K"])
        pi = tuple(ib.Q(v) for v in specification["pi"])
        v = tuple(ib.Q(a) for a in specification["v"])
        f = tuple(ib.Q(a) for a in specification["f"])
        x0 = tuple(ib.Q(a) for a in specification["x0"])
        if len(x0) != K.n or any(a < 0 for a in x0):
            raise ib.DomainError("Invalid synthetic positive initial state")
        kappa = ib.Q(specification["kappa"])
        A = ib.reset_generator_bounds(K, [ib.Interval(p, p) for p in pi], [ib.Interval(a, a) for a in v], kappa)
        H, steps = ib.Q(specification["H"]), specification["steps"]
        if type(steps) is not int or not 1 <= steps <= 16:
            raise ib.DomainError("Synthetic fixture step allowance exceeded")
        cert = ib.finite_block(A, H, specification["N"], 256, identifier=specification["id"] + "_full_A")
        coeff = ib.constant_coefficients(K.lower, pi, v, f)
        X0, xbar0 = sum(x0), ib.Q(specification["Xbar0"])
        state = {"M": X0, "U": sum(abs(x0[i] - pi[i] * X0) for i in range(K.n)), "E": abs(X0 - xbar0)}
        endpoints, whole, forcing = [state], [], []
        rho = ib.Q(cert["rho_upper"])
        for _ in range(steps):
            value = ib.forced_step(state, coeff, H, rho, kappa)
            whole.append(value["whole_block"]); forcing.append(value["forcing_bound"])
            state = value["endpoint"]; endpoints.append(state)
        control = dict(specification, certificate=cert, coefficients=export_tree(coeff),
                       endpoints=export_tree(endpoints), whole_blocks=export_tree(whole),
                       forcing_bounds=export_tree(forcing), scope="declared_synthetic_mathematical_fixture")
        self.result["forced_controls"].append(control)
        self.check("forced", specification["id"] + "_nonnegative_envelopes",
                   all(a >= 0 for state in endpoints + whole for a in state.values()))
        self.check("forced", specification["id"] + "_endpoint_and_whole_separate",
                   all(endpoints[k + 1][name] <= whole[k][name] and endpoints[k][name] <= whole[k][name]
                       for k in range(steps) for name in ("M", "U", "E")))
        n = K.n
        L = [[K.lower[i][j] + pi[i] * v[j] - (v[j] if i == j else 0) for j in range(n)] for i in range(n)]
        split = [[L[i][j] - A.lower[i][j] + (kappa if i == j else 0) for j in range(n)] for i in range(n)]
        self.check("forced", specification["id"] + "_exact_common_killing_on_zero_sum",
                   all(split[i][j] == split[i][-1] for i in range(n) for j in range(n - 1)))
        if specification.get("require_noncommuting"):
            B = [[L[i][j] - K.lower[i][j] for j in range(n)] for i in range(n)]
            comm = [[sum(K.lower[i][k] * B[k][j] - B[i][k] * K.lower[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
            self.check("forced", specification["id"] + "_noncommuting_reset_is_exercised", any(x for row in comm for x in row))
        for scale in (Fraction(1, 1000), Fraction(1000)):
            baseline = ib.forced_step(endpoints[0], coeff, H, rho, kappa)
            transformed = ib.forced_step(endpoints[0], {key: value * scale for key, value in coeff.items()}, H / scale, rho, kappa * scale)
            self.check("clock_covariance", specification["id"] + "_scale_" + ib.rational_text(scale),
                       baseline["endpoint"] == transformed["endpoint"] and baseline["whole_block"] == transformed["whole_block"])
        if specification["id"] == "zero_killing_forced":
            invalid = dict(coeff, b_lower=-1)
            self.rejects("reject_negative_forcing_comparison_coefficient", lambda: ib.forced_step(endpoints[0], invalid, H, rho, kappa))
            self.rejects("reject_rho_above_one", lambda: ib.forced_step(endpoints[0], coeff, H, "11/10", kappa))

    def switched(self, specification):
        durations = [ib.Q(piece["duration"]) for piece in specification["segments"]]
        if not durations or any(dt <= 0 for dt in durations):
            raise ib.DomainError("Each chronological switched segment must have positive duration")
        generators = [ib.exact_generator(piece["A"]) for piece in specification["segments"]]
        n = generators[0].n
        if any(g.n != n for g in generators):
            raise ib.DomainError("Switched generator dimensions disagree")
        lower = [[0 if i == j else min(g.lower[i][j] for g in generators) for j in range(n)] for i in range(n)]
        upper = [[0 if i == j else max(g.upper[i][j] for g in generators) for j in range(n)] for i in range(n)]
        family = ib.generator_from_offdiagonal(lower, upper)
        H = sum(durations)
        cert = ib.finite_block(family, H, specification["N"], 256, identifier=specification["id"])
        P, rate = ib.matrix(cert["P_lower"]), ib.Q(cert["lambda"])
        self.check("switched", "common_P_lower_dominated_by_each_generator",
                   all(P[i][j] <= (Fraction(i == j) + g.lower[i][j] / rate)
                       for g in generators for i in range(n) for j in range(n)))
        self.check("switched", "positive_common_family_overlap", ib.Q(cert["beta_lower"]) > 0)
        self.result["switched_graphs"].append(dict(specification, certificate=cert,
                                                   scope="synthetic_piecewise_constant_control"))

    def run(self, configuration, base):
        if configuration["schema"] != "WU_R6_PRIMARY_INPUT_V1":
            raise ib.DomainError("Unexpected primary input schema")
        self.primitives()
        bad_scale = dict(configuration, source=dict(configuration["source"], rate_unit_cm3_s="1e-10"))
        self.rejects("reject_mismatched_native_clock_scale", lambda: self.source(bad_scale, base))
        self.source(configuration, base)
        fixtures = configuration["forced_controls"]
        if len(fixtures) != 3 or sum(x["steps"] for x in fixtures) > 64:
            raise ib.DomainError("Forced fixture count/step budget mismatch")
        for fixture in fixtures:
            self.forced(fixture)
        switched = configuration["switched_graphs"]
        if len(switched) != 1:
            raise ib.DomainError("Exactly one fixed switched control is contracted")
        bad_segments = [dict(piece) for piece in switched[0]["segments"]]
        bad_segments[0]["duration"] = "-1/4"
        bad_segments[1]["duration"] = "3/4"
        self.rejects("reject_negative_segment_with_positive_total_time",
                     lambda: self.switched(dict(switched[0], segments=bad_segments)))
        self.switched(switched[0])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    input_path, output_path = Path(args.input).resolve(), Path(args.output).resolve()
    if output_path.exists():
        raise FileExistsError("Create-only output already exists; unchanged science must not be replayed")
    start_cpu, start_wall = time.process_time(), time.monotonic()
    result = {"schema": "WU_R6_PRIMARY_RESULT_V1", "run_id": "WU_R6_PRIMARY_01",
              "started_utc": datetime.now(timezone.utc).isoformat(), "status": "STARTED", "cases": [],
              "forced_controls": [], "switched_graphs": [],
              "versions": {"python": sys.version.split()[0], "production_core": ib.VERSION},
              "scope": {"new_R6_primary_runs_consumed": 1, "old_science_replay": 0, "physical_IVP": 0,
                        "new_Q": 0, "PHYS91_remaining": [0, 0, 0], "global_remaining": None,
                        "source_clock_density": "UNBOUND", "destruction_physics": "UNBOUND"},
              "budget": {"CPU_limit_s": 60, "internal_interrupt_s": 58,
                         "max_n": 9, "max_N": 512, "max_bits": 768, "max_mu": 256}}

    def timeout(signum, frame):
        raise BudgetExceeded("58 CPU second internal interrupt")

    old_handler = signal.signal(signal.SIGPROF, timeout)
    signal.setitimer(signal.ITIMER_PROF, 58)
    code = 0
    try:
        raw = input_path.read_bytes()
        result["input_sha256"] = hashlib.sha256(raw).hexdigest()
        result["core_sha256"] = hashlib.sha256(Path(ib.__file__).read_bytes()).hexdigest()
        result["runner_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        Primary(result).run(json.loads(raw), input_path.parent)
        failures = sum(row["status"] != "PASS" for row in result["cases"])
        result["status"] = "PASS_SCOPED_EXACT_CERTIFICATES" if failures == 0 else "PRIMARY_CHECK_FAILURE"
        code = int(failures > 0)
    except BudgetExceeded as error:
        result["status"], result["error"] = "CPU_BUDGET_INTERRUPTED", str(error)
        code = 3
    except Exception as error:
        result["status"], result["error"] = "EXECUTION_ERROR", str(error)
        result["traceback"] = traceback.format_exc(limit=12)
        code = 2
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0)
        signal.signal(signal.SIGPROF, old_handler)
        result["finished_utc"] = datetime.now(timezone.utc).isoformat()
        result["actual_cpu_seconds_at_finalize"] = time.process_time() - start_cpu
        result["actual_process_cpu_seconds_at_finalize"] = time.process_time()
        result["actual_wall_seconds_at_finalize"] = time.monotonic() - start_wall
        result["CPU_allowance_satisfied_at_finalize"] = result["actual_process_cpu_seconds_at_finalize"] <= 60
        result["case_count"] = len(result["cases"])
        result["failure_count"] = sum(row["status"] != "PASS" for row in result["cases"])
        groups = {}
        for row in result["cases"]:
            group = groups.setdefault(row["group"], {"checks": 0, "passed": 0, "failed": 0})
            group["checks"] += 1; group["passed" if row["status"] == "PASS" else "failed"] += 1
        result["groups"] = groups
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("x", encoding="utf-8") as handle:
            json.dump(export_tree(result), handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
        print(json.dumps({"status": result["status"], "case_count": result["case_count"],
                          "failure_count": result["failure_count"],
                          "actual_cpu_seconds_at_finalize": result["actual_cpu_seconds_at_finalize"],
                          "output": str(output_path)}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
