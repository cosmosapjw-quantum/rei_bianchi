import importlib.util
from pathlib import Path
import pytest

HERE = Path(__file__).resolve().parent

def load(name):
    p = HERE / name
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

meta = load("metadata_adapter.py")
pol = load("successor_policy.py")

def test_metadata_number_and_string_are_equal():
    assert meta.identities_match('{"z":2.5}', '{"z":"2.5"}', '2.5')
    assert meta.identities_match('{"z":2.50}', '{"z":"2.500"}', '2.5')

@pytest.mark.parametrize("raw", ['{"z":true}', '{"z":null}', '{"z":"nan"}', '{"z":NaN}', '[]', '{}'])
def test_metadata_bad_z_rejected(raw):
    with pytest.raises((ValueError, TypeError)):
        meta.parse_identity_z(raw)

def test_protocol_classification_is_conservative():
    d = pol.classify_z25_protocol()
    assert d["numerical_result_retained"] is True
    assert d["independent_validation_admitted"] is False
    assert d["retroactive_independence_repair"] is False
    assert d["eligible_for_successor_training"] is True

def test_successor_nodes_and_cells():
    p = pol.successor_training_policy()
    assert p["training_nodes_z"] == [0,.5,1,2,2.5,3,3.5,4]
    assert p["cell_widths_z"] == [.5,.5,1,.5,.5,.5,.5]
    assert p["independent_validation_points"] == []
    assert p["model_family_changed"] is False

def test_z25_local_bounds():
    b = pol.midpoint_lower_bounds(0.019184864006565112, 0.08583702792342718, 2.2358772390338113, 1.0)
    assert b["O_fourth_lower_per_t4"] == pytest.approx(0.29478007821969654)
    assert b["K_second_lower_per_t3"] == pytest.approx(0.13736267798030663)
    assert b["O_fourth_lower_per_z4"] == pytest.approx(7.366987778521003)
    assert b["K_second_lower_per_t_z2"] == pytest.approx(0.6866962233874174)

def test_fresh_candidates_exclude_preexposed_z15():
    c = pol.fresh_candidate_points()
    assert c == [.25,.75,2.25,2.75,3.25,3.75]
    assert 1.5 not in c

def test_selection_rule_and_tie_break():
    r = pol.select_candidate([
        {"z":2.75,"DeltaK":3,"DeltaDmax":4},
        {"z":.75,"DeltaK":0,"DeltaDmax":5},
        {"z":3.75,"DeltaK":1,"DeltaDmax":1},
    ])
    assert r["selected"]["S"] == pytest.approx(5.0)
    assert r["selected"]["z"] == .75

def test_halving_coefficients():
    assert pol.conditional_halving_coefficients() == {"O_cubic":1/16,"K_linear":1/4}

def test_invalid_values_rejected():
    with pytest.raises(ValueError): pol.midpoint_lower_bounds(-1,.1,1)
    with pytest.raises(ValueError): pol.select_candidate([])
