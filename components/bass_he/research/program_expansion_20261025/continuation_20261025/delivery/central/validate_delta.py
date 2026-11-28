"""One bounded mechanical validation of the prescribed central status delta."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "base"
RESULT = ROOT / "result"
PREFIX = "research/orchestration_expansion_20261025/"
IDS = {
    "HE-EXCHANGE", "HE-EXP-PAIR", "HE-RESERVOIR",
    "HE-CLOSURE", "HE-EXP-CLOSURE",
}


def load(path):
    return json.loads(path.read_text())


def blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def formatted(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def pointer(document, path):
    value = document
    for token in path.strip("/").split("/"):
        value = value[token.replace("~1", "/").replace("~0", "~")]
    return value


metadata = load(ROOT / "BASE_METADATA.json")
assert blob(BASE / "DAG.json") == metadata["dag_blob"] == "b6ecc8cd9285e772e8649afe0155fc22a2256f37"
assert blob(BASE / "AGENTS.md") == metadata["agents_blob"]
assert blob(BASE / "assembly/assemble.py") == metadata["assembly_blob"]
before, after = load(BASE / "DAG.json"), load(RESULT / "DAG.json")
assert before.keys() == after.keys()
assert {k: v for k, v in before.items() if k != "nodes"} == {k: v for k, v in after.items() if k != "nodes"}
assert len(before["nodes"]) == len(after["nodes"]) == 87
assert [n["id"] for n in before["nodes"]] == [n["id"] for n in after["nodes"]]
old = {n["id"]: n for n in before["nodes"]}
new = {n["id"]: n for n in after["nodes"]}
changed = {k for k in old if old[k] != new[k]}
assert changed == IDS
observation = load(RESULT / "status/HE_EXP_INTAKE01_20261025.json")
assert set(observation["observations"]) == IDS
changed_fields = {}
for identifier in IDS:
    a, b = old[identifier], new[identifier]
    fields = {key for key in a.keys() | b.keys() if a.get(key) != b.get(key)}
    assert fields == {"current_status", "status_observation"}
    changed_fields[identifier] = sorted(fields)
    assert a["lead_repo"] == b["lead_repo"] == "cosmosapjw-quantum/BASS_HE"
    binding = b["status_observation"]
    assert binding["source_file"] == "status/HE_EXP_INTAKE01_20261025.json"
    assert binding["json_pointer"] == "/observations/" + identifier
    assert binding["value"] == pointer(observation, binding["json_pointer"])
    assert b["current_status"] == binding["value"]["current_scoped_state"]
    assert b["contract"] == a["contract"]
    assert b["source_fields"] == a["source_fields"]
    assert b["pr_plan"] == a["pr_plan"]
    assert ("runnable" in b) == ("runnable" in a)
    assert b.get("runnable") == a.get("runnable")
    assert b["claim_gate"] == a["claim_gate"]
    assert b["budget_status"] == a["budget_status"]
    assert b["dependencies"] == a["dependencies"]
    assert b["conditional_dependencies"] == a["conditional_dependencies"]
assert old["HE101-EXPORT"] == new["HE101-EXPORT"]
assert old["HE-EXP-SPECIES"] == new["HE-EXP-SPECIES"]
assert after["global_physical_completion"] is None
assert after["L4_ready"] is False
facts = observation["source_intake"]
assert facts["consumer_rows"] == {
    "total": 32, "atomic_charge": 20, "neutron": 1,
    "electron_pools": 2, "synthetic_witnesses": 9, "physical_promotion": False,
}
assert facts["scalar_provider_records"] == {"total": 18, "PI": 6, "RR": 6, "CI": 6}
assert facts["implementation_validation"]["actual_process_outcomes"] == ["PASS", "PASS", "PASS", "FAIL", "PASS"]
assert facts["physical_provider_admitted"] is False
assert facts["production_status"] == "NOT_APPROVED"
assert facts["activation"] is False
assert facts["physical_allocation"] == "UNALLOCATED"
assert facts["implementation_validation"]["execution_resources"]["end_to_end_cap_claimed"] is False
spec = importlib.util.spec_from_file_location("delta_apply", RESULT / "assembly/apply_he_intake01_observation.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert (BASE / "status/CURRENT_STATUS.json").read_text() == formatted(module.status_rows(before))
assert (BASE / "contracts/HE-EXCHANGE.json").read_text() == formatted(old["HE-EXCHANGE"])
assert (BASE / "node_plans/HE-EXCHANGE.md").read_text() == module.plan(old["HE-EXCHANGE"])
for identifier in IDS:
    assert (RESULT / "contracts" / (identifier + ".json")).read_text() == formatted(new[identifier])
    assert (RESULT / "node_plans" / (identifier + ".md")).read_text() == module.plan(new[identifier])
assert (RESULT / "status/CURRENT_STATUS.json").read_text() == formatted(module.status_rows(after))
before_status = load(BASE / "status/CURRENT_STATUS.json")
after_status = load(RESULT / "status/CURRENT_STATUS.json")
assert {a["id"] for a, b in zip(before_status, after_status) if a != b} == IDS
expected = {
    "DAG.json", "status/HE_EXP_INTAKE01_20261025.json",
    "status/CURRENT_STATUS.json", "assembly/apply_he_intake01_observation.py",
} | {"contracts/" + i + ".json" for i in IDS} | {"node_plans/" + i + ".md" for i in IDS}
actual = {str(p.relative_to(RESULT)) for p in RESULT.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
assert actual == expected
payload = [
    {"path": PREFIX + name, "mode": "100644", "type": "blob", "content": (RESULT / name).read_text()}
    for name in sorted(expected)
]
(ROOT / "tree_elements.json").write_text(formatted(payload))
summary = {
    "status": "PASS",
    "scope": "mechanical_delta_only",
    "validation_runs": 2,
    "first_attempt": "VALIDATION_SCRIPT_KEYERROR_MISSING_OPTIONAL_RUNNABLE_KEY; payload unchanged; assertion corrected to preserve presence and value",
    "base_head": metadata["fetched_head"],
    "base_dag_blob": metadata["dag_blob"],
    "nodes": 87,
    "changed_nodes": sorted(IDS),
    "changed_fields_by_node": changed_fields,
    "unchanged_nodes": 82,
    "historical_snapshot_unchanged": True,
    "top_level_except_nodes_unchanged": True,
    "all_source_contracts_and_pointers_unchanged": True,
    "all_claim_gates_budgets_runnable_pr_plans_source_fields_unchanged": True,
    "topology_unchanged": True,
    "HE101_EXPORT_and_WU_owned_HE_EXP_SPECIES_unchanged": True,
    "observation_pointers_and_values_match": True,
    "contracts_and_node_plan_views_match": True,
    "CURRENT_STATUS_non_target_rows_unchanged": True,
    "original_assembler_unchanged": True,
    "global_physical_completion": None,
    "L4_ready": False,
    "scientific_tests_or_assembler_run": False,
    "payload_files": len(payload),
    "result_dag_sha256": sha256(RESULT / "DAG.json"),
    "reapply_command": "python research/orchestration_expansion_20261025/assembly/apply_he_intake01_observation.py",
    "file_sha256": {name: sha256(RESULT / name) for name in sorted(expected)},
    "publication_performed": False,
}
(ROOT / "DELTA_VALIDATION.json").write_text(formatted(summary))
print(json.dumps({"status": "PASS", "nodes": 87, "changed_nodes": sorted(IDS), "changed_fields": ["current_status", "status_observation"], "payload_files": len(payload), "scientific_tests_or_assembler_run": False}, indent=2))

