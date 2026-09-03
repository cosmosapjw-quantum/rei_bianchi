#!/usr/bin/env python3
"""Independent standard-library verifier for REI host-epoch governance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED_LOCK = "d6702ccb6b66d0ac4324185a6eb43b0cbf5f58fee143c45771cf2d424aef87a7"


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def acyclic(nodes: list[str], edges: list[list[str]]) -> bool:
    outgoing = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}
    for source, target in edges:
        if source not in outgoing or target not in outgoing:
            return False
        outgoing[source].append(target)
        indegree[target] += 1
    queue = [node for node in nodes if indegree[node] == 0]
    seen = 0
    while queue:
        node = queue.pop()
        seen += 1
        for target in outgoing[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return seen == len(nodes)


def main() -> int:
    policy = load("HOST_EPOCH_REATTESTATION_POLICY.json")
    ledger = load("ATTEMPT_LINEAGE_LEDGER.json")
    lease = load("GLOBAL_ATTEMPT_LEASE_PROTOCOL.json")
    recovery = load("RUNTIME_RECOVERY_INPUTS.json")
    wolfram = load("WOLFRAM_DAG_RECEIPT.json")

    successor = policy["successor_environment_epoch"]
    actual_lock = hashlib.sha256(canonical(successor["semantic_toolchain_lock"])).hexdigest()
    if actual_lock != EXPECTED_LOCK or actual_lock != successor["semantic_toolchain_lock_sha256"]:
        raise SystemExit("SEMANTIC_TOOLCHAIN_LOCK_MISMATCH")
    if not acyclic(policy["dag"]["nodes"], policy["dag"]["edges"]):
        raise SystemExit("GOVERNANCE_DAG_CYCLE_OR_CLOSURE_FAILURE")
    if policy["historical_environment_epoch"]["may_be_reconstructed"]:
        raise SystemExit("HISTORICAL_RECEIPT_RECONSTRUCTION_FORBIDDEN")
    if ledger["next_attempt"]["remaining_attempts"] != 1 or ledger["next_attempt"]["retries_after_outcome"] != 0:
        raise SystemExit("ATTEMPT_BUDGET_MISMATCH")
    if lease["status"] != "DESIGNED_NOT_ACQUIRED" or lease["mutation_policy"]["update_allowed"] or lease["mutation_policy"]["delete_allowed"]:
        raise SystemExit("GLOBAL_LEASE_MUTATION_POLICY_INVALID")
    if recovery["compact_packet"]["artifact_id"] != 9877870910:
        raise SystemExit("COMPACT_PACKET_IDENTITY_MISMATCH")
    if wolfram["status"] != "PASS" or wolfram["authority_effect"] != "NONE":
        raise SystemExit("WOLFRAM_DAG_RECEIPT_INVALID")

    manifest = HERE / "MANIFEST.sha256"
    rows = [line for line in manifest.read_text(encoding="utf-8").splitlines() if line]
    for row in rows:
        digest, name = row.split("  ", 1)
        if name == "MANIFEST.sha256" or hashlib.sha256((HERE / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"MANIFEST_MISMATCH:{name}")

    print(json.dumps({
        "status": "PASS",
        "semantic_toolchain_lock_sha256": actual_lock,
        "historical_attempts": len(ledger["historical_attempts"]),
        "remaining_attempts": 1,
        "dag_nodes": len(policy["dag"]["nodes"]),
        "dag_edges": len(policy["dag"]["edges"]),
        "native_runtime": "NOT_RUN",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
