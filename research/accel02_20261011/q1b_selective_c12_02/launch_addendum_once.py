"""Execute the adopted addendum once, with preserved prior evidence and costs."""
import ast
import hashlib
import json
import resource
import subprocess
import time
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
REL = UNIT.relative_to(ROOT)
EVIDENCE_PINS = {
    "validate_selective.py": "35d8415c67851cfdd1fbbb8ff292be63774d6f5266f83cacebdb1f95f6dad2d4",
    "reconstruction_selective.py": "02faaca63e765b06d2286d07cc7835f445a372681ab753ac0091640ccc0eb741",
    "CONTRACT.json": "3e620d47a52a971ab151092c68636b2b447ed41e0d7b74337d9c40bda9240ab4",
    "evidence/serialization_r1/validate_selective.before.py": "9549de417a4055ce111f1973639b02bdb774b84998755703892bb3d78bbb5f2e",
    "evidence/serialization_r1/test_serialization_ast.py": "0b5bd199cecda98f30296ec6c2ffde31c5c242cf9584bc9523c99c1871601b0f",
    "evidence/attempt1/EXECUTION_RECEIPT.json": "8caf0e0ccd723263b7dfa7fd64b1280fcf17413e56b0717e6238f7fc05d4b0f1",
    "evidence/attempt1/RESULT.json": "dff04f37d379fa19051c65569345c0bb539363225b59de445bc4c1b5f4a0c858",
    "evidence/serialization_r1/RESULT.json": "9f808838a0c7b9340bbb5fa3c3a64ab57062617047121f8e48c8719b0a716eaa",
    "evidence/serialization_r1/FINAL_LF_NOEXEC_RECEIPT.json": "b46bc4b8aac7a578390c6e44427f1665e76402121bd77f9bce0aad84515c638d",
}
ENV = ["env", "OPENBLAS_NUM_THREADS=1", "OMP_NUM_THREADS=1",
       "MKL_NUM_THREADS=1", "NUMEXPR_NUM_THREADS=1"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    encoded = json.dumps(value, indent=2, allow_nan=False) + "\n"
    with path.open("x") as handle:
        handle.write(encoded)


def literal_assignment(path, name):
    tree = ast.parse(path.read_bytes())
    matches = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)
               and any(isinstance(target, ast.Name) and target.id == name
                       for target in node.targets)]
    assert len(matches) == 1, (path, name)
    return ast.literal_eval(matches[0].value)


def strict_load(path):
    def invalid(value):
        raise ValueError("nonfinite JSON: " + value)
    return json.loads(path.read_text(), parse_constant=invalid)


def launch(directory, script, wall, file_bytes, output_bytes, args=()):
    if directory.name == "attempt2":
        directory.mkdir(exist_ok=False)
    command = ENV + ["timeout", "--signal=KILL", f"{wall}s", "prlimit",
                     "--as=2147483648", f"--cpu={wall}", f"--fsize={file_bytes}",
                     "/usr/bin/python3", "-B", str(script), *args]
    write(directory / "STARTED.json", {
        "task": "Q1B_SELECTIVE_C12_02", "allocation": "SERIALIZATION_EXECUTION_ADDENDUM01",
        "started_unix_s": time.time(), "command": command, "cwd": str(ROOT),
        "executor": "controller_direct_owner_authorized", "runtime_model": "NOT_INDEPENDENTLY_OBSERVED",
        "input_pins": observed, "launcher_sha256": sha(Path(__file__)),
        "addendum_sha256": sha(UNIT / "EXECUTION_ADDENDUM01.json"),
        "child_script_sha256": sha(ROOT / script), "prior_files_sha256": preserved,
    })
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.monotonic()
    with (directory / "stdout.txt").open("xb") as out, (directory / "stderr.txt").open("xb") as err:
        child = subprocess.run(command, cwd=ROOT, stdout=out, stderr=err)
    elapsed = time.monotonic() - started
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    outputs = {p.name: {"sha256": sha(p), "bytes": p.stat().st_size}
               for p in directory.iterdir() if p.is_file()}
    try:
        result = strict_load(directory / "RESULT.json")
        complete = True
    except (OSError, ValueError) as exc:
        result = {"outcome": "HOLD_INCOMPLETE_RESULT", "error": str(exc)}
        complete = False
    unchanged = all(sha(ROOT / path) == digest for path, digest in preserved.items())
    receipt = {
        "command": command, "cwd": str(ROOT), "exit": child.returncode,
        "wall_s": elapsed, "cpu_RUSAGE_CHILDREN_s": cpu, "ended_unix_s": time.time(),
        "cpu_limit_semantics": "per-process rlimit; measured child CPU reported separately",
        "output_bytes_before_receipt": sum(item["bytes"] for item in outputs.values()),
        "output_cap_bytes": output_bytes, "outputs": outputs, "complete_result": complete,
        "outcome": result.get("outcome"), "prior_files_unchanged": unchanged,
        "execution": result.get("execution"),
    }
    receipt["limits_pass"] = (elapsed <= wall and receipt["output_bytes_before_receipt"] <= output_bytes
                               and all(item["bytes"] <= file_bytes for item in outputs.values()))
    write(directory / "EXECUTION_RECEIPT.json", receipt)
    return receipt, result


