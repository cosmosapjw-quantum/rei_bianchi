#!/usr/bin/env python3
"""Read-only bounded DAG validator, readiness query, and single-node packet.

This tool does not execute commands, call models, or spawn agents. Paths in
contracts and state evidence are relative to --repo (default: this checkout).
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

STATUSES = {"READY", "PENDING", "IN_PROGRESS", "COMPLETED_REUSED", "COMPLETED", "ON_HOLD", "OPTIONAL_OFF"}
DONE = {"COMPLETED", "COMPLETED_REUSED"}
REQUIRED = {"id", "depends_on", "status", "owner_repo", "write_paths", "read_first", "commands", "outputs", "acceptance", "model_role", "activation"}


class ContractError(ValueError):
    pass


def strings(value, label, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ContractError(f"{label}: expected {'nonempty ' if nonempty else ''}list of nonempty strings")


def existing(paths, repo, label):
    strings(paths, label, nonempty=True)
    for path in paths:
        if not (repo / path).exists():
            raise ContractError(f"{label}: missing evidence {path}")


def load_contract(dag_path, repo, state_path=None):
    dag = json.loads(dag_path.read_text(encoding="utf-8"))
    if not isinstance(dag, dict) or not isinstance(dag.get("schema"), str) or not dag["schema"].strip() or not isinstance(dag.get("nodes"), list) or not dag["nodes"]:
        raise ContractError("DAG requires schema and nonempty nodes")
    nodes = {}
    for node in dag["nodes"]:
        if not isinstance(node, dict) or REQUIRED - node.keys():
            raise ContractError(f"node missing required fields: {sorted(REQUIRED - node.keys()) if isinstance(node, dict) else 'not an object'}")
        for key in ("id", "owner_repo", "model_role"):
            if not isinstance(node[key], str) or not node[key].strip():
                raise ContractError(f"{key}: expected nonempty string")
        nid = node["id"]
        if nid in nodes:
            raise ContractError(f"duplicate node: {nid}")
        if node["status"] not in STATUSES:
            raise ContractError(f"{nid}: unknown status")
        if not isinstance(node["activation"], bool):
            raise ContractError(f"{nid}: activation must be boolean")
        for key in ("depends_on", "write_paths", "read_first", "outputs"):
            strings(node[key], f"{nid}.{key}", nonempty=key == "outputs")
        acceptance = node["acceptance"]
        if not (isinstance(acceptance, str) and acceptance.strip()):
            strings(acceptance, f"{nid}.acceptance", nonempty=True)
        if not isinstance(node["commands"], list):
            raise ContractError(f"{nid}: commands must be argv vectors")
        for command in node["commands"]:
            strings(command, f"{nid}.commands", nonempty=True)
        requirements = node.get("external_requirements", [])
        if not isinstance(requirements, list):
            raise ContractError(f"{nid}: external_requirements must be list")
        for requirement in requirements:
            if isinstance(requirement, str) and requirement.strip():
                continue
            if not isinstance(requirement, dict) or not isinstance(requirement.get("resolved"), bool):
                raise ContractError(f"{nid}: external requirement requires string or object with boolean resolved")
            if requirement["resolved"]:
                existing(requirement.get("evidence"), repo, f"{nid}.external_requirements")
        nodes[nid] = node
    for nid, node in nodes.items():
        if len(set(node["depends_on"])) != len(node["depends_on"]):
            raise ContractError(f"{nid}: duplicate dependency")
        for dep in node["depends_on"]:
            if dep not in nodes:
                raise ContractError(f"{nid}: unknown dependency {dep}")
    seen, active = set(), set()

    def visit(nid):
        if nid in active:
            raise ContractError(f"cyclic dependency at {nid}")
        if nid in seen:
            return
        active.add(nid)
        for dep in nodes[nid]["depends_on"]:
            visit(dep)
        active.remove(nid)
        seen.add(nid)

    for nid in nodes:
        visit(nid)
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path else {"nodes": {}}
    if not isinstance(state, dict) or not isinstance(state.get("nodes"), dict):
        raise ContractError("state requires nodes object")
    for nid, record in state["nodes"].items():
        if nid not in nodes or not isinstance(record, dict) or record.get("status") not in STATUSES:
            raise ContractError(f"invalid state node/status: {nid}")
        if "evidence" in record:
            strings(record["evidence"], f"{nid}.evidence")
    statuses = {}
    for nid, node in nodes.items():
        record = state["nodes"].get(nid)
        status = record["status"] if record else node["status"]
        statuses[nid] = status
        if status in DONE:
            existing(node["outputs"], repo, f"{nid}.outputs")
            if record:
                existing(record.get("evidence"), repo, f"{nid}.evidence")
            elif status == "COMPLETED":
                existing(node.get("evidence"), repo, f"{nid}.evidence")
    return dag, nodes, statuses


def blockers(node, statuses):
    blocked = [f"dependency:{dep}:{statuses[dep]}" for dep in node["depends_on"] if statuses[dep] not in DONE]
    if not node["activation"]:
        blocked.append("activation:false")
    for requirement in node.get("external_requirements", []):
        if isinstance(requirement, str) or not requirement["resolved"]:
            blocked.append({"external_requirement": requirement})
    return blocked


def ready_nodes(nodes, statuses):
    return [{"id": nid, "owner_repo": n["owner_repo"], "model_role": n["model_role"], "status": statuses[nid], "write_paths": n["write_paths"]}
            for nid, n in nodes.items() if statuses[nid] in {"READY", "PENDING"} and not blockers(n, statuses)]


def packet(nid, nodes, statuses, repo):
    if nid not in nodes:
        raise ContractError(f"unknown node: {nid}")
    node = nodes[nid]
    context, remaining = [], 12000
    for source in node["read_first"]:
        path = repo / source
        item = {"path": source, "exists": path.is_file()}
        if path.is_file():
            raw = path.read_bytes()
            item["sha256"] = hashlib.sha256(raw).hexdigest()
            content = raw.decode("utf-8", errors="replace")
            budget = min(remaining, 4000)
            item["excerpt"] = content[:budget]
            item["excerpt_truncated"] = len(content) > budget
            item["read_full_source_required"] = True
            remaining -= len(item["excerpt"])
        context.append(item)
    return {"schema": "rux_codex_packet.v1", "node": node, "effective_status": statuses[nid],
            "eligible": statuses[nid] in {"READY", "PENDING"} and not blockers(node, statuses),
            "blockers": blockers(node, statuses), "dependency_status": {d: statuses[d] for d in node["depends_on"]},
            "required_context": context,
            "return_contract": {"node_id": nid, "required_outputs": node["outputs"], "acceptance_verbatim": node["acceptance"],
                "report": ["actual executor identity if observed; requested identity separately", "owned paths and observed diff", "commands and exit codes", "evidence paths", "failures and unresolved inputs", "scientific admission remains with authorized reviewer"],
                "completed_state_requires": "Existing output artifacts and nonempty existing evidence paths; status text is not proof"},
            "execution": "READ_ONLY: no commands executed; no models called; no agents spawned"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dag", required=True, type=Path)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "ready", "packet"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--state", type=Path)
        if name == "packet":
            cmd.add_argument("node")
    args = parser.parse_args(argv)
    try:
        dag, nodes, statuses = load_contract(args.dag, args.repo, args.state)
        if args.command == "check":
            result = {"schema": dag["schema"], "valid": True, "node_count": len(nodes), "agents_spawned": 0}
        elif args.command == "ready":
            result = {"ready": ready_nodes(nodes, statuses), "agents_spawned": 0}
        else:
            result = packet(args.node, nodes, statuses, args.repo)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ContractError, OSError, ValueError, TypeError) as exc:
        print(f"contract error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
