#!/usr/bin/env python3
"""Bounded planning consistency check; no source/root/history kernel is executed.

Required: --root-overlay, --previous-root-overlay, --phys12-core.
The saved result describes a planning snapshot, not scientific certification.
"""
import argparse
import hashlib
import json
import sys
import time
from decimal import Decimal
from pathlib import Path


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--root-overlay", type=Path, required=True)
    parser.add_argument("--previous-root-overlay", type=Path, required=True)
    parser.add_argument("--phys12-core", type=Path, required=True)
    args = parser.parse_args()
    base, root = args.plan_root, args.root_overlay
    start = time.perf_counter()
    checks = []

    def read(name):
        return json.loads((base / name).read_text())

    def check(name, condition, detail=None):
        checks.append({"id": name, "pass": bool(condition), "detail": detail})

    # Original inputs and retained science are compared as bytes, not recomputed.
    attachment = read("inputs/ATTACHMENT_MANIFEST.json")
    for item in attachment["files"]:
        data = (base / item["relative_path"]).read_bytes()
        check("attachment:" + item["relative_path"],
              len(data) == item["bytes"] and sha256(data) == item["sha256"])

    original = read("inputs/REI_ATOMIC_REUSE_DAG_20261012.json")
    global_nodes = {n["id"]: n for n in original["nodes"]}
    crosswalk = read("DAG_CROSSWALK.json")
    check("all_17_global_nodes_mapped", len(global_nodes) == 17 and
          {r["global_id"] for r in crosswalk["rows"]} == set(global_nodes))
    check("global_snapshot_preserved", all(
        row["original_title"] == global_nodes[row["global_id"]]["title"] and
        row["original_owner"] == global_nodes[row["global_id"]]["execution_owner"] and
        row["original_depends_on"] == global_nodes[row["global_id"]]["depends_on"] and
        row["original_status"] == global_nodes[row["global_id"]]["status"] == "PROPOSED_NOT_EXECUTED" and
        row["actual_global_completion_inferred"] is False
        for row in crosswalk["rows"]))

    dag = read("NEXT_DAG.json")
    nodes = {n["id"]: n for n in dag["nodes"]}
    check("eight_unique_local_nodes", len(nodes) == len(dag["nodes"]) == 8)
    check("typed_edge_references", all(
        set(n["depends_on"]) <= set(nodes) and
        set(n.get("external_dependencies", [])) <= set(global_nodes) and
        set(n.get("global_links", [])) <= set(global_nodes)
        for n in nodes.values()))
    remaining = {k: set(v["depends_on"]) for k, v in nodes.items()}
    order = []
    while remaining:
        ready = sorted(k for k, v in remaining.items() if not v)
        if not ready:
            break
        order.extend(ready)
        for k in ready:
            remaining.pop(k)
        for deps in remaining.values():
            deps.difference_update(ready)
    check("local_DAG_acyclic", not remaining, {"topological_order": order})
    check("actual_history_requires_RUX11", nodes["HH_MATCHED_HISTORY"]["external_dependencies"] == ["RUX11"])
    check("preparation_does_not_wait_for_RUX11", all(
        not nodes[k].get("external_dependencies")
        for k in ["HH_REUSE", "HH_EXPORT", "HH_DOMAIN_SCREEN", "HH_MATERIALITY"]))
    check("independent_HH_lanes_preserved", all(
        nodes[k].get("external_dependencies") == [] and
        nodes[k]["is_REI_baseline_prerequisite"] is False
        for k in ["HH_STRICT_NATIVE", "HH_SINGLET"]))
    check("global_baseline_no_optional_HH_gate",
          dag["global_critical_path_requires_HH_optional_completion"] is False and
          all("RUX14" not in global_nodes[k]["depends_on"] for k in original["main_critical_path"]))
    cards = [json.loads(line) for line in (base / "TASK_CARDS.jsonl").read_text().splitlines() if line]
    check("task_cards_match_DAG", len(cards) == 8 and {c["id"] for c in cards} == set(nodes) and
          all(all(c[k] == v for k, v in nodes[c["id"]].items()) for c in cards))

    retained = read("HH_RETAINED_RESULTS.json")
    check("PHYS12_identity", retained["commit"] == "dcea5dc6545736e6f4afa5acf4b7eabd428485e8" and
          retained["science_subtree"] == "ff2625c424a9c2e17af99d960fd6fcdda79227f9" and
          retained["science_decision"] == "PROMOTE_SCOPED")
    binding = read("evidence/LOCAL_BASELINE_GIT_BINDING.json")
    mismatches = []
    for item in binding["items"]:
        repo_path = item["repo_path"]
        prefix = retained["core_path"] + "/"
        p = (args.phys12_core / repo_path[len(prefix):]) if repo_path.startswith(prefix) else args.previous_root_overlay / repo_path
        data = p.read_bytes()
        if blob(data) != item["remote_git_blob"] or len(data) != item["remote_bytes"]:
            mismatches.append(repo_path)
    check("57_original_parent_files_unchanged", len(binding["items"]) == 57 and not mismatches, mismatches)
    copies = {
        "PHYS12_DECISION.json": "review/DECISION.json",
        "PHYS12_FROZEN_SOURCE_CONTRACT.json": "inputs/family/FROZEN_SOURCE_CONTRACT.json",
        "PHYS12_NCP_TASKS.json": "NCP_TASKS.json",
        "PHYS12_NEXT_DAG.json": "NEXT_DAG.json",
        "PHYS12_RESEARCH_STATE.json": "state/RESEARCH_STATE.json",
        "PHYS12_SUMMARY.json": "results/absolute_v1/SUMMARY.json",
    }
    check("six_PHYS12_baseline_copies_unchanged", all(
        (base / "baseline" / dst).read_bytes() == (args.phys12_core / src).read_bytes()
        for dst, src in copies.items()))
    check("two_previous_root_JSON_copies_unchanged", all(
        (base / "baseline" / ("PREVIOUS_ROOT_" + name)).read_bytes() == (args.previous_root_overlay / name).read_bytes()
        for name in ["CURRENT_DEVELOPMENT_PLAN.json", "RESEARCH_STATE.json"]))
    markers = {"AGENTS.md": "## Preserved execution contract",
               "README.md": "## Historical R31K-B/R31M native-lane guide",
               "README_KO.md": "## 아래 문서의 범위: 보존된 R31K-B/R31M native 안내",
               "docs/coding/IMPLEMENTATION_PLAN.md": "## Preserved R31K-B implementation plan — historical native lane"}
    check("four_historical_root_markdown_bodies_unchanged", all(
        (root / name).read_text().split(marker, 1)[1] ==
        (args.previous_root_overlay / name).read_text().split(marker, 1)[1]
        for name, marker in markers.items()))

    # Verify copied displays by decimal identity only; do not repeat FTC arithmetic.
    displays_ok = True
    for row in read("baseline/PHYS12_SUMMARY.json")["rows"]:
        display = retained["endpoints_outward_display_reused"][row["stage"]]
        for dst, source in [("D_x_HII", row["absolute"]["x_HII"]), ("D_w_eV_per_H", row["absolute"]["w"]),
                            ("I_x_HII_reused", row["mixed_reused"]["x_HII"]), ("I_w_eV_per_H_reused", row["mixed_reused"]["w"]),
                            ("r_x", row["modulation_over_absolute_at_b1"]["ionization_suppression"]),
                            ("r_w", row["modulation_over_absolute_at_b1"]["thermal_loss_reduction"])]:
            displays_ok &= list(map(Decimal, display[dst])) == list(map(Decimal, source["outward_decimal"]))
    check("copied_endpoint_display_identity_only", displays_ok)
    owners = read("contracts/HH_PROCESS_OWNER_ROWS.json")
    check("declared_event_nuclei_and_charge_balance", all(
        sum(row["stoichiometric_net"][k] for k in ["HI", "HII", "H_minus"]) == 0 and
        row["stoichiometric_net"]["HII"] - row["stoichiometric_net"]["H_minus"] - row["stoichiometric_net"]["free_electron"] == 0
        for row in owners["rows"] if "stoichiometric_net" in row))
    export = read("contracts/HH_REI_EXPORT_CONTRACT.json")
    request = read("contracts/HH_CONSUMER_REQUEST_TEMPLATE.json")
    policy = read("contracts/HH_OBSERVABLE_EFFECT_POLICY.json")
    state = read("state/RESEARCH_STATE.json")
    ncp = read("NCP_TASKS.json")
    check("no_consumer_or_effect_fabricated", export["consumer_admission"] is None and
          export["consumer_physical_history"] is None and request["actual_request_received"] is False and
          request["consumer_commit"] is None and policy["predeclared_threshold"] is None and
          state["consumer_bound"] is False and state["HH_effect_on_EoR"] is None and
          retained["global_RUX14_completed"] is False)
    check("scope_and_reuse_guards", export["coordinate_box_overlap_is_sufficient"] is False and
          export["stages_are_sequential"] is False and policy["cases_are_mandatory_new_runs"] is False and
          policy["no_current_omission_decision"] is True)
    check("no_new_science_or_heavy_job", all(state[k] == 0 for k in ["new_scientific_runs", "new_native_runs", "new_NCP_jobs"]) and
          state["new_global_RUX_PASS"] == dag["global_nodes_newly_completed"] == [] and
          state["heavy_queue"] == ncp["heavy_queue"] == dag["active_heavy_queue"] == [] and
          state["launch"] is ncp["launch"] is dag["active_launch"] is False)
    check("NCP_gates_scoped_by_lane", all(ncp["routes"][k]["required_REI_nodes"] == [] for k in ["FT03_NATIVE", "ATOMIC_MICROSCOPIC"]) and
          ncp["hardware_policy"]["measured_optimum"] is None)
    root_plan = json.loads((root / "CURRENT_DEVELOPMENT_PLAN.json").read_text())
    prefix = "research/r31ao_unequal_ladder/hh_atomic_reuse_plan_20261012_v2/"
    check("active_root_entry_paths_exist", all(root_plan[k].startswith(prefix) and
          (base / root_plan[k][len(prefix):]).is_file()
          for k in ["active_plan", "dag", "observable_contracts", "ncp_tasks", "handoff"]))
    check("root_PHYS12_baseline_consistent", root_plan["scientific_baseline"] == root_plan["current_scientific_baseline"] and
          root_plan["scientific_baseline"]["commit"] == retained["commit"])
    for node_id in ["HH_REUSE", "HH_EXPORT"]:
        check("prepared_artifacts_exist:" + node_id, all((base / p).is_file() for p in nodes[node_id]["artifact"]))
    result = {"schema": "hh_reuse_plan_structural_check.v1", "pass": all(c["pass"] for c in checks),
              "scope": "Planning structure, copy identity, declared event bookkeeping and entry paths only; no scientific kernel or external runtime admission",
              "new_scientific_runs": 0, "checks": checks, "wall_seconds": time.perf_counter() - start}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
