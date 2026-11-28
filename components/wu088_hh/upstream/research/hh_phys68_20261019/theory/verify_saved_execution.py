"""Read-only, exact-rational audit of PHYS68's saved execution evidence.

This independent verifier imports no WU088_HH or Arb/FLINT code. It hashes
stored bytes and checks finite integer/rational identities and inclusions.
It never evaluates a Coulomb function, constructs a Taylor kernel, or runs
a numerical integral. Its only write is the requested review JSON.
"""

from __future__ import annotations

from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json


REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RUN = REPO / "research/hh_phys68_20261019/profiles/run_l28_t65_completed"
OLD = REPO / "research/hh_phys68_20261019/profiles/run_l28_t65"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dyadic(record):
    m, e = int(record["mantissa"]), int(record["exponent2"])
    return Q(m << e) if e >= 0 else Q(m, 1 << -e)


def ball(record):
    midpoint, radius = dyadic(record["midpoint"]), dyadic(record["radius"])
    assert radius >= 0, "negative radius"
    return midpoint - radius, midpoint + radius


def box(record):
    return {k: ball(record[k]) for k in ("real", "imag")}


def contains(outer, inner):
    return all(outer[k][0] <= inner[k][0] and outer[k][1] >= inner[k][1]
               for k in ("real", "imag"))


def plus(a, b):
    return {k: (a[k][0] + b[k][0], a[k][1] + b[k][1]) for k in ("real", "imag")}


def rational(record):
    if record.get("type") == "rational-hex-v1":
        return Q(int(record["numerator_hex"], 16), int(record["denominator_hex"], 16))
    return Q(int(record["numerator"]), int(record["denominator"]))


def norm_radius(record):
    return sum(dyadic(record[k]["radius"]) for k in ("real", "imag"))


