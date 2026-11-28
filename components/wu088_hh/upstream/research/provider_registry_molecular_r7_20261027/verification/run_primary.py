#!/usr/bin/env python3
"""One fixed, bounded R7 primary run. This file does not run on import.

The parent executes this once after publishing the contract. It reads only the
frozen R7 input and retained evidence, never imports an earlier scientific core,
and creates one result file without overwriting an existing result.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import resource
import sys
import time
import traceback


LEAF = Path(__file__).resolve().parents[1]
FIXED_INPUT_SHA256 = "3ff9c2535e5c0ce6ffa5e9671de15aad6649e0996cd9b9e275cc290facd8d330"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def set_cpu_limit():
    old_soft, old_hard = resource.getrlimit(resource.RLIMIT_CPU)
    allowed = min([60] + [v for v in (old_soft, old_hard) if v != resource.RLIM_INFINITY])
    resource.setrlimit(resource.RLIMIT_CPU, (allowed, allowed))
    return allowed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=LEAF / "verification/PRIMARY_INPUT.json")
    parser.add_argument("--output", type=Path, default=LEAF / "raw/PRIMARY_RESULTS.json")
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error("Output already exists; no replay or overwrite is permitted")
    input_hash = sha256(args.input)
    if input_hash != FIXED_INPUT_SHA256:
        parser.error("Input differs from the frozen one-run fixture contract")
    inputs = json.loads(args.input.read_text())
    if (inputs.get("primary_runs") != 1 or inputs.get("CPU_limit_s") != 60
            or inputs.get("old_science_replay") != 0 or inputs.get("physical_IVP") != 0):
        parser.error("Input execution scope differs from the R7 contract")

    cpu_limit = set_cpu_limit()
    started, cpu0, wall0 = utc_now(), time.process_time(), time.perf_counter()
    sys.path.insert(0, str(LEAF / "src"))
    import nonlinear_feedback as core

    Q = core.Q
    checks = []

    def check(name, condition, evidence=None):
        checks.append({"name": name, "status": "PASS" if bool(condition) else "FAIL",
                       "evidence": evidence if evidence is not None else {}})

    def expect_domain(name, operation):
        try:
            operation()
        except core.DomainError as exc:
            check(name, True, {"guard": str(exc)})
        except Exception as exc:
            check(name, False, {"wrong_exception": type(exc).__name__, "message": str(exc)})
        else:
            check(name, False, {"guard": "invalid input was accepted"})

    def vector(values):
        return tuple(Q(v) for v in values)

    def matrix(values):
        return tuple(vector(row) for row in values)

    def matvec(A, x):
        return tuple(sum(a * b for a, b in zip(row, x)) for row in A)

    def nonnegative(values):
        return all(x >= 0 for x in values)

    def make_binding(case, *, synthetic=False):
        return {"certificate_id": case.get("certificate_id", "declared_mathematical_" + case["id"]),
                "H": case["H"], "rho": case["rho"],
                "clock": (case.get("scope", "dimensionless mathematical control") if synthetic
                          else inputs["metadata_defaults"]["clock"]),
                "norm": "l1_on_kerP", "generator_scope": "nominal_K",
                "feedback_accounted": True}

    def queries(B, g, H, w0, case):
        result = []
        for fraction in case["query_fractions"]:
            u = H * Q(fraction)
            if not 0 <= u <= H:
                raise core.DomainError("A fixed query lies outside the certified block")
            answer = core.interior_feedback_upper(
                B, g, u, w0, degree=case["degree"],
                coordinate_scales=case["coordinate_scales"])
            result.append({"t": u, "bound": answer["w_upper"],
                           "W_upper": answer["W_upper"], "q": answer["q"],
                           "tail_certificate": answer["tail_certificate"]})
        return result

    result = {"schema": "WU_R7_NONLINEAR_FEEDBACK_PRIMARY_V1", "started_utc": started,
              "unit": inputs["unit"], "input_sha256": input_hash,
              "core_sha256": sha256(LEAF / "src/nonlinear_feedback.py"),
              "runner_sha256": sha256(__file__),
              "source_hashes": {
                  "contract": sha256(LEAF / "CONTRACT.json"),
                  "proof": sha256(LEAF / "theory/NONLINEAR_FEEDBACK_PROOF_KO.md"),
                  "theory_code_map": sha256(LEAF / "theory/THEORY_CODE_MAP.json")},
              "versions": {"python": platform.python_version(), "exact_core": "Fraction/directed dyadic integers"},
              "scope": {"new_primary_runs_consumed": 1, "old_science_replay": 0,
                        "physical_IVP": 0, "new_Q": 0,
                        "source_clock_density": "conditional mathematical fixtures; physical binding remains open",
                        "production": "NOT_ISSUED"},
              "budget": {"CPU_limit_s": cpu_limit, "fixed_affine_cases": 5,
                         "fixed_hd_cases": 4, "blocks_per_hd_case": 3,
                         "queries_per_block": 5, "Taylor_degree": 48,
                         "dyadic_bits": 256},
              "affine_cases": [], "hd_cases": [], "checks": checks}

    try:
        check("fixed_case_counts", len(inputs["affine_cases"]) == 5 and len(inputs["hd_cases"]) == 4)
        all_ids = [case["id"] for key in ("affine_cases", "hd_cases") for case in inputs[key]]
        check("unique_case_identities", len(all_ids) == len(set(all_ids)))

        for case in inputs["affine_cases"]:
            name = "affine/" + case["id"]
            try:
                B, g, H, rho, w0 = (matrix(case["B"]), vector(case["g"]), Q(case["H"]),
                                      Q(case["rho"]), vector(case["w0"]))
                cert = core.block_feedback_upper(
                    B, g, H, rho, w0, degree=case["degree"],
                    coordinate_scales=case["coordinate_scales"],
                    binding=make_binding(case, synthetic=True))
                sample = queries(B, g, H, w0, case)
                out = deepcopy(case)
                out.update({"certificate": cert, "queries": sample})
                result["affine_cases"].append(out)
                check(name + "/T_nonnegative", all(nonnegative(row) for row in cert["T"]))
                check(name + "/forcing_nonnegative", nonnegative(cert["q"]))
                check(name + "/initial_query_exact", sample[0]["t"] == 0 and sample[0]["bound"] == w0)
                check(name + "/uniform_includes_initial", all(a >= b for a, b in zip(cert["whole_block_upper"], w0)))
                check(name + "/endpoint_affine_recurrence",
                      cert["w_next_upper"] == tuple(a + b for a, b in zip(matvec(cert["T"], w0), cert["q"])))
                if case["id"] in ("zero", "constant_forcing"):
                    expected_W = ((Q(1), Q(0)), (Q(0), Q(1)))
                    expected_q = tuple(H * value for value in g)
                    expected_end = (rho * w0[0] + expected_q[0], w0[1] + expected_q[1])
                    check(name + "/exact_zero_matrix", cert["W_upper"] == expected_W and
                          cert["q"] == expected_q and cert["w_next_upper"] == expected_end,
                          {"expected_endpoint": expected_end})
                if case["id"] == "nilpotent":
                    expected_W = ((Q(1), 2 * H), (Q(0), Q(1)))
                    expected_q = (3 * H + 5 * H * H, 5 * H)
                    check(name + "/exact_singular_polynomial", cert["W_upper"] == expected_W
                          and cert["q"] == expected_q, {"expected_q": expected_q})
                if case["id"] == "damped_diagonal":
                    check(name + "/whole_block_not_endpoint_substitute",
                          cert["whole_block_upper"][1] >= w0[1] > cert["w_next_upper"][1])
            except Exception as exc:
                check(name + "/exception", False, {"type": type(exc).__name__, "message": str(exc),
                                                    "traceback": traceback.format_exc()})

        defaults = inputs["metadata_defaults"]
        hd_contexts = []
        for case in inputs["hd_cases"]:
            name = "hd/" + case["id"]
            try:
                p, alpha, d = vector(case["pi"]), vector(case["alpha"]), vector(case["destruction"])
                K, kf, offset = matrix(case["K"]), Q(case["kf"]), Q(case["coarse_kf_offset"])
                fine, coarse = vector(case["initial_fine"]), vector(case["initial_coarse"])
                H, rho = Q(case["H"]), Q(case["rho"])
                initial = core.hd_scalar_error(fine, coarse, p)
                metadata = {"state_ids": ["HD_state_" + str(i) for i in range(len(p))],
                            "source_variant_selection": case.get("formation_variant", defaults["formation_variant"]),
                            "source_map_identity": case["source_map_identity"],
                            "positive_box_evidence": case["positive_box_evidence"],
                            "initial_invariant_compatibility": True,
                            "clock": defaults["clock"], "time_unit": defaults["time_unit"],
                            "density_unit": defaults["density_unit"],
                            "nominal_generator_certificate_identity": case["certificate_id"],
                            "nominal_generator_block_H": H,
                            "common_pool_binding": defaults["common_pool_binding"],
                            "nominal_generator_scope": case["nominal_generator_scope"],
                            "source_scope": case["source_scope"]}
                net = core.hd_network(alpha, kf, d, formation_variant=metadata["source_variant_selection"],
                                      source_scope=case["source_scope"])
                q_actual = core.hd_lift_defect_norm(K, p, (Q(0),) * len(p))
                theta_actual = sum(abs(a - b) for a, b in zip(alpha, p))
                check(name + "/lift_defect_bound", q_actual <= Q(case["q_norm_upper"]),
                      {"actual": q_actual, "supplied": case["q_norm_upper"]})
                check(name + "/branch_distance_bound", theta_actual <= Q(case["branch_distance_upper"]),
                      {"actual": theta_actual, "supplied": case["branch_distance_upper"]})
                check(name + "/initial_scalar_invariant_identity",
                      initial["coarse_error"] == (-initial["eta"], -initial["eta"], initial["eta"], initial["eta"]),
                      initial)

                # The complete nonnegative invariant class is a closed line segment.
                Hn, Dn, charge = initial["invariants"]
                A, base_w = (Hn - charge + Dn) / 2, charge - Dn
                Xlo, Xhi = max(Q(0), Dn - charge), min(Dn, A)
                invariant_box = {"u": (A - Xhi, A - Xlo), "v": (Dn - Xhi, Dn - Xlo),
                                 "w": (base_w + Xlo, base_w + Xhi), "X": (Xlo, Xhi)}
                box_ok = Xlo <= Xhi and all(
                    Q(case["density_box"][key][0]) <= lo <= hi <= Q(case["density_box"][key][1])
                    for key, (lo, hi) in invariant_box.items())
                check(name + "/whole_trajectory_invariant_box", box_ok, invariant_box)
                check(name + "/coarse_source_defect_bound",
                      abs(offset) * Q(case["density_box"]["u"][1]) * Q(case["density_box"]["v"][1])
                      <= Q(case["coarse_scalar_defect_upper"]) and kf + offset >= 0)
                if not box_ok or q_actual > Q(case["q_norm_upper"]) or theta_actual > Q(case["branch_distance_upper"]):
                    raise core.DomainError("A required fixture coefficient bound is not valid")
                coefficients = core.hd_feedback_coefficients(
                    case["density_box"], kf, d, p, q_norm_upper=case["q_norm_upper"],
                    branch_distance_upper=case["branch_distance_upper"],
                    coarse_scalar_defect_upper=case["coarse_scalar_defect_upper"], metadata=metadata)
                B, g = coefficients["B"], coefficients["g"]

                W = ((2, 0, 1) + (1,) * len(p), (0, 1, 0) + (1,) * len(p),
                     (0, 1, 1) + (0,) * len(p))
                check(name + "/exact_H_D_charge_stoichiometry",
                      all(sum(a * b for a, b in zip(row, event.column)) == 0
                          for row in W for event in net.events))
                flow = kf * fine[0] * fine[1] - fine[2] * sum(di * xi for di, xi in zip(d, fine[3:]))
                reaction_expected = (-flow, -flow, flow) + tuple(
                    kf * ai * fine[0] * fine[1] - fine[2] * di * xi
                    for ai, di, xi in zip(alpha, d, fine[3:]))
                check(name + "/event_rhs_exact_channel_formula", net.rhs(fine) == reaction_expected)
                fine_rhs = core.hd_rhs(fine, K, alpha, kf, d,
                                       formation_variant=metadata["source_variant_selection"],
                                       source_scope=case["source_scope"])
                coarse_rhs = core.hd_coarse_rhs(coarse, p, kf + offset, d)
                coarse_W = ((2, 0, 1, 1), (0, 1, 0, 1), (0, 1, 1, 0))
                check(name + "/fine_rhs_invariants", all(v == 0 for v in matvec(W, fine_rhs)))
                check(name + "/coarse_rhs_invariants", all(v == 0 for v in matvec(coarse_W, coarse_rhs)))
                face_values = []
                for i in range(len(fine)):
                    face = list(fine)
                    face[i] = Q(0)
                    face_values.append(core.hd_rhs(
                        face, K, alpha, kf, d, formation_variant=metadata["source_variant_selection"],
                        source_scope=case["source_scope"])[i])
                check(name + "/nonnegative_boundary_derivatives", nonnegative(face_values))

                if "reuse" in case:
                    reuse = case["reuse"]
                    retained_path = (LEAF / reuse["path"]).resolve()
                    retained_hash = sha256(retained_path)
                    retained = json.loads(retained_path.read_text())
                    block = next(v for v in retained["graph"]["blocks"] if v["id"] == reuse["graph_block_id"])
                    low, high = matrix(retained["graph"]["K_lo"]), matrix(retained["graph"]["K_hi"])
                    check(name + "/retained_result_hash", retained_hash == reuse["sha256"], {"sha256": retained_hash})
                    check(name + "/retained_H_rho_literal_binding",
                          H == Q(block["H"]) and rho == Q(block["rho_upper"]))
                    check(name + "/K_inside_retained_box",
                          all(low[i][j] <= K[i][j] <= high[i][j] for i in range(len(p)) for j in range(len(p))))
                    check(name + "/retained_source_hash_binding", retained["thermal"]["source_sha256"] == reuse["source_sha256"])
                    result["source_hashes"]["retained_R6_primary"] = retained_hash
                    result["source_hashes"]["native_source_declared_and_retained"] = reuse["source_sha256"]
                else:
                    analytic = core.exp_neg_enclosure(2 * H, degree=case["degree"])
                    check(name + "/analytic_two_state_nominal_rho", analytic.hi <= rho,
                          {"exp_minus_2H": (analytic.lo, analytic.hi), "rho": rho})

                out = deepcopy(case)
                out["requested_blocks"] = out.pop("blocks")
                out.update({"coefficients": coefficients, "initial_error": initial,
                            "invariant_box": invariant_box, "binding": make_binding(case),
                            "blocks": []})
                w0 = (initial["R"], initial["E"])
                if out["requested_blocks"] != 3:
                    raise core.DomainError("Fixed fixture requires exactly three blocks")
                for block_index in range(out["requested_blocks"]):
                    cert = core.block_feedback_upper(B, g, H, rho, w0, degree=case["degree"],
                                                      coordinate_scales=case["coordinate_scales"],
                                                      binding=make_binding(case))
                    sample = queries(B, g, H, w0, case)
                    out["blocks"].append({"index": block_index, "t0": block_index * H,
                                          "w0": w0, "certificate": cert, "queries": sample})
                    check(name + f"/block_{block_index}/positive_T_and_q",
                          all(nonnegative(row) for row in cert["T"]) and nonnegative(cert["q"]))
                    check(name + f"/block_{block_index}/initial_query", sample[0]["bound"] == w0)
                    check(name + f"/block_{block_index}/whole_includes_initial",
                          all(a >= b for a, b in zip(cert["whole_block_upper"], w0)))
                    w0 = cert["w_next_upper"]
                result["hd_cases"].append(out)
                hd_contexts.append((case, metadata, coefficients))
            except Exception as exc:
                check(name + "/exception", False, {"type": type(exc).__name__, "message": str(exc),
                                                    "traceback": traceback.format_exc()})

        zero_jac = core.mass_action_jacobian_upper(
            ((0, 0), (1, 0), (0, 1), (1, 1), (2, 0)), (2, 3, 5, 7, 11), (0, 0))
        check("jacobian/zero_density_and_zero_exponents",
              zero_jac == ((0, 0), (3, 0), (0, 5), (0, 0), (0, 0)), {"Jacobian_upper": zero_jac})
        high_jac = core.mass_action_jacobian_upper(((1, 1), (2, 0)), (7, 11), (2, 3))
        check("jacobian/explicit_bilinear_and_quadratic", high_jac == ((21, 14), (44, 0)))

        if hd_contexts:
            case, metadata, base = next(x for x in hd_contexts if x[0]["id"] == "two_state_nonlinear")
            expanded_box = {key: (0, Q(bounds[1]) + 1) for key, bounds in case["density_box"].items()}
            expanded = core.hd_feedback_coefficients(
                expanded_box, (0, "1/100"), ((0, "1/100"), (0, "1/100")),
                (("1/4", "3/4"), ("1/4", "3/4")), q_norm_upper="1/1000",
                branch_distance_upper=2, coarse_scalar_defect_upper="1/1000", metadata=metadata)
            check("coefficients/outward_interval_direction",
                  all(expanded[key] >= base[key] for key in ("a", "b", "c", "d", "g_r", "g_e")),
                  {"base_B": base["B"], "expanded_B": expanded["B"],
                   "base_g": base["g"], "expanded_g": expanded["g"]})

            def coefficient_call(**overrides):
                arguments = {"density_box": case["density_box"], "kf": case["kf"],
                             "destruction": case["destruction"], "pi": case["pi"],
                             "q_norm_upper": case["q_norm_upper"],
                             "branch_distance_upper": case["branch_distance_upper"],
                             "coarse_scalar_defect_upper": case["coarse_scalar_defect_upper"],
                             "metadata": metadata}
                arguments.update(overrides)
                return core.hd_feedback_coefficients(**arguments)

            expect_domain("guard/inverted_box", lambda: coefficient_call(
                density_box={**case["density_box"], "u": (2, 1)}))
            expect_domain("guard/negative_box", lambda: coefficient_call(
                density_box={**case["density_box"], "u": (-1, 1)}))
            expect_domain("guard/simplex_box_lower_sum", lambda: coefficient_call(
                pi=(("3/4", 1), ("3/4", 1))))
            expect_domain("guard/simplex_box_upper_sum", lambda: coefficient_call(
                pi=((0, "1/4"), (0, "1/4"))))
            expect_domain("guard/invariant_compatibility_metadata", lambda: coefficient_call(
                metadata={**metadata, "initial_invariant_compatibility": False}))
            expect_domain("guard/branch_bound_over_two", lambda: coefficient_call(branch_distance_upper=3))
            expect_domain("guard/missing_lift_defect_bound", lambda: coefficient_call(q_norm_upper=None))
            expect_domain("guard/negative_destruction", lambda: coefficient_call(destruction=(-1, 0)))
            expect_domain("guard/incompatible_initial_invariants", lambda: core.hd_scalar_error(
                case["initial_fine"], (2, 1, 1, "1/2"), case["pi"]))

        expect_domain("guard/binary_float", lambda: core.Q(0.5))
        expect_domain("guard/nonintegral_reaction_exponent", lambda: core.mass_action_jacobian_upper(((Q("1/2"),),), (1,), (1,)))
        expect_domain("guard/negative_density_rhs", lambda: core.hd_network(
            ("1/2", "1/2"), 1, (1, 1), formation_variant="SYNTHETIC", source_scope="guard").rhs((-1, 1, 1, 1, 1)))
        expect_domain("guard/alternative_models_not_additive", lambda: core.hd_network(
            ("1/2", "1/2"), 1, (1, 1), formation_variant="TIQM+SQM", source_scope="guard"))
        expect_domain("guard/branch_not_normalized", lambda: core.hd_network(
            (1, 1), 1, (1, 1), formation_variant="SYNTHETIC", source_scope="guard"))
        expect_domain("guard/invariant_column_mismatch", lambda: core.ReactionNetwork(
            ("A",), (core.Event("birth", (0,), (1,), 1),), ((1,),)))
        guard_case = inputs["affine_cases"][0]
        binding = make_binding(guard_case, synthetic=True)
        arguments = {"B": ((0, 0), (0, 0)), "g": (0, 0), "H": 1, "rho": "1/3", "w0": (1, 1),
                     "degree": 48, "binding": binding}

        def block_call(**overrides):
            args2 = dict(arguments)
            args2.update(overrides)
            return core.block_feedback_upper(**args2)

        expect_domain("guard/nonpositive_H", lambda: block_call(H=0))
        expect_domain("guard/rho_outside_unit_interval", lambda: block_call(rho=2))
        expect_domain("guard/negative_comparison_offdiagonal", lambda: block_call(B=((0, -1), (0, 0))))
        expect_domain("guard/mismatched_certificate_H", lambda: block_call(H=2))
        expect_domain("guard/full_generator_substitution", lambda: block_call(
            binding={**binding, "generator_scope": "full_reactive_L"}))
        expect_domain("guard/missing_feedback_accounting", lambda: block_call(
            binding={**binding, "feedback_accounted": False}))
        expect_domain("guard/finite_rounded_norm", lambda: block_call(B=((17, 0), (0, 0))))
        expect_domain("guard/degree_finite_cap", lambda: block_call(degree=257))
        expect_domain("guard/negative_forcing", lambda: block_call(g=(-1, 0)))

        # Fixed late forcing: R'=-R+4 on [3/4,1], R(0)=0, total input one.
        exp_H = core.exp_neg_enclosure(1, degree=48)
        exp_epsilon = core.exp_neg_enclosure("1/4", degree=48)
        correct = (4 * (1 - exp_epsilon.hi), 4 * (1 - exp_epsilon.lo))
        wrong_upper = exp_H.hi
        result["late_forcing"] = {"gamma": Q(1), "H": Q(1), "epsilon": Q("1/4"), "J": Q(1),
                                  "rho_interval": (exp_H.lo, exp_H.hi), "rho": exp_H.hi,
                                  "correct_forcing_interval": correct,
                                  "correct_forcing_upper": correct[1], "wrong_forcing_upper": wrong_upper,
                                  "strict_gap_lower": correct[0] - wrong_upper,
                                  "scope": "fixed analytic causality control; total forcing is not contracted by full-block rho"}
        check("late_forcing/strict_counterexample_to_rho_times_all_input", correct[0] > wrong_upper,
              result["late_forcing"])
        check("all_fixed_cases_persisted", len(result["affine_cases"]) == 5 and len(result["hd_cases"]) == 4)
    except Exception as exc:
        check("unhandled_primary_exception", False, {"type": type(exc).__name__, "message": str(exc),
                                                    "traceback": traceback.format_exc()})

    result["finished_utc"] = utc_now()
    # process_time() is cumulative process CPU, including interpreter startup,
    # this runner's imports and the production import. RLIMIT_CPU uses the same
    # process-wide budget; the smaller run-local measurement is only metadata.
    result["actual_process_cpu_seconds_at_finalize"] = time.process_time()
    result["actual_run_cpu_seconds_at_finalize"] = time.process_time() - cpu0
    result["actual_wall_seconds_at_finalize"] = time.perf_counter() - wall0
    result["CPU_allowance_satisfied_at_finalize"] = result["actual_process_cpu_seconds_at_finalize"] <= cpu_limit
    check("CPU_allowance", result["CPU_allowance_satisfied_at_finalize"])
    result["failure_count"] = sum(item["status"] != "PASS" for item in checks)
    result["check_count"] = len(checks)
    result["status"] = "PASS" if result["failure_count"] == 0 else "FAIL"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(core.export(result), handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"output": str(args.output), "status": result["status"],
                      "checks": len(checks), "failures": result["failure_count"],
                      "CPU_seconds": result["actual_process_cpu_seconds_at_finalize"],
                      "wall_seconds": result["actual_wall_seconds_at_finalize"]}, sort_keys=True))
    return 0 if result["failure_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
