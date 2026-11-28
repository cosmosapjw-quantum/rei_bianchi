#!/usr/bin/env python3
"""Optional structural identity check for the 2026-11-01 IGM routing overlay.

No physics acceptance, deployment approval, live status mutation or CI gate.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "docs/strategy_igm_20261101/DAG_OVERLAY.json"

def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def check(root: Path = ROOT) -> str:
    overlay = json.loads((root / "docs/strategy_igm_20261101/DAG_OVERLAY.json").read_text())
    src_meta = overlay["authority"]["predecessor_rux"]
    data = (root / src_meta["path"]).read_bytes()
    assert git_blob_sha(data) == src_meta["git_blob"], "RUX original input changed; inspect before editing overlay"
    source = json.loads(data)
    expected = [{
        "id": n["id"], "depends_on": n["depends_on"],
        "optional": n["optional"], "execution_owner": n["execution_owner"]
    } for n in source["nodes"]]
    actual = overlay["rux_graph"]
    assert len(actual) == len(expected) == 17, "RUX node count changed"
    assert actual == expected, "RUX node identity/dependency/owner/optional flag altered"
    lookup = {n["id"]: n for n in actual}
    assert len(lookup) == len(actual), "Duplicate RUX IDs"
    mandatory = set(overlay["routing"]["core_path"])
    assert mandatory <= set(lookup), "Unknown core nodes"
    assert all(not lookup[x]["optional"] for x in mandatory), "Optional work promoted into core path"
    assert all(lookup[x]["optional"] for x in overlay["routing"]["optional_when_relevant"]), "Nonoptional node parked"
    assert not overlay["routing"]["baseline_is_not_blocked_by_optional_precision"] is False
    for node in actual:
        assert all(dep in lookup for dep in node["depends_on"]), "Missing dependency"
    temp, done = set(), set()
    def visit(x: str) -> None:
        if x in done: return
        assert x not in temp, "Cycle introduced"
        temp.add(x)
        for y in lookup[x]["depends_on"]: visit(y)
        temp.remove(x); done.add(x)
    for name in lookup: visit(name)
    assert overlay["status"] == "PROSPECTIVE_ROUTING_ONLY_NOT_PHYSICAL_ADMISSION"
    assert overlay["baseline_reported_not_recounted"]["canonical_physical_delta"] == 0
    assert overlay["immutable_constraints"]["no_canonical_promotion_from_overlay"]
    assert overlay["immutable_constraints"]["auto_next_node"] is False
    return "PASS: source-exact 17-node RUX identity, DAG acyclicity, priority/optional separation, zero canonical promotion"

if __name__ == "__main__":
    print(check())
