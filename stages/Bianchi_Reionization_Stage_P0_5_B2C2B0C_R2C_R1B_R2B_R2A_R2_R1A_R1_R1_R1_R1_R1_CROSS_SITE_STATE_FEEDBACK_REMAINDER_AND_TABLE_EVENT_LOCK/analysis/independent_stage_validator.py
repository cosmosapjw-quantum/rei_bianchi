#!/usr/bin/env python3
"""Independent replay of sealed cross-site stage evidence.

This validator does not import the interval-map implementation.  It checks the
machine-readable results, exact structural identities, containment, refinement,
event restart, and all locked promotion gates.
"""
from __future__ import annotations
from decimal import Decimal, getcontext
import json
from pathlib import Path

STAGE = Path(__file__).resolve().parents[1]
DATA = STAGE / "data"
getcontext().prec = 80


def read(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def main() -> int:
    three = read("THREE_LANE_INTERVAL_MAP.json")
    part = read("PARTITION_SENSITIVITY.json")
    exact = read("EXACT_SYMBOLIC_VALIDATION.json")
    contain = read("CONTAINMENT_AUDIT.json")
    event = read("TABLE_EVENT_RESTART_AUDIT.json")
    plots = read("PLOT_SUMMARY.json")

    failures: list[str] = []
    gate_width = Decimal("0.002")
    gate_error = Decimal("0.0002")

    if not exact.get("passed"):
        failures.append("exact structural validator failed")
    for key, value in exact.get("identities", {}).items():
        vals = value if isinstance(value, list) else [value]
        if key.endswith("residual") or key.endswith("residuals") or "identity" in key:
            if any(Decimal(str(x)) != 0 for x in vals):
                failures.append(f"nonzero exact identity: {key}")

    rows = three.get("rows", [])
    if len(rows) != 3 or not three.get("all_certified"):
        failures.append("three-lane certification failed")
    max_width = max(Decimal(str(v)) for v in three.get("max_widths", {}).values())
    max_local = Decimal(str(three.get("maximum_validated_local_error")))
    if not max_width < gate_width:
        failures.append("public width gate failed")
    if not max_local < gate_error:
        failures.append("validated local-error gate failed")
    for row in rows:
        if row.get("classification") != "PASS" or not row.get("certified"):
            failures.append(f"lane not PASS: {row.get('lane')}")
        if row.get("table_event", {}).get("any_event"):
            failures.append(f"unexpected table event: {row.get('lane')}")
        for name, interval in row.get("set_ledgers", {}).items():
            lo, hi = map(Decimal, map(str, interval))
            if not (lo <= 0 <= hi):
                failures.append(f"raw ledger misses zero: {row.get('lane')}:{name}")

    if part.get("acceptance_pattern") != {"1024": False, "2048": True, "4096": True}:
        failures.append("partition acceptance pattern changed")
    if not part.get("all_maps_enclosed") or not part.get("monotone_local_error"):
        failures.append("partition map/local-error gate failed")
    if not all(part.get("monotone_widths", {}).values()):
        failures.append("partition widths are not monotone")

    if not contain.get("all_contained"):
        failures.append("stored evidence containment failed")
    for row in contain.get("rows", []):
        if row.get("direct_stagewise_endpoint", {}).get("outside_count") != 0:
            failures.append(f"stagewise witness outside: {row.get('lane')}")
        if row.get("static_lower", {}).get("outside_count") != 0:
            failures.append(f"static lower outside: {row.get('lane')}")
        if row.get("static_upper", {}).get("outside_count") != 0:
            failures.append(f"static upper outside: {row.get('lane')}")
        if any(x.get("outside_count") != 0 for x in row.get("primary_interior", [])):
            failures.append(f"interior sample outside: {row.get('lane')}")

    if not event.get("passed") or not event.get("between_site_crossing_detected"):
        failures.append("table-event/restart audit failed")
    for direction in ("increasing_localization", "decreasing_localization"):
        item = event.get(direction, {})
        if not item.get("certified") or not item.get("parent_unchanged"):
            failures.append(f"transactional localization failed: {direction}")

    expected_ratios = {
        "gate_to_max_width_ratio": gate_width / max_width,
        "local_error_gate_ratio_partition_2048": gate_error / max_local,
    }
    for key, expected in expected_ratios.items():
        actual = Decimal(str(plots.get(key)))
        if abs(actual - expected) > Decimal("1e-12") * max(abs(expected), Decimal(1)):
            failures.append(f"plot summary ratio mismatch: {key}")

    receipt = {
        "classification": "INDEPENDENT_STAGE_VALIDATION",
        "passed": not failures,
        "failures": failures,
        "lane_count": len(rows),
        "maximum_public_width": str(max_width),
        "public_gate": str(gate_width),
        "gate_to_max_width_ratio": str(gate_width / max_width),
        "maximum_validated_local_error": str(max_local),
        "local_error_gate": str(gate_error),
        "local_error_gate_ratio": str(gate_error / max_local),
        "partition_acceptance": part.get("acceptance_pattern"),
        "stagewise_containment": contain.get("all_contained"),
        "event_restart": event.get("passed"),
        "structural_exact_ledgers": exact.get("passed"),
    }
    out = DATA / "INDEPENDENT_STAGE_VALIDATION.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
