"""Consume this pinned intake once and preserve the F01 dependency boundary."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile

OUT = Path(__file__).resolve().parent
EXECUTION = OUT.parent
PACKET = OUT.parents[3]
REPO = PACKET.parents[1]


def module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def write(name, value):
    fd, temporary = tempfile.mkstemp(prefix="." + name, dir=OUT)
    with os.fdopen(fd, "w") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, OUT / name)
    fd = os.open(OUT, os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def main():
    if (OUT / "RETURN.json").exists():
        raise RuntimeError("Preserve this intake; create a new directory for new evidence")
    inspection = json.loads((OUT / "DEPENDENCY_INSPECTION.json").read_bytes())
    files = {}
    for item in inspection["observations"]:
        if item["status"] == 200:
            data = (OUT / item["local_path"]).read_bytes()
            if hashlib.sha256(data).hexdigest() != item["sha256"]:
                raise ValueError("Imported observation bytes changed: " + item["path"])
            files[item["path"]] = data
        elif item["status"] != 404:
            raise ValueError("Unresolved retrieval failure: " + item["path"])
    base = "docs/atomic_reionization_handoff_20261004_v1/"
    receipt_path = base + "runtime_returns/REI-F00.json"
    previous = json.loads((EXECUTION / "HE_F2_INTAKE_20261004T130100Z/RESUME_STATE.json").read_bytes())
    state = module(EXECUTION / "consumer_receipts.py").import_scope_lock(previous, files[receipt_path], files, inspection["commit"])
    state["note"] = "Local overlay with inherited HE-F1 completion and hash-verified published REI-F00 design-lock receipt. No REI-F01 completion or physical admission inferred."
    selector = module(PACKET / "tools/task_packet.py")
    selected = selector.select(json.loads((PACKET / "PROGRAM.json").read_bytes()), state, "BASS_HE")
    unmet = next(t for t in selected["waiting"] if t["id"] == "HE-F2")["unmet"]
    if unmet != ["REI-F01"]:
        raise ValueError("Inspect the changed dependency graph before execution")
    scope = state["runtime_results"][-1]["scope"]
    if scope["rct_enabled"] is not False or scope["physical_provider_admitted"] is not False:
        raise ValueError("Consumer scope changed; obtain its explicit RCT closure contract")
    write("RESUME_STATE.json", state)
    write("NEXT_TASK.json", selected)
    write("CONSUMER_SCOPE_INSPECTION.json", {
        "consumer_commit": inspection["commit"], "verified_task": "REI-F00",
        "scope": scope, "remaining_dependency": "REI-F01",
        "enabled_RCT_photon_closure_admitted": False,
        "HE_F2_ledger_accepted": False,
        "ceiling": "Consumer design lock verified; RCT-disabled baseline does not supply an enabled optional RCT energy/transport closure.",
    })
    result = {
        "task_id": "HE-F2", "state": "blocked",
        "input_identity": {"BASS_HE_commit": "cbc654cf6037a4a0dad2f60fb138964cfff62ada", "consumer_commit": inspection["commit"],
                           "receipt_sha256": hashlib.sha256(files[receipt_path]).hexdigest(),
                           "inspection_sha256": hashlib.sha256((OUT / "DEPENDENCY_INSPECTION.json").read_bytes()).hexdigest()},
        "changed_paths": [str(p.relative_to(REPO)) for p in sorted(OUT.rglob("*")) if p.is_file()] + [str((OUT / "RETURN.json").relative_to(REPO))],
        "commands": [
            {"command": "PYTHONDONTWRITEBYTECODE=1 python3 " + str((EXECUTION / "test_consumer_receipts.py").relative_to(REPO)), "exit_code": 1, "evidence_path": "RED_TESTS.log"},
            {"command": "PYTHONDONTWRITEBYTECODE=1 python3 " + str((EXECUTION / "test_consumer_receipts.py").relative_to(REPO)), "exit_code": 0, "evidence_path": "GREEN_TESTS.log"},
            {"command": "PYTHONDONTWRITEBYTECODE=1 python3 " + str(Path(__file__).relative_to(REPO)), "exit_code": 0, "evidence_path": "ADVANCE_STATE.log"},
        ],
        "artifacts": ["DEPENDENCY_INSPECTION.json", "RESUME_STATE.json", "NEXT_TASK.json", "CONSUMER_SCOPE_INSPECTION.json", "RED_TESTS.log", "GREEN_TESTS.log", "ADVANCE_STATE.log", "consumer/"],
        "claim": {"basis": "Pinned REI-F00 receipt/artifact/fixture hashes and command evidence; 13 focused receipt-boundary tests", "ceiling": "Input synchronization and design-lock dependency only; no physical provider, optional RCT closure, HE-F2 ledger acceptance or scientific kernel execution"},
        "next_task": "HE-F2",
        "blocker": {"kind": "BLOCKED_CONSUMER_CONTRACT", "unmet_tasks": unmet, "reason": "REI-F01 provider implementation and completion receipt absent from selected published paths. Current F00 scope disables He RCT; an enabled RCT ledger requires consumer-owned closure."},
        "tests": {"receipt_boundary": 13, "scientific_suites_reexecuted": False},
        "chatgpt_sync": {"url": "https://chatgpt.com/c/6abfa004-5738-83ee-8b2f-956c60cbdc17", "direct_delivery": "NOT_VERIFIED", "handoff": "../CHATGPT_SYNC_KO.md"},
    }
    import jsonschema
    jsonschema.Draft202012Validator(json.loads((PACKET / "common/RETURN_CONTRACT.schema.json").read_bytes())).validate(result)
    write("RETURN.json", result)
    print(json.dumps({"state_import": "PASS", "verified_external_task": "REI-F00", "HE_F2_unmet": unmet,
                      "consumer_RCT_enabled": scope["rct_enabled"], "scientific_suites_reexecuted": False}))


if __name__ == "__main__":
    main()