if __name__ == "__main__":
    r2 = UNIT / "evidence/serialization_r2"
    a2 = UNIT / "evidence/attempt2"
    assert not a2.exists(), "attempt2 already exists: no retry"
    assert set(p.name for p in r2.iterdir()) == {"test_serialization_ast.py"}, "r2 already started"
    assert not (UNIT / "ADDENDUM01_RETURN.json").exists()
    expected = {str((UNIT / p).relative_to(ROOT)): value for p, value in EVIDENCE_PINS.items()}
    prior = UNIT.parent / "q1b_reconstruction01/validate_reconstruction.py"
    assert sha(prior) == "ed54182dcfc1f4a764dc1b0108e79b6a3c40dd7b83166fa2e3bf50749ffe1934"
    inherited = literal_assignment(prior, "PINS")
    extras = literal_assignment(UNIT / "validate_selective.py", "extras")
    assert len(inherited) == 18 and len(extras) == 5
    expected.update(inherited)
    expected.update(extras)
    observed = {path: sha(ROOT / path) for path in expected}
    if observed != expected:
        write(UNIT / "ADDENDUM01_RETURN.json", {
            "outcome": "HOLD_INPUT_FILE_IDENTITY", "expected": expected, "observed": observed,
            "native_processes_added": 0, "serialization_processes_added": 0})
        raise SystemExit(1)
    new_existing = {"EXECUTION_ADDENDUM01.json", "launch_addendum_once.py",
                    "evidence/serialization_r2/test_serialization_ast.py"}
    preserved = {str(p.relative_to(ROOT)): sha(p) for p in UNIT.rglob("*")
                 if p.is_file() and str(p.relative_to(UNIT)) not in new_existing}
    preserved.update(observed)
    pure_receipt, pure = launch(r2, REL / "evidence/serialization_r2/test_serialization_ast.py",
                                30, 4194304, 4194304)
    pure_pass = (pure_receipt["exit"] == 0 and pure_receipt["complete_result"]
                 and pure_receipt["limits_pass"] and pure_receipt["prior_files_unchanged"]
                 and pure.get("outcome") == "SOURCE_REPAIR_SERIALIZATION_TEST_PASS_SCOPED"
                 and len(pure.get("cases", [])) == 4
                 and all(row["repaired"] == "PASS" for row in pure["cases"]))
    receipts = [pure_receipt]
    native_counts = {"native_process": 0, "SIGMA": 0, "SIGMA_energies": 0}
    outcome = "HOLD_SERIALIZATION_R2"
    if pure_pass:
        science_receipt, science = launch(a2, REL / "validate_selective.py", 180, 33554432, 67108864,
            ["--root", str(ROOT), "--output", str(REL / "evidence/attempt2/RESULT.json")])
        receipts.append(science_receipt)
        native_counts = science.get("execution", {})
        outcome = science.get("outcome", "HOLD_INCOMPLETE_RESULT")
        if not (science_receipt["complete_result"] and science_receipt["limits_pass"]
                and science_receipt["prior_files_unchanged"]):
            outcome = "HOLD_EXECUTION_RESOURCE_OR_CAP"
        elif outcome.startswith("PASS_") and (science_receipt["exit"] != 0 or len(science.get("metrics", {})) != 9):
            outcome = "HOLD_INCOMPLETE_RESULT"
    counts = {key: start + native_counts.get(key, 0) for key, start in
              [("native_process", 2), ("SIGMA", 17), ("SIGMA_energies", 65568)]}
    caps_pass = all(counts[key] <= cap for key, cap in
                    [("native_process", 3), ("SIGMA", 33), ("SIGMA_energies", 131104)])
    forbidden_zero = all(native_counts.get(key, 0) == 0
                         for key in ["RATES", "RHS", "JAC", "ODE", "build", "history_replay"])
    if not caps_pass or not forbidden_zero:
        outcome = "HOLD_EXECUTION_RESOURCE_OR_CAP"
    added_wall = sum(r["wall_s"] for r in receipts)
    added_cpu = sum(r["cpu_RUSAGE_CHILDREN_s"] for r in receipts)
    returned = {
        "task": "Q1B_SELECTIVE_C12_02", "allocation": "SERIALIZATION_EXECUTION_ADDENDUM01",
        "outcome": outcome, "pure_gate": pure.get("outcome"), "receipts": receipts,
        "cumulative_native_counts": counts, "cumulative_caps_pass": caps_pass,
        "forbidden_calls_zero": forbidden_zero, "cumulative_serialization_processes": 2,
        "cumulative_measured_wall_with_source_ic_s": 39.694922727008816 + added_wall,
        "known_cpu_with_source_ic_s": 39.212523 + added_cpu,
        "unmeasured_serialization_r1_cpu_and_orchestration_overhead": "UNKNOWN_NOT_ZERO",
        "executor": "controller_direct_owner_authorized",
        "embedded_validator_requested_model_field": "historical worker request; not actual current executor identity",
        "review": "PENDING; no independent review claimed", "global_admission": "HOLD",
        "next_action": "Review complete saved metrics; if scoped acceptance is justified, plan Q1B3 stage-consistent coupled consumer",
    }
    write(UNIT / "ADDENDUM01_RETURN.json", returned)
    print(json.dumps({"outcome": outcome, "pure_gate": pure.get("outcome"),
                      "cumulative_native_counts": counts, "added_wall_s": added_wall}, indent=2))
    raise SystemExit(0 if outcome.startswith("PASS_") else 1)
