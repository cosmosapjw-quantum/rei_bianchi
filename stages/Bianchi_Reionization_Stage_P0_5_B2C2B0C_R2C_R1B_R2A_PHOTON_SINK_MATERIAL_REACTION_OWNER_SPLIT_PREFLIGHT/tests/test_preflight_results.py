from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).parents[1]
DATA = ROOT / "data"


def test_owner_split_science_gates_close():
    summary = json.loads((DATA / "owner_split_preflight_summary.json").read_text())
    assert summary["hard_pass"] is True
    assert summary["owner_correct_capacity_failures"] == 0
    assert summary["subgrid_resolved_source_coefficients_exact_zero"] is True
    assert summary["max_conditioned_kappa_sum_relative_residual"] < 1e-11
    assert summary["max_conditioned_current_sum_relative_residual"] < 1e-11
    assert summary["max_refinement_total_relative_residual"] < 1e-12


def test_invalid_unsplit_comparison_fails_at_every_first_substep():
    cap = pd.read_csv(DATA / "capacity_refinement_matrix.csv")
    invalid = cap[(cap["mode"] != "OWNER_CORRECT") & cap["reachable"]]
    assert len(invalid) == 20
    assert (invalid["substep"] == 0).all()
    assert (~invalid["feasible"]).all()


def test_owner_correct_capacity_all_refinements_pass():
    cap = pd.read_csv(DATA / "capacity_refinement_matrix.csv")
    corrected = cap[cap["mode"] == "OWNER_CORRECT"]
    assert set(corrected["refinement"]) == {1, 2, 4, 8}
    assert corrected["feasible"].all()
    assert (corrected["reservoir_start_cMpc-3"] >= 0).all()


def test_subgrid_absorption_has_no_resolved_material_or_thermal_source():
    split = pd.read_csv(DATA / "time_resolved_owner_split.csv")
    subgrid = split[split["component"] == "EFFECTIVE_HI_SUBGRID"]
    assert (subgrid["resolved_H_source_coefficient"] == 0).all()
    assert (subgrid["resolved_He_source_coefficient"] == 0).all()
    assert (subgrid["resolved_thermal_source_coefficient"] == 0).all()
