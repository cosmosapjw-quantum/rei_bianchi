"""Stage the root-admitted selected REC-COUPLED observation, without touching originals.

The frozen canonical files are inputs. Run only after the root has written the
unit admission and independent review; this is a mechanical, additive mapper.
It writes under this unit's canonical_updates, never to the live canonical tree.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path


UNIT = Path(__file__).resolve().parents[1]
ROOT = UNIT.parents[2]
CANONICAL = Path("research/orchestration_expansion_20261025")
BASE = UNIT / "intake/canonical_base"
STAGED = UNIT / "canonical_updates" / CANONICAL
DAG_SHA256 = "8b93c017fa2da46f06ac4637fa85c2c61e8f2abe8cba85b6f648838499a2abf7"
STATUS_SHA256 = "b6feead1895a72d2b4e405c2a236a5ecb6fe5acc3f7c45e4ecba4c95dd7c1ca3"
CONTRACT_SHA256 = "56f06bb07ca8589d0bbfefef9613d78223603d2b661d9ee482cdc75e6a11b704"
PLAN_SHA256 = "19752543ad8ab04f1746910bfd4e427d3f79111cc784dba9dbcf257eaf1dfd1a"
NODE = "REC-COUPLED"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def one_node(items: list, node_id: str) -> dict:
    matches = [item for item in items if item.get("id") == node_id]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {node_id}, got {len(matches)}")
    return matches[0]


def stage(admission: Path, review: Path, raw: Path, receipt: Path) -> dict:
    for name, expected in (("DAG.json", DAG_SHA256),
                           ("status/CURRENT_STATUS.json", STATUS_SHA256),
                           ("contracts/REC-COUPLED.json", CONTRACT_SHA256),
                           ("node_plans/REC-COUPLED.md", PLAN_SHA256)):
        base = BASE / name
        live = ROOT / CANONICAL / name
        if sha(base) != expected or (live.is_file() and sha(live) != expected):
            raise ValueError(f"Frozen 413729 canonical identity mismatch: {name}")
    failed_stderr = UNIT / "implementation/attempt01/stderr.log"
    failed_receipt = UNIT / "implementation/attempt01/RESOURCE_RECEIPT.json"
    runner_stderr = UNIT / "implementation/attempt02/stderr.log"
    runner_receipt = UNIT / "implementation/attempt02/RESOURCE_RECEIPT.json"
    for path in (admission, review, raw, receipt, failed_stderr, failed_receipt, runner_stderr, runner_receipt):
        if not path.is_file():
            raise ValueError(f"Missing root-reviewed evidence: {path}")
        rel(path)
    decision = json.loads(admission.read_text())
    if decision.get("REC-COUPLED") != "CONSTRUCTIVE_PARTIAL_SELECTED_NATIVE_PW19_PREASSIMILATION_SOURCE":
        raise ValueError("Root admission must explicitly authorize the exact selected partial status")

    dag = json.loads((BASE / "DAG.json").read_text())
    status = json.loads((BASE / "status/CURRENT_STATUS.json").read_text())
    contract = json.loads((BASE / "contracts/REC-COUPLED.json").read_text())
    plan = (BASE / "node_plans/REC-COUPLED.md").read_text()
    dag_before = copy.deepcopy(dag)
    status_before = copy.deepcopy(status)
    node = one_node(dag["nodes"], NODE)
    row = one_node(status, NODE)
    if node != contract or node["current_status"] != "INPUT_DEPENDENT_NOT_SCHEDULED":
        raise ValueError("Exact standalone contract and embedded frozen DAG wrapper differ")
    if node["runnable"] is not False or node["pr_plan"]["units"]["value"] is not None or node["pr_plan"]["outputs"]["value"] is not None or node["pr_plan"]["PR_boundary"]["value"] is not None:
        raise ValueError("Original readiness guard unexpectedly changed")
    if row["observation"] is not None:
        raise ValueError("Existing REC-COUPLED observation requires root reconciliation")

    evidence = {"admission": rel(admission), "independent_review": rel(review),
                "raw_result": rel(raw), "run_receipt": rel(receipt),
                "original_scientific_check_failed_stderr": rel(failed_stderr),
                "original_scientific_check_failed_receipt": rel(failed_receipt),
                "runner_precheck_failed_stderr": rel(runner_stderr),
                "runner_precheck_failed_receipt": rel(runner_receipt)}
    observation = {
        "unit": "REI-COUPLED-SOURCE-20261027",
        "decision": "CONSTRUCTIVE_PARTIAL_SELECTED_NATIVE_PW19_PREASSIMILATION_SOURCE",
        "scope": "Native PW19 HeII photo component at the saved z=2.479 donor snapshot; baryon-normalized 21-species source and nonthermal electron count/energy with signed external photon ledger, local JVP and pre-assimilation thermal diagnostic.",
        "evidence": evidence,
        "sha256": {key: sha(ROOT / path) for key, path in evidence.items()},
        "claim_limit": "Original REC-COUPLED gate remains open for selected-source thermal kinetics, physical uncertainty/error allocation and convergence; REC-EXP-COUPLED, L4 and all-selected physical pilot remain open. Count 32/88 unchanged.",
    }
    runtime = {
        "unit": observation["unit"],
        "qualification": "SELECTED_RUNTIME_SCOPE_ONLY; ORIGINAL_SOURCE_PR_PLAN_UNCHANGED",
        "inputs": "Admitted PW19 HeII photo moments, native 21-state matched z=2.479 donor snapshot, positive nb and T; zero-initial selected increment reservoirs; fixed prescribed H for optional eta clock.",
        "units": {"Y_and_zeta": "per baryon", "w_nt_and_w_ext": "J per baryon", "time": "proper s", "number_source": "m^-3 s^-1", "power_source": "J m^-3 s^-1", "logT_source": "s^-1"},
        "outputs": ["native photo particle/electron source and local JVP", "primary nonthermal energy and signed external photon ledger", "source-specific zero thermal-count and log-temperature contribution before assimilation", "isotropic primary pressure-source interval diagnostic"],
        "PR_boundary": "research/rei_expanded_event_consumer/coupled_source_20261027/** plus additive REC-COUPLED canonical observation/selectedRuntimeContract and scoped return; no other nodes or original source fields",
        "domain_and_limits": "See theory/CONTRACT.md; this selected runtime scope does not provide a full thermal/history state or an IVP.",
        "evidence": evidence,
    }
    node["current_status"] = observation["decision"]
    node["status_observation"] = observation
    node["selectedRuntimeContract"] = runtime
    row["current_status"] = observation["decision"]
    row["observation"] = observation
    contract["current_status"] = observation["decision"]
    contract["status_observation"] = observation
    contract["selectedRuntimeContract"] = runtime
    if contract != node:
        raise AssertionError("Standalone contract and DAG selected wrapper diverged")
    status_line = "Current status: `INPUT_DEPENDENT_NOT_SCHEDULED`"
    if plan.count(status_line) != 1:
        raise ValueError("Frozen node plan current-status line changed")
    plan = plan.replace(status_line, f"Current status: `{observation['decision']}`", 1)
    plan += ("\n## Selected runtime observation, 2026-10-27\n\n"
             f"Decision: `{observation['decision']}`. This is a constructive selected-source partial at the saved native PW19 He II snapshot. "
             "The original JSON source contract in the fenced block above, its missing fields and `runnable=false` remain unchanged; "
             "the additive selected runtime contract is in this plan's corresponding standalone JSON and DAG wrapper. "
             "The original REC-COUPLED gate, REC-EXP-COUPLED, L4 and full physical pilot remain open; canonical count is 32/88.\n\n"
             "Reviewed evidence:\n\n" + "".join(f"- `{key}`: `{value}` (SHA-256 `{observation['sha256'][key]}`)\n"
                                                    for key, value in evidence.items()) +
             f"\nScoped owner return: `{CANONICAL / 'returns/REI_COUPLED_SOURCE_20261027.json'}`.\n")

    # No other node, original contract, nested PR plan, edge, gate or readiness field may move.
    before_node = one_node(dag_before["nodes"], NODE)
    if {k: v for k, v in node.items() if k not in ("current_status", "status_observation", "selectedRuntimeContract")} != {k: v for k, v in before_node.items() if k != "current_status"}:
        raise AssertionError("Original REC-COUPLED fields changed")
    before_row = one_node(status_before, NODE)
    if {k: v for k, v in row.items() if k not in ("current_status", "observation")} != {k: v for k, v in before_row.items() if k not in ("current_status", "observation")}:
        raise AssertionError("Original status fields changed")
    for a, b in zip(dag["nodes"], dag_before["nodes"]):
        if a["id"] != NODE and a != b:
            raise AssertionError(f"Unrelated DAG node changed: {a['id']}")
    for a, b in zip(status, status_before):
        if a["id"] != NODE and a != b:
            raise AssertionError(f"Unrelated status row changed: {a['id']}")
    if len(dag["nodes"]) != 88 or len(status) != 88 or dag["global_physical_completion"] != dag_before["global_physical_completion"] or dag["L4_ready"] != dag_before["L4_ready"]:
        raise AssertionError("Global DAG count/claim changed")

    for name, obj in (("DAG.json", dag), ("status/CURRENT_STATUS.json", status),
                      ("contracts/REC-COUPLED.json", contract)):
        target = STAGED / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    target = STAGED / "node_plans/REC-COUPLED.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(plan)
    return {"staged": [str(STAGED / "DAG.json"), str(STAGED / "status/CURRENT_STATUS.json")],
            "changed_node": NODE, "unchanged_node_count": 87, "count": "32/88", "original_runnable": False,
            "standalone_contract_and_plan": [str(STAGED / "contracts/REC-COUPLED.json"), str(target)]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admission", type=Path, default=UNIT / "ADMISSION.json")
    parser.add_argument("--review", type=Path, default=UNIT / "review/VALIDATION.json")
    parser.add_argument("--raw", type=Path, default=UNIT / "implementation/attempt03/stdout.json")
    parser.add_argument("--receipt", type=Path, default=UNIT / "implementation/attempt03/RESOURCE_RECEIPT.json")
    args = parser.parse_args()
    print(json.dumps(stage(args.admission, args.review, args.raw, args.receipt), indent=2))
