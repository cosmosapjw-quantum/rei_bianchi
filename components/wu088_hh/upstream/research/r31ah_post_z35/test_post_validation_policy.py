import importlib.util
from pathlib import Path
import pytest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("p", HERE/"post_validation_policy.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def test_midpoint_bounds_quadratic_like_scaling():
    b=m.midpoint_lower_bounds(0.1,0.2,2.0,1.0)
    assert b["O_fourth_lower_per_t4"] == pytest.approx(2.4)
    assert b["K_second_lower_per_t3"] == pytest.approx(0.4)
    assert b["O_fourth_lower_per_z4"] == pytest.approx(38.4)
    assert b["K_second_lower_per_t_z2"] == pytest.approx(1.6)

def test_pareto_path_preserves_next_fresh_point():
    a=m.post_z35_action("PARETO_SUPPORTED_AT_Z35")
    assert a["next_fresh_validation_z"] == 2.5
    assert a["auto_execute_next_node"] is False
    assert a["model_class_review_required"] is False

@pytest.mark.parametrize("v",["GLOBAL_SUPPORTED_AT_Z35","TRADEOFF_UNRESOLVED"])
def test_nonpareto_paths_stop(v):
    a=m.post_z35_action(v)
    assert a["action"]=="STOP_FOR_MODEL_CLASS_REVIEW"
    assert a["next_fresh_validation_z"] is None
    assert a["auto_retune"] is False

def test_z25_information():
    x=m.z25_information()
    assert x["S_design_only_per_ta"] == pytest.approx(0.280789512416017)
    assert x["K_half_gap_per_ta"] == pytest.approx(0.09561189201673985)
    assert x["Dmax_half_gap_per_ta"] == pytest.approx(0.10280590292237807)
    assert x["winner_prediction"] is False

def test_halving_factors():
    assert m.conditional_halving_factors()=={
        "O_cubic_remainder_factor":1/16,
        "K_linear_remainder_factor":1/4
    }

def test_bad_inputs():
    with pytest.raises(ValueError): m.midpoint_lower_bounds(-1,0.2,1)
    with pytest.raises(ValueError): m.post_z35_action("OTHER")
