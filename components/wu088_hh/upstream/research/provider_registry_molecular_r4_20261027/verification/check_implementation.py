"""Changed-input contract checks; never replay the accepted compiler suite or fit samples."""
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import molecular_operator as m
import build_molecular as builder


def main():
    results = []

    def check(name, condition):
        results.append({"id": name, "pass": bool(condition)})

    def rejected(name, function, expected=ValueError):
        try:
            function()
        except expected:
            check(name, True)
        else:
            check(name, False)

    marker = json.loads((BASE / "registry/COMPLETE.json").read_text())
    check("complete_marker_all_member_hashes", all(hashlib.sha256((BASE / x["path"]).read_bytes()).hexdigest() == x["sha256"] for x in marker["members"]))
    c = json.loads((BASE / "registry/compiled.json").read_text())["rows"]
    check("six_new_columns_only", len(c) == 6 and marker["new_compiler_calls"] == 6)
    check("new_columns_conserve_integer_ledgers", all(v["charge_delta"] == v["baryon_delta"] == v["electron_lepton_delta"] == 0 and all(Fraction(str(x)) == 0 for x in v["isotope_delta"].values()) for v in c))
    check("new_energy_and_activation_remain_unqualified", all(v["energy"] is None and v["energy_status"] == "UNQUALIFIED:ENERGY" and v["activation"] is False and v["Q_approved"] is False for v in c))
    check("thermal_particle_change", [v["thermal_material_particle_delta"] for v in c] == [-1, 0, 0, 0, 0, 0])
    by_id = {v["event_id"]: v for v in c}
    check("HD_method_ownership_same", by_id[m.TIQM]["ownership_group_sha256"] == by_id[m.SQM]["ownership_group_sha256"])
    check("HD_ensembles_not_state_reverse_pair", by_id[m.TIQM]["reversible_material_pair_sha256"] != by_id[m.HD]["reversible_material_pair_sha256"])
    rejected("reject_method_sum", lambda: m.select_source_candidates([m.TIQM, m.SQM]))
    rejected("reject_unqualified_spin_sum", lambda: m.select_source_candidates([m.ORTHO, m.PARA]))
    rejected("reject_duplicate_source", lambda: m.select_source_candidates([m.TIQM, m.TIQM]))
    for label, T in [("zero", "0"), ("negative", "-1"), ("bool", True), ("float", 50.0), ("NaN", "NaN"), ("off_node", "51")]:
        rejected("reject_T_" + label, lambda T=T: m.evaluate_source_fit(m.RA, T))
    rejected("reject_extra_statistical_weight", lambda: m.evaluate_source_fit(m.RA, "50", extra_spin_factor="1/4"))
    rejected("reject_quarantined_bovino_fit", lambda: m.evaluate_source_fit(m.ORTHO, "10"))
    rejected("reject_physical_rate_request", lambda: m.request_physical_rate(m.RA))
    rejected("reject_unnormalized_lift", lambda: m.positive_lift("1", ["1/3", "1/3"]))
    rejected("reject_negative_lift", lambda: m.positive_lift("1", ["-1", "2"]))
    rejected("reject_missing_state_rates", lambda: m.destruction_defect(["1"], ["1"], [None], "1"))
    examples = json.loads((BASE / "registry/lift_examples.json").read_text())
    check("stored_sharp_bound", examples["sharp_bound"]["defect"] == "-1" and examples["sharp_bound"]["half_spread_L1_bound"] == "1")
    check("stored_nonconstant_same_total", examples["same_total_other_state"]["exact_flux"] == "3" and examples["sharp_bound"]["exact_flux"] == "1")
    check("stored_constant_and_zero_collider", examples["constant_coefficients"]["defect"] == "0" and examples["zero_collider"]["defect"] == "0")
    # The concrete preexecution finding: any partial output must stop before
    # source import/compilation/evaluation. Use an isolated, deliberately invalid base.
    with tempfile.TemporaryDirectory(prefix="wu_r4_partial_") as tmp:
        root = Path(tmp)
        (root / "registry").mkdir()
        (root / "registry/species.json").write_text("{}\n")
        original = builder.BASE
        builder.BASE = root
        try:
            try:
                builder.main()
            except ValueError as exc:
                check("partial_output_stops_before_source_or_compiler", str(exc).startswith("EXISTING_OUTPUT_REUSE_COMPLETE_OR_REVIEW_PARTIAL_NO_RECOMPUTE"))
            else:
                check("partial_output_stops_before_source_or_compiler", False)
        finally:
            builder.BASE = original
    # Failure receipt test in a copied runner, with no scientific command.
    with tempfile.TemporaryDirectory(prefix="wu_r4_runner_") as tmp:
        root = Path(tmp)
        (root / "verification").mkdir()
        runner = root / "verification/run_bounded.py"
        runner.write_bytes((BASE / "verification/run_bounded.py").read_bytes())
        attempt = subprocess.run([sys.executable, str(runner), "--attempt", "missing_executable", "--kind", "implementation", "--", str(root / "never_exists")], capture_output=True, text=True)
        receipt = json.loads((root / "raw/missing_executable/RECEIPT.json").read_text())
        check("failed_launch_has_actual_receipt", attempt.returncode == 1 and not receipt["child_spawned"] and receipt["exit_code"] is None and receipt["launch_error"]["type"] == "FileNotFoundError")
        empty = subprocess.run([sys.executable, str(runner), "--attempt", "empty", "--kind", "implementation", "--"], capture_output=True, text=True)
        check("empty_command_rejected_before_attempt_creation", empty.returncode != 0 and not (root / "raw/empty").exists())
        (BASE / "verification/EXPECTED_LAUNCH_FAILURE_RECEIPT.json").write_text(json.dumps({"purpose": "targeted implementation rejection-path test, not scientific execution failure", "receipt": receipt, "stdout": attempt.stdout, "stderr": attempt.stderr, "empty_command_returncode": empty.returncode}, indent=2) + "\n")
    result = {"scope": "CHANGED_INPUT_IMPLEMENTATION_CONTRACTS", "checks": results, "passed": sum(r["pass"] for r in results), "total": len(results),
              "new_positive_source_formula_samples": 0, "new_compiler_calls": 0, "old249_replays": 0}
    (BASE / "verification/IMPLEMENTATION_RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    if not all(x["pass"] for x in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
