#!/usr/bin/env python3
"""Independent replay of the R2-R1A four-corner propagation evidence."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

STAGE = Path(__file__).resolve().parents[1]
DATA = STAGE / "data"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _physical_result(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result.pop("elapsed_s", None)
    return result


def validate() -> dict[str, Any]:
    results = json.loads((STAGE / "results.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader((DATA / "policy_trial_summary.csv").open(newline="", encoding="utf-8")))
    endpoints = json.loads((DATA / "endpoint_hashes.json").read_text(encoding="utf-8"))
    reference = json.loads(
        (STAGE / "attempts/ATTEMPT_4_SINGLE_PROCESS_REFERENCE_RECEIPT.json").read_text(
            encoding="utf-8"
        )
    )

    assert len(rows) == 24
    identities = {(row["lane"], row["policy_id"]) for row in rows}
    assert len(identities) == 24
    assert sum(row["load_bearing"] == "True" for row in rows) == 12
    assert all(row["hard_gates_pass"] == "True" for row in rows)
    assert all(float(row["local_error"]) < float(row["local_error_gate"]) for row in rows)
    assert all(float(row["minimum_species"]) > 0.0 for row in rows)
    assert all(float(row["max_H_residual"]) <= 1.0e-11 for row in rows)
    assert all(float(row["max_He_residual"]) <= 1.0e-11 for row in rows)
    assert all(float(row["max_owner_residual"]) <= 1.0e-11 for row in rows)
    assert all(float(row["max_photon_residual"]) <= 1.0e-8 for row in rows)
    assert all(float(row["max_thermal_residual"]) <= 1.0e-10 for row in rows)
    assert all(float(row["max_PDS_residual"]) <= 1.0e-11 for row in rows)
    assert all(float(row["max_OTS_energy_residual"]) <= 1.0e-10 for row in rows)

    with np.load(DATA / "strict_corner_envelopes.npz", allow_pickle=False) as data:
        keys = sorted(data.files)
        assert len(keys) == 24
        recomputed: dict[str, dict[str, float]] = {}
        for lane in (
            "LOCAL_NEUTRAL_HAZARD_PRIMARY",
            "RECOMBINATION_WEIGHTED_AUDITOR",
            "SCRIPT_SELF_SHIELDING_AUDITOR",
        ):
            token = lane.lower()
            recomputed[lane] = {}
            for field in ("x_HII", "x_HeII", "x_HeIII", "log_T"):
                lower = np.asarray(data[f"{token}__{field}_lower"], dtype=np.float64)
                upper = np.asarray(data[f"{token}__{field}_upper"], dtype=np.float64)
                assert lower.shape == (46080,)
                assert upper.shape == (46080,)
                assert np.all(np.isfinite(lower)) and np.all(np.isfinite(upper))
                assert np.all(upper >= lower)
                recomputed[lane][field] = float(np.max(upper - lower))
                assert abs(recomputed[lane][field] - float(results["lane_widths"][lane][field])) <= 2.0e-15

    overall = {
        field: max(recomputed[lane][field] for lane in recomputed)
        for field in ("x_HII", "x_HeII", "x_HeIII", "log_T")
    }
    for field, value in overall.items():
        assert abs(value - float(results["overall_widths"][field])) <= 2.0e-15

    counts = Counter(endpoints.values())
    assert len(endpoints) == 24
    assert len(counts) == 8
    assert set(counts.values()) == {3}

    assert results["all_numerical_gates_pass"] is True
    assert results["decision"]["classification"] == "CONTINUOUS_PARAMETER_ENCLOSURE_UNCERTIFIED"
    assert results["production_history_authorized"] is False
    assert results["production_node_chemistry_authorized"] is False
    assert results["continuous_parameter_certificate"].startswith("NOT_AVAILABLE")
    assert _physical_result(results) == _physical_result(reference["result"])

    stable = {}
    for rel in ("data/endpoint_hashes.json", "data/strict_corner_envelopes.npz"):
        current = sha256(STAGE / rel)
        expected = reference["files"][rel]["sha256"]
        assert current == expected
        stable[rel] = current

    receipt = {
        "classification": "R2_R1A_INDEPENDENT_VALIDATION",
        "status": "PASS",
        "policy_row_count": len(rows),
        "load_bearing_row_count": 12,
        "unique_endpoint_count": len(counts),
        "endpoint_multiplicity": sorted(counts.values()),
        "all_hard_gates_pass": True,
        "overall_widths": overall,
        "continuous_parameter_certificate_present": False,
        "stable_artifact_sha256": stable,
        "result_parity_excluding_elapsed": True,
    }
    return receipt


def main() -> int:
    receipt = validate()
    output = STAGE / "receipts/INDEPENDENT_VALIDATION.json"
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
