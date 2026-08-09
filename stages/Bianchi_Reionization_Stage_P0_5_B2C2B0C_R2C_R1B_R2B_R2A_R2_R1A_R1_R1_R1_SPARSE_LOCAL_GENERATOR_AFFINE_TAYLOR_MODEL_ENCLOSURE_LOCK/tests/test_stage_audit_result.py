from __future__ import annotations

import json
from pathlib import Path

STAGE = Path(__file__).resolve().parents[1]


def test_sparse_stage_result_is_fail_closed_at_discrete_map_control_gap() -> None:
    data = json.loads((STAGE / "results.json").read_text(encoding="utf-8"))
    assert data["verdict"] == (
        "DURABLE_FAIL_CLOSED_R2_R1A_R1_R1_R1_"
        "SPARSE_LOCAL_SOURCE_AND_LOW_RANK_GLOBAL_COUPLING_PASS_"
        "STATIC_SUBSTEP_CONTROL_ESCAPED_BY_ADMISSIBLE_STAGEWISE_SCHEDULE_"
        "VALIDATED_DISCRETE_MAP_REMAINDER_NOT_CLOSED"
    )
    assert data["source_safe_local_rank_lower_bound"] == 92003
    assert data["global_rank_upper_bound"] == 11
    assert data["evaluation_site_count"] == 4
    assert data["evaluation_site_input_rank_lower_bound"] == 368012
    assert data["static_parameter_enclosure_certified"] is False
    assert data["stagewise_witness_all_hard_gates_pass"] is True
    assert data["stagewise_witness_outside_coordinate"] == "x_HeIII"
    assert data["stagewise_witness_max_fraction_of_static_width"] > 0.02
    assert data["rust_backend_load_bearing"] is False
    assert data["rust_bounds_contain_python"] is True
    assert data["production_history_authorized"] is False
    assert data["next_stage_authorized"] is True


def test_all_three_lanes_have_identical_stagewise_witness_endpoint() -> None:
    data = json.loads((STAGE / "results.json").read_text(encoding="utf-8"))
    rows = data["temporal_control_lanes"]
    assert len(rows) == 3
    assert len({row["endpoint_sha256"] for row in rows}) == 1
    assert all(row["all_trial_hard_gates_pass"] for row in rows)
