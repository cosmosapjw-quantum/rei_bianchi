#!/usr/bin/env python3
"""PHYS28 final-review checks using frozen files and retained arithmetic only.

No science module imports, kernel evaluations, roots, quadrature, replay,
subprocesses, external writes, or new scientific validation campaign.
"""
from pathlib import Path
from decimal import Decimal as D, getcontext
from datetime import datetime, timezone
from hashlib import sha256, sha1
import argparse
import ast
import json
import stat
import zipfile

getcontext().prec = 80
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CANDIDATE = "64a556ce60ed6055ec12c49447b4715e91c0b3e60538c314bbe4289bc4900cc2"
RECORDS = []
RAW_PREDICATES = []
SCALE = D("1e-64")
KPSCALE = SCALE / 18
SSCALE = SCALE / (18 * 18)
TOL = D("1e-60")


def read(path):
    return json.loads((ROOT / path).read_bytes())


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def record(name, passed, **evidence):
    RECORDS.append({"name": name, "pass": bool(passed), **evidence})


def near(name, actual, expected, scale=D(1), tolerance=TOL):
    actual, expected, scale = D(actual), D(expected), D(scale)
    error = abs(actual - expected) / scale
    record(name, error <= tolerance, actual=str(actual), expected=str(expected),
           scale=str(scale), scaled_error=str(error), tolerance=str(tolerance))


def identity_rows(rows, prefix, base=ROOT):
    for row in rows:
        path = base / row["path"]
        data = path.read_bytes()
        record(prefix + row["path"],
               len(data) == row["bytes"] and sha256(data).hexdigest() == row["sha256"],
               bytes=len(data), sha256=sha256(data).hexdigest())


