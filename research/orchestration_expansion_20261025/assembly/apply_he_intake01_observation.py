"""Reapply the frozen HE-EXP-INTAKE-01 wrapper observation after graph assembly.

Run: python research/orchestration_expansion_20261025/assembly/apply_he_intake01_observation.py
Only five wrapper current_status/status_observation values and their existing
rendered views are updated. Original scientific contracts and gates are retained.
"""
import argparse
import copy
import json
from pathlib import Path

OBSERVATION_PATH = "status/HE_EXP_INTAKE01_20261025.json"
STATES = {
    "HE-EXCHANGE": "SOURCE_INTAKE_AND_CONDITIONAL_IMPLEMENTATION_VERIFIED_PHYSICAL_BINDING_PENDING",
    "HE-EXP-PAIR": "SOURCE_INTAKE_AND_CONDITIONAL_IMPLEMENTATION_VERIFIED_PHYSICAL_BINDING_PENDING",
    "HE-RESERVOIR": "CONDITIONAL_OWNERSHIP_IMPLEMENTATION_VERIFIED_PHYSICAL_INPUT_PENDING",
    "HE-CLOSURE": "CONDITIONAL_OWNERSHIP_IMPLEMENTATION_VERIFIED_PHYSICAL_INPUT_PENDING",
    "HE-EXP-CLOSURE": "CONDITIONAL_OWNERSHIP_IMPLEMENTATION_VERIFIED_PHYSICAL_INPUT_PENDING",
}


def text(value):
    return json.dumps(value, ensure_ascii=False, indent=2)


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text(value) + "\n")


def plan(node):
    return "\n".join([
        "# " + node["id"], "", "Lead: " + node["lead_repo"], "",
        "Current status: `" + str(node["current_status"]) + "`", "",
        "Source: `" + node["source_file"] + "#" + node["json_pointer"] + "`", "",
        "```json", text(node), "```", "",
    ])


def status_rows(dag):
    return [
        {key: node[key] for key in (
            "id", "lead_repo", "current_status", "change_class",
            "source_file", "json_pointer",
        )} | {"observation": node.get("status_observation")}
        for node in dag["nodes"]
    ]


def apply(package):
    dag = json.loads((package / "DAG.json").read_text())
    observation = json.loads((package / OBSERVATION_PATH).read_text())
    if observation["unit_id"] != "HE-EXP-INTAKE-01":
        raise ValueError("Unexpected observation unit")
    if set(observation["observations"]) != set(STATES):
        raise ValueError("Unexpected observation node set")
    index = {node["id"]: node for node in dag["nodes"]}
    if len(index) != 87 or len(dag["nodes"]) != 87:
        raise ValueError("Expected the frozen 87-node graph")
    for identifier, state in STATES.items():
        node = index[identifier]
        value = observation["observations"][identifier]
        if node["lead_repo"] != "cosmosapjw-quantum/BASS_HE":
            raise ValueError("Unexpected lead repository: " + identifier)
        if value["current_scoped_state"] != state:
            raise ValueError("Unexpected scoped state: " + identifier)
        node["current_status"] = state
        node["status_observation"] = {
            "source_file": OBSERVATION_PATH,
            "json_pointer": "/observations/" + identifier,
            "value": copy.deepcopy(value),
        }
    dump(package / "DAG.json", dag)
    for identifier in STATES:
        node = index[identifier]
        dump(package / "contracts" / (identifier + ".json"), node)
        target = package / "node_plans" / (identifier + ".md")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(plan(node))
    dump(package / "status/CURRENT_STATUS.json", status_rows(dag))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    apply(args.package)

