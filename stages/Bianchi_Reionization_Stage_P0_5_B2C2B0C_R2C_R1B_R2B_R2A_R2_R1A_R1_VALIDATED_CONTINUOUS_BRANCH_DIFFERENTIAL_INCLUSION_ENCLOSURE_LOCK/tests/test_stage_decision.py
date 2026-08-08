from pathlib import Path
import json

STAGE = Path(__file__).resolve().parents[1]


def test_stage_is_fail_closed_for_method_not_physical_nonexistence():
    result = json.loads((STAGE / "results.json").read_text())
    assert result["verdict"].startswith("DURABLE_FAIL_CLOSED")
    assert result["constant_diagonal_orthant_excluded"] is True
    assert result["continuous_parameter_certified"] is False
    assert result["physical_nonexistence_claimed"] is False
    assert result["production_history_authorized"] is False
    assert result["next_stage_authorized"] is True
    assert "AFFINE-SET-PARAMETERIZED-TAYLOR-MODEL" in result["next_stage"]


def test_all_locked_box_partitions_fail_at_unlocalized_source_table_boundary():
    result = json.loads((STAGE / "results.json").read_text())
    rows = result["box_picard"]["partition_audits"]
    assert [row["partition"] for row in rows] == [16, 32, 64]
    assert all(row["certified"] is False for row in rows)
    assert all(row["classification"] == "TABLE_TOPOLOGY_EVENT_UNLOCALIZED" for row in rows)
    assert all(row["accepted_segments"] == 0 for row in rows)


def test_inherited_corner_widths_are_regression_evidence_only():
    result = json.loads((STAGE / "results.json").read_text())
    inherited = result["inherited_numerical_evidence"]
    assert inherited["realization_count"] == 24
    assert inherited["all_numerical_gates_pass"] is True
    assert inherited["classification"] == "REGRESSION_EVIDENCE_NOT_CONTINUOUS_CERTIFICATE"
    assert max(inherited["strict_corner_widths"].values()) < inherited["uncertainty_gate"]


def test_independent_and_wolfram_receipts_pass():
    independent = json.loads((STAGE / "receipts/INDEPENDENT_VALIDATION.json").read_text())
    wolfram = json.loads((STAGE / "receipts/WOLFRAM_SYMBOLIC_RECEIPT.json").read_text())
    assert independent["passed"] is True
    assert wolfram["constant_orthant_sign_reversal_feasible"] is False
    assert wolfram["corner_weight_sum_residual"] == "0"