def check_all():
    frozen = read("evidence/CANDIDATE_FROZEN.json")
    record("candidate_manifest_identity",
           digest(ROOT / "evidence/CANDIDATE_FROZEN.json") == EXPECTED_CANDIDATE)
    record("candidate_file_count", frozen["file_count"] == len(frozen["files"]) == 87)
    identity_rows(frozen["files"], "candidate__")
    pre = read("contributions/numerics/PREEXECUTION_FROZEN.json")
    protocol = read("contributions/numerics/PROTOCOL.json")
    identity_rows(pre["files"], "preexecution__")
    identity_rows(protocol["inputs"], "protocol__")
    raw = read("contributions/numerics/SMALL_WIDTH_FIRST.json")
    old = read("inputs/PHYS26/contributions/numerics/FIXED_VARIANCE_ENVELOPE_FIRST.json")
    finite = read("inputs/PHYS27/contributions/numerics/FINITE_WIDTH_FIRST.json")
    run = read("contributions/numerics/EXECUTION.json")
    replay = read("portability/REPLAY_RECEIPT.json")
    summary = read("report/PHYS28_RESULTS_SUMMARY.json")
    source = read("SOURCE_MANIFEST.json")
    cts = raw["summary"]["actual_counts"]
    a, m, b = D("13.61"), D(18), D("24.58")
    L, H, delta = m - a, b - m, D("0.05")
    roots = old["inherited_boundary_residuals"]
    finite_comp = finite["threshold_comparison"]
    nodes = {key: D(value) for key, value in raw["energy_nodes_eV"].items()}
    forbidden = [
        "new_physical_root_searches", "physical_root_iterations",
        "quadrature_evaluations", "quadrature_node_solves",
        "finite_difference_evaluations", "width_root_sweep", "old_module_imports",
        "old_main_invocations", "closed_suite_replays", "old_physical_root_searches",
        "new_derivative_sign_campaigns", "native_runs", "gas_IVP_runs",
        "dense_LP_or_multiple_parameter_campaigns",
        "display_new_kernel_derivative_evaluations",
    ]
    bools = {
        "contract_expected_sha256": digest(ROOT / "PHYSICS_CONTRACT.json")
        == "d9c50cb43d60bf466eb92e91e8e62791fcf84680025c34fc0c42c899ed16fde2",
        "protocol_expected_sha256": digest(ROOT / "contributions/numerics/PROTOCOL.json")
        == "5298c389da5ddd7eb2a5246c3cb472faba93c7d97a39efe7ee99de441200b56a",
        "inherited_PHYS26_all_pass": old["summary"]["all_pass"],
        "inherited_PHYS27_all_pass": finite["summary"]["all_pass"],
        "PHYS27_copied_PHYS26_root_strings_unchanged":
        roots["Vstar_eV2"] == finite_comp["PHYS26_Vstar0_eV2"]
        and roots["W0_eV2"] == finite_comp["PHYS26_W00_eV2"],
        "PHYS27_root_summary_equals_raw_root_record":
        all(D(finite["new_physical_roots"][key]["midpoint_physical_variance_eV2"])
            == D(finite_comp[field]) for key, field in
            [("W_star_delta", "W_star_delta_eV2"), ("W_0_delta", "W_0_delta_eV2")]),
        "frozen_half_width_and_support":
        D(finite["constants"]["half_width_eV"]) == delta
        and [D(x) for x in finite["constants"]["photon_support_eV"]] == [a, b]
        and D(finite["constants"]["mean_eV"]) == m,
        "frozen_analytic_support":
        D.from_float(13.60) < a < m < b < D.from_float(24.59),
        "source_manifest_identity": digest(ROOT / "SOURCE_MANIFEST.json")
        == next(row["sha256"] for row in protocol["inputs"]
                if row["path"] == "SOURCE_MANIFEST.json"),
        "exactly_four_distinct_supported_nodes":
        len(set(nodes.values())) == 4 and all(a <= e <= b for e in nodes.values()),
        "actual_joint_evaluation_counts_match_preregistered":
        cts["primary_jet_joint_evaluations"] == cts["independent_scalar_joint_evaluations"] == 4
        and cts["combined_kernel_derivative_joint_evaluations"] == 8,
        "actual_component_output_counts":
        cts["k_component_outputs"] == cts["k_prime_component_outputs"] == 8
        and cts["combined_k_and_k_prime_component_outputs"] == 16,
        "all_forbidden_execution_counts_zero": all(cts[key] == 0 for key in forbidden),
    }
    for label, key in [("upper_root", "Vstar_eV2"), ("lower_root", "W0_eV2")]:
        law = raw["fixed_W_differentiated_laws"][label]
        w = D(roots[key])
        bools[label + "_law__interior_supported_positive"] = (
            0 < w < L * H and all(a <= D(e) <= b for e in law["energies_eV"])
            and all(0 < D(p) < 1 for p in law["probabilities"]))
    for row in raw["checks"]:
        name = row["name"]
        extra = {}
        if "actual" in row:
            actual, expected, scale, tolerance = [
                D(row[key]) for key in ("actual", "expected", "scale", "tolerance")]
            error = abs(actual - expected) / scale
            expected_tol = D("1e-65") if name.endswith("stored_root_response_small") else TOL
            if name.startswith("PHYS26_constant__"):
                expected_scale = max(abs(actual), abs(expected))
            elif "sigma_cm2" in name:
                expected_scale = D("1e-18")
            elif ("k_prime_s-4_eV-1" in name or "B_partial_delta" in name
                  or name.endswith("B_terms_equal_compact")):
                expected_scale = KPSCALE
            elif ("S_partial_W" in name or name.endswith("S_secant_equal_quotient")):
                expected_scale = SSCALE
            elif ("kernel_expression" in name or "__response_formula" in name
                  or "__stored_root_" in name):
                expected_scale = SCALE
            else:
                expected_scale = max(D(1), abs(actual), abs(expected))
            passed = (error <= tolerance and tolerance == expected_tol
                      and scale == expected_scale
                      and error == D(row["scaled_error"])
                      and actual - expected == D(row["residual"]))
            extra = {"recomputed_scaled_error": str(error), "normalization_rechecked": True}
        elif "actual_sha256" in row:
            path = ROOT / name.removeprefix("frozen_identity__")
            passed = (digest(path) == row["actual_sha256"] == row["expected_sha256"]
                      and path.stat().st_size == row["actual_bytes"] == row["expected_bytes"])
        elif name in bools:
            passed = bools[name]
        elif name.endswith("__slope_positive"):
            passed = D(row["slope"]) > 0
        elif name.endswith("__trapezoid_gap_negative"):
            passed = D(row["gap"]) < 0
        elif name.endswith("__expected_coefficient_sign"):
            passed = (D(row["coefficient_eV"]) > 0 if "upper_root" in name
                      else D(row["coefficient_eV"]) < 0)
            passed = passed and row["blind_prediction_test"] is False
        else:
            passed = False
            extra = {"unknown_check_schema": True}
        RAW_PREDICATES.append({"name": name, "reassessed_pass": bool(passed),
                               "stored_pass": row["pass"], **extra})
    record("all_120_retained_predicates_reassessed",
           len(RAW_PREDICATES) == 120
           and all(x["reassessed_pass"] and x["stored_pass"] is True for x in RAW_PREDICATES))

    j = read("inputs/PHYS22_INITIAL_COEFFICIENTS.json")["results"]["baseline_local"]["J_nonphoto"][2]
    record("full_serialized_J", raw["constants"]["J_h2_x"] == j[0]
           and raw["constants"]["J_h2_w"] == j[3])
    record("four_node_definitions", nodes == {
        "a": a, "v_star": m + D(roots["Vstar_eV2"]) / L,
        "u_zero": m - D(roots["W0_eV2"]) / H, "b": b})
    for label, root_key, distance in [("upper_root", "Vstar_eV2", L),
                                      ("lower_root", "W0_eV2", H)]:
        w = D(roots[root_key])
        law = raw["fixed_W_differentiated_laws"][label]
        e = list(map(D, law["energies_eV"]))
        p = list(map(D, law["probabilities"]))
        ep = list(map(D, law["endpoint_center_first_derivatives"]))
        pp = list(map(D, law["probability_first_derivatives_eV-1"]))
        for field, value in {
            "mass": sum(p), "mean_eV": sum(p[i] * e[i] for i in range(2)),
            "variance_eV2": sum(p[i] * (e[i] - m)**2 for i in range(2)),
            "mass_first_derivative_eV-1": sum(pp),
            "mean_first_derivative": sum(pp[i] * e[i] + p[i] * ep[i] for i in range(2)),
            "physical_variance_first_derivative_eV":
            sum(pp[i] * (e[i] - m)**2 + 2 * p[i] * (e[i] - m) * ep[i] for i in range(2)),
        }.items():
            near(label + "__retained_law__" + field, value, law[field])
        for path in ("jet", "scalar"):
            cache = raw["joint_kernel_outputs"][path]
            data = raw["sensitivity"][path][label]
            anchor_key, moving_key = (("a", "v_star") if label == "upper_root"
                                      else ("b", "u_zero"))
            ka, kc = [D(cache[key]["k_s-4"]) for key in (anchor_key, moving_key)]
            kpa, kpc = [D(cache[key]["k_prime_s-4_eV-1"])
                        for key in (anchor_key, moving_key)]
            span = abs(nodes[anchor_key] - nodes[moving_key])
            den = distance**2 + w
            if label == "upper_root":
                kvals, kpvals = [ka, kc], [kpa, kpc]
                gap = kpa + kpc - 2 * (kc - ka) / span
                width_derivative = w / den * gap
                slope = (ka - kc + span * kpc) / span**2
                numerator = w * ka + distance**2 * kc
            else:
                kvals, kpvals = [kc, ka], [kpc, kpa]
                gap = kpc + kpa - 2 * (ka - kc) / span
                width_derivative = -w / den * gap
                slope = (ka - kc - span * kpc) / span**2
                numerator = distance**2 * kc + w * ka
            chain = sum(pp[i] * kvals[i] + p[i] * kpvals[i] * ep[i] for i in range(2))
            prefix = path + "__" + label + "__cached_rearithmetic__"
            near(prefix + "B_chain_rule", chain, data["B_partial_delta_compact_s-4_eV-1"], KPSCALE)
            near(prefix + "B_compact", width_derivative, data["B_partial_delta_compact_s-4_eV-1"], KPSCALE)
            near(prefix + "C", slope, data["S_partial_W_secant_s-4_eV-2"], SSCALE)
            near(prefix + "response", numerator / den, data["baseline_response_s-4"], SCALE)
            near(prefix + "c", -width_derivative / slope, data["coefficient_c_eV"])
            near(prefix + "sum_c_terms",
                 sum(D(v) for v in data["coefficient_decomposition_eV"].values()),
                 data["coefficient_c_eV"])
            for key, value in data["coefficient_decomposition_eV"].items():
                near(prefix + key, -D(data["B_partial_delta_terms_s-4_eV-1"][key]) / slope, value)
            near(prefix + "local_residual_diagnostic", -D(data["baseline_response_s-4"]) / slope,
                 data["local_root_residual_linearized_displacement_eV2"])
    comparison = raw["delta_005_comparison"]
    for label, root_key, finite_key in [
        ("upper_root", "Vstar_eV2", "W_star_delta"),
        ("lower_root", "W0_eV2", "W_0_delta"),
    ]:
        data = comparison[label]
        old_w = D(roots[root_key])
        new_w = D(finite["new_physical_roots"][finite_key]["midpoint_physical_variance_eV2"])
        coefficient = D(raw["sensitivity"]["jet"][label]["coefficient_c_eV"])
        shift, linear = new_w - old_w, delta * coefficient
        residual = shift - linear
        computed = {
            "PHYS26_zero_width_root_eV2": old_w, "PHYS27_delta_005_root_eV2": new_w,
            "coefficient_c_eV": coefficient, "linear_shift_at_delta_005_eV2": linear,
            "predicted_root_at_delta_005_eV2": old_w + linear,
            "actual_shift_at_delta_005_eV2": shift,
            "residual_actual_minus_linear_eV2": residual,
            "absolute_residual_relative_to_actual_shift": abs(residual / shift),
            "absolute_residual_relative_to_actual_shift_percent": 100 * abs(residual / shift),
            "single_width_effective_slope_eV": shift / delta,
        }
        for field, value in computed.items():
            near(label + "__single_width__" + field, value, data[field])
    gap = comparison["coexistence_width"]
    old_gap = D(roots["W0_eV2"]) - D(roots["Vstar_eV2"])
    new_gap = (D(comparison["lower_root"]["PHYS27_delta_005_root_eV2"])
               - D(comparison["upper_root"]["PHYS27_delta_005_root_eV2"]))
    slope_gap = (D(raw["sensitivity"]["jet"]["lower_root"]["coefficient_c_eV"])
                 - D(raw["sensitivity"]["jet"]["upper_root"]["coefficient_c_eV"]))
    reduction, linear_red = old_gap - new_gap, -delta * slope_gap
    residual_red = reduction - linear_red
    for field, value in {
        "PHYS26_width_eV2": old_gap, "PHYS27_delta_005_width_eV2": new_gap,
        "width_first_derivative_eV": slope_gap, "reduction_first_derivative_eV": -slope_gap,
        "linear_reduction_at_delta_005_eV2": linear_red,
        "actual_reduction_at_delta_005_eV2": reduction,
        "predicted_width_at_delta_005_eV2": old_gap - linear_red,
        "reduction_residual_actual_minus_linear_eV2": residual_red,
        "absolute_reduction_residual_relative_to_actual": abs(residual_red / reduction),
        "absolute_reduction_residual_relative_to_actual_percent": 100 * abs(residual_red / reduction),
        "actual_reduction_fraction": reduction / old_gap, "linear_reduction_fraction": linear_red / old_gap,
    }.items():
        near("coexistence__" + field, value, gap[field])
    record("summary_exact_field_copies",
           summary["sensitivity"] == raw["sensitivity"]["jet"]
           and summary["comparison_at_delta_005"] == comparison
           and summary["first_summary"] == raw["summary"]
           and summary["energy_nodes_eV"] == raw["energy_nodes_eV"])
    display = read("figures/DISPLAY_DATA.json")
    for label in ("upper_root", "lower_root"):
        item = raw["sensitivity"]["jet"][label]
        record("display_cached_fields__" + label,
               display["branches"][label]["c_contributions_eV"] == item["coefficient_decomposition_eV"]
               and display["branches"][label]["c_total_eV"] == item["coefficient_c_eV"])
    first_bytes = (ROOT / "contributions/numerics/SMALL_WIDTH_FIRST.json").read_bytes()
    replay_bytes = (ROOT / "portability/REPLAY_RESULT.json").read_bytes()
    record("actual_first_replay_byte_and_json_equal",
           first_bytes == replay_bytes and raw == json.loads(replay_bytes))
    record("first_stdout_result_binding",
           read("contributions/numerics/FIRST_STDOUT.txt")["result_sha256"] == sha256(first_bytes).hexdigest()
           and read("contributions/numerics/FIRST_STDOUT.txt")["summary"] == raw["summary"])
    record("both_stderr_empty", (ROOT / "contributions/numerics/FIRST_STDERR.txt").stat().st_size
           == (ROOT / "portability/REPLAY_STDERR.txt").stat().st_size == 0)
    record("stdout_byte_equal", (ROOT / "contributions/numerics/FIRST_STDOUT.txt").read_bytes()
           == (ROOT / "portability/REPLAY_STDOUT.txt").read_bytes())
    record("actual_execution_success", run["exit_code"] == replay["actual_exit_code"] == 0
           and not run["timed_out"] and not replay["timed_out"]
           and replay["launch_error"] is None and replay["status"] == "REPLAY_PASS")
    record("actual_ledgers_agree", run["actual_counts"] == replay["actual_counts"] == cts
           and run["first_result_summary"] == replay["result_summary"] == raw["summary"]
           and summary["total_execution"]["new_main"] == 2
           and summary["total_execution"]["joint_k_kprime_evaluations"] == 16)
    timing = [protocol["written_utc"], pre["frozen_utc"], run["started_utc"],
              run["finished_utc"], read("portability/PORTABILITY_PROTOCOL.json")["frozen_before_replay_utc"],
              replay["started_utc"], replay["ended_utc"], frozen["frozen_utc"]]
    dates = list(map(datetime.fromisoformat, timing))
    record("chronology_frozen_before_first_and_replay", dates == sorted(dates), timestamps=timing)
    archive_path = ROOT / "portability/PHYS28_PORTABLE_STAGE.zip"
    manifest = read("portability/PORTABLE_MANIFEST.json")
    destination = Path(replay["destination"])
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        expected_names = [x["path"] for x in manifest["files"]] + ["PORTABLE_MANIFEST.json"]
        record("portable_exact_member_set", len(names) == len(set(names)) == 29
               and set(names) == set(expected_names))
        record("portable_archive_identity", digest(archive_path) == replay["archive"]["sha256"]
               and archive_path.stat().st_size == replay["archive"]["bytes"])
        manifest_bytes = (ROOT / "portability/PORTABLE_MANIFEST.json").read_bytes()
        record("portable_manifest_exact", archive.read("PORTABLE_MANIFEST.json") == manifest_bytes
               == (destination / "PORTABLE_MANIFEST.json").read_bytes())
        for row in manifest["files"]:
            data = archive.read(row["path"])
            restored = destination / row["path"]
            current = ROOT / row["path"]
            mode = (archive.getinfo(row["path"]).external_attr >> 16) & 0o777
            record("portable_payload__" + row["path"],
                   sha256(data).hexdigest() == row["sha256"] and len(data) == row["bytes"]
                   and data == restored.read_bytes() == current.read_bytes()
                   and not restored.is_symlink() and stat.S_IMODE(restored.stat().st_mode) == 0o644
                   and row["mode"] == "100644" and mode == 0o644)
    record("retained_restore_tree_exact",
           sorted(p.relative_to(destination).as_posix() for p in destination.rglob("*") if p.is_file())
           == sorted(expected_names))
    record("portable_runtime_dependency_set",
           len(manifest["files"]) == 28 and len(manifest["runtime_files"]) == 22
           and set(manifest["runtime_files"]) == {x["path"] for x in pre["files"]}
           | {"contributions/numerics/PREEXECUTION_FROZEN.json"})
    for section in ("preexecution_restore", "postexecution_restore"):
        data = replay[section]
        record("receipt__" + section, data["payload_count"] == 28 and data["all_pass"]
               and all(row[key] for row in data["files"] for key in
                       ["size_equal", "sha256_equal", "archive_byte_equal", "regular_file", "mode_100644"]))
    dep = replay["preexecution_dependency_chain"]
    record("receipt_dependency_checks", dep["all_pass"] and all(x["pass"] for x in dep["checks"])
           and (dep["protocol_input_count"], dep["frozen_identity_count"], dep["runtime_file_count"])
           == (18, 21, 22))
    correction = read("contributions/numerics/PREEXECUTION_CORRECTION.json")
    identity_rows(correction["preserved_v1"], "preserved_first_version__")
    old_code = (ROOT / "contributions/numerics/preexecution_versions/v1/small_width_sensitivity.py").read_text()
    new_code = (ROOT / "contributions/numerics/small_width_sensitivity.py").read_text()
    record("v1_v2_only_expected_protocol_hash_in_code",
           old_code.replace("6bf9436619c473b8f919a2735bb680da1890f9615786f6c8eb94f676d8cf852f",
                            "5298c389da5ddd7eb2a5246c3cb472faba93c7d97a39efe7ee99de441200b56a") == new_code)
    old_protocol = read("contributions/numerics/preexecution_versions/v1/PROTOCOL.json")
    for field in ("meaning", "arithmetic", "node_selection", "kernel_paths",
                  "fixed_W_derivatives", "checks", "tolerances", "budgets"):
        record("preexecution_science_semantics_unchanged__" + field,
               old_protocol[field] == protocol[field])
    tree = ast.parse(new_code)
    imports = sorted({node.module.split(".")[0] for node in ast.walk(tree)
                      if isinstance(node, ast.ImportFrom)}
                     | {alias.name.split(".")[0] for node in ast.walk(tree)
                        if isinstance(node, ast.Import) for alias in node.names})
    record("new_science_static_imports", imports == sorted([
        "__future__", "argparse", "decimal", "hashlib", "json", "math", "pathlib", "platform", "traceback"]),
           imports=imports, main_imported_or_executed=False)
    for path, row in source["files"].items():
        data = (ROOT / "inputs/pinned_source" / path).read_bytes()
        blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        record("pinned_source_local_blob__" + path,
               blob == row["git_blob"] == row["actual_blob"]
               and sha256(data).hexdigest() == row["sha256"] and len(data) == row["bytes"])
    record("protected_state_consistency", summary["protected"] == read("PHYSICS_CONTRACT.json")["protected"]
           and summary["physical_admission"] == "HOLD")
    report = (ROOT / "report/PHYS28_REPORT_KO.md").read_text()
    record("report_operational_closeout_not_preclaimed",
           "선제 완료 주장하지 않는다" in report
           and "PHYS28_PUBLICATION_RECEIPT.json" in report
           and "NOT_RUN" in summary["next"]["status"])
    record("report_representative_numeric_tokens", all(token in report for token in [
        "+5.71638089140", "-2.37494837006", "+0.285819044570", "-0.118747418503",
        "+0.00369532482000", "-0.000605391537981", "1.27638736%", "0.50722856%",
        "0.404566463073", "0.408867179431", "0.00430071635798", "1.05186148%"]))
    record("candidate_preserved_at_review_end", all(
        (ROOT / row["path"]).stat().st_size == row["bytes"]
        and digest(ROOT / row["path"]) == row["sha256"] for row in frozen["files"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise FileExistsError("Preserve first review output; fresh output required")
    check_all()
    failures = [row["name"] for row in RECORDS if not row["pass"]]
    data = {
        "task": "REI-PHYS28-20261011", "reviewer": "/root/phys28_decision",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "STATIC_RETAINED_EVIDENCE_REVIEW_NOT_NEW_SCIENCE",
        "review_script_sha256": digest(Path(__file__)),
        "candidate_sha256": EXPECTED_CANDIDATE,
        "decimal_precision_for_retained_arithmetic": 80,
        "science_main": 0, "old_main": 0, "new_kernel_derivative_evaluations": 0,
        "physical_root_searches": 0, "replay": 0,
        "checks": RECORDS, "retained_raw_predicates": RAW_PREDICATES,
        "summary": {"checks": len(RECORDS), "passed": len(RECORDS) - len(failures),
                    "failed": len(failures), "failure_names": failures,
                    "raw_predicates_reassessed": len(RAW_PREDICATES),
                    "raw_predicate_failures": [r["name"] for r in RAW_PREDICATES
                                               if not r["reassessed_pass"]],
                    "all_pass": not failures},
        "limitations": "Retained-value arithmetic and identity checks do not supply a new kernel oracle, exact-root enclosure, physical validation, archive rebuild, replay, or publication evidence.",
    }
    with output.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(data["summary"], ensure_ascii=False))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
