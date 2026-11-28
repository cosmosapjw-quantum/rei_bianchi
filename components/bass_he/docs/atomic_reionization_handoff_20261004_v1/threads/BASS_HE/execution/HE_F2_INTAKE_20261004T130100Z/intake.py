"""Record one bounded HE-F2 dependency inspection; never run scientific kernels."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
from datetime import datetime, timezone
import urllib.error
import urllib.request

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
REPO = ROOT.parents[1]
REI_REPO = "https://github.com/cosmosapjw-quantum/rei_bianchi.git"
REI_BRANCH = "forward/rust-reion-kernels-20260922"


def atomic_json(name, value):
    fd, temporary = tempfile.mkstemp(prefix="." + name, dir=OUT)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, OUT / name)
        directory = os.open(OUT, os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run(*args):
    return subprocess.check_output(args, cwd=REPO, text=True).strip()


def main():
    # This evidence directory is immutable after its first inspection.
    if (OUT / "RETURN.json").exists():
        raise RuntimeError("Preserve this inspection; use a new directory for a new run")
    head = run("git", "rev-parse", "HEAD")
    branch = run("git", "branch", "--show-current")
    tasks = json.loads((OUT.parents[1] / "TASKS.json").read_text())
    assert branch == tasks["branch"]
    receipt_path = OUT.parents[1] / "runs/HE-F1_20261004/RETURN.json"
    receipt_bytes = receipt_path.read_bytes()
    receipt = json.loads(receipt_bytes)
    assert receipt["task_id"] == "HE-F1" and receipt["state"] == "completed"
    core = REPO / "research/shared_c64/20261003/EOR_B3_ATOMIC_EXPORT_v1/src/bass_he_atomic_export/_rate.py"
    core_hash = hashlib.sha256(core.read_bytes()).hexdigest()
    assert core_hash == receipt["input_identity"]["GM25_core_sha256"]
    # The completion receipt is inherited evidence, not a fresh suite execution.
    state = json.loads((ROOT / "EXECUTION_STATE.json").read_text())
    state["completed_task_ids"].append("HE-F1")
    state["note"] = "Local resumption overlay: inherited HE-F1 implementation receipt; no external task completion or scientific admission inferred."
    state["runtime_results"].append({
        "task_id": "HE-F1",
        "evidence_kind": "inherited_completion_receipt",
        "path": str(receipt_path.relative_to(ROOT)),
        "sha256": hashlib.sha256(receipt_bytes).hexdigest(),
        "published_commit": head,
        "suite_reexecuted": False,
    })
    atomic_json("RESUME_STATE.json", state)
    spec = importlib.util.spec_from_file_location("task_packet", ROOT / "tools/task_packet.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    program = json.loads((ROOT / "PROGRAM.json").read_text())
    next_task = module.select(program, state, "BASS_HE")
    assert next_task["status"] == "WAITING_OR_FINISHED"
    unmet = next(t for t in next_task["waiting"] if t["id"] == "HE-F2")["unmet"]
    assert set(unmet) == {"REI-F00", "REI-F01"}
    atomic_json("NEXT_TASK.json", next_task)
    remote_sha = run("git", "ls-remote", "--heads", REI_REPO, "refs/heads/" + REI_BRANCH).split()[0]
    base = f"https://raw.githubusercontent.com/cosmosapjw-quantum/rei_bianchi/{remote_sha}/"
    paths = [
        "docs/atomic_reionization_handoff_20261004_v1/threads/rei_bianchi/TASKS.json",
        "docs/atomic_reionization_handoff_20261004_v1/EXECUTION_STATE.json",
        "docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/rei_model_lock.json",
        "docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/closure_process_decision.json",
        "docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/parent_and_lane_applicability.json",
        "rust/rei_microphysics/src/atomic_provider.rs",
    ]
    observed = []
    for path in paths:
        observation = {"path": path, "url": base + path}
        try:
            with urllib.request.urlopen(base + path, timeout=20) as response:
                data = response.read()
                observation.update(status=response.status, sha256=hashlib.sha256(data).hexdigest())
                if path.endswith("TASKS.json"):
                    content = json.loads(data)
                    observation["selected_tasks"] = [t for t in content["tasks"] if t["id"] in {"REI-F00", "REI-F01"}]
                elif path.endswith("EXECUTION_STATE.json"):
                    observation["content"] = json.loads(data)
        except urllib.error.HTTPError as error:
            observation.update(status=error.code, error=str(error))
        except Exception as error:
            observation.update(status="TRANSPORT_ERROR", error=str(error))
        observed.append(observation)
        # Preserve each completed observation even if the next request fails.
        atomic_json("DEPENDENCY_INSPECTION.json", {
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "repository": "cosmosapjw-quantum/rei_bianchi",
            "branch": REI_BRANCH, "commit": remote_sha,
            "observations": observed,
            "ceiling": "Selected published paths only; absence here does not exclude private or unpublished consumer work.",
        })
    schema = json.loads((ROOT / "common/RETURN_CONTRACT.schema.json").read_text())
    result = {
        "task_id": "HE-F2", "state": "blocked",
        "input_identity": {
            "repository": "cosmosapjw-quantum/BASS_HE", "branch": branch,
            "execution_commit": head, "HE_F1_receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
            "GM25_core_sha256": core_hash, "rei_commit": remote_sha,
        },
        "changed_paths": [str(p.relative_to(REPO)) for p in sorted(OUT.iterdir()) if p.is_file()] + [str((OUT / "RETURN.json").relative_to(REPO))],
        "commands": [{"command": f"python3 {Path(__file__).relative_to(REPO)}", "exit_code": 0, "evidence_path": "INSPECTION_LOG.txt"}],
        "artifacts": ["RESUME_STATE.json", "NEXT_TASK.json", "DEPENDENCY_INSPECTION.json", "INSPECTION_LOG.txt", "intake.py"],
        "claim": {"basis": "Inherited HE-F1 completion receipt, exact GM25 core identity, fresh local selector and pinned consumer-path inspection", "ceiling": "Resumption and dependency inspection only; HE-F2 ledger/closure not implemented or admitted; no fresh scientific suite or physical runtime"},
        "next_task": "HE-F2",
        "blocker": {"kind": "BLOCKED_CONSUMER_CONTRACT", "unmet_tasks": unmet, "reason": "Require actual REI-F00 scope/closure artifacts and REI-F01 provider contract with completion evidence before binding. Published task cards are not completion receipts."},
        "tests": None,
        "chatgpt_sync": {"url": "https://chatgpt.com/c/6abfa004-5738-83ee-8b2f-956c60cbdc17", "status": "AUTH_REQUIRED_NOT_READ_OR_WRITTEN", "handoff": "../CHATGPT_SYNC_KO.md"},
        "baseline_nonblocking": "REI-F08 baseline may proceed; HE-F2 only delays optional REI-F09 sensitivity.",
    }
    import jsonschema
    jsonschema.Draft202012Validator(schema).validate(result)
    atomic_json("RETURN.json", result)
    print(json.dumps({"return_schema": "PASS", "GM25_core_identity": "PASS", "selector_skips_completed_HE_F1": "PASS", "HE_F2_unmet": unmet, "consumer_commit": remote_sha, "scientific_suite_reexecuted": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
