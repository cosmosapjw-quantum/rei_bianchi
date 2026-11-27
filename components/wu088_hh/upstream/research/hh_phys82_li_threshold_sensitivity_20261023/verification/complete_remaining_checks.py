"""Complete only the unfinished PHYS82 checks after a test-label NameError.

The numerical pass is reused by byte-pinned evidence.  This command does not
call verify_numeric, quadrature, a valid temperature-rate evaluation, or the
production study's scientific branch.
"""
from collections import Counter
from contextlib import ExitStack
from datetime import datetime, timezone
import difflib
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("phys82_verifier_repaired", ROOT / "tests/verify_threshold.py")
v = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v
spec.loader.exec_module(v)


def main():
    original_path = ROOT / "verification/INDEPENDENT_VERIFICATION_01.json"
    original_script = ROOT / "verification/verify_threshold_attempt01.py"
    output = ROOT / "verification/INDEPENDENT_VERIFICATION_FINAL.json"
    attempt = Path(str(output) + ".attempt.json")
    fixtures = Path("/tmp/phys82_work_20261023/review/independent_verification_02_controls")
    if output.exists() or attempt.exists() or fixtures.exists():
        raise FileExistsError("TARGETED_COMPLETION_ALREADY_ATTEMPTED_INSPECT_NO_REPLAY")
    first = json.loads(original_path.read_text())
    original_hashes = first["source_sha256"]
    if v.sha(original_script) != original_hashes["tests/verify_threshold.py"]:
        raise ValueError("FIRST_VERIFIER_BYTES_NOT_PRESERVED")
    for name, expected in original_hashes.items():
        if name != "tests/verify_threshold.py" and v.sha(ROOT / name) != expected:
            raise ValueError("NUMERICAL_EVIDENCE_SOURCE_IDENTITY_CHANGED:" + name)
    if (first["status"] != "FAIL_RETAINED_FOR_DIAGNOSIS"
            or len(first["failures"]) != 2
            or {f["category"] for f in first["failures"]} != {"unexpected_exception", "callback_accounting"}
            or "NameError: name 'b' is not defined" not in first["failures"][0].get("traceback", "")):
        raise ValueError("UNEXPECTED_FIRST_PASS_FAILURE_REQUIRES_DIAGNOSIS")
    started = datetime.now(timezone.utc).isoformat()
    repair = {
        "status": "TARGETED_TEST_HARNESS_REPAIR", "started_utc": started,
        "defect": "Three repr(b) test labels referenced a lambda-local name; use repr(bad).",
        "extraction": "Split unfinished API guards into verify_api_guards so completed checks are not replayed.",
        "numerical_implementation_changed": False, "numerical_test_tolerances_changed": False,
        "original_script_sha256": v.sha(original_script),
        "repaired_script_sha256": v.sha(ROOT / "tests/verify_threshold.py"),
        "numerical_evidence_sha256": v.sha(original_path),
        "first_pass_failures": first["failures"],
        "numerical_failures_in_first_pass": 0,
    }
    v.create_json(attempt, repair)
    diff = "".join(difflib.unified_diff(
        original_script.read_text().splitlines(keepends=True),
        (ROOT / "tests/verify_threshold.py").read_text().splitlines(keepends=True),
        fromfile="verify_threshold_attempt01.py", tofile="tests/verify_threshold.py"))
    with (ROOT / "verification/VERIFIER_LABEL_REPAIR.diff").open("x") as stream:
        stream.write(diff)
    audit = v.Audit()
    audit.checks.update(first["counts"]["checks_by_category"])
    # This failed assertion was a consequence of the interrupted control tests.
    del audit.checks["callback_accounting"]
    audit.callbacks.update(first["counts"]["observed_callbacks"])
    audit.maxima = first["error_maxima"]
    audit.records = first["records"]
    blocked_calls = Counter()
    initial_callbacks = dict(audit.callbacks)

    def blocked(label):
        def reject(*args, **kwargs):
            blocked_calls[label] += 1
            raise AssertionError("REPEATED_NUMERICAL_CALLBACK_FORBIDDEN:" + label)
        return reject

    original_log_moment = v.gapmod._log_scaled_moment

    def only_removable_zero_limit(a, z):
        if z != 0.0:
            return blocked("nonzero_scaled_moment")(a, z)
        return original_log_moment(a, z)

    try:
        for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                     "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"):
            audit.check(os.environ.get(name) == "1", "repair_resources", name)
        profile, saved = v.runner.load_saved_li_rows(ROOT)
        baseline = v.runner.saved_baseline_rate(saved[255.0], profile["science_id"])
        reference = next(row["reference"] for row in first["records"]["independent_numerical_rows"]
                         if row["model"] == "L0" and row["T_K"] == 255.0)
        gap = v.gapmod.ThresholdRate(
            255.0, reference["K"], reference["logK"], reference["mean"], reference["excess"],
            reference["dK"], reference["dlog"], False, False,
            "L0", "gap", "REUSED_QUADRATURE_GUARD_FIXTURE_NOT_NEW_SCIENCE",
            v.I, v.I, v.E0, 1.0)
        models = v.gapmod.named_models()
        with ExitStack() as stack:
            stack.enter_context(patch.object(v, "quad", side_effect=blocked("quadrature")))
            stack.enter_context(patch.object(v.FiniteWindowCI, "evaluate", side_effect=blocked("finite_rate")))
            stack.enter_context(patch.object(v.gapmod, "_log_scaled_moment", side_effect=only_removable_zero_limit))
            v.verify_api_guards(audit, models, baseline, gap)
            v.verify_runner(audit, profile, saved, fixtures)
        audit.check(not blocked_calls, "repair_no_numerical_replay", "blocked_callback_counts", dict(blocked_calls))
    except Exception:
        audit.failures.append({"category": "targeted_completion_exception", "traceback": traceback.format_exc()})
    expected_callbacks = dict(initial_callbacks)
    expected_callbacks.update(runner_no_science_skip_invocations=2, runner_no_science_rejection_invocations=5)
    audit.check(dict(audit.callbacks) == expected_callbacks, "callback_accounting", "combined_observed_callbacks",
                {"observed": dict(audit.callbacks), "expected": expected_callbacks})
    final_hashes = {name: v.sha(ROOT / name) for name in original_hashes}
    audit.check(all(final_hashes[n] == h for n, h in original_hashes.items() if n != "tests/verify_threshold.py"),
                "byte_identity", "scientific_sources_unchanged_through_targeted_completion")
    repair.update(completed_utc=datetime.now(timezone.utc).isoformat(),
                  new_numerical_callbacks=dict(blocked_calls),
                  current_script_sha256=final_hashes["tests/verify_threshold.py"],
                  original_numerical_assertions_replayed=0)
    result = dict(first)
    result.update(schema="PHYS82_INDEPENDENT_VERIFICATION_COMBINED_V1",
                  status="PASS_SCOPED" if not audit.failures else "FAIL_RETAINED_FOR_DIAGNOSIS",
                  completed_utc=repair["completed_utc"], failures=audit.failures,
                  source_sha256=final_hashes, error_maxima=audit.maxima, records=audit.records,
                  repair=repair,
                  evidence_files={"original_pass": str(original_path.relative_to(ROOT)),
                                  "original_pass_sha256": v.sha(original_path),
                                  "original_verifier_bytes": str(original_script.relative_to(ROOT)),
                                  "repair_diff": "verification/VERIFIER_LABEL_REPAIR.diff"})
    result["counts"] = dict(first["counts"])
    result["counts"].update(checks=sum(audit.checks.values()), failures=len(audit.failures),
                            checks_by_category=dict(audit.checks), observed_callbacks=dict(audit.callbacks),
                            numerical_assertions_replayed_in_repair=0,
                            first_pass_bookkeeping_and_exception_failures=2,
                            first_pass_numerical_failures=0)
    v.create_json(output, result)
    print(json.dumps({"status": result["status"], "output": str(output),
                      "checks": result["counts"]["checks"], "failures": audit.failures,
                      "observed_callbacks": dict(audit.callbacks),
                      "additional_numerical_callbacks": dict(blocked_calls),
                      "original_verifier_sha256": repair["original_script_sha256"],
                      "repaired_verifier_sha256": repair["repaired_script_sha256"]}, indent=2))
    return 0 if not audit.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
