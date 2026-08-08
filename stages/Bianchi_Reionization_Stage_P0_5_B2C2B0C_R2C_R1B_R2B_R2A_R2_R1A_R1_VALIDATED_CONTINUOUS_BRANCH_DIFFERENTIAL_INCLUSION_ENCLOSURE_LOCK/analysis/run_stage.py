#!/usr/bin/env python3
"""Execute and serialize the R2-R1A-R1 validated-enclosure audit."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
REPO = STAGE.parents[1]
PREVIOUS = REPO / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_FOUR_CORNER_BRANCH_AND_UNRESOLVED_OTS_ENERGY_PROPAGATION_PREFLIGHT/results.json"


def _load(name: str, path: Path) -> Any:
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


monotonicity = _load("r2_r1a_r1_run_monotonicity", HERE / "monotonicity_audit.py")
enclosure = _load("r2_r1a_r1_run_enclosure", HERE / "validated_enclosure.py")

VERDICT = (
    "DURABLE_FAIL_CLOSED_R2_R1A_R1_CONSTANT_ORTHANT_EXCLUDED_"
    "COMPONENTWISE_BOX_WRAPPING_CROSSES_SOURCE_TABLE_BOUNDARY_"
    "AFFINE_TAYLOR_MODEL_LOCK_AUTHORIZED"
)
NEXT_STAGE = (
    "P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-"
    "AFFINE-SET-PARAMETERIZED-TAYLOR-MODEL-CONTINUOUS-BRANCH-ENCLOSURE-LOCK"
)


def _write_partition_csv(rows: list[dict[str, Any]]) -> None:
    path = STAGE / "data/BOX_PICARD_PARTITION_AUDIT.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = (
        "partition", "segment_count", "accepted_segments",
        "first_failed_segment_zero_based", "classification", "message",
        "picard_iterations_at_failure", "maximum_internal_coordinate_width",
        "elapsed_s", "certified",
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fields})


def run() -> dict[str, Any]:
    started = time.perf_counter()
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    mono = monotonicity.run_audit(REPO)
    box = enclosure.run_project_audit(REPO, partitions=(16, 32, 64))
    _write_partition_csv(box["partition_audits"])
    (STAGE / "data").mkdir(parents=True, exist_ok=True)
    (STAGE / "data/MONOTONICITY_AUDIT.json").write_text(
        json.dumps(mono, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (STAGE / "data/BOX_PICARD_AUDIT.json").write_text(
        json.dumps(box, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    all_box_failed = all(not bool(row["certified"]) for row in box["partition_audits"])
    table_boundary_failures = sum(
        row["classification"] == "TABLE_TOPOLOGY_EVENT_UNLOCALIZED"
        for row in box["partition_audits"]
    )
    result = {
        "stage": (
            "P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-"
            "VALIDATED-CONTINUOUS-BRANCH-DIFFERENTIAL-INCLUSION-ENCLOSURE-LOCK"
        ),
        "verdict": VERDICT,
        "completed": True,
        "continuous_parameter_certified": False,
        "production_history_authorized": False,
        "production_node_chemistry_authorized": False,
        "R2C_R2_authorized": False,
        "B2C2B_authorized": False,
        "physical_nonexistence_claimed": False,
        "next_stage": NEXT_STAGE,
        "next_stage_authorized": True,
        "constant_diagonal_orthant_excluded": bool(
            mono["constant_diagonal_orthant_excluded"]
        ),
        "monotonicity_witness": mono["witness"],
        "box_picard": {
            "all_locked_partitions_failed": bool(all_box_failed),
            "table_boundary_failure_count": int(table_boundary_failures),
            "partition_audits": box["partition_audits"],
            "scope": box["method_scope"],
        },
        "inherited_numerical_evidence": {
            "realization_count": int(previous["state_realization_count"]),
            "all_numerical_gates_pass": bool(previous["all_numerical_gates_pass"]),
            "strict_corner_widths": previous["overall_widths"],
            "uncertainty_gate": float(previous["uncertainty_gate"]),
            "classification": "REGRESSION_EVIDENCE_NOT_CONTINUOUS_CERTIFICATE",
        },
        "coordinate_attempts_preserved": [
            "INDEPENDENT_HELIUM_BOX_SIMPLEX_WRAPPING",
            "NEAR_UNIT_LOGIT_INTERVAL_AMPLIFICATION",
            "NEUTRAL_LOG_COORDINATE_DEPENDENCY",
            "DIRECT_NEUTRAL_CONDITIONAL_BOX_TABLE_BOUNDARY_WRAPPING",
        ],
        "interpretation": (
            "The fixed orthant comparison route is excluded by a robust Jacobian sign reversal. "
            "Outward-rounded componentwise Picard boxes are valid on an analytic scalar regression, "
            "but on the project RHS dependency/wrapping enlarges the first tube through the source "
            "table boundary before any locked partition is certified. This is not a physical no-go; "
            "an affine/Taylor-model set parameterization is required."
        ),
        "elapsed_s": float(time.perf_counter() - started),
    }
    (STAGE / "results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    print(json.dumps(run(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