def rq(value):
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def main():
    request = json.loads((RUN / "REQUEST.json").read_text())
    cert = json.loads((RUN / "CERTIFICATE.json").read_text())
    adoption = json.loads((RUN / "ADOPTION_RECEIPT.json").read_text())
    previous_request = json.loads((OLD / "REQUEST.json").read_text())
    binding = request["binding"]
    fp = hashlib.sha256(canonical(binding)).hexdigest()
    assert fp == request["fingerprint"] == cert["fingerprint"] == adoption["new_fingerprint"]
    spec = binding["request"]
    assert spec == cert["request"] == previous_request["binding"]["request"]
    assert spec == {"coefficient_bits": 1024, "d1_absolute_goal": "1e-45",
                    "d2_absolute_goal": "1e-62", "degree": 80, "ell": 21,
                    "ellprime": 20, "half_width": "1/4", "majorant_radius": "2",
                    "max_ell": 28, "outer": "65", "precision_bits": 384,
                    "zero_free_radius": "1/2"}
    for name, sha in binding["engine"]["files_sha256"].items():
        assert digest(REPO / "src/wu088_hh" / name) == sha, name
    expected_source = "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
    assert binding["source_sha256"] == cert["source_sha256"] == expected_source
    assert cert["HH_R10"] == request["HH_R10"] == adoption["HH_R10"] == "OFF"
    assert cert["PHYS63_qualitative_existence"] == "ESTABLISHED_REUSED"
    assert cert["finite_block_only"] is True and cert["m"] == 0
    assert cert["excluded_angular_bound"] is None
    assert cert["original_driven_xi_certified"] is False

    pairs = sorted({tuple(sorted((e, j))) for e in (21, 20) for j in range(29)})
    pair_names = {f"{a},{b}" for a, b in pairs}
    assert len(pairs) == 57 and cert["pairs"] == [list(p) for p in pairs]
    assert cert["full_intermediate_sum"] == list(range(29))
    assert len(list(RUN.glob("panel_*.json"))) == len(cert["panels"]) == cert["panel_count_required"] == 76
    h, rho, big, outer, degree = Q(1, 4), Q(1, 2), Q(2), Q(65), 80
    zero_ball = {"display": "0", "midpoint": {"exponent2": 0, "mantissa": "0"},
                 "radius": {"exponent2": 0, "mantissa": "0"}}
    zero_complex = {"imag": zero_ball, "real": zero_ball}
    state = {f"{a},{b}": zero_complex for a, b in pairs}
    sum_increments = {k: (Q(0), Q(0)) for k in ("real", "imag")}
    minimum = None
    all_tail_upper = Q(0)
    per_panel = []

    for i, manifest in enumerate(cert["panels"]):
        path = RUN / f"panel_{i:04d}.json"
        saved = json.loads(path.read_text())
        payload = saved["payload"]
        payload_sha = hashlib.sha256(canonical(payload)).hexdigest()
        assert manifest == {"file": path.name, "index": i, "payload_sha256": payload_sha}
        assert saved["index"] == i and saved["fingerprint"] == fp
        assert saved["payload_sha256"] == payload_sha
        assert saved["right_state_sha256"] == hashlib.sha256(canonical(state)).hexdigest()
        center = outer - (2 * i + 1) * h
        assert Q(payload["center"]) == center
        assert Q(payload["left"]) == center - h and Q(payload["right"]) == center + h
        assert Q(payload["half_width"]) == h
        assert payload["request"] == spec and payload["source_sha256"] == expected_source
        assert payload["HH_R10"] == "OFF"
        assert payload["analytic_domain_includes_uncut_K_beyond_terminal_T"] is True
        assert payload["q_profile_reconstruction_requires_same_kernel_fingerprint"] is True
        assert payload["full_intermediate_sum"] == list(range(29))
        assert center - big - Q(7, 10) > 0 and 0 < h < rho < big

        rows = {tuple(r["pair"]): r for r in payload["pairs"]}
        assert len(payload["pairs"]) == 57 and sorted(rows) == pairs
        for p, row in rows.items():
            name = f"{p[0]},{p[1]}"
            assert contains(box(row["q_right"]), box(state[name])), (i, p, "carry")
            assert row["q_coefficient_count"] == degree + 2
            km = ball(row["K_big_disk_majorant"])
            rem = ball(row["K_panel_remainder_upper"])
            assert km[0] > 0 and rem[0] >= km[1] * (h / big) ** (degree + 1) / (1 - h / big)
            assert ball(row["q_small_disk_majorant"])[0] > 0
            box(row["q_center"])
            box(row["q_left"])
            box(row["D1_center"])
        state = {f"{p[0]},{p[1]}": row["q_left"] for p, row in rows.items()}

        zero_free = payload["Coulomb_zero_free_lower"]
        assert set(zero_free) == {str(j) for j in range(29)}
        lowers = {j: ball(zero_free[str(j)])[0] for j in range(29)}
        assert all(x > 0 for x in lowers.values())
        panel_min = min(lowers.values())
        recorded_min = ball(payload["minimum_zero_free_lower"])
        assert 0 < recorded_min[0] <= recorded_min[1] <= panel_min
        minimum = panel_min if minimum is None else min(minimum, panel_min)
        terms = payload["second_Born_terms"]
        assert len(terms) == 29 and [r["j"] for r in terms] == list(range(29))
        term_sum = {k: (Q(0), Q(0)) for k in ("real", "imag")}
        tail_sum = Q(0)
        for term in terms:
            j = term["j"]
            first = rows[tuple(sorted((21, j)))]
            second = rows[tuple(sorted((20, j)))]
            q1 = ball(first["q_small_disk_majorant"])[1]
            q2 = ball(second["q_small_disk_majorant"])[1]
            majorant = ball(term["integrand_majorant"])
            tail = ball(term["integration_tail_upper"])
            assert majorant[0] >= q1 * q2 / lowers[j] ** 2
            assert tail[0] >= 2 * h * majorant[1] * (h / rho) ** (degree + 1) / (1 - h / rho)
            assert all(dyadic(term["integral"][k]["radius"]) >= tail[0] for k in ("real", "imag"))
            term_sum = plus(term_sum, box(term["integral"]))
            tail_sum += tail[1]
        assert ball(payload["integration_Cauchy_tail_sum_upper"])[0] >= tail_sum
        increment = box(payload["second_Born_increment"])
        assert contains(increment, term_sum), (i, "sum over all j")
        sum_increments = plus(sum_increments, increment)
        all_tail_upper += tail_sum
        if i < 2:
            old_saved = json.loads((OLD / path.name).read_text())
            assert canonical(old_saved["payload"]) == canonical(payload)
        per_panel.append({"index": i, "file_sha256": digest(path), "payload_sha256": payload_sha})

    assert center - h == Q(27)
    assert set(cert["D1_B_cutoff"]) == set(cert["D1_B_full_radial_absolute_error_l1"]) == pair_names
    radial = cert["analytic_radial_cutoff"]
    gamma = rational(radial["gamma"])
    a, b, chi = (rational(radial[k]) for k in ("a", "b", "chi"))
    assert gamma == 5929 and a == gamma * Q("3e-23") / 2 and b == gamma / 4 and chi == 4 * a * b
    assert radial["max_ell"] == 28 and rational(radial["outer"]) == 65 and radial["orders"] == 2
    beta1, beta2 = (rational(row["radial_cutoff_bound"]) for row in radial["terms"])
    assert beta2 == beta1 * chi and beta1 > 0
    assert rational(cert["D2_radial_cutoff_error"]) == beta2
    errors = {}
    for name, saved_q in state.items():
        final_q = cert["D1_B_cutoff"][name]
        assert contains(box(final_q), box(saved_q)), (name, "D1 final boundary")
        errors[name] = rational(cert["D1_B_full_radial_absolute_error_l1"][name])
        assert errors[name] == norm_radius(final_q) + beta1
        assert errors[name] <= Q(spec["d1_absolute_goal"])
    assert rational(cert["D1_B_max_full_radial_absolute_error_l1"]) == max(errors.values())
    numerical = cert["D2_B_cutoff"]
    assert contains(box(numerical), sum_increments), "sum over all panels"
    numerror = rational(cert["D2_numerical_absolute_error_l1"])
    totalerror = rational(cert["D2_full_radial_absolute_error_about_cutoff_midpoint"])
    assert numerror == norm_radius(numerical)
    assert numerror >= 2 * all_tail_upper
    assert totalerror == numerror + beta2 <= Q(spec["d2_absolute_goal"])
    inflated = {k: (v[0] - beta2, v[1] + beta2) for k, v in box(numerical).items()}
    assert contains(box(cert["D2_B_full_radial_box"]), inflated)
    assert cert["absolute_goal_met"] == {"D1_B_all_requested_pairs": True, "D2_target": True}
    assert cert["status"] == "CERTIFIED_GOALS_MET" and cert["scientific_execution"] == "COMPLETE"
    assert cert["panels_computed_this_call"] == 74 and cert["panels_reused_this_call"] == 2

    invocations = [json.loads(line) for line in (RUN / "INVOCATIONS.jsonl").read_text().splitlines()]
    old_invocations = [json.loads(line) for line in (OLD / "INVOCATIONS.jsonl").read_text().splitlines()]
    assert len(invocations) == 1
    invocation = invocations[0]
    assert invocation["fingerprint"] == fp and invocation["request"] == spec
    assert invocation["exit_code"] == 0 and invocation["computed"] == 74 and invocation["reused"] == 2
    assert old_invocations[0]["exit_code"] == 0 and old_invocations[0]["computed"] == 2
    assert old_invocations[1]["exit_code"] == 1 and "panel chain/request mismatch: 1" in old_invocations[1]["error"]
    assert adoption["solver_integrations"] == 0 and len(adoption["panels_adopted"]) == 2

    review = {
        "schema": "PHYS68_INDEPENDENT_FINAL_EXECUTION_REVIEW_V1",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "PASS_SCOPED_FINITE_L_SECOND_BORN_CERTIFICATE",
        "review_method": "Only stored JSON/byte hashes and Python standard-library exact Fraction arithmetic; no project imports or solver calls.",
        "verifier_sha256": digest(Path(__file__)),
        "certificate": str((RUN / "CERTIFICATE.json").relative_to(REPO)),
        "certificate_sha256": digest(RUN / "CERTIFICATE.json"),
        "request_sha256": digest(RUN / "REQUEST.json"),
        "fingerprint": fp,
        "engine_files_current_bytes_match_request": True,
        "engine": binding["engine"],
        "original_source_sha256": expected_source,
        "source_hash_scope": "Matches prior actual source guard and run-bound identity; this final audit does not rerun the prior source/campaign validation.",
        "checks": {
            "payload_hashes_and_manifest_entries": 76,
            "raw_predecessor_state_hashes": 76,
            "exact_boundary_endpoint_inequalities": 76 * 57 * 4,
            "distinct_profile_pairs_per_panel": 57,
            "total_profile_pair_records": 76 * 57,
            "intermediate_j_per_panel": 29,
            "strictly_positive_complex_zero_free_lower_bounds": 76 * 29,
            "all_j_term_rectangle_sums_contained_by_panel_increment": 76,
            "all_panel_increment_rectangle_sum_contained_by_final_cutoff_box": True,
            "Cauchy_majorant_to_integrated_tail_inequalities": 76 * 29,
            "kernel_big_disk_to_panel_remainder_inequalities": 76 * 57,
            "terminal_boundary_exact_zero": True,
            "coverage_exact_interval": ["27", "65"],
            "D1_B_all_57_full_radial_goal_checks": 57,
            "D2_total_error_exactly_numerical_plus_beta2": True,
            "both_request_goals_fixed_before_first_two_panels": True,
            "current_first_two_payloads_canonically_identical_to_original": True,
        },
        "minimum_zero_free_lower_exact": rq(minimum),
        "minimum_zero_free_lower_display_only": format(float(minimum), ".17e"),
        "D2_cutoff_midpoint_authority": "Exact dyadic real/imag midpoint in the hashed CERTIFICATE.json; decimal display strings are rounded summaries.",
        "D2_cutoff_midpoint_display": {k: format(float(dyadic(numerical[k]["midpoint"])), ".17e") for k in ("real", "imag")},
        "errors": {
            "D1_B_max_full_radial_l1": rq(max(errors.values())),
            "D1_B_max_full_radial_l1_display_only": format(float(max(errors.values())), ".17e"),
            "D2_numerical_l1": rq(numerror),
            "D2_radial_cutoff_beta2": rq(beta2),
            "D2_total_absolute_about_exact_cutoff_midpoint": rq(totalerror),
            "D2_total_display_only": format(float(totalerror), ".17e"),
            "D1_B_goal": spec["d1_absolute_goal"], "D2_goal": spec["d2_absolute_goal"],
            "Gamma28": str(gamma),
        },
        "execution": {
            "original_successful_panels_computed": 2,
            "bounded_adoption_integrals": 0,
            "completion_panels_reused": invocation["reused"],
            "completion_panels_computed": invocation["computed"],
            "completion_exit_code": invocation["exit_code"],
            "completion_started_utc": invocation["started_utc"],
            "completion_finished_utc": invocation["finished_utc"],
            "completion_elapsed_seconds": invocation["elapsed_seconds"],
            "original_failed_resume_preserved": old_invocations[1],
            "audit_solver_integrals": 0,
        },
        "scope": {
            "finite_L": 28, "m": 0, "second_Born_entry": [21, 20], "B": "27", "T": "65",
            "first_Born_profiles": "57 symmetric pairs for two required external rows, not a separately executed full first-Born matrix",
            "radial_cutoff": "PR115 order-2 bound added exactly; finite-L infinite-radius target only",
            "excluded_angular_certification": False,
            "original_source_driven_xi_certification": False,
            "PHYS63_qualitative_existence": "ESTABLISHED_REUSED",
            "HH_R10": "OFF",
            "NCP_submission_performed_by_audit": False,
            "publication_performed_by_audit": False,
            "backup_performed_by_audit": False,
        },
        "panel_byte_hashes": per_panel,
        "remaining_mathematical_blockers_for_this_scoped_certificate": [],
    }
    output = HERE / "FINAL_EXECUTION_REVIEW.json"
    output.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"decision": review["decision"], "review": str(output),
                      "review_sha256": digest(output), "certificate_sha256": review["certificate_sha256"],
                      "checks": review["checks"],
                      "D1_B_max": review["errors"]["D1_B_max_full_radial_l1_display_only"],
                      "D2_total": review["errors"]["D2_total_display_only"],
                      "minimum_zero_free_lower": review["minimum_zero_free_lower_display_only"]}, indent=2))


if __name__ == "__main__":
    main()
