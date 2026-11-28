#!/usr/bin/env python3
"""Read-only independent handoff-schema and exact corollary check.

No evaluator is imported or run. Read-field expressions are contract paths,
not general executable code. All arithmetic below is exact rational arithmetic.
"""
from pathlib import Path
from fractions import Fraction as F
import ast
import hashlib
import json
import re
import time
from datetime import datetime, timezone

CORE = Path(__file__).resolve().parents[2]
WORK = CORE.parent


def identity(p):
    b = p.read_bytes()
    return {"path": str(p.relative_to(WORK)), "bytes": len(b),
            "sha256": hashlib.sha256(b).hexdigest()}


def resolve(data, expression):
    nodes = [data]
    for token in expression.split("."):
        m = re.fullmatch(r"([^\[]+)(?:\[([^\]]+)\])?", token)
        assert m, expression
        key, selector = m.groups()
        got = []
        for node in nodes:
            assert isinstance(node, dict) and key in node, expression
            item = node[key]
            if selector is None:
                got.append(item)
            elif selector == "*":
                assert isinstance(item, (list, dict)), expression
                got.extend(item.values() if isinstance(item, dict) else item)
            else:
                field, value = selector.split("=", 1)
                assert isinstance(item, list), expression
                got.extend(v for v in item if v[field] == value)
        assert got, expression
        nodes = got
    return len(nodes)


def pair(raw):
    return tuple(F(int(raw[k][0]), int(raw[k][1])) for k in ("lo", "hi"))


def main():
    start = time.perf_counter()
    contract = CORE / "theory/CURVATURE_CONTRACT_DRAFT.json"
    d = json.loads(contract.read_text())
    checks = []
    for b in d["input_bindings"]:
        p = WORK / b["path"]
        ident = identity(p)
        assert ident["bytes"] == b["bytes"] and ident["sha256"] == b["sha256"], b["path"]
        fields = []
        if p.suffix == ".json":
            raw = json.loads(p.read_text())
            fields = [{"field": x, "resolved_nodes": resolve(raw, x)} for x in b["read_fields"]]
        elif p.name == "phys14_advance.py":
            tree = ast.parse(p.read_text())
            names = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
            for x in b["read_fields"]:
                assert x in names, x
                fields.append({"symbol": x, "declared": True})
        else:
            fields = [{"descriptive_text_locator": x, "review": "manually read"} for x in b["read_fields"]]
        checks.append({**ident, "identity_matches": True, "fields": fields})

    corpath = CORE / "theory/MIXED_RESPONSE_COROLLARIES.json"
    c = json.loads(corpath.read_text())
    r = json.loads((CORE / "checks/application/run02/results/MIXED_RESPONSE_RESULTS.json").read_text())
    for b in c["inputs"]:
        ident = identity(WORK / b["path"])
        assert all(ident[k] == b[k] for k in ("bytes", "sha256"))
    assert c["derivative"]["exact"] == r["DeltaT_mixed_intersection_K"]["exact"]
    assert c["four_corner_interaction"]["exact"] == r["four_corner_interaction_K"]["exact"]
    assert [g["exact"] for g in c["mixed_gas_defect"]] == [g["exact"] for g in r["d_mixed_intersection"]]
    lo, hi = pair(c["derivative"]["exact"])
    dlo, dhi = map(F, c["derivative"]["outward_decimal"])
    assert dlo <= lo <= hi <= dhi < 0
    a = c["anchored_axis_reconstruction"]
    cm = F(*map(int, a["cross_coefficient_exact_from_outward_endpoints"]))
    rm = F(*map(int, a["cross_remainder_radius_exact_from_outward_endpoints"]))
    assert cm == (dlo + dhi) / 2 == F(a["cross_coefficient_decimal_K"])
    assert rm == (dhi - dlo) / 2 == F(a["cross_remainder_radius_decimal_K"])
    assert cm-rm <= lo <= hi <= cm+rm
    assert d["current_execution_state"]["pure_response_application"] == "not_run"
    out = {
        "schema": "WU088_HH_PHYS18_INDEPENDENT_SUCCESSOR_BINDING_CHECK_V1",
        "status": "PASS", "contract": identity(contract),
        "binding_count": len(checks), "checks": checks,
        "corollary": identity(corpath),
        "exact_corollary_identities": "mixed derivative, interaction and four gas components equal production raw rational intervals",
        "outward_decimal_and_anchor_midpoint_radius": "PASS",
        "pure_curvature_application": "not_run",
        "new_source_calls": 0, "root_solves": 0, "history_replays": 0,
        "elapsed_seconds": time.perf_counter()-start,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
    }
    target = CORE / "checks/independent/SUCCESSOR_BINDING_CHECK.json"
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps({"status": out["status"], "bindings": len(checks),
                      "elapsed_seconds": out["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
