"""Reapply reviewed HE-EXP-DRIFT-02 observations without scientific execution.

Order: existing assembly, prior observation patches when applicable, then this
bounded patch. Existing independent CURRENT_STATUS observations are preserved.
Runtime recovery reconstructed this mechanical script; saved science was reused.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

STATUS_PATH = "status/HE_EXP_FINITE_DRIFT_20261027.json"
IDS = {"HE-EXCHANGE", "HE-EXP-PAIR", "HE-CLOSURE", "HE-EXP-CLOSURE"}
EXPECTED_OBSERVATION_SHA256 = "__OBSERVATION_SHA256__"
EXPECTED_TARGETS_SHA256 = "__TARGETS_SHA256__"
EXPECTED_NODE_IDS_SHA256 = "__NODE_IDS_SHA256__"
EXPECTED_TOP_SHA256 = "__TOP_SHA256__"


def formatted(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def target_structure(dag):
    return {n["id"]:{k:v for k,v in n.items() if k not in {"current_status", "status_observation"}} for n in dag["nodes"] if n["id"] in IDS}


def plan(node):
    return "\n".join(["# "+node["id"],"","Lead: "+node["lead_repo"],"",
        "Current status: `"+str(node["current_status"])+"`","",
        "Source: `"+node["source_file"]+"#"+node["json_pointer"]+"`","",
        "```json",json.dumps(node,ensure_ascii=False,indent=2),"```",""])


def status_rows(dag, current_rows):
    updates = {n["id"]:{k:n[k] for k in ("id","lead_repo","current_status","change_class","source_file","json_pointer")} | {"observation":n.get("status_observation")} for n in dag["nodes"] if n["id"] in IDS}
    if [r["id"] for r in current_rows] != [n["id"] for n in dag["nodes"]]:
        raise ValueError("Current status row mapping changed")
    return [copy.deepcopy(updates.get(r["id"],r)) for r in current_rows]


def apply(package):
    raw = (package/STATUS_PATH).read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_OBSERVATION_SHA256:
        raise ValueError("Reviewed source observation changed")
    observation = json.loads(raw)
    dag = json.loads((package/"DAG.json").read_text())
    if fingerprint([n["id"] for n in dag["nodes"]]) != EXPECTED_NODE_IDS_SHA256:
        raise ValueError("Reviewed node schema changed")
    if fingerprint({k:v for k,v in dag.items() if k != "nodes"}) != EXPECTED_TOP_SHA256:
        raise ValueError("Reviewed graph invariants changed")
    if fingerprint(target_structure(dag)) != EXPECTED_TARGETS_SHA256:
        raise ValueError("Reviewed target source schema/dependencies/invariants changed")
    if dag["global_physical_completion"] is not None or dag["L4_ready"] is not False:
        raise ValueError("Global claim ceiling changed")
    index = {n["id"]:n for n in dag["nodes"]}
    for identifier in sorted(IDS):
        n = index[identifier]
        value = observation["observations"][identifier]
        binding = {"source_file":STATUS_PATH,"json_pointer":"/observations/"+identifier,"value":copy.deepcopy(value)}
        previous = observation["previous_observations"][identifier]
        if n.get("status_observation") not in (previous,binding):
            raise ValueError("Apply prior observations first: "+identifier)
        if n["current_status"] not in (previous["value"]["current_scoped_state"],value["current_scoped_state"]):
            raise ValueError("Unexpected target status: "+identifier)
        n["current_status"] = value["current_scoped_state"]
        n["status_observation"] = binding
    current = json.loads((package/"status/CURRENT_STATUS.json").read_text())
    outputs = {"DAG.json":formatted(dag),"status/CURRENT_STATUS.json":formatted(status_rows(dag,current))}
    for identifier in sorted(IDS):
        outputs["contracts/"+identifier+".json"] = formatted(index[identifier])
        outputs["node_plans/"+identifier+".md"] = plan(index[identifier])
    for name,value in outputs.items():
        path = package/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package",type=Path,default=Path(__file__).resolve().parents[1])
    apply(parser.parse_args().package)
