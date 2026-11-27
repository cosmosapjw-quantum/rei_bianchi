"""Run the already frozen OD and independent JVP commands for one z=3.5 node."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNTIME = Path("/root/WU088_R31AG_Z35_RUNTIME_20260930")
PYTHON = "/root/wu088_hh_ncp_work_v2/venv/bin/python"
LEDGER = HERE / "ONE_SHOT_LEDGER.json"


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_ledger(data: dict) -> None:
    tmp = LEDGER.with_suffix(".json.tmp")
    with tmp.open("w") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, LEDGER)


def stage(name: str, argv: list[str], assembled: Path, ledger: dict) -> None:
    if assembled.exists() or (HERE / (name + ".exit")).exists():
        raise RuntimeError("existing output or stage exit: refusing a rerun")
    ledger["science_commands_started"] += 1
    ledger["one_shot_state"] = name + "_IN_PROGRESS"
    ledger[name.lower() + "_started_utc"] = now()
    write_ledger(ledger)
    (HERE / (name + ".argv.json")).write_text(json.dumps(argv, indent=2) + "\n")
    with (HERE / (name + ".stdout")).open("w") as stdout, (HERE / (name + ".stderr")).open("w") as stderr:
        process = subprocess.Popen(argv, cwd=RUNTIME, stdout=stdout, stderr=stderr)
        seen = False
        while process.poll() is None:
            if assembled.exists() and not seen:
                ledger["authorization_consumed"] = True
                ledger["first_scientific_output_identity_utc"] = now()
                ledger["one_shot_state"] = "CONSUMED_" + name + "_OUTPUT_IDENTITY"
                ledger[name.lower() + "_output_sha256"] = sha(assembled)
                ledger[name.lower() + "_output_bytes"] = assembled.stat().st_size
                write_ledger(ledger)
                seen = True
            time.sleep(0.25)
        code = process.wait()
    (HERE / (name + ".exit")).write_text(str(code) + "\n")
    if assembled.exists() and not seen:
        ledger["authorization_consumed"] = True
        ledger["first_scientific_output_identity_utc"] = ledger.get("first_scientific_output_identity_utc", now())
        ledger[name.lower() + "_output_sha256"] = sha(assembled)
        ledger[name.lower() + "_output_bytes"] = assembled.stat().st_size
    ledger[name.lower() + "_completed_utc"] = now()
    ledger["one_shot_state"] = "CONSUMED_" + name + "_OUTPUT_IDENTITY" if assembled.exists() else name + "_FAILED_NO_OUTPUT"
    write_ledger(ledger)
    print(json.dumps({"stage": name, "exit_code": code, "assembled_exists": assembled.exists(), "sha256": ledger.get(name.lower() + "_output_sha256")}), flush=True)
    if code != 0 or not assembled.exists():
        raise RuntimeError(name + " failed; no rerun under this envelope")


def main() -> None:
    lock = json.loads((HERE / "PRE_OUTPUT_LOCK.json").read_text())
    ledger = json.loads(LEDGER.read_text())
    if ledger != lock or ledger["one_shot_state"] != "AUTHORIZED_PRE_OUTPUT":
        raise RuntimeError("one-shot authorization already started or lock drift")
    for relative, expected in lock["frozen_hashes"].items():
        preflight = json.loads((HERE / "PREFLIGHT_RUNTIME.json").read_text())
        rel = {"engine": "research/r31ad_five_node/unit_cell_model.py", "adaptive_policy": "research/r31af_adaptive/adaptive_policy.py", "global_model": "research/r31z_source_bound/source_bound.py", "six_node_manifest": "research/r31af_adaptive/ncp_followup_20260929/SIX_NODE_INPUT_MANIFEST.json", "z35_selection": "research/r31af_adaptive/ncp_followup_20260929/Z35_PREDICTION_SELECTION.json", "decision_rule": "research/r31af_adaptive/ncp_followup_20260929/FROZEN_Z35_DECISION_RULE.json", "preregistration": "research/r31af_adaptive/ncp_followup_20260929/NEXT_VALIDATION_PREREGISTRATION.json", "post_z35_policy": "research/r31ah_post_z35/POST_Z35_DECISION_POLICY.json", "post_z35_policy_helper": "research/r31ah_post_z35/post_validation_policy.py"}[relative]
        if sha(REPO / rel) != expected or preflight["status"] != "AUTHORIZED_PREFLIGHT_PASSED":
            raise RuntimeError("frozen source drift before science")
    for relative, expected in lock["producer_hashes"].items():
        if sha(RUNTIME / relative) != expected:
            raise RuntimeError("producer source drift before science")
    for filename, expected in lock["evidence_source_sha256"].items():
        if sha(HERE / filename) != expected:
            raise RuntimeError("pre-output evidence script drift")
    od = RUNTIME / "completion/mixed_h/od/B192_z3.5/ASSEMBLED_OD.npz"
    jvp = RUNTIME / "completion/mixed_derivative/B192_z3.5/ASSEMBLED.npz"
    if od.exists() or jvp.exists():
        raise RuntimeError("pre-existing direct z3.5 output")
    stage("OD", [PYTHON, "completion/mixed_h/od_run.py", "--n", "192", "--z", "3.5", "--workers", "1"], od, ledger)
    od_identity = json.loads(od.with_name("IDENTITY.json").read_text())
    od_results = json.loads(od.with_name("RESULTS.json").read_text())
    if (float(od_identity["z"]), od_identity["n"]) != (3.5, 192) or od_results["Hamiltonian_included"] is not False:
        raise RuntimeError("OD output identity/scope mismatch")
    stage("JVP", [PYTHON, "completion/mixed_derivative/run.py", "--z", "3.5", "--n", "192"], jvp, ledger)
    jvp_identity = json.loads(jvp.with_name("IDENTITY.json").read_text())
    if (float(jvp_identity["z"]), jvp_identity["n"]) != (3.5, 192):
        raise RuntimeError("JVP output identity mismatch")
    ledger["science_node_count"] = 1
    ledger["one_shot_state"] = "CONSUMED_OUTPUTS_COMPLETE"
    ledger["output_identity_verified_utc"] = now()
    write_ledger(ledger)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ONE_SHOT_STOP: {exc}", file=sys.stderr, flush=True)
        raise
