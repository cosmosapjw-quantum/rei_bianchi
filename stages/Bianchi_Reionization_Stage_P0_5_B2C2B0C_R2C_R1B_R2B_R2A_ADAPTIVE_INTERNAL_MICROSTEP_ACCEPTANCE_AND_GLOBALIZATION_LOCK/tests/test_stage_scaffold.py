from __future__ import annotations

import json
from pathlib import Path

STAGE = Path(__file__).resolve().parents[1]


def test_precalculation_lock_declares_exact_adaptive_policy():
    lock = json.loads((STAGE / "INPUT_LOCK.json").read_text())
    assert lock["calculation_started"] is False
    assert lock["adaptive"]["initial_partition"] == 8
    assert lock["adaptive"]["minimum_partition"] == 1024
    assert lock["adaptive"]["damping_candidates"] == [
        1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625
    ]
    assert lock["tolerances"] == {
        "fixed_point": 1e-10,
        "owner_nuclei": 1e-11,
        "photon": 1e-8,
        "local_error": 2e-4,
    }
    assert lock["forbidden"][0] == "clipping"
    assert lock["stage"].endswith("GLOBALIZATION-LOCK")


def test_stage_contracts_and_harness_receipt_exist():
    for name in (
        "SCIENTIFIC_CONTRACT.md",
        "RESEARCH_CONTRACT.md",
        "STAGE_STATE.json",
        "receipts/HARNESS_RECEIPT.json",
        "receipts/BASELINE_RECEIPT.json",
        "inputs/APPROVED_DESIGN.md",
        "inputs/PERFORMANCE_BENCHMARK_SPEC.json",
    ):
        assert (STAGE / name).is_file(), name
