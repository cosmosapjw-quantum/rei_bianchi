#!/usr/bin/env python3
"""Independent replay of the R2-R1A-R1 fail-closed decision."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
REPO = STAGE.parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


mono_mod = _load("r2_r1a_r1_independent_mono", HERE / "monotonicity_audit.py")
enclosure_mod = _load("r2_r1a_r1_independent_enclosure", HERE / "validated_enclosure.py")


def validate() -> dict[str, object]:
    results = json.loads((STAGE / "results.json").read_text(encoding="utf-8"))
    replay_mono = mono_mod.run_audit(REPO)
    demo = enclosure_mod.scalar_linear_demo(rate=-0.5, initial=1.0, duration=0.2)
    partition_rows = results["box_picard"]["partition_audits"]
    previous_widths = results["inherited_numerical_evidence"]["strict_corner_widths"]

    checks = {
        "verdict_is_fail_closed": results["verdict"].startswith("DURABLE_FAIL_CLOSED"),
        "physical_no_go_not_claimed": results["physical_nonexistence_claimed"] is False,
        "production_not_authorized": results["production_history_authorized"] is False,
        "next_affine_taylor_stage_authorized": (
            results["next_stage_authorized"] is True
            and "AFFINE-SET-PARAMETERIZED-TAYLOR-MODEL" in results["next_stage"]
        ),
        "orthant_replay_excluded": replay_mono["constant_diagonal_orthant_excluded"] is True,
        "jacobian_sign_reversal": (
            replay_mono["witness"]["low_node"]["derivative"] < 0.0
            < replay_mono["witness"]["high_node"]["derivative"]
        ),
        "scalar_picard_positive_control_pass": demo["certified"] is True,
        "all_box_partitions_fail_certificate": all(not row["certified"] for row in partition_rows),
        "all_failures_are_table_wrapping": all(
            row["classification"] == "TABLE_TOPOLOGY_EVENT_UNLOCALIZED"
            for row in partition_rows
        ),
        "previous_corner_widths_narrow": all(
            np.isfinite(float(value)) and float(value) < 2.0e-3
            for value in previous_widths.values()
        ),
        "previous_corner_evidence_not_promoted": (
            results["inherited_numerical_evidence"]["classification"]
            == "REGRESSION_EVIDENCE_NOT_CONTINUOUS_CERTIFICATE"
        ),
    }
    passed = all(checks.values())
    payload = {
        "classification": "R2_R1A_R1_INDEPENDENT_VALIDATION",
        "passed": bool(passed),
        "checks": checks,
        "replayed_monotonicity_witness": replay_mono["witness"],
        "scalar_control": demo,
        "partition_classifications": [row["classification"] for row in partition_rows],
    }
    if not passed:
        raise AssertionError(json.dumps(payload, indent=2, sort_keys=True))
    return payload


def main() -> int:
    print(json.dumps(validate(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
